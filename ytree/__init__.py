import libyang
import re

def parse_modules(modules):
    parsed_modules = []
    for module in modules:
        match = re.match(r'(\S+)\s*(.*)', module)
        if match:
            module_name = match.group(1)
            features = re.findall(r'-e\s+(\S+)', match.group(2))
            parsed_modules.append((module_name, features))
    return parsed_modules

def load_modules(ctx, modules):
    loaded_modules = []
    for module_name, features in modules:
        module = ctx.load_module(module_name.split('@')[0])
        for feature in features:
            module.feature_enable(feature)
        loaded_modules.append(module)
    return loaded_modules

def generate_tree(node, depth=0):
    description = node.description() if node.description() else "No description available"
    tree = f'<li data-jstree=\'{{"opened": true}}\'><abbr title="{description}">{node.name()}</abbr>'
    print(f'DEBUG: {node.name()} - {node.keyword()} - {node.nodetype()}')

    if node.keyword() in ['container', 'list', 'choice', 'case']:
        tree += '<ul>'
        for child in node.children():
            tree += generate_tree(child, depth + 1)
        tree += '</ul>'
    tree += '</li>'
    return tree

def generate_html_tree(modules):
    tree_html = '<ul>'
    for module in modules:
        print(f'DEBUG: Processing module {module.name()}')  # Debug print
        for node in module.children():
            tree_html += generate_tree(node)
    tree_html += '</ul>'
    return tree_html

def create_html_output(tree_html, output_file):
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>YANG Tree View</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/themes/default/style.min.css" />
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        #jstree {{
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <h1>YANG Tree View</h1>
    <div id="jstree">
        {tree_html}
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/jstree.min.js"></script>
    <script>
        $(document).ready(function() {{
            $('#jstree').jstree({{
                "core": {{
                    "themes": {{
                        "variant": "large"
                    }}
                }},
                "plugins": ["search"]
            }});
        }});
    </script>
</body>
</html>
"""

    with open(output_file, 'w') as f:
        f.write(html_template)

    print(f"HTML file generated: {output_file}")
