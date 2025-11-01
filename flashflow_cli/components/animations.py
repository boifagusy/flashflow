"""
FlashFlow Animation Utilities
Provides various animation effects for UI components
"""

class AnimationUtils:
    """Utility class for animations in FlashFlow"""
    
    @staticmethod
    def generate_transition_styles():
        """Generate CSS transitions for smooth animations"""
        return '''
        /* FlashFlow Transition Classes */
        .ff-fade-in {
            animation: ffFadeIn 0.3s ease-in-out;
        }
        
        .ff-fade-out {
            animation: ffFadeOut 0.3s ease-in-out;
        }
        
        .ff-slide-up {
            animation: ffSlideUp 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        
        .ff-slide-down {
            animation: ffSlideDown 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        
        .ff-slide-left {
            animation: ffSlideLeft 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        
        .ff-slide-right {
            animation: ffSlideRight 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        
        .ff-bounce {
            animation: ffBounce 0.6s ease;
        }
        
        .ff-pulse {
            animation: ffPulse 1s infinite;
        }
        
        .ff-spin {
            animation: ffSpin 1s linear infinite;
        }
        
        .ff-flip {
            animation: ffFlip 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }
        
        .ff-zoom-in {
            animation: ffZoomIn 0.3s ease-out;
        }
        
        .ff-zoom-out {
            animation: ffZoomOut 0.3s ease-out;
        }
        
        /* Keyframe Animations */
        @keyframes ffFadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes ffFadeOut {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(10px);
            }
        }
        
        @keyframes ffSlideUp {
            from {
                transform: translateY(100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes ffSlideDown {
            from {
                transform: translateY(-100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes ffSlideLeft {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes ffSlideRight {
            from {
                transform: translateX(-100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes ffBounce {
            0%, 20%, 50%, 80%, 100% {
                transform: translateY(0);
            }
            40% {
                transform: translateY(-20px);
            }
            60% {
                transform: translateY(-10px);
            }
        }
        
        @keyframes ffPulse {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
            100% {
                transform: scale(1);
            }
        }
        
        @keyframes ffSpin {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }
        
        @keyframes ffFlip {
            0% {
                transform: perspective(400px) rotateY(90deg);
                opacity: 0;
            }
            40% {
                transform: perspective(400px) rotateY(-10deg);
            }
            70% {
                transform: perspective(400px) rotateY(10deg);
            }
            100% {
                transform: perspective(400px) rotateY(0deg);
                opacity: 1;
            }
        }
        
        @keyframes ffZoomIn {
            from {
                opacity: 0;
                transform: scale(0.8);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes ffZoomOut {
            from {
                opacity: 1;
                transform: scale(1);
            }
            to {
                opacity: 0;
                transform: scale(0.8);
            }
        }
        
        /* Hover Animations */
        .ff-hover-grow {
            transition: transform 0.3s ease;
        }
        
        .ff-hover-grow:hover {
            transform: scale(1.05);
        }
        
        .ff-hover-float {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .ff-hover-float:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        .ff-hover-shadow {
            transition: box-shadow 0.3s ease;
        }
        
        .ff-hover-shadow:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .ff-hover-tilt {
            transition: transform 0.3s ease;
        }
        
        .ff-hover-tilt:hover {
            transform: rotate(2deg);
        }
        '''
    
    @staticmethod
    def generate_animation_script():
        """Generate JavaScript for dynamic animations"""
        return '''
        <script>
        // FlashFlow Animation Utilities
        class FlashFlowAnimations {
            static fadeIn(element, duration = 300) {
                element.style.opacity = '0';
                element.style.transform = 'translateY(10px)';
                element.style.transition = `opacity ${duration}ms ease-in-out, transform ${duration}ms ease-in-out`;
                
                setTimeout(() => {
                    element.style.opacity = '1';
                    element.style.transform = 'translateY(0)';
                }, 10);
            }
            
            static fadeOut(element, duration = 300, callback = null) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
                element.style.transition = `opacity ${duration}ms ease-in-out, transform ${duration}ms ease-in-out`;
                
                setTimeout(() => {
                    element.style.opacity = '0';
                    element.style.transform = 'translateY(10px)';
                    
                    if (callback) {
                        setTimeout(callback, duration);
                    }
                }, 10);
            }
            
            static slideUp(element, duration = 400) {
                element.style.transform = 'translateY(100%)';
                element.style.opacity = '0';
                element.style.transition = `all ${duration}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)`;
                
                setTimeout(() => {
                    element.style.transform = 'translateY(0)';
                    element.style.opacity = '1';
                }, 10);
            }
            
            static slideDown(element, duration = 400) {
                element.style.transform = 'translateY(-100%)';
                element.style.opacity = '0';
                element.style.transition = `all ${duration}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)`;
                
                setTimeout(() => {
                    element.style.transform = 'translateY(0)';
                    element.style.opacity = '1';
                }, 10);
            }
            
            static bounce(element) {
                element.classList.add('ff-bounce');
                setTimeout(() => {
                    element.classList.remove('ff-bounce');
                }, 600);
            }
            
            static pulse(element) {
                element.classList.add('ff-pulse');
                setTimeout(() => {
                    element.classList.remove('ff-pulse');
                }, 1000);
            }
            
            static spin(element) {
                element.classList.add('ff-spin');
            }
            
            static stopSpin(element) {
                element.classList.remove('ff-spin');
            }
        }
        
        // Auto-initialize animations on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Apply hover animations to elements with ff-hover-* classes
            const hoverElements = document.querySelectorAll('[class*="ff-hover-"]');
            hoverElements.forEach(element => {
                element.style.transition = 'all 0.3s ease';
            });
        });
        </script>
        '''
    
    @staticmethod
    def generate_loading_animations():
        """Generate CSS for loading animations"""
        return '''
        /* FlashFlow Loading Animations */
        
        .ff-loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(59, 130, 246, 0.3);
            border-radius: 50%;
            border-top-color: #3B82F6;
            animation: ffSpin 1s linear infinite;
        }
        
        .ff-loading-dots {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }
        
        .ff-loading-dots span {
            width: 8px;
            height: 8px;
            background-color: #3B82F6;
            border-radius: 50%;
            display: inline-block;
            animation: ffLoadingDots 1.4s ease-in-out infinite both;
        }
        
        .ff-loading-dots span:nth-child(1) {
            animation-delay: -0.32s;
        }
        
        .ff-loading-dots span:nth-child(2) {
            animation-delay: -0.16s;
        }
        
        @keyframes ffLoadingDots {
            0%, 80%, 100% {
                transform: scale(0);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        .ff-loading-bar {
            width: 100%;
            height: 4px;
            background-color: #e5e7eb;
            border-radius: 2px;
            overflow: hidden;
        }
        
        .ff-loading-bar-inner {
            height: 100%;
            background-color: #3B82F6;
            border-radius: 2px;
            animation: ffLoadingBar 2s ease-in-out infinite;
        }
        
        @keyframes ffLoadingBar {
            0% {
                width: 0%;
                transform: translateX(-100%);
            }
            50% {
                width: 100%;
                transform: translateX(0%);
            }
            100% {
                width: 100%;
                transform: translateX(100%);
            }
        }
        '''

# Export utility functions
def generate_transitions():
    """Generate CSS transitions"""
    return AnimationUtils.generate_transition_styles()

def generate_animation_script():
    """Generate JavaScript for animations"""
    return AnimationUtils.generate_animation_script()

def generate_loading_animations():
    """Generate CSS for loading animations"""
    return AnimationUtils.generate_loading_animations()