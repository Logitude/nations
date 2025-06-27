from .resources import *
from .cards import *
from .actions import *

class DynastyCard(Card):
    card_type = CardType.DYNASTY
    production_value = Resources()

    def play(self):
        pass

class DemocraticRepublicans(DynastyCard):
    """Action: Least [Military]: Must change Dynasty immediately; For each changed: +3 [Books]"""
    name = 'Democratic Republicans'
    abbr = 'Am_DR'

    def play(self):
        self.global_effect = True

    def action_available(self, player):
        if player is not self.owner:
            return False
        least_military = self.match.least_military()
        if player in least_military:
            return False
        eligible_players = [eligible_player for eligible_player in least_military if eligible_player.dynasty_cards()]
        return eligible_players and len(eligible_players) <= self.match.turmoil

    def activate(self, player):
        eligible_players = [eligible_player for eligible_player in self.match.least_military() if eligible_player.dynasty_cards()]
        need_other_player_choice = False
        for player in eligible_players:
            if len(player.dynasty_cards()) > 1:
                need_other_player_choice = True
                break
        if need_other_player_choice:
            options = [ConfirmAction()]
            if self.owner.remaining_main_actions <= 1:
                options.append(ConfirmCompleteAction())
            choice = self.match.get_move(self.owner, 'Confirm activation before another player makes a choice?', tuple(options))
            self.owner.need_confirmation = choice.action_type is not ActionType.CONFIRM_AND_COMPLETE_TURN
        for player in eligible_players:
            self.match.turmoil -= 1
            player.turmoil += 1
            player.resources[Resource.STABILITY] -= 2
            dynasty_cards = player.dynasty_cards()
            if len(dynasty_cards) == 1:
                self.match.log(f'[{self}] {player} takes a turmoil card and must play the remaining dynasty.')
                card = dynasty_cards[0]
            else:
                self.match.log(f'[{self}] {player} takes a turmoil card and must play a dynasty.')
                card = self.match.get_move(player, 'Play which dynasty?', dynasty_cards)
            player.play_dynasty(card)
            if player.need_confirmation:
                self.match.get_move(player, 'Confirm?', ('Confirm',))
        books = 3 * len(eligible_players)
        self.match.log(f'[{self}] {self.owner} gains {books} [Books].')
        self.owner.resources[Resource.BOOKS] += books

