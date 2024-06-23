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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" />
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        .container {{
            max-width: 1200px;
            margin: auto;
        }}
        .sidebar {{
            width: 250px;
            float: left;
        }}
        .content {{
            margin-left: 270px;
        }}
        .navbar-right {{
            margin-right: 0;
        }}
        .navbar-header {{
            float: left;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="#"><i class="fas fa-yin-yang"></i> YANG Tree View</a>
            </div>
            <div class="navbar-right">
                <input type="text" class="form-control" id="search-box" placeholder="Search..." style="margin-top: 8px;">
            </div>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="sidebar">
            <button id="toggle-all" class="btn btn-default"><i class="fas fa-plus-circle"></i></button>
            <div id="jstree">
                {tree_html}
            </div>
        </div>
        <div class="content">
            <h2>YANG Module Details</h2>
            <!-- You can add more content here -->
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/jstree.min.js"></script>
    <script>
        $(document).ready(function() {{
            $('#jstree').jstree({{
                "core": {{
                    "themes": {{
                        "dots": false
                    }},
                    "check_callback": true
                }},
                "types": {{
                    "default": {{
                        "icon": "fas fa-folder"
                    }},
                    "file": {{
                        "icon": "fas fa-leaf"
                    }}
                }},
                "plugins": ["search", "types"]
            }});

            var isExpanded = false;
            $('#toggle-all').click(function() {{
                if (isExpanded) {{
                    $('#jstree').jstree('close_all');
                    $(this).find('i').removeClass('fa-minus-circle').addClass('fa-plus-circle');
                }} else {{
                    $('#jstree').jstree('open_all');
                    $(this).find('i').removeClass('fa-plus-circle').addClass('fa-minus-circle');
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
