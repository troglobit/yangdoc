import os
import libyang
import logging


def find_yang_file(yang_dir, module_name):
    base_module_name = module_name.split('@')[0]
    for root, _, files in os.walk(yang_dir):
        for file in files:
            if file.startswith(base_module_name) and file.endswith(".yang"):
                return os.path.join(root, file)
    return None


def load_module(ctx, module_name, features, yang_dir):
    try:
        module_path = find_yang_file(yang_dir, module_name)
        if not module_path:
            logging.error(f"Error: Module file {module_name} not found in {yang_dir}.")
            return None

        with open(module_path, "r", encoding="utf-8") as module_file:
            logging.info(f"Parsing {module_name}, enabling features: {features}")
            module = ctx.parse_module_file(module_file, features=features)
            return module
    except libyang.util.LibyangError as err:
        logging.warning(f"Warning: {err}")
    except FileNotFoundError as err:
        logging.error(f"Error: {err}")
    return None


def generate_tree(node, depth=0):
    description = node.description() if node.description() else "No description available"
    tree = f'<li data-jstree=\'{{"opened": false}}\'><abbr title="{description}">{node.name()}</abbr>'
    logging.debug("%s - %s - %s", node.name(), node.keyword(), node.nodetype())

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
        logging.info("Processing module %s", module.name())
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
        .jstree-icon {{
            display: none;
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

            $('#jstree').on('open_node.jstree close_node.jstree', function (e, data) {{
                data.instance.set_icon(data.node, data.node.state.opened ? 'glyphicon glyphicon-minus' : 'glyphicon glyphicon-plus');
            }});

            $('#jstree').jstree(true).get_json('#', {{ 'flat': true }}).forEach(function (node) {{
                $('#jstree').jstree('set_icon', node.id, 'glyphicon glyphicon-plus');
            }});
        }});
    </script>
</body>
</html>
"""

    with open(output_file, 'w', encoding="utf-8") as file:
        file.write(html_template)

    logging.info("HTML file generated: %s", output_file)
