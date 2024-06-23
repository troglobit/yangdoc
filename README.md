YANG Tree Viewer
================

Very limited YANG tree viewer based on libyang, similar output to that
of `pyang -f jstree`.  The default output is a standalone HTML file,
called `ytree.html`, that can be included in documentation bundles.


Usage
-----

See below [setup instructions](#setup) first.

```
~/src/ytree(main)$ python main.py -p yang -m ietf-system -e authentication -e local-users -e ntp -e ntp-udp-port -e timezone-name -m ietf-interfaces -e if-mib
INFO: Parsing ietf-system, enabling features: ['authentication', 'local-users', 'ntp', 'ntp-udp-port', 'timezone-name']
WARNING: Warning: failed to parse module: Data model "ietf-netconf-acm" not found in local searchdirs.: Loading "ietf-netconf-acm" module failed.: Parsing module "ietf-system" failed.
INFO: Parsing ietf-interfaces, enabling features: ['if-mib']
INFO: Processing module ietf-interfaces
INFO: HTML file generated: ytree.html
x-www-browser yang_tree_view.html
~/src/ytree(main)$ x-www-browser yang_tree_view.html
```


Screenshot
----------

![](screenshot.png)


Setup
-----

> The following instructions have been tested on Linux Mint but are
> mostly the same for other operating systems.

Clone the repository to your home directory:

```
~$ cd src/
~/src$ git clone https://github.com/troglobit/ytree
~/src$ cd ytree
~/src/ytree(main)$
```

Set up your virtual environment, this ensures all python packages
installed from `requirements.txt` are installed only in `.venv/`:

```
~/src/ytree(main)$ python -m venv .venv
~/src/ytree(main)$ source .venv/bin/activate
```

Install all required packages:

```
~/src/ytree(main)$ sudo apt install libyang2
~/src/ytree(main)$ pip install -r requirements.txt
```
