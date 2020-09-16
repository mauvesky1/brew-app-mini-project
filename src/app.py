import os
from typing import List

from src.constants import DRINKS_FILE_PATH, PEOPLE_FILE_PATH, FAVOURITES_FILE_PATH
from src.constants import APP_NAME, VERSION
from src.core.table import print_table
from src.data_store.files import read_lines, save_lines

# Define data
# App data
drinks = []
people = []
favourite_drinks = {}


def clear_screen():
    os.system('clear')


# Input helper funcs
def get_numeric_menu_input(message: str):
    try:
        return int(input(f'{message} '))
    except ValueError:
        output("Menu items - numbers are the only input I understand")
        wait()
        return False


def validate_menu_input(index: int, data: list):
    if index < 0 or index >= len(data):
        print(f'"{index}" is not a valid option from that menu\n')
        wait()
        return False
    return data[index]


def select_from_menu(message: str, data: list):
    print_menu(message, data)
    selection = get_numeric_menu_input(f'{message} ')
    return validate_menu_input(selection, data)


def wait():
    input('\nPress any key to return to the main menu')


# Output helper funcs
def output(text: str):
    print(f'\n{text}')


def print_menu(title: str, data: list):
    items = []
    # enumerate() will produce the index/position in the list and the item in
    # the list for use within your loop. If you are not interested in knowing
    # what position you are at in the list then you wouldn't want to use
    # enumerate()
    #
    # https://www.programiz.com/python-programming/methods/built-in/enumerate
    # https://docs.python.org/3/library/functions.html#enumerate
    for i, item in enumerate(data):
        items.append(f'[{i}] {item}')
    clear_screen()
    print(f'{title}\n')
    print('\n'.join(items), '\n')


def print_favourites(favourites: dict):
    items = []
    for name, drink in favourites.items():
        items.append(f'{name}: {drink}')
    print_table('Favourites', items)


# Data persistence helper funcs
def load_favourites(people: list, drinks: list):
    for item in read_lines(FAVOURITES_FILE_PATH):
        # Unpacking the items in the list to separate variables
        # https://treyhunner.com/2018/03/tuple-unpacking-improves-python-code-readability/
        # I know items.split will return a list with two items, because of the second argument
        # it will only split once even if there are more instances of ':' in the string
        #
        # https://www.programiz.com/python-programming/methods/string/split
        # https://docs.python.org/3/library/stdtypes.html?highlight=split#str.rsplit
        name, drink = item.split(":", 1)
        if name in people and drink in drinks:
            favourite_drinks[name] = drink
        else:
            print('Unexpected data returned when loading favourites.')
            print(f'Drink is not known: {drink in drinks}')
            print(f'Name is not known: {name in people}')


def load_data():
    for person in read_lines(PEOPLE_FILE_PATH):
        people.append(person)
    for drink in read_lines(DRINKS_FILE_PATH):
        drinks.append(drink)
    load_favourites(people, drinks)


def save_favourites(favourites: dict):
    items = []
    for item in favourites.items():
        name, drink = item
        # Defining a consistent structure here so that I can parse/recognise it when loading
        items.append(f'{name}:{drink}')
    save_lines(FAVOURITES_FILE_PATH, items)


# Menu handlers
def handle_exit():
    print('Saving data...')
    save_lines(DRINKS_FILE_PATH, drinks)
    save_lines(PEOPLE_FILE_PATH, people)
    save_favourites(favourite_drinks)
    print(f'Thank you for using {APP_NAME}')
    exit()


def handle_add_person():
    name = input("What is the name of the user? ")
    if name not in people:
        people.append(name)


def handle_add_drink():
    drink = input("What is the name of the drink? ")
    if drink not in drinks:
        drinks.append(drink)


def handle_get_people():
    print_table('people', people)


def handle_get_drinks():
    print_table('drinks', drinks)


def handle_set_favourite_drink():
    person = select_from_menu('Choose a person', people)
    if not person:
        wait()
        run_menu()

    drink = select_from_menu(f'Choose a drink for {person}', drinks)
    if not drink:
        wait()
        run_menu()

    favourite_drinks[person] = drink
    print(f"\nThank you - {person}'s favourite drink is now {drink}")


def handle_view_favourites():
    print_favourites(favourite_drinks)


# Menu config
menu_config = [
    {'menu_option': 1, 'menu_text': 'Get all people', 'handler': handle_get_people},
    {'menu_option': 2, 'menu_text': 'Get all drinks', 'handler': handle_get_drinks},
    {'menu_option': 3, 'menu_text': 'Add a person', 'handler': handle_add_person},
    {'menu_option': 4, 'menu_text': 'Add a drink', 'handler': handle_add_drink},
    {'menu_option': 5, 'menu_text': 'Set a favourite drink',
        'handler': handle_set_favourite_drink},
    {'menu_option': 6, 'menu_text': 'View favourites',
        'handler': handle_view_favourites},
    {'menu_option': 7, 'menu_text': 'Exit', 'handler': handle_exit},
]


# CLI menu
def make_menu(config: List[dict]):
    new_line = "\n"
    return f'''
Welcome to {APP_NAME} v{VERSION}!
Please, select an option by entering a number:

{new_line.join([f'[{item.get("menu_option")}] {item.get("menu_text")}' for item in config])}
'''


MENU_TEXT = make_menu(menu_config)


# App
def run_menu():
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
            (item for item in menu_config if item.get('menu_option') == option), None)

        # Handle unknown args
        if option_config is None:
            output(f'"{option}"" is not an option that I recognise')
            wait()
            continue

        # Invoke handler
        option_config.get('handler')()
        wait()
        continue


def start():
    load_data()
    run_menu()


# When this file is run from terminal/cli  as a module __name__ is set to "__main__"
# eg. python -m src.app
# When the file is imported (eg. import app) __name__ is NOT set to "__main__"
#
# Great resource explaining Python modules/packages - https://alex.dzyoba.com/blog/python-import/
if __name__ == "__main__":
    start()
