from typing import NamedTuple, Callable, FrozenSet, Optional, Union, Tuple

import basic_io as io

# # # TYPES # # #

# Game models
class Mind(NamedTuple):
    seized_by_player: bool
    confusion: int
    impatience: int
    beliefs: FrozenSet[str]
    statements_of_confusion: Tuple[Optional[str], ...]
    statements_of_impatience: Tuple[Optional[str], ...]
    cached_strategy: Optional['Strategy']
    primary_control_system: Optional['ControlSystem']

class Location(NamedTuple):
    name: str
    perception: str
    position: str
    nature: Tuple[str, ...]
    foci: Tuple[str, ...]

class Action(NamedTuple):
    summary: str

class ConfusionDetails(NamedTuple):
    suggestions: Tuple[str, ...]
    explanation: str

class ConditionalStrategy(NamedTuple):
    condition: Callable[[Mind], bool]
    then: 'Strategy'

class StrategyFork(NamedTuple):
    check: Union[ConditionalStrategy, Tuple[ConditionalStrategy]]
    fallback: 'Strategy'

# These are instantiated as base classes rather than NamedTuples to avoid "recursive types"
# which, sadly, aren't supported by mypy yet. See https://github.com/python/mypy/issues/731
# One day maybe they'll be truly immutable!
class Strategy:
    def __init__(self, active: 'ControlSystem', onward: Union[None, 'Strategy', StrategyFork]) -> None:
        self._active = active
        self._onward = onward

    @property
    def active(self) -> 'ControlSystem':
        return self._active

    @property
    def onward(self) -> Union[None, 'Strategy', StrategyFork]:
        return self._onward

class ControlSystem:
    def __init__(self,
                 name: str,
                 is_satisfied: Callable[[Mind], bool],
                 init_action: Optional[Action],
                 confusion_details: Optional[ConfusionDetails],
                 say_on_progress: Callable[[str, Mind], str],
                 say_on_return_without_progress: Optional[Callable[[Mind], str]]) -> None:
        self.name = name
        self.is_satisfied = is_satisfied
        self.init_action = init_action
        self.confusion_details = confusion_details
        self.say_on_progress = say_on_progress
        self.say_on_return_without_progress = say_on_return_without_progress

# # # CONTROL SYSTEMS # # #

def respond_master_cast_a_spell(player_intent: str, mind: Mind) -> str:
    if mind.confusion > 0:
        response = "Ah, finally...\n" if mind.confusion > 3 else ""
        response += "I notice that I am concerned that something went wrong with the binding. I'm going to begin the tests unless you object."
        return response
    else:
        return "The binding appears to be a success. Shall we continue with the tests?"
wait_for_master_to_cast_a_spell = ControlSystem(
    name='waiting for you to demonstrate that the binding was a success by invoking _shta_',
    is_satisfied=lambda mind: "Master can cast spells" in mind.beliefs,
    init_action=None,
    confusion_details=ConfusionDetails(
        suggestions=(
            "Perhaps you should _shta_?",
            "I encourage you to _shta_ to get your bearings.",
            "If you _shta_ it might help you understand.",
        ),
        explanation="The binding must have disoriented you.",
    ),
    say_on_progress=respond_master_cast_a_spell,
    say_on_return_without_progress=None,
)

def respond_asked_about_starting_tests(player_intent: str, mind: Mind) -> str:
    if player_intent == "unknown" and mind.impatience == 0:
        return "I don't understand you. Something must've gone wrong. I'll head downstairs..."
    else:
        return "Hrm. Yes, I think we should continue with the testing..."
ask_about_starting_tests = ControlSystem(
    name="asking you whether I can start the tests",
    is_satisfied=lambda mind: ("the binding appears to have problems" in mind.beliefs or mind.impatience > 0),
    init_action=None,
    say_on_progress=respond_asked_about_starting_tests,
    say_on_return_without_progress=lambda mind: "Does this mean we should start?",
    confusion_details=None,
)

def respond_checked_for_objection_to_begin_tests(player_intent: str, mind: Mind) -> str:
    if player_intent == "unknown":
        return "Yes, I think continuing with the tests is a good idea. You're not making any sense."
    else:
        return "I'm heading downstairs to begin the tests..."
check_for_objection_to_begin_tests = ControlSystem(
    name='checking whether I can start the tests',
    is_satisfied=lambda mind: True,
    init_action=None,
    say_on_progress=respond_checked_for_objection_to_begin_tests,
    say_on_return_without_progress=None,
    confusion_details=None,
)

