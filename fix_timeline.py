#!/usr/bin/env python3
"""Fix the timeline JSON by removing entries that reference missing snapshot files."""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
WEIGHTS_JSON = PROJECT_ROOT / "frontend" / "exports" / "mlp_weights.json"
EXPORTS_DIR = PROJECT_ROOT / "frontend" / "exports" / "mlp_weights"

def fix_timeline():
    """Remove timeline entries that reference missing snapshot files."""
    if not WEIGHTS_JSON.exists():
        print(f"[ERROR] Weights JSON not found: {WEIGHTS_JSON}")
        return False
    
    if not EXPORTS_DIR.exists():
        print(f"[ERROR] Exports directory not found: {EXPORTS_DIR}")
        return False
    
    # Load the timeline JSON
    with open(WEIGHTS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get list of existing snapshot files
    existing_files = set()
    for file in EXPORTS_DIR.glob("*.json"):
        existing_files.add(file.name)
    
    print(f"Found {len(existing_files)} existing snapshot files")
    print(f"Original timeline has {len(data.get('timeline', []))} entries")
    
    # Filter timeline to only include entries with existing files
    original_timeline = data.get('timeline', [])
    filtered_timeline = []
    removed_ids = []
    
    for entry in original_timeline:
        weights_path = entry.get('weights', {}).get('path', '')
        filename = os.path.basename(weights_path)
        
        if filename in existing_files:
            filtered_timeline.append(entry)
        else:
            removed_ids.append(entry.get('id', 'unknown'))
    
    if removed_ids:
        print(f"\nRemoving {len(removed_ids)} entries with missing files:")
        for entry_id in removed_ids:
            print(f"  - {entry_id}")
    
    # Update the timeline
    data['timeline'] = filtered_timeline
    
    # Backup the original file
    backup_path = WEIGHTS_JSON.with_suffix('.json.backup')
    if not backup_path.exists():
        print(f"\nCreating backup: {backup_path}")
        # Load original data again for backup
        with open(WEIGHTS_JSON, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(original_data, f, indent=2, ensure_ascii=False)
    
    # Write the fixed timeline
    print(f"\nWriting fixed timeline with {len(filtered_timeline)} entries...")
    with open(WEIGHTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("[OK] Timeline fixed successfully!")
    return True

if __name__ == "__main__":
    fix_timeline()

