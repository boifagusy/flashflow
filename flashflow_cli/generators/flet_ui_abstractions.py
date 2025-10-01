"""
Flet UI Abstractions - Cross-platform UI components for FlashFlow mobile apps
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template

from ..core import FlashFlowProject, FlashFlowIR

class FletUIAbstractions:
    """Generates Flet UI abstraction components"""
    
    def __init__(self, project: FlashFlowProject, ir: FlashFlowIR):
        self.project = project
        self.ir = ir
        self.mobile_path = project.dist_path / "mobile"
    
    def generate_flet_abstractions(self, platform: str = "both"):
        """Generate Flet UI abstraction components for mobile apps"""
        
        if platform in ["ios", "both"]:
            self._generate_ios_abstractions()
        
        if platform in ["android", "both"]:
            self._generate_android_abstractions()
            
        # Generate shared abstractions
        self._generate_shared_abstractions()
    
    def _generate_ios_abstractions(self):
        """Generate iOS-specific Flet abstractions"""
        platform_path = self.mobile_path / "ios" / "src"
        self._create_abstraction_components(platform_path)
    
    def _generate_android_abstractions(self):
        """Generate Android-specific Flet abstractions"""
        platform_path = self.mobile_path / "android" / "src"
        self._create_abstraction_components(platform_path)
    
    def _generate_shared_abstractions(self):
        """Generate shared Flet UI abstractions"""
        # Create shared abstractions for both platforms
        shared_dirs = [
            self.mobile_path / "ios" / "src" / "abstractions",
            self.mobile_path / "android" / "src" / "abstractions"
        ]
        
        for dir_path in shared_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            self._create_shared_abstraction_components(dir_path)
    
    def _create_abstraction_components(self, platform_path: Path):
        """Create core abstraction components"""
        abstractions_path = platform_path / "abstractions"
        abstractions_path.mkdir(parents=True, exist_ok=True)
        
        # Generate Declarative Layout Manager
        self._generate_declarative_layout_manager(abstractions_path)
        
        # Generate Adaptive Layout Component
        self._generate_adaptive_layout_component(abstractions_path)
        
        # Generate Navigation Abstraction
        self._generate_navigation_abstraction(abstractions_path)
        
        # Generate UX State Management
        self._generate_ux_state_management(abstractions_path)
    
    def _create_shared_abstraction_components(self, abstractions_path: Path):
        """Create shared abstraction components"""
        # Generate base abstraction classes
        self._generate_base_abstractions(abstractions_path)
        
        # Generate utility components
        self._generate_utility_components(abstractions_path)
    
    def _generate_declarative_layout_manager(self, abstractions_path: Path):
        """Generate Declarative Flet Layout Manager"""
        
        template = Template("""
\"\"\"Declarative Flet Layout Manager\"\"\"

import flet as ft
from typing import List, Optional, Union
from abc import ABC, abstractmethod

class LayoutComponent(ABC):
    \"\"\"Base class for layout components\"\"\"
    
    def __init__(self, name: str):
        self.name = name
        self.children: List['LayoutComponent'] = []
    
    def add_child(self, child: 'LayoutComponent'):
        \"\"\"Add a child component\"\"\"
        self.children.append(child)
    
    @abstractmethod
    def build(self, platform: str = "desktop") -> ft.Control:
        \"\"\"Build the Flet control for this component\"\"\"
        pass

