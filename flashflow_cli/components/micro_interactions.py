"""
FlashFlow Cross-Native UI Micro-Interactions
Works on both Web (React) and Flet (Python)
"""

class MicroInteractions:
    """UI micro-interactions for enhanced user experience"""
    
    @staticmethod
    def generate_floating_label_input(field_id, field_name, placeholder="", required=False, value=""):
        """
        Generate HTML for a floating label input (Material style)
        
        Args:
            field_id (str): Unique ID for the input field
            field_name (str): Display name for the field
            placeholder (str): Placeholder text
            required (bool): Whether the field is required
            value (str): Initial value
            
        Returns:
            str: HTML string for floating label input
        """
        required_attr = "required" if required else ""
        value_attr = f'value="{value}"' if value else ""
        
        return f'''
        <div class="ff-floating-input-container">
            <input type="text" id="{field_id}" name="{field_id}" 
                   class="ff-floating-input" placeholder="{placeholder}" 
                   {required_attr} {value_attr}>
            <label for="{field_id}" class="ff-floating-label">{field_name}</label>
            <div class="ff-input-underline"></div>
        </div>
        '''
    
    @staticmethod
    def generate_password_field(field_id, field_name, placeholder="", required=False, value=""):
        """
        Generate HTML for a password field with reveal toggle
        
        Args:
            field_id (str): Unique ID for the input field
            field_name (str): Display name for the field
            placeholder (str): Placeholder text
            required (bool): Whether the field is required
            value (str): Initial value
            
        Returns:
            str: HTML string for password field with toggle
        """
        required_attr = "required" if required else ""
        value_attr = f'value="{value}"' if value else ""
        
        return f'''
        <div class="ff-password-container">
            <div class="ff-floating-input-container">
                <input type="password" id="{field_id}" name="{field_id}" 
                       class="ff-floating-input ff-password-input" placeholder="{placeholder}" 
                       {required_attr} {value_attr}>
                <label for="{field_id}" class="ff-floating-label">{field_name}</label>
                <div class="ff-input-underline"></div>
            </div>
            <button type="button" class="ff-password-toggle" 
                    onclick="togglePasswordVisibility('{field_id}')"
                    aria-label="Toggle password visibility">
                👁️
            </button>
        </div>
        '''
    
    @staticmethod
    def generate_validation_input(field_id, field_name, field_type="text", placeholder="", required=False, value=""):
        """
        Generate HTML for an input with validation feedback
        
        Args:
            field_id (str): Unique ID for the input field
            field_name (str): Display name for the field
            field_type (str): Type of input (text, email, etc.)
            placeholder (str): Placeholder text
            required (bool): Whether the field is required
            value (str): Initial value
            
        Returns:
            str: HTML string for input with validation
        """
        required_attr = "required" if required else ""
        value_attr = f'value="{value}"' if value else ""
        
        return f'''
        <div class="ff-validation-container">
            <div class="ff-floating-input-container">
                <input type="{field_type}" id="{field_id}" name="{field_id}" 
                       class="ff-floating-input ff-validation-input" placeholder="{placeholder}" 
                       {required_attr} {value_attr}
                       onfocus="showValidationState('{field_id}', 'focus')"
                       onblur="showValidationState('{field_id}', 'blur')">
                <label for="{field_id}" class="ff-floating-label">{field_name}</label>
                <div class="ff-input-underline"></div>
            </div>
            <div class="ff-validation-icon" id="{field_id}-validation-icon"></div>
            <div class="ff-validation-message" id="{field_id}-validation-message"></div>
        </div>
        '''
    
    @staticmethod
    def generate_loading_spinner(spinner_id="loading-spinner", size="md"):
        """
        Generate HTML for a loading spinner
        
        Args:
            spinner_id (str): Unique ID for the spinner
            size (str): Size of spinner (sm, md, lg)
            
        Returns:
            str: HTML string for loading spinner
        """
        size_class = f"ff-spinner-{size}"
        
        return f'''
        <div class="ff-loading-container">
            <div id="{spinner_id}" class="ff-loading-spinner {size_class}"></div>
            <div class="ff-loading-text">Loading...</div>
        </div>
        '''
    
    @staticmethod
    def generate_progress_ring(ring_id="progress-ring", size=120, stroke=8):
        """
        Generate HTML for a progress ring
        
        Args:
            ring_id (str): Unique ID for the progress ring
            size (int): Size of the ring in pixels
            stroke (int): Stroke width in pixels
            
        Returns:
            str: HTML string for progress ring
        """
        radius = (size - stroke) / 2
        circumference = radius * 2 * 3.14159
        
        return f'''
        <div class="ff-progress-ring-container">
            <svg id="{ring_id}" class="ff-progress-ring" width="{size}" height="{size}">
                <circle class="ff-progress-ring-circle-bg" 
                        stroke="#e0e0e0" 
                        stroke-width="{stroke}" 
                        fill="transparent" 
                        r="{radius}" 
                        cx="{size/2}" 
                        cy="{size/2}" />
                <circle class="ff-progress-ring-circle" 
                        stroke="#3B82F6" 
                        stroke-width="{stroke}" 
                        fill="transparent" 
                        r="{radius}" 
                        cx="{size/2}" 
                        cy="{size/2}" 
                        stroke-dasharray="{circumference} {circumference}" 
                        stroke-dashoffset="{circumference}" />
            </svg>
            <div class="ff-progress-text" id="{ring_id}-text">0%</div>
        </div>
        '''
    
    @staticmethod
    def generate_toast_notification(toast_id="toast-notification", message="", type="info"):
        """
        Generate HTML for a toast notification
        
        Args:
            toast_id (str): Unique ID for the toast
            message (str): Message to display
            type (str): Type of toast (info, success, error, warning)
            
        Returns:
            str: HTML string for toast notification
        """
        type_class = f"ff-toast-{type}"
        
        return f'''
        <div id="{toast_id}" class="ff-toast-notification {type_class}">
            <div class="ff-toast-content">
                <span class="ff-toast-icon"></span>
                <span class="ff-toast-message">{message}</span>
            </div>
            <button class="ff-toast-close" onclick="hideToast('{toast_id}')">×</button>
        </div>
        '''
    
    @staticmethod
    def generate_flash_feedback(flash_id="flash-feedback", target_element="form-section"):
        """
        Generate HTML for flash feedback effect
        
        Args:
            flash_id (str): Unique ID for the flash effect
            target_element (str): Element to apply flash to
            
        Returns:
            str: HTML string for flash feedback
        """
        return f'''
        <div id="{flash_id}" class="ff-flash-overlay" data-target="{target_element}"></div>
        '''
    
    @staticmethod
    def generate_confirm_dialog(dialog_id="confirm-dialog", title="Confirm Action", message="Are you sure?"):
        """
        Generate HTML for a confirm dialog
        
        Args:
            dialog_id (str): Unique ID for the dialog
            title (str): Dialog title
            message (str): Confirmation message
            
        Returns:
            str: HTML string for confirm dialog
        """
        return f'''
        <div id="{dialog_id}" class="ff-confirm-dialog">
            <div class="ff-confirm-dialog-content">
                <div class="ff-confirm-dialog-header">
                    <h3>{title}</h3>
                </div>
                <div class="ff-confirm-dialog-body">
                    <p>{message}</p>
                </div>
                <div class="ff-confirm-dialog-footer">
                    <button class="ff-btn ff-btn-secondary" onclick="hideConfirmDialog('{dialog_id}')">Cancel</button>
                    <button class="ff-btn ff-btn-primary" onclick="confirmAction('{dialog_id}')">Confirm</button>
                </div>
            </div>
        </div>
        '''
    
    @staticmethod
    def generate_progress_bar(bar_id="progress-bar", initial_value=0):
        """
        Generate HTML for a progress bar
        
        Args:
            bar_id (str): Unique ID for the progress bar
            initial_value (int): Initial progress value (0-100)
            
        Returns:
            str: HTML string for progress bar
        """
        return f'''
        <div class="ff-progress-container">
            <div class="ff-progress-bar">
                <div id="{bar_id}" class="ff-progress-bar-fill" style="width: {initial_value}%"></div>
            </div>
            <div class="ff-progress-text" id="{bar_id}-text">{initial_value}%</div>
        </div>
        '''
    
    @staticmethod
    def generate_hover_card(card_id="hover-card", content=""):
        """
        Generate HTML for a hover lift card
        
        Args:
            card_id (str): Unique ID for the card
            content (str): Content to display in the card
            
        Returns:
            str: HTML string for hover card
        """
        return f'''
        <div id="{card_id}" class="ff-hover-card">
            <div class="ff-card-content">
                {content}
            </div>
        </div>
        '''
    
    @staticmethod
    def generate_pulse_indicator(indicator_id="pulse-indicator", status="active"):
        """
        Generate HTML for a pulse indicator
        
        Args:
            indicator_id (str): Unique ID for the indicator
            status (str): Status (active, inactive, pending)
            
        Returns:
            str: HTML string for pulse indicator
        """
        status_class = f"ff-pulse-{status}"
        
        return f'''
        <div id="{indicator_id}" class="ff-pulse-indicator {status_class}">
            <div class="ff-pulse-dot"></div>
            <div class="ff-pulse-ring"></div>
        </div>
        '''
    
    @staticmethod
    def generate_page_loading_animation(animation_id="page-loading", variant="spinner", message="Loading...", progress=0):
        """
        Generate HTML for a page loading animation with different variants
        
        Args:
            animation_id (str): Unique ID for the loading animation
            variant (str): Type of animation (spinner, ring, bar, skeleton)
            message (str): Loading message to display
            progress (int): Progress percentage (0-100) for progress-based variants
            
        Returns:
            str: HTML string for page loading animation
        """
        variant_class = f"ff-loading-{variant}"
        
        # Generate content based on variant
        if variant == "spinner":
            animation_content = f'<div class="ff-loading-spinner ff-spinner-lg"></div>'
        elif variant == "ring":
            radius = 40  # For 100px size
            circumference = radius * 2 * 3.14159
            offset = circumference - (progress / 100) * circumference
            animation_content = f'''
            <svg class="ff-loading-ring" width="100" height="100">
                <circle class="ff-progress-ring-circle-bg" 
                        stroke="#e0e0e0" 
                        stroke-width="8" 
                        fill="transparent" 
                        r="{radius}" 
                        cx="50" 
                        cy="50" />
                <circle class="ff-progress-ring-circle" 
                        stroke="#3B82F6" 
                        stroke-width="8" 
                        fill="transparent" 
                        r="{radius}" 
                        cx="50" 
                        cy="50" 
                        stroke-dasharray="{circumference} {circumference}" 
                        stroke-dashoffset="{offset}" />
            </svg>
            '''
        elif variant == "bar":
            animation_content = f'''
            <div class="ff-loading-bar">
                <div class="ff-progress-bar">
                    <div class="ff-progress-bar-fill" style="width: {progress}%"></div>
                </div>
            </div>
            '''
        elif variant == "skeleton":
            animation_content = '''
            <div class="ff-loading-skeleton">
                <div class="ff-skeleton-line"></div>
                <div class="ff-skeleton-line"></div>
                <div class="ff-skeleton-line"></div>
                <div class="ff-skeleton-line short"></div>
            </div>
            '''
        else:
            # Default to spinner
            animation_content = f'<div class="ff-loading-spinner ff-spinner-lg"></div>'
        
        return f'''
        <div id="{animation_id}" class="ff-page-loading {variant_class}">
            <div class="ff-loading-content">
                {animation_content}
                <div class="ff-loading-message">{message}</div>
                <div class="ff-loading-progress-text">{progress}%</div>
            </div>
        </div>
        '''
    
    @staticmethod
    def generate_css():
        """
        Generate CSS for all micro-interactions
        
        Returns:
            str: CSS string for micro-interactions
        """
        return '''
        /* Floating Label Input */
        .ff-floating-input-container {
            position: relative;
            margin-bottom: 1.5rem;
        }
        
        .ff-floating-input {
            width: 100%;
            padding: 1.2rem 1rem 0.5rem;
            border: none;
            border-bottom: 1px solid #ccc;
            background: transparent;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .ff-floating-input:focus {
            border-bottom: 2px solid #3B82F6;
        }
        
        .ff-floating-label {
            position: absolute;
            top: 1rem;
            left: 1rem;
            font-size: 1rem;
            color: #999;
            pointer-events: none;
            transition: all 0.3s ease;
        }
        
        .ff-floating-input:focus + .ff-floating-label,
        .ff-floating-input:not(:placeholder-shown) + .ff-floating-label {
            top: 0.5rem;
            font-size: 0.8rem;
            color: #3B82F6;
        }
        
        .ff-input-underline {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: #3B82F6;
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .ff-floating-input:focus ~ .ff-input-underline {
            transform: scaleX(1);
        }
        
        /* Password Field with Toggle */
        .ff-password-container {
            position: relative;
            margin-bottom: 1.5rem;
        }
        
        .ff-password-toggle {
            position: absolute;
            right: 0.5rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.2rem;
            padding: 0.5rem;
            border-radius: 50%;
            transition: background-color 0.3s;
        }
        
        .ff-password-toggle:hover {
            background-color: #f0f0f0;
        }
        
        /* Validation Input */
        .ff-validation-container {
            position: relative;
            margin-bottom: 1.5rem;
        }
        
        .ff-validation-input.valid {
            border-bottom: 2px solid #10B981;
        }
        
        .ff-validation-input.invalid {
            border-bottom: 2px solid #EF4444;
        }
        
        .ff-validation-icon {
            position: absolute;
            right: 0.5rem;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: none;
        }
        
        .ff-validation-icon.valid {
            display: block;
            background: #10B981;
            mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='none' stroke='%23000' stroke-width='2' d='M5 13l4 4L19 7'/%3E%3C/svg%3E");
            mask-size: contain;
        }
        
        .ff-validation-icon.invalid {
            display: block;
            background: #EF4444;
            mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='none' stroke='%23000' stroke-width='2' d='M6 18L18 6M6 6l12 12'/%3E%3C/svg%3E");
            mask-size: contain;
        }
        
        .ff-validation-message {
            font-size: 0.8rem;
            margin-top: 0.25rem;
            min-height: 1rem;
        }
        
        .ff-validation-message.error {
            color: #EF4444;
        }
        
        .ff-validation-message.success {
            color: #10B981;
        }
        
        /* Loading Spinner */
        .ff-loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 1rem;
        }
        
        .ff-loading-spinner {
            border: 4px solid rgba(59, 130, 246, 0.3);
            border-radius: 50%;
            border-top: 4px solid #3B82F6;
            animation: ffSpin 1s linear infinite;
        }
        
        .ff-spinner-sm {
            width: 20px;
            height: 20px;
        }
        
        .ff-spinner-md {
            width: 40px;
            height: 40px;
        }
        
        .ff-spinner-lg {
            width: 60px;
            height: 60px;
        }
        
        .ff-loading-text {
            margin-top: 0.5rem;
            color: #666;
            font-size: 0.9rem;
        }
        
        @keyframes ffSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Progress Ring */
        .ff-progress-ring-container {
            position: relative;
            display: inline-block;
        }
        
        .ff-progress-ring-circle {
            transition: stroke-dashoffset 0.3s ease;
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }
        
        .ff-progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1rem;
            font-weight: bold;
        }
        
        /* Toast Notification */
        .ff-toast-notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-width: 300px;
            transform: translateX(120%);
            transition: transform 0.3s ease;
            z-index: 1000;
        }
        
        .ff-toast-notification.show {
            transform: translateX(0);
        }
        
        .ff-toast-info {
            background: #3B82F6;
            color: white;
        }
        
        .ff-toast-success {
            background: #10B981;
            color: white;
        }
        
        .ff-toast-error {
            background: #EF4444;
            color: white;
        }
        
        .ff-toast-warning {
            background: #F59E0B;
            color: white;
        }
        
        .ff-toast-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .ff-toast-close {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Flash Feedback */
        .ff-flash-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0;
            z-index: 999;
        }
        
        .ff-flash-success {
            background: rgba(16, 185, 129, 0.2);
            animation: ffFlashSuccess 0.5s ease;
        }
        
        .ff-flash-error {
            background: rgba(239, 68, 68, 0.2);
            animation: ffFlashError 0.5s ease;
        }
        
        @keyframes ffFlashSuccess {
            0% { opacity: 0; }
            50% { opacity: 1; }
            100% { opacity: 0; }
        }
        
        @keyframes ffFlashError {
            0% { opacity: 0; }
            50% { opacity: 1; }
            100% { opacity: 0; }
        }
        
        /* Confirm Dialog */
        .ff-confirm-dialog {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1001;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
        }
        
        .ff-confirm-dialog.show {
            opacity: 1;
            visibility: visible;
        }
        
        .ff-confirm-dialog-content {
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            max-width: 500px;
            width: 90%;
        }
        
        .ff-confirm-dialog-header {
            padding: 1.5rem 1.5rem 0;
        }
        
        .ff-confirm-dialog-header h3 {
            margin: 0;
            color: #333;
        }
        
        .ff-confirm-dialog-body {
            padding: 1rem 1.5rem;
        }
        
        .ff-confirm-dialog-body p {
            margin: 0;
            color: #666;
        }
        
        .ff-confirm-dialog-footer {
            padding: 1rem 1.5rem 1.5rem;
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
        }
        
        /* Progress Bar */
        .ff-progress-container {
            margin-bottom: 1.5rem;
        }
        
        .ff-progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .ff-progress-bar-fill {
            height: 100%;
            background: #3B82F6;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .ff-progress-text {
            text-align: right;
            font-size: 0.8rem;
            color: #666;
            margin-top: 0.25rem;
        }
        
        /* Hover Card */
        .ff-hover-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        
        .ff-hover-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        
        /* Pulse Indicator */
        .ff-pulse-indicator {
            position: relative;
            display: inline-block;
        }
        
        .ff-pulse-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .ff-pulse-ring {
            position: absolute;
            top: -4px;
            left: -4px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid transparent;
        }
        
        .ff-pulse-active .ff-pulse-dot {
            background: #10B981;
        }
        
        .ff-pulse-active .ff-pulse-ring {
            border-color: rgba(16, 185, 129, 0.5);
            animation: ffPulseRing 1.5s infinite;
        }
        
        .ff-pulse-inactive .ff-pulse-dot {
            background: #999;
        }
        
        .ff-pulse-pending .ff-pulse-dot {
            background: #F59E0B;
        }
        
        .ff-pulse-pending .ff-pulse-ring {
            border-color: rgba(245, 158, 11, 0.5);
            animation: ffPulseRing 1.5s infinite;
        }
        
        @keyframes ffPulseRing {
            0% {
                transform: scale(0.1);
                opacity: 1;
            }
            70% {
                transform: scale(2);
                opacity: 0;
            }
            100% {
                transform: scale(2);
                opacity: 0;
            }
        }
        
        /* Page Loading Animation */
        .ff-page-loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 1;
            transition: opacity 0.3s ease;
        }
        
        .ff-page-loading.hidden {
            opacity: 0;
            pointer-events: none;
        }
        
        .ff-loading-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
        }
        
        .ff-loading-message {
            font-size: 1.2rem;
            color: #333;
            font-weight: 500;
        }
        
        .ff-loading-progress-text {
            font-size: 0.9rem;
            color: #666;
        }
        
        /* Loading Spinner Variant */
        .ff-loading-spinner {
            border: 4px solid rgba(59, 130, 246, 0.3);
            border-radius: 50%;
            border-top: 4px solid #3B82F6;
            animation: ffSpin 1s linear infinite;
        }
        
        .ff-spinner-sm {
            width: 20px;
            height: 20px;
        }
        
        .ff-spinner-md {
            width: 40px;
            height: 40px;
        }
        
        .ff-spinner-lg {
            width: 60px;
            height: 60px;
        }
        
        @keyframes ffSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Loading Ring Variant */
        .ff-loading-ring {
            animation: ffSpin 2s linear infinite;
        }
        
        /* Loading Bar Variant */
        .ff-loading-bar {
            width: 200px;
        }
        
        .ff-loading-bar .ff-progress-bar {
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .ff-loading-bar .ff-progress-bar-fill {
            height: 100%;
            background: #3B82F6;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        /* Loading Skeleton Variant */
        .ff-loading-skeleton {
            width: 300px;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .ff-skeleton-line {
            height: 20px;
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: ffSkeletonLoading 1.5s infinite;
            border-radius: 4px;
        }
        
        .ff-skeleton-line.short {
            width: 70%;
        }
        
        @keyframes ffSkeletonLoading {
            0% {
                background-position: 200% 0;
            }
            100% {
                background-position: -200% 0;
            }
        }
        
        /* Buttons */
        .ff-btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .ff-btn-primary {
            background: #3B82F6;
            color: white;
        }
        
        .ff-btn-primary:hover {
            background: #2563EB;
        }
        
        .ff-btn-secondary {
            background: #64748B;
            color: white;
        }
        
        .ff-btn-secondary:hover {
            background: #475569;
        }
        '''
    
    @staticmethod
    def generate_javascript():
        """
        Generate JavaScript for all micro-interactions
        
        Returns:
            str: JavaScript string for micro-interactions
        """
        return '''
        <script>
        // Toggle password visibility
        function togglePasswordVisibility(fieldId) {
            const passwordInput = document.getElementById(fieldId);
            const toggleButton = passwordInput.nextElementSibling || 
                                passwordInput.parentElement.querySelector('.ff-password-toggle');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleButton.textContent = '🔒';
                toggleButton.setAttribute('aria-label', 'Hide password');
            } else {
                passwordInput.type = 'password';
                toggleButton.textContent = '👁️';
                toggleButton.setAttribute('aria-label', 'Show password');
            }
        }
        
        // Show validation state
        function showValidationState(fieldId, state) {
            const input = document.getElementById(fieldId);
            const icon = document.getElementById(fieldId + '-validation-icon');
            const message = document.getElementById(fieldId + '-validation-message');
            
            if (state === 'focus') {
                input.classList.add('focused');
            } else if (state === 'blur') {
                input.classList.remove('focused');
                // Simulate validation
                if (input.value) {
                    input.classList.add('valid');
                    input.classList.remove('invalid');
                    icon.className = 'ff-validation-icon valid';
                    message.textContent = 'Looks good!';
                    message.className = 'ff-validation-message success';
                } else {
                    input.classList.add('invalid');
                    input.classList.remove('valid');
                    icon.className = 'ff-validation-icon invalid';
                    message.textContent = 'This field is required';
                    message.className = 'ff-validation-message error';
                }
            }
        }
        
        // Show toast notification
        function showToast(toastId, message, type = 'info', duration = 3000) {
            const toast = document.getElementById(toastId);
            if (!toast) return;
            
            // Set message and type
            const messageElement = toast.querySelector('.ff-toast-message');
            if (messageElement) {
                messageElement.textContent = message;
            }
            
            toast.className = `ff-toast-notification ff-toast-${type} show`;
            
            // Auto hide after duration
            setTimeout(() => {
                hideToast(toastId);
            }, duration);
        }
        
        // Hide toast notification
        function hideToast(toastId) {
            const toast = document.getElementById(toastId);
            if (toast) {
                toast.classList.remove('show');
            }
        }
        
        // Show confirm dialog
        function showConfirmDialog(dialogId, onConfirm) {
            const dialog = document.getElementById(dialogId);
            if (!dialog) return;
            
            dialog.classList.add('show');
            
            // Store callback for confirm action
            dialog.dataset.onConfirm = onConfirm.toString();
        }
        
        // Hide confirm dialog
        function hideConfirmDialog(dialogId) {
            const dialog = document.getElementById(dialogId);
            if (dialog) {
                dialog.classList.remove('show');
            }
        }
        
        // Confirm action
        function confirmAction(dialogId) {
            const dialog = document.getElementById(dialogId);
            if (!dialog) return;
            
            // Execute callback if exists
            if (dialog.dataset.onConfirm) {
                try {
                    eval('(' + dialog.dataset.onConfirm + ')()');
                } catch (e) {
                    console.error('Error executing confirm callback:', e);
                }
            }
            
            hideConfirmDialog(dialogId);
        }
        
        // Update progress ring
        function updateProgressRing(ringId, percent) {
            const ring = document.getElementById(ringId);
            if (!ring) return;
            
            const circle = ring.querySelector('.ff-progress-ring-circle');
            const text = document.getElementById(ringId + '-text');
            if (!circle || !text) return;
            
            const radius = circle.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            const offset = circumference - (percent / 100) * circumference;
            
            circle.style.strokeDasharray = `${circumference} ${circumference}`;
            circle.style.strokeDashoffset = offset;
            text.textContent = `${Math.round(percent)}%`;
        }
        
        // Update progress bar
        function updateProgressBar(barId, percent) {
            const bar = document.getElementById(barId);
            const text = document.getElementById(barId + '-text');
            if (!bar) return;
            
            bar.style.width = `${percent}%`;
            if (text) {
                text.textContent = `${Math.round(percent)}%`;
            }
        }
        
        // Show flash feedback
        function showFlashFeedback(flashId, type = 'success') {
            const flash = document.getElementById(flashId);
            if (!flash) return;
            
            const targetElementId = flash.dataset.target;
            const targetElement = document.getElementById(targetElementId);
            if (!targetElement) return;
            
            // Position flash overlay over target element
            const rect = targetElement.getBoundingClientRect();
            flash.style.top = rect.top + 'px';
            flash.style.left = rect.left + 'px';
            flash.style.width = rect.width + 'px';
            flash.style.height = rect.height + 'px';
            
            flash.className = `ff-flash-overlay ff-flash-${type}`;
            flash.style.opacity = '1';
            
            setTimeout(() => {
                flash.style.opacity = '0';
            }, 500);
        }
        
        // Show page loading animation
        function showPageLoading(animationId, variant = 'spinner') {
            const loading = document.getElementById(animationId);
            if (!loading) return;
            
            loading.classList.remove('hidden');
        }
        
        // Hide page loading animation
        function hidePageLoading(animationId) {
            const loading = document.getElementById(animationId);
            if (!loading) return;
            
            loading.classList.add('hidden');
        }
        
        // Update page loading progress
        function updatePageLoadingProgress(animationId, progress) {
            const loading = document.getElementById(animationId);
            if (!loading) return;
            
            const progressText = loading.querySelector('.ff-loading-progress-text');
            if (progressText) {
                progressText.textContent = `${Math.round(progress)}%`;
            }
            
            // Update progress bar if it exists
            const progressBar = loading.querySelector('.ff-progress-bar-fill');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
            
            // Update progress ring if it exists
            const progressRing = loading.querySelector('.ff-progress-ring-circle');
            if (progressRing) {
                const radius = progressRing.r.baseVal.value;
                const circumference = radius * 2 * Math.PI;
                const offset = circumference - (progress / 100) * circumference;
                
                progressRing.style.strokeDasharray = `${circumference} ${circumference}`;
                progressRing.style.strokeDashoffset = offset;
            }
        }
        
        // Initialize floating labels
        document.addEventListener('DOMContentLoaded', function() {
            // Add placeholder to inputs with floating labels
            const floatingInputs = document.querySelectorAll('.ff-floating-input');
            floatingInputs.forEach(input => {
                if (!input.placeholder) {
                    input.placeholder = ' ';
                }
            });
        });
        </script>
        '''

