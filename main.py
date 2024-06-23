import argparse
import libyang
from ytree import load_modules, generate_html_tree, create_html_output


def main():
    parser = argparse.ArgumentParser(description="Generate YANG tree view.")
    parser.add_argument('--yang-dir', required=True,
                        help='Search path, used recursively')
    parser.add_argument('-m', '--module', action='append',
                        help='YANG module, e.g., ietf-system')
    parser.add_argument('-e', '--feature', action='append',
                        help='Enable features for the last module, e.g., ntp')
    parser.add_argument('-o', '--output', default='ytree.html',
                        help='Output HTML')

    args = parser.parse_args()
    if not args.module:
        parser.error('No modules specified. Use -m to specify modules.')

    modules = []
    current_features = []
    for module in args.module:
        if args.feature:
            current_features = [feature for feature in args.feature if feature]
        modules.append((module, current_features))
        args.feature = None  # Reset for the next module

    ctx = libyang.Context(args.yang_dir)
    loaded_modules = load_modules(ctx, modules)

    tree_html = generate_html_tree(loaded_modules)
    create_html_output(tree_html, args.output)


if __name__ == '__main__':
    main()
