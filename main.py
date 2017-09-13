from copy import deepcopy as copy

def spell__shta(location):
    result = "+--"
    result += "\n|Perception: " + location['perception']
    if False:  # TODO: position power
        result += "\n|Position: " + location['position']
    result += "\n|Nature: " + (', '.join(location['nature']))
    result += "\n|Foci: " + (', '.join(location['foci']) if location['foci'] else "None")
    result += "\n+--"
    return result

def spell_shak(original_tomar, location):
    tomar = copy(original_tomar)
    tomar['seized_by_player'] = not tomar['seized_by_player']
    tomar['primary_control_system'] = None
    tomar['confusion'] = 0
    tomar['impatience'] = 0
    result = "+--"
    if tomar['seized_by_player']:
        result += "\n|Tomar's mind yields before your power."
        result += "\n|Your aura is empty."
    else:
        result += "\n|You release Tomar's mind."
    result += "\n+--"
    return tomar, result

def is_spell(player_intent):
    return player_intent in ['shta', 'shak']

def attempt_spell(speech, tomar, location):
    description = None
    if speech == "shta":
        description = spell__shta(location)
    elif speech == "shak":
        tomar, description = spell_shak(tomar, location)
    return tomar, description

def react_to_nonsense(original_mind):
    mind = copy(original_mind)
    response = None

    try:
        response = mind['statements_of_confusion'][mind['confusion']]
    except IndexError:
        response = mind['statements_of_confusion'][-1]
    response = response.format(**mind['primary_control_system']['confusion_details'])
    mind['confusion'] += 1
    mind['beliefs'].add('binding_appears_to_have_problems')

    return mind, response

def react_to_lack_of_progress(original_mind):
    mind = copy(original_mind)
    response = None

    try:
        response = mind['statements_of_impatience'][mind['impatience']]
    except IndexError:
        response = mind['statements_of_impatience'][-1]
    mind['impatience'] += 1

    return mind, response

def build_primary_control_system(mind):
    if mind['cached_strategy'] is not None:
        raise NotImplementedError()
        return
    else:
        raise NotImplementedError()

def advance_strategy(original_mind):
    mind = copy(original_mind)
    action = None

    if type(mind['cached_strategy']['next']) is list:
        for option in mind['cached_strategy']['next']:
            if 'else' in option:
                mind['cached_strategy'] = option['else']
            else:
                if option['if'](mind):
                    mind['cached_strategy'] = option['then']
                    break
    else:
        mind['cached_strategy'] = mind['cached_strategy']['next']
    mind['primary_control_system'] = mind['cached_strategy']['active']

    if 'init_action' in mind['primary_control_system'].keys():  # HACK Make this nicer.
        action = mind['primary_control_system']['init_action']

    return mind, action

def entity_turn(original_mind, location, speech):
    mind = copy(original_mind)
    response = None
    action = None

    if mind['seized_by_player']:
        return mind, response, action

    player_intent = "unknown"
    if speech == "shta":
        player_intent = "shta"
    elif speech == "shak":
        player_intent = "shak"

    if mind['primary_control_system'] is None:
        response = "Thank you for using me, Master.\nPlease give me a moment to collect myself."
        mind['primary_control_system'] = build_primary_control_system(mind)

    else:
        satisfaction = mind['primary_control_system']['is_satisfied'](player_intent, mind)
        if satisfaction:
            response = mind['primary_control_system']['say_on_progress'](player_intent, mind)
            mind, action = advance_strategy(mind)
        else:
            if player_intent == "unknown":
                mind, response = react_to_nonsense(mind)
            else:
                mind, response = react_to_lack_of_progress(mind)

    if player_intent != "unknown":
        mind['confusion'] = 0

    if original_mind['primary_control_system'] != mind['primary_control_system'] or action is not None:
        mind['impatience'] = 0

    return mind, response, action

