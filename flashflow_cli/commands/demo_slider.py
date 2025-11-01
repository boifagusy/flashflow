"""
FlashFlow CLI Command for Slider Demo
"""

import click
from pathlib import Path
from flashflow_cli.core import FlashFlowProject
from flashflow_cli.generators.frontend import FrontendGenerator
from core.framework import FlashFlowIR

@click.command()
@click.option('--port', default=3000, help='Port to run the slider demo')
@click.option('--output', default='slider-demo', help='Output directory for the demo')
def demo_slider(port, output):
    """Generate and run a demo of slider components with animations"""
    
    # Create a simple IR for the demo
    ir_data = {
        "project": {
            "name": "FlashFlow Slider Demo",
            "description": "Demo of slider components with animations",
            "version": "1.0.0"
        },
        "pages": {
            "/": {
                "title": "Slider Animation Demo",
                "body": [
                    {
                        "component": "hero",
                        "title": "FlashFlow Slider Demo",
                        "subtitle": "Interactive sliders with smooth animations",
                        "cta": {
                            "text": "Get Started",
                            "link": "#sliders"
                        }
                    }
                ]
            }
        },
        "theme": {
            "colors": {
                "primary": "#3B82F6",
                "secondary": "#64748B",
                "success": "#10B981",
                "warning": "#F59E0B",
                "danger": "#EF4444",
                "light": "#F8FAFC",
                "dark": "#0F172A"
            }
        }
    }
    
    # Create project directory
    project_path = Path(output).resolve()
    project_path.mkdir(exist_ok=True)
    
    # Create a minimal flashflow.json
    flashflow_config = {
        "name": "slider-demo",
        "description": "FlashFlow Slider Animation Demo",
        "frontend": {
            "framework": "react"
        }
    }
    
    import json
    with open(project_path / "flashflow.json", "w") as f:
        json.dump(flashflow_config, f, indent=2)
    
    # Create project instance
    project = FlashFlowProject(project_path)
    
    # Create IR instance
    ir = FlashFlowIR()
    ir.project = ir_data["project"]
    ir.pages = ir_data["pages"]
    ir.theme = ir_data["theme"]
    
    # Generate frontend with slider components
    generator = FrontendGenerator(project, ir)
    generator.generate()
    
    # Add custom slider demo page
    _create_slider_demo_page(generator.frontend_path, ir)
    
    click.echo(f"Slider demo generated in {output}")
    click.echo(f"Run 'cd {output}/dist/frontend && npx vite --port {port}' to view the demo")

