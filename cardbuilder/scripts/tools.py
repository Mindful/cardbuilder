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
    """
    Sets the specified value in Cardbuilder's configuration.

    Used like ``cardbuilder set_conf <key> <value>``
    """
    if len(sys.argv) < 3:
        print('Please pass in a key and the value you would like to set it to, like "set_conf A B"')
    else:
        key, value = sys.argv[1:3]
        if key in Config.get_conf():
            _confirm_intent('overwrite the existing value for {} (which is {})'.format(key, Config.get(key)))

        Config.set(key, value)


@command('view_conf')
def view_conf() -> None:
    """
    Prints Cardbuilder's current configuration from the database.

    Used like ``cardbuilder view_conf``
    """
    print(Config.get_conf())


@command('purge_db')
def purge_database() -> None:
    """
    Deletes Cardbuilder's local database, clearing the config and any cached content.

    Used like ``cardbuilder purge_db``
    """
    _confirm_intent('purge cardbuilder\'s entire local database')

    with InDataDir():
        os.remove(DATABASE_NAME)


@command('purge_conf')
def purge_config() -> None:
    """
    Clears Cardbuilder's local config.

    Used like ``cardbuilder purge_conf``
    """
    _confirm_intent('purge cardbuilder\'s config settings')

    Config.clear()


@command('purge_all')
def purge_all_data() -> None:
    """
    Delete's Cardbuilder's local database, along with any downloaded content. This command exists mostly for debugging
    purposes; if you do this, Cardbuilder will need to redownload data next time it runs.

    Used like ``cardbuilder purge_all``
    """
    _confirm_intent('purge cardbuilder\'s database and all downloaded data')
    with InDataDir():
        for file in glob.glob('*'):
            os.remove(file)


@command('help')
def help_cmd() -> None:
    """
    Provides a list of possible Cardbuilder commands, or information about a specific command.

    Used like ``cardbuilder help`` or ``cardbuilder help <command>``
    """
    if len(sys.argv) > 1:
        command_query = sys.argv[1]
        if command_query in commands:
            print(command_query, ':', commands[command_query].__doc__)
        else:
            print(f'Apologies, "{command_query}" doesn\'t seem to be a recognized command. '
                  f'Please run "cardbuilder help" to get a list of possible commands.')
    else:
        log(None, 'Possible cardbuilder commands:')
        for key in commands:
            print(' - {}'.format(key))