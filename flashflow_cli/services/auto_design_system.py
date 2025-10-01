"""
FlashFlow Auto Beautiful Design System
Provides automatic theming and responsive layouts
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DesignTheme:
    name: str
    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str
    font_family: str
    spacing_unit: str
    border_radius: str


class AutoDesignSystem:
    """Auto beautiful design system generator"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.themes_dir = project_root / "src" / "themes"
        
        # Predefined themes
        self.themes = {
            "material": DesignTheme("material", "#1976d2", "#dc004e", "#fafafa", "#212121", "'Roboto', sans-serif", "8px", "4px"),
            "tailwind": DesignTheme("tailwind", "#3b82f6", "#8b5cf6", "#f8fafc", "#1e293b", "'Inter', sans-serif", "4px", "6px"),
            "minimal": DesignTheme("minimal", "#000000", "#666666", "#ffffff", "#000000", "'Helvetica', sans-serif", "8px", "2px"),
            "dark": DesignTheme("dark", "#bb86fc", "#03dac6", "#121212", "#ffffff", "'Roboto', sans-serif", "8px", "8px")
        }
    
    def initialize_design_system(self, theme_name: str = "material", brand_colors: Optional[Dict] = None):
        """Initialize design system with theme"""
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        theme = self.themes.get(theme_name, self.themes["material"])
        
        if brand_colors:
            if "primary" in brand_colors:
                theme.primary_color = brand_colors["primary"]
            if "secondary" in brand_colors:
                theme.secondary_color = brand_colors["secondary"]
        
        self._generate_css_theme(theme)
        self._generate_tailwind_config(theme)
        self._generate_component_library(theme)
        
        return theme
    
    def _generate_css_theme(self, theme: DesignTheme):
        """Generate CSS theme file"""
        css_content = f"""/* FlashFlow Auto Design - {theme.name} Theme */
:root {{
  --ff-primary: {theme.primary_color};
  --ff-secondary: {theme.secondary_color};
  --ff-background: {theme.background_color};
  --ff-text: {theme.text_color};
  --ff-font: {theme.font_family};
  --ff-spacing: {theme.spacing_unit};
  --ff-radius: {theme.border_radius};
}}

body {{
  font-family: var(--ff-font);
  background: var(--ff-background);
  color: var(--ff-text);
  margin: 0;
}}

.ff-container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 calc(var(--ff-spacing) * 2);
}}

.ff-button {{
  background: var(--ff-primary);
  color: white;
  border: none;
  padding: var(--ff-spacing) calc(var(--ff-spacing) * 2);
  border-radius: var(--ff-radius);
  cursor: pointer;
  font-family: inherit;
}}

.ff-card {{
  background: var(--ff-background);
  border-radius: var(--ff-radius);
  padding: calc(var(--ff-spacing) * 2);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}

.ff-input {{
  width: 100%;
  padding: var(--ff-spacing);
  border: 1px solid #ddd;
  border-radius: var(--ff-radius);
  font-family: inherit;
}}

@media (max-width: 768px) {{
  .ff-container {{ padding: 0 var(--ff-spacing); }}
  .ff-grid {{ grid-template-columns: 1fr; }}
}}

.ff-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--ff-spacing);
}}
"""
        
        with open(self.themes_dir / f"{theme.name}.css", 'w') as f:
            f.write(css_content)
    
    def _generate_tailwind_config(self, theme: DesignTheme):
        """Generate Tailwind config"""
        config = {
            "content": ["./src/**/*.{js,jsx,ts,tsx}"],
            "theme": {
                "extend": {
                    "colors": {
                        "primary": theme.primary_color,
                        "secondary": theme.secondary_color
                    },
                    "fontFamily": {
                        "primary": [theme.font_family.replace("'", "")]
                    }
                }
            }
        }
        
        with open(self.project_root / "tailwind.config.js", 'w') as f:
            f.write(f"module.exports = {json.dumps(config, indent=2)}")
    
    def _generate_component_library(self, theme: DesignTheme):
        """Generate auto-styled components"""
        button_component = f"""import React from 'react';

interface AutoButtonProps {{
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
}}

export const AutoButton: React.FC<AutoButtonProps> = ({{ children, variant = 'primary', onClick }}) => {{
  const baseClasses = 'ff-button';
  const variantClasses = variant === 'secondary' ? 'ff-button--secondary' : '';
  
  return (
    <button className={{`${{baseClasses}} ${{variantClasses}}`}} onClick={{onClick}}>
      {{children}}
    </button>
  );
}};
"""
        
        components_dir = self.project_root / "src" / "components" / "auto"
        components_dir.mkdir(parents=True, exist_ok=True)
        
        with open(components_dir / "AutoButton.tsx", 'w') as f:
            f.write(button_component)
    
    def generate_theme_switcher(self):
        """Generate theme switcher"""
        switcher = """import React, { useState } from 'react';

export const ThemeSwitcher = () => {
  const [theme, setTheme] = useState('material');
  const themes = ['material', 'tailwind', 'minimal', 'dark'];
  
  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };
  
  return (
    <select value={theme} onChange={(e) => handleThemeChange(e.target.value)}>
      {themes.map(t => <option key={t} value={t}>{t}</option>)}
    </select>
  );
};
"""
        
        components_dir = self.project_root / "src" / "components" / "auto"
        with open(components_dir / "ThemeSwitcher.tsx", 'w') as f:
            f.write(switcher)