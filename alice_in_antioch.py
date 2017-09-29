import random
from collections import deque
from copy import deepcopy

random.seed(1)

class DoneInteracting(Exception):
    pass

class World:
    def __init__(self):
        self.main_character = None
        self.entity_lookup = {}  # Indexed by entity name
        self.entity_locations = {}  # Indexed by entity name

    def __str__(self):
        return str(["{} at {}".format(self.entity_lookup[x], self.entity_locations[x]) for x in self.entity_lookup])

    def insert_entity(self, entity, location):
        self.entity_lookup[str(entity)] = entity
        self.entity_locations[str(entity)] = location

    def step(self, entity_actions):
        next_world = deepcopy(self)
        for entity_name in entity_actions:
            action = entity_actions[entity_name]
            if action.summary != "wait":
                next_world.get_entity(entity_name).fatigue += 0.1
            if action.summary == "go north":
                try:
                    new_location = self.entity_locations[entity_name].north
                    next_world.entity_locations[entity_name] = new_location
                except AttributeError:
                    pass
        return next_world

    def location_of(self, entity_name):
        return self.entity_locations[entity_name]

    def get_entity(self, entity_name):
        return self.entity_lookup[entity_name]

class Location:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Body:
    def __init__(self, mind):
        self.mind = mind
        self.fatigue = 0

    def __repr__(self):
        return self.mind.name

    def act(self, world):
        return self.mind.act(self.sense(world))

    def sense(self, world):
        return Sensation()

class Sensation:
    def __init__(self):
        pass

class Mind:
    def __init__(self, name):
        self.name = name
        self.goals = set()
        self.possible_actions = set()
        self.internal_clock = 0
        self.policy = None
        self.recent_policies = deque(maxlen=3)
        self.world_model = World()
        self.self_model = Body(self)
        self.world_model.insert_entity(self.self_model, Location("Somewhere"))
        self.surprise_threshold = 10  # TODO WAT

    def __str__(self):
        return "{}'s mind".format(self.name)

    def generate_possible_policies(self):
        # TODO Better policies!
        policies = list(self.recent_policies)
        for act1 in self.possible_actions:
            for act2 in self.possible_actions:
                policies.append(Policy([act1, act2], self.internal_clock))
        return policies

    def imagine(self, world_model, policy, search_depth):
        reward_sum = 0
        discount_factor = 0.9
        imagined_time = self.internal_clock
        for t in range(search_depth):
            act = policy.act(world_model, imagined_time + t)
            world_model = world_model.step({str(self.self_model): act})
            reward_sum += self.satisfaction(world_model) * discount_factor
            discount_factor = discount_factor * discount_factor
        return reward_sum

    def satisfaction(self, world):
        return sum([goal.satisfaction(world) for goal in self.goals])

    def act(self, sensation):
        self.internal_clock += 1

        surprise = self.update_from(sensation)

        if self.policy and surprise > self.surprise_threshold:
            self.policy = None

        if not self.policy:
            possible_policies = self.generate_possible_policies()
            score_estimates = {policy: (0, -9999999) for policy in possible_policies}
            search_breadth = 1000
            search_depth = 10
            for i in range(search_breadth):
                policy = possible_policies[i % len(possible_policies)]
                score = self.imagine(self.world_model, policy, search_depth)
                prev_samples, prev_score = score_estimates[policy]
                new_samples = prev_samples + 1
                new_score = (prev_score * (prev_samples / new_samples)) + score / new_samples
                score_estimates[policy] = (new_samples, new_score)
            self.policy = max(possible_policies, key=lambda x: score_estimates[x])
            print("Selecting: " + str(self.policy))
            self.recent_policies.append(self.policy)

        return self.policy.act(self.world_model, self.internal_clock) if self.policy else None

    def update_from(self, sensation):
        return 0

class Policy:
    def __init__(self, sequence, start_time):
        self.sequence = sequence
        self.start_time = start_time

    def __repr__(self):
        return " then ".join([str(s) for s in self.sequence]).capitalize()

    def act(self, world, time):
        index = time - self.start_time
        index = min(max(index, 0), len(self.sequence) - 1)
        return self.sequence[index]

class Goal:
    def __init__(self, subject, relation, object):
        self.subject = subject
        self.relation = relation
        self.object = object

    def satisfaction(self, world_model):
        if self.relation == "is in":
            if world_model.location_of(self.subject).name == self.object.name:
                return 1
            else:
                return 0
        elif self.relation == "has low":
            return max(0, 1 - getattr(world_model.get_entity(self.subject), self.object))
        raise NotImplementedError()

class Action:
    def __init__(self, summary, present_tense):
        self.summary = summary
        self.present_tense = present_tense

    def __repr__(self):
        return self.summary

class Statement:
    def __init__(self, speaker, words):
        self.speaker = speaker
        self.words = words

    def __str__(self):
        return str(self.speaker) + ": " + self.words

world = World()

antioch = Location("in Antioch")
south_of_antioch = Location("in the desert, south of Antioch")
south_of_antioch.north = antioch

alice = Body(Mind("Alice"))
alice.mind.goals.add(Goal(str(alice), "is in", antioch))
alice.mind.goals.add(Goal(str(alice), "has low", "fatigue"))
alice.mind.possible_actions.add(Action("wait", "waits"))
alice.mind.possible_actions.add(Action("go north", "goes north"))
alice.mind.possible_actions.add(Action("go east", "goes east"))
alice.mind.possible_actions.add(Action("go west", "goes west"))
alice.mind.possible_actions.add(Action("go south", "goes south"))

world.insert_entity(alice, south_of_antioch)

alice.mind.world_model = deepcopy(world)  # Give Alice all the knowledge

while True:
    action = alice.act(world)
    print(alice, "({})".format(world.location_of(str(alice))), action.present_tense)
    world = world.step({str(alice): action})
    alice = world.get_entity(str(alice))
