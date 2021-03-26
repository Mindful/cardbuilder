import sys
import pkgutil
from importlib import import_module

from cardbuilder import scripts
from cardbuilder.common.util import log, enable_console_reporting
from logging import ERROR


commands = {}


def command(name):
    def decorator(function):
        commands[name] = function
        return function
    return decorator


def main():
    enable_console_reporting()
    if len(sys.argv) == 1:
        cmd = 'help'
    else:
        cmd = sys.argv[1]
        del sys.argv[0]  # if we delete "cardbuilder" help messages from argparse reference the specific command

    for _, module_name, _ in pkgutil.iter_modules(scripts.__path__, 'cardbuilder.scripts.'):
        module_unqualified_name = module_name.split('.')[-1]
        if module_unqualified_name not in ['helpers', 'router']:
            import_module(module_name)

    if cmd not in commands:
        log(None, 'Unknown cardbuilder command: {}'.format(cmd), ERROR)
        exit(1)
    else:
        log(None, 'Running command {}'.format(cmd))
        commands[cmd]()

