import os
import random

from .exceptions import *
from .phases import *
from .resources import *
from .cards import *
from . import events
from . import event_cards
from . import progress_cards
from . import nations
from .player import Player

ordinals = ('0th', '1st', '2nd', '3rd', '4th', '5th', '6th')

card_draw_limits = {
    2: {
        ProgressCardType.BUILDING: 5,
        ProgressCardType.BATTLE: 4,
        ProgressCardType.GOLDEN_AGE: 4,
        ProgressCardType.ADVISOR: 3,
        ProgressCardType.COLONY: 3,
        ProgressCardType.MILITARY: 3,
        ProgressCardType.WONDER: 3,
        ProgressCardType.NATURAL_WONDER: 3,
        ProgressCardType.WAR: 2
    },
    3: {
        ProgressCardType.BUILDING: 6,
        ProgressCardType.BATTLE: 4,
        ProgressCardType.GOLDEN_AGE: 4,
        ProgressCardType.ADVISOR: 4,
        ProgressCardType.COLONY: 4,
        ProgressCardType.MILITARY: 4,
        ProgressCardType.WONDER: 4,
        ProgressCardType.NATURAL_WONDER: 4,
        ProgressCardType.WAR: 3
    },
    4: {
        ProgressCardType.BUILDING: 7,
        ProgressCardType.BATTLE: 5,
        ProgressCardType.GOLDEN_AGE: 5,
        ProgressCardType.ADVISOR: 5,
        ProgressCardType.COLONY: 5,
        ProgressCardType.MILITARY: 5,
        ProgressCardType.WONDER: 5,
        ProgressCardType.NATURAL_WONDER: 5,
        ProgressCardType.WAR: 3
    },
    5: {
        ProgressCardType.BUILDING: 8,
        ProgressCardType.BATTLE: 6,
        ProgressCardType.GOLDEN_AGE: 6,
        ProgressCardType.ADVISOR: 6,
        ProgressCardType.COLONY: 6,
        ProgressCardType.MILITARY: 6,
        ProgressCardType.WONDER: 6,
        ProgressCardType.NATURAL_WONDER: 5,
        ProgressCardType.WAR: 4
    },
    6: {
        ProgressCardType.BUILDING: 9,
        ProgressCardType.BATTLE: 7,
        ProgressCardType.GOLDEN_AGE: 7,
        ProgressCardType.ADVISOR: 7,
        ProgressCardType.COLONY: 7,
        ProgressCardType.MILITARY: 7,
        ProgressCardType.WONDER: 6,
        ProgressCardType.NATURAL_WONDER: 6,
        ProgressCardType.WAR: 4
    }
}

card_draw_weights = {
    2: {
        ProgressCardType.BUILDING: 7,
        ProgressCardType.MILITARY: 4,
        ProgressCardType.BATTLE: 4,
        ProgressCardType.GOLDEN_AGE: 4,
        ProgressCardType.ADVISOR: 3,
        ProgressCardType.COLONY: 3,
        ProgressCardType.WONDER: 3,
        ProgressCardType.NATURAL_WONDER: 3,
        ProgressCardType.WAR: 2
    },
    3: {
        ProgressCardType.BUILDING: 9,
        ProgressCardType.MILITARY: 5,
        ProgressCardType.BATTLE: 4,
        ProgressCardType.GOLDEN_AGE: 4,
        ProgressCardType.ADVISOR: 4,
        ProgressCardType.COLONY: 4,
        ProgressCardType.WONDER: 4,
        ProgressCardType.NATURAL_WONDER: 4,
        ProgressCardType.WAR: 3
    },
    4: {
        ProgressCardType.BUILDING: 11,
        ProgressCardType.MILITARY: 6,
        ProgressCardType.BATTLE: 5,
        ProgressCardType.GOLDEN_AGE: 5,
        ProgressCardType.ADVISOR: 5,
        ProgressCardType.COLONY: 5,
        ProgressCardType.WONDER: 5,
        ProgressCardType.NATURAL_WONDER: 4,
        ProgressCardType.WAR: 3
    },
    5: {
        ProgressCardType.BUILDING: 13,
        ProgressCardType.MILITARY: 6,
        ProgressCardType.BATTLE: 6,
        ProgressCardType.GOLDEN_AGE: 6,
        ProgressCardType.ADVISOR: 6,
        ProgressCardType.COLONY: 6,
        ProgressCardType.WONDER: 6,
        ProgressCardType.NATURAL_WONDER: 5,
        ProgressCardType.WAR: 4
    },
    6: {
        ProgressCardType.BUILDING: 15,
        ProgressCardType.MILITARY: 7,
        ProgressCardType.BATTLE: 7,
        ProgressCardType.GOLDEN_AGE: 7,
        ProgressCardType.ADVISOR: 7,
        ProgressCardType.COLONY: 7,
        ProgressCardType.WONDER: 7,
        ProgressCardType.NATURAL_WONDER: 5,
        ProgressCardType.WAR: 4
    }
}

