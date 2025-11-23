#!/usr/bin/env python3
"""Main entry point to run the Neural Network Visualization application.

This script handles:
1. Checking and optionally training the model
2. Checking and optionally preparing MNIST test assets
3. Starting a web server to serve the frontend
4. Opening the browser automatically
"""

from __future__ import annotations

import argparse
import http.server
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.resolve()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TRAINING_SCRIPT = BACKEND_DIR / "training" / "mlp_train.py"
MNIST_PREP_SCRIPT = BACKEND_DIR / "tools" / "mnist_assets" / "prepare_mnist_test_assets.py"

# Asset paths
WEIGHTS_JSON = PROJECT_ROOT / "frontend" / "exports" / "mlp_weights.json"
MNIST_MANIFEST = PROJECT_ROOT / "frontend" / "assets" / "data" / "mnist-test-manifest.json"
FRONTEND_INDEX = PROJECT_ROOT / "index.html"

# Default server configuration
DEFAULT_PORT = 8000
DEFAULT_HOST = "localhost"


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler that serves from project root with proper path mapping."""

    def __init__(self, *args: Any, root_dir: Path | None = None, **kwargs: Any) -> None:
        if root_dir:
            self.root_dir = Path(root_dir).resolve()
        else:
            self.root_dir = PROJECT_ROOT
        super().__init__(*args, **kwargs)

    def translate_path(self, path: str) -> str:
        """Translate URL path to filesystem path with proper mapping."""
        # Remove query string and fragment
        path = path.split("?")[0].split("#")[0]
        
        # Normalize path
        path = path.lstrip("/")
        
        # Handle root - serve root index.html
        if path == "" or path == "/" or path == "index.html":
            if FRONTEND_INDEX.exists():
                return str(FRONTEND_INDEX)
            # Fallback to frontend index.html
            frontend_index = FRONTEND_DIR / "index.html"
            if frontend_index.exists():
                return str(frontend_index)
            return str(self.root_dir)
        
        # Map assets/ to frontend/assets/
        if path.startswith("assets/"):
            # Check frontend/assets/ first
            frontend_asset_path = FRONTEND_DIR / path
            if frontend_asset_path.exists():
                return str(frontend_asset_path)
            # Fallback to root assets/
            root_asset_path = self.root_dir / path
            if root_asset_path.exists():
                return str(root_asset_path)
        
        # Map exports/ to frontend/exports/
        if path.startswith("exports/"):
            frontend_export_path = FRONTEND_DIR / path
            if frontend_export_path.exists():
                return str(frontend_export_path)
            root_export_path = self.root_dir / path
            if root_export_path.exists():
                return str(root_export_path)
        
        # Check if path exists in root first
        root_path = self.root_dir / path
        if root_path.exists() and root_path.is_file():
            return str(root_path)
        
        # Check frontend directory
        frontend_path = FRONTEND_DIR / path
        if frontend_path.exists() and frontend_path.is_file():
            return str(frontend_path)
        
        # Fall back to root directory
        return str(root_path)
    
    def end_headers(self) -> None:
        """Add CORS headers for development."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()
    
    def log_message(self, format: str, *args: Any) -> None:
        """Custom log message format."""
        print(f"[HTTP] {format % args}")


def check_weights_exist() -> bool:
    """Check if trained weights exist."""
    return WEIGHTS_JSON.exists() and WEIGHTS_JSON.stat().st_size > 0


def check_mnist_assets_exist() -> bool:
    """Check if MNIST test assets exist."""
    return MNIST_MANIFEST.exists()


