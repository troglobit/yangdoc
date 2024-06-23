import argparse
import libyang
from ytree import parse_modules, load_modules, generate_html_tree, create_html_output

def main():
    parser = argparse.ArgumentParser(description="Generate YANG tree view HTML from YANG modules.")
    parser.add_argument('modules', nargs='+', help='List of YANG modules with optional features (e.g., "foo@date.yang -e featureA -e featureB").')
    parser.add_argument('--output', default='yang_tree_view.html', help='Output HTML file')
    parser.add_argument('--yang-dir', required=True, help='Directory containing YANG modules')
    args = parser.parse_args()

    # Initialize the libyang context with the directory containing YANG modules
    ctx = libyang.Context(args.yang_dir)

    # Parse the modules and features
    modules = parse_modules(args.modules)

    # Load the modules with enabled features
    loaded_modules = load_modules(ctx, modules)

    # Generate the tree structure for the loaded modules
    tree_html = generate_html_tree(loaded_modules)

    # Create the HTML output
    create_html_output(tree_html, args.output)

if __name__ == '__main__':
    main()
