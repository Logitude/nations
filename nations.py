from .exceptions import *
from .cards import *
from .resources import *
from .progress_cards import *
from .dynasty_cards import *

def s_if_not_1(value):
    return 's' if value != 1 else ''

class Special(Card):
    card_type = CardType.SPECIAL

class WorkerPool:
    def __init__(self, workers, resource_cost):
        self.spots = workers
        self.resource_cost_per_worker = resource_cost
        self.reset()

    def reset(self):
        self.ungrown_workers = self.spots
        self.markers = 0
        self.total_resource_cost = Resources()

    def grow_worker(self):
        self.ungrown_workers -= 1
        self.total_resource_cost += self.resource_cost_per_worker

    def may_return_worker(self):
        return self.ungrown_workers < self.spots - self.markers

    def return_worker(self):
        self.ungrown_workers += 1
        self.total_resource_cost -= self.resource_cost_per_worker

    def mark(self):
        self.markers += 1
        self.total_resource_cost -= self.resource_cost_per_worker

    def state(self):
        s = {}
        s['workers'] = self.ungrown_workers
        if self.markers:
            s['markers'] = self.markers
        return s

class Nation:
    def __init__(self, match):
        self.match = match
        self.dynasties = [card(match) if card is not None else None for card in self.dynasties]
        self.advisors = [card(match) if card is not None else None for card in self.advisors]
        self.buildings_military = [card(match) if card is not None else None for card in self.buildings_military]
        self.specials = [card(match) if card is not None else None for card in self.specials]
        self.colonies = [card(match) if card is not None else None for card in self.colonies]
        self.wonders_under_construction = [card(match) if card is not None else None for card in self.wonders_under_construction]
        self.wonders = [card(match) if card is not None else None for card in self.wonders]

    def all_slots(self):
        return self.dynasties + self.advisors + self.buildings_military + self.specials + self.colonies + self.wonders_under_construction + self.wonders

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

    def reset(self):
        for card in self.all_slots():
            if card is not None:
                card.reset()
        for worker_pool in self.worker_pools:
            worker_pool.reset()

    def state(self):
        s = {}
        s['dynasties'] = [dynasty.abbr for dynasty in self.dynasties]
        s['resources'] = self.starting_resources.state()
        s['points'] = self.starting_points
        s['workers'] = self.starting_workers
        s['slots'] = {slot: card.abbr for (slot, card) in self.slot_names_cards() if card is not None}
        return s

    def __str__(self):
        return self.name

class StartingCard:
    starting_card = True
    age = 0

class StartingBuilding(Building, StartingCard):
    deployment_cost = -1
    worker_points = (1,)
    max_workers = False

class StartingMilitary(Military, StartingCard):
    deployment_cost = -1
    worker_points = (1,)
    max_workers = False
    raid_value = 2

class StartingColony(Colony, StartingCard):
    points = 0

class StartingWonder(Wonder, StartingCard):
    pass

class StartingAdvisor(Advisor, StartingCard):
    pass

class AmericaBuffaloHorde(StartingBuilding):
    name = 'Buffalo Horde'
    abbr = 'Am_BfHd'
    max_workers = True
    production_per_worker = Resources({Resource.FOOD: 4})

class AmericaTeePee(StartingBuilding):
    name = 'Teepee'
    abbr = 'Am_Tpe'
    production_per_worker = Resources({Resource.STONE: 1, Resource.BOOKS: 1})

class AmericaBrave(StartingMilitary):
    name = 'Brave'
    abbr = 'Am_Brv'
    production_per_worker = Resources({Resource.MILITARY: 1, Resource.GOLD: 1})

class AmericaAdobe(StartingBuilding):
    name = 'Adobe'
    abbr = 'Am_Adb'
    production_per_worker = Resources({Resource.STABILITY: 2})

class AmericaSpecial(Special):
    """Discover Natrual Wonder: +2 [Food]"""
    name = 'America Special'
    abbr = 'Am_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('discover', self.owned, self.gain_food)

    def gain_food(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Food].')
        player.resources[Resource.FOOD] += 2

