import os
import sqlite3
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from flask import Flask

from models import database
from routes import register_routes
from services import artifact_service
from services import chat_service
from services import profile_service
from utils.security import CSRF_HEADER, CSRF_SESSION_KEY, get_csrf_token


class UiFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db_path = database.DB_PATH
        self.old_data_dir = database.DATA_DIR
        self.old_profile_path = profile_service.PROFILE_PATH
        database.DB_PATH = os.path.join(self.tmp.name, "chats.db")
        database.DATA_DIR = self.tmp.name
        profile_service.PROFILE_PATH = os.path.join(self.tmp.name, "profile.json")
        database.init_db()
        profile_service.save_first_setup("Leon", "testpass", "testpass")

        self.app = Flask(__name__, template_folder="../templates")
        self.app.secret_key = "test"
        self.app.config.update(TESTING=True)
        register_routes(self.app)

        @self.app.context_processor
        def csrf_context():
            return {"csrf_token": get_csrf_token()}

    def tearDown(self):
        database.DB_PATH = self.old_db_path
        database.DATA_DIR = self.old_data_dir
        profile_service.PROFILE_PATH = self.old_profile_path
        self.tmp.cleanup()

    def login_session(self, client, token="ui-token"):
        with client.session_transaction() as sess:
            sess["authenticated"] = True
            sess[CSRF_SESSION_KEY] = token
        return {CSRF_HEADER: token}


