"""
FlashFlow Core Classes
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# DEPRECATED: This module has been moved to core/framework.py
# This stub will be removed in a future version
import warnings
warnings.warn("flashflow_cli.core is deprecated, use core.framework instead", DeprecationWarning, stacklevel=2)

# Import classes from the new location with different names to avoid conflicts
from core.framework import FlashFlowConfig as NewFlashFlowConfig
from core.framework import FlashFlowProject as NewFlashFlowProject
from core.framework import FlashFlowIR as NewFlashFlowIR

# Re-export with original names for backward compatibility
FlashFlowConfig = NewFlashFlowConfig
FlashFlowProject = NewFlashFlowProject
FlashFlowIR = NewFlashFlowIR