class America(Nation):
    name = 'America'
    abbr = 'Am'
    dynasties = [DemocraticRepublicans, FederalistParty]
    advisors = [None]
    buildings_military = [AmericaBuffaloHorde, AmericaTeePee, AmericaBrave, AmericaAdobe]
    specials = [AmericaSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 2, Resource.STONE: 5, Resource.GOLD: 7})
    starting_points = 5
    starting_workers = 5

class ArabsKaba(StartingBuilding):
    name = 'Kaba'
    abbr = 'Ar_Kba'
    deployment_cost = -2
    worker_points = (2,)
    max_workers = True
    production_per_worker = Resources({Resource.GOLD: 2, Resource.BOOKS: 2})

class ArabsQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'Ar_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class ArabsAxeman(StartingMilitary):
    name = 'Axeman'
    abbr = 'Ar_Axm'
    production_per_worker = Resources({Resource.MILITARY: 2, Resource.FOOD: -1})

class ArabsBazaar(StartingBuilding):
    name = 'Bazaar'
    abbr = 'Ar_Bzr'
    production_per_worker = Resources({Resource.FOOD: 1, Resource.GOLD: 1})

class ArabsSpecial(Special):
    """Buy Battle: May also take 1 [Worker]"""
    name = 'Arabs Special'
    abbr = 'Ar_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('bought card', self.bought_battle, self.may_take_worker)

    def bought_battle(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_battle()

    def may_take_worker(self, player, **kwargs):
        if player.may_take_workers():
            self.match.log(f'[{self}] {player} may take 1 [Worker].')
            answer = self.match.get_move(player, 'Take 1 [Worker]?', ('Yes', 'No'))
            if answer == 'Yes':
                player.take_worker()
        else:
            self.match.log(f'[{self}] {player} has no remaining [Workers] to take.')

class Arabs(Nation):
    name = 'Arabs'
    abbr = 'Ar'
    dynasties = [AbbasidCaliphate, UmayyadCaliphate]
    advisors = [None]
    buildings_military = [ArabsKaba, ArabsQuarry, ArabsAxeman, ArabsBazaar]
    specials = [ArabsSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 2, Resource.STONE: 5, Resource.GOLD: 8})
    starting_points = 5
    starting_workers = 5

class ChinaFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'C_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class ChinaQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'C_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class ChinaAxeman(StartingMilitary):
    name = 'Axeman'
    abbr = 'C_Axm'
    production_per_worker = Resources({Resource.MILITARY: 2, Resource.FOOD: -1})

class ChinaPagoda(StartingBuilding):
    name = 'Pagoda'
    abbr = 'C_Pgd'
    worker_points = (1, 1)
    production_per_worker = Resources({Resource.BOOKS: 2, Resource.STABILITY: 1})

class ChinaSpecial(Special):
    """Production: If passed first: +1 [Food]"""
    name = 'China Special'
    abbr = 'C_S'

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.passed_first:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 1 [Food].')
            production[Resource.FOOD] += 1
        return production

class China(Nation):
    name = 'China'
    abbr = 'C'
    dynasties = [MingDynasty, QinDynasty]
    advisors = [None]
    buildings_military = [ChinaFarm, ChinaQuarry, ChinaAxeman, ChinaPagoda]
    specials = [ChinaSpecial]
    colonies = [None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None, None]
    worker_pools = [WorkerPool(3, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 1, Resource.STONE: 5, Resource.GOLD: 5})
    starting_points = 3
    starting_workers = 6

class EgyptBrewery(StartingBuilding):
    name = 'Brewery'
    abbr = 'Eg_Brw'
    worker_points = (1, 1)
    production_per_worker = Resources({Resource.FOOD: 2, Resource.BOOKS: 1})

class EgyptQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'Eg_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class EgyptTemple(StartingBuilding):
    name = 'Temple'
    abbr = 'Eg_Tpl'
    production_per_worker = Resources({Resource.BOOKS: 1, Resource.GOLD: 1})

class EgyptCaravan(StartingBuilding):
    name = 'Caravan'
    abbr = 'Eg_Crv'
    production_per_worker = Resources({Resource.STABILITY: 1, Resource.GOLD: 1})

class EgyptSpecial(Special):
    """1 private [Architect] per round"""
    name = 'Egypt Special'
    abbr = 'Eg_S'
    private_architects = 1

