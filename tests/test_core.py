import os
import base64
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from flask import Flask

from models import database
from routes.api import api_bp
from routes.auth import auth_bp
from routes.middleware import register_middleware
from services import artifact_service
from services import backup_service
from services import chat_service
from utils import privacy as privacy_module
from utils import system_health as health_module
from utils.debug_logs import parse_log_entries
from utils.errors import register_error_handlers
from utils.media import decode_image_base64
from utils.privacy import PURGE_CONFIRMATION, privacy_summary, purge_private_data
from utils.security import CSRF_HEADER, CSRF_SESSION_KEY, get_csrf_token
from utils.system_health import collect_health


class IsolatedDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db_path = database.DB_PATH
        self.old_data_dir = database.DATA_DIR
        database.DB_PATH = os.path.join(self.tmp.name, "chats.db")
        database.DATA_DIR = self.tmp.name

    def tearDown(self):
        database.DB_PATH = self.old_db_path
        database.DATA_DIR = self.old_data_dir
        self.tmp.cleanup()


class DatabaseMigrationTests(IsolatedDatabaseTest):
    def test_parent_id_migration_backfills_existing_linear_history(self):
        con = sqlite3.connect(database.DB_PATH)
        con.execute(
            """CREATE TABLE rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model TEXT NOT NULL DEFAULT 'llama3',
                created TEXT NOT NULL
            )"""
        )
        con.execute(
            """CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                favorite INTEGER DEFAULT 0,
                created TEXT NOT NULL
            )"""
        )
        con.execute("INSERT INTO rooms (name,model,created) VALUES (?,?,?)", ("Alt", "llama3", "now"))
        for role, content in (("user", "eins"), ("ai", "zwei"), ("user", "drei")):
            con.execute(
                "INSERT INTO messages (room_id,role,content,created) VALUES (?,?,?,?)",
                (1, role, content, "now"),
            )
        con.commit()
        con.close()

        database.init_db()

        con = sqlite3.connect(database.DB_PATH)
        rows = con.execute("SELECT id,parent_id FROM messages ORDER BY id ASC").fetchall()
        columns = [row[1] for row in con.execute("PRAGMA table_info(messages)").fetchall()]
        con.close()

        self.assertIn("parent_id", columns)
        self.assertEqual(rows, [(1, None), (2, 1), (3, 2)])

    def test_artifact_versions_table_is_created(self):
        database.init_db()

        con = sqlite3.connect(database.DB_PATH)
        columns = [row[1] for row in con.execute("PRAGMA table_info(artifact_versions)").fetchall()]
        indexes = [row[1] for row in con.execute("PRAGMA index_list(artifact_versions)").fetchall()]
        con.close()

        self.assertIn("content_hash", columns)
        self.assertIn("html", columns)
        self.assertTrue(any("idx_artifact_versions_room" in idx for idx in indexes))


