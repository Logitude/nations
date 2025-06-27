import enum

from .exceptions import *
from .resources import *

class CardType(enum.Enum):
    EVENT = enum.auto()
    SPECIAL = enum.auto()
    DYNASTY = enum.auto()
    PROGRESS = enum.auto()
    EXTENSION = enum.auto()

class ProgressCardType(enum.Enum):
    BUILDING = enum.auto()
    MILITARY = enum.auto()
    COLONY = enum.auto()
    WAR = enum.auto()
    BATTLE = enum.auto()
    WONDER = enum.auto()
    ADVISOR = enum.auto()
    GOLDEN_AGE = enum.auto()
    NATURAL_WONDER = enum.auto()

    def __str__(self):
        return self.name.replace('_', ' ').lower()

class Card:
    card_type = None
    starting_card = False
    production_value = Resources()
    golden_age_bonus = 0
    private_architects = 0

    def __init__(self, match):
        self.match = match
        self.registered_events = []
        self.reset()

    def __str__(self):
        return self.name

    def true(self, player, **kwargs):
        return True

    def owned(self, player, **kwargs):
        return player is self.owner

    def action_available(self, player):
        return False

    def register_for_event(self, name, condition, event):
        self.registered_events.append(name)
        self.match.events[name].register(self, condition, event)

    def unregister_for_event(self, name):
        self.registered_events.remove(name)
        self.match.events[name].unregister(self)

    def unregister_all_events(self):
        self.global_effect = False
        for name in list(self.registered_events):
            self.unregister_for_event(name)

    def is_dynasty(self):
        return self.card_type is CardType.DYNASTY

    def is_progress(self):
        return self.card_type is CardType.PROGRESS

    def is_extension(self):
        return self.card_type is CardType.EXTENSION

    def is_building(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.BUILDING

    def is_military(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.MILITARY

    def is_colony(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.COLONY

    def is_war(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.WAR

    def is_battle(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.BATTLE

    def is_wonder(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.WONDER

    def is_advisor(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.ADVISOR

    def is_golden_age(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.GOLDEN_AGE

    def is_natural_wonder(self):
        return self.is_progress() and self.progress_card_type is ProgressCardType.NATURAL_WONDER

    def is_natural_wonder_extension(self):
        return self.is_extension() and self.progress_card_type is ProgressCardType.NATURAL_WONDER

    def is_building_military(self):
        return self.is_building() or self.is_military()

    def is_building_military_colony_advisor(self):
        return self.is_building() or self.is_military() or self.is_colony() or self.is_advisor()

    def is_war_battle(self):
        return self.is_war() or self.is_battle()

    def is_wonder_natural_wonder(self):
        return self.is_wonder() or self.is_natural_wonder()

    def is_golden_age_wonder_natural_wonder(self):
        return self.is_golden_age() or self.is_wonder() or self.is_natural_wonder()

    def is_natural_wonder_or_extension(self):
        return self.is_natural_wonder() or self.is_natural_wonder_extension()

    def reset(self):
        self.owner = None
        self.private_architects_available = 0
        self.markers = 0
        self.covered_by = None
        self.unregister_all_events()

    def assign_owner(self, player):
        self.owner = player
        self.private_architects_available = self.private_architects
        self.markers = 0
        self.covered_by = None

    def new_round(self):
        self.private_architects_available = self.private_architects
        self.markers = 0

    def placed(self):
        pass

    def produce(self, projected=False):
        return self.production_value.production()

    def bonus_points(self, projected=False):
        return 0

    def state(self):
        s = {}
        if self.private_architects_available:
            s['private'] = self.private_architects_available
        if self.markers:
            s['markers'] = self.markers
        if self.covered_by is not None:
            s['covered_by'] = self.covered_by.abbr
        if self.global_effect:
            s['global'] = 1
        return s