class EgyptPyramids(StartingWonder):
    name = 'Pyramids'
    abbr = 'Eg_Prm'
    points = 3
    production_value = Resources({Resource.GOLD: 2, Resource.FOOD: -2})

class Egypt(Nation):
    name = 'Egypt'
    abbr = 'Eg'
    dynasties = [NewKingdom, OldKingdom]
    advisors = [None]
    buildings_military = [EgyptBrewery, EgyptQuarry, EgyptTemple, EgyptCaravan]
    specials = [EgyptSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [EgyptPyramids, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 2, Resource.STONE: 7, Resource.GOLD: 5})
    starting_points = 4
    starting_workers = 5

class EthiopiaStele(StartingBuilding):
    name = 'Stele'
    abbr = 'Et_Stl'
    production_per_worker = Resources({Resource.GOLD: 1, Resource.STABILITY: 1, Resource.BOOKS: 1})

class EthiopiaQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'Et_qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class EthiopiaAxeman(StartingMilitary):
    name = 'Axeman'
    abbr = 'Et_Axm'
    production_per_worker = Resources({Resource.MILITARY: 2, Resource.FOOD: -1})

class EthiopiaFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'Et_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class EthiopiaSpecial(Special):
    """Player Order: Add [Stability] to [Military]"""
    name = 'Ethiopia Special'
    abbr = 'Et_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('extra player order military', self.owned, self.stability)

    def stability(self, player, **kwargs):
        self.match.log(f'[{self}] {player} adds [Stability] to [Military] for determining player order.')
        return player.resources[Resource.STABILITY]

class Ethiopia(Nation):
    name = 'Ethiopia'
    abbr = 'Et'
    dynasties = [AxumiteKingdom, Sheba]
    advisors = [None]
    buildings_military = [EthiopiaStele, EthiopiaQuarry, EthiopiaAxeman, EthiopiaFarm]
    specials = [EthiopiaSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 4, Resource.STONE: 7, Resource.GOLD: 5})
    starting_points = 5
    starting_workers = 5

class GreeceFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'G_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class GreeceQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'G_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class GreeceHoplite(StartingMilitary):
    name = 'Hoplite'
    abbr = 'G_Hpl'
    worker_points = (1, 1)
    raid_value = 3
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.STONE: -1})

class GreeceLyceum(StartingBuilding):
    name = 'Lyceum'
    abbr = 'G_Lyc'
    worker_points = (1, 1)
    production_per_worker = Resources({Resource.BOOKS: 2, Resource.STONE: 1})

class GreeceSpecial(Special):
    """Golden age bonus: 1"""
    name = 'Greece Special'
    abbr = 'G_S'
    golden_age_bonus = 1

class Greece(Nation):
    name = 'Greece'
    abbr = 'G'
    dynasties = [Athens, Sparta]
    advisors = [None]
    buildings_military = [GreeceFarm, GreeceQuarry, GreeceHoplite, GreeceLyceum]
    specials = [GreeceSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 3, Resource.STONE: 6, Resource.GOLD: 6})
    starting_points = 5
    starting_workers = 5

class IndiaTemple(StartingBuilding):
    name = 'Temple'
    abbr = 'I_Tpl'
    production_per_worker = Resources({Resource.BOOKS: 1, Resource.GOLD: 1})

class IndiaQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'I_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class IndiaChariot(StartingMilitary):
    name = 'Chariot'
    abbr = 'I_Crt'
    worker_points = (2,)
    raid_value = 3
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.GOLD: -1})

class IndiaFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'I_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class IndiaSpecial(Special):
    name = 'India Special'
    abbr = 'I_S'
    production_value = Resources({Resource.FOOD: 2})

class IndiaVaranasi(StartingWonder):
    """Production: per undeployed [Worker]: 1 [Book] 1 [Food]"""
    name = 'Varanasi'
    abbr = 'I_Vrn'
    points = 0

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.workers:
            extra_production = Resources({Resource.BOOKS: self.owner.workers, Resource.FOOD: self.owner.workers})
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra {extra_production}.')
            production += extra_production
        return production

