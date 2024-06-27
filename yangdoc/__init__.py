import os
import libyang
import logging
import importlib.metadata
import subprocess


def get_git_version():
    try:
        output = subprocess.check_output(["git", "describe", "--tags"])
        return output.strip().decode('utf-8')
    except Exception as err:
        logging.debug("Git describe failed: %s", err)
        return "0.0.0"


def get_version():
    try:
        return importlib.metadata.version("yangdoc")
    except Exception as err:
        logging.debug("Not installed, using git version: %s", err)
        return get_git_version()


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
