import logging


def generate_tree(node, depth=0):
    if node.description():
        description = node.description()
    else:
        description = "No description available"

    is_leaf = not hasattr(node, 'children') or not any(node.children())
    node_type = 'file' if is_leaf else 'default'

    tree = f'<li data-jstree=\'{{"type": "{node_type}"}}\'>' \
           f'<abbr title="{description}">{node.name()}</abbr>'
    logging.debug('%s - %s - %s', node.name(), node.keyword(), node.nodetype())

    if not is_leaf:
        tree += '<ul>'
        for child in node.children():
            tree += generate_tree(child, depth + 1)
        tree += '</ul>'
    tree += '</li>'

    return tree


def generate_html_tree(modules):
    tree_html = '<ul>'
    for module in modules:
        logging.info('Processing module %s', module.name())
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
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/themes/default/style.min.css" />
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
    </style>
</head>
<body>
    <h1>YANG Tree View <input type="text" id="search-box" placeholder="Search..."></h1>
    <button id="toggle-all"><i class="glyphicon glyphicon-plus-sign"></i></button>
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
                        "dots": false,
                        "responsive": false,
                        "stripes": true,
                        "variant": "large"
                    }},
                    "check_callback": true
                }},
                "types": {{
                    "default": {{
                        "icon": "glyphicon glyphicon-folder-close"
                    }},
                    "file": {{
                        "icon": "glyphicon glyphicon-leaf"
                    }}
                }},
                "plugins": ["search", "types"]
            }});

            var isExpanded = false;
            $('#toggle-all').click(function() {{
                if (isExpanded) {{
                    $('#jstree').jstree('close_all');
                    $(this).find('i').removeClass('glyphicon-minus-sign').addClass('glyphicon-plus-sign');
                }} else {{
                    $('#jstree').jstree('open_all');
                    $(this).find('i').removeClass('glyphicon-plus-sign').addClass('glyphicon-minus-sign');
                }}
                isExpanded = !isExpanded;
            }});

            var to = false;
            $('#search-box').keyup(function () {{
                if(to) {{ clearTimeout(to); }}
                to = setTimeout(function () {{
                    var v = $('#search-box').val();
                    $('#jstree').jstree(true).search(v);
                }}, 250);
            }});
        }});
    </script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_template)

    logging.info('HTML file generated: %s', output_file)