class ArtifactVersionTests(IsolatedDatabaseTest):
    def setUp(self):
        super().setUp()
        database.init_db()

    def test_save_artifacts_deduplicates_by_content_hash(self):
        payload = [{
            "key": "html:1",
            "title": "Demo",
            "lang": "HTML",
            "html": "<!doctype html><h1>Hallo</h1>",
            "source": "```html\n<h1>Hallo</h1>\n```",
            "message_id": None,
        }]

        first = artifact_service.save_artifacts(1, payload)
        second = artifact_service.save_artifacts(1, payload)
        versions = artifact_service.list_artifacts(1)

        self.assertEqual(len(first["saved"]), 1)
        self.assertEqual(len(second["saved"]), 0)
        self.assertEqual(len(second["skipped"]), 1)
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0]["title"], "Demo")

    def test_delete_artifact_removes_single_version(self):
        saved = artifact_service.save_artifacts(1, [{
            "key": "html:delete",
            "title": "Delete Me",
            "lang": "HTML",
            "html": "<!doctype html><p>Delete</p>",
            "source": "source",
        }])
        artifact_id = saved["saved"][0]

        result = artifact_service.delete_artifact(1, artifact_id)

        self.assertEqual(result["deleted"], artifact_id)
        self.assertEqual(artifact_service.list_artifacts(1), [])

    def test_artifact_api_requires_login_and_saves_with_csrf(self):
        app = Flask(__name__)
        app.secret_key = "test"
        register_middleware(app)
        register_error_handlers(app)
        app.register_blueprint(auth_bp)
        app.register_blueprint(api_bp)

        payload = {"artifacts": [{
            "key": "html:api",
            "title": "API Demo",
            "lang": "HTML",
            "html": "<!doctype html><p>API</p>",
            "source": "source",
        }]}

        with app.test_client() as client:
            locked = client.get("/api/rooms/1/artifacts")
            with client.session_transaction() as sess:
                sess["authenticated"] = True
                sess[CSRF_SESSION_KEY] = "artifact-token"
            saved = client.post(
                "/api/rooms/1/artifacts",
                json=payload,
                headers={CSRF_HEADER: "artifact-token"},
            )
            artifact_id = saved.get_json()["saved"][0]
            deleted = client.delete(
                f"/api/rooms/1/artifacts/{artifact_id}",
                headers={CSRF_HEADER: "artifact-token"},
            )
            listed = client.get("/api/rooms/1/artifacts")

        self.assertEqual(locked.status_code, 302)
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(len(saved.get_json()["saved"]), 1)
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(deleted.get_json()["deleted"], artifact_id)
        self.assertEqual(len(listed.get_json()["versions"]), 0)


class ChatServiceTests(IsolatedDatabaseTest):
    def setUp(self):
        super().setUp()
        database.init_db()

    def test_build_messages_uses_only_selected_branch_path(self):
        con = database.get_db()
        con.execute("DELETE FROM messages")
        now = datetime.now().isoformat()
        messages = [
            (1, None, "user", "Root"),
            (1, 1, "ai", "Antwort A"),
            (1, 2, "user", "Weiter A"),
            (1, 3, "ai", "Ende A"),
            (1, 2, "user", "Weiter B"),
            (1, 5, "ai", "Ende B"),
        ]
        for room_id, parent_id, role, content in messages:
            con.execute(
                "INSERT INTO messages (room_id,parent_id,role,content,created,tokens) VALUES (?,?,?,?,?,?)",
                (room_id, parent_id, role, content, now, 1),
            )
        con.commit()
        con.close()

        payload, model = chat_service.build_messages(1, "Neue Frage", parent_id=6)

        self.assertEqual(model, "llama3")
        self.assertEqual([m["content"] for m in payload[1:]], ["Root", "Antwort A", "Weiter B", "Ende B", "Neue Frage"])

    def test_build_messages_empty_chat_does_not_duplicate_new_message(self):
        payload, _model = chat_service.build_messages(1, "Nur neu", parent_id=None)

        self.assertEqual([m["role"] for m in payload], ["system", "user"])
        self.assertEqual(payload[-1]["content"], "Nur neu")

    def test_generate_auto_title_uses_fast_title_model_and_updates_room(self):
        con = database.get_db()
        con.execute("UPDATE rooms SET name='Neuer Chat' WHERE id=1")
        con.commit()
        con.close()

        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = {"message": {"content": '"Kurzer Titel"'}}

        with patch.object(chat_service.requests, "post", return_value=fake_response) as post:
            title = chat_service.generate_auto_title(1, "Bitte erkläre mir Branching.")

        self.assertEqual(title, "Kurzer Titel")
        self.assertEqual(post.call_args.kwargs["json"]["model"], "llama3.2:1b")

        con = database.get_db()
        room = con.execute("SELECT name FROM rooms WHERE id=1").fetchone()
        con.close()
        self.assertEqual(room["name"], "Kurzer Titel")

    def test_clean_auto_title_removes_explanatory_noise(self):
        title = chat_service.clean_auto_title(
            "Hier ist der Titel: **Python Fehleranalyse**\nMehr Text",
            "Bitte debugge meinen Python Code",
        )

        self.assertEqual(title, "Python Fehleranalyse")


