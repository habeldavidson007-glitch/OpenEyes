"""
Success Pattern Learner - Adaptive Fallback System

Learns from successful query outcomes to enable intelligent fallbacks.
Instead of rigidly halting when requirements aren't met, the system
checks historical success patterns for similar queries and dynamically
adjusts requirements.

Key Features:
- Observes successful queries and extracts patterns (domain, tier, fragment roles)
- Stores patterns in persistent JSON cache
- Enables adaptive tier downgrade when similar low-risk queries succeeded
- Maintains safety while improving responsiveness
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class SuccessPatternLearner:
    """Learns and applies success patterns for adaptive fallbacks."""
    
    def __init__(self, cache_path: str = None):
