"""Flask server for Neural Network Visualization backend."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.api.routes import api_bp

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__, static_folder=None)
    
    # Enable CORS for development
    CORS(app)
    
    # Register API blueprint
    app.register_blueprint(api_bp)
    
    # Serve static files from frontend directory
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path: str):
        """Serve frontend files."""
        # Don't serve API routes as static files
        if path.startswith('api/'):
            from flask import abort
            abort(404)
        
        if not path or path == 'index.html':
            return send_from_directory(str(FRONTEND_DIR), 'index.html')
        
        # Check if file exists in frontend directory
        file_path = FRONTEND_DIR / path
        if file_path.exists() and file_path.is_file():
            # Determine the directory and filename
            directory = file_path.parent
            filename = file_path.name
            return send_from_directory(str(directory), filename)
        
        # Fallback to index.html for SPA routing
        return send_from_directory(str(FRONTEND_DIR), 'index.html')
    
    return app


def run_server(host: str = "localhost", port: int = 8000, debug: bool = False) -> None:
    """Run the Flask development server."""
    app = create_app()
    print(f"\n{'='*60}")
    print(f"Server starting...")
    print(f"{'='*60}")
    print(f"API:     http://{host}:{port}/api/v1")
    print(f"Frontend: http://{host}:{port}/")
    print(f"\nServing from: {FRONTEND_DIR}")
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server()

