"""
FlashFlow Form Utilities - Enhanced form input features
Provides beautiful error feedback and password visibility toggle functionality
"""

class FormUtils:
    """Utility class for enhanced form handling in FlashFlow"""
    
    @staticmethod
    def generate_form_field(field_name, field_type="text", placeholder="", required=False, value=""):
        """
        Generate HTML for a form field with enhanced features
        
        Args:
            field_name (str): Name of the field
            field_type (str): Type of the field (text, password, email, etc.)
            placeholder (str): Placeholder text
            required (bool): Whether the field is required
            value (str): Default value for the field
            
        Returns:
            str: HTML string for the form field
        """
        field_id = field_name.replace(" ", "-").lower()
        
        if field_type == "password":
            return FormUtils._generate_password_field(field_id, field_name, placeholder, required, value)
        else:
            return FormUtils._generate_standard_field(field_id, field_name, field_type, placeholder, required, value)
    
    @staticmethod
    def _generate_standard_field(field_id, field_name, field_type, placeholder, required, value):
        """Generate HTML for a standard form field"""
        required_attr = "required" if required else ""
        value_attr = f'value="{value}"' if value else ""
        
        return f'''
        <div class="form-group">
            <label for="{field_id}">{field_name}</label>
            <input type="{field_type}" id="{field_id}" name="{field_id}" 
                   class="form-control" placeholder="{placeholder}" 
                   {required_attr} {value_attr}>
            <div class="error-message" id="{field_id}-error"></div>
        </div>
        '''
    
    @staticmethod
    def _generate_password_field(field_id, field_name, placeholder, required, value):
        """Generate HTML for a password field with visibility toggle"""
        required_attr = "required" if required else ""
        value_attr = f'value="{value}"' if value else ""
        
        return f'''
        <div class="form-group">
            <label for="{field_id}">{field_name}</label>
            <div class="password-field-container">
                <input type="password" id="{field_id}" name="{field_id}" 
                       class="form-control password-input" placeholder="{placeholder}" 
                       {required_attr} {value_attr}>
                <button type="button" class="password-toggle" 
                        onclick="togglePasswordVisibility('{field_id}')"
                        aria-label="Toggle password visibility">
                    👁️
                </button>
            </div>
            <div class="error-message" id="{field_id}-error"></div>
        </div>
        '''
    
    @staticmethod
    def generate_form_validation_script():
        """
        Generate JavaScript for form validation with beautiful persistent error feedback
        
        Returns:
            str: JavaScript code for form validation
        """
        return '''
        <script>
        // Form validation with beautiful persistent error feedback
        class FlashFlowFormValidator {
            constructor() {
                this.init();
            }
            
            init() {
                // Add event listeners to all form fields
                document.addEventListener('DOMContentLoaded', () => {
                    const formControls = document.querySelectorAll('.form-control');
                    formControls.forEach(control => {
                        // Only validate on blur to avoid annoying real-time validation
                        control.addEventListener('blur', () => {
                            this.validateField(control);
                        });
                        
                        // Clear error only when field becomes valid
                        control.addEventListener('input', () => {
                            if (control.classList.contains('error')) {
                                const isValid = this.validateField(control);
                                if (isValid) {
                                    this.clearFieldError(control);
                                }
                            }
                        });
                    });
                });
            }
            
            validateField(field) {
                const fieldName = field.name || field.id;
                const fieldValue = field.value.trim();
                const errorElement = document.getElementById(`${fieldName}-error`);
                
                // Clear previous error state
                field.classList.remove('error');
                if (errorElement) {
                    errorElement.classList.remove('show');
                }
                
                // Required field validation
                if (field.hasAttribute('required') && !fieldValue) {
                    const fieldNameLabel = this.getFieldLabel(fieldName);
                    this.showFieldError(field, errorElement, `${fieldNameLabel} is required`);
                    return false;
                }
                
                // Type-specific validation
                if (fieldValue) {
                    if (field.type === 'email' && !this.isValidEmail(fieldValue)) {
                        this.showFieldError(field, errorElement, 'Please enter a valid email address');
                        return false;
                    }
                    
                    if (field.type === 'password' && fieldValue.length < 8) {
                        this.showFieldError(field, errorElement, 'Password must be at least 8 characters');
                        return false;
                    }
                    
                    // Add more validation rules as needed
                    if (field.type === 'tel' && !this.isValidPhone(fieldValue)) {
                        this.showFieldError(field, errorElement, 'Please enter a valid phone number');
                        return false;
                    }
                }
                
                return true;
            }
            
            validateForm(formElement) {
                const formControls = formElement.querySelectorAll('.form-control');
                let isFormValid = true;
                
                formControls.forEach(control => {
                    if (!this.validateField(control)) {
                        isFormValid = false;
                    }
                });
                
                return isFormValid;
            }
            
            showFieldError(field, errorElement, message) {
                field.classList.add('error');
                if (errorElement) {
                    errorElement.textContent = message;
                    errorElement.classList.add('show');
                }
            }
            
            clearFieldError(field) {
                field.classList.remove('error');
                const fieldName = field.name || field.id;
                const errorElement = document.getElementById(`${fieldName}-error`);
                if (errorElement) {
                    errorElement.classList.remove('show');
                }
            }
            
            getFieldLabel(fieldName) {
                const labelElement = document.querySelector(`label[for="${fieldName}"]`);
                return labelElement ? labelElement.textContent : fieldName.replace(/-/g, ' ');
            }
            
            isValidEmail(email) {
                const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
                return emailRegex.test(email);
            }
            
            isValidPhone(phone) {
                const phoneRegex = /^[+]?[\\d\\s\\-()]+$/;
                return phoneRegex.test(phone) && phone.replace(/[\\s\\-()]/g, '').length >= 10;
            }
        }
        
        // Initialize form validator
        const formValidator = new FlashFlowFormValidator();
        
        // Password visibility toggle function
        function togglePasswordVisibility(fieldId) {
            const passwordInput = document.getElementById(fieldId);
            const toggleButton = passwordInput.nextElementSibling;
            
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
        
        // Form submission handler
        function handleFormSubmission(formId, submitHandler) {
            const form = document.getElementById(formId);
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    
                    if (formValidator.validateForm(form)) {
                        // Form is valid, call the submit handler
                        if (submitHandler) {
                            submitHandler(new FormData(form));
                        }
                    } else {
                        // Form has errors, scroll to first error
                        const firstError = form.querySelector('.error');
                        if (firstError) {
                            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }
                });
            }
        }
        </script>
        '''
    
    @staticmethod
    def generate_form_styles():
        """
        Generate CSS styles for enhanced form elements
        
        Returns:
            str: CSS styles for forms
        """
        return '''
        <style>
        /* FlashFlow Form Styles with Beautiful Error Feedback */
        
        .form-group {
            margin-bottom: 1.5rem;
            position: relative;
        }
        
        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #D1D5DB;
            border-radius: 6px;
            font-size: 1rem;
            transition: all 0.2s ease;
            box-sizing: border-box;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #3B82F6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Error styling - persistent and beautiful */
        .form-control.error {
            border-color: #EF4444;
            background-color: #FEF2F2;
        }
        
        .form-control.error:focus {
            border-color: #EF4444;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
        }
        
        .error-message {
            color: #DC2626;
            font-size: 0.875rem;
            margin-top: 0.25rem;
            display: none;
            padding: 0.5rem;
            background-color: #FEE2E2;
            border-radius: 4px;
            border-left: 3px solid #EF4444;
        }
        
        .error-message.show {
            display: block;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Password field with visibility toggle */
        .password-field-container {
            position: relative;
        }
        
        .password-input {
            padding-right: 3rem;
        }
        
        .password-toggle {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            color: #6B7280;
            font-size: 1.2rem;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        .password-toggle:hover {
            background-color: #F3F4F6;
            color: #1F2937;
        }
        
        .password-toggle:focus {
            outline: none;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Form labels */
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #374151;
        }
        
        /* Submit button */
        .btn-submit {
            background-color: #3B82F6;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 500;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-submit:hover {
            background-color: #2563EB;
        }
        
        .btn-submit:focus {
            outline: none;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
        }
        
        .btn-submit:disabled {
            background-color: #9CA3AF;
            cursor: not-allowed;
        }
        </style>
        '''

# Export utility functions for easier access
def generate_form_field(*args, **kwargs):
    """Generate a form field with enhanced features"""
    return FormUtils.generate_form_field(*args, **kwargs)

def generate_form_validation_script():
    """Generate JavaScript for form validation"""
    return FormUtils.generate_form_validation_script()

def generate_form_styles():
    """Generate CSS styles for forms"""
    return FormUtils.generate_form_styles()