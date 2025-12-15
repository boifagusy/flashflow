"""
FlashFlow .flow file parser
Converts .flow syntax into FlashFlow IR (Intermediate Representation)
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any, List
from .core import FlashFlowIR
from .services.default_ui_service import default_ui_service

# DEPRECATED: This module has been moved to core/parser/parser.py
# This stub will be removed in a future version
import warnings
warnings.warn("flashflow_cli.parser is deprecated, use core.parser.parser instead", DeprecationWarning, stacklevel=2)

from core.parser.parser import *