class India(Nation):
    name = 'India'
    abbr = 'I'
    dynasties = [MauryanEmpire, MughalEmpire]
    advisors = [None]
    buildings_military = [IndiaTemple, IndiaQuarry, IndiaChariot, IndiaFarm]
    specials = [IndiaSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [IndiaVaranasi, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 3, Resource.STONE: 4, Resource.GOLD: 6})
    starting_points = 4
    starting_workers = 5

class JapanEmperor(StartingAdvisor):
    """Buy Advisor: Discard, +1 [Marker]; +1 [Military] per [Marker]"""
    name = 'Emperor'
    abbr = 'J_Epr'
    production_value = Resources({Resource.STABILITY: 2})

    def new_round(self):
        pass

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('discard immediately', self.bought_advisor, self.gain_military)

    def bought_advisor(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_advisor()

    def gain_military(self, player, **kwargs):
        card = kwargs['card']
        self.match.log(f'[{self}] {player} discards "{card}" and gains 1 [Military].')
        self.markers += 1
        player.resources[Resource.MILITARY] += 1
        return True

class JapanTemple(StartingBuilding):
    name = 'Temple'
    abbr = 'J_Tpl'
    production_per_worker = Resources({Resource.BOOKS: 1, Resource.GOLD: 1})

class JapanQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'J_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class JapanAxeman(StartingMilitary):
    name = 'Axeman'
    abbr = 'J_Axm '
    production_per_worker = Resources({Resource.MILITARY: 2, Resource.FOOD: -1})

class JapanRiceFields(StartingBuilding):
    name = 'Rice Fields'
    abbr = 'J_RcFd'
    production_per_worker = Resources({Resource.FOOD: 3})

class JapanHokkaido(StartingBuilding):
    name = 'Hokkaido'
    abbr = 'J_Hkd'
    deployment_cost = -0
    worker_points = ()
    max_workers = True
    production_per_worker = Resources()

class Japan(Nation):
    name = 'Japan'
    abbr = 'J'
    dynasties = [EdoPeriod, HeianPeriod]
    advisors = [JapanEmperor]
    buildings_military = [JapanTemple, JapanQuarry, JapanAxeman, JapanRiceFields, JapanHokkaido]
    specials = []
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 3, Resource.STONE: 6, Resource.GOLD: 7})
    starting_points = 5
    starting_workers = 5

    def place_dynasty(self, player, card):
        for (i, slot) in enumerate(player.buildings_military):
            if slot is not None and slot.is_dynasty():
                player.remove(slot)
                player.buildings_military[i] = card
                break
        else:
            for (i, slot) in reversed(list(enumerate(player.buildings_military))):
                if slot is None:
                    player.buildings_military[i] = card
                    break
            else:
                slots = [f'BM{i + 1}' for i in range(len(player.buildings_military))]
                slot = self.match.get_move(player, 'Replace which building/military slot?', slots)
                (slot_type, index) = player.slot_type_index_from_slot(slot)
                old_card = player.slots_from_slot_type(slot_type)[index]
                player.remove(old_card)
                player.slots_from_slot_type(slot_type)[index] = card

class KoreaTemple(StartingBuilding):
    name = 'Temple'
    abbr = 'K_Tpl'
    production_per_worker = Resources({Resource.BOOKS: 1, Resource.GOLD: 1})

class KoreaQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'K_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class KoreaArcher(StartingMilitary):
    name = 'Archer'
    abbr = 'K_Arc'
    worker_points = (1, 1)
    raid_value = 4
    production_per_worker = Resources({Resource.MILITARY: 2})

class KoreaConfucianAcadamy(StartingBuilding):
    name = 'Confucian Academy'
    abbr = 'K_CfAc'
    worker_points = (1, 1)
    production_per_worker = Resources({Resource.STABILITY: 2, Resource.GOLD: 1})