def _create_slider_demo_page(frontend_path, ir):
    """Create a custom slider demo page"""
    
    from jinja2 import Template
    
    # Extract theme colors
    colors = ir.theme.get('colors', {})
    primary = colors.get('primary', '#3B82F6')
    
    template = Template("""import React, { useState } from 'react';
import Slider from '../components/Slider';
import { fadeIn, fadeOut, bounce, pulse } from '../components/Animations';
import './SliderDemo.css';

const SliderDemo = () => {
  const [volume, setVolume] = useState(50);
  const [brightness, setBrightness] = useState(75);
  const [contrast, setContrast] = useState(60);
  const [animationType, setAnimationType] = useState('slide');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleVolumeChange = (value) => {
    setVolume(value);
  };

  const handleBrightnessChange = (value) => {
    setBrightness(value);
  };

  const handleContrastChange = (value) => {
    setContrast(value);
  };

  const toggleAdvanced = () => {
    const newState = !showAdvanced;
    setShowAdvanced(newState);
    
    // Apply animation to advanced settings
    setTimeout(() => {
      const element = document.getElementById('advanced-settings');
      if (element) {
        if (newState) {
          fadeIn(element, 400);
        } else {
          fadeOut(element, 400);
        }
      }
    }, 10);
  };

  const triggerBounce = () => {
    const element = document.querySelector('.demo-card');
    if (element) {
      bounce(element);
    }
  };

  const triggerPulse = () => {
    const element = document.querySelector('.demo-card');
    if (element) {
      pulse(element);
    }
  };

  return (
    <div className="slider-demo-page">
      <div className="header">
        <div className="container">
          <h1>Slider Animation Demo</h1>
          <p>Interactive sliders with smooth animations</p>
        </div>
      </div>

      <div className="container">
        <div className="demo-card ff-hover-float">
          <div className="card-header">
            <h2>Basic Sliders</h2>
          </div>
          <div className="card-body">
            <div className="slider-group">
              <label htmlFor="volume">Volume: {volume}%</label>
              <Slider
                id="volume"
                min={0}
                max={100}
                initialValue={volume}
                step={1}
                animationType={animationType}
                onChange={handleVolumeChange}
              />
            </div>

            <div className="slider-group">
              <label htmlFor="brightness">Brightness: {brightness}%</label>
              <Slider
                id="brightness"
                min={0}
                max={100}
                initialValue={brightness}
                step={1}
                animationType={animationType}
                onChange={handleBrightnessChange}
              />
            </div>

            <div className="slider-group">
              <label htmlFor="contrast">Contrast: {contrast}%</label>
              <Slider
                id="contrast"
                min={0}
                max={100}
                initialValue={contrast}
                step={1}
                animationType={animationType}
                onChange={handleContrastChange}
              />
            </div>
          </div>
        </div>

        <div className="demo-card ff-hover-float">
          <div className="card-header">
            <h2>Animation Controls</h2>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label>Animation Type</label>
              <div className="radio-group">
                <label className="radio-option">
                  <input
                    type="radio"
                    name="animation"
                    value="slide"
                    checked={animationType === 'slide'}
                    onChange={() => setAnimationType('slide')}
                  />
                  Slide
                </label>
                <label className="radio-option">
                  <input
                    type="radio"
                    name="animation"
                    value="fade"
                    checked={animationType === 'fade'}
                    onChange={() => setAnimationType('fade')}
                  />
                  Fade
                </label>
                <label className="radio-option">
                  <input
                    type="radio"
                    name="animation"
                    value="zoom"
                    checked={animationType === 'zoom'}
                    onChange={() => setAnimationType('zoom')}
                  />
                  Zoom
                </label>
              </div>
            </div>

            <div className="button-group">
              <button className="btn btn-primary" onClick={triggerBounce}>
                Bounce Effect
              </button>
              <button className="btn btn-secondary" onClick={triggerPulse}>
                Pulse Effect
              </button>
              <button className="btn btn-success" onClick={toggleAdvanced}>
                {showAdvanced ? 'Hide' : 'Show'} Advanced
              </button>
            </div>

            <div id="advanced-settings" style={{ display: showAdvanced ? 'block' : 'none' }}>
              <h3>Advanced Settings</h3>
              <p>These are additional settings that can be controlled with sliders.</p>
              <div className="slider-group">
                <label>Speed: 75%</label>
                <Slider
                  min={0}
                  max={100}
                  initialValue={75}
                  step={1}
                  animationType={animationType}
                />
              </div>
              <div className="slider-group">
                <label>Quality: 90%</label>
                <Slider
                  min={0}
                  max={100}
                  initialValue={90}
                  step={1}
                  animationType={animationType}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="demo-card ff-hover-float">
          <div className="card-header">
            <h2>Customization</h2>
          </div>
          <div className="card-body">
            <p>Sliders can be customized with different colors, sizes, and behaviors.</p>
            <div className="slider-group">
              <label>Custom Styled Slider</label>
              <Slider
                min={0}
                max={100}
                initialValue={30}
                step={5}
                animationType="slide"
                className="custom-slider"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SliderDemo;
""")
    
    # Create the demo page
    pages_dir = frontend_path / "src" / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    demo_content = template.render(primary_color=primary)
    
    demo_file = pages_dir / "SliderDemo.jsx"
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(demo_content)
    
    # Create CSS for the demo
    css_content = f""".slider-demo-page {{
  min-height: 100vh;
}}

.header {{
  background: {primary};
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
}}

.header h1 {{
  margin: 0;
  font-size: 2rem;
}}

.header p {{
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
}}

.demo-card {{
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
}}

.card-header {{
  margin-bottom: 1rem;
}}

.card-header h2 {{
  margin: 0;
  color: {primary};
}}

.slider-group {{
  margin-bottom: 1.5rem;
}}

.slider-group label {{
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}}

.form-group {{
  margin-bottom: 1.5rem;
}}

.radio-group {{
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}}

.radio-option {{
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}}

.button-group {{
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin: 1.5rem 0;
}}

.btn {{
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}}

.btn:hover {{
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}}

.btn-primary {{
  background: {primary};
  color: white;
}}

.btn-secondary {{
  background: #64748B;
  color: white;
}}

.btn-success {{
  background: #10B981;
  color: white;
}}

.custom-slider {{ 
  --primary-color: #8B5CF6; /* Purple */
}}

/* Add the slider CSS from the component */
{open(frontend_path / "src" / "components" / "Slider.css").read()}
"""
    
    css_file = pages_dir / "SliderDemo.css"
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # Update App.tsx to include the demo page
    app_file = frontend_path / "src" / "App.tsx"
    if app_file.exists():
        with open(app_file, 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Add import for SliderDemo
        if "import SliderDemo" not in app_content:
            app_content = app_content.replace(
                "import './styles/App.css'",
                "import './styles/App.css'\nimport SliderDemo from './pages/SliderDemo'"
            )
        
        # Add route for SliderDemo
        if "SliderDemo" not in app_content:
            # Find the Routes component and add the new route
            app_content = app_content.replace(
                "<Route path=\"*\" element={<div>Page Not Found</div>} />",
                "<Route path=\"/slider-demo\" element={<SliderDemo />} />\n          <Route path=\"*\" element={<div>Page Not Found</div>} />"
            )
        
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(app_content)

if __name__ == '__main__':
    demo_slider()