class MiddlewareAndErrorTests(unittest.TestCase):
    def make_app(self):
        app = Flask(__name__)
        app.secret_key = "test"
        register_middleware(app)
        register_error_handlers(app)
        app.register_blueprint(api_bp)

        @app.route("/api/ok", methods=["POST"])
        def ok():
            return {"ok": True}

        @app.route("/api/boom")
        def boom():
            raise RuntimeError("secret internal detail")

        return app

    def test_request_id_is_returned_and_internal_detail_is_hidden(self):
        app = self.make_app()
        with app.test_client() as client:
            res = client.get("/api/boom", headers={"X-Request-ID": "test-request-1"})

        body = res.get_json()
        self.assertEqual(res.status_code, 500)
        self.assertEqual(res.headers["X-Request-ID"], "test-request-1")
        self.assertEqual(body["request_id"], "test-request-1")
        self.assertNotIn("detail", body)

    def test_cross_origin_post_is_blocked(self):
        app = self.make_app()
        with app.test_client() as client:
            res = client.post("/api/ok", headers={"Origin": "http://evil.example"})

        body = res.get_json()
        self.assertEqual(res.status_code, 403)
        self.assertEqual(body["error"], "Ungültiger Ursprung")
        self.assertIn("request_id", body)

    def test_authenticated_mutation_requires_csrf_token(self):
        app = self.make_app()
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["authenticated"] = True
                sess[CSRF_SESSION_KEY] = "known-token"
            blocked = client.post("/api/ok")
            allowed = client.post("/api/ok", headers={CSRF_HEADER: "known-token"})

        self.assertEqual(blocked.status_code, 403)
        self.assertEqual(blocked.get_json()["error"], "Ungültiger Sicherheits-Token")
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.get_json(), {"ok": True})

    def test_csp_allows_required_rich_preview_cdns(self):
        app = self.make_app()
        with app.test_client() as client:
            res = client.post("/api/ok")

        csp = res.headers["Content-Security-Policy"]
        self.assertIn("https://cdnjs.cloudflare.com", csp)
        self.assertIn("https://cdn.jsdelivr.net", csp)
        self.assertIn("https://cdn.tailwindcss.com", csp)

    def test_api_route_errors_hide_internal_details_and_keep_request_id(self):
        class BrokenConnection:
            def execute(self, *_args, **_kwargs):
                raise RuntimeError("secret db path should stay in logs")

            def close(self):
                pass

        app = self.make_app()
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["authenticated"] = True
                sess[CSRF_SESSION_KEY] = "known-token"
            with patch("routes.api.get_db", return_value=BrokenConnection()):
                res = client.post(
                    "/api/rooms",
                    json={"name": "Test"},
                    headers={CSRF_HEADER: "known-token", "X-Request-ID": "api-safe-1"},
                )

        body = res.get_json()
        self.assertEqual(res.status_code, 500)
        self.assertEqual(body["error"], "Raum konnte nicht erstellt werden")
        self.assertEqual(body["request_id"], "api-safe-1")
        self.assertNotIn("secret db path", str(body))


class AuthSecurityTests(unittest.TestCase):
    def make_app(self):
        app = Flask(__name__)
        app.secret_key = "test"
        register_middleware(app)
        app.register_blueprint(auth_bp)

        @app.context_processor
        def csrf_context():
            return {"csrf_token": get_csrf_token()}

        return app

    def test_login_post_requires_csrf_token(self):
        app = self.make_app()
        with app.test_client() as client:
            with patch("routes.auth.setup_required", return_value=False):
                res = client.post("/login", data={"password": "pw"})

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Ungültiger Sicherheits-Token")

    def test_login_accepts_form_csrf_token_and_regenerates_session_state(self):
        app = self.make_app()
        with app.test_client() as client:
            with patch("routes.auth.setup_required", return_value=False):
                client.get("/login")
                with client.session_transaction() as sess:
                    token = sess[CSRF_SESSION_KEY]
                with patch("routes.auth.check_password", return_value=True):
                    res = client.post("/login", data={"password": "pw", "csrf_token": token})
            with client.session_transaction() as sess:
                authenticated = sess.get("authenticated")
                new_login = sess.get("new_login")

        self.assertEqual(res.status_code, 302)
        self.assertTrue(authenticated)
        self.assertTrue(new_login)


class FrontendIntegrationTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def read(self, path):
        return (self.root / path).read_text(encoding="utf-8")

    def test_chat_page_loads_rich_block_libraries(self):
        html = self.read("templates/index.html")

        self.assertIn('name="csrf-token"', html)
        self.assertIn("mermaid.min.js", html)
        self.assertIn("Chart.js", html)
        self.assertIn("rich-mermaid-body", html)
        self.assertIn("leon-color-red", html)

    def test_chat_renderer_supports_mermaid_charts_and_color_tags(self):
        js = self.read("static/js/chat.js")

        self.assertIn("Leon.renderMermaidBlock", js)
        self.assertIn("Leon.renderChartBlock", js)
        self.assertIn("Leon.expandColorTags", js)
        self.assertIn("chart-codeblock", js)
        self.assertIn("parseChartCandidate", js)
        self.assertIn("clean === ''", js)
        self.assertIn("[\\\\/(${tagNames})\\\\]", js)
        self.assertIn("openColor !== closeColor", js)
        self.assertIn("normalizeMermaidSource", js)
        self.assertIn("diagramm", js)
        self.assertIn("flussdiagramm", js)
        self.assertIn("balkendiagramm", js)
        self.assertIn("source.replace(/^\\s*(diagramm|diagram|flussdiagramm)", js)
        self.assertIn("flowchart TD", js)
        self.assertIn("$1|$2| ", js)
        self.assertIn("$1\\n$2 $3", js)
        self.assertIn("[^\\\\s\\\\[\\\\]<>,.;:!?]+", js)
        self.assertIn("[^\\\\n<]+", js)

    def test_artifact_preview_injects_tailwind(self):
        js = self.read("static/js/artifacts.js")

        self.assertIn("injectTailwind", js)
        self.assertIn("https://cdn.tailwindcss.com", js)
        self.assertIn('<script src="https://cdn.tailwindcss.com"></script>', js)
        self.assertIn("leon-neutralized-assets", js)
        self.assertIn("data-leon-", js)
        self.assertIn("waitForLoadPyodide", js)
        self.assertIn("ensurePyodideLoader", js)
        self.assertIn("Vorschau wurde neu gestartet", js)
        self.assertIn("Script error", js)
        self.assertIn("setFrameHtml", js)
        self.assertIn("URL.createObjectURL", js)
        self.assertIn("data:text/html;charset=utf-8", js)
        self.assertIn("dataUrl.length < 1800000", js)
        self.assertIn("frame.removeAttribute('srcdoc')", js)
        self.assertIn("frame-src 'self' data: blob:", self.read("routes/middleware.py"))

    def test_artifact_panel_has_tabs_and_console_bridge(self):
        html = self.read("templates/index.html")
        js = self.read("static/js/artifacts.js")

        self.assertIn("data-artifact-tab=\"console\"", html)
        self.assertIn(">Terminal<", html)
        self.assertIn("data-artifact-tab=\"errors\"", html)
        self.assertIn("id=\"artifact-select\"", html)
        self.assertIn("downloadArtifactHtml", html)
        self.assertIn("downloadArtifactZip", html)
        self.assertIn("downloadAllArtifactsZip", html)
        self.assertIn("deleteArtifactVersion", html)
        self.assertIn("leon-artifact-log", js)
        self.assertIn("switchArtifactTab", js)
        self.assertIn("switchArtifactVersion", js)
        self.assertIn("zipBlob", js)
        self.assertIn("loadArtifactHistory", js)
        self.assertIn("syncArtifactHistory", js)
        self.assertIn("downloadAllArtifactsZip", js)
        self.assertIn("deleteArtifactVersion", js)
        self.assertIn("/artifacts", js)

    def test_frontend_requests_send_csrf_tokens(self):
        api_js = self.read("static/js/api.js")
        chat_js = self.read("static/js/chat.js")
        dashboard_html = self.read("templates/dashboard.html")

        self.assertIn("Leon.csrfToken", api_js)
        self.assertIn("X-CSRF-Token", api_js)
        self.assertIn("Leon.requestHeaders({ method: 'POST' })", chat_js)
        self.assertIn('name="csrf-token"', dashboard_html)
        self.assertIn("requestHeaders(options)", dashboard_html)


class PublicLaunchFileTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def read(self, path):
        return (self.root / path).read_text(encoding="utf-8")

    def test_cross_platform_launchers_are_documented(self):
        readme = self.read("README.md")

        self.assertTrue((self.root / "Starten.command").is_file())
        self.assertTrue((self.root / "Starten.ps1").is_file())
        self.assertTrue((self.root / "start.sh").is_file())
        self.assertIn(".\\Starten.ps1", readme)
        self.assertIn("./start.sh", readme)
        self.assertIn("./Starten.command", readme)

    def test_playwright_browser_qa_is_wired_into_ci(self):
        workflow = self.read(".github/workflows/test.yml")
        config = self.read("playwright.config.js")
        spec = self.read("tests/browser/leon-public-launch.spec.js")
        package = self.read("package.json")

        self.assertIn("npm install", workflow)
        self.assertIn("npx playwright install --with-deps chromium", workflow)
        self.assertIn("npm run test:browser", workflow)
        self.assertIn("webServer", config)
        self.assertIn("data_browser_test", config)
        self.assertIn("artifact preview renders simple HTML", spec)
        self.assertIn("@playwright/test", package)

    def test_feedback_templates_and_roadmap_exist(self):
        expected = [
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/general_feedback.yml",
            ".github/ISSUE_TEMPLATE/security_contact.yml",
            ".github/PULL_REQUEST_TEMPLATE.md",
            "TROUBLESHOOTING.md",
            "docs/de/TROUBLESHOOTING.md",
            "ROADMAP.md",
        ]

        for path in expected:
            self.assertTrue((self.root / path).is_file(), path)
        self.assertIn("Feedback Wanted", self.read("ROADMAP.md"))
        self.assertIn("source-available", self.read(".github/PULL_REQUEST_TEMPLATE.md"))

    def test_german_documentation_lives_inside_docs_de(self):
        readme = self.read("README.md")
        german_readme = self.read("docs/de/README.md")

        self.assertIn("docs/de/README.md", readme)
        self.assertIn("STRUKTUR.md", german_readme)
        self.assertIn("SECURITY.md", german_readme)
        self.assertIn("TESTING.md", german_readme)
        self.assertIn("TROUBLESHOOTING.md", german_readme)
        self.assertIn("CONTRIBUTING.md", german_readme)
        self.assertIn("ROADMAP.md", german_readme)
        self.assertIn("CHANGELOG.md", german_readme)

    def test_frontend_error_diagnostics_include_request_ids(self):
        api_js = self.read("static/js/api.js")
        chat_js = self.read("static/js/chat.js")
        dashboard_html = self.read("templates/dashboard.html")
        chat_route = self.read("routes/chat.py")
        api_route = self.read("routes/api.py")

        self.assertIn("Leon.errorFromResponse", api_js)
        self.assertIn("Leon.errorLabel", api_js)
        self.assertIn("lastRequestId", api_js)
        self.assertIn("request_id: Leon.state.lastRequestId", api_js)
        self.assertIn("Leon.errorLabel(e", chat_js)
        self.assertIn("data.request_id", chat_js)
        self.assertIn("errorLabel(e", dashboard_html)
        self.assertIn("'request_id': request_id", chat_route)
        self.assertIn("related_request_id", api_route)

    def test_system_prompt_mentions_rich_outputs(self):
        config_text = self.read("config.py")

        self.assertIn("mermaid-Codeblock", config_text)
        self.assertIn("chart-Codeblock", config_text)
        self.assertIn("```chart", config_text)
        self.assertIn("[rot]Text[/rot]", config_text)
        self.assertIn("Tailwind", config_text)

    def test_dashboard_exposes_health_and_privacy_controls(self):
        html = self.read("templates/dashboard.html")

        self.assertIn("Health Center", html)
        self.assertIn("Privacy", html)
        self.assertIn("/api/health", html)
        self.assertIn("/api/privacy/summary", html)
        self.assertIn("/api/privacy/purge", html)
        self.assertIn("/api/backups/run", html)
        self.assertIn("/api/backups", html)
        self.assertIn("/api/backups/restore", html)
        self.assertIn("restoreBackup", html)
        self.assertIn("Backups laden", html)
        self.assertIn("p.artifacts", html)

    def test_dashboard_and_chat_expose_premium_polish_controls(self):
        dashboard_html = self.read("templates/dashboard.html")
        index_html = self.read("templates/index.html")
        ui_js = self.read("static/js/ui.js")

        self.assertIn("Status-Legende", ui_js)
        self.assertIn("toggleRoomPin", ui_js)
        self.assertIn("room-pin", index_html)
        self.assertIn("Chats</button>", index_html)
        self.assertIn("Dashboard</button>", index_html)
        self.assertIn("data-tip=\"Tokens", dashboard_html)
        self.assertIn("Tokens sind Wortbausteine", dashboard_html)
        self.assertIn("Wortbausteine der KI", dashboard_html)
        self.assertIn("toggleDebugCenter", dashboard_html)
        self.assertIn("Übersicht", dashboard_html)
        self.assertIn("setType('favorites'", dashboard_html)

    def test_login_exposes_feature_button_and_github_readme_exists(self):
        auth_route = self.read("routes/auth.py")
        readme = self.read("README.md")
        start_script = self.read("Starten.command")

        self.assertIn("Fähigkeiten", auth_route)
        self.assertIn("Was LEON AI kann", auth_route)
        self.assertIn("Farbig markieren", auth_route)
        self.assertIn("LEON AI läuft bereits", start_script)
        self.assertIn("## Features That Make You Want To Try It", readme)
        self.assertIn("## About The Developer", readme)
        self.assertIn("English is the main documentation language", readme)
        self.assertIn("docs/de/README.md", readme)
        self.assertIn("## Download / Clone And Install", readme)
        self.assertIn("## Storage Needed", readme)
        self.assertIn("CHANGELOG.md", readme)
        self.assertIn("TROUBLESHOOTING.md", readme)
        self.assertNotIn("LeonAI-DE", readme)
        self.assertNotIn("Mobile Documents/com~apple~CloudDocs", readme)
        self.assertIn("Real folder overview", readme)

    def test_release_doctor_passes_and_is_documented(self):
        result = subprocess.run(
            [sys.executable, "scripts/leon_doctor.py"],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        readme = self.read("README.md")
        testing = self.read("TESTING.md")
        workflow = self.read(".github/workflows/test.yml")

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("LEON AI Release Doctor", result.stdout)
        self.assertIn("scripts/leon_doctor.py", readme)
        self.assertIn("scripts/leon_doctor.py", testing)
        self.assertIn("python scripts/leon_doctor.py", workflow)

    def test_troubleshooting_docs_cover_common_public_support_cases(self):
        english = self.read("TROUBLESHOOTING.md")
        german = self.read("docs/de/TROUBLESHOOTING.md")

        for needle in (
            "Ollama",
            "Artifacts preview is blank",
            "Mermaid diagram does not render",
            "Chart.js output stays as code",
            "Request ID",
            "data/logs/leon.log",
            "GitHub Actions",
        ):
            self.assertIn(needle, english)

        for needle in (
            "Ollama",
            "Artifacts-Vorschau bleibt leer",
            "Mermaid-Diagramm rendert nicht",
            "Chart.js-Ausgabe bleibt Code",
            "Request ID",
            "data/logs/leon.log",
            "GitHub Actions",
        ):
            self.assertIn(needle, german)


class DebugAndMediaTests(unittest.TestCase):
    def test_parse_log_entries_groups_traceback_lines(self):
        text = (
            "2026-06-06 10:00:00 | ERROR    | abc123 | leon.errors | file.py:1 | Fehler\n"
            "Traceback line\n"
            "2026-06-06 10:00:01 | INFO     | - | leon | app.py:1 | OK\n"
        )

        entries = parse_log_entries(text)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["request_id"], "abc123")
        self.assertEqual(entries[0]["trace"], ["Traceback line"])

    def test_decode_image_base64_accepts_png_and_rejects_text(self):
        png = base64.b64encode(b"\x89PNG\r\n\x1a\nrest").decode("ascii")
        raw, kind = decode_image_base64(png)

        self.assertEqual(kind, "png")
        self.assertTrue(raw.startswith(b"\x89PNG"))
        with self.assertRaises(ValueError):
            decode_image_base64(base64.b64encode(b"hello").decode("ascii"))


