import sys
import libyang
import logging
from yangdoc import load_module, get_version
from yangdoc.html import generate_html_tree, create_html_output


def usage():
    text = """Usage: yangdoc [options]

Options:
  -d, --debug               Enable debug output
  -e, --feature  <feature>  Feature(s) for current module
  -h, --help                Show this help message and exit
  -m, --module   <module>   YANG module to load
  -o, --output   <file>     Output HTML file, default: yangdoc.html
  -p, --yang-dir <path>     YANG module search path
  -x, --exclude  <node>     Exclude top-level container/node
  -v, --version             Show the version and exit

Example:
  yangdoc -m ietf-system -e authentication -e ntp -m ietf-system -e if-mib
"""
    print(text)


def main():
    # Get the command line arguments excluding the script name
    arguments = sys.argv[1:]

    module_features = {}
    yang_dir = None
    output_file = 'yangdoc.html'
    current_module = None
    debug = False
    exclusions = []

    i = 0
    while i < len(arguments):
        arg = arguments[i]
        if arg in ['-h', '--help']:
            usage()
            return
        if arg in ['-v', '--version']:
            print(f"Version {get_version()}")
            return
        if arg in ['-d', '--debug']:
            debug = True
        elif arg in ['-p', '--yang-dir']:
            i += 1
            if i < len(arguments):
                yang_dir = arguments[i]
        elif arg in ['-o', '--output']:
            i += 1
            if i < len(arguments):
                output_file = arguments[i]
        elif arg in ['-m', '--module']:
            i += 1
            if i < len(arguments):
                current_module = arguments[i]
                if current_module not in module_features:
                    module_features[current_module] = []
        elif arg in ['-e', '--feature']:
            i += 1
            if i < len(arguments) and current_module:
                feature = arguments[i]
                module_features[current_module].append(feature)
        elif arg in ['-x', '--exclude']:
            i += 1
            if i < len(arguments):
                exclusions.append(arguments[i])
        i += 1

    if not module_features:
        usage()
        return

    if not yang_dir:
        print("Error: -p is required")
        usage()
        return

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    ctx = libyang.Context(yang_dir)
    modules = []

    for module, features in module_features.items():
        loaded_module = load_module(ctx, module, features, yang_dir)
        if loaded_module:
            modules.append(loaded_module)

    # Sort modules alphabetically
    sorted_modules = sorted(ctx, key=lambda m: m.name())

    tree_html = generate_html_tree(sorted_modules, exclusions)
    create_html_output(tree_html, output_file)


if __name__ == '__main__':
    main()