class ResponsiveMainLayout(LayoutComponent):
    \"\"\"Responsive main layout with sidebar and main content\"\"\"
    
    def __init__(self, name: str = "main_layout"):
        super().__init__(name)
        self.sidebar_width = 250
        self.main_content: Optional[LayoutComponent] = None
        self.sidebar_content: Optional[LayoutComponent] = None
    
    def set_main_content(self, content: LayoutComponent):
        \"\"\"Set the main content area\"\"\"
        self.main_content = content
    
    def set_sidebar_content(self, content: LayoutComponent):
        \"\"\"Set the sidebar content\"\"\"
        self.sidebar_content = content
    
    def build(self, platform: str = "desktop") -> ft.Control:
        \"\"\"Build responsive layout based on platform\"\"\"
        if platform == "mobile":
            # Mobile: Stack layout with collapsible sidebar
            return self._build_mobile_layout()
        else:
            # Desktop: Split view with sidebar
            return self._build_desktop_layout()
    
    def _build_desktop_layout(self) -> ft.Control:
        \"\"\"Build desktop layout with sidebar\"\"\"
        sidebar = ft.Container(
            content=self.sidebar_content.build("desktop") if self.sidebar_content else ft.Text("Sidebar"),
            width=self.sidebar_width,
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=10
        )
        
        main_area = ft.Container(
            content=self.main_content.build("desktop") if self.main_content else ft.Text("Main Content"),
            expand=True,
            padding=10
        )
        
        return ft.Row(
            controls=[sidebar, main_area],
            expand=True
        )
    
    def _build_mobile_layout(self) -> ft.Control:
        \"\"\"Build mobile layout with collapsible sidebar\"\"\"
        # For mobile, we'll use a navigation rail that can be toggled
        main_content = self.main_content.build("mobile") if self.main_content else ft.Text("Main Content")
        
        return ft.Column(
            controls=[main_content],
            expand=True
        )

class LayoutManager:
    \"\"\"Manages layout components and their responsive behavior\"\"\"
    
    def __init__(self):
        self.layouts: Dict[str, LayoutComponent] = {}
        self.current_platform = "desktop"
    
    def register_layout(self, name: str, layout: LayoutComponent):
        \"\"\"Register a layout component\"\"\"
        self.layouts[name] = layout
    
    def get_layout(self, name: str) -> Optional[LayoutComponent]:
        \"\"\"Get a registered layout component\"\"\"
        return self.layouts.get(name)
    
    def set_platform(self, platform: str):
        \"\"\"Set the current platform (desktop/mobile)\"\"\"
        self.current_platform = platform.lower()
    
    def render_layout(self, name: str) -> ft.Control:
        \"\"\"Render a layout for the current platform\"\"\"
        layout = self.get_layout(name)
        if layout:
            return layout.build(self.current_platform)
        return ft.Text(f"Layout '{name}' not found")
""")
        
        with open(abstractions_path / "layout_manager.py", 'w') as f:
            f.write(template.render())
    
    def _generate_adaptive_layout_component(self, abstractions_path: Path):
        """Generate Adaptive Layout Component"""
        
        template = Template("""
\"\"\"Adaptive Layout Component - Declarative Grid Splitter\"\"\"

import flet as ft
from typing import List, Optional, Union
from .layout_manager import LayoutComponent

class AdaptiveGridSplitter(LayoutComponent):
    \"\"\"Declarative Grid Splitter that adapts to screen constraints\"\"\"
    
    def __init__(self, name: str = "adaptive_grid"):
        super().__init__(name)
        self.columns: List[LayoutComponent] = []
        self.column_widths: List[float] = []
        self.adaptive_behavior = "stack"  # stack or flex
    
    def add_column(self, column: LayoutComponent, width: float = 1.0):
        \"\"\"Add a column to the grid\"\"\"
        self.columns.append(column)
        self.column_widths.append(width)
    
    def set_adaptive_behavior(self, behavior: str):
        \"\"\"Set adaptive behavior: 'stack' for mobile, 'flex' for desktop\"\"\"
        self.adaptive_behavior = behavior
    
    def build(self, platform: str = "desktop") -> ft.Control:
        \"\"\"Build adaptive grid based on platform\"\"\"
        if platform == "mobile":
            return self._build_mobile_grid()
        else:
            return self._build_desktop_grid()
    
    def _build_desktop_grid(self) -> ft.Control:
        \"\"\"Build flexible column layout for desktop\"\"\"
        if not self.columns:
            return ft.Text("No columns defined")
        
        # Calculate total width for proportions
        total_width = sum(self.column_widths)
        controls = []
        
        for i, column in enumerate(self.columns):
            width_proportion = self.column_widths[i] / total_width
            content = column.build("desktop")
            
            controls.append(
                ft.Container(
                    content=content,
                    expand=True,
                    width=width_proportion * 1000  # Relative width
                )
            )
        
        return ft.Row(
            controls=controls,
            expand=True,
            spacing=10
        )
    
    def _build_mobile_grid(self) -> ft.Control:
        \"\"\"Build stacked column layout for mobile\"\"\"
        if not self.columns:
            return ft.Text("No columns defined")
        
        controls = []
        for column in self.columns:
            content = column.build("mobile")
            controls.append(
                ft.Container(
                    content=content,
                    padding=5
                )
            )
        
        return ft.Column(
            controls=controls,
            expand=True,
            spacing=10
        )

