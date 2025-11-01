"""
FlashFlow Slider Component with Animations
"""

class SliderComponent:
    """Slider component with smooth animations and transitions"""
    
    def __init__(self, min_value=0, max_value=100, initial_value=50, step=1, 
                 animation_type="slide", animation_duration=300):
        """
        Initialize slider component
        
        Args:
            min_value (int): Minimum slider value
            max_value (int): Maximum slider value
            initial_value (int): Initial slider position
            step (int): Step increment
            animation_type (str): Type of animation (slide, fade, zoom)
            animation_duration (int): Animation duration in milliseconds
        """
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = initial_value
        self.step = step
        self.animation_type = animation_type
        self.animation_duration = animation_duration
        self.on_change_callback = None
        
    def set_on_change(self, callback):
        """Set callback function for value changes"""
        self.on_change_callback = callback
        
    def update_value(self, new_value):
        """Update slider value with animation"""
        if self.min_value <= new_value <= self.max_value:
            old_value = self.current_value
            self.current_value = new_value
            
            # Trigger callback if set
            if self.on_change_callback:
                self.on_change_callback(old_value, new_value)
                
            return True
        return False
        
    def generate_html(self, element_id="slider"):
        """
        Generate HTML for the slider component
        
        Args:
            element_id (str): Unique ID for the slider element
            
        Returns:
            str: HTML string for the slider component
        """
        return f'''
        <div class="flashflow-slider-container" id="{element_id}-container">
            <input type="range" 
                   id="{element_id}" 
                   class="flashflow-slider {self.animation_type}-animation"
                   min="{self.min_value}" 
                   max="{self.max_value}" 
                   value="{self.current_value}" 
                   step="{self.step}"
                   data-animation-type="{self.animation_type}"
                   data-animation-duration="{self.animation_duration}">
            <div class="flashflow-slider-value" id="{element_id}-value">{self.current_value}</div>
        </div>
        '''
        
    def generate_css(self):
        """
        Generate CSS for slider animations
        
        Returns:
            str: CSS string for slider animations
        """
        return '''
        /* FlashFlow Slider Styles with Animations */
        
        .flashflow-slider-container {
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 20px 0;
        }
        
        .flashflow-slider {
            flex: 1;
            height: 8px;
            border-radius: 4px;
            background: #e0e0e0;
            outline: none;
            -webkit-appearance: none;
            appearance: none;
            transition: all 0.3s ease;
        }
        
        .flashflow-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #3B82F6;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }
        
        .flashflow-slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #3B82F6;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }
        
        .flashflow-slider:hover {
            background: #d0d0d0;
        }
        
        .flashflow-slider::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            background: #2563EB;
        }
        
        .flashflow-slider::-moz-range-thumb:hover {
            transform: scale(1.2);
            background: #2563EB;
        }
        
        .flashflow-slider-value {
            min-width: 40px;
            text-align: center;
            font-weight: 500;
            color: #374151;
            padding: 4px 8px;
            background: #f3f4f6;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        
        /* Slide Animation */
        .slide-animation::-webkit-slider-thumb {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .slide-animation::-moz-range-thumb {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Fade Animation */
        .fade-animation::-webkit-slider-thumb {
            transition: all 0.3s ease-in-out;
        }
        
        .fade-animation::-moz-range-thumb {
            transition: all 0.3s ease-in-out;
        }
        
        /* Zoom Animation */
        .zoom-animation::-webkit-slider-thumb {
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        
        .zoom-animation::-moz-range-thumb {
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        
        /* Bounce Effect */
        .flashflow-slider.bounce::-webkit-slider-thumb {
            transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        
        .flashflow-slider.bounce::-moz-range-thumb {
            transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        '''
        
    def generate_javascript(self):
        """
        Generate JavaScript for slider interactions and animations
        
        Returns:
            str: JavaScript string for slider functionality
        """
        return '''
        <script>
        // FlashFlow Slider Component with Animations
        class FlashFlowSlider {
            constructor(sliderId) {
                this.slider = document.getElementById(sliderId);
                this.valueDisplay = document.getElementById(sliderId + '-value');
                this.container = document.getElementById(sliderId + '-container');
                this.init();
            }
            
            init() {
                if (this.slider) {
                    // Update value display when slider changes
                    this.slider.addEventListener('input', (e) => {
                        this.updateValueDisplay(e.target.value);
                        this.applyAnimation(e.target);
                    });
                    
                    // Add smooth transition on release
                    this.slider.addEventListener('change', (e) => {
                        this.applyBounceEffect(e.target);
                    });
                    
                    // Initialize value display
                    this.updateValueDisplay(this.slider.value);
                }
            }
            
            updateValueDisplay(value) {
                if (this.valueDisplay) {
                    this.valueDisplay.textContent = value;
                    
                    // Add animation to value display
                    this.valueDisplay.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        this.valueDisplay.style.transform = 'scale(1)';
                    }, 150);
                }
            }
            
            applyAnimation(slider) {
                const animationType = slider.dataset.animationType || 'slide';
                const duration = parseInt(slider.dataset.animationDuration) || 300;
                
                // Apply animation class
                slider.classList.add('animating');
                
                // Remove animation class after duration
                setTimeout(() => {
                    slider.classList.remove('animating');
                }, duration);
            }
            
            applyBounceEffect(slider) {
                // Add bounce effect on release
                slider.classList.add('bounce');
                
                setTimeout(() => {
                    slider.classList.remove('bounce');
                }, 500);
            }
        }
        
        // Initialize all FlashFlow sliders
        document.addEventListener('DOMContentLoaded', function() {
            const sliders = document.querySelectorAll('.flashflow-slider');
            sliders.forEach(slider => {
                new FlashFlowSlider(slider.id);
            });
        });
        </script>
        '''

# Utility functions for easier usage
def create_slider(*args, **kwargs):
    """Create a slider component"""
    return SliderComponent(*args, **kwargs)

def generate_slider_field(element_id, min_value=0, max_value=100, initial_value=50, 
                         step=1, animation_type="slide"):
    """Generate a complete slider field with label and component"""
    slider = SliderComponent(min_value, max_value, initial_value, step, animation_type)
    return f'''
    <div class="form-group">
        <label for="{element_id}">Select Value</label>
        {slider.generate_html(element_id)}
    </div>
    <style>
        {slider.generate_css()}
    </style>
    {slider.generate_javascript()}
    '''