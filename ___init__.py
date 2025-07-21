# gui/__init__.py
"""
SKY SHIELD GUI Package
Modern GUI system for Sky Shield Air Defense System
"""

__version__ = "2.0.0"
__author__ = "Sky Shield Team"

from .main_window import SkyShieldMainWindow
from .controllers.app_controller import AppController

__all__ = [
    'SkyShieldMainWindow',
    'AppController'
]