class KoreaSpecial(Special):
    """Buy Golden Age: May also hire 2 [Architects] for free"""
    name = 'Korea Special'
    abbr = 'K_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('bought card', self.bought_golden_age, self.may_hire)

    def bought_golden_age(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_golden_age()

    def may_hire(self, player, **kwargs):
        architects = 1 if self.match.korea_nerf else 2
        self.match.log(f'[{self}] {player} may hire up to {architects} [Architect{s_if_not_1(architects)}] for free.')
        for i in range(architects):
            if player.incomplete_wonder_stages():
                answer = self.match.get_move(player, 'Hire [Architect] for free?', ('Yes', 'No'))
                if answer == 'Yes':
                    card = player.wonders_under_construction[0]
                    self.match.log(f'[{self}] {player} hires a free architect for "{card}".')
                    player.hire_free_architect(card)
            else:
                self.match.log(f'[{self}] {player} has no wonders under construction.')
                break

class Korea(Nation):
    name = 'Korea'
    abbr = 'K'
    dynasties = [JoseonKingdom, KoryoKingdom]
    advisors = [None]
    buildings_military = [KoreaTemple, KoreaQuarry, KoreaArcher, KoreaConfucianAcadamy]
    specials = [KoreaSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 2, Resource.STONE: 6, Resource.GOLD: 5})
    starting_points = 4
    starting_workers = 5

class MaliSaltCaravan(StartingBuilding):
    name = 'Salt Caravan'
    abbr = 'Ml_StCv'
    deployment_cost = -2
    production_per_worker = Resources({Resource.FOOD: 1, Resource.STABILITY: 1, Resource.BOOKS: 1})

class MaliQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'Ml_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class MaliGoldMine(StartingBuilding):
    name = 'Gold Mine'
    abbr = 'Ml_GdMn'
    max_workers = True
    production_per_worker = Resources({Resource.GOLD: 3})

class MaliFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'Ml_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class MaliSpecial(Special):
    """Growth: [Gold] bonus: +1 [Gold]; Golden Age bonus: 1"""
    name = 'Mali Special'
    abbr = 'Ml_S'
    golden_age_bonus = 1

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('extra growth resources', self.chose_gold, self.extra_gold)
        self.register_for_event('received extra growth resources', self.chose_gold, self.log_extra_gold)

    def chose_gold(self, player, **kwargs):
        return player is self.owner and kwargs['growth'][Resource.GOLD]

    def extra_gold(self, player, **kwargs):
        return 1

    def log_extra_gold(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains an extra 1 [Gold].')

class Mali(Nation):
    name = 'Mali'
    abbr = 'Ml'
    dynasties = [MaliEmpire, SonghaiEmpire]
    advisors = [None]
    buildings_military = [MaliSaltCaravan, MaliQuarry, MaliGoldMine, MaliFarm]
    specials = [MaliSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 3, Resource.STONE: 7, Resource.GOLD: 5})
    starting_points = 4
    starting_workers = 5

class MongoliaYurt(StartingBuilding):
    name = 'Yurt'
    abbr = 'Mg_Yrt'
    production_per_worker = Resources({Resource.FOOD: 1, Resource.GOLD: 1})

class MongoliaCaravan(StartingBuilding):
    name = 'Caravan'
    abbr = 'Mg_Crv'
    production_per_worker = Resources({Resource.STABILITY: 1, Resource.GOLD: 1})

class MongoliaHorseArcher(StartingMilitary):
    name = 'Horse Archer'
    abbr = 'Mg_HsAr'
    deployment_cost = -2
    worker_points = (1, 1, 2)
    raid_value = 4
    production_per_worker = Resources({Resource.MILITARY: 5, Resource.FOOD: -1})

class MongoliaSteppe(StartingBuilding):
    name = 'Steppe'
    abbr = 'Mg_Stp'
    deployment_cost = -0
    worker_points = ()
    max_workers = True
    production_per_worker = Resources()

class MongoliaSpecial(Special):
    """All: Defeats cost 2 same extra ([Food] / [Stone] / [Gold] / [Books])"""
    name = 'Mongolia Special'
    abbr = 'Mg_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('extra war penalty', self.true, self.two)
        self.global_effect = True

    def two(self, player, **kwargs):
        self.match.log(f'[{self}] Defeats cost 2 extra {self.match.war.penalty_resource}.')
        return 2

