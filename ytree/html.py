import logging


def generate_tree(node, depth=0):
    if node.description():
        description = node.description()
    else:
        description = "No description available"

    logging.debug('node: %s - %s - %s in %s', node.name(), node.keyword(),
                  node.nodetype(), node.parent().name() if node.parent() else None)

    default_value = node.default() if hasattr(node, 'default') and node.default() else None
    is_leaf = not hasattr(node, 'children') or not any(node.children())

    node_type = 'file' if is_leaf else 'default'
    node_prefix = ""
    if node.keyword() == "rpc":
        node_prefix = "rpc: "
        node_type = 'rpc'
    elif node.keyword() == "action":
        node_prefix = "action: "
        node_type = 'action'
    elif node.keyword() == "leaf":
        parent = node.parent()
        logging.debug('%s: is a leaf with parent \'%s\'', node.name(), parent.keyword() if parent else None)
        if parent and parent.keyword() == "input":
            logging.debug('%s: is an input!', node.name())
            node_prefix = "Input: "
            node_type = 'input'
        elif parent and parent.keyword() == "output":
            logging.debug('%s: is an output!', node.name())
            node_prefix = "Output: "
            node_type = 'output'
        else:
            logging.debug('%s: is just a leaf ...', node.name())

    default_attr = f' data-default="{default_value}"' if default_value else ''

    tree = f'<li data-jstree=\'{{"type": "{node_type}"}}\' data-description="{description}"{default_attr}>' \
           f'<abbr title="{description}">{node_prefix}{node.name()}</abbr>'
    logging.debug('item: %s - %s - %s', node.name(), node_type, node_prefix)

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
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" />
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
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-xl">
            <a class="navbar-brand" href="#"><i class="fas fa-yin-yang"></i> YANG Tree View</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <input type="text" class="form-control" id="search-box" placeholder="Search...">
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="container-xl mt-4">
        <div class="row">
            <div class="col-md-3">
                <button id="toggle-all" class="btn btn-default mb-3"><i class="fas fa-plus-circle me-2"></i>Expand/Collapse All</button>
                <div id="jstree">
                    {tree_html}
                </div>
            </div>
            <div class="col-md-9">
                <h2>Description</h2>
                <pre id="description">Select a node in the tree for its YANG description.</pre>
                <h2 id="default-heading" style="display: none;">Default</h2>
                <pre id="default-value" style="display: none;"></pre>
            </div>
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
                    }},
                    "rpc": {{
                        "icon": "fas fa-cog"
                    }},
                    "action": {{
                        "icon": "fas fa-play-circle"
                    }},
                    "input": {{
                        "icon": "fas fa-caret-square-left"
                    }},
                    "output": {{
                        "icon": "fas fa-caret-square-right"
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

            $('#jstree').on('select_node.jstree', function (e, data) {{
                var description = data.instance.get_node(data.node, true).data('description') || "No description available";
                var defaultValue = data.instance.get_node(data.node, true).data('default') || "";
                $('#description').text(description);
                if (defaultValue) {{
                    $('#default-value').text(defaultValue).show();
                    $('#default-heading').show();
                }} else {{
                    $('#default-value').hide();
                    $('#default-heading').hide();
                }}
            }});
        }});
    </script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_template)

    logging.info('HTML file generated: %s', output_file)