class FederalistParty(DynastyCard):
    """Buy Building: +2 [Stone]"""
    name = 'Federalist Party'
    abbr = 'Am_FP'

    def play(self):
        self.register_for_event('buying card', self.buying_building, self.gain_stone)

    def buying_building(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_building()

    def gain_stone(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Stone].')
        player.resources[Resource.STONE] += 2

class AbbasidCaliphate(DynastyCard):
    """Other player buys Golden Age: You may buy [Point]"""
    name = 'Abbasid Caliphate'
    abbr = 'Ar_AC'

    def play(self):
        self.register_for_event('after bought card', self.other_bought_golden_age, self.may_buy_point)
        self.global_effect = True

    def other_bought_golden_age(self, player, **kwargs):
        card = kwargs['card']
        price = card.age - self.owner.golden_age_bonus()
        return player is not self.owner and card.is_golden_age() and self.owner.resources.production().total() >= price

    def may_buy_point(self, player, **kwargs):
        card = kwargs['card']
        self.match.log(f'[{self}] {self.owner} may buy the [Point] from "{card}".')
        options = [ConfirmAction()]
        if player.remaining_main_actions <= 1:
            options.append(ConfirmCompleteAction())
        choice = self.match.get_move(player, f'Confirm buying golden age before "{self}" takes effect?', tuple(options))
        player.need_confirmation = choice.action_type is not ActionType.CONFIRM_AND_COMPLETE_TURN
        answer = self.match.get_move(self.owner, f'Buy a [Point] from "{card}"?', ('Yes', 'No'))
        if answer == 'Yes':
            self.owner.pay_for_golden_age_point(card)
        self.match.get_move(self.owner, 'Confirm?', ('Confirm',))

class UmayyadCaliphate(DynastyCard):
    """Buy Colony: Requires -4 [Military]"""
    name = 'Umayyad Caliphate'
    abbr = 'Ar_UC'

    def play(self):
        self.register_for_event('colony discount', self.owned, self.colony_discount)

    def colony_discount(self, player, **kwargs):
        self.match.log(f'[{self}] {player} requires 4 [Military] less to buy colonies.')
        return 4

class MingDynasty(DynastyCard):
    """Take [Worker]: +4 [Food]"""
    name = 'Ming Dynasty'
    abbr = 'C_MD'

    def play(self):
        self.register_for_event('take worker', self.owned, self.gain_food)

    def gain_food(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 4 [Food].')
        player.resources[Resource.FOOD] += 4

class QinDynasty(DynastyCard):
    """Action, max 3 per round: Return 1 [Worker], hire 1 private [Architect] for free"""
    name = 'Qin Dynasty'
    abbr = 'C_QD'

    def action_available(self, player):
        return player is self.owner and self.markers < 3 and player.grown_workers and player.incomplete_wonder_stages()

    def activate(self, player):
        self.markers += 1
        player.return_worker(no_confirmation=True)
        card = player.wonders_under_construction[0]
        self.match.log(f'[{self}] {player} hires a free architect for "{card}".')
        player.hire_free_architect(card)

class OldKingdom(DynastyCard):
    """Action: Remove Advisor and place 1 [Marker] on this card; Production: +2 [Books] per [Marker]; Defeated: remove 1 [Marker]"""
    name = 'Old Kingdom'
    abbr = 'Eg_OK'

    def new_round(self):
        pass

    def play(self):
        self.register_for_event('defeated', self.owned, self.remove_marker)

    def remove_marker(self, player, **kwargs):
        if self.markers:
            self.match.log(f'[{self}] {player} removes 1 [Marker].')
            self.markers -= 1
        else:
            self.match.log(f'[{self}] no [Markers] to remove.')

    def action_available(self, player):
        return player is self.owner and player.removable_advisor_cards()

    def activate(self, player):
        cards = player.removable_advisor_cards()
        for card in cards[:]:
            if card.covered_by is not None:
                cards.remove(card)
        if len(cards) == 1:
            card = cards[0]
        else:
            card = self.match.get_move(player, 'Remove which advisor?', cards)
        self.match.log(f'[{self}] {player} removes "{card}".')
        player.remove(card)
        self.markers += 1

    def produce(self, projected=False):
        production = self.production_value.production()
        books = 2 * self.markers
        if not projected:
            self.match.log(f'[{self}] {self.owner} produces an extra {books} [Books].')
        production[Resource.BOOKS] += books
        return production

class NewKingdom(DynastyCard):
    """Battles cost 2 [Gold] less (min 0)"""
    name = 'New Kingdom'
    abbr = 'Eg_NK'

    def play(self):
        self.register_for_event('card discount', self.buying_battle, self.card_discount)

    def buying_battle(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_battle()

    def card_discount(self, player, **kwargs):
        self.match.log(f'[{self}] {player} pays up to 2 [Gold] less for battles.')
        return 2

class AxumiteKingdom(DynastyCard):
    """After revealing Events: Place 1 [Marker] on a card on Progress board; If Others buy this card: They must pay you 3 [Gold]"""
    name = 'Axumite Kingdom'
    abbr = 'Et_AK'

    def reset(self):
        super().reset()
        self.marked_cards = []

    def play(self):
        self.register_for_event('after event reveal', self.owned, self.mark_card)
        self.register_for_event('extra payment', self.other_buying_marked, self.extra_payment)
        self.register_for_event('make extra payment', self.true, self.pay_owner)
        self.register_for_event('buying card', self.is_marked_card, self.unmark_card)
        self.register_for_event('keep dynasty effects', self.owned, self.got_replaced)

    def mark_card(self, player, **kwargs):
        possible_marks = {}
        for (row, cards_in_row) in enumerate(self.match.progress_board):
            for (col, card) in enumerate(cards_in_row):
                if card is not None and card not in self.marked_cards:
                    possible_marks[f'P{row + 1}{col + 1}'] = card
        choice = self.match.get_move(player, 'Mark which progress card?', tuple(possible_marks.keys()))
        card = possible_marks[choice]
        self.marked_cards.append(card)
        self.match.log(f'[{self}] {player} marks "{card}".')
        self.match.get_move(player, 'Confirm?', ('Confirm',))

    def other_buying_marked(self, player, **kwargs):
        return player is not self.owner and kwargs['card'] in self.marked_cards

    def extra_payment(self, player, **kwargs):
        return 3

    def pay_owner(self, player, **kwargs):
        card = kwargs['card']
        self.match.log(f'[{self}] {player} pays {self.owner} 3 [Gold] for buying "{card}".')
        player.resources[Resource.GOLD] -= 3
        self.owner.resources[Resource.GOLD] += 3

    def is_marked_card(self, player, **kwargs):
        return kwargs['card'] in self.marked_cards

    def unmark_card(self, player, **kwargs):
        self.marked_cards.remove(kwargs['card'])

    def got_replaced(self, player, **kwargs):
        self.unregister_for_event('after event reveal')
        return True

    def state(self):
        s = super().state()
        if self.marked_cards:
            s['marked'] = [card.abbr for card in self.marked_cards]
        return s

class Sheba(DynastyCard):
    """Buy Colony: No upkeep for Military [Workers] this round"""
    name = 'Sheba'
    abbr = 'Et_Sb'

    def play(self):
        self.bought_colony = False
        self.register_for_event('buying card', self.buying_colony, self.remove_upkeep)
        self.register_for_event('no military upkeep', self.if_bought_colony, self.true)
        self.register_for_event('end of round', self.if_bought_colony, self.restore_upkeep)
        self.register_for_event('when removed', self.is_self_and_bought_colony, self.restore_upkeep)

    def buying_colony(self, player, **kwargs):
        return player is self.owner and not self.bought_colony and kwargs['card'].is_colony()

    def remove_upkeep(self, player, **kwargs):
        self.match.log(f'[{self}] {player} has no upkeep for military [Workers] this round.')
        self.bought_colony = True
        for card in self.owner.military_cards():
            self.owner.resources -= card.deployed_workers * card.production_per_worker.immediate().negative()

    def if_bought_colony(self, player, **kwargs):
        return player is self.owner and self.bought_colony

    def is_self_and_bought_colony(self, player, **kwargs):
        return player is self.owner and kwargs['card'] is self and self.bought_colony

    def restore_upkeep(self, player, **kwargs):
        for card in player.military_cards():
            player.resources += card.deployed_workers * card.production_per_worker.immediate().negative()
        self.bought_colony = False

class Athens(DynastyCard):
    """After Production: If most [Books]: +3 [Gold]"""
    name = 'Athens'
    abbr = 'G_At'

    def play(self):
        self.register_for_event('after production', self.most_books, self.gain_gold)

    def most_books(self, player, **kwargs):
        return player is self.owner and player in self.match.most_least_of_resource(Resource.BOOKS)[0]

    def gain_gold(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 3 [Gold].')
        player.resources[Resource.GOLD] += 3

class Sparta(DynastyCard):
    """Exactly 1 Military [Worker]: +4 [Military]"""
    name = 'Sparta'
    abbr = 'G_St'

    def play(self):
        self.active = False
        self.register_for_event('updating most least stability military', self.owned, self.maybe_change_military)
        self.register_for_event('when removed', self.is_self_and_active, self.remove_bonus)
        self.maybe_change_military(self.owner)

    def maybe_change_military(self, player, **kwargs):
        military_workers = 0
        for card in player.military_cards():
            military_workers += card.deployed_workers
        if not self.active and military_workers == 1:
            self.active = True
            self.match.log(f'[{self}] {player} gains 4 [Military].')
            player.resources[Resource.MILITARY] += 4
        elif self.active and military_workers != 1:
            self.active = False
            self.match.log(f'[{self}] {player} loses 4 [Military].')
            player.resources[Resource.MILITARY] -= 4

    def is_self_and_active(self, player, **kwargs):
        return player is self.owner and kwargs['card'] is self and self.active

    def remove_bonus(self, player, **kwargs):
        self.match.log(f'[{self}] {player} loses 4 [Military].')
        player.resources[Resource.MILITARY] -= 4

class MauryanEmpire(DynastyCard):
    """Growth: Take [Worker]: May take 2 [Workers] extra"""
    name = 'Mauryan Empire'
    abbr = 'I_My'

    def play(self):
        self.register_for_event('take worker', self.may_grow_two_more, self.maybe_grow_two_more)

    def may_grow_two_more(self, player, **kwargs):
        return player is self.owner and kwargs['growth'] and player.may_take_workers()

    def maybe_grow_two_more(self, player, **kwargs):
        if player.may_take_workers(2):
            answer = self.match.get_move(player, 'Take 2 [Workers] extra?', ('Yes', 'No'))
            if answer == 'Yes':
                player.take_worker()
                player.take_worker()
        else:
            answer = self.match.get_move(player, 'Take 1 [Worker] extra?', ('Yes', 'No'))
            if answer == 'Yes':
                player.take_worker()

class MughalEmpire(DynastyCard):
    """When Wonder ready: +1 [Point]"""
    name = 'Mughal Empire'
    abbr = 'I_Mg'

    def play(self):
        self.register_for_event('wonder ready', self.owned, self.gain_point)

    def gain_point(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 1 [Point].')
        player.points += 1

class EdoPeriod(DynastyCard):
    """If defeated: No effect; May not buy Colonies or Natural Wonders"""
    name = 'Edo Period'
    abbr = 'J_EP'

    def play(self):
        self.register_for_event('no defeated effect', self.owned, self.log_effect)
        self.register_for_event('may not buy card', self.buying_colony_or_natural_wonder, self.invalid_move)

    def log_effect(self, player, **kwargs):
        self.match.log(f'[{self}] {player} has no effect from being defeated.')
        return True

    def buying_colony_or_natural_wonder(self, player, **kwargs):
        card = kwargs['card']
        return player is self.owner and (card.is_colony() or card.is_natural_wonder())

    def invalid_move(self, player, **kwargs):
        card = kwargs['card']
        if card.is_colony():
            raise InvalidMove(f'[{self}] May not buy colony.')
        elif card.is_natural_wonder():
            raise InvalidMove(f'[{self}] May not buy natural wonder.')

class HeianPeriod(DynastyCard):
    """Buy Golden Age: Gain [Books]: +4 [Books]"""
    name = 'Heian Period'
    abbr = 'J_HP'

    def play(self):
        self.register_for_event('golden age choose books', self.owned, self.gain_books)

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 4 [Books].')
        player.resources[Resource.BOOKS] += 4

class JoseonKingdom(DynastyCard):
    """Action, 1 per round: Place up to 3 [Food] / [Stone] / [Gold] here; After Resolution Phase: [Food] / [Stone] / [Gold] x2 and take them back"""
    name = 'Joseon Kingdom'
    abbr = 'K_JK'

    def reset(self):
        super().reset()
        self.resources = Resources()

    def play(self):
        self.register_for_event('end of round', self.has_resources, self.gain_twice_resources)

    def has_resources(self, player, **kwargs):
        return player is self.owner and self.resources

    def gain_twice_resources(self, player, **kwargs):
        resources = 2 * self.resources
        self.match.log(f'[{self}] {player} gains {resources} back.')
        player.resources += resources
        self.resources = Resources()

    def action_available(self, player):
        return player is self.owner and not self.resources and (player.resources[Resource.FOOD] + player.resources[Resource.STONE] + player.resources[Resource.GOLD]) >= 1

    def activate(self, player):
        options = []
        for food in range(1, min(3, player.resources[Resource.FOOD]) + 1):
            options.append(Resources({Resource.FOOD: food}))
        for stone in range(1, min(3, player.resources[Resource.STONE]) + 1):
            options.append(Resources({Resource.STONE: stone}))
        for gold in range(1, min(3, player.resources[Resource.GOLD]) + 1):
            options.append(Resources({Resource.GOLD: gold}))
        choice = self.match.get_move(player, 'Place which resources?', options)
        self.match.log(f'[{self}] {player} places {choice}.')
        had_gold = player.resources[Resource.GOLD] > 0
        player.resources -= choice
        self.resources = choice
        if had_gold and player.resources[Resource.GOLD] == 0:
            self.match.events['spent last gold'].happen(player)

    def state(self):
        s = super().state()
        if self.resources:
            s['resources'] = self.resources.state()
        return s

class KoryoKingdom(DynastyCard):
    """Against War: +3 [Military] per Military [Worker]"""
    name = 'Koryo Kingdom'
    abbr = 'K_KK'

    def play(self):
        self.register_for_event('extra war military', self.owned, self.extra_war_military)

    def extra_war_military(self, player, **kwargs):
        extra = 3 * sum(card.deployed_workers for card in player.military_cards())
        self.match.log(f'[{self}] {player} has an extra {extra} [Military] against war.')
        return extra

class MaliEmpire(DynastyCard):
    """Action: Remove Advisor: -2 [Gold], +3 [Books], +1 [Point]"""
    name = 'Mali Empire'
    abbr = 'Ml_ME'

    def action_available(self, player):
        return player is self.owner and player.removable_advisor_cards() and player.resources[Resource.GOLD] >= 2

    def activate(self, player):
        cards = player.removable_advisor_cards()
        for card in cards[:]:
            if card.covered_by is not None:
                cards.remove(card)
        if len(cards) == 1:
            card = cards[0]
        else:
            card = self.match.get_move(player, 'Remove which advisor?', cards)
        self.match.log(f'[{self}] {player} pays 2 [Gold] to remove "{card}" and gain 3 [Books] and 1 [Point].')
        player.resources += Resources({Resource.GOLD: -2, Resource.BOOKS: 3})
        player.points += 1
        if player.resources[Resource.GOLD] == 0:
            self.match.events['spent last gold'].happen(player)
        player.remove(card)

class SonghaiEmpire(DynastyCard):
    """Famine: Others: Least [Military]: -3 [Food] extra"""
    name = 'Songhai Empire'
    abbr = 'Ml_SE'

    def play(self):
        self.register_for_event('extra famine', self.other_least_military, self.extra_famine)
        self.global_effect = True

    def other_least_military(self, player, **kwargs):
        return player is not self.owner and player.least_military

    def extra_famine(self, player, **kwargs):
        self.match.log(f'[{self}] {player} loses 3 [Food] extra.')
        return -3

class GoldenHorde(DynastyCard):
    """Others buy War: You get the [Gold]"""
    name = 'Golden Horde'
    abbr = 'Mg_GH'

    def play(self):
        self.register_for_event('buy card for gold', self.other_buying_war, self.gain_gold)

    def other_buying_war(self, player, **kwargs):
        return player is not self.owner and kwargs['card'].is_war()

    def gain_gold(self, player, **kwargs):
        gold = kwargs['gold']
        self.match.log(f'[{self}] {self.owner} gains {gold} [Gold].')
        self.owner.resources[Resource.GOLD] += gold

class YuanDynasty(DynastyCard):
    """When played: Take 3 [Workers]"""
    name = 'Yuan Dynasty'
    abbr = 'Mg_YD'

    def play(self):
        if self.owner.may_take_workers():
            self.owner.take_worker()
        if self.owner.may_take_workers():
            self.owner.take_worker()
        if self.owner.may_take_workers():
            self.owner.take_worker()

class AchaemenidEmpire(DynastyCard):
    """Growth: Take [Worker]: 1st action: May deploy the new [Worker] for free"""
    name = 'Achaemenid Empire'
    abbr = 'Ps_AE'

    def new_round(self):
        self.took_growth_worker = False

    def play(self):
        self.took_growth_worker = False
        self.register_for_event('take worker', self.taking_growth_worker, self.mark_took_growth_worker)
        self.register_for_event('deploy discount', self.took_worker_first_action, self.may_deploy_free)

    def taking_growth_worker(self, player, **kwargs):
        return player is self.owner and kwargs['growth']

    def mark_took_growth_worker(self, player, **kwargs):
        self.took_growth_worker = True

    def took_worker_first_action(self, player, **kwargs):
        return player is self.owner and self.took_growth_worker and player.action_number == 1

    def may_deploy_free(self, player, **kwargs):
        answer = self.match.get_move(player, 'Deploy for free?', ('Yes', 'No'))
        if answer == 'Yes':
            self.match.log(f'[{self}] {player} deploys for free.')
            return kwargs['cost']
        self.match.log(f'[{self}] {player} declines to deploy for free.')
        return 0

class SassanidEmpire(DynastyCard):
    """Take Turmoil card, take [Gold]: Discard the Turmoil card"""
    name = 'Sassanid Empire'
    abbr = 'Ps_SE'

    def play(self):
        self.register_for_event('defer taking turmoil', self.owned, self.true)
        self.register_for_event('discard gold turmoil', self.owned, self.log_effect)

    def log_effect(self, player, **kwargs):
        self.match.log(f'[{self}] {player} discards the turmoil card.')
        return True

class JagellonianDynasty(DynastyCard):
    """Before Progress: May pay 1 [Gold] to 1st player (2nd player if first) to take an extra Action before all other players"""
    name = 'Jagellonian Dynasty'
    abbr = 'Pl_JD'

    def play(self):
        self.paid = False
        self.register_for_event('before progress', self.has_gold, self.maybe_pay_for_extra_action)
        self.register_for_event('take extra first action', self.paid_for_extra_action, self.take_extra_action)

    def has_gold(self, player, **kwargs):
        return player is self.owner and player.resources[Resource.GOLD] >= 1

    def maybe_pay_for_extra_action(self, player, **kwargs):
        if player is self.match.players[0]:
            payee = self.match.players[1]
        else:
            payee = self.match.players[0]
        self.match.log(f'[{self}] {player} may pay 1 [Gold] to {payee} to take an extra action before all other players.')
        answer = self.match.get_move(player, f'Pay 1 [Gold] to {payee} to take an extra action before all other players?', ('Yes', 'No'))
        if answer == 'Yes':
            self.match.log(f'[{self}] {player} pays.')
            player.resources[Resource.GOLD] -= 1
            payee.resources[Resource.GOLD] += 1
            self.paid = True
            if player.resources[Resource.GOLD] == 0:
                self.match.events['spent last gold'].happen(player)
        else:
            self.match.log(f'[{self}] {player} declines.')
        self.match.get_move(player, 'Confirm?', ('Confirm',))

    def paid_for_extra_action(self, player, **kwargs):
        return player is self.owner and self.paid

    def take_extra_action(self, player, **kwargs):
        self.paid = False
        player.remaining_main_actions = 1
        while player.remaining_main_actions:
            player.take_one_action()
        while True:
            possible_actions = [ConfirmAction()]
            if not player.passed and not player.explore_actions():
                possible_actions += player.undeploy_actions()
            action = self.match.get_move(player, 'Complete the turn?', possible_actions)
            if action.action_type is ActionType.CONFIRM:
                return
            player.take_action(action)

class PolishLithuanianCommonwealth(DynastyCard):
    """Buy Advisor: May place on Wonder space; Others: Action: Pay Poland 3 [Gold] to buy an Advisor from Wonder space"""
    name = 'Polish-Lithuanian Commonwealth'
    abbr = 'Pl_PLC'

    def play(self):
        self.register_for_event('advisors on wonder spaces', self.owned, self.true)
        self.register_for_event('when removed', self.is_self, self.remove_advisors_on_wonder_spaces)
        self.register_for_event('additional buys', self.other_player, self.wonderful_advisor_buys)
        self.register_for_event('buy from player', self.is_wonderful_advisor, self.buy_wonderful_advisor)

    def is_self(self, player, **kwargs):
        return player is self.owner and kwargs['card'] is self

    def remove_advisors_on_wonder_spaces(self, player, **kwargs):
        player.remove_cards([card for card in player.wonders if card is not None and card.is_advisor()])

    def other_player(self, player, **kwargs):
        return player is not self.owner and player.resources[Resource.GOLD] >= 3

    def wonderful_advisors(self):
        cards = [card for card in self.owner.wonders if card is not None and card.is_advisor()]
        for card in cards[:]:
            if card.covered_by is not None:
                cards.remove(card)
                cards.append(card.covered_by)
        return cards

    def wonderful_advisor_buys(self, player, **kwargs):
        return [(self.owner, card) for card in self.wonderful_advisors()]

    def is_wonderful_advisor(self, player, **kwargs):
        return kwargs['card'] in self.wonderful_advisors()

    def buy_wonderful_advisor(self, player, **kwargs):
        card = kwargs['card']
        self.match.log(f'{player} pays 3 [Gold] to {self.owner} to buy "{card}".')
        player.resources[Resource.GOLD] -= 3
        self.owner.resources[Resource.GOLD] += 3
        self.owner.remove(card)
        return 3

class KingdomOfLeon(DynastyCard):
    """Buy War: Also gain the effects of having bought a Battle"""
    name = 'Kingdom of Leon'
    abbr = 'Pg_KL'

    def play(self):
        self.register_for_event('buying card', self.buying_war, self.effect_of_buying_battle)
        self.register_for_event('bought card', self.buying_war, self.effect_of_bought_battle)
        self.register_for_event('after bought card', self.buying_war, self.effect_of_after_bought_battle)

    def buying_war(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_war()

    def effect_of_buying_battle(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains effects of buying a battle.')
        player.do_battle(allow_no_raid=True)
        card = kwargs['card']
        card.progress_card_type = ProgressCardType.BATTLE
        self.match.events['buying card'].happen(player, card=card)
        card.progress_card_type = ProgressCardType.WAR

    def effect_of_bought_battle(self, player, **kwargs):
        card = kwargs['card']
        card.progress_card_type = ProgressCardType.BATTLE
        self.match.events['bought card'].happen(player, card=card)
        card.progress_card_type = ProgressCardType.WAR

    def effect_of_after_bought_battle(self, player, **kwargs):
        card = kwargs['card']
        card.progress_card_type = ProgressCardType.BATTLE
        self.match.events['after bought card'].happen(player, card=card)
        card.progress_card_type = ProgressCardType.WAR

class PortugeseEmpire(DynastyCard):
    """Buy Colony: May place on a Wonder space"""
    name = 'Portugese Empire'
    abbr = 'Pg_PE'

    def play(self):
        self.register_for_event('colonies on wonder spaces', self.has_replaceable_wonder_spaces, self.true)
        self.register_for_event('when removed', self.is_self, self.remove_colonies_on_wonder_spaces)

    def has_replaceable_wonder_spaces(self, player, **kwargs):
        return player is self.owner and player.replaceable_wonder_spaces()

    def is_self(self, player, **kwargs):
        return player is self.owner and kwargs['card'] is self

    def remove_colonies_on_wonder_spaces(self, player, **kwargs):
        player.remove_cards([card for card in player.wonders if card is not None and card.is_colony()])

class RomanEmpire(DynastyCard):
    """Production: If most [Military] and [Stability]: +1 [Point]; If only most [Stability]: +2 [Books]"""
    name = 'Roman Empire'
    abbr = 'R_RE'

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.most_military and self.owner.most_stability:
            if not projected:
                self.match.log(f'[{self}] {self.owner} gains 1 [Point].')
                self.owner.points += 1
        elif self.owner.most_stability:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 2 [Books].')
            production[Resource.BOOKS] += 2
        return production

class RomanRepublic(DynastyCard):
    """Action: Discard [Architect]: +1 [Stability] this round"""
    name = 'Roman Republic'
    abbr = 'R_RR'

    def play(self):
        self.register_for_event('end of round', self.has_markers, self.reduce_stability)

    def action_available(self, player):
        return player is self.owner and self.match.architects

    def activate(self, player):
        self.match.log(f'[{self}] {player} discards 1 [Architect] and gains 1 [Stability].')
        self.markers += 1
        self.match.architects -= 1
        player.resources[Resource.STABILITY] += 1

    def has_markers(self, player, **kwargs):
        return player is self.owner and self.markers

    def reduce_stability(self, player, **kwargs):
        self.match.log(f'[{self}] {player} loses {self.markers} [Stability].')
        player.resources[Resource.STABILITY] -= self.markers
        self.markers = 0

class DomainsOfTheSea(DynastyCard):
    """Buy Colony: Discard it: +1 [Point], +2 [Gold]"""
    name = 'Domains of the Sea'
    abbr = 'Vn_DS'

    def play(self):
        self.register_for_event('discard immediately', self.bought_colony, self.gain_point_and_gold)

    def bought_colony(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_colony()

    def gain_point_and_gold(self, player, **kwargs):
        card = kwargs['card']
        self.match.log(f'[{self}] {player} discards "{card}" and gains 1 [Point] and 2 [Gold].')
        player.points += 1
        player.resources[Resource.GOLD] += 2
        return True

class PactumWarmundi(DynastyCard):
    """Others buy Battle or Colony: +1 [Gold]"""
    name = 'Pactum Warmundi'
    abbr = 'Vn_PW'

    def play(self):
        self.register_for_event('buying card', self.other_buying_battle_colony, self.gain_gold)

    def other_buying_battle_colony(self, player, **kwargs):
        card = kwargs['card']
        return player is not self.owner and (card.is_battle() or card.is_colony())

    def gain_gold(self, player, **kwargs):
        self.match.log(f'[{self}] {self.owner} gains 1 [Gold].')
        self.owner.resources[Resource.GOLD] += 1

class Normans(DynastyCard):
    """+3 [Raid Value]"""
    name = 'Normans'
    abbr = 'Vk_Nm'

    def play(self):
        self.register_for_event('extra raid value', self.owned, self.extra_raid_value)

    def extra_raid_value(self, player, **kwargs):
        return 3

class Varangians(DynastyCard):
    """Buy Advisor: +4 [Books]"""
    name = 'Varangians'
    abbr = 'Vk_Vr'

    def play(self):
        self.register_for_event('buying card', self.buying_advisor, self.gain_books)

    def buying_advisor(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_advisor()

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 4 [Books].')
        player.resources[Resource.BOOKS] += 4
