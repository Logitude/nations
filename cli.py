from . import match
from .phases import *

def s_if_not_1(value):
    return 's' if value != 1 else ''

class NationsCLI:
    def get_move_prompt(self, choice, options, undo):
        if self.verbose:
            self.print_state()
            print(choice)
            if undo:
                print('-1) UNDO')
            for (i, option) in enumerate(options):
                print(f'{i}) {option}')
            if self.match.invalid_move is not None:
                print(f'Move was invalid: {self.match.invalid_move}')
        while True:
            if self.quit_after_replay:
                raise KeyboardInterrupt()
            option_number = input(f'{self.match.current_player}? ')
            try:
                option_number = int(option_number)
            except ValueError:
                continue
            if undo and option_number == -1:
                return 'UNDO'
            if 0 <= option_number and option_number < len(options):
                return options[option_number]

    def logger(self, message):
        print(message)

    def __init__(self, player_names, seed=None, replay=None, quit_after_replay=False, verbose=True, rules={}):
        self.verbose = verbose
        self.quit_after_replay = quit_after_replay
        logger = self.logger if verbose else None
        self.match = match.Match(player_names=player_names, seed=seed, replay=replay, move_getter=self.get_move_prompt, logger=logger, rules=rules)

    def nation_board(self, nation):
        s = f'{nation.name}:\n'
        for card in nation.dynasties:
            if card is None:
                s += 'Dynasty: None\n'
            else:
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Dynasty:{text}{production}\n'
        for card in nation.advisors:
            if card is None:
                s += 'Advisor: None\n'
            else:
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Advisor:{text}{production}\n'
        for card in nation.buildings_military:
            if card is None:
                s += 'Building or Military: None\n'
            else:
                production = f'[{card.production_per_worker}]'
                name = f'"{card.name}"'
                raid_value = f' ({card.raid_value})' if card.is_military() else ''
                cost = f'({card.deployment_cost})'
                max_workers = 'Max' if card.max_workers else ''
                worker_points = f'[{max_workers}{card.worker_points}]'
                building_military_type = 'Building' if card.is_building() else 'Military'
                s += f'{building_military_type}: {production} {name}{raid_value} {cost} {worker_points}\n'
        for card in nation.specials:
            if card is None:
                s += 'Special: None\n'
            else:
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Special:{text}{production}\n'
        for card in nation.colonies:
            if card is None:
                s += 'Colony: None\n'
            else:
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Colony:{text}{production}\n'
        for card in nation.wonders_under_construction:
            if card is None:
                s += 'Wonder Under Construction: None\n'
            else:
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Wonder Under Construction:{text}{production}\n'
        for card in nation.wonders:
            if card is None:
                s += 'Wonder: None\n'
            else:
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Wonder:{text}{production}\n'
        s += '; '.join(', '.join(f'{pool.resource_cost_per_worker}' for i in range(pool.spots)) for pool in nation.worker_pools) + '\n'
        s += f'{nation.starting_resources.all_types_str()}, {nation.starting_points} [Points], {nation.starting_workers} [Workers]\n'
        return s

    def player_board(self, player):
        s = f'{player.name}:\n'
        s += f'<{player.nation.name}>\n'
        for card in player.dynasties:
            if card is None:
                s += 'Dynasty: None\n'
            else:
                name = f'"{card.name}"'
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Dynasty: {name}{text}{production}\n'
        for card in player.advisors:
            if card is None:
                s += 'Advisor: None\n'
            else:
                name = f'"{card.name}"'
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Advisor: {name}{text}{production}\n'
        for card in player.buildings_military:
            if card is None:
                s += 'Building or Military: None\n'
            else:
                production = f'[{card.production_per_worker}]'
                name = f'"{card.name}"'
                raid_value = f' ({card.raid_value})' if card.is_military() else ''
                cost = f'({card.deployment_cost})'
                max_workers = 'Max' if card.max_workers else ''
                worker_points = f'[{max_workers}{card.worker_points}]'
                building_military_type = 'Building' if card.is_building() else 'Military'
                s += f'{building_military_type}: {production} {name}{raid_value} {cost} {worker_points}\n'
        for card in player.specials:
            if card is None:
                s += 'Special: None\n'
            else:
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Special:{text}{production}\n'
        for card in player.colonies:
            if card is None:
                s += 'Colony: None\n'
            else:
                name = f'"{card.name}"'
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Colony: {name}{text}{production}\n'
        for card in player.wonders_under_construction:
            if card is None:
                s += 'Wonder Under Construction: None\n'
            else:
                name = f'"{card.name}"'
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Wonder Under Construction: {name}{text}{production}\n'
        for card in player.wonders:
            if card is None:
                s += 'Wonder: None\n'
            else:
                name = f'"{card.name}"'
                text = f' [{card.__doc__}]' if hasattr(card, '__doc__') else ''
                production = f' [{card.production_value}]' if card.production_value else ''
                s += f'Wonder: {name}{text}{production}\n'
        worker_pool_strings = []
        for pool in player.worker_pools:
            worker_spot_strings = []
            for i in range(pool.spots - pool.ungrown_workers):
                worker_spot_strings.append(f'({pool.resource_cost_per_worker})')
            for i in range(pool.ungrown_workers):
                worker_spot_strings.append(f'({pool.resource_cost_per_worker} [Worker])')
            worker_pool_strings.append(', '.join(worker_spot_strings))
        s += '; '.join(worker_pool_strings) + '\n'
        s += f'{player.resources.all_types_str()}, {player.points} [Point{s_if_not_1(player.points)}], {player.workers} [Workers]\n'
        return s

    def main_board(self):
        round_number = max(1, self.match.round_number)
        age = (round_number + 1) // 2
        round_string = f'{age}' + ('A' if round_number % 2 == 1 else 'B')
        s = f'Round: {round_string}\n\n'
        s += 'Player Order: ' + ', '.join(player.name for player in self.match.players) + '\n\n'
        s += f'Available Architects: {self.match.architects}\n\n'
        s += f'Available Turmoil Cards: {self.match.turmoil}\n\n'
        if self.match.event is not None:
            s += 'Event:\n'
            s += f'{self.match.event.name_a}: {self.match.event.effect_a}\n'
            s += f'{self.match.event.name_b}: {self.match.event.effect_b}\n'
            s += f'additional architects: {self.match.event.architects}\n'
            s += f'famine: {self.match.event.famine}\n'
        else:
            s += 'Event: Not yet revealed\n'
        war_value = f' @ {self.match.war_value}' if self.match.war is not None else ''
        s += f'War: {self.match.war}{war_value}\n\n'
        for row in range(len(self.match.progress_board) - 1, -1, -1):
            s += f'{row + 1}-Gold Cards:\n\n'
            for (col, card) in enumerate(self.match.progress_board[row]):
                if card is None:
                    s += 'Empty\n'
                    continue
                if card.is_advisor():
                    name = f'"{card.name}"'
                    text = f' [{card.__doc__}]' if card.__doc__ else ''
                    production = f' [{card.production_value}]' if card.production_value else ''
                    s += f'Advisor: {name}{text}{production}\n'
                elif card.is_building_military():
                    production = f'[{card.production_per_worker}]'
                    name = f'"{card.name}"'
                    raid_value = f' ({card.raid_value})' if card.is_military() else ''
                    cost = f'({card.deployment_cost})'
                    max_workers = 'Max' if card.max_workers else ''
                    worker_points = f'[{max_workers}{card.worker_points}]'
                    building_military_type = 'Building' if card.is_building() else 'Military'
                    s += f'{building_military_type}: {name} {production}{raid_value} {cost} {worker_points}\n'
                elif card.is_colony():
                    name = f'"{card.name}"'
                    text = f' [{card.__doc__}]' if card.__doc__ else ''
                    requirement = f' [{card.military_requirement}]' if card.military_requirement else ''
                    production = f' [{card.production_value}]' if card.production_value else ''
                    s += f'Colony: {name}{text}{requirement}{production}\n'
                elif card.is_wonder():
                    name = f'"{card.name}"'
                    stages = ''.join(f'[{stone}]' for stone in card.stage_costs)
                    text = f' [{card.__doc__}]' if card.__doc__ else ''
                    production = f' [{card.production_value}]' if card.production_value else ''
                    s += f'Wonder: {name} {stages}{text}{production}\n'
                elif card.is_natural_wonder():
                    name = f'"{card.name}"'
                    text = f' [{card.__doc__}]' if card.__doc__ else ''
                    production = f' [{card.production_value}]' if card.production_value else ''
                    s += f'Natural Wonder: {name}{text}{production}\n'
                elif card.is_war():
                    name = f'"{card.name}"'
                    penalty = f'[{card.penalty_amount} {card.penalty_resource}]'
                    s += f'War: {name} {penalty}\n'
                elif card.is_battle():
                    name = f'"{card.name}"'
                    s += f'Battle: {name}\n'
                elif card.is_golden_age():
                    name = f'"{card.name}"'
                    effect = '+2 [Books]' if card.offers_books else '+2 [Stone]' if card.offers_stone else '<Special>'
                    s += f'Golden Age: {name} {effect}\n'
            s += '\n'
        return s

    def print_state(self):
        if not self.verbose or self.match.replaying_invalid_or_undo > 1:
            return
        print(self.main_board())
        if self.match.phase is Phase.DRAFTING:
            for player in self.match.players:
                if player.nation is not None:
                    print(self.player_board(player))
            print()
            for nation in self.match.available_nations:
                print(self.nation_board(nation))
        else:
            for player in self.match.players:
                print(self.player_board(player))
            print()
            print(self.player_board(self.match.current_player))

    def play(self):
        exception = None
        try:
            self.match.play()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            exception = e
        self.match.scoring()
        if exception is not None:
            raise exception

    def get_replay(self, clean=False):
        return self.match.get_replay(clean=clean)

    def get_log(self, clean=False):
        return self.match.get_log(clean=clean)

    def get_state(self):
        return self.match.get_state()
