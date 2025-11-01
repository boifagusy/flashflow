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
    </style>
</head>
<body>
    <div class="demo-container">
        <h1>🧩 FlashFlow Micro-Interactions Demo</h1>
        
        <div class="interaction-demo">
            <div class="interaction-title">1️⃣ Floating Label Input</div>
            <div class="interaction-description">Label moves above the input when typing or focused (Material style)</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">2️⃣ Password Reveal Toggle</div>
            <div class="interaction-description">Eye icon lets user show/hide password text</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">3️⃣ Input Focus Glow</div>
            <div class="interaction-description">Input field glows on focus or validation result</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">4️⃣ Async Loading Spinner</div>
            <div class="interaction-description">Circular spinner or ring animation while waiting for response</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">5️⃣ Toast Notification</div>
            <div class="interaction-description">Small bottom popup for instant feedback ("Saved ✓", "Error!")</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">6️⃣ Success/Error Flash</div>
            <div class="interaction-description">Form or section briefly flashes green/red after submission</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">7️⃣ Modal Confirm Dialog</div>
            <div class="interaction-description">"Are you sure?" popup for confirm/cancel actions</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">8️⃣ Progress Bar Animation</div>
            <div class="interaction-description">Linear bar fills smoothly as a task progresses</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">9️⃣ Hover Lift Card</div>
            <div class="interaction-description">Card lifts slightly with shadow when hovered or focused</div>
        </div>
        
        <div class="interaction-demo">
            <div class="interaction-title">🔟 Pulse Indicator</div>
            <div class="interaction-description">Small dot or icon that gently pulses to show active/live state</div>
        </div>
    </div>
</body>
</html>"""
    
    # Write demo HTML file
    demo_path = Path("micro-interactions-demo.html")
    with open(demo_path, "w") as f:
        f.write(demo_html)
    
    click.echo(f"Demo HTML file created: {demo_path.absolute()}")
    click.echo("Open this file in your browser to see the micro-interactions showcase.")

if __name__ == '__main__':
    demo_micro_interactions()