# Export utility functions
def generate_floating_label_input(*args, **kwargs):
    """Generate floating label input"""
    return MicroInteractions.generate_floating_label_input(*args, **kwargs)

def generate_password_field(*args, **kwargs):
    """Generate password field with toggle"""
    return MicroInteractions.generate_password_field(*args, **kwargs)

def generate_validation_input(*args, **kwargs):
    """Generate input with validation"""
    return MicroInteractions.generate_validation_input(*args, **kwargs)

def generate_loading_spinner(*args, **kwargs):
    """Generate loading spinner"""
    return MicroInteractions.generate_loading_spinner(*args, **kwargs)

def generate_progress_ring(*args, **kwargs):
    """Generate progress ring"""
    return MicroInteractions.generate_progress_ring(*args, **kwargs)

def generate_toast_notification(*args, **kwargs):
    """Generate toast notification"""
    return MicroInteractions.generate_toast_notification(*args, **kwargs)

def generate_flash_feedback(*args, **kwargs):
    """Generate flash feedback"""
    return MicroInteractions.generate_flash_feedback(*args, **kwargs)

def generate_confirm_dialog(*args, **kwargs):
    """Generate confirm dialog"""
    return MicroInteractions.generate_confirm_dialog(*args, **kwargs)

def generate_progress_bar(*args, **kwargs):
    """Generate progress bar"""
    return MicroInteractions.generate_progress_bar(*args, **kwargs)

def generate_hover_card(*args, **kwargs):
    """Generate hover card"""
    return MicroInteractions.generate_hover_card(*args, **kwargs)

def generate_pulse_indicator(*args, **kwargs):
    """Generate pulse indicator"""
    return MicroInteractions.generate_pulse_indicator(*args, **kwargs)

def generate_page_loading_animation(animation_id="page-loading", variant="spinner", message="Loading..."):
    """Generate page loading animation with different variants
    
    Args:
        animation_id (str): Unique ID for the loading animation
        variant (str): Type of animation (spinner, ring, bar, skeleton)
        message (str): Loading message to display
        
    Returns:
        str: HTML string for page loading animation
    """
    return MicroInteractions.generate_page_loading_animation(animation_id, variant, message)