def respond_tests_have_started(player_intent: str, mind: Mind) -> str:
    if player_intent == "unknown":
        results = "Alright. We're here. Let's see if we can figure out why you're not making sense.\n"
        results += "Try another " if "I can be seized" in mind.beliefs else "Try "
        results += "_shak_ and we'll start the first test.\n"
    elif player_intent == "shta":
        results = "Yes, here we are, Master. Go ahead and _shak_ so we may begin the first test.\n"
    elif player_intent == "shak":
        results = "Ah, I think you released me too soon, Master. To complete the first test you'll need to _shak_ again.\n"
    else:
        raise NotImplementedError()
    results += "Once in control of me, _chai_ _reho_ the target, and then _shak_ again to finish the test."
    return results
start_the_tests = ControlSystem(
    name="starting the tests for your binding",
    is_satisfied=lambda mind: True,
    init_action=Action('go downstairs'),
    say_on_progress=respond_tests_have_started,
    say_on_return_without_progress=None,
    confusion_details=None,
)

def give_hint_for_first_test(mind: Mind) -> str:
    return "Did something go wrong? The target appears undamaged.\nYou'll need to _chai_ then _reho_ the target to complete the test."
wait_for_target_to_be_destroyed = ControlSystem(
    name='testing whether you can invoke _chai_ _reho_',
    is_satisfied=lambda mind: False,
    init_action=None,
    say_on_progress=lambda player_intent, mind: "raise NotImplementedError()",
    say_on_return_without_progress=give_hint_for_first_test,
    confusion_details=ConfusionDetails(
        suggestions=(
            "I think you should _shak_, then _chai_ _reho_.",
            "If you _shak_ down here we can make progress towards figuring out what went wrong.",
            "If you _shak_, you'll be able to harness _chai_ and then _reho_.",
        ),
        explanation="The binding went wrong somehow.",
    ),
)

# # # STRATEGIES # # #

test_master = Strategy(
    active=start_the_tests,
    onward=Strategy(
        active=wait_for_target_to_be_destroyed,
        onward=None,
    ),
)

test_binding = Strategy(
    active=wait_for_master_to_cast_a_spell,
    onward=StrategyFork(
        check=ConditionalStrategy(
            condition=lambda mind: 'the binding appears to have problems' not in mind.beliefs,
            then=Strategy(
                active=ask_about_starting_tests,
                onward=test_master,
            ),
        ),
        fallback=Strategy(
            active=check_for_objection_to_begin_tests,
            onward=test_master,
        ),
    ),
)

# # # TOMAR # # #

TOMAR = Mind(
    seized_by_player=False,
    confusion=0,
    impatience=0,
    beliefs=frozenset(),
    cached_strategy=test_binding,
    primary_control_system=wait_for_master_to_cast_a_spell,
    statements_of_confusion=(
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
    ),
    statements_of_impatience=(
        None,
        "Any time now...",
        None,
    ),
)

# # # SPELLS # # #

def spell__shta(location: Location) -> str:
    result = "+--"
    result += "\n|Perception: " + location.perception
    if False:  # TODO: position power
        result += "\n|Position: " + location.position
    result += "\n|Nature: " + (', '.join(location.nature))
    result += "\n|Foci: " + (', '.join(location.foci) if location.foci else "None")
    result += "\n+--"
    return result

def spell_shak(tomar: Mind, location: Location) -> Tuple[Mind, str]:
    tomar = tomar._replace(
        seized_by_player=not tomar.seized_by_player,
        primary_control_system=None,
        confusion=0,
        impatience=0)
    result = "+--"
    if tomar.seized_by_player:
        result += "\n|Tomar's mind yields before your power."
        result += "\n|Your aura is empty."
    else:
        result += "\n|You release Tomar's mind."
    result += "\n+--"
    return tomar, result

def spell_chai(tomar: Mind, location: Location) -> Tuple[Mind, str]:
    raise NotImplementedError()

def spell_reho(tomar: Mind, location: Location) -> Tuple[Mind, str]:
    raise NotImplementedError()

def attempt_spell(speech: str, tomar: Mind, location: Location) -> Tuple[Mind, Optional[str]]:
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

def react_to_nonsense(mind: Mind) -> Tuple[Mind, Optional[str]]:
    response = None
    try:
        response = mind.statements_of_confusion[mind.confusion]
    except IndexError:  # type: ignore
        response = mind.statements_of_confusion[-1]
    if response and mind.primary_control_system and mind.primary_control_system.confusion_details:
        response = response.format(**mind.primary_control_system.confusion_details._asdict())
    mind = mind._replace(
        confusion=mind.confusion + 1,
        beliefs=mind.beliefs | {'the binding appears to have problems'},
    )
    return mind, response

def react_to_lack_of_progress(mind: Mind) -> Tuple[Mind, Optional[str]]:
    try:
        response = mind.statements_of_impatience[mind.impatience]
    except IndexError:  # type: ignore
        response = mind.statements_of_impatience[-1]
    mind = mind._replace(
        impatience=mind.impatience + 1,
    )
    return mind, response