class Mongolia(Nation):
    name = 'Mongolia'
    abbr = 'Mg'
    dynasties = [GoldenHorde, YuanDynasty]
    advisors = [None]
    buildings_military = [MongoliaYurt, MongoliaCaravan, MongoliaHorseArcher, MongoliaSteppe]
    specials = [MongoliaSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(3, Resources({Resource.FOOD: -3})), WorkerPool(5, Resources({Resource.MILITARY: -3}))]
    starting_resources = Resources({Resource.FOOD: 3, Resource.STONE: 6, Resource.GOLD: 7})
    starting_points = 4
    starting_workers = 4

class PersiaQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'Ps_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class PersiaAxeman(StartingMilitary):
    name = 'Axeman'
    abbr = 'Ps_Axm'
    production_per_worker = Resources({Resource.MILITARY: 2, Resource.FOOD: -1})

class PersiaZiggurat(StartingBuilding):
    name = 'Ziggurat'
    abbr = 'Ps_Zgr'
    worker_points = (1, 1)
    production_per_worker = Resources({Resource.STABILITY: 2, Resource.STONE: 1})

class PersiaTemple(StartingBuilding):
    name = 'Temple'
    abbr = 'Ps_Tpl'
    production_per_worker = Resources({Resource.BOOKS: 1, Resource.GOLD: 1})

class Persia(Nation):
    name = 'Persia'
    abbr = 'Ps'
    dynasties = [AchaemenidEmpire, SassanidEmpire]
    advisors = [None]
    buildings_military = [PersiaQuarry, PersiaAxeman, PersiaZiggurat, PersiaTemple]
    specials = []
    colonies = [None, None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 3, Resource.STONE: 5, Resource.GOLD: 7})
    starting_points = 4
    starting_workers = 5

    def place_dynasty(self, player, card):
        for (i, slot) in enumerate(player.colonies):
            if slot is not None and slot.is_dynasty():
                player.remove(slot)
                player.colonies[i] = card
                break
        else:
            for (i, slot) in reversed(list(enumerate(player.colonies))):
                if slot is None:
                    player.colonies[i] = card
                    break
            else:
                slots = [f'C{i + 1}' for i in range(len(player.colonies))]
                slot = self.match.get_move(player, 'Replace which colony?', slots)
                (slot_type, index) = player.slot_type_index_from_slot(slot)
                old_card = player.slots_from_slot_type(slot_type)[index]
                player.remove(old_card)
                player.slots_from_slot_type(slot_type)[index] = card

class PolandTemple(StartingBuilding):
    name = 'Temple'
    abbr = 'Pl_Tpl'
    production_per_worker = Resources({Resource.BOOKS: 1, Resource.GOLD: 1})

class PolandForge(StartingBuilding):
    name = 'Forge'
    abbr = 'Pl_Frg'
    worker_points = (1, 1)
    production_per_worker = Resources({Resource.STONE: 2, Resource.FOOD: 1})

class PolandAxeman(StartingMilitary):
    name = 'Axeman'
    abbr = 'Pl_Axm'
    production_per_worker = Resources({Resource.MILITARY: 2, Resource.FOOD: -1})

class PolandQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'Pl_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class PolandSpecial(Special):
    """War: +3 [Books] if you are not defeated"""
    name = 'Poland Special'
    abbr = 'Pl_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('not defeated', self.owned, self.gain_books)

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 3 [Books].')
        player.resources[Resource.BOOKS] += 3

class Poland(Nation):
    name = 'Poland'
    abbr = 'Pl'
    dynasties = [JagellonianDynasty, PolishLithuanianCommonwealth]
    advisors = [None]
    buildings_military = [PolandTemple, PolandForge, PolandAxeman, PolandQuarry]
    specials = [PolandSpecial]
    colonies = [None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 3, Resource.STONE: 5, Resource.GOLD: 5})
    starting_points = 3
    starting_workers = 5

class PortugalTemple(StartingBuilding):
    name = 'Temple'
    abbr = 'Pg_Tpl'
    production_per_worker = Resources({Resource.BOOKS: 1, Resource.GOLD: 1})

class PortugalLighthouse(StartingBuilding):
    name = 'Lighthouse'
    abbr = 'Pg_Lth'
    worker_points = (1, 1)
    production_per_worker = Resources({Resource.GOLD: 2, Resource.STONE: 1})