class FlexibleColumn(LayoutComponent):
    \"\"\"Flexible column that can adapt to different screen sizes\"\"\"
    
    def __init__(self, name: str, min_width: int = 300, max_width: Optional[int] = None):
        super().__init__(name)
        self.min_width = min_width
        self.max_width = max_width
        self.content: Optional[LayoutComponent] = None
    
    def set_content(self, content: LayoutComponent):
        \"\"\"Set the column content\"\"\"
        self.content = content
    
    def build(self, platform: str = "desktop") -> ft.Control:
        \"\"\"Build column based on platform\"\"\"
        if self.content:
            content_control = self.content.build(platform)
        else:
            content_control = ft.Text(f"Column: {self.name}")
        
        if platform == "mobile":
            # Mobile: Full width column
            return ft.Container(
                content=content_control,
                expand=True,
                padding=5
            )
        else:
            # Desktop: Constrained width column
            container_width = self.max_width if self.max_width else None
            return ft.Container(
                content=content_control,
                width=container_width,
                padding=10
            )
""")
        
        with open(abstractions_path / "adaptive_layout.py", 'w') as f:
            f.write(template.render())
    
    def _generate_navigation_abstraction(self, abstractions_path: Path):
        """Generate Navigation Abstraction"""
        
        template = Template("""
\"\"\"Navigation Abstraction - AI-Powered Tab Organizer\"\"\"

import flet as ft
from typing import List, Dict, Optional, Callable
from .layout_manager import LayoutComponent

class NavigationAbstraction(LayoutComponent):
    \"\"\"AI-Powered Tab Organizer with platform-specific navigation\"\"\"
    
    def __init__(self, name: str = "navigation"):
        super().__init__(name)
        self.tabs: List[Dict] = []
        self.current_tab_index = 0
        self.on_tab_change: Optional[Callable] = None
        self.platform = "desktop"  # desktop or mobile
    
    def add_tab(self, title: str, icon: str, content: LayoutComponent, group: str = "main"):
        \"\"\"Add a tab to the navigation\"\"\"
        self.tabs.append({
            'title': title,
            'icon': icon,
            'content': content,
            'group': group
        })
    
    def set_platform(self, platform: str):
        \"\"\"Set the platform (desktop/mobile)\"\"\"
        self.platform = platform.lower()
    
    def set_on_tab_change(self, callback: Callable):
        \"\"\"Set callback for tab change events\"\"\"
        self.on_tab_change = callback
    
    def build(self, platform: str = "desktop") -> ft.Control:
        \"\"\"Build navigation based on platform\"\"\"
        self.platform = platform.lower()
        
        if self.platform == "mobile":
            return self._build_mobile_navigation()
        else:
            return self._build_desktop_navigation()
    
    def _build_desktop_navigation(self) -> ft.Control:
        \"\"\"Build sidebar tab grouping for desktop\"\"\"
        if not self.tabs:
            return ft.Text("No tabs defined")
        
        # Group tabs by category
        tab_groups: Dict[str, List] = {}
        for tab in self.tabs:
            group = tab['group']
            if group not in tab_groups:
                tab_groups[group] = []
            tab_groups[group].append(tab)
        
        # Build sidebar with grouped tabs
        sidebar_controls = []
        for group_name, group_tabs in tab_groups.items():
            if len(tab_groups) > 1:
                # Add group header
                sidebar_controls.append(
                    ft.Text(group_name.title(), weight=ft.FontWeight.BOLD, size=16)
                )
            
            # Add tabs in this group
            for i, tab in enumerate(group_tabs):
                tab_index = self.tabs.index(tab)
                sidebar_controls.append(
                    ft.ListTile(
                        title=ft.Text(tab['title']),
                        leading=ft.Icon(tab['icon']),
                        on_click=lambda e, idx=tab_index: self._on_tab_selected(idx),
                        selected=tab_index == self.current_tab_index
                    )
                )
        
        sidebar = ft.Container(
            content=ft.Column(sidebar_controls, spacing=5),
            width=250,
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=10
        )
        
        # Build main content area
        current_content = self.tabs[self.current_tab_index]['content'].build("desktop") \
            if self.tabs else ft.Text("Select a tab")
        
        main_content = ft.Container(
            content=current_content,
            expand=True,
            padding=10
        )
        
        return ft.Row(
            controls=[sidebar, main_content],
            expand=True
        )
    
    def _build_mobile_navigation(self) -> ft.Control:
        \"\"\"Build bottom navigation bar for mobile\"\"\"
        if not self.tabs:
            return ft.Text("No tabs defined")
        
        # Build bottom navigation bar
        destinations = []
        for tab in self.tabs:
            destinations.append(
                ft.NavigationDestination(
                    icon=tab['icon'],
                    label=tab['title']
                )
            )
        
        bottom_nav = ft.NavigationBar(
            destinations=destinations,
            on_change=self._on_mobile_tab_change
        )
        
        # Build main content area
        current_content = self.tabs[self.current_tab_index]['content'].build("mobile") \
            if self.tabs else ft.Text("Select a tab")
        
        main_content = ft.Container(
            content=current_content,
            expand=True,
            padding=10
        )
        
        return ft.Column(
            controls=[main_content, bottom_nav],
            expand=True
        )
    
    def _on_tab_selected(self, index: int):
        \"\"\"Handle tab selection on desktop\"\"\"
        self.current_tab_index = index
        if self.on_tab_change:
            self.on_tab_change(index)
    
    def _on_mobile_tab_change(self, e):
        \"\"\"Handle tab change on mobile\"\"\"
        self.current_tab_index = e.control.selected_index
        if self.on_tab_change:
            self.on_tab_change(self.current_tab_index)

