import os
from typing import List

from src.constants import (
    DRINKS_FILE_PATH,
    PEOPLE_FILE_PATH,
    FAVOURITES_FILE_PATH,
    APP_NAME,
    VERSION,
    DRNIKS_MENU_USUAL_OPTION
)
from src.core.table import print_table
from src.core.main import load_data, save_data, build_round
from src.core.menu import clear_screen, select_from_menu, get_numeric_menu_input
from src.models.round import Round
from src.models.person import Person
from src.core.output import print_people_table
from src.core.input import select_person_from_menu
from src.data_store.db import FileDB
from src.menu_handlers.add_person import make_handle_add_person

# Define data
# App data
drinks = []
people = []
favourite_drinks = {}


# Input helper funcs
def wait():
    input('\nPress any key to return to the main menu')


# Menu handlers
def handle_exit(db):
    print('Saving data...')
    save_data(drinks, favourite_drinks)
    print(f'Thank you for using {APP_NAME}')
    exit()


def handle_add_person(db):
    name = input("What is the name of the user? ")
    parts = name.split(" ", maxsplit=1)
    first_name = parts[0]
    last_name = None if len(parts) != 2 else parts[1]
    people = db.load_people()
    last_id = get_last_id(people)
    people.append(Person(last_id + 1, first_name, last_name, None))
    db.save_people(people)


def handle_add_drink(db):
    drink = input("What is the name of the drink? ")
    if drink not in drinks:
        drinks.append(drink)


def handle_get_people(db):
    people = db.load_people()
    print_people_table(people)


def handle_get_drinks(db):
    print_table('drinks', drinks)


def handle_set_favourite_drink(db):
    people = db.load_people()
    person = select_person_from_menu(people, 'Choose a person')
    if not person:
        return

    index = select_from_menu(f'Choose a drink for {person.get_full_name()}', drinks)
    if index is False:
        return
    drink = drinks[index]

    favourite_drinks[person.get_full_name()] = drink
    print(f"\nThank you - {person.get_full_name()}'s favourite drink is now {drink}")


def handle_view_favourites(db):
    # Using list comprehension to loop through favourites dictionary (dict.items())
    # Using tuple unpacking to dict (key, value) pairs into separate name, drink variables
    # Creating a list where each item is the result of f'{name}: {drink}'
    print_table('Favourites', [
                f'{name}: {drink}' for name, drink in favourite_drinks.items()])


def handle_start_round(db):
    people = db.load_people()
    # Whose round is it?
    person = select_person_from_menu(people, 'Whose round is this?')
    if not person:
        print("Please choose a number from the menu")
        handle_start_round(db)

    # Create round with owner, get user input to add drinks to the round
    round = build_round(Round(person), favourite_drinks, people, drinks)

    clear_screen()
    print(f'Time for you to make some drinks {person.get_full_name()}\n')
    round.print_order()


# Menu config
# Work in progress - a make handler func should return a handler func with a captured DB
# lambdas fake a make handler func where one has not been implemented yet
menu_config = [
    {'menu_option': 1, 'menu_text': 'Get all people', 'handler': lambda x: handle_get_people},
    {'menu_option': 2, 'menu_text': 'Get all drinks', 'handler': lambda x: handle_get_drinks},
    {'menu_option': 3, 'menu_text': 'Add a person',
        'handler': make_handle_add_person},
    {'menu_option': 4, 'menu_text': 'Add a drink',
        'handler': lambda x: handle_add_drink},
    {'menu_option': 5, 'menu_text': 'Set a favourite drink',
        'handler': lambda x: handle_set_favourite_drink},
    {'menu_option': 6, 'menu_text': 'View favourites',
        'handler': lambda x: handle_view_favourites},
    {'menu_option': 7, 'menu_text': 'Start a round',
        'handler': lambda x: handle_start_round},
    {'menu_option': 8, 'menu_text': 'Exit', 'handler': lambda x: handle_exit},
]


# CLI menu
# Using list comprehension to loop through menu_config and create lines that read
# [1] Option 1
# [2] Option 2
# etc.
def make_menu(config: List[dict]):
    # Backslash "\" is not allowed in in a f-string f'{python} some string' so defining
    # a new line character in variable here to use in the f-string below
    new_line = "\n"
    return f'''
Welcome to {APP_NAME} v{VERSION}!
Please, select an option by entering a number:

{new_line.join([f'[{item.get("menu_option")}] {item.get("menu_text")}' for item in config])}
'''


MENU_TEXT = make_menu(menu_config)


# App
def run_menu(db, handlers=None):
    # Enter an infinite loop - the exit option calls exit() which will kill the program
    while True:
        clear_screen()
        print(MENU_TEXT)

        # Ask the user to choose an item from the menu - we want a number
        option = get_numeric_menu_input('Enter your selection:')
        if not option:
            wait()
            continue

        # Find item in menu_config that matches input
        #
        # (item for item in menu_config if item.get('menu_option') == option) list comprehension
        # to create a list all menu_config items that match user inputted option - there should only be one
        #
        # next(list, default_value) - get the next/first item in the list, or None if it is empty
        #
        # https: // www.programiz.com/python-programming/methods/built-in/next
        # https://docs.python.org/3/library/functions.html#next
        option_config = next(
            (item for item in handlers if item.get('id') == option), None)

        # Handle unknown args
        if option_config is None:
            print(f'\n"{option}" is not an option that I recognise')
            wait()
            continue

        # Invoke handler
        option_config.get('handler')(db)
        wait()
        continue


def start():
    db = FileDB(PEOPLE_FILE_PATH, DRINKS_FILE_PATH, FAVOURITES_FILE_PATH)
    menu_handlers = [{"id": config["menu_option"], "handler": config["handler"](db)} for config in menu_config]
    load_data(db.load_people(), drinks, favourite_drinks)
    run_menu(db, handlers=menu_handlers)


# When this file is run from terminal/cli  as a module __name__ is set to "__main__"
# eg. python -m src.app
# When the file is imported (eg. import app) __name__ is NOT set to "__main__"
#
# Great resource explaining Python modules/packages - https://alex.dzyoba.com/blog/python-import/
if __name__ == "__main__":
    start()
