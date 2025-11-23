"""Training service for neural network model training and validation."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
BACKEND_DIR = PROJECT_ROOT / "backend"
TRAINING_SCRIPT = BACKEND_DIR / "training" / "mlp_train.py"
WEIGHTS_JSON = PROJECT_ROOT / "frontend" / "exports" / "mlp_weights.json"


def check_weights_exist() -> bool:
    """Check if trained weights exist."""
    return WEIGHTS_JSON.exists() and WEIGHTS_JSON.stat().st_size > 0


def run_training(skip_if_exists: bool = True, force: bool = False) -> dict[str, Any]:
    """Run the training script if weights don't exist.
    
    Args:
        skip_if_exists: If True, skip training if weights already exist
        force: If True, force training even if weights exist
        
    Returns:
        Dictionary with 'success', 'message', and optional 'error' keys
    """
    if not force and skip_if_exists and check_weights_exist():
        return {
            "success": True,
            "message": "Weights already exist, skipping training.",
            "location": str(WEIGHTS_JSON)
        }
    
    if not TRAINING_SCRIPT.exists():
        return {
            "success": False,
            "error": f"Training script not found: {TRAINING_SCRIPT}"
        }
    
    try:
        # Ensure export directory exists
        WEIGHTS_JSON.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert absolute path to relative path from project root
        try:
            export_path = WEIGHTS_JSON.relative_to(PROJECT_ROOT)
        except ValueError:
            export_path = WEIGHTS_JSON
        
        result = subprocess.run(
            [sys.executable, str(TRAINING_SCRIPT), "--export-path", str(export_path)],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Training completed successfully!",
                "location": str(WEIGHTS_JSON)
            }
        else:
            return {
                "success": False,
                "error": f"Training failed with exit code {result.returncode}",
                "stderr": result.stderr
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error running training: {e}"
        }


def validate_timeline(fix: bool = False) -> dict[str, Any]:
    """Validate that timeline entries reference existing snapshot files.
    
    Args:
        fix: If True, automatically fix missing entries by removing them
        
    Returns:
        Dictionary with validation results
    """
    if not WEIGHTS_JSON.exists():
        return {
            "valid": True,
            "message": "Weights file does not exist yet, nothing to validate"
        }
    
    try:
        with open(WEIGHTS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timeline = data.get('timeline', [])
        if not timeline:
            return {
                "valid": True,
                "message": "Timeline is empty"
            }
        
        # Get existing snapshot files
        exports_dir = WEIGHTS_JSON.parent / "mlp_weights"
        if not exports_dir.exists():
            return {
                "valid": True,
                "message": "Exports directory does not exist"
            }
        
        existing_files = {f.name for f in exports_dir.glob("*.json")}
        
        # Check for missing files
        missing_entries = []
        for entry in timeline:
            weights_path = entry.get('weights', {}).get('path', '')
            filename = os.path.basename(weights_path)
            if filename and filename not in existing_files:
                missing_entries.append(entry)
        
        if not missing_entries:
            return {
                "valid": True,
                "message": "All timeline entries are valid",
                "total_entries": len(timeline)
            }
        
        result = {
            "valid": False,
            "message": f"Found {len(missing_entries)} missing snapshot files",
            "missing_count": len(missing_entries),
            "total_entries": len(timeline),
            "missing_ids": [entry.get('id', 'unknown') for entry in missing_entries]
        }
        
        if fix:
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
            
            result["fixed"] = True
            result["remaining_entries"] = len(filtered_timeline)
            result["message"] = f"Fixed timeline: {len(filtered_timeline)} valid entries remaining"
        
        return result
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Could not validate timeline: {e}"
        }


def get_model_info() -> dict[str, Any]:
    """Get information about the trained model.
    
    Returns:
        Dictionary with model information
    """
    if not check_weights_exist():
        return {
            "exists": False,
            "message": "Model weights do not exist"
        }
    
    try:
        with open(WEIGHTS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        network = data.get('network', {})
        timeline = data.get('timeline', [])
        
        return {
            "exists": True,
            "location": str(WEIGHTS_JSON),
            "architecture": network.get('architecture', []),
            "normalization": network.get('normalization', {}),
            "layers": len(network.get('layers', [])),
            "timeline_entries": len(timeline),
            "output_dim": network.get('output_dim', None)
        }
    except Exception as e:
        return {
            "exists": True,
            "error": f"Could not read model info: {e}"
        }

