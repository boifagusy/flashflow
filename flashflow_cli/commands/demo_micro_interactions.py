"""
Demo command for micro-interactions
"""

import click
from pathlib import Path

@click.command()
def demo_micro_interactions():
    """Demo command to showcase micro-interactions"""
    click.echo("Micro-Interactions Demo")
    click.echo("======================")
    click.echo()
    click.echo("1. Floating Label Input - Label moves above the input when typing or focused")
    click.echo("2. Password Reveal Toggle - Eye icon lets user show/hide password text")
    click.echo("3. Input Focus Glow - Input field glows on focus")
    click.echo("4. Async Loading Spinner - Circular spinner while waiting for response")
    click.echo("5. Toast Notification - Small popup for instant feedback")
    click.echo("6. Success/Error Flash - Form briefly flashes after submission")
    click.echo("7. Modal Confirm Dialog - 'Are you sure?' popup for confirm/cancel actions")
    click.echo("8. Progress Bar Animation - Linear bar fills smoothly as a task progresses")
    click.echo("9. Hover Lift Card - Card lifts slightly with shadow when hovered")
    click.echo("10. Pulse Indicator - Small dot that gently pulses to show active status")
    click.echo("11. Page Loading Animation - Full-page loading overlay with multiple variants (spinner, ring, bar, skeleton)")
    click.echo()
    click.echo("These micro-interactions have been added to the frontend generator.")
    click.echo("They work on both Web (React) and Flet applications.")
    
    # Create a simple HTML demo file
    demo_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlashFlow Micro-Interactions Demo</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .demo-container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .interaction-demo {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #eee;
            border-radius: 6px;
        }
        .interaction-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .interaction-description {
            color: #666;
            font-size: 14px;
        }
        
        /* Page Loading Animation Styles */
        .ff-page-loading {
            position: relative;
            width: 100%;
            height: 150px;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            margin-top: 10px;
        }
        
        .ff-loading-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
        }
        
        .ff-loading-message {
            font-size: 1rem;
            color: #333;
            font-weight: 500;
        }
        
        .ff-loading-progress-text {
            font-size: 0.9rem;
            color: #666;
        }
        
        /* Loading Spinner */
        .ff-loading-spinner {
            border: 4px solid rgba(59, 130, 246, 0.3);
            border-radius: 50%;
            border-top: 4px solid #3B82F6;
            animation: ffSpin 1s linear infinite;
        }
        
        .ff-spinner-lg {
            width: 40px;
            height: 40px;
        }
        
        @keyframes ffSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="demo-container">
        <h1>FlashFlow Micro-Interactions Demo</h1>
        
        <div class="interaction-demo">
            <div class="interaction-title">1. Floating Label Input</div>
            <div class="interaction-description">Label moves above the input when typing or focused (Material style)</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">2. Password Reveal Toggle</div>
            <div class="interaction-description">Eye icon lets user show/hide password text</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">3. Input Focus Glow</div>
            <div class="interaction-description">Input field glows on focus or validation result</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">4. Async Loading Spinner</div>
            <div class="interaction-description">Circular spinner or ring animation while waiting for response</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">5. Toast Notification</div>
            <div class="interaction-description">Small bottom popup for instant feedback ("Saved", "Error!")</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">6. Success/Error Flash</div>
            <div class="interaction-description">Form or section briefly flashes green/red after submission</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">7. Modal Confirm Dialog</div>
            <div class="interaction-description">"Are you sure?" popup for confirm/cancel actions</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">8. Progress Bar Animation</div>
            <div class="interaction-description">Linear bar fills smoothly as a task progresses</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">9. Hover Lift Card</div>
            <div class="interaction-description">Card lifts slightly with shadow when hovered or focused</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">10. Pulse Indicator</div>
            <div class="interaction-description">Small dot or icon that gently pulses to show active/live state</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">11. Page Loading Animation</div>
            <div class="interaction-description">Full-page loading overlay with multiple variants (spinner, ring, bar, skeleton)</div>
            <div id="page-loading-demo" class="ff-page-loading ff-loading-spinner">
                <div class="ff-loading-content">
                    <div class="ff-loading-spinner ff-spinner-lg"></div>
                    <div class="ff-loading-message">Loading your content...</div>
                    <div class="ff-loading-progress-text">0%</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Write demo HTML file with UTF-8 encoding
    demo_path = Path("micro-interactions-demo.html")
    with open(demo_path, "w", encoding="utf-8") as f:
        f.write(demo_html)
    
    click.echo(f"Demo HTML file created: {demo_path.absolute()}")
    click.echo("Open this file in your browser to see the micro-interactions showcase.")

if __name__ == '__main__':
    demo_micro_interactions()