class AITabOrganizer:
    \"\"\"AI-Powered Tab Organizer that intelligently groups tabs\"\"\"
    
    def __init__(self):
        self.tab_usage_history: List[Dict] = []
        self.tab_relationships: Dict[str, List[str]] = {}
    
    def record_tab_access(self, tab_name: str, timestamp: float, context: str = ""):
        \"\"\"Record when a tab is accessed\"\"\"
        self.tab_usage_history.append({
            'tab': tab_name,
            'timestamp': timestamp,
            'context': context
        })
    
    def suggest_tab_grouping(self) -> Dict[str, List[str]]:
        \"\"\"Suggest intelligent tab grouping based on usage patterns\"\"\"
        # Simple algorithm: group tabs accessed within 5 minutes of each other
        groups: Dict[str, List[str]] = {}
        group_id = 0
        
        sorted_history = sorted(self.tab_usage_history, key=lambda x: x['timestamp'])
        current_group = []
        last_timestamp = 0
        
        for record in sorted_history:
            if not current_group or (record['timestamp'] - last_timestamp) <= 300:  # 5 minutes
                current_group.append(record['tab'])
            else:
                # Start new group
                groups[f"group_{group_id}"] = list(set(current_group))  # Remove duplicates
                current_group = [record['tab']]
                group_id += 1
            
            last_timestamp = record['timestamp']
        
        # Add final group
        if current_group:
            groups[f"group_{group_id}"] = list(set(current_group))
        
        return groups
    
    def get_frequently_used_tabs(self, limit: int = 5) -> List[str]:
        \"\"\"Get most frequently used tabs\"\"\"
        tab_counts: Dict[str, int] = {}
        for record in self.tab_usage_history:
            tab = record['tab']
            tab_counts[tab] = tab_counts.get(tab, 0) + 1
        
        # Sort by count and return top tabs
        sorted_tabs = sorted(tab_counts.items(), key=lambda x: x[1], reverse=True)
        return [tab for tab, count in sorted_tabs[:limit]]
""")
        
        with open(abstractions_path / "navigation_abstraction.py", 'w') as f:
            f.write(template.render())
    
    def _generate_ux_state_management(self, abstractions_path: Path):
        """Generate UX State Management"""
        
        template = Template("""
\"\"\"UX State Management - Responsive Context Panel\"\"\"

import flet as ft
from typing import Optional, Callable, Any
from .layout_manager import LayoutComponent

