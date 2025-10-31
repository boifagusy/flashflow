"""
FlashFlow 'demo-form' command - Demonstrate enhanced form features
"""

import click
from flask import Flask, render_template_string
from flashflow_cli.components.form_utils import generate_form_field, generate_form_styles, generate_form_validation_script

@click.command()
def demo_form():
    """Demonstrate FlashFlow's enhanced form features including beautiful error feedback and password visibility toggle"""
    
    app = Flask(__name__)
    
    @app.route('/')
    def form_demo():
        # Generate form fields with enhanced features
        username_field = generate_form_field("Username", "text", "Enter your username", True)
        email_field = generate_form_field("Email", "email", "Enter your email address", True)
        password_field = generate_form_field("Password", "password", "Enter your password", True)
        confirm_password_field = generate_form_field("Confirm Password", "password", "Confirm your password", True)
        phone_field = generate_form_field("Phone Number", "tel", "Enter your phone number")
        
        # Generate styles and scripts
        form_styles = generate_form_styles()
        form_scripts = generate_form_validation_script()
        
        # Render template with enhanced form features
        template = open('flashflow_cli/templates/enhanced_form.html').read()
        
        return render_template_string(
            template,
            username_field=username_field,
            email_field=email_field,
            password_field=password_field,
            confirm_password_field=confirm_password_field,
            phone_field=phone_field,
            form_styles=form_styles,
            form_scripts=form_scripts
        )
    
    click.echo("🎨 Starting FlashFlow Enhanced Form Demo")
    click.echo("📍 Available at: http://localhost:8082")
    click.echo("👀 Form demo server is running... (Ctrl+C to stop)")
    
    app.run(host='localhost', port=8082, debug=True, use_reloader=False)

if __name__ == '__main__':
    demo_form()