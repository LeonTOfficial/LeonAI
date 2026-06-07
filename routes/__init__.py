"""Route registration."""
from routes.api import api_bp
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.middleware import register_middleware
from routes.pages import pages_bp


def register_routes(app) -> None:
    register_middleware(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(chat_bp)