def play_game(get_input, output):
    location = {
        'name': "Starting Laboratory",
        'perception': "I'm in Master's laboratory. Everything is as it should be.",
        'position': "36 degrees and 4101 meters from the _guhi_ nexus, 12 meters above the weave",
        'nature': ["Stone", "Artifice", "Arcana"],
        'foci': [],
    }

    def respond_master_cast_a_spell(player_intent, mind):
        if mind['confusion'] > 0:
            response = "Ah, finally...\n" if mind['confusion'] > 3 else ""
            response += "I notice that I am concerned that something went wrong with the binding. I'm going to begin the tests unless you object."
            return response
        else:
            return "The binding appears to be a success. Shall we continue with the tests?"
    wait_for_master_to_cast_a_spell = {
        'name': 'wait_for_master_to_cast_a_spell',
        'is_satisfied': lambda player_intent, mind: is_spell(player_intent),
        'confusion_details': {
            'suggestions': [
                "Perhaps you should _shta_?",
                "I encourage you to _shta_ to get your bearings.",
                "If you _shta_ it might help you understand.",
            ],
            'explanation': "The binding must have disoriented you.",
        },
        'say_on_progress': respond_master_cast_a_spell,
    }

    def respond_asked_about_starting_tests(player_intent, mind):
        if player_intent == "unknown" and mind['impatience'] == 0:
            return "I don't understand you. Something must've gone wrong. I'll head downstairs..."
        else:
            return "Hrm. Yes, I think we should continue with the testing..."
    ask_about_starting_tests = {
        'name': 'ask_about_starting_tests',
        'is_satisfied': lambda player_intent, mind: (player_intent == "unknown" or mind['confusion'] > 0 or mind['impatience'] > 0),
        'say_on_progress': respond_asked_about_starting_tests,
    }

    def respond_checked_for_objection_to_begin_tests(player_intent, mind):
        if player_intent == "unknown":
            return "Yes, I think continuing with the tests is a good idea. You're not making any sense."
        else:
            return "I'm heading downstairs to begin the tests..."
    check_for_objection_to_begin_tests = {
        'name': 'check_for_objection_to_begin_tests',
        'is_satisfied': lambda player_intent, mind: True,
        'say_on_progress': respond_checked_for_objection_to_begin_tests,
    }

    def respond_tests_have_started(player_intent, mind):
        if player_intent == "unknown":
            return "Alright. We're here. Let's see if we can figure out why you're not making sense.\nTry _shak_ and we'll start the first test."
        elif player_intent == "shta":
            return "Yes, here we are, Master. Go ahead and _shak_ so we may begin the first test."
        else:
            raise NotImplementedError()
    start_the_tests = {
        'name': 'start_the_tests',
        'is_satisfied': lambda player_intent, mind: True,
        'init_action': 'go downstairs',
        'say_on_progress': respond_tests_have_started,
    }
    wait_for_shak = {
        'name': 'wait_for_shak',
        'is_satisfied': lambda player_intent, mind: False,
        'confusion_details': {
            'suggestions': [
                "I think you should _shak_?",
                "Having you _shak_ will help both of us understand how to proceed.",
                "If you to _shak_ the tests will start.",
            ],
            'explanation': "The binding went wrong somehow.",
        },
    }

    test_master = {
        'active': start_the_tests,
        'next': {
            'active': wait_for_shak,
            'next': None,
        }
    }
    test_binding = {
        'active': wait_for_master_to_cast_a_spell,
        'next': [
            {'if': lambda mind: 'binding_appears_to_have_problems' not in mind['beliefs'],
             'then': {
                 'active': ask_about_starting_tests,
                 'next': test_master,
            }},
            {'else': {
                'active': check_for_objection_to_begin_tests,
                'next': test_master,
            }},
        ]
    }

    tomar = {
        'seized_by_player': False,
        'confusion': 0,
        'impatience': 0,
        'beliefs': set(),
        'cached_strategy': test_binding,
        'primary_control_system': wait_for_master_to_cast_a_spell,
        'statements_of_confusion': [
            "I don't understand, Master.",
            "I still don't understand what you're trying to say.\n{suggestions[0]}",
            "{explanation} {suggestions[1]}",
            "I don't understand, Master.",
            "{suggestions[2]}",
            "Please Master, I'm trying.",
            "I don't understand.",
            "Have I displeased you?",
            "I await a command that I can comprehend.",
            "Master, your thoughts are madness. Please say something in Liltish.",
            "Please!",
            "...",
            None,
            "Perhaps something is wrong.",
            "I will meditate on the problem.",
            "When you are ready to _shta_ or anything else that makes sense, I will respond.",
            "..."
        ],
        'statements_of_impatience': [
            None,
            "Any time now...",
            None,
        ],
    }

    speech = None

    output("")
    output("What say you, Master?")
    while True:
        speech = get_input()
        tomar, spell_says = attempt_spell(speech, tomar, location)
        if spell_says:
            output(spell_says)
        tomar, tomar_says, tomar_does = entity_turn(tomar, location, speech)
        if tomar_says:
            output(tomar_says)
        if tomar_does:
            location = {
                "name": "Training Hall",
                'perception': "I'm in the training hall below Master's lab. The test aparatus is ready.",
                "position": "36 degrees and 4101 meters from the _guhi_ nexus, 9.5 meters above the weave",
                "nature": ["Stone", "Artifice", "Metal"],
                'foci': [],
            }

def show_help(get_input, output):
    output("Endless is a minimal, single-player version of Waving Hands.")
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
        ("Help", show_help),
        ("Quit", None),
    ]
    menu("Main Menu", options, get_input, output)

if __name__ == "__main__":
    main()
