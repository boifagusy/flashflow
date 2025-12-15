# Script to fix the frontend generator file by removing duplicate method definitions

def fix_frontend_file():
    # Read the original file
    with open(r'c:\Users\VineMaster\Desktop\flashflow\flashflow-main\flashflow_cli\generators\frontend.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find duplicate method definitions
    new_lines = []
    skip_lines = set()
    
    # Find indices of duplicate method definitions
    serverless_method_indices = []
    help_panel_indices = []
    
    for i, line in enumerate(lines):
        if 'def _generate_serverless_components(self)' in line:
            serverless_method_indices.append(i)
        if 'css_file = components_dir / "HelpPanel.css"' in line:
            help_panel_indices.append(i)
    
    # Mark lines to skip (everything after the first duplicate)
    if len(serverless_method_indices) > 1:
        # Skip from the second occurrence to the end
        start_skip = serverless_method_indices[1]
        # Find the end of the duplicate section
        end_skip = len(lines)
        for i in range(start_skip, len(lines)):
            if i > start_skip and lines[i].strip() == '' and i+1 < len(lines) and lines[i+1].startswith('    def'):
                end_skip = i
                break
        skip_lines.update(range(start_skip, end_skip))
    
    # Write the cleaned file
    with open(r'c:\Users\VineMaster\Desktop\flashflow\flashflow-main\flashflow_cli\generators\frontend_fixed.py', 'w', encoding='utf-8') as f:
        for i, line in enumerate(lines):
            if i not in skip_lines:
                f.write(line)

if __name__ == '__main__':
    fix_frontend_file()
    print("Frontend file fixed successfully!")