class BackupSecurityTests(IsolatedDatabaseTest):
    def setUp(self):
        super().setUp()
        self.old_backup_dir = backup_service.BACKUP_DIR
        self.old_health_backup_dir = health_module.BACKUP_DIR
        self.old_privacy_backup_dir = privacy_module.BACKUP_DIR
        self.backup_dir = os.path.join(self.tmp.name, "backup")
        os.makedirs(self.backup_dir, exist_ok=True)
        backup_service.BACKUP_DIR = self.backup_dir
        health_module.BACKUP_DIR = self.backup_dir
        privacy_module.BACKUP_DIR = self.backup_dir
        database.init_db()

    def tearDown(self):
        backup_service.BACKUP_DIR = self.old_backup_dir
        health_module.BACKUP_DIR = self.old_health_backup_dir
        privacy_module.BACKUP_DIR = self.old_privacy_backup_dir
        super().tearDown()

    def test_backup_creates_checksum_manifest_and_verifies(self):
        result = backup_service.backup_db()

        backup_path = Path(result["path"])
        manifest_path = backup_path.with_suffix(backup_path.suffix + ".sha256.json")

        self.assertTrue(result["ok"])
        self.assertTrue(backup_path.exists())
        self.assertTrue(manifest_path.exists())
        self.assertEqual(backup_service.verify_backup(backup_path)["status"], "ok")

    def test_health_reports_verified_latest_backup(self):
        backup_service.backup_db()

        with patch("utils.system_health.ollama_is_running", return_value=False):
            health = collect_health()

        checks = {c["name"]: c for c in health["checks"]}
        self.assertEqual(checks["backups"]["status"], "ok")
        self.assertEqual(checks["backups"]["verification"]["status"], "ok")

    def test_backup_verification_detects_modified_file(self):
        result = backup_service.backup_db()
        backup_path = Path(result["path"])
        with backup_path.open("ab") as handle:
            handle.write(b"changed")

        verification = backup_service.verify_backup(backup_path)

        self.assertEqual(verification["status"], "error")
        self.assertIn("Prüfsumme", verification["detail"])

    def test_restore_backup_replaces_database_after_verification(self):
        con = database.get_db()
        con.execute(
            "INSERT INTO rooms (name,model,created) VALUES (?,?,?)",
            ("Vor Restore", "llama3", datetime.now().isoformat()),
        )
        con.commit()
        con.close()
        result = backup_service.backup_db()

        con = database.get_db()
        con.execute(
            "INSERT INTO rooms (name,model,created) VALUES (?,?,?)",
            ("Nach Backup", "llama3", datetime.now().isoformat()),
        )
        con.commit()
        con.close()

        restored = backup_service.restore_backup(result["file"])

        con = database.get_db()
        names = [row["name"] for row in con.execute("SELECT name FROM rooms").fetchall()]
        con.close()

        self.assertTrue(restored["ok"])
        self.assertIn("Vor Restore", names)
        self.assertNotIn("Nach Backup", names)
        self.assertTrue((Path(self.backup_dir) / restored["before_restore"]).exists())

    def test_restore_backup_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            backup_service.restore_backup("../chats_2026-01-01.db")

    def test_backup_api_lists_and_restores_with_confirmation(self):
        con = database.get_db()
        con.execute(
            "INSERT INTO rooms (name,model,created) VALUES (?,?,?)",
            ("API Backup", "llama3", datetime.now().isoformat()),
        )
        con.commit()
        con.close()
        result = backup_service.backup_db()

        app = Flask(__name__)
        app.secret_key = "test"
        register_middleware(app)
        register_error_handlers(app)
        app.register_blueprint(auth_bp)
        app.register_blueprint(api_bp)

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["authenticated"] = True
                sess[CSRF_SESSION_KEY] = "backup-token"
            listed = client.get("/api/backups")
            blocked = client.post(
                "/api/backups/restore",
                json={"file": result["file"], "confirmation": "wrong"},
                headers={CSRF_HEADER: "backup-token"},
            )
            restored = client.post(
                "/api/backups/restore",
                json={"file": result["file"], "confirmation": result["file"]},
                headers={CSRF_HEADER: "backup-token"},
            )

        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.get_json()["backups"][0]["file"], result["file"])
        self.assertEqual(blocked.status_code, 400)
        self.assertEqual(restored.status_code, 200)
        self.assertEqual(restored.get_json()["restored"], result["file"])

    def test_privacy_purge_backups_removes_manifests_too(self):
        backup_service.backup_db()
        before = privacy_summary()

        purge_private_data(["backups"], PURGE_CONFIRMATION)
        after = privacy_summary()

        self.assertGreaterEqual(before["backup_files"], 2)
        self.assertEqual(after["backup_files"], 0)