class LoginAndNewChatUiFlowTests(UiFlowTestCase):
    def test_login_page_contains_csrf_and_ui_shell(self):
        with self.app.test_client() as client:
            res = client.get("/login")

        html = res.get_data(as_text=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('name="csrf-token"', html)
        self.assertIn('name="csrf_token"', html)
        self.assertIn("LEON AI", html)

    def test_first_start_setup_creates_profile_and_logs_in(self):
        os.remove(profile_service.PROFILE_PATH)
        with self.app.test_client() as client:
            page = client.get("/login")
            with client.session_transaction() as sess:
                token = sess[CSRF_SESSION_KEY]
            res = client.post(
                "/setup",
                data={
                    "first_name": "Mia",
                    "password": "sicher123",
                    "password_confirm": "sicher123",
                    "csrf_token": token,
                },
            )
            with client.session_transaction() as sess:
                authenticated = sess.get("authenticated")

        html = page.get_data(as_text=True)
        self.assertEqual(page.status_code, 200)
        self.assertIn("Erster Start", html)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(authenticated)
        self.assertEqual(profile_service.get_first_name(), "Mia")

    def test_logged_in_chat_page_exposes_artifact_and_rich_ui_controls(self):
        with self.app.test_client() as client:
            self.login_session(client)
            res = client.get("/")

        html = res.get_data(as_text=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('id="artifact-panel"', html)
        self.assertIn('id="artifact-frame"', html)
        self.assertIn('sandbox="allow-scripts"', html)
        self.assertIn('id="artifact-select"', html)
        self.assertIn("mermaid.min.js", html)
        self.assertIn("Chart.js", html)
        self.assertIn("window.LEON_PROFILE", html)

    def test_new_chat_ui_flow_creates_empty_room_and_loads_messages(self):
        with self.app.test_client() as client:
            headers = self.login_session(client)
            created = client.post(
                "/api/rooms",
                json={"name": "UI Test Chat", "model": "llama3"},
                headers=headers,
            )
            room_id = created.get_json()["id"]
            rooms = client.get("/api/rooms")
            messages = client.get(f"/api/rooms/{room_id}/messages")

        self.assertEqual(created.status_code, 200)
        self.assertEqual(messages.status_code, 200)
        self.assertEqual(messages.get_json(), [])
        self.assertTrue(any(room["id"] == room_id for room in rooms.get_json()))

    def test_login_cleans_empty_rooms_but_keeps_chats_with_messages(self):
        con = database.get_db()
        now = datetime.now().isoformat()
        con.execute("INSERT INTO rooms (name,model,created) VALUES (?,?,?)", ("Leer", "llama3", now))
        con.execute("INSERT INTO rooms (name,model,created) VALUES (?,?,?)", ("Mit Verlauf", "llama3", now))
        keep_id = con.execute("SELECT id FROM rooms WHERE name='Mit Verlauf'").fetchone()["id"]
        con.execute(
            "INSERT INTO messages (room_id,role,content,created) VALUES (?,?,?,?)",
            (keep_id, "user", "Hallo", now),
        )
        con.commit()
        con.close()

        with self.app.test_client() as client:
            client.get("/login")
            with client.session_transaction() as sess:
                token = sess[CSRF_SESSION_KEY]
            with patch("routes.auth.check_password", return_value=True):
                res = client.post("/login", data={"password": "pw", "csrf_token": token})
            self.login_session(client)
            rooms = client.get("/api/rooms").get_json()

        self.assertEqual(res.status_code, 302)
        self.assertEqual([room["name"] for room in rooms], ["Mit Verlauf"])

    def test_room_pinning_updates_order(self):
        with self.app.test_client() as client:
            headers = self.login_session(client)
            first = client.post("/api/rooms", json={"name": "Normal", "model": "llama3"}, headers=headers).get_json()
            second = client.post("/api/rooms", json={"name": "Wichtig", "model": "llama3"}, headers=headers).get_json()
            pinned = client.patch(f"/api/rooms/{second['id']}", json={"pinned": True}, headers=headers)
            rooms = client.get("/api/rooms").get_json()

        self.assertEqual(pinned.status_code, 200)
        self.assertEqual(rooms[0]["id"], second["id"])
        self.assertFalse(rooms[0]["id"] == first["id"])

    def test_stats_activity_type_filters_messages_and_tokens(self):
        con = database.get_db()
        now = datetime.now().isoformat()
        con.execute("DELETE FROM messages")
        con.executemany(
            "INSERT INTO messages (room_id,role,content,favorite,created,tokens) VALUES (?,?,?,?,?,?)",
            [
                (1, "user", "Frage", 0, now, 3),
                (1, "ai", "Antwort", 1, now, 7),
            ],
        )
        con.commit()
        con.close()

        with self.app.test_client() as client:
            self.login_session(client)
            user_stats = client.get("/api/stats?type=user").get_json()
            ai_stats = client.get("/api/stats?type=ai").get_json()
            fav_stats = client.get("/api/stats?type=favorites").get_json()

        self.assertEqual(user_stats["total_messages"], 1)
        self.assertEqual(user_stats["total_tokens"], 3)
        self.assertEqual(ai_stats["total_messages"], 1)
        self.assertEqual(ai_stats["total_tokens"], 7)
        self.assertEqual(fav_stats["total_messages"], 1)


class BranchingUiFlowTests(UiFlowTestCase):
    def seed_branching_chat(self):
        con = database.get_db()
        now = datetime.now().isoformat()
        con.execute("DELETE FROM messages")
        rows = [
            (1, None, "user", "Root"),
            (1, 1, "ai", "Antwort A"),
            (1, 2, "user", "Weiter A"),
            (1, 2, "user", "Weiter B"),
            (1, 4, "ai", "Ende B"),
        ]
        for room_id, parent_id, role, content in rows:
            con.execute(
                "INSERT INTO messages (room_id,parent_id,role,content,created,tokens) VALUES (?,?,?,?,?,?)",
                (room_id, parent_id, role, content, now, 1),
            )
        con.commit()
        con.close()

    def test_branching_messages_are_visible_and_active_path_uses_selected_leaf(self):
        self.seed_branching_chat()

        with self.app.test_client() as client:
            self.login_session(client)
            res = client.get("/api/rooms/1/messages")
        payload, _model = chat_service.build_messages(1, "Neue Frage", parent_id=5)

        messages = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len([m for m in messages if m["parent_id"] == 2]), 2)
        self.assertEqual([m["content"] for m in payload[1:]], ["Root", "Antwort A", "Weiter B", "Ende B", "Neue Frage"])

    def test_delete_messages_after_prunes_future_artifacts(self):
        self.seed_branching_chat()
        artifact_service.save_artifacts(1, [{
            "key": "branch-artifact",
            "title": "Branch Artifact",
            "lang": "HTML",
            "html": "<!doctype html><h1>Branch</h1>",
            "source": "source",
            "message_id": 5,
        }])

        with self.app.test_client() as client:
            headers = self.login_session(client)
            deleted = client.delete("/api/rooms/1/messages/after/3", headers=headers)
            artifacts = client.get("/api/rooms/1/artifacts")

        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(artifacts.get_json()["versions"], [])


class ArtifactRichOutputUiFlowTests(UiFlowTestCase):
    def test_artifact_api_persists_versions_for_preview_dropdown(self):
        with self.app.test_client() as client:
            headers = self.login_session(client)
            saved = client.post(
                "/api/rooms/1/artifacts",
                json={"artifacts": [{
                    "key": "ui-html",
                    "title": "Landing Preview",
                    "lang": "HTML",
                    "html": "<!doctype html><main class='p-6 text-red-500'>Hallo</main>",
                    "source": "```html\n<main>Hallo</main>\n```",
                    "message_id": None,
                }]},
                headers=headers,
            )
            artifact_id = saved.get_json()["saved"][0]
            before_delete = client.get("/api/rooms/1/artifacts")
            deleted = client.delete(f"/api/rooms/1/artifacts/{artifact_id}", headers=headers)
            listed = client.get("/api/rooms/1/artifacts")

        version = before_delete.get_json()["versions"][0]
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(version["title"], "Landing Preview")
        self.assertIn("text-red-500", version["html"])
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(listed.get_json()["versions"], [])

    def test_frontend_contract_covers_pyodide_mermaid_and_charts(self):
        root = Path(__file__).resolve().parents[1]
        chat_js = (root / "static/js/chat.js").read_text(encoding="utf-8")
        artifacts_js = (root / "static/js/artifacts.js").read_text(encoding="utf-8")
        index_html = (root / "templates/index.html").read_text(encoding="utf-8")

        self.assertIn("Leon.renderMermaidBlock", chat_js)
        self.assertIn("Leon.renderChartBlock", chat_js)
        self.assertIn("Leon.buildPyodideHtml", artifacts_js)
        self.assertIn("loadPyodide", artifacts_js)
        self.assertIn("downloadAllArtifactsZip", artifacts_js)
        self.assertIn("deleteArtifactVersion", artifacts_js)
        self.assertIn("artifact-frame", index_html)


if __name__ == "__main__":
    unittest.main()
