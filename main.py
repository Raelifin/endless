from copy import deepcopy as copy

def respond_master_cast_a_spell(player_intent, mind):
    if mind['confusion'] > 0:
        response = "Ah, finally...\n" if mind['confusion'] > 3 else ""
        response += "I notice that I am concerned that something went wrong with the binding. I'm going to begin the tests unless you object."
        return response
    else:
        return "The binding appears to be a success. Shall we continue with the tests?"
wait_for_master_to_cast_a_spell = {
    'name': 'waiting for you to demonstrate that the binding was a success by invoking _shta_',
    'is_satisfied': lambda mind: "Master can cast spells" in mind['beliefs'],
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
    'name': 'asking you whether I can start the tests',
    'is_satisfied': lambda mind: ('the binding appears to have problems' in mind['beliefs'] or mind['impatience'] > 0),
    'say_on_progress': respond_asked_about_starting_tests,
    'say_on_return_without_progress': lambda mind: "Does this mean we should start?",
    'confusion_details': {},
}

def respond_checked_for_objection_to_begin_tests(player_intent, mind):
    if player_intent == "unknown":
        return "Yes, I think continuing with the tests is a good idea. You're not making any sense."
    else:
        return "I'm heading downstairs to begin the tests..."
check_for_objection_to_begin_tests = {
    'name': 'checking whether I can start the tests',
    'is_satisfied': lambda mind: True,
    'say_on_progress': respond_checked_for_objection_to_begin_tests,
}

def respond_tests_have_started(player_intent, mind):
    if player_intent == "unknown":
        results = "Alright. We're here. Let's see if we can figure out why you're not making sense.\n"
        results += "Try another " if "I can be seized" in mind['beliefs'] else "Try "
        results += "_shak_ and we'll start the first test.\n"
    elif player_intent == "shta":
        results = "Yes, here we are, Master. Go ahead and _shak_ so we may begin the first test.\n"
    elif player_intent == "shak":
        results = "Ah, I think you released me too soon, Master. To complete the first test you'll need to _shak_ again.\n"
    else:
        raise NotImplementedError()
    results += "Once in control of me, _chai_ _reho_ the target, and then _shak_ again to finish the test."
    return results
start_the_tests = {
    'name': "starting the tests for your binding",
    'is_satisfied': lambda mind: True,
    'init_action': 'go downstairs',
    'say_on_progress': respond_tests_have_started,
}

def give_hint_for_first_test(mind):
    return "Did something go wrong? The target appears undamaged.\nYou'll need to _chai_ then _reho_ the target to complete the test."
wait_for_target_to_be_destroyed = {
    'name': 'testing whether you can invoke _chai_ _reho_',
    'is_satisfied': lambda mind: False,
    'say_on_return_without_progress': give_hint_for_first_test,
    'confusion_details': {
        'suggestions': [
            "I think you should _shak_, then _chai_ _reho_.",
            "If you _shak_ down here we can make progress towards figuring out what went wrong.",
            "If you _shak_, you'll be able to harness _chai_ and then _reho_.",
        ],
        'explanation': "The binding went wrong somehow.",
    },
}

test_master = {
    'active': start_the_tests,
    'next': {
        'active': wait_for_target_to_be_destroyed,
        'next': None,
    }
}
test_binding = {
    'active': wait_for_master_to_cast_a_spell,
    'next': [
        {'if': lambda mind: 'the binding appears to have problems' not in mind['beliefs'],
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

def make_tomar():
    return {
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

def spell_chai(original_tomar, location):
    raise NotImplementedError()

def spell_reho(original_tomar, location):
    raise NotImplementedError()

def attempt_spell(speech, tomar, location):
    description = None
    if speech == "shta":
        description = spell__shta(location)
    elif speech == "shak":
        tomar, description = spell_shak(tomar, location)
    elif speech == "chai":
        tomar, description = spell_chai(tomar, location)
    elif speech == "reho":
        tomar, description = spell_reho(tomar, location)
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
    mind['beliefs'].add('the binding appears to have problems')

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

def build_primary_control_system(mind, location):
    if mind['cached_strategy'] is not None:
        return mind['cached_strategy']['active']
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
        mind['beliefs'].add("Master can cast spells")
    elif speech == "shak":
        player_intent = "shak"
        mind['beliefs'].add("Master can cast spells")
    elif speech in ["chai", "reho"]:
        player_intent = "battle_magic"

    if mind['primary_control_system'] is None:
        mind['beliefs'].add('I can be seized')
        response = "Thank you for using me, Master.\nPlease give me a moment to collect myself.\n...\n"
        mind['primary_control_system'] = build_primary_control_system(mind, location)
        response += "I seem to remember something about " + mind['primary_control_system']['name'] + '...\n'
        satisfaction = mind['primary_control_system']['is_satisfied'](mind)
        if satisfaction:
            response += mind['primary_control_system']['say_on_progress'](player_intent, mind)
            mind, action = advance_strategy(mind)
        else:
            print(mind['primary_control_system']['name'])
            response += mind['primary_control_system']['say_on_return_without_progress'](mind)

    else:
        satisfaction = mind['primary_control_system']['is_satisfied'](mind)
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
    tomar = make_tomar()

    location = {
        'name': "Starting Laboratory",
        'perception': "I'm in Master's laboratory. Everything is as it should be.",
        'position': "36 degrees and 4101 meters from the _guhi_ nexus, 12 meters above the weave",
        'nature': ["Stone", "Artifice", "Arcana"],
        'foci': [],
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
                'foci': ["Target"],
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