class HealthAndPrivacyTests(IsolatedDatabaseTest):
    def setUp(self):
        super().setUp()
        database.init_db()

    def test_health_reports_database_and_ollama_warning(self):
        with patch("utils.system_health.ollama_is_running", return_value=False):
            health = collect_health()

        self.assertIn(health["status"], ("ok", "warn"))
        checks = {c["name"]: c for c in health["checks"]}
        self.assertEqual(checks["database"]["status"], "ok")
        self.assertEqual(checks["ollama"]["status"], "warn")

    def test_privacy_summary_and_purge_memory(self):
        con = database.get_db()
        con.execute(
            "INSERT INTO memory (room_id,fact,created) VALUES (?,?,?)",
            (1, "Test Fakt", datetime.now().isoformat()),
        )
        con.commit()
        con.close()

        self.assertEqual(privacy_summary()["memory"], 1)
        result = purge_private_data(["memory"], PURGE_CONFIRMATION)

        self.assertEqual(result["purged"], ["memory"])
        self.assertEqual(privacy_summary()["memory"], 0)

    def test_privacy_purge_requires_confirmation(self):
        with self.assertRaises(ValueError):
            purge_private_data(["memory"], "falsch")

    def test_health_and_privacy_api_require_login_and_work_with_session(self):
        app = Flask(__name__)
        app.secret_key = "test"
        register_middleware(app)
        register_error_handlers(app)
        app.register_blueprint(auth_bp)
        app.register_blueprint(api_bp)

        with app.test_client() as client:
            locked = client.get("/api/health")
            with client.session_transaction() as sess:
                sess["authenticated"] = True
            with patch("utils.system_health.ollama_is_running", return_value=False):
                health = client.get("/api/health")
            privacy = client.get("/api/privacy/summary")

        self.assertEqual(locked.status_code, 302)
        self.assertEqual(health.status_code, 200)
        self.assertIn("checks", health.get_json())
        self.assertEqual(privacy.status_code, 200)
        self.assertIn("confirmation", privacy.get_json())


if __name__ == "__main__":
    unittest.main()
