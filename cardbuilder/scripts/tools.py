import glob
import os
import sys

from cardbuilder.common.config import Config
from cardbuilder.common.util import DATABASE_NAME, InDataDir, log
from cardbuilder.scripts.router import command, commands


def _confirm_intent(action: str):
    question = "This will {} - are you sure you want to do this?".format(action)
    answers = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    while True:
        sys.stdout.write(question + " [y/n] ")
        choice = input().lower()
        if choice in answers:
            if answers[choice]:
                print('Proceeding')
                return
            else:
                print('Aborting')
                exit(0)
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


@command('set_conf')
def set_conf() -> None:
    if len(sys.argv) < 3:
        print('Please pass in a key and the value you would like to set it to, like "set_conf A B"')
    else:
        key, value = sys.argv[1:3]
        if key in Config.get_conf():
            _confirm_intent('overwrite the existing value for {} (which is {})'.format(key, Config.get(key)))

        Config.set(key, value)


@command('view_conf')
def view_conf() -> None:
    print(Config.get_conf())


@command('purge_db')
def purge_database() -> None:
    _confirm_intent('purge cardbuilder\'s entire local database')

    with InDataDir():
        os.remove(DATABASE_NAME)


@command('purge_conf')
def purge_config() -> None:
    _confirm_intent('purge cardbuilder\'s config settings')

    Config.clear()


@command('purge_all')
def purge_all_data() -> None:
    _confirm_intent('purge cardbuilder\'s database and all downloaded data')
    with InDataDir():
        for file in glob.glob('*'):
            os.remove(file)


@command('help')
def help_cmd() -> None:
    log(None, 'Possible cardbuilder commands:')
    for key in commands:
        print(' - {}'.format(key))