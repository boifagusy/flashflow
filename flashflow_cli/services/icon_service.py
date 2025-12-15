"""
Icon Service for FlashFlow
Provides support for various icon packs out of the box
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class IconPack:
    """Represents an icon pack with its metadata and icons"""
    
    def __init__(self, name: str, version: str, icons: Dict[str, str], prefix: str = ""):
        self.name = name
        self.version = version
        self.icons = icons
        self.prefix = prefix
    
    def get_icon(self, icon_name: str) -> Optional[str]:
        """Get the icon path or class for a given icon name"""
        return self.icons.get(icon_name)
    
    def get_prefixed_icon(self, icon_name: str) -> Optional[str]:
        """Get the icon with the pack prefix"""
        icon = self.get_icon(icon_name)
        if icon and self.prefix:
            return f"{self.prefix}-{icon}"
        return icon


class IconService:
    """Main service for managing icon packs in FlashFlow"""
    
    def __init__(self):
        self.icon_packs: Dict[str, IconPack] = {}
        self.default_pack = "material-icons"
        self._load_builtin_icon_packs()
    
    def _load_builtin_icon_packs(self):
        """Load built-in icon packs"""
        # Material Icons (default)
        material_icons = {
            "home": "home",
            "dashboard": "dashboard",
            "settings": "settings",
            "user": "person",
            "users": "people",
            "add": "add",
            "edit": "edit",
            "delete": "delete",
            "save": "save",
            "cancel": "cancel",
            "search": "search",
            "filter": "filter_list",
            "sort": "sort",
            "menu": "menu",
            "close": "close",
            "check": "check",
            "error": "error",
            "info": "info",
            "warning": "warning",
            "help": "help",
            "arrow_back": "arrow_back",
            "arrow_forward": "arrow_forward",
            "expand_more": "expand_more",
            "expand_less": "expand_less",
            "favorite": "favorite",
            "share": "share",
            "download": "download",
            "upload": "upload",
            "print": "print",
            "email": "email",
            "phone": "phone",
            "location": "location_on",
            "calendar": "calendar_today",
            "time": "schedule",
            "lock": "lock",
            "unlock": "lock_open",
            "visibility": "visibility",
            "visibility_off": "visibility_off",
            "refresh": "refresh",
            "undo": "undo",
            "redo": "redo"
        }
        
        self.icon_packs["material-icons"] = IconPack(
            name="material-icons",
            version="1.0.0",
            icons=material_icons,
            prefix="material-icons"
        )
        
        # Font Awesome Icons
        font_awesome_icons = {
            "home": "fa-home",
            "dashboard": "fa-tachometer-alt",
            "settings": "fa-cog",
            "user": "fa-user",
            "users": "fa-users",
            "add": "fa-plus",
            "edit": "fa-edit",
            "delete": "fa-trash",
            "save": "fa-save",
            "cancel": "fa-times",
            "search": "fa-search",
            "filter": "fa-filter",
            "sort": "fa-sort",
            "menu": "fa-bars",
            "close": "fa-times",
            "check": "fa-check",
            "error": "fa-exclamation-circle",
            "info": "fa-info-circle",
            "warning": "fa-exclamation-triangle",
            "help": "fa-question-circle",
            "arrow_back": "fa-arrow-left",
            "arrow_forward": "fa-arrow-right",
            "expand_more": "fa-chevron-down",
            "expand_less": "fa-chevron-up",
            "favorite": "fa-heart",
            "share": "fa-share",
            "download": "fa-download",
            "upload": "fa-upload",
            "print": "fa-print",
            "email": "fa-envelope",
            "phone": "fa-phone",
            "location": "fa-map-marker",
            "calendar": "fa-calendar",
            "time": "fa-clock",
            "lock": "fa-lock",
            "unlock": "fa-unlock",
            "visibility": "fa-eye",
            "visibility_off": "fa-eye-slash",
            "refresh": "fa-sync",
            "undo": "fa-undo",
            "redo": "fa-redo"
        }
        
        self.icon_packs["font-awesome"] = IconPack(
            name="font-awesome",
            version="5.15.4",
            icons=font_awesome_icons,
            prefix="fas"
        )
        
        # Bootstrap Icons
        bootstrap_icons = {
            "home": "bi-house",
            "dashboard": "bi-speedometer2",
            "settings": "bi-gear",
            "user": "bi-person",
            "users": "bi-people",
            "add": "bi-plus",
            "edit": "bi-pencil",
            "delete": "bi-trash",
            "save": "bi-save",
            "cancel": "bi-x",
            "search": "bi-search",
            "filter": "bi-funnel",
            "sort": "bi-sort-down",
            "menu": "bi-list",
            "close": "bi-x",
            "check": "bi-check",
            "error": "bi-exclamation-circle",
            "info": "bi-info-circle",
            "warning": "bi-exclamation-triangle",
            "help": "bi-question-circle",
            "arrow_back": "bi-arrow-left",
            "arrow_forward": "bi-arrow-right",
            "expand_more": "bi-chevron-down",
            "expand_less": "bi-chevron-up",
            "favorite": "bi-heart",
            "share": "bi-share",
            "download": "bi-download",
            "upload": "bi-upload",
            "print": "bi-printer",
            "email": "bi-envelope",
            "phone": "bi-telephone",
            "location": "bi-geo-alt",
            "calendar": "bi-calendar",
            "time": "bi-clock",
            "lock": "bi-lock",
            "unlock": "bi-unlock",
            "visibility": "bi-eye",
            "visibility_off": "bi-eye-slash",
            "refresh": "bi-arrow-repeat",
            "undo": "bi-arrow-counterclockwise",
            "redo": "bi-arrow-clockwise"
        }
        
        self.icon_packs["bootstrap-icons"] = IconPack(
            name="bootstrap-icons",
            version="1.10.0",
            icons=bootstrap_icons,
            prefix="bi"
        )
    
    def get_icon_pack(self, pack_name: str) -> Optional[IconPack]:
        """Get an icon pack by name"""
        return self.icon_packs.get(pack_name)
    
    def get_icon(self, icon_name: str, pack_name: Optional[str] = None) -> Optional[str]:
        """Get an icon from a specific pack or the default pack"""
        if pack_name is None:
            pack_name = self.default_pack
        
        pack = self.get_icon_pack(pack_name)
        if pack:
            return pack.get_icon(icon_name)
        return None
    
    def get_prefixed_icon(self, icon_name: str, pack_name: Optional[str] = None) -> Optional[str]:
        """Get an icon with its prefix from a specific pack or the default pack"""
        if pack_name is None:
            pack_name = self.default_pack
        
        pack = self.get_icon_pack(pack_name)
        if pack:
            return pack.get_prefixed_icon(icon_name)
        return None
    
    def set_default_pack(self, pack_name: str) -> bool:
        """Set the default icon pack"""
        if pack_name in self.icon_packs:
            self.default_pack = pack_name
            return True
        return False
    
    def add_icon_pack(self, pack: IconPack):
        """Add a custom icon pack"""
        self.icon_packs[pack.name] = pack
    
    def get_available_packs(self) -> List[str]:
        """Get list of available icon pack names"""
        return list(self.icon_packs.keys())
    
    def get_pack_metadata(self, pack_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for an icon pack"""
        pack = self.get_icon_pack(pack_name)
        if pack:
            return {
                "name": pack.name,
                "version": pack.version,
                "icon_count": len(pack.icons)
            }
        return None


# Global instance
icon_service = IconService()