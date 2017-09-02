from copy import deepcopy as copy

def spell__shta(location):
    result = "+--"
    result += "\n|Position: " + location['position']
    result += "\n|Nature: " + (', '.join(location['nature']))
    result += "\n|Brightsouls: Tomar"
    result += "\n|Foci: None"
    result += "\n+--"
    return result

def attempt_spell(speech, location, output):
    if speech == "shta":
        output(spell__shta(location))

def entity_speak(tomar, output):
    if tomar['wants_master_to_cast_spell']:
        output(tomar['statements_of_confusion'][tomar['sequential_confusion']])
    elif tomar['wants_to_begin_tests'] and tomar['uncertain']:
        if tomar['sequential_confusion'] > 3:
            output("Ah, finally...")
        if tomar['any_trouble']:
            output("I notice that I am concerned that something went wrong with the binding. I'm going to begin the tests unless you object.")
        else:
            output("The binding appears to be a success. Shall we continue with the tests?")
    elif tomar['wants_to_begin_tests']:
        output("Yes, I think continuing with the tests is a good idea. You're not making any sense.")

def entity_listen(tomar, speech):
    tomar = copy(tomar)
    if speech == "shta":
        if tomar['wants_master_to_cast_spell']:
            tomar['wants_master_to_cast_spell'] = False
        elif tomar['wants_to_begin_tests']:
            tomar['uncertain'] = False
    else:
        tomar['any_trouble'] = True
        if tomar['wants_to_begin_tests'] and not tomar['wants_master_to_cast_spell']:
            tomar['uncertain'] = False
        tomar['sequential_confusion'] += 1
        if tomar['sequential_confusion'] >= len(tomar['statements_of_confusion']):
            tomar['sequential_confusion'] = len(tomar['statements_of_confusion']) - 1
    return tomar

def play_game(get_input, output):
    location = {
        'name': "Starting Laboratory",
        'position': "36 degrees and 4101 meters from the _guhi_ nexus, 12 meters above the weave",
        'nature': ["Stone", "Artifice", "Arcana"],
    }
    tomar = {
        'sequential_confusion': 0,
        'any_trouble': False,
        'wants_master_to_cast_spell': True,
        'wants_to_begin_tests': True,
        'uncertain': True,
        'statements_of_confusion': [
            "What say you, Master?",
            "I don't understand, Master.",
            "I still don't understand what you're trying to say.\nPerhaps you should _shta_?",
            "The binding must have disoriented you. I encourage you to _shta_ to get your bearings.",
            "I don't understand, Master.",
            "Master, please tell me to _shta_ so I can help you understand.",
            "Please Master, I'm trying.",
            "I don't understand.",
            "Have I displeased you?",
            "I await a command that I can comprehend.",
            "Master, your thoughts are madness. Please say something in Liltish.",
            "Please!",
            "...",
            "Perhaps something is wrong.",
            "I will meditate on the problem.",
            "When you are ready to _shta_ or anything else that makes sense, I will respond.",
            "..."
        ],
    }

    speech = None

    output("")
    entity_speak(tomar, output)
    while tomar['wants_master_to_cast_spell']:
        speech = get_input()
        attempt_spell(speech, location, output)
        tomar = entity_listen(tomar, speech)
        entity_speak(tomar, output)

    speech = get_input()
    attempt_spell(speech, location, output)
    tomar = entity_listen(tomar, speech)
    entity_speak(tomar, output)

    location = {
        "name": "Training Hall",
        "position": "36 degrees and 4101 meters from the _guhi_ nexus, 9.5 meters above the weave",
        "nature": ["Stone", "Artifice", "Metal"],
    }

    speech = get_input()
    attempt_spell(speech, location, output)
    tomar = entity_listen(tomar, speech)

    if speech == "shta":
        output("Yes, here we are, Master. Go ahead and _shak_ so we may begin the first test.")
    else:
        output("Alright. We're here. Let's see if we can figure out why you're not making sense.\nTry _shak_ and we'll start the first test.")

    speech = get_input()

    raise NotImplementedError()

def print_help(get_input, output):
    output("Spellbinder is a minimal, single-player version of Waving Hands.")
    output("See: http://www.gamecabinet.com/rules/WavingHands.html")

def get_input_from_stdin():
    result = ""
    while result == "":
        result = input("> ")
    return result

def print_to_stdout(text):
    print(text)

def get_int_input(range_, get_input, output):
    result = None
    while result is None:
        try:
            result = int(get_input())
        except ValueError:
            output("That is not a valid integer.")
            continue
        if result not in range_:
            output("That choice is not valid. (Valid choices are {})".format(','.join([str(x) for x in range_])))
            result = None
    return result

def menu(menu_name, options, get_input, output):
    while True:
        output("")
        output("{}:".format(menu_name))
        for i in range(len(options)):
            output("{}) {}".format(i, options[i][0]))
        command = get_int_input(range(len(options)), get_input, output)
        action = options[command][1]
        if action is None:
            return  # Exit menu
        action(get_input, output)

# http://patorjk.com/software/taag/
# Font = "Big"
title = """\
  ______           _ _
 |  ____|         | | |
 | |__   _ __   __| | | ___  ___ ___
 |  __| | '_ \ / _` | |/ _ \/ __/ __|
 | |____| | | | (_| | |  __/\__ \__ \\
 |______|_| |_|\__,_|_|\___||___/___/"""

def main(get_input=get_input_from_stdin, output=print_to_stdout):
    output(title)
    options = [
        ("Play Game", play_game),
        ("Help", print_help),
        ("Quit", None),
    ]
    menu("Main Menu", options, get_input, output)

if __name__ == "__main__":
    main()
