import enum

class Phase(enum.Enum):
    DRAFTING = enum.auto()
    PROGRESS = enum.auto()
    GROWTH = enum.auto()
    NEW_EVENTS = enum.auto()
    ACTION = enum.auto()
    PRODUCTION = enum.auto()
    PLAYER_ORDER = enum.auto()
    WAR = enum.auto()
    EVENTS = enum.auto()
    FAMINE = enum.auto()
    DISCARD_TURMOIL = enum.auto()
    SCORE_BOOKS = enum.auto()
    SCORING = enum.auto()

    def __str__(self):
        return self.name.replace('_', ' ').title() + ' Phase'
