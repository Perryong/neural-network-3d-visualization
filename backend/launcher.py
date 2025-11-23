"""Launcher for Neural Network Visualization application.

This script handles:
1. Checking and optionally training the model
2. Checking and optionally preparing MNIST test assets
3. Starting the Flask server
4. Opening the browser automatically
"""

from __future__ import annotations

import argparse
import threading
import time
import webbrowser

from backend.server import run_server
from backend.services import asset_service, training_service


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
  python -m backend.launcher

  # Force training even if weights exist
  python -m backend.launcher --train --force-train

  # Skip training entirely
  python -m backend.launcher --no-train --no-mnist-prep

  # Use custom port
  python -m backend.launcher --port 8080

  # Don't open browser automatically
  python -m backend.launcher --no-browser
        """,
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run Flask server in debug mode",
    )
    
    args = parser.parse_args()
    
    print("Neural Network Visualization - Application Launcher")
    print("=" * 60)
    
    # Validate timeline (fix missing snapshot references)
    timeline_result = training_service.validate_timeline(fix=True)
    if not timeline_result.get("valid") and timeline_result.get("fixed"):
        print(f"[INFO] {timeline_result.get('message', 'Timeline validated')}")
    
    # Check and prepare MNIST assets
    if not args.no_mnist_prep:
        if args.prepare_mnist or args.force_prepare_mnist:
            result = asset_service.prepare_mnist_assets(
                skip_if_exists=not args.force_prepare_mnist,
                force=args.force_prepare_mnist
            )
            if result.get('success'):
                print(f"[OK] {result.get('message')}")
            else:
                print(f"[ERROR] {result.get('error')}")
        elif not asset_service.check_mnist_assets_exist():
            print("[WARNING] MNIST assets not found. Use --prepare-mnist to create them.")
            print("  The app may not work correctly without MNIST assets.")
    else:
        print("[SKIP] Skipping MNIST asset preparation (--no-mnist-prep)")
    
    # Check and run training
    if not args.no_train:
        if args.train or args.force_train or not training_service.check_weights_exist():
            if not training_service.check_weights_exist():
                print("\n[WARNING] Weights not found. Training will be required.")
            result = training_service.run_training(
                skip_if_exists=not args.force_train,
                force=args.force_train
            )
            if result.get('success'):
                print(f"[OK] {result.get('message')}")
            else:
                print(f"[ERROR] {result.get('error')}")
        else:
            print("[OK] Weights exist, skipping training.")
            print(f"  Use --force-train to retrain.")
    else:
        print("[SKIP] Skipping training (--no-train)")
        if not training_service.check_weights_exist():
            print("[WARNING] Weights not found. The app may not work correctly.")
    
    # Open browser
    url = f"http://{args.host}:{args.port}"
    if not args.no_browser:
        open_browser(url)
    
    # Start server (this blocks)
    print("\nPress Ctrl+C to stop the server.\n")
    try:
        run_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        print("[OK] Server stopped.")


if __name__ == "__main__":
    main()

