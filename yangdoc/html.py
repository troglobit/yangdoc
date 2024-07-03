import logging


def construct_xpath(node):
    parts = []
    while node:
        if node.parent() is None:
            # Root node, include the module name
            parts.insert(0, f"{node.module().name()}:{node.name()}")
        else:
            parts.insert(0, f"{node.module().prefix()}:{node.name()}")
        node = node.parent()
    return "/" + "/".join(parts)


def get_type_definition(node):
    try:
        type_ = node.type()
        if type_:
            return type_.name()
        return "unknown"
    except Exception as err:
        logging.error("Error getting type definition: %s", err)
        return "unknown"


def generate_tree(node, depth=0, ctx=None, exclusions=None):
    if node.deprecated() or node.obsolete():
        status = "deprecated" if node.deprecated() else "obsolete"
        logging.info("Skipping %s node %s", status, construct_xpath(node))
        return ""

    logging.debug('%s: is a %s type %s in %s', node.name(),
                  node.keyword(), node.nodetype(),
                  node.parent().name() if node.parent() else None)
    if node.description():
        description = node.description()
    else:
        description = "No description available"
    if hasattr(node, 'default') and node.default():
        default_attr = f' data-default="{node.default()}"'
    else:
        default_attr = ''

    if exclusions is None:
        exclusions = []

    if node.name() in exclusions and depth == 0:
        logging.info("Excluding top-level node %s", node.name())
        return ""

    is_leaf = not hasattr(node, 'children') or not any(node.children())

    node_type = 'file' if is_leaf else 'default'
    node_prefix = ""
    if node.keyword() == "rpc":
        node_prefix = "rpc: "
        node_type = 'rpc'
    elif node.keyword() == "action":
        node_prefix = "action: "
        node_type = 'action'
    elif node.keyword() == "notification":
        node_prefix = "notify: "
        node_type = 'notification'
    elif node.keyword() in ["leaf", "leaf-list"]:
        parent = node.parent()
        logging.debug('%s: is a leaf with parent \'%s\'', node.name(),
                      parent.keyword() if parent else None)
        if parent and parent.keyword() == "input":
            node_prefix = "Input: "
            node_type = 'input'
        elif parent and parent.keyword() == "output":
            node_prefix = "Output: "
            node_type = 'output'

    xpath = construct_xpath(node)
    if node.keyword() in ["leaf", "leaf-list"]:
        node_type_info = get_type_definition(node)
    else:
        node_type_info = "N/A"

    if node.mandatory():
        mandatory = ' data-mandatory="Yes"'
    else:
        mandatory = ''

    if node.config_false():
        read_only = ' data-read-only="(read-only)"'
    else:
        read_only = ''

    tree = f'<li data-jstree=\'{{"type": "{node_type}"}}\' data-description="{description}"{default_attr} data-xpath="{xpath}" data-node-type="{node_type_info}"{mandatory}{read_only}>' \
           f'<abbr title="{description}">{node_prefix}{node.name()}</abbr>'
    logging.debug('item: %s - %s - %s', node.name(), node_type, node_prefix)

    if not is_leaf:
        tree += '<ul>'
        for child in node.children():
            tree += generate_tree(child, depth + 1, ctx, exclusions)
        tree += '</ul>'
    tree += '</li>'

    return tree


def generate_html_tree(ctx, exclusions):
    tree_html = '<ul>'
    for module in ctx:
        logging.info('Processing module %s', module.name())
        for node in module.children():
            tree_html += generate_tree(node, ctx=ctx, exclusions=exclusions)
    tree_html += '</ul>'
    return tree_html


