import json

def get_boolean_from_prompt(prompt):
    print(prompt)
    user_choice = input("Enter Yes | No: ").capitalize()

    if user_choice == "YES":
        return "True"
    else:
        return "False"


def colorize(text, color):
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    magenta = '\033[95m'
    cyan = '\033[96m'
    white = '\033[97m'
    reset = '\033[0m'

    if color == 'red':
        return red + text + reset
    if color == 'green':
        return green + text + reset
    if color == 'yellow':
        return yellow + text + reset
    if color == 'blue':
        return blue + text + reset
    if color == 'magenta':
        return magenta + text + reset
    if color == 'cyan':
        return cyan + text + reset
    if color == 'white':
        return white + text + reset


def print_menu(list_of_options, menu_title):
    choice = -1
    print("-------------------------")
    print(f"      {menu_title}")
    print("-------------------------")
    while choice == -1:
        for index, option in enumerate(list_of_options, start=1):
            print(f"  {index}. {option}")
        print("-------------------------")
        user_choice = int(input("Your Selection: "))
        choice = user_choice
    return choice


def print_file_data(filename):
    try:
        # Open the file and read its contents
        with open(filename, 'r') as file:
            data = json.load(file)

        # Iterate over the dictionary and print key-value pairs
        for key, value in data.items():
            print(f"{key}: {value}")

    except FileNotFoundError:
        print("File not found.")
    except json.JSONDecodeError:
        print("Invalid JSON format in file.")
    except Exception as e:
        print("An error occurred:", e)


