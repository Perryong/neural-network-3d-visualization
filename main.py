#!/usr/bin/env python3
"""Main entry point to run the Neural Network Visualization application.

This is a compatibility wrapper that calls the new backend launcher.
For new code, use: python -m backend.launcher
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Import and run the launcher
if __name__ == "__main__":
    from backend.launcher import main
    main()