def create_html_output(tree_html, output_file):
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>YANG Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/themes/default/style.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.8.1/font/bootstrap-icons.min.css" />
    <style>
        body {{
            font-family: Arial, sans-serif;
            overflow: hidden;
        }}
        .container-xl {{
            max-width: 1200px;
            margin: auto;
        }}
        .sidebar {{
            width: 350px;
            height: calc(100vh - 70px);
            overflow-y: auto;
            position: fixed;
            top: 70px;
            resize: horizontal;
            overflow-x: hidden; /* Hide horizontal scrollbar */
        }}
        .content {{
            margin-left: 370px;
            height: calc(100vh - 120px); /* Adjust this value if needed */
            overflow-y: auto;
            padding-top: 50px;
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
            <a class="navbar-brand" href="#"><i class="bi bi-yin-yang"></i> YANG Documentation</a>
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
            <div class="col-md-3 sidebar">
                <button id="toggle-all" class="btn btn-default mb-3"><i class="bi bi-plus-circle me-2"></i>Expand/Collapse All</button>
                <div id="jstree">
                    {tree_html}
                </div>
            </div>
            <div class="col-md-9 content">
                <h3>XPath</h3>
                <pre id="xpath">Select a node in the tree to see its XPath.</pre>
                <h3>Description</h3>
                <pre id="description">Select a node in the tree for its YANG description.</pre>
                <h3 id="type-heading" style="display: none;">Type</h3>
                <pre id="node-type" style="display: none;"></pre>
                <h3 id="mandatory-heading" style="display: none;">Mandatory</h3>
                <pre id="node-mandatory" style="display: none;"></pre>
                <h3 id="default-heading" style="display: none;">Default</h2>
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
                        "icon": "bi bi-folder-plus"
                    }},
                    "file": {{
                        "icon": "bi bi-geo-alt"
                    }},
                    "rpc": {{
                        "icon": "bi bi-gear"
                    }},
                    "action": {{
                        "icon": "bi bi-play-circle"
                    }},
                    "notification": {{
                        "icon": "bi bi-bell"
                    }},
                    "input": {{
                        "icon": "bi bi-box-arrow-in-left"
                    }},
                    "output": {{
                        "icon": "bi bi-box-arrow-right"
                    }}
                }},
                "plugins": ["search", "types"]
            }});

            var isExpanded = false;
            $('#toggle-all').click(function() {{
                if (isExpanded) {{
                    $('#jstree').jstree('close_all');
                    $(this).find('i').removeClass('bi-dash-circle').addClass('bi-plus-circle');
                }} else {{
                    $('#jstree').jstree('open_all');
                    $(this).find('i').removeClass('bi-plus-circle').addClass('bi-dash-circle');
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
                var xpath = data.instance.get_node(data.node, true).data('xpath') || "No XPath available";
                var nodeType = data.instance.get_node(data.node, true).data('node-type') || "No type available";
                var mandatory = data.instance.get_node(data.node, true).data('mandatory') || "";
                var readOnly = data.instance.get_node(data.node, true).data('read-only') || "";

                $('#xpath').text(xpath);
                $('#description').text(description);
                if (defaultValue) {{
                    $('#default-value').text(defaultValue).show();
                    $('#default-heading').show();
                }} else {{
                    $('#default-value').hide();
                    $('#default-heading').hide();
                }}
                if (nodeType && nodeType !== "N/A") {{
                    var tmp = nodeType;
                    if (readOnly) {{
                        tmp += ` ${{readOnly}}`;
                    }}
                    $('#node-type').text(tmp).show();
                    $('#type-heading').show();
                }} else {{
                    $('#node-type').hide();
                    $('#type-heading').hide();
                }}
                if (mandatory) {{
                    $('#node-mandatory').text(mandatory).show();
                    $('#mandatory-heading').show();
                }} else {{
                    $('#node-mandatory').hide();
                    $('#mandatory-heading').hide();
                }}
            }});

            $('#jstree').on('open_node.jstree', function (e, data) {{
                data.instance.set_icon(data.node, 'bi bi-folder-minus');
            }});

            $('#jstree').on('close_node.jstree', function (e, data) {{
                data.instance.set_icon(data.node, 'bi bi-folder-plus');
            }});

            // Handle sidebar resizing
            const sidebar = document.querySelector('.sidebar');
            const content = document.querySelector('.content');

            new ResizeObserver(entries => {{
                for (let entry of entries) {{
                    content.style.marginLeft = `${{entry.contentRect.width + 50}}px`;
                }}
            }}).observe(sidebar);
        }});
    </script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_template)

    logging.info('HTML file generated: %s', output_file)
