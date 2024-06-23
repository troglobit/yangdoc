import libyang


def load_modules(ctx, modules):
    loaded_modules = []
    for module_name, features in modules:
        module = ctx.load_module(module_name.split('@')[0])
        for feature in features:
            try:
                print(f"{module_name}: enabling {feature}")
                module.feature_enable(feature)
                onoff = module.feature_state(feature)
                print(f"{module_name}: feature {feature} is now {onoff}")
            except libyang.util.LibyangError as err:
                print(f"Warning: {err}")
        loaded_modules.append(module)
    return loaded_modules

def generate_tree(node, depth=0):
    description = node.description() if node.description() else "No description available"
    tree = f'<li data-jstree=\'{{"opened": false}}\'><abbr title="{description}">{node.name()}</abbr>'
    print(f'DEBUG: {node.name()} - {node.keyword()} - {node.nodetype()}')  # Debug print

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
    <button id="expand-all">Expand All</button>
    <button id="collapse-all">Collapse All</button>
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

            $('#expand-all').click(function() {{
                $('#jstree').jstree('open_all');
            }});

            $('#collapse-all').click(function() {{
                $('#jstree').jstree('close_all');
            }});
        }});
    </script>
</body>
</html>
"""

    with open(output_file, 'w') as f:
        f.write(html_template)

    print(f"HTML file generated: {output_file}")