def run_training(skip_if_exists: bool = True) -> bool:
    """Run the training script if weights don't exist."""
    if skip_if_exists and check_weights_exist():
        print("[OK] Weights already exist, skipping training.")
        print(f"  Location: {WEIGHTS_JSON}")
        return True
    
    print("Training model...")
    print(f"  Script: {TRAINING_SCRIPT}")
    
    if not TRAINING_SCRIPT.exists():
        print(f"[ERROR] Training script not found: {TRAINING_SCRIPT}")
        return False
    
    try:
        # Ensure export directory exists
        WEIGHTS_JSON.parent.mkdir(parents=True, exist_ok=True)
        
        # Change to project root to run training
        # The training script exports relative to current directory
        # Convert absolute path to relative path from project root
        try:
            export_path = WEIGHTS_JSON.relative_to(PROJECT_ROOT)
        except ValueError:
            # If not relative to project root, use as-is
            export_path = WEIGHTS_JSON
        
        result = subprocess.run(
            [sys.executable, str(TRAINING_SCRIPT), "--export-path", str(export_path)],
            cwd=PROJECT_ROOT,
            check=False,
        )
        
        if result.returncode == 0:
            print("[OK] Training completed successfully!")
            return True
        else:
            print(f"[ERROR] Training failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"[ERROR] Error running training: {e}")
        return False


def validate_timeline() -> bool:
    """Validate that timeline entries reference existing snapshot files."""
    if not WEIGHTS_JSON.exists():
        return True  # Not an error if weights don't exist yet
    
    try:
        import json
        
        with open(WEIGHTS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timeline = data.get('timeline', [])
        if not timeline:
            return True
        
        # Get existing snapshot files
        exports_dir = WEIGHTS_JSON.parent / "mlp_weights"
        if not exports_dir.exists():
            return True
        
        existing_files = {f.name for f in exports_dir.glob("*.json")}
        
        # Check for missing files
        missing_entries = []
        for entry in timeline:
            weights_path = entry.get('weights', {}).get('path', '')
            filename = os.path.basename(weights_path)
            if filename and filename not in existing_files:
                missing_entries.append(entry)
        
        if missing_entries:
            print(f"\n[WARNING] Timeline references {len(missing_entries)} missing snapshot files")
            print("  Removing invalid timeline entries...")
            
            # Filter timeline
            filtered_timeline = [
                entry for entry in timeline
                if os.path.basename(entry.get('weights', {}).get('path', '')) in existing_files
            ]
            
            # Backup original
            backup_path = WEIGHTS_JSON.with_suffix('.json.backup')
            if not backup_path.exists():
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Update timeline
            data['timeline'] = filtered_timeline
            with open(WEIGHTS_JSON, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"  Fixed timeline: {len(filtered_timeline)} valid entries remaining")
            return True
        
        return True
    except Exception as e:
        print(f"[WARNING] Could not validate timeline: {e}")
        return True  # Don't fail startup if validation fails


def prepare_mnist_assets(skip_if_exists: bool = True) -> bool:
    """Prepare MNIST test assets if they don't exist."""
    if skip_if_exists and check_mnist_assets_exist():
        print("[OK] MNIST assets already exist, skipping preparation.")
        print(f"  Location: {MNIST_MANIFEST}")
        return True
    
    print("Preparing MNIST test assets...")
    print(f"  Script: {MNIST_PREP_SCRIPT}")
    
    if not MNIST_PREP_SCRIPT.exists():
        print(f"[ERROR] MNIST preparation script not found: {MNIST_PREP_SCRIPT}")
        return False
    
    try:
        # Ensure output directory exists
        MNIST_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        
        # Change to project root to run preparation
        result = subprocess.run(
            [
                sys.executable,
                str(MNIST_PREP_SCRIPT),
                "--output-dir",
                str(MNIST_MANIFEST.parent),
            ],
            cwd=PROJECT_ROOT,
            check=False,
        )
        
        if result.returncode == 0:
            print("[OK] MNIST assets prepared successfully!")
            return True
        else:
            print(f"[ERROR] MNIST preparation failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"[ERROR] Error preparing MNIST assets: {e}")
        return False


def start_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> socketserver.TCPServer:
    """Start the HTTP server."""
    handler = lambda *args, **kwargs: CustomHTTPRequestHandler(
        *args, root_dir=PROJECT_ROOT, **kwargs
    )
    
    server = socketserver.TCPServer((host, port), handler, bind_and_activate=False)
    server.allow_reuse_address = True
    
    try:
        server.server_bind()
        server.server_activate()
        print(f"\n{'='*60}")
        print(f"Server started successfully!")
        print(f"{'='*60}")
        print(f"Local:   http://{host}:{port}")
        print(f"Network: http://127.0.0.1:{port}")
        print(f"\nServing from: {PROJECT_ROOT}")
        print(f"{'='*60}\n")
        return server
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"[ERROR] Port {port} is already in use. Try a different port with --port")
        else:
            print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)


def open_browser(url: str, delay: float = 1.0) -> None:
    """Open browser after a short delay."""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"[OK] Browser opened: {url}")
        except Exception as e:
            print(f"[ERROR] Failed to open browser: {e}")
            print(f"  Please open manually: {url}")
    
    thread = threading.Thread(target=_open, daemon=True)
    thread.start()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the Neural Network Visualization application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (skip training/assets if they exist)
  python main.py

  # Force training even if weights exist
  python main.py --train --force-train

  # Skip training entirely
  python main.py --no-train --no-mnist-prep

  # Use custom port
  python main.py --port 8080

  # Don't open browser automatically
  python main.py --no-browser
        """,
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOST,
        help=f"Host to bind to (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to bind to (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Run training if weights don't exist",
    )
    parser.add_argument(
        "--force-train",
        action="store_true",
        help="Force training even if weights exist",
    )
    parser.add_argument(
        "--no-train",
        action="store_true",
        help="Skip training entirely",
    )
    parser.add_argument(
        "--prepare-mnist",
        action="store_true",
        help="Prepare MNIST test assets if they don't exist",
    )
    parser.add_argument(
        "--force-prepare-mnist",
        action="store_true",
        help="Force MNIST asset preparation even if they exist",
    )
    parser.add_argument(
        "--no-mnist-prep",
        action="store_true",
        help="Skip MNIST asset preparation entirely",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically",
    )
    
    args = parser.parse_args()
    
    print("Neural Network Visualization - Application Launcher")
    print("=" * 60)
    
    # Validate timeline (fix missing snapshot references)
    if WEIGHTS_JSON.exists():
        validate_timeline()
    
    # Check and prepare MNIST assets
    if not args.no_mnist_prep:
        if args.prepare_mnist or args.force_prepare_mnist:
            prepare_mnist_assets(skip_if_exists=not args.force_prepare_mnist)
        elif not check_mnist_assets_exist():
            print("[WARNING] MNIST assets not found. Use --prepare-mnist to create them.")
            print("  The app may not work correctly without MNIST assets.")
    else:
        print("[SKIP] Skipping MNIST asset preparation (--no-mnist-prep)")
    
    # Check and run training
    if not args.no_train:
        if args.train or args.force_train or not check_weights_exist():
            if not check_weights_exist():
                print("\n[WARNING] Weights not found. Training will be required.")
            run_training(skip_if_exists=not args.force_train)
        else:
            print("[OK] Weights exist, skipping training.")
            print(f"  Use --force-train to retrain.")
    else:
        print("[SKIP] Skipping training (--no-train)")
        if not check_weights_exist():
            print("[WARNING] Weights not found. The app may not work correctly.")
    
    # Verify essential files exist
    if not FRONTEND_INDEX.exists():
        print(f"\n[ERROR] Frontend index.html not found: {FRONTEND_INDEX}")
        print("  Please ensure the frontend files are in the correct location.")
        sys.exit(1)
    
    # Start server
    try:
        server = start_server(host=args.host, port=args.port)
        url = f"http://{args.host}:{args.port}"
        
        # Open browser
        if not args.no_browser:
            open_browser(url)
        
        # Serve requests
        print("Press Ctrl+C to stop the server.\n")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()
        print("[OK] Server stopped.")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

