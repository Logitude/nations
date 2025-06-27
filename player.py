from .exceptions import *
from .resources import *
from .actions import *
from . import nations

def s_if_not_1(value):
    return 's' if value != 1 else ''

class Player:
    def __init__(self, match, name):
        self.match = match
        self.name = name
        self.reset()

    def reset(self):
        self.nation = None
        self.resources = Resources()
        self.most_stability = False
        self.least_stability = True
        self.most_military = False
        self.least_military = True
        self.resource_deficit_points = Resources()
        self.passed = False
        self.passed_first = False
        self.passed_last = False
        self.bought_colony_this_round = False
        self.need_confirmation = False

    def __str__(self):
        return self.name

    def all_slots(self):
        return self.dynasties + self.advisors + self.buildings_military + self.specials + self.colonies + self.wonders_under_construction + self.wonders + self.extra_cards

    def completed_slots(self):
        return self.advisors + self.buildings_military + self.specials + self.colonies + self.wonders

    def all_cards(self):
        cards = []
        for card in self.all_slots():
            while card is not None:
                cards.append(card)
                card = card.covered_by
        return cards

    def incomplete_wonders(self):
        cards = []
        for card in self.wonders_under_construction:
            while card is not None:
                cards.append(card)
                card = card.covered_by
        return cards

    def dynasty_cards(self):
        cards = []
        for card in self.dynasties:
            if card is not None:
                cards.append(card)
        return cards

    def completed_cards(self):
        cards = []
        for card in self.completed_slots():
            while card is not None:
                cards.append(card)
                card = card.covered_by
        return cards

    def slot_names_cards(self):
        slots_cards = []
        for (i, card) in enumerate(self.advisors):
            slots_cards.append((f'A{i + 1}', card))
        for (i, card) in enumerate(self.buildings_military):
            slots_cards.append((f'BM{i + 1}', card))
        for (i, card) in enumerate(self.specials):
            slots_cards.append((f'S{i + 1}', card))
        for (i, card) in enumerate(self.colonies):
            slots_cards.append((f'C{i + 1}', card))
        for (i, card) in enumerate(self.wonders):
            slots_cards.append((f'W{i + 1}', card))
        return slots_cards

    def filled_slot_names_cards(self):
        slot_names_cards = []
        for (slot, card) in self.slot_names_cards():
            while card is not None:
                slot_names_cards.append((slot, card))
                card = card.covered_by
        return slot_names_cards

    def slot_type_index_from_slot(self, slot):
        if slot.startswith('BM'):
            return (slot[:2], int(slot[2:]) - 1)
        else:
            return (slot[:1], int(slot[1:]) - 1)

    def slots_from_slot_type(self, slot_type):
        return {'A': self.advisors, 'BM': self.buildings_military, 'S': self.specials, 'C': self.colonies, 'W': self.wonders}[slot_type]

    def building_cards(self):
        cards = []
        for card in self.completed_cards():
            if card.is_building():
                cards.append(card)
        return cards

    def military_cards(self):
        cards = []
        for card in self.completed_cards():
            if card.is_military():
                cards.append(card)
        return cards

    def colony_cards(self):
        cards = []
        for card in self.completed_cards():
            if card.is_colony():
                cards.append(card)
        return cards

    def advisor_cards(self):
        cards = []
        for card in self.completed_cards():
            if card.is_advisor():
                cards.append(card)
        return cards

    def removable_advisor_cards(self):
        cards = []
        for card in self.completed_cards():
            if card.is_advisor() and card.age > 0:
                cards.append(card)
        return cards

    def natural_wonder_cards(self):
        cards = []
        for card in self.completed_cards():
            if card.is_natural_wonder():
                cards.append(card)
        return cards

    def building_military_cards(self):
        cards = []
        for card in self.completed_cards():
            if card.is_building_military():
                cards.append(card)
        return cards

    def wonder_natural_wonder_cards(self):
        cards = []
        for card in self.completed_cards():
            if card.is_wonder_natural_wonder():
                cards.append(card)
        return cards

    def incomplete_wonder_stages(self):
        total = 0
        for card in self.incomplete_wonders():
            total += len(card.stage_costs) - card.completed_stages
        return total

    def replaceable_wonder_spaces(self):
        return len([space for space in self.wonders if space is None or not space.is_natural_wonder_or_extension()])

    def assign_nation(self, nation):
        self.nation = nation
        self.dynasties = nation.dynasties[:]
        self.advisors = nation.advisors[:]
        self.buildings_military = nation.buildings_military[:]
        self.specials = nation.specials[:]
        self.colonies = nation.colonies[:]
        self.wonders_under_construction = nation.wonders_under_construction[:]
        self.wonders = nation.wonders[:]
        self.extra_cards = []
        for card in self.all_cards():
            card.assign_owner(self)
        self.worker_pools = []
        for worker_pool in nation.worker_pools:
            self.worker_pools.append(nations.WorkerPool(worker_pool.spots, worker_pool.resource_cost_per_worker))
        initial_books = self.resources[Resource.BOOKS]
        self.resources = Resources(nation.starting_resources)
        for card in (self.advisors + self.buildings_military + self.specials + self.colonies + self.wonders):
            if card is not None:
                self.resources += card.production_value.immediate()
        self.resources[Resource.BOOKS] = initial_books
        self.points = nation.starting_points
        self.workers = nation.starting_workers
        self.grown_workers = self.workers
        self.extra_worker_pool = 0
        self.turmoil = 0
        self.match.update_most_least_stability_military()
        self.new_round()

    def raid_value(self):
        raid_values = [0]
        for card in self.military_cards():
            if card.deployed_workers > 0:
                raid_values.append(card.raid_value)
        base_raid_value = max(raid_values)
        if base_raid_value > 0:
            return base_raid_value + self.match.events['extra raid value'].happen(self)
        return 0

    def golden_age_bonus(self):
        return sum(card.golden_age_bonus for card in self.completed_cards())

    def new_round(self):
        self.resource_deficit_points = Resources()
        self.turn_number = 0
        self.action_number = 1
        self.remaining_main_actions = 0
        self.passed = False
        self.passed_first = False
        self.passed_last = False
        self.bought_colony_this_round = False
        for card in self.completed_cards():
            card.new_round()

    def growth(self):
        growth_options = []
        if self.extra_worker_pool:
            growth_options.append('[Worker]')
        else:
            for worker_pool in self.worker_pools:
                if worker_pool.ungrown_workers:
                    growth_options.append(f'{worker_pool.resource_cost_per_worker} [Worker]')
        growth_options_with_extra_resources = {}
        for resource_type in (Resource.FOOD, Resource.STONE, Resource.GOLD):
            growth_option = Resources({resource_type: self.growth_resources})
            extra_resources = self.match.events['extra growth resources'].happen(self, growth=growth_option)
            if extra_resources:
                growth_options_with_extra_resources[resource_type] = growth_option
            growth_option[resource_type] += extra_resources
            growth_options.append(growth_option)
        growth_chosen = self.match.get_move(self, 'Take what for growth?', growth_options)
        if '[Worker]' in str(growth_chosen):
            if self.extra_worker_pool:
                self.match.log(f'{self} chooses to take a [Worker] for growth.')
                self.extra_worker_pool -= 1
                self.workers += 1
                self.grown_workers += 1
            else:
                for worker_pool in self.worker_pools:
                    if growth_chosen.startswith(str(worker_pool.resource_cost_per_worker)):
                        self.match.log(f'{self} chooses to take a {worker_pool.resource_cost_per_worker} [Worker] for growth.')
                        if worker_pool.resource_cost_per_worker.immediate():
                            self.resources += worker_pool.resource_cost_per_worker.immediate()
                            self.match.update_most_least_stability_military()
                        worker_pool.grow_worker()
                        self.workers += 1
                        self.grown_workers += 1
                        break
            self.match.events['take worker'].happen(self, growth=True)
        else:
            for (resource_type, growth_option) in growth_options_with_extra_resources.items():
                if growth_chosen[resource_type]:
                    self.match.events['received extra growth resources'].happen(self, growth=growth_option)
            self.match.log(f'{self} chooses to take {growth_chosen} for growth.')
            self.resources += growth_chosen
        self.match.get_move(self, 'Confirm?', ('Confirm',))

    def buy_actions(self):
        possible_buys = []
        for (row, cards_in_row) in enumerate(self.match.progress_board):
            for (col, card) in enumerate(cards_in_row):
                if card is not None:
                    possible_buys.append(BuyAction(row, col, card))
        for (player, card) in [additional_buy for additional_buys in self.match.events['additional buys'].happen(self) for additional_buy in additional_buys]:
            possible_buys.append(BuyAction(-1, -1, card, player=player))
        return possible_buys

    def deploy_actions(self):
        if self.workers == 0:
            return []
        possible_deploys = []
        for (slot, card) in self.filled_slot_names_cards():
            if card.is_building_military() and not (card.max_workers and card.deployed_workers == len(card.worker_points)):
                possible_deploys.append(DeployAction(slot, card))
        return possible_deploys

    def undeploy_actions(self):
        possible_undeploys = []
        for (slot, card) in self.filled_slot_names_cards():
            if card.is_building_military():
                if card.deployed_workers > 0:
                    possible_undeploys.append(UndeployAction(slot, card))
        return possible_undeploys

    def hire_actions(self):
        possible_hires = []
        if self.replaceable_wonder_spaces():
            for card in self.wonders_under_construction:
                if card is not None and card.is_wonder():
                    if self.match.architects:
                        possible_hires.append(HireAction(card))
                    for private in self.completed_cards():
                        if private.private_architects_available:
                            possible_hires.append(HireAction(card, private))
        return possible_hires

    def explore_actions(self):
        possible_explores = []
        for card in self.wonders_under_construction:
            if card is not None and card.is_natural_wonder():
                possible_explores.append(ExploreAction(card))
        return possible_explores

    def turmoil_actions(self):
        if self.match.turmoil > 0:
            return [TurmoilAction()]
        return []

    def special_actions(self):
        possible_specials = []
        for card in self.completed_cards():
            if card.action_available(self):
                possible_specials.append(SpecialAction(card))
        return possible_specials

    def place_card(self, card, update_most_least_stability_military=True):
        slots = []
        if card.is_building_military():
            for (i, old_card) in enumerate(self.buildings_military):
                if old_card is None or old_card.is_building_military():
                    slots.append(f'BM{i + 1}')
        elif card.is_colony():
            self.bought_colony_this_round = True
            if any(self.match.events['colonies on wonder spaces'].happen(self)):
                for (i, old_card) in enumerate(self.colonies):
                    if old_card is None or old_card.is_colony():
                        slots.append(f'C{i + 1}')
                for (i, old_card) in enumerate(self.wonders):
                    if old_card is None or not old_card.is_natural_wonder():
                        slots.append(f'W{i + 1}')
            else:
                for (i, old_card) in enumerate(self.colonies):
                    if old_card is None:
                        slots = [f'C{i + 1}']
                        break
                    elif old_card.is_colony():
                        slots.append(f'C{i + 1}')
        elif card.is_advisor():
            if any(self.match.events['advisors on wonder spaces'].happen(self)):
                for (i, old_card) in enumerate(self.wonders):
                    if old_card is None or not old_card.is_natural_wonder():
                        slots.append(f'W{i + 1}')
            for i in range(len(self.advisors)):
                slots.append(f'A{i + 1}')
        extra_spots = self.match.events['coverable cards'].happen(self, card=card)
        if extra_spots:
            for (slot, old_card) in self.filled_slot_names_cards():
                if old_card in extra_spots:
                    slots.append(slot)
        if len(slots) == 1:
            slot = slots[0]
        else:
            slot = self.match.get_move(self, 'Place card where?', slots)
        (slot_type, index) = self.slot_type_index_from_slot(slot)
        old_card = self.slots_from_slot_type(slot_type)[index]
        card_to_cover = None
        while old_card is not None and any(self.match.events['cover card'].happen(self, card=card, old_card=old_card)):
            card_to_cover = old_card
            old_card = card_to_cover.covered_by
        if old_card is not None:
            self.match.log(f'{self} replaces "{old_card}".')
            self.match.events['replaced card'].happen(self, old_card=old_card, new_card=card)
            self.remove(old_card)
        if card_to_cover is not None:
            card_to_cover.covered_by = card
        else:
            self.slots_from_slot_type(slot_type)[index] = card
        self.resources += card.production_value.immediate()
        card.placed()
        if update_most_least_stability_military:
            self.match.update_most_least_stability_military()

    def cover_with(self, card_to_cover, card):
        card_to_cover.covered_by = card
        self.resources += card.production_value.immediate()
        card.placed()
        self.match.update_most_least_stability_military()

    def declare_war(self, card):
        if self.match.war is not None:
            raise InvalidMove('Already at war!')
        self.match.war = card
        war_value = min(40, max(0, self.resources[Resource.MILITARY]))
        self.match.log(f'War value set to {war_value}.')
        self.match.war_value = war_value

    def do_battle(self, allow_no_raid=False):
        raid_value = self.raid_value()
        if not raid_value:
            if allow_no_raid:
                self.match.log(f'{self} does not have a raid value, so gains no resources.')
                return
            raise InvalidMove('Cannot buy a battle without a military [Worker].')
        choices = [Resources({Resource.BOOKS: raid_value}), Resources({Resource.FOOD: raid_value}), Resources({Resource.STONE: raid_value})]
        benefit = self.match.get_move(self, 'Take which resources?', choices)
        self.match.log(f'{self} gains {benefit}.')
        self.resources += benefit

    def pay_for_golden_age_point(self, card):
        had_gold = self.resources[Resource.GOLD] > 0
        remainder = max(0, card.age - self.golden_age_bonus())
        remainder = self.match.events['golden age discount'].happen(self, cost=remainder)
        payment = Resources()
        if remainder:
            available_resources = self.resources.production()
            if available_resources.total() < remainder:
                raise InvalidMove('Not enough resources to buy a [Point].')
            if len(available_resources) == 1:
                for resource_type in available_resources:
                    payment = Resources({resource_type: remainder})
            else:
                available_resource_types = [resource_type for resource_type in available_resources]
                for (i, resource_type) in enumerate(available_resource_types[:-1]):
                    if remainder:
                        remaining_resource_types = available_resource_types[i+1:]
                        total_remaining_resources = sum(available_resources[resource_type] for resource_type in remaining_resource_types)
                        min_of_resource = max(0, remainder - total_remaining_resources)
                        max_of_resource = min(available_resources[resource_type], remainder)
                        options = tuple(range(min_of_resource, max_of_resource + 1))
                        remaining = '/'.join(f'{resource_type}' for resource_type in remaining_resource_types)
                        if len(remaining_resource_types) > 1:
                            remaining = 'your choice of ' + remaining
                        resources_to_pay = self.match.get_move(self, f'Pay what portion in {resource_type}? (and the rest in {remaining})', options)
                        payment[resource_type] += resources_to_pay
                        remainder -= resources_to_pay
                if remainder:
                    payment[available_resource_types[-1]] += remainder
        self.match.log(f'{self} pays {payment} and gains 1 [Point].')
        self.resources -= payment
        self.points += 1
        self.match.events['bought golden age point'].happen(self)
        if had_gold and self.resources[Resource.GOLD] == 0:
            self.match.events['spent last gold'].happen(self)

    def have_golden_age(self, card):
        bonus = self.golden_age_bonus()
        choices = []
        if card.offers_special_action:
            choices.append('Special Action')
        elif card.offers_books:
            choices.append(Resources({Resource.BOOKS: 2 + bonus}))
        elif card.offers_stone:
            choices.append(Resources({Resource.STONE: 2 + bonus}))
        choices.append('Buy 1 [Point]')
        benefit = self.match.get_move(self, 'Take which benefit?', choices)
        benefit_string = str(benefit)
        if benefit_string == 'Special Action':
            card.assign_owner(self)
            card.activate(self)
        elif benefit_string == 'Buy 1 [Point]':
            self.pay_for_golden_age_point(card)
        else:
            self.match.log(f'{self} gains {benefit}.')
            self.resources += benefit
            if benefit[Resource.BOOKS]:
                self.match.events['golden age choose books'].happen(self)

    def buy_action(self, action, free=False):
        card = action.card
        had_gold = self.resources[Resource.GOLD] > 0
        buy_with = None
        if action.player is None:
            card.assign_owner(self)
            self.match.progress_board[action.row][action.col] = None
            self.match.events['may not buy card'].happen(self, card=card)
            if card.is_colony():
                military_requirement = card.military_requirement + self.match.events['extra colony military requirement'].happen(self)
                military_requirement = self.match.events['colony discount'].happen(self, cost=military_requirement)
                if self.resources[Resource.MILITARY] < military_requirement:
                    raise InvalidMove(f'Military requirement not met to buy "{card}".')
            elif card.is_natural_wonder():
                card.buying()
                wonder_spaces_needed = 1 + self.match.events['extra wonder space'].happen(self, card=card)
                if wonder_spaces_needed > self.replaceable_wonder_spaces():
                    raise InvalidMove('Not enough replaceable wonder spaces remaining.')
            if free:
                price = 0
            else:
                row = action.row + 1
                price = row
                price += self.match.events['extra card cost'].happen(self, card=card)
                price = self.match.events['card discount'].happen(self, card=card, row=row, cost=price)
                extra_payment = self.match.events['extra payment'].happen(self, card=card)
                if self.resources[Resource.GOLD] < price + extra_payment:
                    raise InvalidMove(f'Not enough [Gold] to buy "{card}".')
                self.match.log(f'{self} pays {price} [Gold] to buy "{card}".')
                self.resources[Resource.GOLD] -= price
                if extra_payment:
                    self.match.events['make extra payment'].happen(self, card=card)
        else:
            buy_with = self.match.events['buy with'].happen(self, card=card)
            price = self.match.events['buy from player'].happen(self, card=card)[0]
            if buy_with:
                buy_with = buy_with[0]
            else:
                buy_with = None
            if buy_with is not None:
                buy_with.assign_owner(self)
            card.assign_owner(self)
        self.match.events['buying card'].happen(self, card=card)
        self.match.events['buy card for gold'].happen(self, card=card, gold=price)
        if had_gold and self.resources[Resource.GOLD] == 0:
            self.match.events['spent last gold'].happen(self)
        if any(self.match.events['discard immediately'].happen(self, card=card)):
            card.unregister_all_events()
            self.match.update_most_least_stability_military()
            return
        if buy_with is not None:
            buy_with.buy()
        card.buy()
        if card.is_building_military_colony_advisor():
            if buy_with is not None:
                self.place_card(buy_with, update_most_least_stability_military=False)
                self.cover_with(buy_with, card)
            else:
                self.place_card(card)
        elif card.is_wonder_natural_wonder():
            old_card = self.wonders_under_construction[0]
            if old_card is not None:
                old_card.global_effect = False
                self.match.log(f'{self} replaces wonder under construction, "{old_card}".')
            self.wonders_under_construction[0] = card
        elif card.is_war():
            self.declare_war(card)
        elif card.is_battle():
            self.do_battle()
        elif card.is_golden_age():
            self.have_golden_age(card)
        self.match.events['bought card'].happen(self, card=card)
        self.match.events['after bought card'].happen(self, card=card)

    def deploy_for_free(self, card):
        self.workers -= 1
        card.deploy()
        self.match.update_most_least_stability_military()
        self.match.events['deployed'].happen(self, card=card)

    def deploy_action(self, action):
        if self.workers == 0:
            raise InvalidMove('No workers available to deploy.')
        card = action.card
        cost = -card.deployment_cost
        cost = self.match.events['deploy discount'].happen(self, card=card, cost=cost)
        if not (self.resources[Resource.STONE] >= cost):
            raise InvalidMove(f'Not enough resources to deploy to "{card}".')
        self.match.log(f'{self} pays {cost} [Stone] to deploy to "{card}".')
        self.resources[Resource.STONE] -= cost
        self.deploy_for_free(card)

    def undeploy_action(self, action, update_most_least_stability_military=True):
        card = action.card
        self.match.log(f'{self} undeploys 1 [Worker] from "{card}".')
        card.undeploy()
        self.workers += 1
        if update_most_least_stability_military:
            self.match.update_most_least_stability_military()

    def place_wonder_or_natural_wonder(self, card):
        slots = []
        for (i, space) in enumerate(self.wonders):
            if space is None or not space.is_natural_wonder_or_extension():
                slots.append(f'W{i + 1}')
        if len(slots) == 1:
            slot = slots[0]
        else:
            slot = self.match.get_move(self, f'Place {card.progress_card_type} where?', slots)
        (slot_type, index) = self.slot_type_index_from_slot(slot)
        old_card = self.wonders[index]
        if old_card is not None:
            self.match.log(f'{self} replaces "{old_card}".')
            self.match.events['replaced card'].happen(self, old_card=old_card, new_card=card)
            self.remove(old_card)
        self.wonders[index] = card
        self.resources += card.production_value.immediate()

    def hire_free_architect(self, card):
        card.completed_stages += 1
        self.match.events['hire architect'].happen(self)
        if card.completed_stages == len(card.stage_costs):
            self.match.log(f'"{card}" is ready.')
            self.match.events['wonder ready'].happen(self)
            card.ready()
            self.place_wonder_or_natural_wonder(card)
            self.wonders_under_construction[0] = None
            card.completed_stages = 0
            card.placed()
            self.match.update_most_least_stability_military()

    def hire_action(self, action):
        card = action.card
        private = action.private
        if private is None and self.match.architects == 0:
            raise InvalidMove('No available architects to hire.')
        elif private is not None and private.private_architects_available == 0:
            raise InvalidMove(f'[{private}] No available architects to hire.')
        cost = -card.stage_costs[card.completed_stages]
        cost = self.match.events['hire discount'].happen(self, cost=cost)
        if not (self.resources[Resource.STONE] >= cost):
            raise InvalidMove(f'Not enough resources for next stage of "{card}".')
        if private is None:
            self.match.log(f'{self} pays {cost} [Stone] to hire an architect for "{card}".')
            self.match.architects -= 1
        else:
            self.match.log(f'{self} pays {cost} [Stone] to hire a private architect from "{private}" for "{card}".')
            private.private_architects_available -= 1
        self.resources[Resource.STONE] -= cost
        self.hire_free_architect(card)

    def explore_action(self, action):
        card = action.card
        self.match.log(f'{self} explores "{card}".')
        card.turns_explored += 1
        if card.turns_explored == card.exploration_turns:
            self.match.log(f'"{card}" has been discovered.')
            card.discovered()
            self.match.events['discover'].happen(self, card=card)
            self.place_wonder_or_natural_wonder(card)
            self.wonders_under_construction[0] = None
            card.turns_explored = 0
            card.placed()
            self.match.update_most_least_stability_military()

    def special_action(self, action):
        action.card.activate(self)
        self.match.update_most_least_stability_military()

    def play_dynasty(self, card, defer_taking_turmoil=False):
        self.match.log(f'{self} plays "{card}".')
        for i in range(len(self.dynasties)):
            if self.dynasties[i] is card:
                self.dynasties[i] = None
        if defer_taking_turmoil:
            self.turmoil += 1
            self.resources[Resource.STABILITY] -= 2
        if self.specials:
            if self.match.events['keep dynasty effects'].happen(self):
                self.specials[0].covered_by = card
            else:
                self.remove(self.specials[0])
                self.specials[0] = card
        else:
            self.nation.place_dynasty(self, card)
        self.resources += card.production_value.immediate()
        return card.play()

    def turmoil_action(self, action):
        self.match.log(f'{self} takes a turmoil card.')
        self.match.turmoil -= 1
        defer_taking_turmoil = any(self.match.events['defer taking turmoil'].happen(self))
        if not defer_taking_turmoil:
            self.turmoil += 1
            self.resources[Resource.STABILITY] -= 2
        possible_benefits = [Resources({Resource.GOLD: 2})]
        if self.dynasty_cards():
            for card in self.dynasty_cards():
                possible_benefits.append(f'Play "{card}"')
            benefit = self.match.get_move(self, 'Which benefit?', possible_benefits)
        else:
            benefit = possible_benefits[0]
        if str(benefit).startswith('Play '):
            for card in self.dynasties:
                if benefit == f'Play "{card}"':
                    self.play_dynasty(card, defer_taking_turmoil=defer_taking_turmoil)
                    break
        else:
            self.match.log(f'{self} gains 2 [Gold].')
            if defer_taking_turmoil and not any(self.match.events['discard gold turmoil'].happen(self)):
                self.turmoil += 1
                self.resources[Resource.STABILITY] -= 2
            self.resources[Resource.GOLD] += 2
        self.match.update_most_least_stability_military()

    def pass_action(self, action):
        self.match.log(f'{self} passes.')
        self.passed = True
        max_most_min_least = 1 if len(self.match.players) < 5 else 2
        passed_players = [player for player in self.match.players if player.passed]
        if len(passed_players) <= max_most_min_least:
            self.passed_first = True
        if len(passed_players) > len(self.match.players) - max_most_min_least:
            self.passed_last = True
        self.match.events['pass'].happen(self)

    def take_action(self, action):
        return {
            ActionType.BUY: self.buy_action,
            ActionType.DEPLOY: self.deploy_action,
            ActionType.UNDEPLOY: self.undeploy_action,
            ActionType.HIRE: self.hire_action,
            ActionType.EXPLORE: self.explore_action,
            ActionType.SPECIAL: self.special_action,
            ActionType.TURMOIL: self.turmoil_action,
            ActionType.PASS: self.pass_action
        }[action.action_type](action)

    def take_one_action(self):
        possible_actions = self.explore_actions()
        if possible_actions:
            action = possible_actions[0]
        else:
            possible_actions += self.buy_actions()
            possible_actions += self.deploy_actions()
            possible_actions += self.undeploy_actions()
            possible_actions += self.hire_actions()
            possible_actions += self.turmoil_actions()
            possible_actions += self.special_actions()
            possible_actions.append(PassAction())
            action = self.match.get_move(self, 'Which action?', possible_actions)
        self.take_action(action)
        if action.action_type is ActionType.PASS:
            self.remaining_main_actions = 0
        elif action.action_type is not ActionType.UNDEPLOY:
            self.remaining_main_actions -= 1
            self.action_number += 1

    def take_turn(self):
        self.turn_number += 1
        if any(self.match.events['skip turn'].happen(self)):
            self.remaining_main_actions = 0
            return
        self.remaining_main_actions = 1
        if any(self.match.events['additional action'].happen(self)):
            self.remaining_main_actions += 1
        while self.remaining_main_actions:
            self.take_one_action()
        while self.need_confirmation:
            possible_actions = [ConfirmAction()]
            if not self.passed and not self.explore_actions():
                possible_actions += self.undeploy_actions()
            action = self.match.get_move(self, 'Complete the turn?', possible_actions)
            if action.action_type is ActionType.CONFIRM:
                return
            self.take_action(action)

    def may_take_workers(self, number=1, from_extra=True):
        available = self.extra_worker_pool if from_extra else 0
        for worker_pool in self.worker_pools:
            available += worker_pool.ungrown_workers
        return available >= number

    def take_worker(self, from_extra=True, update_immediate_production=True):
        if not self.may_take_workers(from_extra=from_extra):
            raise InvalidMove('Not enough workers available to take.')
        if from_extra and self.extra_worker_pool:
            self.match.log(f'{self} takes a [Worker] from the extra worker pool.')
            self.extra_worker_pool -= 1
            self.workers += 1
            self.grown_workers += 1
        else:
            worker_options = []
            for worker_pool in self.worker_pools:
                if worker_pool.ungrown_workers:
                    worker_options.append(f'{worker_pool.resource_cost_per_worker} [Worker]')
            if len(worker_options) == 1:
                worker_chosen = worker_options[0]
            else:
                worker_chosen = self.match.get_move(self, 'Take which type of [Worker]?', worker_options)
            for worker_pool in self.worker_pools:
                if worker_chosen.startswith(str(worker_pool.resource_cost_per_worker)):
                    self.match.log(f'{self} takes a {worker_pool.resource_cost_per_worker} [Worker].')
                    if update_immediate_production and worker_pool.resource_cost_per_worker.immediate():
                        self.resources += worker_pool.resource_cost_per_worker.immediate()
                        self.match.update_most_least_stability_military()
                    worker_pool.grow_worker()
                    self.workers += 1
                    self.grown_workers += 1
                    break
        self.match.events['take worker'].happen(self, growth=False)

    def return_worker(self, no_confirmation=False):
        if self.workers == 0:
            possible_undeploys = self.undeploy_actions()
            if not possible_undeploys:
                self.match.log(f'{self} has no workers that can be returned!')
                return
            if len(possible_undeploys) == 1:
                undeploy = possible_undeploys[0]
            else:
                undeploy = self.match.get_move(self, 'Undeploy worker to return from where?', possible_undeploys)
            self.undeploy_action(undeploy, update_most_least_stability_military=False)
        return_options = []
        for worker_pool in self.worker_pools:
            if worker_pool.may_return_worker():
                return_options.append(f'{worker_pool.resource_cost_per_worker} [Worker]')
        if not return_options:
            self.match.log(f'{self} returns a [Worker] to the extra worker pool.')
            self.extra_worker_pool += 1
        else:
            if len(return_options) == 1:
                return_chosen = return_options[0]
            else:
                return_chosen = self.match.get_move(self, 'Return what type of worker?', return_options)
            for worker_pool in self.worker_pools:
                if return_chosen.startswith(str(worker_pool.resource_cost_per_worker)):
                    self.match.log(f'{self} returns a {worker_pool.resource_cost_per_worker} [Worker].')
                    if worker_pool.resource_cost_per_worker.immediate():
                        self.resources -= worker_pool.resource_cost_per_worker.immediate()
                    worker_pool.return_worker()
                    break
        self.workers -= 1
        self.grown_workers -= 1
        self.match.update_most_least_stability_military()
        if self.need_confirmation and not no_confirmation:
            self.match.get_move(self, 'Confirm?', ('Confirm',))

    def remove_cards(self, cards):
        cards_to_remove = set(cards)
        for card in cards:
            cards_to_remove |= set(self.match.events['remove with'].happen(self, card=card))
        for (slot, board_card) in self.filled_slot_names_cards():
            if board_card in cards_to_remove:
                card = board_card
                card_stack = [card]
                while card.covered_by is not None:
                    card = card.covered_by
                    card_stack.append(card)
                for card in reversed(card_stack):
                    cards_to_remove -= {card}
                    if card.is_building_military():
                        workers = card.deployed_workers
                        while card.deployed_workers:
                            card.undeploy()
                        self.workers += workers
                    self.resources -= card.production_value.immediate()
                    (slot_type, index) = self.slot_type_index_from_slot(slot)
                    base_card = self.slots_from_slot_type(slot_type)[index]
                    if base_card is card:
                        self.slots_from_slot_type(slot_type)[index] = card.covered_by
                    else:
                        while base_card.covered_by is not card:
                            base_card = base_card.covered_by
                        base_card.covered_by = card.covered_by
                    self.match.events['when removed'].happen(self, card=card)
                    card.unregister_all_events()
        self.match.update_most_least_stability_military()

    def remove(self, card):
        self.remove_cards([card])

    def remove_all_advisors(self):
        self.remove_cards(self.removable_advisor_cards())

    def losing_resources_needs_choice(self, resources_to_lose):
        resources_after_loss = self.resources.production()
        remainder = 0
        for resource_type in resources_to_lose:
            amount = resources_to_lose[resource_type]
            if resources_after_loss[resource_type] + amount >= 0:
                resources_after_loss[resource_type] += amount
            else:
                remainder += resources_after_loss[resource_type] + amount
                resources_after_loss[resource_type] = 0
        if remainder == 0:
            return False
        remainder = -remainder
        if resources_after_loss[Resource.BOOKS] - remainder >= 0:
            return False
        remainder -= resources_after_loss[Resource.BOOKS]
        resources_after_loss[Resource.BOOKS] = 0
        if resources_after_loss.total() - remainder <= 0:
            return False
        if len(resources_after_loss) == 1:
            return False
        return True

    def lose_point(self):
        if self.points > 0:
            self.match.log(f'{self} loses 1 [Point].')
            self.points -= 1
        else:
            self.match.log(f'{self} is spared the [Point] loss.')

    def lose_resources(self, resources_to_lose, lost_to_war=False):
        if lost_to_war:
            total_loss = self.resources.production()
        remainder = 0
        mentioned_negative_books = False
        for resource_type in resources_to_lose:
            amount = resources_to_lose[resource_type]
            if self.resources[resource_type] + amount >= 0:
                self.resources[resource_type] += amount
            else:
                self.match.log(f'{self} goes negative in {resource_type}!')
                if resource_type is Resource.BOOKS:
                    mentioned_negative_books = True
                remainder += self.resources[resource_type] + amount
                self.resources[resource_type] = 0
                if any(self.match.events['no resource point loss'].happen(self)):
                    pass
                elif not self.resource_deficit_points[resource_type] and self.points:
                    self.match.log(f'{self} loses 1 [Point] for negative {resource_type}.')
                    self.points -= 1
                    if lost_to_war:
                        self.match.events['lost to war'].happen(self, points=1)
                    self.resource_deficit_points[resource_type] = -1
                elif self.resource_deficit_points[resource_type]:
                    self.match.log(f'{self} already lost a [Point] for negative {resource_type}.')
                else:
                    self.match.log(f'{self} is spared the [Point] loss.')
        if remainder:
            remainder = -remainder
            if self.resources[Resource.BOOKS]:
                self.match.log(f'{self} loses {remainder} [Book{s_if_not_1(remainder)}] for negative resources.')
            if self.resources[Resource.BOOKS] - remainder >= 0:
                self.resources[Resource.BOOKS] -= remainder
                remainder = 0
            else:
                remainder -= self.resources[Resource.BOOKS]
                self.resources[Resource.BOOKS] = 0
                self.match.log(f'{self} goes negative in [Books] and must lose {remainder} other resources.')
                if any(self.match.events['no resource point loss'].happen(self)):
                    pass
                elif not self.resource_deficit_points[Resource.BOOKS] and self.points:
                    self.match.log(f'{self} loses 1 [Point] for negative [Books].')
                    self.points -= 1
                    if lost_to_war:
                        self.match.events['lost to war'].happen(self, points=1)
                    self.resource_deficit_points[Resource.BOOKS] = -1
                elif self.resource_deficit_points[Resource.BOOKS]:
                    if not mentioned_negative_books:
                        self.match.log(f'{self} already lost a [Point] for negative [Books].')
                else:
                    self.match.log(f'{self} is spared the [Point] loss.')
                if self.resources.production().total() == 0:
                    self.match.log(f'{self} has no remaining resources to lose.')
                    self.resources -= self.resources.production()
                elif self.resources.production().total() - remainder <= 0:
                    self.match.log(f'{self} loses all remaining resources.')
                    self.resources -= self.resources.production()
                else:
                    available_resources = self.resources.production()
                    if len(available_resources) == 1:
                        for resource_type in available_resources:
                            self.match.log(f'{self} loses {remainder} {resource_type} for going negative in [Books].')
                            self.resources[resource_type] -= remainder
                    else:
                        loss = Resources()
                        available_resource_types = [resource_type for resource_type in available_resources]
                        for (i, resource_type) in enumerate(available_resource_types[:-1]):
                            if remainder:
                                remaining_resource_types = available_resource_types[i+1:]
                                total_remaining_resources = sum(available_resources[resource_type] for resource_type in remaining_resource_types)
                                min_of_resource = max(0, remainder - total_remaining_resources)
                                max_of_resource = min(available_resources[resource_type], remainder)
                                options = tuple(range(min_of_resource, max_of_resource + 1))
                                remaining = '/'.join(f'{resource_type}' for resource_type in remaining_resource_types)
                                if len(remaining_resource_types) > 1:
                                    remaining = 'your choice of ' + remaining
                                amount_to_lose = self.match.get_move(self, f'Lose what portion as {resource_type}? (and the rest as {remaining})', options)
                                loss[resource_type] += amount_to_lose
                                remainder -= amount_to_lose
                        if remainder:
                            loss[available_resource_types[-1]] += remainder
                        self.match.log(f'{self} loses {loss} for going negative in [Books].')
                        self.resources -= loss
                        self.match.get_move(self, 'Confirm resource loss?', ('Confirm',))
        if lost_to_war:
            total_loss -= self.resources.production()
            self.match.events['lost to war'].happen(self, resources=total_loss)

    def production(self, projected=False):
        total_production = Resources()
        for card in self.completed_cards():
            total_production += card.produce(projected=projected)
        for worker_pool in self.worker_pools:
            total_production += worker_pool.total_resource_cost
        if self.resources[Resource.STABILITY] < 0:
            total_production[Resource.BOOKS] += self.resources[Resource.STABILITY]
        if self.resources[Resource.MILITARY] < 0:
            total_production[Resource.BOOKS] += self.resources[Resource.MILITARY]
        for additional_production in self.match.events['additional production'].happen(self, production=total_production, projected=projected):
            total_production += additional_production
        return total_production.production()

    def produce(self):
        total_production = self.production()
        if self.resources[Resource.STABILITY] < 0:
            self.match.log(f'{self} is in revolt!')
            if self.points > 0:
                self.match.log(f'{self} loses 1 [Point] for revolt.')
                self.points -= 1
            else:
                self.match.log(f'{self} is spared the [Point] loss.')
        if self.resources[Resource.MILITARY] < 0:
            self.match.log(f'{self} has negative [Military]!')
            if self.points > 0:
                self.match.log(f'{self} loses 1 [Point] for negative [Military].')
                self.points -= 1
            else:
                self.match.log(f'{self} is spared the [Point] loss.')
        self.match.log(f'{self} produces: {total_production.production_str()}')
        positive_production = total_production.positive()
        negative_production = total_production.negative()
        self.resources += positive_production
        self.lose_resources(negative_production)

    def war(self, penalty):
        if self.resources[Resource.MILITARY] + self.match.events['extra war military'].happen(self) < self.match.war_value:
            if not any(self.match.events['no defeated effect'].happen(self)):
                self.match.events['defeated'].happen(self)
                if not any(self.match.events['spared war point loss'].happen(self)):
                    if self.points > 0:
                        self.match.log(f'{self} loses 1 [Point] for being defeated in the "{self.match.war}".')
                        self.points -= 1
                        self.match.events['lost to war'].happen(self, points=1)
                    else:
                        self.match.log(f'{self} is spared the [Point] loss from being defeated in the "{self.match.war}".')
                resource_loss_amount = penalty.total()
                if self.resources[Resource.STABILITY] > 0:
                    resource_loss_amount += self.resources[Resource.STABILITY]
                if resource_loss_amount < 0:
                    if self.resources[Resource.STABILITY] > 0:
                        if len(penalty) == 1:
                            self.match.log(f'{self} mitigates part of the resource loss with [Stability].')
                            resource_loss = Resources({resource_type: resource_loss_amount for resource_type in penalty})
                        else:
                            mitigation = Resources()
                            remainder = self.resources[Resource.STABILITY]
                            penalty_resource_types = [resource_type for resource_type in penalty]
                            for resource_type in penalty_resource_types[1:]:
                                if remainder:
                                    max_of_resource = min(-penalty[resource_type], remainder)
                                    amount_to_mitigate = self.match.get_move(self, f'Prevent how much of the {resource_type} loss?', tuple(range(max_of_resource + 1)))
                                    mitigation[resource_type] += amount_to_mitigate
                                    remainder -= amount_to_mitigate
                            if remainder:
                                mitigation[penalty_resource_types[0]] += remainder
                            self.match.log(f'{self} mitigates {mitigation} of the war penalty with [Stability].')
                            resource_loss = Resources(penalty)
                            resource_loss += mitigation
                    else:
                        resource_loss = penalty
                    self.match.log(f'{self} loses {-resource_loss}.')
                    self.lose_resources(resource_loss, lost_to_war=True)
                    if self.need_confirmation:
                        self.match.get_move(self, 'Confirm war resolution?', ('Confirm',))
                else:
                    self.match.log(f'{self} mitigates the resource loss entirely with [Stability].')
            return True
        else:
            self.match.events['not defeated'].happen(self)
            return False

    def famine(self):
        famine = self.match.event.famine + self.match.events['extra famine'].happen(self)
        self.lose_resources(Resources({Resource.FOOD: famine}))

    def discard_turmoil(self):
        if self.turmoil:
            self.match.log(f'{self} discards {self.turmoil} turmoil card{s_if_not_1(self.turmoil)} and gains {2 * self.turmoil} [Stability].')
            self.resources[Resource.STABILITY] += 2 * self.turmoil
            self.turmoil = 0

    def score(self, projected=False):
        if self.nation is None:
            return 0
        extra_stone = self.match.events['extra scoring stone'].happen(self, projected=projected)
        total = self.points
        for card in self.colony_cards():
            total += card.points
        for card in self.wonder_natural_wonder_cards():
            total += card.points
        for card in self.building_military_cards():
            total += sum(card.worker_points[:min(len(card.worker_points),card.deployed_workers)])
        for card in self.completed_cards():
            total += card.bonus_points(projected)
        self.resources[Resource.STONE] += extra_stone
        total += self.resources.total() // 10
        self.resources[Resource.STONE] -= extra_stone
        return total

    def resource_remainder(self):
        if self.nation is None:
            return 0
        extra_stone = self.match.events['extra scoring stone'].happen(self, projected=True)
        self.resources[Resource.STONE] += extra_stone
        remainder = self.resources.total() % 10
        self.resources[Resource.STONE] -= extra_stone
        return remainder

    def state(self):
        s = {}
        s['nation'] = self.nation.name if self.nation is not None else None
        if self.nation is None:
            return s
        s['resources'] = self.resources.state()
        s['production'] = self.production(projected=True).state()
        s['workers'] = self.workers
        s['grown_workers'] = self.grown_workers
        s['points'] = self.points
        s['worker_pools'] = {str(worker_pool.resource_cost_per_worker): worker_pool.state() for worker_pool in self.worker_pools}
        s['extra_workers'] = self.extra_worker_pool
        slots = {slot: card.abbr for (slot, card) in self.slot_names_cards() if card is not None}
        if self.wonders_under_construction[0] is not None:
            slots['Hire'] = self.wonders_under_construction[0].abbr
        s['slots'] = slots
        s['dynasties'] = [card.abbr if card is not None else None for card in self.dynasties]
        s['cards'] = {card.abbr: card.state() for card in self.all_cards()}
        s['turmoil'] = self.turmoil
        s['most_stability'] = int(self.most_stability)
        s['least_stability'] = int(self.least_stability)
        s['most_military'] = int(self.most_military)
        s['least_military'] = int(self.least_military)
        s['resource_deficit_points'] = self.resource_deficit_points.state()
        s['passed'] = int(self.passed)
        s['passed_first'] = int(self.passed_first)
        s['passed_last'] = int(self.passed_last)
        s['bought_colony'] = int(self.bought_colony_this_round)
        s['score'] = self.score(projected=True)
        return s