def s_if_not_1(value):
    return 's' if value != 1 else ''

class Match:
    def __init__(self, player_names=None, seed=None, replay=None, move_getter=None, logger=None, rules={}):
        match_growth_resources = 2
        player_growth_resources = {}
        if 'growth_resources' in rules:
            match_growth_resources = rules['growth_resources']
            if match_growth_resources == -1:
                player_growth_resources = rules['player_growth_resources']
        self.extra_draft_nations = 0
        if 'extra_draft_nations' in rules:
            self.extra_draft_nations = rules['extra_draft_nations']
        self.resource_remainder_tiebreaker = 'resource_remainder_tiebreaker' in rules
        self.card_draw_limits = 'card_draw_limits' in rules
        self.weighted_card_draw = 'weighted_card_draw' in rules
        self.korea_nerf = 'korea_nerf' in rules
        self.lincoln_nerf = 'lincoln_nerf' in rules
        self.move_list = []
        self.replay_lines = []
        self.log_lines = [[]]
        if replay is not None:
            prev_player_name = None
            replay_player_names = []
            in_header = True
            for line in replay.replace('\r', '').rstrip('\n').split('\n'):
                if in_header:
                    if line.startswith('seed '):
                        seed = line[len('seed '):]
                    elif line.startswith('extra_draft_nations '):
                        self.extra_draft_nations = int(line[len('extra_draft_nations '):])
                    elif line == 'resource_remainder_tiebreaker':
                        self.resource_remainder_tiebreaker = True
                    elif line == 'card_draw_limits':
                        self.card_draw_limits = True
                    elif line == 'weighted_card_draw':
                        self.weighted_card_draw = True
                    elif line == 'korea_nerf':
                        self.korea_nerf = True
                    elif line == 'lincoln_nerf':
                        self.lincoln_nerf = True
                    elif line.startswith('player '):
                        player_name = line[len('player '):]
                        replay_player_names.append(player_name)
                        prev_player_name = player_name
                    elif line.startswith('growth_resources '):
                        growth_resources = int(line[len('growth_resources '):])
                        if prev_player_name is None:
                            match_growth_resources = growth_resources
                        else:
                            player_growth_resources[prev_player_name] = growth_resources
                    elif not line:
                        in_header = False
                else:
                    self.move_list.append(line)
            if replay_player_names:
                player_names = replay_player_names
        if seed is None:
            self.seed = os.urandom(64)
        else:
            if len(seed) % 2 == 1:
                self.seed = bytes().fromhex('0' + seed)
            else:
                self.seed = bytes().fromhex(seed)
        self.events = {event.name: event(self) for event in events.events}
        self.players = [Player(self, name) for name in player_names]
        for player in self.players:
            if player.name not in player_growth_resources:
                player_growth_resources[player.name] = match_growth_resources
            player.growth_resources = player_growth_resources[player.name]
        self.initial_player_order = self.players
        self.event_cards = {}
        self.initial_event_card_order = {}
        for age in range(1, 1 + 4):
            self.event_cards[age] = [card(self) for card in event_cards.all_event_cards if card.age == age]
            self.initial_event_card_order[age] = self.event_cards[age]
        self.progress_cards = {}
        self.initial_progress_card_order = {}
        for age in range(1, 1 + 4):
            self.progress_cards[age] = [card(self) for card in progress_cards.all_progress_cards if card.age == age]
            self.initial_progress_card_order[age] = self.progress_cards[age]
        self.nations = [nation(self) for nation in nations.all_nations]
        if self.korea_nerf:
            for nation in self.nations:
                if nation.name == 'Korea':
                    nation.specials[0].abbr = 'K_S_Nerf'
                    break
        if self.lincoln_nerf:
            for card in self.progress_cards[4]:
                if card.name == 'Abraham Lincoln':
                    card.abbr = 'AhLc_Nerf'
                    break
        self.initial_nation_order = self.nations
        self.move_getter = move_getter
        self.logger = logger
        self.replaying_invalid_or_undo = 0
        self.replay_lines.append(f'seed {self.seed.hex()}')
        if self.extra_draft_nations != 0:
            self.replay_lines.append(f'extra_draft_nations {self.extra_draft_nations}')
        if self.resource_remainder_tiebreaker:
            self.replay_lines.append('resource_remainder_tiebreaker')
        if self.card_draw_limits:
            self.replay_lines.append('card_draw_limits')
        if self.weighted_card_draw:
            self.replay_lines.append('weighted_card_draw')
        if self.korea_nerf:
            self.replay_lines.append('korea_nerf')
        if self.lincoln_nerf:
            self.replay_lines.append('lincoln_nerf')
        for player_name in player_names:
            self.replay_lines.append(f'player {player_name}')
            self.replay_lines.append(f'growth_resources {player_growth_resources[player_name]}')
        self.replay_lines.append('')
        self.invalid_move = None
        self.reset()

    def reset(self):
        self.random = random.Random(self.seed)
        self.players = self.initial_player_order[:]
        self.random.shuffle(self.players)
        self.first_round_player_order = self.players[:]
        self.nations = self.initial_nation_order[:]
        self.random.shuffle(self.nations)
        if self.extra_draft_nations >= 0:
            self.nations = self.nations[:len(self.players)+self.extra_draft_nations]
        if self.weighted_card_draw:
            self.card_draw_weights = {}
            self.separated_decks = {}
        for age in range(1, 1 + 4):
            self.event_cards[age] = self.initial_event_card_order[age][:]
            self.random.shuffle(self.event_cards[age])
            self.progress_cards[age] = self.initial_progress_card_order[age][:]
            self.random.shuffle(self.progress_cards[age])
            for card in self.event_cards[age]:
                card.reset()
            for card in self.progress_cards[age]:
                card.reset()
            if self.weighted_card_draw:
                self.card_draw_weights[age] = card_draw_weights[len(self.players)].copy()
                self.separated_decks[age] = {}
                for progress_card_type in ProgressCardType:
                    self.separated_decks[age][progress_card_type] = [card for card in self.progress_cards[age] if card.progress_card_type == progress_card_type]
                self.progress_cards[age] = []
        for player in self.players:
            player.reset()
        for nation in self.nations:
            nation.reset()
        self.available_nations = self.nations[:]
        self.progress_board = [[None for j in range(len(self.players) + 2)] for i in range(3)]
        for (i, player) in enumerate(self.players):
            player.resources[Resource.BOOKS] = i + 1
        self.current_player = None
        self.previous_player = None
        self.game_over = False
        self.round_number = 0
        self.phase = None
        self.architects = 0
        self.turmoil = 0
        self.event = None
        self.war = None
        self.war_value = None
        self.undo_allowed = False
        self.undo_disallowed_reason = 'Beginning of the game.'
        self.next_move_player = None
        self.next_move_choice = ''
        self.next_move_options = ()

    def undo(self, invalid=False):
        self.reset()
        self.replay_lines.pop()
        self.log_lines.pop()
        if not invalid:
            self.replay_lines.pop()
            self.log_lines.pop()
        replay_moves = self.replay_lines[self.replay_lines.index('')+1:]
        self.replaying_invalid_or_undo = len(replay_moves) + 1
        self.move_list = replay_moves + self.move_list

    def next_player_forward(self, player):
        return self.players[(self.players.index(player) + 1) % len(self.players)]

    def most_least(self, player_amounts):
        max_most_min_least = 1 if len(self.players) < 5 else 2
        amounts = []
        for player in self.players:
            amounts.append(player_amounts[player.name])
        amounts.sort()
        most_threshold = max(0, amounts[-max_most_min_least])
        if amounts[-max_most_min_least-1] == most_threshold:
            most_threshold += 1
        least_threshold = max(-1, amounts[max_most_min_least-1])
        most_players = []
        least_players = []
        for player in self.players[::-1]:
            if player_amounts[player.name] >= most_threshold:
                most_players.append(player)
            if player_amounts[player.name] <= least_threshold:
                least_players.append(player)
        return (most_players, least_players)

    def most_least_of_resource(self, resource):
        player_amounts = {}
        for player in self.players:
            amount = player.resources[resource]
            if resource is Resource.STABILITY:
                amount = min(15, amount)
                if any(self.events['force least stability'].happen(player)):
                    amount = -1
            elif resource is Resource.MILITARY:
                amount = min(40, amount)
            player_amounts[player.name] = amount
        return self.most_least(player_amounts)

    def update_most_least_stability_military(self):
        for player in self.players[::-1]:
            self.events['updating most least stability military'].happen(player)
        (most_stability, least_stability) = self.most_least_of_resource(Resource.STABILITY)
        (most_military, least_military) = self.most_least_of_resource(Resource.MILITARY)
        for player in self.players:
            player.most_stability = player in most_stability
            player.least_stability = player in least_stability
            player.most_military = player in most_military
            player.least_military = player in least_military
        for player in self.players[::-1]:
            if player.least_stability:
                self.events['least stability'].happen(player)
            if player.least_military:
                self.events['least military'].happen(player)

    def most_stability(self):
        most = []
        for player in self.players[::-1]:
            if player.most_stability:
                most.append(player)
        return most

    def least_stability(self):
        least = []
        for player in self.players[::-1]:
            if player.least_stability:
                least.append(player)
        return least

    def most_military(self):
        most = []
        for player in self.players[::-1]:
            if player.most_military:
                most.append(player)
        return most

    def least_military(self):
        least = []
        for player in self.players[::-1]:
            if player.least_military:
                least.append(player)
        return least

    def most_food(self):
        (most, least) = self.most_least_of_resource(Resource.FOOD)
        return most

    def least_food(self):
        (most, least) = self.most_least_of_resource(Resource.FOOD)
        return least

    def draw_cards(self, number):
        age = (max(1, self.round_number) + 1) // 2
        if self.weighted_card_draw:
            draw_pile = []
            for progress_card_type in ProgressCardType:
                draw_pile += self.separated_decks[age][progress_card_type]
            self.random.shuffle(draw_pile)
            drawn_cards = draw_pile[:number]
            del draw_pile[:number]
            self.separated_decks[age] = {}
            for progress_card_type in ProgressCardType:
                self.separated_decks[age][progress_card_type] = [card for card in draw_pile if card.progress_card_type == progress_card_type]
        else:
            drawn_cards = self.progress_cards[age][:number]
            del self.progress_cards[age][:number]
        return drawn_cards

    def drafting_phase(self):
        player_order_string = ', '.join(str(player) for player in self.players)
        self.log(f'Initial player order: {player_order_string}')
        self.log('Drafting!')
        self.phase = Phase.DRAFTING
        available_nations_string = ', '.join(str(nation) for nation in self.available_nations)
        self.log(f'Available nations: {available_nations_string}')
        for player in self.players[::-1]:
            self.undo_allowed = False
            self.undo_disallowed_reason = 'Drafting nations.'
            if len(self.available_nations) == 1:
                nation = self.available_nations[0]
                self.log(f'{player} gets {nation}.')
                player.assign_nation(nation)
                self.available_nations.remove(nation)
            else:
                nation = self.get_move(player, 'Draft which nation?', self.available_nations)
                self.log(f'{player} drafts {nation}.')
                player.assign_nation(nation)
                self.available_nations.remove(nation)
                self.get_move(player, 'Confirm?', ('Confirm',))
        self.available_nations = []

    def progress_phase(self):
        self.phase = Phase.PROGRESS
        for player in self.players[::-1]:
            self.events['before progress'].happen(player)
        remaining_cards = [card for card in self.progress_board[2] if card is not None]
        self.progress_board = [[None for j in range(len(self.players) + 2)] for i in range(3)]
        self.progress_board[0][:len(remaining_cards)] = remaining_cards
        age = (max(1, self.round_number) + 1) // 2
        num_cards_to_draw = 3 * len(self.progress_board[0]) - len(remaining_cards)
        if self.weighted_card_draw:
            weights = self.card_draw_weights[age]
            choices = []
            for progress_card_type in ProgressCardType:
                choices += [progress_card_type] * weights[progress_card_type]
            for progress_card_type in ProgressCardType:
                if not self.separated_decks[age][progress_card_type]:
                    while progress_card_type in choices:
                        choices.remove(progress_card_type)
            drawn_cards = []
            for i in range(num_cards_to_draw):
                progress_card_type = self.random.choice(choices)
                drawn_cards.append(self.separated_decks[age][progress_card_type].pop(0))
                choices.remove(progress_card_type)
                weights[progress_card_type] -= 1
                if not self.separated_decks[age][progress_card_type]:
                    while progress_card_type in choices:
                        choices.remove(progress_card_type)
            self.random.shuffle(drawn_cards)
        elif self.card_draw_limits:
            limits = card_draw_limits[len(self.players)]
            counts = {progress_card_type: 0 for progress_card_type in progress_cards.ProgressCardType}
            for card in remaining_cards:
                counts[card.progress_card_type] += 1
            kept_cards = []
            discarded_cards = []
            for card in self.progress_cards[age]:
                progress_card_type = card.progress_card_type
                if counts[progress_card_type] < limits[progress_card_type]:
                    kept_cards.append(card)
                    counts[progress_card_type] += 1
                else:
                    discarded_cards.append(card)
                if len(kept_cards) == num_cards_to_draw:
                    break
            if discarded_cards:
                self.random.shuffle(kept_cards)
            self.progress_cards[age] = self.progress_cards[age][len(kept_cards)+len(discarded_cards):] + discarded_cards
            self.random.shuffle(self.progress_cards[age])
            drawn_cards = kept_cards
        else:
            drawn_cards = self.progress_cards[age][:num_cards_to_draw]
            del self.progress_cards[age][:num_cards_to_draw]
        row_1_cards_needed = len(self.progress_board[0]) - len(remaining_cards)
        self.progress_board[0][len(remaining_cards):] = drawn_cards[:row_1_cards_needed]
        del drawn_cards[:row_1_cards_needed]
        self.progress_board[1][:] = drawn_cards[:len(self.progress_board[1])]
        del drawn_cards[:len(self.progress_board[1])]
        self.progress_board[2][:] = drawn_cards[:len(self.progress_board[2])]

    def new_events_phase(self):
        self.phase = Phase.NEW_EVENTS
        age = (self.round_number + 1) // 2
        top_event = self.event_cards[age][0]
        next_event = self.event_cards[age][1]
        for player in self.players[::-1]:
            self.events['choose event card'].happen(player, events=(top_event, next_event))
        if self.event is None:
            self.event = top_event
            del self.event_cards[age][:1]
        else:
            del self.event_cards[age][:2]
        self.log(f'New event: {self.event}')
        self.event.reveal()
        self.architects = {1: 0, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3}[len(self.players)]
        self.architects += self.event.architects
        self.turmoil = self.architects
        for player in self.players[::-1]:
            self.events['after event reveal'].happen(player)

    def maintenance_phase(self):
        self.architects = 0
        self.turmoil = 0
        if self.event is not None:
            self.event.unregister_all_events()
        self.event = None
        self.war = None
        self.war_value = None
        age = (self.round_number + 1) // 2
        round_string = f'{age}' + ('A' if self.round_number % 2 == 1 else 'B')
        self.log(f'Beginning of Round {round_string}!')
        for player in self.players[::-1]:
            player.new_round()
        if self.round_number != 1:
            self.undo_allowed = False
            self.undo_disallowed_reason = 'Beginning of the round.'
            self.progress_phase()
            self.undo_allowed = False
            self.undo_disallowed_reason = 'Beginning of the round.'
        self.phase = Phase.GROWTH
        for player in self.players[::-1]:
            player.growth()
        self.undo_allowed = False
        self.undo_disallowed_reason = 'New events revealed.'
        self.new_events_phase()

    def action_phase(self):
        self.phase = Phase.ACTION
        for player in self.players[::-1]:
            self.events['take extra first action'].happen(player)
        current_player = self.players[0]
        while True:
            current_player.take_turn()
            next_player = current_player
            players_passed_over = []
            while True:
                next_player = self.next_player_forward(next_player)
                if not next_player.passed:
                    current_player = next_player
                    break
                if next_player is current_player:
                    break
                players_passed_over.append(next_player)
            if current_player.passed:
                break
            for player in players_passed_over:
                self.events['passed over'].happen(player)

    def production_phase(self):
        self.log('Production:')
        self.phase = Phase.PRODUCTION
        for player in self.players[::-1]:
            player.produce()
        for player in self.players:
            self.events['after production'].happen(player)

    def player_order_phase(self):
        self.phase = Phase.PLAYER_ORDER
        if any(self.events['skip player order'].happen(None)):
            self.log('No change in player order.')
            return
        current_player_order = self.players[:]
        def sort_key(player):
            military = min(40, player.resources[Resource.MILITARY])
            military += self.events['extra player order military'].happen(player)
            stability = max(-1, min(15, player.resources[Resource.STABILITY]))
            if any(self.events['force least stability'].happen(player)):
                stability = -1
            return (-military, -stability, current_player_order.index(player))
        self.players.sort(key=sort_key)
        player_names = ', '.join(str(player) for player in self.players)
        self.log(f'New player order: {player_names}')

    def war_phase(self):
        self.log('War:')
        self.phase = Phase.WAR
        if self.war is not None:
            amount = self.war.penalty_amount - self.events['extra war penalty'].happen(None)
            war_penalty = Resources({self.war.penalty_resource: amount})
            war_penalty[Resource.FOOD] -= self.events['extra war food penalty'].happen(None)
            self.log(f'[{self.war}] The war value is {self.war_value} and the penalty is {war_penalty}.')
            any_defeated = False
            for player in self.players[::-1]:
                defeated = player.war(war_penalty)
                if defeated:
                    any_defeated = True
            if not any_defeated:
                self.log('No one was defeated.')
        else:
            self.log('No war.')

    def events_phase(self):
        self.log('Events:')
        self.phase = Phase.EVENTS
        self.event.happen()

    def famine_phase(self):
        self.log('Famine:')
        self.phase = Phase.FAMINE
        self.log(f'All players lose {-self.event.famine} [Food].')
        for player in self.players[::-1]:
            player.famine()

    def discard_turmoil_phase(self):
        self.log('Discard Turmoil:')
        self.phase = Phase.DISCARD_TURMOIL
        for player in self.players[::-1]:
            player.discard_turmoil()

    def score_books(self):
        self.log('Book Scoring:')
        self.phase = Phase.SCORE_BOOKS
        book_values = []
        for player in self.players[::-1]:
            book_values.append(player.resources[Resource.BOOKS])
        for player in self.players[::-1]:
            points = sum(1 for book_value in book_values if book_value < player.resources[Resource.BOOKS])
            self.log(f'{player} scores {points} [Point{s_if_not_1(points)}] for books.')
            player.points += points

    def resolution_phase(self):
        self.production_phase()
        self.player_order_phase()
        self.war_phase()
        self.events_phase()
        self.famine_phase()
        self.discard_turmoil_phase()
        end_of_age = self.round_number % 2 == 0
        if end_of_age:
            self.score_books()
        for player in self.players[::-1]:
            self.events['end of round'].happen(player)
        self.update_most_least_stability_military()
        if end_of_age:
            for player in self.players[::-1]:
                self.events['end of age'].happen(player)
            self.update_most_least_stability_military()
        if self.round_number == 8:
            self.scoring()
            self.game_over = True
            self.undo_allowed = False
            self.undo_disallowed_reason = 'The game is over.'
            self.next_move_player = None
            self.next_move_choice = ''
            self.next_move_options = ()
            raise GameOver()

    def scoring(self):
        self.log('Game over!')
        self.phase = Phase.SCORING
        placement = self.players[:]
        player_scores = {}
        for player in self.players:
            player_scores[player.name] = player.score()
        if self.resource_remainder_tiebreaker:
            any_ties = len(list(player_scores.values())) != len(set(player_scores.values()))
            player_resource_remainders = {}
            for player in self.players:
                player_resource_remainders[player.name] = player.resource_remainder()
            def sort_key(player):
                return (-player_scores[player.name], -player_resource_remainders[player.name], self.players.index(player))
        else:
            def sort_key(player):
                return (-player_scores[player.name], self.players.index(player))
        placement.sort(key=sort_key)
        score_width = max(len(str(player_score)) for player_score in player_scores.values())
        for (i, player) in enumerate(placement):
            if self.resource_remainder_tiebreaker and any_ties:
                if list(player_scores.values()).count(player_scores[player.name]) > 1:
                    self.log(f'[{ordinals[i+1]}] {player_scores[player.name]:{-score_width}d}.{player_resource_remainders[player.name]} - {player}')
                else:
                    self.log(f'[{ordinals[i+1]}] {player_scores[player.name]:{-score_width}d}   - {player}')
            else:
                self.log(f'[{ordinals[i+1]}] {player_scores[player.name]:{-score_width}d} - {player}')

    def play_round(self):
        self.round_number += 1
        self.maintenance_phase()
        self.action_phase()
        self.resolution_phase()

    def play(self):
        while True:
            try:
                self.progress_phase()
                self.drafting_phase()
                while True:
                    self.play_round()
            except InvalidMove as e:
                self.invalid_move = str(e)
                self.log(f'Move is invalid: {self.invalid_move}')
                self.undo(invalid=True)
            except Undo:
                self.undo()
            except GameOver:
                return

    def log(self, message):
        if not self.replaying_invalid_or_undo:
            self.log_lines[-1].append(message)
            if self.logger is not None:
                self.logger(message)

    def get_move(self, player, choice, options):
        self.current_player = player
        if player is not self.previous_player:
            self.previous_player = player
            if self.undo_allowed:
                self.undo_allowed = False
                self.undo_disallowed_reason = 'Beginning of a turn.'
        while True:
            self.next_move_player = player.name if player is not None else None
            self.next_move_choice = choice
            self.next_move_options = tuple(str(option) for option in options)
            if self.replaying_invalid_or_undo > 0:
                self.replaying_invalid_or_undo -= 1
            if self.move_list:
                move = self.move_list.pop(0)
                if move == 'UNDO':
                    option = move
                else:
                    for option in options:
                        if str(option) == move:
                            break
                    else:
                        self.replay_lines.append(move)
                        self.log_lines.append([])
                        raise InvalidMove(f'Not a valid option: {move}')
            else:
                option = self.move_getter(choice, tuple(options), self.undo_allowed)
            if not self.replaying_invalid_or_undo:
                self.replay_lines.append(str(option))
                self.log_lines.append([])
                self.invalid_move = None
            if str(option) == 'UNDO':
                if self.undo_allowed:
                    raise Undo()
                else:
                    self.log(f'Undo is not allowed: {self.undo_disallowed_reason}')
                    continue
            elif option not in options:
                raise InvalidMove(f'"{option}" is not a valid move.')
            break
        self.undo_allowed = True
        self.undo_disallowed_reason = None
        player.need_confirmation = str(option) != 'Confirm'
        return option

    def undo_lines(self):
        return [i for (i, line) in enumerate(self.replay_lines) if line == 'UNDO']

    def get_replay(self, clean=True):
        remove_lines = self.undo_lines() if clean else []
        return '\n'.join(line for (i, line) in enumerate(self.replay_lines) if i not in remove_lines) + '\n'

    def get_log(self, clean=True):
        remove_lines = self.undo_lines() if clean else []
        offset = self.replay_lines.index('')
        return '\n'.join(line for (i, chunk) in enumerate(self.log_lines) if (i + offset) not in remove_lines for line in chunk) + '\n'

    def get_state(self):
        s = {}
        s['first_round_player_order'] = [player.name for player in self.first_round_player_order]
        s['player_order'] = [player.name for player in self.players]
        s['players'] = {player.name: player.state() for player in self.players}
        s['available_nations'] = [nation.name for nation in self.available_nations]
        s['nations'] = {nation.name: nation.state() for nation in self.available_nations}
        progress_board = {}
        for (row, cards_in_row) in enumerate(self.progress_board):
            for (col, card) in enumerate(cards_in_row):
                if card is not None:
                    progress_board[f'P{row + 1}{col + 1}'] = card.abbr
        s['progress_board'] = progress_board
        s['round'] = self.round_number
        s['phase'] = str(self.phase)
        s['architects'] = self.architects
        s['turmoil'] = self.turmoil
        s['event'] = self.event.abbr if self.event is not None else None
        s['war'] = self.war.abbr if self.war is not None else None
        s['war_value'] = self.war_value
        s['next_move_player'] = self.next_move_player
        s['next_move_choice'] = self.next_move_choice
        s['next_move_options'] = self.next_move_options
        s['game_over'] = int(self.game_over)
        s['undo_allowed'] = int(self.undo_allowed)
        s['invalid_move'] = self.invalid_move
        return s