class ResponsiveContextPanel(LayoutComponent):
    \"\"\"Responsive Context Panel that adapts to device context\"\"\"
    
    def __init__(self, name: str = "context_panel"):
        super().__init__(name)
        self.content: Optional[LayoutComponent] = None
        self.is_open = False
        self.position = "sidebar"  # sidebar, overlay, bottom_sheet
        self.platform = "desktop"  # desktop or mobile
        self.on_close: Optional[Callable] = None
        self.on_open: Optional[Callable] = None
    
    def set_content(self, content: LayoutComponent):
        \"\"\"Set the panel content\"\"\"
        self.content = content
    
    def set_position(self, position: str):
        \"\"\"Set panel position: sidebar, overlay, or bottom_sheet\"\"\"
        self.position = position
    
    def set_platform(self, platform: str):
        \"\"\"Set the platform (desktop/mobile)\"\"\"
        self.platform = platform.lower()
    
    def set_on_close(self, callback: Callable):
        \"\"\"Set callback for close events\"\"\"
        self.on_close = callback
    
    def set_on_open(self, callback: Callable):
        \"\"\"Set callback for open events\"\"\"
        self.on_open = callback
    
    def open_panel(self):
        \"\"\"Open the context panel\"\"\"
        self.is_open = True
        if self.on_open:
            self.on_open()
    
    def close_panel(self):
        \"\"\"Close the context panel\"\"\"
        self.is_open = False
        if self.on_close:
            self.on_close()
    
    def build(self, platform: str = "desktop") -> ft.Control:
        \"\"\"Build context panel based on platform and position\"\"\"
        self.platform = platform.lower()
        
        if not self.content:
            return ft.Text("Context Panel")
        
        if self.platform == "mobile":
            return self._build_mobile_panel()
        else:
            return self._build_desktop_panel()
    
    def _build_desktop_panel(self) -> ft.Control:
        \"\"\"Build pinned sidebar for desktop\"\"\"
        if self.position == "sidebar":
            # Pinned sidebar
            content = self.content.build("desktop")
            return ft.Container(
                content=content,
                width=300,
                bgcolor=ft.colors.SURFACE_VARIANT,
                padding=10,
                visible=self.is_open
            )
        else:
            # Overlay or bottom sheet
            return self._build_overlay_panel()
    
    def _build_mobile_panel(self) -> ft.Control:
        \"\"\"Build collapsible modal overlay for mobile\"\"\"
        if self.position == "bottom_sheet":
            # Bottom sheet for mobile
            return self._build_bottom_sheet()
        else:
            # Modal overlay
            return self._build_overlay_panel()
    
    def _build_overlay_panel(self) -> ft.Control:
        \"\"\"Build overlay panel\"\"\"
        content = self.content.build(self.platform)
        
        overlay = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Context Panel", weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        on_click=lambda e: self.close_panel()
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                content
            ]),
            width=350,
            height=500,
            bgcolor=ft.colors.SURFACE,
            border_radius=10,
            padding=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.BLACK26
            )
        )
        
        # Overlay background
        overlay_bg = ft.Container(
            content=overlay,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.BLACK38 if self.is_open else None,
            visible=self.is_open,
            on_click=lambda e: self.close_panel() if self.is_open else None
        )
        
        return overlay_bg
    
    def _build_bottom_sheet(self) -> ft.Control:
        \"\"\"Build bottom sheet for mobile\"\"\"
        content = self.content.build("mobile")
        
        sheet_content = ft.Column([
            ft.Row([
                ft.Text("Context Panel", weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    on_click=lambda e: self.close_panel()
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            content
        ])
        
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=sheet_content,
                padding=15
            ),
            open=self.is_open
        )
        
        return bottom_sheet

class IntelligentDevToolsAssistant(LayoutComponent):
    \"\"\"Intelligent DevTools Assistant integrated into context panel\"\"\"
    
    def __init__(self, name: str = "devtools_assistant"):
        super().__init__(name)
        self.tools: List[Dict] = []
        self.current_tool_index = 0
        self.on_tool_change: Optional[Callable] = None
    
    def add_tool(self, name: str, icon: str, description: str, handler: Callable):
        \"\"\"Add a dev tool\"\"\"
        self.tools.append({
            'name': name,
            'icon': icon,
            'description': description,
            'handler': handler
        })
    
    def build(self, platform: str = "desktop") -> ft.Control:
        \"\"\"Build dev tools assistant interface\"\"\"
        if not self.tools:
            return ft.Text("No dev tools available")
        
        # Tool selection
        tool_tabs = []
        for i, tool in enumerate(self.tools):
            tool_tabs.append(
                ft.ListTile(
                    title=ft.Text(tool['name']),
                    leading=ft.Icon(tool['icon']),
                    on_click=lambda e, idx=i: self._select_tool(idx),
                    selected=i == self.current_tool_index
                )
            )
        
        # Current tool content
        current_tool = self.tools[self.current_tool_index]
        tool_content = ft.Column([
            ft.Text(current_tool['name'], size=20, weight=ft.FontWeight.BOLD),
            ft.Text(current_tool['description'], size=14),
            ft.Divider(),
            ft.ElevatedButton(
                "Run Tool",
                on_click=lambda e: self._run_current_tool()
            )
        ])
        
        return ft.Column([
            ft.Text("Intelligent DevTools Assistant", weight=ft.FontWeight.BOLD, size=16),
            ft.Divider(),
            ft.Row([
                ft.Column(tool_tabs, spacing=5),
                ft.VerticalDivider(),
                ft.Container(tool_content, expand=True, padding=10)
            ], expand=True)
        ])
    
    def _select_tool(self, index: int):
        \"\"\"Select a tool\"\"\"
        self.current_tool_index = index
        if self.on_tool_change:
            self.on_tool_change(index)
    
    def _run_current_tool(self):
        \"\"\"Run the currently selected tool\"\"\"
        if 0 <= self.current_tool_index < len(self.tools):
            tool = self.tools[self.current_tool_index]
            if tool['handler']:
                tool['handler']()
""")
        
        with open(abstractions_path / "ux_state_management.py", 'w') as f:
            f.write(template.render())
    
    def _generate_base_abstractions(self, abstractions_path: Path):
        """Generate base abstraction classes"""
        
        template = Template("""
\"\"\"Base Abstraction Classes\"\"\"

import flet as ft
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class FlashFlowComponent(ABC):
    \"\"\"Base class for all FlashFlow UI components\"\"\"
    
    def __init__(self, name: str, platform: str = "desktop"):
        self.name = name
        self.platform = platform.lower()
        self.properties: Dict[str, Any] = {}
        self.children: List['FlashFlowComponent'] = []
        self.parent: Optional['FlashFlowComponent'] = None
    
    def set_property(self, key: str, value: Any):
        \"\"\"Set a component property\"\"\"
        self.properties[key] = value
    
    def get_property(self, key: str, default: Any = None) -> Any:
        \"\"\"Get a component property\"\"\"
        return self.properties.get(key, default)
    
    def add_child(self, child: 'FlashFlowComponent'):
        \"\"\"Add a child component\"\"\"
        child.parent = self
        self.children.append(child)
    
    @abstractmethod
    def build(self) -> ft.Control:
        \"\"\"Build the Flet control for this component\"\"\"
        pass
    
    def adapt_to_platform(self, platform: str) -> ft.Control:
        \"\"\"Adapt component to specific platform\"\"\"
        self.platform = platform.lower()
        return self.build()

class PlatformDetector:
    \"\"\"Detects the current platform and provides platform-specific behaviors\"\"\"
    
    @staticmethod
    def detect_platform(page: ft.Page) -> str:
        \"\"\"Detect platform from Flet page\"\"\"
        if page.platform in [ft.PagePlatform.ANDROID, ft.PagePlatform.IOS]:
            return "mobile"
        elif page.platform in [ft.PagePlatform.WINDOWS, ft.PagePlatform.MACOS, ft.PagePlatform.LINUX]:
            return "desktop"
        else:
            # Default to desktop for web
            return "desktop"
    
    @staticmethod
    def get_screen_size(page: ft.Page) -> Dict[str, int]:
        \"\"\"Get screen dimensions\"\"\"
        return {
            'width': page.width or 1024,
            'height': page.height or 768
        }
    
    @staticmethod
    def is_constrained_screen(page: ft.Page, threshold: int = 768) -> bool:
        \"\"\"Check if screen is constrained (mobile-like)\"\"\"
        screen_size = PlatformDetector.get_screen_size(page)
        return screen_size['width'] <= threshold

class ResponsiveBehavior:
    \"\"\"Provides responsive behavior patterns\"\"\"
    
    @staticmethod
    def get_responsive_spacing(platform: str) -> int:
        \"\"\"Get appropriate spacing for platform\"\"\"
        return 5 if platform == "mobile" else 10
    
    @staticmethod
    def get_responsive_padding(platform: str) -> int:
        \"\"\"Get appropriate padding for platform\"\"\"
        return 10 if platform == "mobile" else 20
    
    @staticmethod
    def get_font_size(platform: str, base_size: int = 14) -> int:
        \"\"\"Get appropriate font size for platform\"\"\"
        if platform == "mobile":
            return base_size + 2
        return base_size
""")
        
        with open(abstractions_path / "base_abstractions.py", 'w') as f:
            f.write(template.render())
    
    def _generate_utility_components(self, abstractions_path: Path):
        """Generate utility components"""
        
        template = Template("""
\"\"\"Utility Components\"\"\"

import flet as ft
from typing import Optional, Callable, List
from .base_abstractions import FlashFlowComponent

class ProgressiveDisclosure(FlashFlowComponent):
    \"\"\"Progressive disclosure component that shows/hides content\"\"\"
    
    def __init__(self, name: str, title: str, platform: str = "desktop"):
        super().__init__(name, platform)
        self.title = title
        self.is_expanded = False
        self.content: Optional[FlashFlowComponent] = None
        self.on_toggle: Optional[Callable] = None
    
    def set_content(self, content: FlashFlowComponent):
        \"\"\"Set the disclosure content\"\"\"
        self.content = content
    
    def set_on_toggle(self, callback: Callable):
        \"\"\"Set toggle callback\"\"\"
        self.on_toggle = callback
    
    def toggle(self):
        \"\"\"Toggle the disclosure state\"\"\"
        self.is_expanded = not self.is_expanded
        if self.on_toggle:
            self.on_toggle(self.is_expanded)
    
    def build(self) -> ft.Control:
        \"\"\"Build progressive disclosure component\"\"\"
        # Header with toggle button
        header = ft.Row([
            ft.IconButton(
                icon=ft.icons.ARROW_DROP_DOWN if self.is_expanded else ft.icons.ARROW_RIGHT,
                on_click=lambda e: self.toggle()
            ),
            ft.Text(self.title, weight=ft.FontWeight.BOLD)
        ])
        
        # Content (visible when expanded)
        content_control = None
        if self.content and self.is_expanded:
            content_control = self.content.build()
        
        controls = [header]
        if content_control:
            controls.append(
                ft.Container(
                    content=content_control,
                    padding=10
                )
            )
        
        return ft.Column(controls, spacing=5)

class SmartTooltip(FlashFlowComponent):
    \"\"\"Smart tooltip with platform-adaptive behavior\"\"\"
    
    def __init__(self, name: str, message: str, platform: str = "desktop"):
        super().__init__(name, platform)
        self.message = message
        self.show_delay = 500 if platform == "desktop" else 1000  # ms
        self.hide_delay = 2000  # ms
    
    def build(self) -> ft.Control:
        \"\"\"Build smart tooltip\"\"\"
        if self.platform == "mobile":
            # On mobile, use a simple text display or snackbar
            return ft.Text(self.message, size=12, color=ft.colors.GREY)
        else:
            # On desktop, use tooltip
            return ft.Tooltip(
                message=self.message,
                wait_duration=self.show_delay
            )

class ContextualHelp(FlashFlowComponent):
    \"\"\"Contextual help system\"\"\"
    
    def __init__(self, name: str, platform: str = "desktop"):
        super().__init__(name, platform)
        self.help_items: List[Dict] = []
    
    def add_help_item(self, trigger: str, content: str, position: str = "right"):
        \"\"\"Add a help item\"\"\"
        self.help_items.append({
            'trigger': trigger,
            'content': content,
            'position': position
        })
    
    def build(self) -> ft.Control:
        \"\"\"Build contextual help\"\"\"
        if not self.help_items:
            return ft.Text("")
        
        # Create help icons for each item
        help_controls = []
        for item in self.help_items:
            help_icon = ft.IconButton(
                icon=ft.icons.HELP_OUTLINE,
                tooltip=item['content'],
                icon_size=18
            )
            help_controls.append(help_icon)
        
        return ft.Row(help_controls, spacing=5)

# Export all components
__all__ = [
    'ProgressiveDisclosure',
    'SmartTooltip', 
    'ContextualHelp'
]
""")
        
        with open(abstractions_path / "utility_components.py", 'w') as f:
            f.write(template.render())