class PortugalCaravan(StartingBuilding):
    name = 'Caravan'
    abbr = 'Pg_Crv'
    production_per_worker = Resources({Resource.STABILITY: 1, Resource.GOLD: 1})

class PortugalFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'Pg_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class PortugalSpecial(Special):
    """Buy Progress card: Row 3 cost 1 [Gold] less"""
    name = 'Portugal Special'
    abbr = 'Pg_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('card discount', self.row_3, self.card_discount)

    def row_3(self, player, **kwargs):
        return player is self.owner and kwargs['row'] == 3

    def card_discount(self, player, **kwargs):
        self.match.log(f'[{self}] {player} pays 1 [Gold] less for cards from row 3.')
        return 1

class Portugal(Nation):
    name = 'Portugal'
    abbr = 'Pg'
    dynasties = [KingdomOfLeon, PortugeseEmpire]
    advisors = [None]
    buildings_military = [PortugalTemple, PortugalLighthouse, PortugalCaravan, PortugalFarm]
    specials = [PortugalSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 2, Resource.STONE: 6, Resource.GOLD: 5})
    starting_points = 2
    starting_workers = 5

class RomeFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'R_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class RomeQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'R_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class RomeLegionary(StartingMilitary):
    name = 'Legionary'
    abbr = 'R_Lgn'
    worker_points = (1, 1)
    raid_value = 3
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.FOOD: -1})

class RomeAqueduct(StartingBuilding):
    name = 'Aqueduct'
    abbr = 'R_Aqd'
    worker_points = (1, 1)
    production_per_worker = Resources({Resource.FOOD: 2, Resource.STABILITY: 1})

class RomeSpecial(Special):
    name = 'Rome Special'
    abbr = 'R_S'
    production_value = Resources({Resource.MILITARY: 2})

class Rome(Nation):
    name = 'Rome'
    abbr = 'R'
    dynasties = [RomanEmpire, RomanRepublic]
    advisors = [None]
    buildings_military = [RomeFarm, RomeQuarry, RomeLegionary, RomeAqueduct]
    specials = [RomeSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 2, Resource.STONE: 6, Resource.GOLD: 6})
    starting_points = 4
    starting_workers = 5

class VeniceGlassBlower(StartingBuilding):
    name = 'Glass Blower'
    abbr = 'Vn_GlBw'
    production_per_worker = Resources({Resource.BOOKS: 2})

class VeniceQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'Vn_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class VeniceTrireme(StartingMilitary):
    name = 'Trireme'
    abbr = 'Vn_Trm'
    deployment_cost = -2
    worker_points = (1, 1)
    raid_value = 3
    production_per_worker = Resources({Resource.MILITARY: 3})

class VeniceFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'Vn_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class VeniceSpecial(Special):
    """Pass last: +2 [Books]"""
    name = 'Venice Special'
    abbr = 'Vn_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('pass', self.passed_last, self.gain_books)

    def passed_last(self, player, **kwargs):
        return player is self.owner and player.passed_last

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Books].')
        player.resources[Resource.BOOKS] += 2

class VeniceConstantinople(StartingColony):
    """Buy Golden Age: [Point] cost 1 less"""
    name = 'Constantinople'
    abbr = 'Vn_Ctn'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('golden age discount', self.owned, self.golden_age_discount)

    def golden_age_discount(self, player, **kwargs):
        self.match.log(f'[{self}] {player} pays 1 less resource for a point.')
        return 1

class Venice(Nation):
    name = 'Venice'
    abbr = 'Vn'
    dynasties = [DomainsOfTheSea, PactumWarmundi]
    advisors = [None]
    buildings_military = [VeniceGlassBlower, VeniceQuarry, VeniceTrireme, VeniceFarm]
    specials = [VeniceSpecial]
    colonies = [None, VeniceConstantinople]
    wonders_under_construction = [None]
    wonders = [None, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 3, Resource.STONE: 6, Resource.GOLD: 6})
    starting_points = 5
    starting_workers = 5

class VikingsStaveChurch(StartingBuilding):
    name = 'Stave Church'
    abbr = 'Vk_StCh'
    production_per_worker = Resources({Resource.STABILITY: 1, Resource.BOOKS: 1})