def build_primary_control_system(mind: Mind, location: Location) -> ControlSystem:
    if mind.cached_strategy is not None:
        return mind.cached_strategy.active
    else:
        raise NotImplementedError()

def evaluate_fork(fork: StrategyFork, mind: Mind) -> Optional[Strategy]:
    if isinstance(fork.check, ConditionalStrategy):
        if fork.check.condition(mind):
            return fork.check.then
    else:
        for option in fork.check:
            if option.condition(mind):
                return option.then
    return fork.fallback

def advance_strategy(mind: Mind) -> Tuple[Mind, Optional[Action]]:
    if mind.cached_strategy:
        if isinstance(mind.cached_strategy.onward, StrategyFork):
            next_strategy = evaluate_fork(mind.cached_strategy.onward, mind)
        else:
            next_strategy = mind.cached_strategy.onward
        mind = mind._replace(cached_strategy=next_strategy)
    else:
        raise NotImplementedError()

    action = None
    if mind.cached_strategy:
        mind = mind._replace(primary_control_system=mind.cached_strategy.active)
        if mind.primary_control_system and mind.primary_control_system.init_action:
            action = mind.primary_control_system.init_action

    return mind, action

def entity_turn(original_mind: Mind, location: Location, speech: str) -> Tuple[Mind, Optional[str], Optional[Action]]:
    mind = original_mind
    response = None
    action = None

    if mind.seized_by_player:
        return mind, response, action

    player_intent = "unknown"
    if speech == "shta":
        player_intent = "shta"
        mind = mind._replace(beliefs=mind.beliefs | {"Master can cast spells"})
    elif speech == "shak":
        player_intent = "shak"
        mind = mind._replace(beliefs=mind.beliefs | {"Master can cast spells"})
    elif speech in ["chai", "reho"]:
        player_intent = "battle_magic"

    if mind.primary_control_system is None:
        mind = mind._replace(beliefs=mind.beliefs | {"I can be seized"})
        response = "Thank you for using me, Master.\nPlease give me a moment to collect myself.\n...\n"
        mind = mind._replace(primary_control_system=build_primary_control_system(mind, location))
        if mind.primary_control_system:  # Guaranteed. This check is just for typechecking safety.
            response += "I seem to remember something about " + mind.primary_control_system.name + '...\n'
            satisfaction = mind.primary_control_system.is_satisfied(mind)
            if satisfaction:
                response += mind.primary_control_system.say_on_progress(player_intent, mind)
                mind, action = advance_strategy(mind)
            else:
                if mind.primary_control_system and mind.primary_control_system.say_on_return_without_progress:
                    response += mind.primary_control_system.say_on_return_without_progress(mind)

    else:
        satisfaction = mind.primary_control_system.is_satisfied(mind)
        if satisfaction:
            response = mind.primary_control_system.say_on_progress(player_intent, mind)
            mind, action = advance_strategy(mind)
        else:
            if player_intent == "unknown":
                mind, response = react_to_nonsense(mind)
            else:
                mind, response = react_to_lack_of_progress(mind)

    if player_intent != "unknown":
        mind = mind._replace(confusion=0)

    if original_mind.primary_control_system != mind.primary_control_system or action is not None:
        mind = mind._replace(impatience=0)

    return mind, response, action

def play_game(get_input: io.Input, output: io.Output) -> None:
    tomar: Mind = TOMAR
    location = Location(
        name="Starting Laboratory",
        perception="I'm in Master's laboratory. Everything is as it should be.",
        position="36 degrees and 4101 meters from the _guhi_ nexus, 12 meters above the weave",
        nature=("Stone", "Artifice", "Arcana"),
        foci=(),
    )

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
            location = Location(
                name="Training Hall",
                perception="I'm in the training hall below Master's lab. The test aparatus is ready.",
                position="36 degrees and 4101 meters from the _guhi_ nexus, 9.5 meters above the weave",
                nature=("Stone", "Artifice", "Metal"),
                foci=("Target",),
            )

def show_help(get_input: io.Input, output: io.Output) -> None:
    output("Endless is a minimal, single-player version of Waving Hands.")
    output("See: http://www.gamecabinet.com/rules/WavingHands.html")

def menu(menu_name: str, options: Tuple[Tuple[str, Optional[Callable[[io.Input, io.Output], None]]], ...], get_input: io.Input, output: io.Output) -> None:
    while True:
        output("")
        output("{}:".format(menu_name))
        for i in range(len(options)):
            output("{}) {}".format(i, options[i][0]))
        command = io.get_int_input(range(len(options)), get_input, output)
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

def main(get_input: io.Input=io.get_input_from_stdin, output: io.Output=io.print_to_stdout) -> None:
    output(title)
    options = (
        ("Play Game", play_game),
        ("Help", show_help),
        ("Quit", None),
    )
    menu("Main Menu", options, get_input, output)

if __name__ == "__main__":
    main()
