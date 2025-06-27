import enum

class ActionType(enum.Enum):
    BUY = enum.auto()
    DEPLOY = enum.auto()
    HIRE = enum.auto()
    SPECIAL = enum.auto()
    TURMOIL = enum.auto()
    EXPLORE = enum.auto()
    UNDEPLOY = enum.auto()
    PASS = enum.auto()
    CONFIRM = enum.auto()
    CONFIRM_AND_COMPLETE_TURN = enum.auto()

class Action:
    pass

class BuyAction(Action):
    action_type = ActionType.BUY

    def __init__(self, row, col, card, player=None):
        self.player = player
        self.row = row
        self.col = col
        self.card = card

    def __str__(self):
        if self.player is not None:
            return f'Buy "{self.card}"'
        return f'Buy P{self.row + 1}{self.col + 1}'

class DeployAction(Action):
    action_type = ActionType.DEPLOY

    def __init__(self, slot, card):
        self.slot = slot
        self.card = card

    def __str__(self):
        return f'Deploy to {self.slot}'

class HireAction(Action):
    action_type = ActionType.HIRE

    def __init__(self, card, private=None):
        self.card = card
        self.private = private

    def __str__(self):
        if self.private is not None:
            return f'Hire from "{self.private}"'
        return 'Hire'

class SpecialAction(Action):
    action_type = ActionType.SPECIAL

    def __init__(self, card):
        self.card = card

    def __str__(self):
        return f'Special of "{self.card}"'

class TurmoilAction(Action):
    action_type = ActionType.TURMOIL

    def __str__(self):
        return 'Turmoil'

class ExploreAction(Action):
    action_type = ActionType.EXPLORE

    def __init__(self, card):
        self.card = card

    def __str__(self):
        return 'Explore'

class UndeployAction(Action):
    action_type = ActionType.UNDEPLOY

    def __init__(self, slot, card):
        self.slot = slot
        self.card = card

    def __str__(self):
        return f'Undeploy from {self.slot}'

class PassAction(Action):
    action_type = ActionType.PASS

    def __str__(self):
        return 'Pass'

class ConfirmAction(Action):
    action_type = ActionType.CONFIRM

    def __str__(self):
        return 'Confirm'

class ConfirmCompleteAction(Action):
    action_type = ActionType.CONFIRM_AND_COMPLETE_TURN

    def __str__(self):
        return 'Confirm and complete the turn now'