class VikingsQuarry(StartingBuilding):
    name = 'Quarry'
    abbr = 'Vk_Qry'
    production_per_worker = Resources({Resource.STONE: 1, Resource.GOLD: 1})

class VikingsBerserkers(StartingMilitary):
    name = 'Berserkers'
    abbr = 'Vk_Bsk'
    raid_value = 3
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.FOOD: -2})

class VikingsFarm(StartingBuilding):
    name = 'Farm'
    abbr = 'Vk_Frm'
    production_per_worker = Resources({Resource.STONE: 1, Resource.FOOD: 1})

class VikingsSpecial(Special):
    """After production: Choose 1 ([Food] [Stone] [Gold] [Books]): Others lose 1 of that resource"""
    name = 'Vikings Special'
    abbr = 'Vk_S'

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('after production', self.owned, self.raze)
        self.global_effect = True

    def raze(self, player, **kwargs):
        options = (Resources({Resource.FOOD: 1}), Resources({Resource.STONE: 1}), Resources({Resource.GOLD: 1}), Resources({Resource.BOOKS: 1}))
        loss = self.match.get_move(player, 'Others lose which resource?', options)
        self.match.log(f'[{self}] {player} chose for other nations to lose {loss}.')
        self.match.get_move(player, 'Confirm?', ('Confirm',))
        for other_player in self.match.players[::-1]:
            if other_player is not player:
                other_player.lose_resources(-loss)

class VikingsOldUppsala(StartingWonder):
    """Action, 1 per round: -1 [Food] +3 [Military] this round"""
    name = 'Old Uppsala'
    abbr = 'Vk_OlUp'
    points = -2

    def assign_owner(self, player):
        super().assign_owner(player)
        self.register_for_event('when removed', self.is_self_with_marker, self.reduce_military)
        self.register_for_event('end of round', self.has_marker, self.reduce_military)

    def action_available(self, player):
        return player is self.owner and self.markers < 1 and player.resources[Resource.FOOD] >= 1

    def activate(self, player):
        self.markers += 1
        self.match.log(f'[{self}] {player} pays 1 [Food] and gains 3 [Military] this round.')
        player.resources[Resource.FOOD] -= 1
        player.resources[Resource.MILITARY] += 3

    def is_self_with_marker(self, player, **kwargs):
        return player is self.owner and kwargs['card'] is self and self.markers

    def has_marker(self, player, **kwargs):
        return player is self.owner and self.markers

    def reduce_military(self, player, **kwargs):
        self.match.log(f'[{self}] {player} loses 3 [Military].')
        player.resources[Resource.MILITARY] -= 3

class Vikings(Nation):
    name = 'Vikings'
    abbr = 'Vk'
    dynasties = [Normans, Varangians]
    advisors = [None]
    buildings_military = [VikingsStaveChurch, VikingsQuarry, VikingsBerserkers, VikingsFarm]
    specials = [VikingsSpecial]
    colonies = [None, None]
    wonders_under_construction = [None]
    wonders = [VikingsOldUppsala, None, None, None, None]
    worker_pools = [WorkerPool(4, Resources({Resource.FOOD: -3})), WorkerPool(4, Resources({Resource.STABILITY: -3}))]
    starting_resources = Resources({Resource.FOOD: 2, Resource.STONE: 5, Resource.GOLD: 6})
    starting_points = 3
    starting_workers = 5

all_nations = []
subclasses = [Nation]
while subclasses:
    next_subclasses = []
    for cls in subclasses:
        if cls.__subclasses__():
            next_subclasses.extend(cls.__subclasses__())
        elif cls not in all_nations:
            all_nations.append(cls)
    subclasses = next_subclasses

def sort_key(nation):
    return nation.name

all_nations.sort(key=sort_key)
all_nation_cards = []
for nation in all_nations:
    for card in (nation.dynasties + nation.advisors + nation.buildings_military + nation.specials + nation.colonies + nation.wonders):
        if card is not None:
            all_nation_cards.append(card)
nation_card_abbrs = {card.abbr: card.name for card in all_nation_cards}
nation_card_abbrs['K_S_Nerf'] = 'Korea Special'
