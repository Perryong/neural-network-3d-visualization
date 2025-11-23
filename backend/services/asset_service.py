"""Asset service for MNIST test data preparation and management."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
BACKEND_DIR = PROJECT_ROOT / "backend"
MNIST_PREP_SCRIPT = BACKEND_DIR / "tools" / "mnist_assets" / "prepare_mnist_test_assets.py"
MNIST_MANIFEST = PROJECT_ROOT / "frontend" / "assets" / "data" / "mnist-test-manifest.json"


def check_mnist_assets_exist() -> bool:
    """Check if MNIST test assets exist."""
    return MNIST_MANIFEST.exists()


def prepare_mnist_assets(skip_if_exists: bool = True, force: bool = False) -> dict[str, Any]:
    """Prepare MNIST test assets if they don't exist.
    
    Args:
        skip_if_exists: If True, skip preparation if assets already exist
        force: If True, force preparation even if assets exist
        
    Returns:
        Dictionary with 'success', 'message', and optional 'error' keys
    """
    if not force and skip_if_exists and check_mnist_assets_exist():
        return {
            "success": True,
            "message": "MNIST assets already exist, skipping preparation.",
            "location": str(MNIST_MANIFEST)
        }
    
    if not MNIST_PREP_SCRIPT.exists():
        return {
            "success": False,
            "error": f"MNIST preparation script not found: {MNIST_PREP_SCRIPT}"
        }
    
    try:
        # Ensure output directory exists
        MNIST_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            [
                sys.executable,
                str(MNIST_PREP_SCRIPT),
                "--output-dir",
                str(MNIST_MANIFEST.parent),
            ],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "MNIST assets prepared successfully!",
                "location": str(MNIST_MANIFEST)
            }
        else:
            return {
                "success": False,
                "error": f"MNIST preparation failed with exit code {result.returncode}",
                "stderr": result.stderr
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing MNIST assets: {e}"
        }


def get_mnist_status() -> dict[str, Any]:
    """Get status of MNIST assets.
    
    Returns:
        Dictionary with MNIST asset status information
    """
    exists = check_mnist_assets_exist()
    
    result = {
        "exists": exists,
        "manifest_path": str(MNIST_MANIFEST)
    }
    
    if exists:
        try:
            import json
            with open(MNIST_MANIFEST, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            result["num_samples"] = manifest_data.get('numSamples', 0)
            result["image_shape"] = manifest_data.get('imageShape', [])
            result["image_file"] = manifest_data.get('image', {}).get('file', '')
            result["labels_file"] = manifest_data.get('labels', {}).get('file', '')
        except Exception as e:
            result["error"] = f"Could not read manifest: {e}"
    else:
        result["message"] = "MNIST assets not found. Use prepare-mnist endpoint to create them."
    
    return result

