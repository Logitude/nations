from .exceptions import *
from .cards import *
from .resources import *
from .phases import *
from .actions import *

def s_if_not_1(value):
    return 's' if value != 1 else ''

class ProgressCard(Card):
    card_type = CardType.PROGRESS

    def buy(self):
        pass

class ExtensionCard(Card):
    card_type = CardType.EXTENSION

class BuildingMilitary(ProgressCard):
    max_workers = False

    def reset(self):
        super().reset()
        self.deployed_workers = 0

    def state(self):
        s = super().state()
        if self.deployed_workers:
            s['deployed'] = self.deployed_workers
        return s

class Building(BuildingMilitary):
    progress_card_type = ProgressCardType.BUILDING

    def deploy(self):
        if self.max_workers and self.deployed_workers >= len(self.worker_points):
            raise InvalidMove(f'"{self}" already has the maximum number of [Workers].')
        self.deployed_workers += 1
        self.owner.resources += self.production_per_worker.immediate()

    def undeploy(self):
        self.deployed_workers -= 1
        self.owner.resources -= self.production_per_worker.immediate()

    def produce(self, projected=False):
        return self.deployed_workers * self.production_per_worker.production()

class Military(BuildingMilitary):
    progress_card_type = ProgressCardType.MILITARY

    def deploy(self):
        if self.max_workers and self.deployed_workers >= len(self.worker_points):
            raise InvalidMove(f'"{self}" already has the maximum number of [Workers].')
        self.deployed_workers += 1
        if any(self.match.events['no military upkeep'].happen(self.owner)):
            self.owner.resources += self.production_per_worker.immediate().positive()
        else:
            self.owner.resources += self.production_per_worker.immediate()

    def undeploy(self):
        self.deployed_workers -= 1
        if any(self.match.events['no military upkeep'].happen(self.owner)):
            self.owner.resources -= self.production_per_worker.immediate().positive()
        else:
            self.owner.resources -= self.production_per_worker.immediate()

    def produce(self, projected=False):
        production = self.deployed_workers * self.production_per_worker.production()
        if any(self.match.events['no military upkeep'].happen(self.owner)):
            return production.positive()
        return production

class Colony(ProgressCard):
    progress_card_type = ProgressCardType.COLONY

class War(ProgressCard):
    progress_card_type = ProgressCardType.WAR

class Battle(ProgressCard):
    progress_card_type = ProgressCardType.BATTLE

class Wonder(ProgressCard):
    progress_card_type = ProgressCardType.WONDER

    def reset(self):
        super().reset()
        self.completed_stages = 0

    def ready(self):
        pass

    def state(self):
        s = super().state()
        if self.completed_stages:
            s['architects'] = self.completed_stages
        return s

class Advisor(ProgressCard):
    progress_card_type = ProgressCardType.ADVISOR

class GoldenAge(ProgressCard):
    progress_card_type = ProgressCardType.GOLDEN_AGE
    offers_special_action = False
    offers_books = False
    offers_stone = False

class NaturalWonder(ProgressCard):
    progress_card_type = ProgressCardType.NATURAL_WONDER

    def reset(self):
        super().reset()
        self.turns_explored = 0

    def buying(self):
        pass

    def discovered(self):
        pass

    def state(self):
        s = super().state()
        s['exploration_turns'] = self.exploration_turns
        if self.turns_explored:
            s['explored'] = self.turns_explored
        return s

class Age1Building(Building):
    age = 1
    deployment_cost = -1
    worker_points = (1, 1)

class Aqueduct(Age1Building):
    name = 'Aqueduct'
    abbr = 'Aqd'
    production_per_worker = Resources({Resource.FOOD: 2, Resource.STABILITY: 1})

class Brewery(Age1Building):
    name = 'Brewery'
    abbr = 'Brw'
    production_per_worker = Resources({Resource.FOOD: 2, Resource.BOOKS: 1})

class CityWall(Age1Building):
    name = 'City Wall'
    abbr = 'CtWl'
    production_per_worker = Resources({Resource.STONE: 2, Resource.STABILITY: 1})

class ConfucianAcademy(Age1Building):
    name = 'Confucian Academy'
    abbr = 'CfAc'
    production_per_worker = Resources({Resource.STABILITY: 2, Resource.GOLD: 1})

class Forge(Age1Building):
    name = 'Forge'
    abbr = 'Frg'
    production_per_worker = Resources({Resource.STONE: 2, Resource.FOOD: 1})

class Forum(Age1Building):
    name = 'Forum'
    abbr = 'Frm'
    production_per_worker = Resources({Resource.GOLD: 2, Resource.FOOD: 1})

class Granary(Age1Building):
    name = 'Granary'
    abbr = 'Grn'
    production_per_worker = Resources({Resource.FOOD: 2, Resource.STONE: 1})

class Library(Age1Building):
    name = 'Library'
    abbr = 'Lib'
    production_per_worker = Resources({Resource.BOOKS: 2, Resource.GOLD: 1})

class Lighthouse(Age1Building):
    name = 'Lighthouse'
    abbr = 'Lth'
    production_per_worker = Resources({Resource.GOLD: 2, Resource.STONE: 1})

class Lyceum(Age1Building):
    name = 'Lyceum'
    abbr = 'Lyc'
    production_per_worker = Resources({Resource.BOOKS: 2, Resource.STONE: 1})

class Mine(Age1Building):
    name = 'Mine'
    abbr = 'Min'
    production_per_worker = Resources({Resource.STONE: 2, Resource.GOLD: 1})

class Pagoda(Age1Building):
    name = 'Pagoda'
    abbr = 'Pgd'
    production_per_worker = Resources({Resource.BOOKS: 2, Resource.STABILITY: 1})

class SilkRoad(Age1Building):
    name = 'Silk Road'
    abbr = 'SkRd'
    deployment_cost = -2
    worker_points = (3,)
    max_workers = True
    production_per_worker = Resources({Resource.GOLD: 5, Resource.STONE: -1})

class Synagogue(Age1Building):
    name = 'Synagogue'
    abbr = 'Sng'
    production_per_worker = Resources({Resource.GOLD: 2, Resource.BOOKS: 1})

class Vatican(Age1Building):
    name = 'Vatican'
    abbr = 'Vtc'
    deployment_cost = -2
    worker_points = (2,)
    max_workers = True
    production_per_worker = Resources({Resource.BOOKS: 3, Resource.GOLD: 1})

class Ziggurat(Age1Building):
    name = 'Ziggurat'
    abbr = 'Zgr'
    production_per_worker = Resources({Resource.STABILITY: 2, Resource.STONE: 1})

class Age2Building(Building):
    age = 2
    deployment_cost = -2
    worker_points = (1, 1, 1)

class BallCourt(Age2Building):
    name = 'Ball Court'
    abbr = 'BlCt'
    production_per_worker = Resources({Resource.GOLD: 3, Resource.FOOD: 1})

class Castle(Age2Building):
    name = 'Castle'
    abbr = 'Cas'
    production_per_worker = Resources({Resource.STABILITY: 3, Resource.STONE: 1})

class Cathedral(Age2Building):
    name = 'Cathedral'
    abbr = 'Cat'
    production_per_worker = Resources({Resource.STONE: 2, Resource.STABILITY: 2})

class GuildHall(Age2Building):
    name = 'Guild Hall'
    abbr = 'GdHl'
    production_per_worker = Resources({Resource.STONE: 3, Resource.BOOKS: 1})

class Hansa(Age2Building):
    name = 'Hansa'
    abbr = 'Han'
    deployment_cost = -4
    worker_points = (2, 2)
    max_workers = True
    production_per_worker = Resources({Resource.FOOD: 4, Resource.STABILITY: 1})

class Hippodrome(Age2Building):
    name = 'Hippodrome'
    abbr = 'Hip'
    production_per_worker = Resources({Resource.STABILITY: 3, Resource.BOOKS: 1})

class KnightsTemplar(Age2Building):
    name = 'Knights Templar'
    abbr = 'KnTp'
    worker_points = (2,)
    max_workers = True
    production_per_worker = Resources({Resource.STONE: 2, Resource.MILITARY: 4})

class Madrasa(Age2Building):
    name = 'Madrasa'
    abbr = 'Mdr'
    production_per_worker = Resources({Resource.BOOKS: 2, Resource.GOLD: 2})

class Market(Age2Building):
    name = 'Market'
    abbr = 'Mkt'
    production_per_worker = Resources({Resource.GOLD: 2, Resource.FOOD: 2})

class Mint(Age2Building):
    name = 'Mint'
    abbr = 'Mnt'
    production_per_worker = Resources({Resource.GOLD: 3, Resource.STABILITY: 1})

class Monastery(Age2Building):
    name = 'Monastery'
    abbr = 'Mon'
    production_per_worker = Resources({Resource.BOOKS: 3, Resource.FOOD: 1})

class Mosque(Age2Building):
    name = 'Mosque'
    abbr = 'Msq'
    production_per_worker = Resources({Resource.GOLD: 2, Resource.STABILITY: 2})

class OceanFishing(Age2Building):
    name = 'Ocean Fishing'
    abbr = 'OcFs'
    production_per_worker = Resources({Resource.FOOD: 2, Resource.STONE: 2})

class University(Age2Building):
    name = 'University'
    abbr = 'Uni'
    production_per_worker = Resources({Resource.STONE: 2, Resource.BOOKS: 2})

class Watermill(Age2Building):
    name = 'Watermill'
    abbr = 'Wtm'
    production_per_worker = Resources({Resource.STONE: 3, Resource.FOOD: 1})

class Windmill(Age2Building):
    name = 'Windmill'
    abbr = 'Wdm'
    production_per_worker = Resources({Resource.FOOD: 3, Resource.GOLD: 1})

class Age3Building(Building):
    age = 3
    deployment_cost = -3
    worker_points = (2, 1, 1)

class Bank(Age3Building):
    name = 'Bank'
    abbr = 'Bnk'
    production_per_worker = Resources({Resource.GOLD: 3, Resource.BOOKS: 2})

class Chateau(Age3Building):
    name = 'Chateau'
    abbr = 'Cht'
    production_per_worker = Resources({Resource.STABILITY: 3, Resource.GOLD: 2})

class CoffeeHouse(Age3Building):
    """Pass last: +2 [Books] per [Worker] on Coffee House"""
    name = 'Coffee House'
    abbr = 'CfHs'
    worker_points = (2, 1, 1, 2)
    production_per_worker = Resources({Resource.FOOD: 2, Resource.GOLD: 2})

    def buy(self):
        self.register_for_event('pass', self.passed_last, self.gain_books)

    def passed_last(self, player, **kwargs):
        return player is self.owner and player.passed_last

    def gain_books(self, player, **kwargs):
        books = 2 * self.deployed_workers
        self.match.log(f'[{self}] {player} will produce an extra {books} [Books].')

    def produce(self, projected=False):
        production = self.deployed_workers * self.production_per_worker.production()
        if self.owner.passed_last:
            production += self.deployed_workers * Resources({Resource.BOOKS: 2})
        return production

class ColonialTrading(Age3Building):
    name = 'Colonial Trading'
    abbr = 'ClTr'
    production_per_worker = Resources({Resource.GOLD: 3, Resource.STABILITY: 2})

class Courthouse(Age3Building):
    name = 'Courthouse'
    abbr = 'Cth'
    production_per_worker = Resources({Resource.STABILITY: 3, Resource.BOOKS: 2})

class Dike(Age3Building):
    name = 'Dike'
    abbr = 'Dik'
    production_per_worker = Resources({Resource.STONE: 3, Resource.FOOD: 2})

class Hammam(Age3Building):
    name = 'Hammam'
    abbr = 'Hmm'
    production_per_worker = Resources({Resource.FOOD: 3, Resource.STABILITY: 2})

class Observatory(Age3Building):
    name = 'Observatory'
    abbr = 'Obs'
    production_per_worker = Resources({Resource.BOOKS: 3, Resource.STONE: 2})

class Parliament(Age3Building):
    name = 'Parliament'
    abbr = 'Plm'
    production_per_worker = Resources({Resource.STONE: 3, Resource.STABILITY: 2})

class Potosi(Age3Building):
    name = 'Potosi'
    abbr = 'Pts'
    worker_points = (1,)
    max_workers = True
    production_per_worker = Resources({Resource.GOLD: 7})

class PrintingPress(Age3Building):
    name = 'Printing Press'
    abbr = 'PrPr'
    production_per_worker = Resources({Resource.STONE: 3, Resource.BOOKS: 2})

class SacrificialAltar(Age3Building):
    name = 'Sacrificial Altar'
    abbr = 'ScAl'
    production_per_worker = Resources({Resource.STABILITY: 3, Resource.FOOD: 2})

class Sawmill(Age3Building):
    name = 'Sawmill'
    abbr = 'Swm'
    production_per_worker = Resources({Resource.GOLD: 3, Resource.FOOD: 2})

class Shipyard(Age3Building):
    name = 'Shipyard'
    abbr = 'Shp'
    production_per_worker = Resources({Resource.STONE: 3, Resource.GOLD: 2})

class TerraceFarming(Age3Building):
    name = 'Terrace Farming'
    abbr = 'TrFm'
    production_per_worker = Resources({Resource.FOOD: 3, Resource.STONE: 2})

class Theatre(Age3Building):
    name = 'Theatre'
    abbr = 'Thr'
    production_per_worker = Resources({Resource.BOOKS: 3, Resource.GOLD: 2})

class Age4Building(Building):
    age = 4
    deployment_cost = -4
    worker_points = (2, 2, 1)

class CoalMine(Age4Building):
    name = 'Coal Mine'
    abbr = 'ClMn'
    production_per_worker = Resources({Resource.STONE: 4, Resource.GOLD: 2})

class DepartmentStore(Age4Building):
    name = 'Department Store'
    abbr = 'DpSr'
    deployment_cost = -6
    worker_points = (4,)
    max_workers = True
    production_per_worker = Resources({Resource.GOLD: 3, Resource.BOOKS: 1})

class EngineeringSchool(Age4Building):
    name = 'Engineering School'
    abbr = 'EgSl'
    production_per_worker = Resources({Resource.STONE: 4, Resource.BOOKS: 2})

class Factory(Age4Building):
    name = 'Factory'
    abbr = 'Fct'
    production_per_worker = Resources({Resource.GOLD: 3, Resource.STONE: 3})

class Hospital(Age4Building):
    name = 'Hospital'
    abbr = 'Hsp'
    production_per_worker = Resources({Resource.BOOKS: 4, Resource.FOOD: 2})

class HydroPlant(Age4Building):
    name = 'Hydro Plant'
    abbr = 'HdPl'
    production_per_worker = Resources({Resource.FOOD: 3, Resource.GOLD: 3})

class NationalPark(Age4Building):
    name = 'National Park'
    abbr = 'NtPk'
    production_per_worker = Resources({Resource.BOOKS: 4, Resource.STONE: 2})

class PenalColony(Age4Building):
    name = 'Penal Colony'
    abbr = 'PnCl'
    production_per_worker = Resources({Resource.FOOD: 4, Resource.STABILITY: 2})

class Radio(Age4Building):
    name = 'Radio'
    abbr = 'Rad'
    production_per_worker = Resources({Resource.STABILITY: 4, Resource.GOLD: 2})

class Railroad(Age4Building):
    name = 'Railroad'
    abbr = 'Rlr'
    production_per_worker = Resources({Resource.STONE: 3, Resource.STABILITY: 3})

class SewerSystem(Age4Building):
    name = 'Sewer System'
    abbr = 'SwSt'
    production_per_worker = Resources({Resource.FOOD: 4, Resource.STABILITY: 2})

class Shantytown(Age4Building):
    name = 'Shantytown'
    abbr = 'Stt'
    deployment_cost = -1
    worker_points = (1, 1, 1, 1)
    production_per_worker = Resources({Resource.STONE: 7, Resource.STABILITY: -1})

class StockExchange(Age4Building):
    name = 'Stock Exchange'
    abbr = 'SkEx'
    production_per_worker = Resources({Resource.GOLD: 4, Resource.STONE: 2})

class UrbanCenter(Age4Building):
    name = 'Urban Center'
    abbr = 'UbCt'
    production_per_worker = Resources({Resource.GOLD: 3, Resource.STABILITY: 3})

class Voortrekker(Age4Building):
    name = 'Voortrekker'
    abbr = 'Vtk'
    production_per_worker = Resources({Resource.FOOD: 3, Resource.STONE: 3})

class Zeppelin(Age4Building):
    name = 'Zeppelin'
    abbr = 'Zpl'
    production_per_worker = Resources({Resource.BOOKS: 4, Resource.STABILITY: 2})

class Age1Military(Military):
    age = 1
    deployment_cost = -1
    worker_points = (1, 1)
    raid_value = 3

class Archer(Age1Military):
    name = 'Archer'
    abbr = 'Arc'
    raid_value = 4
    production_per_worker = Resources({Resource.MILITARY: 2})

class Chariot(Age1Military):
    name = 'Chariot'
    abbr = 'Crt'
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.GOLD: -1})

class Elephant(Age1Military):
    name = 'Elephant'
    abbr = 'Elp'
    production_per_worker = Resources({Resource.MILITARY: 4, Resource.FOOD: -2})

class Hoplite(Age1Military):
    name = 'Hoplite'
    abbr = 'Hpl'
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.STONE: -1})

class Immortal(Age1Military):
    name = 'Immortal'
    abbr = 'Imt'
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.STABILITY: -1})

class Legionary(Age1Military):
    name = 'Legionary'
    abbr = 'Lgn'
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.FOOD: -1})

class Phalanx(Age1Military):
    name = 'Phalanx'
    abbr = 'Plx'
    production_per_worker = Resources({Resource.MILITARY: 4, Resource.STONE: -2})

class PraetorianGuard(Age1Military):
    name = 'Praetorian Guard'
    abbr = 'PtGd'
    worker_points = (2,)
    max_workers = True
    production_per_worker = Resources({Resource.MILITARY: 3, Resource.STABILITY: 1})

class Trireme(Age1Military):
    name = 'Trireme'
    abbr = 'Trm'
    deployment_cost = -2
    production_per_worker = Resources({Resource.MILITARY: 3})

class Age2Military(Military):
    age = 2
    deployment_cost = -2
    worker_points = (1, 1, 2)
    raid_value = 4

class Assassin(Age2Military):
    """Buy battle: Others: Choose -3 [Food] or remove Advisor"""
    name = 'Assassin'
    abbr = 'Ass'
    deployment_cost = -1
    worker_points = (2,)
    raid_value = 5
    production_per_worker = Resources()

    def state(self):
        s = super().state()
        if self.deployed_workers:
            s['global'] = 1
        return s

    def buy(self):
        self.register_for_event('after bought card', self.bought_battle, self.assassinate)

    def bought_battle(self, player, **kwargs):
        return player is self.owner and self.deployed_workers and kwargs['card'].is_battle()

    def assassinate(self, player, **kwargs):
        need_other_player_choice = False
        player_has_advisor = {}
        for player in self.match.players[::-1]:
            if player is not self.owner:
                has_advisor = False
                if player.removable_advisor_cards():
                    has_advisor = True
                player_has_advisor[player.name] = has_advisor
                has_3_food = player.resources[Resource.FOOD] >= 3
                if has_advisor and has_3_food:
                    need_other_player_choice = True
                elif not has_advisor and not has_3_food:
                    if player.losing_resources_needs_choice(Resources({Resource.FOOD: -3})):
                        need_other_player_choice = True
        if need_other_player_choice:
            options = [ConfirmAction()]
            if self.owner.remaining_main_actions <= 1:
                options.append(ConfirmCompleteAction())
            choice = self.match.get_move(self.owner, 'Confirm buying battle before another player makes a choice?', tuple(options))
            self.owner.need_confirmation = choice.action_type is not ActionType.CONFIRM_AND_COMPLETE_TURN
        for player in self.match.players[::-1]:
            if player is not self.owner:
                has_advisor = player_has_advisor[player.name]
                has_3_food = player.resources[Resource.FOOD] >= 3
                remove_advisors = False
                if has_advisor and not has_3_food:
                    remove_advisors = True
                elif not has_advisor:
                    remove_advisors = False
                else:
                    choice = self.match.get_move(player, 'Lose 3 [Food] or remove advisors?', ('-3 [Food]', 'remove advisors'))
                    if choice == 'remove advisors':
                        remove_advisors = True
                if remove_advisors:
                    self.match.log(f'[{self}] {player} removes advisors.')
                    player.remove_all_advisors()
                else:
                    self.match.log(f'[{self}] {player} loses 3 [Food].')
                    player.lose_resources(Resources({Resource.FOOD: -3}))
                if player.need_confirmation:
                    self.match.get_move(player, 'Confirm?', ('Confirm',))

class CamelArcher(Age2Military):
    name = 'Camel Archer'
    abbr = 'CmAr'
    production_per_worker = Resources({Resource.MILITARY: 5, Resource.STABILITY: -1})

class Cataphract(Age2Military):
    name = 'Cataphract'
    abbr = 'Ctp'
    production_per_worker = Resources({Resource.MILITARY: 6, Resource.STONE: -2})

class ChoKoNu(Age2Military):
    name = 'Cho-Ko-Nu'
    abbr = 'CKN'
    production_per_worker = Resources({Resource.MILITARY: 5, Resource.GOLD: -1})

class GreekFireGalley(Age2Military):
    name = 'Greek Fire Galley'
    abbr = 'GFG'
    production_per_worker = Resources({Resource.MILITARY: 6, Resource.FOOD: -2})

class HorseArcher(Age2Military):
    name = 'Horse Archer'
    abbr = 'HsAr'
    production_per_worker = Resources({Resource.MILITARY: 5, Resource.FOOD: -1})

class Knight(Age2Military):
    name = 'Knight'
    abbr = 'Knt'
    production_per_worker = Resources({Resource.MILITARY: 5, Resource.STONE: -1})

class Longbowman(Age2Military):
    name = 'Longbowman'
    abbr = 'Lbm'
    production_per_worker = Resources({Resource.MILITARY: 4})

class Longships(Age2Military):
    name = 'Longships'
    abbr = 'Lsp'
    production_per_worker = Resources({Resource.MILITARY: 5, Resource.BOOKS: -1})

class Age3Military(Military):
    age = 3
    deployment_cost = -3
    worker_points = (1, 2, 2)
    raid_value = 5

class Conquistador(Age3Military):
    name = 'Conquistador'
    abbr = 'Cqd'
    production_per_worker = Resources({Resource.MILITARY: 7, Resource.BOOKS: -1})

class Frigate(Age3Military):
    name = 'Frigate'
    abbr = 'Fgt'
    deployment_cost = -4
    raid_value = 6
    production_per_worker = Resources({Resource.MILITARY: 8, Resource.STONE: -1})

class Hakkapeliitta(Age3Military):
    name = 'Hakkapeliitta'
    abbr = 'Hkp'
    production_per_worker = Resources({Resource.MILITARY: 8, Resource.STABILITY: -2})

class JaguarWarrior(Age3Military):
    name = 'Jaguar Warrior'
    abbr = 'JgWr'
    production_per_worker = Resources({Resource.MILITARY: 7, Resource.STABILITY: -1})

class Mercenary(Age3Military):
    name = 'Mercenary'
    abbr = 'Mcn'
    deployment_cost = -2
    raid_value = 4
    production_per_worker = Resources({Resource.MILITARY: 8, Resource.GOLD: -2})

class Privateer(Age3Military):
    name = 'Privateer'
    abbr = 'Pvt'
    deployment_cost = -2
    worker_points = (2, 2, 1)
    raid_value = 7
    production_per_worker = Resources({Resource.MILITARY: 4})

class Ranger(Age3Military):
    name = 'Ranger'
    abbr = 'Rng'
    production_per_worker = Resources({Resource.MILITARY: 6})

class Redcoat(Age3Military):
    name = 'Redcoat'
    abbr = 'Rdc'
    production_per_worker = Resources({Resource.MILITARY: 7, Resource.FOOD: -1})

class Samurai(Age3Military):
    name = 'Samurai'
    abbr = 'Smr'
    production_per_worker = Resources({Resource.MILITARY: 7, Resource.GOLD: -1})

class Age4Military(Military):
    age = 4
    deployment_cost = -4
    worker_points = (1, 2, 2, 2)
    raid_value = 6

class Boxers(Age4Military):
    name = 'Boxers'
    abbr = 'Bxr'
    deployment_cost = -1
    worker_points = (1, 1, 2, 2, 3)
    raid_value = 2
    production_per_worker = Resources({Resource.MILITARY: 6})

class Cavalry(Age4Military):
    name = 'Cavalry'
    abbr = 'Cvr'
    production_per_worker = Resources({Resource.MILITARY: 9, Resource.BOOKS: -1})

class Conscript(Age4Military):
    name = 'Conscript'
    abbr = 'Cns'
    deployment_cost = -2
    worker_points = (1, 1, 1, 1)
    raid_value = 4
    production_per_worker = Resources({Resource.MILITARY: 7})

class Cossack(Age4Military):
    name = 'Cossack'
    abbr = 'Csk'
    production_per_worker = Resources({Resource.MILITARY: 9, Resource.STABILITY: -1})

class Curassiers(Age4Military):
    name = 'Curassiers'
    abbr = 'Crs'
    production_per_worker = Resources({Resource.MILITARY: 9, Resource.GOLD: -1})

class Dreadnought(Age4Military):
    name = 'Dreadnought'
    abbr = 'Drn'
    deployment_cost = -6
    worker_points = (1, 2, 3)
    raid_value = 7
    production_per_worker = Resources({Resource.MILITARY: 14, Resource.STONE: -3})

class MachineGunner(Age4Military):
    name = 'Machine Gunner'
    abbr = 'McGn'
    production_per_worker = Resources({Resource.MILITARY: 10, Resource.GOLD: -2})

class Rifleman(Age4Military):
    name = 'Rifleman'
    abbr = 'Rfm'
    production_per_worker = Resources({Resource.MILITARY: 9, Resource.FOOD: -1})

class Submarine(Age4Military):
    name = 'Submarine'
    abbr = 'Sub'
    deployment_cost = -3
    raid_value = 5
    production_per_worker = Resources({Resource.MILITARY: 8})

class Age1Colony(Colony):
    age = 1
    points = 0

class Armenia(Age1Colony):
    name = 'Armenia'
    abbr = 'Arm'
    military_requirement = 6
    production_value = Resources({Resource.STONE: 2})

class Babylonia(Age1Colony):
    name = 'Babylonia'
    abbr = 'Bbl'
    military_requirement = 5
    production_value = Resources({Resource.GOLD: 2})

class Gaul(Age1Colony):
    name = 'Gaul'
    abbr = 'Gal'
    military_requirement = 7
    production_value = Resources({Resource.FOOD: 2})

class HinduKush(Age1Colony):
    name = 'Hindu Kush'
    abbr = 'HdKs'
    military_requirement = 9
    production_value = Resources({Resource.STONE: 3})

class Hispania(Age1Colony):
    name = 'Hispania'
    abbr = 'Hsn'
    military_requirement = 4
    production_value = Resources({Resource.FOOD: 2})

class Israel(Age1Colony):
    name = 'Israel'
    abbr = 'Isr'
    military_requirement = 5
    production_value = Resources({Resource.BOOKS: 2})

class Macedonia(Age1Colony):
    name = 'Macedonia'
    abbr = 'Mcd'
    military_requirement = 4
    production_value = Resources({Resource.MILITARY: 2})

class Nubia(Age1Colony):
    name = 'Nubia'
    abbr = 'Nub'
    military_requirement = 3
    production_value = Resources({Resource.GOLD: 2})

class Age2Colony(Colony):
    age = 2
    points = 1

class CrusaderStates(Age2Colony):
    name = 'Crusader States'
    abbr = 'CsSt'
    points = 2
    military_requirement = 13
    production_value = Resources({Resource.MILITARY: 3})

class England(Age2Colony):
    name = 'England'
    abbr = 'Eng'
    military_requirement = 11
    production_value = Resources({Resource.GOLD: 3})

class Greenland(Age2Colony):
    name = 'Greenland'
    abbr = 'Grl'
    military_requirement = 7
    production_value = Resources({Resource.FOOD: 3})

class Lombardy(Age2Colony):
    name = 'Lombardy'
    abbr = 'Lbd'
    military_requirement = 9
    production_value = Resources({Resource.BOOKS: 3})

class Prussia(Age2Colony):
    name = 'Prussia'
    abbr = 'Prs'
    military_requirement = 12
    production_value = Resources({Resource.BOOKS: 3})

class SaharanTrade(Age2Colony):
    name = 'Saharan Trade'
    abbr = 'ShTd'
    military_requirement = 15
    production_value = Resources({Resource.STONE: 4})

class Sicily(Age2Colony):
    name = 'Sicily'
    abbr = 'Scl'
    military_requirement = 12
    production_value = Resources({Resource.FOOD: 3})

class Tibet(Age2Colony):
    name = 'Tibet'
    abbr = 'Tbt'
    military_requirement = 8
    production_value = Resources({Resource.STABILITY: 3})

class Age3Colony(Colony):
    age = 3
    points = 1

class AztecEmpire(Age3Colony):
    name = 'Aztec Empire'
    abbr = 'AzEp'
    military_requirement = 15
    production_value = Resources({Resource.GOLD: 4})

class Brazil(Age3Colony):
    name = 'Brazil'
    abbr = 'Brz'
    military_requirement = 14
    production_value = Resources({Resource.STONE: 4})

class IncanEmpire(Age3Colony):
    name = 'Incan Empire'
    abbr = 'IcEp'
    military_requirement = 17
    production_value = Resources({Resource.GOLD: 4})

class Philippines(Age3Colony):
    name = 'Philippines'
    abbr = 'Plp'
    military_requirement = 18
    production_value = Resources({Resource.STONE: 4})

class Quebec(Age3Colony):
    name = 'Quebec'
    abbr = 'Qbc'
    military_requirement = 12
    production_value = Resources({Resource.BOOKS: 4})

class SouthAfrica(Age3Colony):
    name = 'South Africa'
    abbr = 'StAf'
    military_requirement = 13
    production_value = Resources({Resource.FOOD: 4})

class TheCaribbean(Age3Colony):
    name = 'The Caribbean'
    abbr = 'TCrb'
    military_requirement = 15
    production_value = Resources({Resource.STABILITY: 4})

class Virginia(Age3Colony):
    name = 'Virginia'
    abbr = 'Vgn'
    military_requirement = 21
    production_value = Resources({Resource.STONE: 5})

class Age4Colony(Colony):
    age = 4
    points = 2

class Algeria(Age4Colony):
    name = 'Algeria'
    abbr = 'Agr'
    military_requirement = 25
    production_value = Resources({Resource.MILITARY: 5})

class Australia(Age4Colony):
    name = 'Australia'
    abbr = 'Arl'
    military_requirement = 24
    production_value = Resources({Resource.STABILITY: 5})

class Congo(Age4Colony):
    name = 'Congo'
    abbr = 'Con'
    military_requirement = 23
    production_value = Resources({Resource.GOLD: 5})

class HongKong(Age4Colony):
    name = 'Hong Kong'
    abbr = 'HgKg'
    military_requirement = 27
    production_value = Resources({Resource.BOOKS: 5})

class India(Age4Colony):
    name = 'India'
    abbr = 'Ind'
    military_requirement = 25
    production_value = Resources({Resource.BOOKS: 5})

class Libya(Age4Colony):
    name = 'Libya'
    abbr = 'Lby'
    military_requirement = 30
    production_value = Resources({Resource.STONE: 6})

class Nigeria(Age4Colony):
    name = 'Nigeria'
    abbr = 'Ngr'
    military_requirement = 20
    production_value = Resources({Resource.BOOKS: 5})

class Ostafrika(Age4Colony):
    name = 'Ostafrika'
    abbr = 'Oak'
    military_requirement = 22
    production_value = Resources({Resource.FOOD: 5})

class Age1War(War):
    age = 1

class HunnicInvasions(Age1War):
    name = 'Hunnic Invasions'
    abbr = 'HncI'
    penalty_resource = Resource.FOOD
    penalty_amount = -4

class HyksosInvasion(Age1War):
    name = 'Hyksos Invasion'
    abbr = 'HksI'
    penalty_resource = Resource.STONE
    penalty_amount = -4

class ParthianWars(Age1War):
    name = 'Parthian Wars'
    abbr = 'PrtW'
    penalty_resource = Resource.GOLD
    penalty_amount = -3

class PelopponesianWar(Age1War):
    name = 'Pelopponesian War'
    abbr = 'PlpW'
    penalty_resource = Resource.BOOKS
    penalty_amount = -4

class PunicWars(Age1War):
    name = 'Punic Wars'
    abbr = 'PncW'
    penalty_resource = Resource.FOOD
    penalty_amount = -6

class ThreeKingdoms(Age1War):
    name = 'Three Kingdoms'
    abbr = 'ThKd'
    penalty_resource = Resource.GOLD
    penalty_amount = -5

class WarringStates(Age1War):
    name = 'Warring States'
    abbr = 'WSts'
    penalty_resource = Resource.BOOKS
    penalty_amount = -3

class WarsOfAlexander(Age1War):
    name = 'Wars of Alexander'
    abbr = 'WAlx'
    penalty_resource = Resource.FOOD
    penalty_amount = -2

class Age2War(War):
    age = 2

class ByzantineArabWar(Age2War):
    name = 'Byzantine-Arab War'
    abbr = 'BAW'
    penalty_resource = Resource.BOOKS
    penalty_amount = -3

class FirstCrusade(Age2War):
    name = 'First Crusade'
    abbr = 'FstC'
    penalty_resource = Resource.BOOKS
    penalty_amount = -6

class HundredYearsWar(Age2War):
    name = 'Hundred Years War'
    abbr = 'HYW'
    penalty_resource = Resource.FOOD
    penalty_amount = -5

class MongolInvasions(Age2War):
    name = 'Mongol Invasions'
    abbr = 'MngI'
    penalty_resource = Resource.FOOD
    penalty_amount = -10

class Reconquista(Age2War):
    name = 'Reconquista'
    abbr = 'Rcq'
    penalty_resource = Resource.GOLD
    penalty_amount = -4

class VandalicWar(Age2War):
    name = 'Vandalic War'
    abbr = 'VdlW'
    penalty_resource = Resource.STONE
    penalty_amount = -6

class VikingRaids(Age2War):
    name = 'Viking Raids'
    abbr = 'VkgR'
    penalty_resource = Resource.BOOKS
    penalty_amount = -4

class WarOfTheRoses(Age2War):
    name = 'War of the Roses'
    abbr = 'WRss'
    penalty_resource = Resource.GOLD
    penalty_amount = -7

class Age3War(War):
    age = 3

class CortesExpedition(Age3War):
    name = 'Cortes Expedition'
    abbr = 'CtEx'
    penalty_resource = Resource.FOOD
    penalty_amount = -6

class DutchLiberationWar(Age3War):
    name = 'Dutch Liberation War'
    abbr = 'DLW'
    penalty_resource = Resource.GOLD
    penalty_amount = -9

class GreatNorthernWar(Age3War):
    name = 'Great Northern War'
    abbr = 'GNW'
    penalty_resource = Resource.FOOD
    penalty_amount = -8

class ImjinWar(Age3War):
    name = 'Imjin War'
    abbr = 'ImjW'
    penalty_resource = Resource.STONE
    penalty_amount = -5

class MughalInvasion(Age3War):
    name = 'Mughal Invasion'
    abbr = 'MghI'
    penalty_resource = Resource.BOOKS
    penalty_amount = -7

class ThirtyYearsWar(Age3War):
    name = 'Thirty Years War'
    abbr = 'TYW'
    penalty_resource = Resource.FOOD
    penalty_amount = -9

class WarOfCyprus(Age3War):
    name = 'War of Cyprus'
    abbr = 'WCpr'
    penalty_resource = Resource.STONE
    penalty_amount = -7

class WarOfJenkinsEar(Age3War):
    name = 'War of Jenkins\' Ear'
    abbr = 'WJE'
    penalty_resource = Resource.GOLD
    penalty_amount = -6

class Age4War(War):
    age = 4

class AmericanCivilWar(Age4War):
    name = 'American Civil War'
    abbr = 'ACW'
    penalty_resource = Resource.BOOKS
    penalty_amount = -12

class AngloAfghanWar(Age4War):
    name = 'Anglo-Afghan War'
    abbr = 'AAW'
    penalty_resource = Resource.STONE
    penalty_amount = -7

class BalkanWars(Age4War):
    name = 'Balkan Wars'
    abbr = 'BknW'
    penalty_resource = Resource.BOOKS
    penalty_amount = -7

class CrimeanWar(Age4War):
    name = 'Crimean War'
    abbr = 'CmnW'
    penalty_resource = Resource.GOLD
    penalty_amount = -10

class FrancoPrussianWar(Age4War):
    name = 'Franco-Prussian War'
    abbr = 'FPW'
    penalty_resource = Resource.STONE
    penalty_amount = -9

class NapoleonicWar(Age4War):
    name = 'Napoleonic War'
    abbr = 'NplW'
    penalty_resource = Resource.FOOD
    penalty_amount = -11

class OpiumWar(Age4War):
    name = 'Opium War'
    abbr = 'OpmW'
    penalty_resource = Resource.GOLD
    penalty_amount = -8

class SecondBoerWar(Age4War):
    name = 'Second Boer War'
    abbr = 'SBW'
    penalty_resource = Resource.FOOD
    penalty_amount = -8

class Age1Battle(Battle):
    age = 1

class BattleOfCannae(Age1Battle):
    name = 'Battle of Cannae'
    abbr = 'BCnn'

class BattleOfIssus(Age1Battle):
    name = 'Battle of Issus'
    abbr = 'BIss'

class BattleOfKadesh(Age1Battle):
    name = 'Battle of Kadesh'
    abbr = 'BKds'

class BattleOfThermopylae(Age1Battle):
    name = 'Battle of Thermopylae'
    abbr = 'BTmp'

class CrossingTheAlps(Age1Battle):
    name = 'Crossing the Alps'
    abbr = 'CsAp'

class MilvianBridge(Age1Battle):
    name = 'Milvian Bridge'
    abbr = 'MvBr'

class SiegeOfAlesia(Age1Battle):
    name = 'Siege of Alesia'
    abbr = 'SAls'

class SiegeOfTroy(Age1Battle):
    name = 'Siege of Troy'
    abbr = 'STry'

class Age2Battle(Battle):
    age = 2

class BattleOfAgincourt(Age2Battle):
    name = 'Battle of Agincourt'
    abbr = 'BAgc'

class BattleOfAinJalut(Age2Battle):
    name = 'Battle of Ain Jalut'
    abbr = 'BAJ'

class BattleOfHastings(Age2Battle):
    name = 'Battle of Hastings'
    abbr = 'BHst'

class BattleOfManzikert(Age2Battle):
    name = 'Battle of Manzikert'
    abbr = 'BMzk'

class BattleOfPoitiers(Age2Battle):
    name = 'Battle of Poitiers'
    abbr = 'BPtr'

class BattleOfTannenberg(Age2Battle):
    name = 'Battle of Tannenberg'
    abbr = 'BTnb'

class SiegeOfConstantinople(Age2Battle):
    name = 'Siege of Constantinople'
    abbr = 'SCtn'

class TheHornsOfHattin(Age2Battle):
    name = 'The Horns of Hattin'
    abbr = 'THH'

class Age3Battle(Battle):
    age = 3

class BattleOfCajamarca(Age3Battle):
    name = 'Battle of Cajamarca'
    abbr = 'BCjm'

class BattleOfNoryang(Age3Battle):
    name = 'Battle of Noryang'
    abbr = 'BNry'

class BattleOfPoltava(Age3Battle):
    name = 'Battle of Poltava'
    abbr = 'BPtv'

class FallOfConstantinople(Age3Battle):
    name = 'Fall of Constantinople'
    abbr = 'FCtn'

class FallOfLouisburg(Age3Battle):
    name = 'Fall of Louisburg'
    abbr = 'FLsb'

class LaNocheTriste(Age3Battle):
    name = 'La Noche Triste'
    abbr = 'LNT'

class SiegeOfRhodes(Age3Battle):
    name = 'Siege of Rhodes'
    abbr = 'SRhd'

class SiegeOfVienna(Age3Battle):
    name = 'Siege of Vienna'
    abbr = 'SVnn'

class Age4Battle(Battle):
    age = 4

class BattleOfAusterlitz(Age4Battle):
    name = 'Battle of Austerlitz'
    abbr = 'BAtl'

class BattleOfBalaclava(Age4Battle):
    name = 'Battle of Balaclava'
    abbr = 'BBlc'

class BattleOfBorodino(Age4Battle):
    name = 'Battle of Borodino'
    abbr = 'BBrd'

class BattleOfTrafalgar(Age4Battle):
    name = 'Battle of Trafalgar'
    abbr = 'BTfg'

class BattleOfTsushima(Age4Battle):
    name = 'Battle of Tsushima'
    abbr = 'BTsm'

class BattleOfWaterloo(Age4Battle):
    name = 'Battle of Waterloo'
    abbr = 'BWtl'

class FashodaIncident(Age4Battle):
    name = 'Fashoda Incident'
    abbr = 'FsIn'

class SurrenderAtYorktown(Age4Battle):
    name = 'Surrender at Yorktown'
    abbr = 'SYkt'

class Age1Wonder(Wonder):
    age = 1

class Colosseum(Age1Wonder):
    """When ready: -2 [Food]"""
    name = 'Colosseum'
    abbr = 'Cls'
    points = 1
    stage_costs = (-2, -2)
    production_value = Resources({Resource.MILITARY: 3})

    def ready(self):
        self.match.log(f'[{self}] {self.owner} loses 2 [Food].')
        self.owner.lose_resources(Resources({Resource.FOOD: -2}))

class GreatLibrary(Age1Wonder):
    """Lost if least [Stability]"""
    name = 'Great Library'
    abbr = 'GrLr'
    points = 0
    stage_costs = (-1,)
    production_value = Resources({Resource.BOOKS: 2})
    golden_age_bonus = 1

    def placed(self):
        self.register_for_event('least stability', self.owned, self.remove)

    def remove(self, player, **kwargs):
        self.match.log(f'{player} removes "{self}".')
        player.remove(self)

class GreatLighthouse(Age1Wonder):
    """Buy card for 3 [Gold]: +1 [Book]"""
    name = 'Great Lighthouse'
    abbr = 'GrLh'
    points = 2
    stage_costs = (-1, -3)
    production_value = Resources({Resource.GOLD: 1})

    def ready(self):
        self.register_for_event('buy card for gold', self.payed_3_gold, self.gain_book)

    def payed_3_gold(self, player, **kwargs):
        return player is self.owner and kwargs['gold'] == 3

    def gain_book(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 1 [Book].')
        player.resources[Resource.BOOKS] += 1

class HangingGardens(Age1Wonder):
    name = 'Hanging Gardens'
    abbr = 'HgGd'
    points = 1
    stage_costs = (-1, -2)
    production_value = Resources({Resource.FOOD: 2, Resource.STONE: -1, Resource.STABILITY: 1})

class Petra(Age1Wonder):
    """Action, 1 per round: -1 [Food]: +3 [Books] / +3 [Gold] / +3 [Stone]"""
    name = 'Petra'
    abbr = 'Ptr'
    points = 0
    stage_costs = (-2, 0, -1)

    def action_available(self, player):
        return player is self.owner and self.markers < 1 and player.resources[Resource.FOOD] >= 1

    def activate(self, player):
        self.markers += 1
        options = (Resources({Resource.BOOKS: 3}), Resources({Resource.GOLD: 3}), Resources({Resource.STONE: 3}))
        choice = self.match.get_move(player, 'Pay 1 [Food] to get which resources?', options)
        self.match.log(f'[{self}] {player} pays 1 [Food] and gains {choice}.')
        player.resources[Resource.FOOD] -= 1
        player.resources += choice

class Pyramids(Age1Wonder):
    name = 'Pyramids'
    abbr = 'Prm'
    points = 3
    stage_costs = (-2, -1, 0)
    production_value = Resources({Resource.GOLD: 2, Resource.FOOD: -2})

class SolomonsTemple(Age1Wonder):
    """End of each age +1 [Point]; If defeated: Remove"""
    name = 'Solomon\'s Temple'
    abbr = 'SmTp'
    points = 0
    stage_costs = (-1, -1)

    def ready(self):
        self.register_for_event('end of age', self.owned, self.gain_point)
        self.register_for_event('defeated', self.owned, self.remove)

    def gain_point(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 1 [Point].')
        player.points += 1

    def remove(self, player, **kwargs):
        self.match.log(f'{player} removes "{self}".')
        player.remove(self)

class Sphinx(Age1Wonder):
    """New Wonder ready: +5 [Stone]"""
    name = 'Sphinx'
    abbr = 'Spx'
    points = 1
    stage_costs = (-2, -2)
    production_value = Resources({Resource.STONE: 1})

    def ready(self):
        self.register_for_event('wonder ready', self.owned, self.gain_stone)

    def gain_stone(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 5 [Stone].')
        player.resources[Resource.STONE] += 5

class Stonehenge(Age1Wonder):
    """When ready: +6 [Books] +4 [Food]"""
    name = 'Stonehenge'
    abbr = 'Sth'
    points = 0
    stage_costs = (-1, -1, -1)

    def ready(self):
        self.match.log(f'[{self}] {self.owner} gains 6 [Books] and 4 [Food].')
        self.owner.resources[Resource.BOOKS] += 6
        self.owner.resources[Resource.FOOD] += 4

class TerracottaArmy(Age1Wonder):
    """When ready: Least [Stability]: -4 [Gold]"""
    name = 'Terracotta Army'
    abbr = 'TcAm'
    points = 2
    stage_costs = (0, 0, -3)
    production_value = Resources({Resource.MILITARY: 1})

    def buy(self):
        self.global_effect = True

    def placed(self):
        least_stability = self.match.least_stability()
        need_other_player_choice = False
        for player in least_stability:
            if player is not self.owner:
                if player.losing_resources_needs_choice(Resources({Resource.GOLD: -4})):
                    need_other_player_choice = True
        complete_turn = False
        if need_other_player_choice:
            options = [ConfirmAction()]
            if self.owner.remaining_main_actions <= 1:
                options.append(ConfirmCompleteAction())
            choice = self.match.get_move(self.owner, f'Confirm placing "{self}" before another player makes a choice?', tuple(options))
            if choice.action_type is ActionType.CONFIRM_AND_COMPLETE_TURN:
                complete_turn = True
        for player in least_stability:
            self.match.log(f'[{self}] {player} loses 4 [Gold].')
            player.lose_resources(Resources({Resource.GOLD: -4}))
        self.owner.need_confirmation = not complete_turn
        self.global_effect = False

class TheOracle(Age1Wonder):
    name = 'The Oracle'
    abbr = 'Orc'
    points = 1
    stage_costs = (-2, -1)
    production_value = Resources({Resource.STABILITY: 2})

class Age2Wonder(Wonder):
    age = 2

class Alhambra(Age2Wonder):
    """1 private [Architect] per round"""
    name = 'Alhambra'
    abbr = 'Ahb'
    points = 1
    stage_costs = (-1, -1)
    private_architects = 1

    def buy(self):
        self.private_architects_available = 0

    def placed(self):
        self.private_architects_available = self.private_architects

class AngkorWat(Age2Wonder):
    """Production: If least [Military]: -4 [Books]"""
    name = 'Angkor Wat'
    abbr = 'AkWt'
    points = 1
    stage_costs = (-3, -1)
    production_value = Resources({Resource.FOOD: 4})

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.least_military:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces 4 fewer [Books].')
            production[Resource.BOOKS] -= 4
        return production

class ChichenItza(Age2Wonder):
    """Buy War: +1 [Point]"""
    name = 'Chichen Itza'
    abbr = 'CcIz'
    points = 1
    stage_costs = (-2, -2)

    def ready(self):
        self.register_for_event('buying card', self.buying_war, self.gain_point)

    def buying_war(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_war()

    def gain_point(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 1 [Point].')
        player.points += 1

class GreatWall(Age2Wonder):
    """Pass first: No [Points] lost to War"""
    name = 'Great Wall'
    abbr = 'GrWl'
    points = 1
    stage_costs = (-1, -1)
    production_value = Resources({Resource.STABILITY: 2})

    def ready(self):
        self.register_for_event('spared war point loss', self.passed_first, self.spared_war_point_loss)

    def passed_first(self, player, **kwargs):
        return player is self.owner and player.passed_first

    def spared_war_point_loss(self, player, **kwargs):
        self.match.log(f'[{self}] {player} is spared losing 1 [Point] from war.')
        return True

class KrakDesChevaliers(Age2Wonder):
    name = 'Krak des Chevaliers'
    abbr = 'KrCv'
    points = 2
    stage_costs = (-5, -5)
    production_value = Resources({Resource.MILITARY: 6})

class MoaiStatues(Age2Wonder):
    """When ready: +12 [Stone]"""
    name = 'Moai Statues'
    abbr = 'MoSt'
    points = 2
    stage_costs = (-1, -1, -1)
    production_value = Resources({Resource.FOOD: -1})

    def ready(self):
        self.match.log(f'[{self}] {self.owner} gains 12 [Stone].')
        self.owner.resources[Resource.STONE] += 12

class NotreDame(Age2Wonder):
    """Production: If most [Stability]: +3 [Books]"""
    name = 'Notre Dame'
    abbr = 'NtDm'
    points = 1
    stage_costs = (-2, -1)
    production_value = Resources({Resource.BOOKS: 2})

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.most_stability:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 3 [Books].')
            production[Resource.BOOKS] += 3
        return production

class PiazzaSanMarco(Age2Wonder):
    """Action, 1 per round: -2 [Gold]: +5 [Books] / +5 [Food] / +5 [Stone]"""
    name = 'Piazza San Marco'
    abbr = 'PSM'
    points = 1
    stage_costs = (-3, -2, -1)

    def action_available(self, player):
        return player is self.owner and self.markers < 1 and player.resources[Resource.GOLD] >= 2

    def activate(self, player):
        self.markers += 1
        options = (Resources({Resource.BOOKS: 5}), Resources({Resource.FOOD: 5}), Resources({Resource.STONE: 5}))
        choice = self.match.get_move(player, 'Pay 2 [Gold] to get which resources?', options)
        self.match.log(f'[{self}] {player} pays 2 [Gold] and gains {choice}.')
        player.resources[Resource.GOLD] -= 2
        player.resources += choice
        if player.resources[Resource.GOLD] == 0:
            self.match.events['spent last gold'].happen(player)

class PorcelainTower(Age2Wonder):
    """This wonder space may be used for an Advisor"""
    name = 'Porcelain Tower'
    abbr = 'PcTw'
    points = 0
    stage_costs = (-1, 0)

    def ready(self):
        self.register_for_event('coverable cards', self.placing_advisor, self.coverable)
        self.register_for_event('cover card', self.is_self_and_advisor, self.true)

    def placing_advisor(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_advisor()

    def coverable(self, player, **kwargs):
        return self

    def is_self_and_advisor(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_advisor() and kwargs['old_card'] is self

class SankoreUniversity(Age2Wonder):
    """When ready: +8 [Books]"""
    name = 'Sankore University'
    abbr = 'SkUn'
    points = 2
    stage_costs = (-1, -2, -3)

    def ready(self):
        self.match.log(f'[{self}] {self.owner} gains 8 [Books].')
        self.owner.resources[Resource.BOOKS] += 8

class ShwedagonPagoda(Age2Wonder):
    """Action, if none have passed: +1 [Stability] until end of round"""
    name = 'Shwedagon Pagoda'
    abbr = 'SwPg'
    points = 1
    stage_costs = (-3, -2)

    def ready(self):
        self.register_for_event('when removed', self.is_self_with_markers, self.reduce_stability)
        self.register_for_event('end of round', self.has_markers, self.reduce_stability)

    def action_available(self, player):
        return player is self.owner and not any(player.passed for player in self.match.players)

    def activate(self, player):
        self.markers += 1
        self.match.log(f'[{self}] {player} gains 1 [Stability].')
        player.resources[Resource.STABILITY] += 1

    def is_self_with_markers(self, player, **kwargs):
        return player is self.owner and kwargs['card'] is self and self.markers

    def has_markers(self, player, **kwargs):
        return player is self.owner and self.markers

    def reduce_stability(self, player, **kwargs):
        self.match.log(f'[{self}] {player} loses {self.markers} [Stability].')
        player.resources[Resource.STABILITY] -= self.markers
        self.markers = 0

class Age3Wonder(Wonder):
    age = 3

class ForbiddenPalace(Age3Wonder):
    """Pass first: +1 [Point]"""
    name = 'Forbidden Palace'
    abbr = 'FbPl'
    points = 1
    stage_costs = (-2, -1)

    def ready(self):
        self.register_for_event('pass', self.passed_first, self.gain_point)

    def passed_first(self, player, **kwargs):
        return player is self.owner and player.passed_first

    def gain_point(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 1 [Point].')
        player.points += 1

class HimejiCastle(Age3Wonder):
    """Replace Building with newer age Building: +4 [Stone]"""
    name = 'Himeji Castle'
    abbr = 'HmCs'
    points = 1
    stage_costs = (-1, -1, -1)

    def ready(self):
        self.register_for_event('replaced card', self.replaced_building_with_newer_age_building, self.gain_stone)

    def replaced_building_with_newer_age_building(self, player, **kwargs):
        old_card = kwargs['old_card']
        new_card = kwargs['new_card']
        return player is self.owner and old_card.is_building() and new_card.is_building() and new_card.age > old_card.age

    def gain_stone(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 4 [Stone].')
        player.resources[Resource.STONE] += 4

class MachuPicchu(Age3Wonder):
    name = 'Machu Picchu'
    abbr = 'McPc'
    points = 0
    stage_costs = (0, -2, 0)
    production_value = Resources({Resource.GOLD: 6})

class OresundDues(Age3Wonder):
    """After passing, when passed over: +2 [Stone]"""
    name = 'Oresund Dues'
    abbr = 'OsDs'
    points = 1
    stage_costs = (-2, -1, 0)

    def ready(self):
        self.register_for_event('passed over', self.owned, self.gain_stone)
        self.global_effect = True

    def gain_stone(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Stone].')
        player.resources[Resource.STONE] += 2

class PotalaPalace(Age3Wonder):
    """Scoring: +1 [Point] per Advisor"""
    name = 'Potala Palace'
    abbr = 'PtPl'
    points = 1
    stage_costs = (-1, -1)

    def bonus_points(self, projected=False):
        bonus = len(self.owner.advisor_cards())
        if not projected:
            self.match.log(f'[{self}] {self.owner} gains {bonus} [Point{s_if_not_1(bonus)}] for having {bonus} advisor{s_if_not_1(bonus)}.')
        return bonus

class RedFort(Age3Wonder):
    """Buy card for 1 [Gold]: +2 [Food]"""
    name = 'Red Fort'
    abbr = 'RdFt'
    points = 1
    stage_costs = (0, -3)

    def ready(self):
        self.register_for_event('buy card for gold', self.payed_1_gold, self.gain_food)

    def payed_1_gold(self, player, **kwargs):
        return player is self.owner and kwargs['gold'] == 1

    def gain_food(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Food].')
        player.resources[Resource.FOOD] += 2

class RoyalSociety(Age3Wonder):
    """Action, 1 per round: Deploy 1 [Worker] for free"""
    name = 'Royal Society'
    abbr = 'RySc'
    points = 1
    stage_costs = (-3, -2)

    def action_available(self, player):
        return player is self.owner and self.markers < 1 and player.deploy_actions()

    def activate(self, player):
        self.markers += 1
        options = player.deploy_actions()
        if len(options) == 1:
            choice = options[0]
        else:
            choice = self.match.get_move(player, 'Deploy to where?', options)
        self.match.log(f'[{self}] {player} deploys to "{choice.card}" for free.')
        player.deploy_for_free(choice.card)

class SistineChapel(Age3Wonder):
    """Hire [Architect]: +3 [Books]"""
    name = 'Sistine Chapel'
    abbr = 'StCp'
    points = 1
    stage_costs = (-1, -1)
    production_value = Resources({Resource.BOOKS: 1})

    def ready(self):
        self.register_for_event('hire architect', self.owned, self.gain_books)

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 3 [Books].')
        player.resources[Resource.BOOKS] += 3

class TajMahal(Age3Wonder):
    """When ready: +15 [Books]"""
    name = 'Taj Mahal'
    abbr = 'TjMh'
    points = 1
    stage_costs = (-3, -1, -2)

    def ready(self):
        self.match.log(f'[{self}] {self.owner} gains 15 [Books].')
        self.owner.resources[Resource.BOOKS] += 15

class Uraniborg(Age3Wonder):
    name = 'Uraniborg'
    abbr = 'Unb'
    points = 2
    stage_costs = (0, -3, -2)
    production_value = Resources({Resource.BOOKS: 2})
    golden_age_bonus = 2

class Versailles(Age3Wonder):
    """When ready: Least [Stability] for rest of the round."""
    name = 'Versailles'
    abbr = 'Vrs'
    points = 4
    stage_costs = (-4, 0, -1)

    def ready(self):
        self.match.log(f'[{self}] {self.owner} has least [Stability] for the rest of the round.')
        self.register_for_event('force least stability', self.owned, self.true)
        self.register_for_event('end of round', self.owned, self.remove_effect)
        self.global_effect = True

    def remove_effect(self, player, **kwargs):
        self.unregister_all_events()
        self.global_effect = False

class Age4Wonder(Wonder):
    age = 4

class BigBen(Age4Wonder):
    """Scoring: +1 [Point] per Industrial Colony"""
    name = 'Big Ben'
    abbr = 'BgBn'
    points = 1
    stage_costs = (-3, 0)

    def bonus_points(self, projected=False):
        bonus = len([card for card in self.owner.colony_cards() if card.age == 4])
        if not projected:
            colony_or_colonies = 'colony' if bonus == 1 else 'colonies'
            self.match.log(f'[{self}] {self.owner} gains {bonus} [Point{s_if_not_1(bonus)}] for having {bonus} Industrial {colony_or_colonies}.')
        return bonus

class BrandenburgGate(Age4Wonder):
    """When ready: Most [Military]: +6 [Gold], +6 [Stone]"""
    name = 'Brandenburg Gate'
    abbr = 'BbGt'
    points = 2
    stage_costs = (-2, -2)

    def buy(self):
        self.global_effect = True

    def ready(self):
        most_military = self.match.most_military()
        if not most_military:
            self.match.log(f'[{self}] No most [Military].')
        else:
            for player in most_military:
                self.match.log(f'[{self}] {player} gains 6 [Gold] and 6 [Stone].')
                player.resources[Resource.GOLD] += 6
                player.resources[Resource.STONE] += 6
        self.global_effect = False

class BritishMuseum(Age4Wonder):
    """When ready: Least [Military]: -10 [Books]"""
    name = 'British Museum'
    abbr = 'BtMs'
    points = 2
    stage_costs = (0, -1, -3)

    def buy(self):
        self.global_effect = True

    def placed(self):
        least_military = self.match.least_military()
        need_other_player_choice = False
        for player in least_military:
            if player is not self.owner:
                if player.losing_resources_needs_choice(Resources({Resource.BOOKS: -10})):
                    need_other_player_choice = True
        complete_turn = False
        if need_other_player_choice:
            options = [ConfirmAction()]
            if self.owner.remaining_main_actions <= 1:
                options.append(ConfirmCompleteAction())
            choice = self.match.get_move(self.owner, f'Confirm placing "{self}" before another player makes a choice?', tuple(options))
            if choice.action_type is ActionType.CONFIRM_AND_COMPLETE_TURN:
                complete_turn = True
        for player in least_military:
            self.match.log(f'[{self}] {player} loses 10 [Books].')
            player.lose_resources(Resources({Resource.BOOKS: -10}))
        self.owner.need_confirmation = not complete_turn
        self.global_effect = False

class DarwinsVoyage(Age4Wonder):
    """When ready: +15 [Gold]"""
    name = 'Darwin\'s Voyage'
    abbr = 'DwVy'
    points = 1
    stage_costs = (-3, -2)

    def ready(self):
        self.match.log(f'[{self}] {self.owner} gains 15 [Gold].')
        self.owner.resources[Resource.GOLD] += 15

class FordMotorCompany(Age4Wonder):
    name = 'Ford Motor Company'
    abbr = 'FMC'
    points = 1
    stage_costs = (-2, -2)
    production_value = Resources({Resource.STONE: 6})

class MIT(Age4Wonder):
    """Buy a new building: Deploy 1 [Worker] on it for free"""
    name = 'MIT'
    abbr = 'MIT'
    points = 1
    stage_costs = (0, -1)

    def ready(self):
        self.register_for_event('bought card', self.bought_building, self.may_deploy_for_free)

    def bought_building(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_building() and player.grown_workers

    def may_deploy_for_free(self, player, **kwargs):
        card = kwargs['card']
        answer = self.match.get_move(player, f'Deploy 1 [Worker] on "{card}" for free?', ('Yes', 'No'))
        if answer == 'Yes':
            if player.workers == 0:
                possible_undeploys = player.undeploy_actions()
                if len(possible_undeploys) == 1:
                    undeploy = possible_undeploys[0]
                else:
                    undeploy = self.match.get_move(self.owner, 'Undeploy worker from where?', possible_undeploys)
                player.undeploy_action(undeploy)
            self.match.log(f'[{self}] {player} deploys 1 [Worker] to "{card}" for free.')
            player.deploy_for_free(card)

class SouthPoleExpedition(Age4Wonder):
    """When ready: -5 [Food]"""
    name = 'South Pole Expedition'
    abbr = 'SPE'
    points = 3
    stage_costs = (-2, -1)

    def ready(self):
        self.match.log(f'[{self}] {self.owner} loses 5 [Food].')
        self.owner.lose_resources(Resources({Resource.FOOD: -5}))

class StatueOfLiberty(Age4Wonder):
    """Scoring: +2 [Points] if most [Workers]"""
    name = 'Statue of Liberty'
    abbr = 'StLb'
    points = 1
    stage_costs = (0, -2)

    def bonus_points(self, projected=False):
        if self.owner in self.match.most_least({player.name: player.grown_workers for player in self.match.players})[0]:
            if not projected:
                self.match.log(f'[{self}] {self.owner} gains 2 [Points] for having the most [Workers].')
            return 2
        if not projected:
            self.match.log(f'[{self}] {self.owner} does not have the most [Workers].')
        return 0

class SuezCanal(Age4Wonder):
    name = 'Suez Canal'
    abbr = 'SzCn'
    points = 1
    stage_costs = (-2, -1)
    production_value = Resources({Resource.GOLD: 3, Resource.MILITARY: 4})

class Titanic(Age4Wonder):
    """When ready: All: -4 [Gold] or remove Advisor"""
    name = 'Titanic'
    abbr = 'Ttn'
    points = 3
    stage_costs = (-2, 0, -2)

    def buy(self):
        self.global_effect = True

    def placed(self):
        need_other_player_choice = False
        player_has_advisor = {}
        for player in self.match.players[::-1]:
            has_advisor = False
            if player.removable_advisor_cards():
                has_advisor = True
            player_has_advisor[player.name] = has_advisor
            if player is not self.owner:
                has_4_gold = player.resources[Resource.GOLD] >= 4
                if has_advisor and has_4_gold:
                    need_other_player_choice = True
                elif not has_advisor and not has_4_gold:
                    if player.losing_resources_needs_choice(Resources({Resource.GOLD: -4})):
                        need_other_player_choice = True
        complete_turn = False
        if need_other_player_choice:
            options = [ConfirmAction()]
            if self.owner.remaining_main_actions <= 1:
                options.append(ConfirmCompleteAction())
            choice = self.match.get_move(self.owner, f'Confirm placing "{self}" before another player makes a choice?', tuple(options))
            if choice.action_type is ActionType.CONFIRM_AND_COMPLETE_TURN:
                complete_turn = True
            self.owner.need_confirmation = False
        for player in self.match.players[::-1]:
            has_advisor = player_has_advisor[player.name]
            has_4_gold = player.resources[Resource.GOLD] >= 4
            remove_advisors = False
            if has_advisor and not has_4_gold:
                remove_advisors = True
            elif not has_advisor:
                remove_advisors = False
            else:
                choice = self.match.get_move(player, 'Lose 4 [Gold] or remove advisors?', ('-4 [Gold]', 'remove advisors'))
                if choice == 'remove advisors':
                    remove_advisors = True
            if remove_advisors:
                self.match.log(f'[{self}] {player} removes advisors.')
                player.remove_all_advisors()
            else:
                self.match.log(f'[{self}] {player} loses 4 [Gold].')
                player.lose_resources(Resources({Resource.GOLD: -4}))
            if player.need_confirmation:
                self.match.get_move(player, 'Confirm?', ('Confirm',))
        self.owner.need_confirmation = not complete_turn
        self.global_effect = False

class WardenclyffeTower(Age4Wonder):
    """When ready: Take 3 actions"""
    name = 'Wardenclyffe Tower'
    abbr = 'WcTw'
    points = 1
    stage_costs = (-1, -1)

    def placed(self):
        if self.match.phase is Phase.ACTION:
            self.owner.remaining_main_actions += 3
        else:
            self.owner.remaining_main_actions = 3
            while self.owner.remaining_main_actions:
                self.owner.take_one_action()
            while not self.owner.passed:
                possible_actions = [ConfirmAction()]
                if not self.owner.explore_actions():
                    possible_actions += self.owner.undeploy_actions()
                action = self.match.get_move(self.owner, 'Complete the turn?', possible_actions)
                if action.action_type is ActionType.CONFIRM:
                    return
                self.owner.take_action(action)

class Age1Advisor(Advisor):
    age = 1

class Archimedes(Age1Advisor):
    """1 private [Architect] per round"""
    name = 'Archimedes'
    abbr = 'Acm'
    production_value = Resources({Resource.STONE: 1})
    private_architects = 1

class Augustus(Age1Advisor):
    """Production: If most [Military]: +2 [Stone]"""
    name = 'Augustus'
    abbr = 'Agt'
    production_value = Resources({Resource.MILITARY: 1})

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.most_military:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 2 [Stone].')
            production[Resource.STONE] += 2
        return production

class Boudica(Age1Advisor):
    """If you have Military [Workers]: remove"""
    name = 'Boudica'
    abbr = 'Bdc'
    production_value = Resources({Resource.MILITARY: 1, Resource.GOLD: 1, Resource.FOOD: 1})

    def placed(self):
        self.register_for_event('updating most least stability military', self.has_military_worker, self.remove)

    def has_military_worker(self, player, **kwargs):
        return player is self.owner and any(card.deployed_workers for card in player.military_cards())

    def remove(self, player, **kwargs):
        self.match.log(f'{player} removes "{self}".')
        player.remove(self)

class Buddha(Age1Advisor):
    """Action, first turn: Must skip"""
    name = 'Buddha'
    abbr = 'Bdh'
    production_value = Resources({Resource.STABILITY: 3})

    def buy(self):
        self.register_for_event('skip turn', self.owned, self.first_turn)

    def first_turn(self, player, **kwargs):
        if player.turn_number == 1:
            self.match.log(f'[{self}] {player} skips first turn.')
            return True
        return False

class CyrusTheGreat(Age1Advisor):
    """Production: If you bought Colony this round: +3 [Gold]"""
    name = 'Cyrus the Great'
    abbr = 'CrGr'

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.bought_colony_this_round:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 3 [Gold].')
            production[Resource.GOLD] += 3
        return production

class Hannibal(Age1Advisor):
    """+1 [Raid Value]; Others: Battles cost 1 [Gold] more"""
    name = 'Hannibal'
    abbr = 'Hnb'

    def buy(self):
        self.register_for_event('extra raid value', self.owned, self.extra_raid_value)
        self.register_for_event('extra card cost', self.others_battles, self.extra_gold)
        self.global_effect = True

    def extra_raid_value(self, player, **kwargs):
        return 1

    def others_battles(self, player, **kwargs):
        return player is not self.owner and kwargs['card'].is_battle()

    def extra_gold(self, player, **kwargs):
        return 1

class Hatshepsut(Age1Advisor):
    """When Wonder ready: +3 [Books]"""
    name = 'Hatshepsut'
    abbr = 'Hss'
    production_value = Resources({Resource.GOLD: 1})

    def buy(self):
        self.register_for_event('wonder ready', self.owned, self.gain_books)

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 3 [Books].')
        player.resources[Resource.BOOKS] += 3

class Hypatia(Age1Advisor):
    """If over 2 [Stability]: Remove; Production: +1 [Marker] then +1 [Book] per [Marker]"""
    name = 'Hypatia'
    abbr = 'Hpt'

    def new_round(self):
        pass

    def placed(self):
        self.register_for_event('updating most least stability military', self.stability_over_2, self.remove)

    def stability_over_2(self, player, **kwargs):
        return player is self.owner and player.resources[Resource.STABILITY] > 2

    def remove(self, player, **kwargs):
        self.match.log(f'{player} removes "{self}".')
        player.remove(self)

    def produce(self, projected=False):
        production = self.production_value.production()
        if projected:
            books = self.markers + 1
        else:
            self.match.log(f'"{self}" gains 1 [Marker].')
            self.markers += 1
            books = self.markers
            self.match.log(f'[{self}] {self.owner} produces an extra {books} [Book{s_if_not_1(books)}].')
        production[Resource.BOOKS] += books
        return production

class QinShiHuang(Age1Advisor):
    """If least [Stability]: Remove"""
    name = 'Qin Shi Huang'
    abbr = 'QSH'
    production_value = Resources({Resource.FOOD: 3})

    def placed(self):
        self.register_for_event('least stability', self.owned, self.remove)

    def remove(self, player, **kwargs):
        self.match.log(f'{player} removes "{self}".')
        player.remove(self)

class SaintAugustine(Age1Advisor):
    """Production: If most [Stability]: +2 [Books]"""
    name = 'Saint Augustine'
    abbr = 'StAg'
    production_value = Resources({Resource.STABILITY: 1})

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.most_stability:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 2 [Books].')
            production[Resource.BOOKS] += 2
        return production

class SunTzu(Age1Advisor):
    """Action, first turn each round: Take 2 Actions"""
    name = 'Sun Tzu'
    abbr = 'SnTz'

    def buy(self):
        self.register_for_event('additional action', self.owned, self.first_turn)

    def first_turn(self, player, **kwargs):
        if player.turn_number == 1:
            self.match.log(f'[{self}] {player} takes 2 actions.')
            return True
        return False

class Age2Advisor(Advisor):
    age = 2

class AbuBakr(Age2Advisor):
    """Buy Battle: +2 [Books]"""
    name = 'Abu Bakr'
    abbr = 'AbBk'
    production_value = Resources({Resource.MILITARY: 2})

    def buy(self):
        self.register_for_event('buying card', self.buying_battle, self.gain_books)

    def buying_battle(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_battle()

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Books].')
        player.resources[Resource.BOOKS] += 2

class Alhazen(Age2Advisor):
    """Action, 1 per round: Swap places of two cards on the Progress Board"""
    name = 'Alhazen'
    abbr = 'Ahz'
    production_value = Resources({Resource.BOOKS: 2})

    def action_available(self, player):
        return player is self.owner and self.markers < 1

    def activate(self, player):
        self.markers += 1
        options = []
        for (row, cards_in_row) in enumerate(self.match.progress_board):
            for (col, card) in enumerate(cards_in_row):
                if card is not None:
                    options.append(f'P{row + 1}{col + 1}')
        choice1 = self.match.get_move(player, 'Swap which card?', options)
        row1 = int(choice1[1]) - 1
        col1 = int(choice1[2]) - 1
        card1 = self.match.progress_board[row1][col1]
        if card1 is None:
            raise InvalidMove('Must be a card there.')
        choice2 = self.match.get_move(player, 'With which card?', options)
        row2 = int(choice2[1]) - 1
        col2 = int(choice2[2]) - 1
        card2 = self.match.progress_board[row2][col2]
        if card2 is None:
            raise InvalidMove('Must be a card there.')
        if choice1 == choice2:
            raise InvalidMove('Must swap two different cards.')
        self.match.log(f'[{self}] {player} swaps "{card1}" with "{card2}".')
        self.match.progress_board[row1][col1] = card2
        self.match.progress_board[row2][col2] = card1

class AnnaKomnene(Age2Advisor):
    """Production: No upkeep for Military [Workers]"""
    name = 'Anna Komnene'
    abbr = 'AnKn'
    production_value = Resources({Resource.BOOKS: 1})

    def buy(self):
        self.register_for_event('no military upkeep', self.owned, self.true)
        self.register_for_event('when removed', self.is_self, self.restore_upkeep)
        for card in self.owner.military_cards():
            self.owner.resources -= card.deployed_workers * card.production_per_worker.immediate().negative()

    def is_self(self, player, **kwargs):
        return player is self.owner and kwargs['card'] is self

    def restore_upkeep(self, player, **kwargs):
        for card in player.military_cards():
            player.resources += card.deployed_workers * card.production_per_worker.immediate().negative()

class EleanorOfAquitaine(Age2Advisor):
    """Production: If you bought Colony this round: +5 [Gold]"""
    name = 'Eleanor of Aquitaine'
    abbr = 'EnAq'

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.bought_colony_this_round:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 5 [Gold].')
            production[Resource.GOLD] += 5
        return production

class GenghisKhan(Age2Advisor):
    """All: -3 [Stability]"""
    name = 'Genghis Khan'
    abbr = 'GgKn'
    production_value = Resources({Resource.MILITARY: 3})

    def buy(self):
        self.register_for_event('when removed', self.is_self, self.restore_stability)
        self.match.log(f'[{self}] All players lose 3 [Stability].')
        for player in self.match.players[::-1]:
            player.resources[Resource.STABILITY] -= 3
        self.global_effect = True

    def is_self(self, player, **kwargs):
        return player is self.owner and kwargs['card'] is self

    def restore_stability(self, player, **kwargs):
        self.match.log(f'[{self}] All players regain 3 [Stability].')
        for player in self.match.players[::-1]:
            player.resources[Resource.STABILITY] += 3

class HaraldHardrada(Age2Advisor):
    """If least [Military]: Remove"""
    name = 'Harald Hardrada'
    abbr = 'HrHd'
    production_value = Resources({Resource.GOLD: 4})

    def placed(self):
        self.register_for_event('least military', self.owned, self.remove)

    def remove(self, player, **kwargs):
        self.match.log(f'{player} removes "{self}".')
        player.remove(self)

class MansaMusa(Age2Advisor):
    """Spend your last [Gold]: +2 [Books] and +1 [Food]"""
    name = 'Mansa Musa'
    abbr = 'MsMs'
    production_value = Resources({Resource.GOLD: 1})

    def placed(self):
        self.register_for_event('spent last gold', self.owned, self.gain_books_and_food)

    def gain_books_and_food(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Books] and 1 [Food].')
        player.resources[Resource.BOOKS] += 2
        player.resources[Resource.FOOD] += 1

class MarcoPolo(Age2Advisor):
    """Action, 1 per round: -2 [Food] / -2 [Stone]: +4 [Gold]"""
    name = 'Marco Polo'
    abbr = 'McPl'

    def action_available(self, player):
        return player is self.owner and self.markers < 1 and (player.resources[Resource.FOOD] >= 2 or player.resources[Resource.STONE] >= 2)

    def activate(self, player):
        self.markers += 1
        food_payment = Resources({Resource.FOOD: 2})
        stone_payment = Resources({Resource.STONE: 2})
        if player.resources[Resource.STONE] < 2:
            payment = food_payment
        elif player.resources[Resource.FOOD] < 2:
            payment = stone_payment
        else:
            payment = self.match.get_move(player, 'Pay which resources?', (food_payment, stone_payment))
        self.match.log(f'[{self}] {player} pays {payment} and gains 4 [Gold].')
        player.resources -= payment
        player.resources[Resource.GOLD] += 4

class SejongTheGreat(Age2Advisor):
    """Buy Golden Age: +2 [Stone]"""
    name = 'Sejong the Great'
    abbr = 'SjGr'
    production_value = Resources({Resource.FOOD: 2})

    def buy(self):
        self.register_for_event('buying card', self.buying_golden_age, self.gain_stone)

    def buying_golden_age(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_golden_age()

    def gain_stone(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Stone].')
        player.resources[Resource.STONE] += 2

class ThomasAquino(Age2Advisor):
    """Production: If most [Stability]: +4 [Books]"""
    name = 'Thomas Aquino'
    abbr = 'TmAq'
    production_value = Resources({Resource.STABILITY: 1})

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.most_stability:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 4 [Books].')
            production[Resource.BOOKS] += 4
        return production

class ZhuXi(Age2Advisor):
    """Keep when replaced 1st time"""
    name = 'Zhu Xi'
    abbr = 'ZhXi'
    production_value = Resources({Resource.STABILITY: 1, Resource.GOLD: 1})

    def buy(self):
        self.register_for_event('cover card', self.is_self_and_advisor_and_not_covered, self.cover)
        self.register_for_event('remove with', self.covered, self.this_card)
        self.register_for_event('buy with', self.covered, self.this_card)

    def is_self_and_advisor_and_not_covered(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_advisor() and kwargs['old_card'] is self and self.covered_by is None

    def cover(self, player, **kwargs):
        self.match.log(f'[{self}] Not replaced.')
        return True

    def covered(self, player, **kwargs):
        return kwargs['card'] is self.covered_by

    def this_card(self, player, **kwargs):
        return self

class Age3Advisor(Advisor):
    age = 3

class CarolusLinneaus(Age3Advisor):
    """Buy Golden Age: Gain [Point]: +1 [Point]"""
    name = 'Carolus Linneaus'
    abbr = 'CrLn'
    production_value = Resources({Resource.STABILITY: 1})

    def buy(self):
        self.register_for_event('bought golden age point', self.owned, self.gain_point)

    def gain_point(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 1 [Point].')
        player.points += 1

class Elizabeth(Age3Advisor):
    """War: +8 [Military]"""
    name = 'Elizabeth'
    abbr = 'Elz'
    production_value = Resources({Resource.STONE: 2})

    def buy(self):
        self.register_for_event('extra war military', self.owned, self.extra_war_military)

    def extra_war_military(self, player, **kwargs):
        self.match.log(f'[{self}] {player} has an extra 8 [Military] against war.')
        return 8

class GalileoGalilei(Age3Advisor):
    """Action, 1 per round: Buy Golden Age or Wonder for free"""
    name = 'Galileo Galilei'
    abbr = 'GlGl'
    production_value = Resources({Resource.BOOKS: 2})

    def action_available(self, player):
        return player is self.owner and self.markers < 1 and [action for action in player.buy_actions() if action.card.is_golden_age_wonder_natural_wonder()]

    def activate(self, player):
        self.markers += 1
        options = []
        for action in player.buy_actions():
            if action.card.is_golden_age_wonder_natural_wonder():
                options.append(action)
        choice = self.match.get_move(player, 'Buy which card for free?', options)
        self.match.log(f'[{self}] {player} buys "{choice.card}" for free.')
        player.buy_action(choice, free=True)

class Isabella(Age3Advisor):
    """Production: +3 [Gold] per Renaissance Colony"""
    name = 'Isabella'
    abbr = 'Isb'
    production_value = Resources({Resource.FOOD: 2})

    def produce(self, projected=False):
        production = self.production_value.production()
        gold = 3 * len([card for card in self.owner.colony_cards() if card.age == 3])
        if gold:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra {gold} [Gold].')
            production[Resource.GOLD] += gold
        return production

class MartinLuther(Age3Advisor):
    """All: Defeats cost 4 extra [Food]"""
    name = 'Martin Luther'
    abbr = 'MtLt'
    production_value = Resources({Resource.GOLD: 4})

    def buy(self):
        self.register_for_event('extra war food penalty', self.true, self.extra_war_food_penalty)
        self.global_effect = True

    def extra_war_food_penalty(self, player, **kwargs):
        self.match.log(f'[{self}] Defeats cost 4 extra [Food].')
        return 4

class Montezuma(Age3Advisor):
    """Buy War or Battle: +3 [Books]"""
    name = 'Montezuma'
    abbr = 'Mtz'
    production_value = Resources({Resource.FOOD: 2})

    def buy(self):
        self.prev_card = None
        self.register_for_event('buying card', self.buying_war_battle, self.gain_books)

    def buying_war_battle(self, player, **kwargs):
        card = kwargs['card']
        seen = card is self.prev_card
        self.prev_card = card
        return player is self.owner and kwargs['card'].is_war_battle() and not seen

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 3 [Books].')
        player.resources[Resource.BOOKS] += 3

class NiccoloMachiavelli(Age3Advisor):
    """Reveal Events: Draw 2 choose 1"""
    name = 'Niccolo Machiavelli'
    abbr = 'NcMc'
    production_value = Resources({Resource.BOOKS: 4})

    def buy(self):
        self.register_for_event('choose event card', self.owned, self.choose_event_card)

    def choose_event_card(self, player, **kwargs):
        event_cards = kwargs['events']
        event_card = self.match.get_move(player, 'Which event card?', event_cards)
        discarded_event_card = [card for card in event_cards if card is not event_card][0]
        self.match.log(f'[{self}] {player} chooses "{event_card}" as the event card for the round, discarding "{discarded_event_card}".')
        self.match.event = event_card
        self.match.get_move(player, 'Confirm?', ('Confirm',))

class PeterTheGreat(Age3Advisor):
    """Production: If [Military] > War [Military]: +5 [Stone] / +5 [Gold] / +5 [Books]"""
    name = 'Peter the Great'
    abbr = 'PtGr'

    def produce(self, projected=False):
        production = self.production_value.production()
        if projected:
            return production
        if self.match.war is not None and min(40, self.owner.resources[Resource.MILITARY]) > self.match.war_value:
            options = (Resources({Resource.STONE: 5}), Resources({Resource.GOLD: 5}), Resources({Resource.BOOKS: 5}))
            choice = self.match.get_move(self.owner, 'Produce which extra resources?', options)
            self.match.log(f'[{self}] {self.owner} produces an extra {choice}.')
            production += choice
            self.match.get_move(self.owner, 'Confirm?', ('Confirm',))
        return production

class Pocahontas(Age3Advisor):
    """All: Colonies require 4 [Military] extra"""
    name = 'Pocahontas'
    abbr = 'Pch'
    production_value = Resources({Resource.FOOD: 4})

    def buy(self):
        self.register_for_event('extra colony military requirement', self.true, self.extra_colony_military_requirement)
        self.global_effect = True

    def extra_colony_military_requirement(self, player, **kwargs):
        self.match.log(f'[{self}] Colonies require 4 [Military] extra.')
        return 4

class SuleimanI(Age3Advisor):
    """Action, if most [Military]: Take 1 [Worker]"""
    name = 'Suleiman I'
    abbr = 'Slm'
    production_value = Resources({Resource.MILITARY: 3})

    def action_available(self, player):
        return player is self.owner and player.most_military and player.may_take_workers()

    def activate(self, player):
        self.match.log(f'{player} takes the "{self}" special action.')
        player.take_worker()

class Tokugawa(Age3Advisor):
    """Production: +2 [Stone] per Building and Military from current age"""
    name = 'Tokugawa'
    abbr = 'Tkg'
    production_value = Resources({Resource.MILITARY: 2})

    def produce(self, projected=False):
        production = self.production_value.production()
        current_age = (self.match.round_number + 1) // 2
        stone = 2 * len([card for card in self.owner.building_military_cards() if card.age == current_age])
        if stone:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra {stone} [Stone].')
            production[Resource.STONE] += stone
        return production

class Age4Advisor(Advisor):
    age = 4

class AbrahamLincoln(Age4Advisor):
    """Action: Take 1 [Worker]"""
    name = 'Abraham Lincoln'
    abbr = 'AhLc'
    production_value = Resources({Resource.STABILITY: 3})

    def action_available(self, player):
        if self.match.lincoln_nerf:
            return player is self.owner
        else:
            return player is self.owner and player.may_take_workers()

    def activate(self, player):
        self.match.log(f'{player} takes the "{self}" special action.')
        if self.match.lincoln_nerf:
            if player.may_take_workers():
                player.take_worker()
            if player.may_take_workers():
                player.take_worker()
            self.match.log(f'{player} removes "{self}".')
            player.remove(self)
        else:
            player.take_worker()

class AlfredNobel(Age4Advisor):
    """May not buy War; Production: +3 [Stone] per [Worker] on Industrial Building"""
    name = 'Alfred Nobel'
    abbr = 'AfNb'

    def buy(self):
        self.register_for_event('may not buy card', self.buying_war, self.invalid_move)

    def buying_war(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_war()

    def invalid_move(self, player, **kwargs):
        raise InvalidMove(f'[{self}] May not buy war.')

    def produce(self, projected=False):
        production = self.production_value.production()
        stone = 3 * sum(card.deployed_workers for card in self.owner.building_cards() if card.age == 4)
        if stone:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra {stone} [Stone].')
            production[Resource.STONE] += stone
        return production

class BenjaminDisraeli(Age4Advisor):
    """Production: If you bought Colony this round: +8 [Food]"""
    name = 'Benjamin Disraeli'
    abbr = 'BjDr'
    production_value = Resources({Resource.GOLD: 2})

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.bought_colony_this_round:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces an extra 8 [Food].')
            production[Resource.FOOD] += 8
        return production

class FlorenceNightingale(Age4Advisor):
    """Lack of resources: No [Point] loss"""
    name = 'Florence Nightingale'
    abbr = 'FrNg'
    production_value = Resources({Resource.BOOKS: 6})

    def buy(self):
        self.register_for_event('no resource point loss', self.owned, self.log_effect)

    def log_effect(self, player, **kwargs):
        self.match.log(f'[{self}] {player} is spared the [Point] loss.')
        return True

class FredericChopin(Age4Advisor):
    """Production: [Books] x2; Others, before you pass: Action: May buy Chopin for 5 [Gold]"""
    name = 'Frederic Chopin'
    abbr = 'FdCp'

    def buy(self):
        self.register_for_event('additional production', self.owned, self.double_books)
        self.register_for_event('additional buys', self.not_passed, self.this_card)
        self.register_for_event('buy from player', self.is_this_card, self.buy_this_card)

    def double_books(self, player, **kwargs):
        additional_books = kwargs['production'][Resource.BOOKS]
        if not kwargs['projected']:
            self.match.log(f'[{self}] {player} produces an extra {additional_books} [Books].')
        return Resources({Resource.BOOKS: additional_books})

    def not_passed(self, player, **kwargs):
        return player is not self.owner and not self.owner.passed and player.resources[Resource.GOLD] >= 5

    def this_card(self, player, **kwargs):
        return [(self.owner, self)]

    def is_this_card(self, player, **kwargs):
        return kwargs['card'] is self

    def buy_this_card(self, player, **kwargs):
        self.match.log(f'{player} pays 5 [Gold] to buy "{self}" from {self.owner}.')
        player.resources[Resource.GOLD] -= 5
        self.owner.remove(self)
        return 5

class FrederickTheGreat(Age4Advisor):
    """Military [Workers] cost 2 [Stone] less to deploy (at least 1 [Stone])"""
    name = 'Frederick the Great'
    abbr = 'FdGr'
    production_value = Resources({Resource.MILITARY: 2})

    def buy(self):
        self.register_for_event('deploy discount', self.military, self.deploy_discount)

    def military(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_military()

    def deploy_discount(self, player, **kwargs):
        cost = kwargs['cost']
        discount = cost - max(1, cost - 2)
        self.match.log(f'[{self}] {player} pays {discount} [Stone] less to deploy military [Worker].')
        return discount

class LinZexu(Age4Advisor):
    """Production: If least [Military]: -8 [Books]"""
    name = 'Lin Zexu'
    abbr = 'LnZx'
    production_value = Resources({Resource.FOOD: 4, Resource.GOLD: 4})

    def produce(self, projected=False):
        production = self.production_value.production()
        if self.owner.least_military:
            if not projected:
                self.match.log(f'[{self}] {self.owner} produces 8 fewer [Books].')
            production[Resource.BOOKS] -= 8
        return production

class MarieAntoinette(Age4Advisor):
    name = 'Marie Antoinette'
    abbr = 'MrAn'
    production_value = Resources({Resource.BOOKS: 10, Resource.STABILITY: -3})

class MarieCurie(Age4Advisor):
    """2 private [Architects] per round"""
    name = 'Marie Curie'
    abbr = 'MrCr'
    production_value = Resources({Resource.STONE: 4})
    private_architects = 2

class ShakaZulu(Age4Advisor):
    """Others: Buy Colony: +5 [Stone]"""
    name = 'Shaka Zulu'
    abbr = 'SkZl'
    production_value = Resources({Resource.MILITARY: 8})

    def buy(self):
        self.register_for_event('buying card', self.other_buying_colony, self.gain_stone)
        self.global_effect = True

    def other_buying_colony(self, player, **kwargs):
        return player is not self.owner and kwargs['card'].is_colony()

    def gain_stone(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 5 [Stone].')
        player.resources[Resource.STONE] += 5

class SimonBolivar(Age4Advisor):
    """Action: Remove Colony: +4 [Gold] and +4 [Stone]"""
    name = 'Simon Bolivar'
    abbr = 'SmBl'

    def action_available(self, player):
        return player is self.owner and player.colony_cards()

    def activate(self, player):
        colonies = player.colony_cards()
        if len(colonies) == 1:
            colony = colonies[0]
        else:
            colony = self.match.get_move(player, 'Remove which colony?', colonies)
        self.match.log(f'[{self}] {player} removes {colony} and gains 4 [Gold] and 4 [Stone].')
        player.remove(colony)
        player.resources[Resource.GOLD] += 4
        player.resources[Resource.STONE] += 4

class Age1GoldenAge(GoldenAge):
    age = 1

class Aeneid(Age1GoldenAge):
    name = 'Aeneid'
    abbr = 'And'
    offers_books = True

class Coinage(Age1GoldenAge):
    name = 'Coinage'
    abbr = 'Cng'
    offers_stone = True

class IronWorking(Age1GoldenAge):
    name = 'Iron Working'
    abbr = 'IrWk'
    offers_stone = True

class Mahabharata(Age1GoldenAge):
    name = 'Mahabharata'
    abbr = 'Mhb'
    offers_books = True

class MapMaking(Age1GoldenAge):
    name = 'Map Making'
    abbr = 'MpMk'
    offers_stone = True

class Silk(Age1GoldenAge):
    name = 'Silk'
    abbr = 'Slk'
    offers_stone = True

class TheBible(Age1GoldenAge):
    name = 'The Bible'
    abbr = 'Bib'
    offers_books = True

class TheOdyssey(Age1GoldenAge):
    name = 'The Odyssey'
    abbr = 'Ods'
    offers_books = True

class Age2GoldenAge(GoldenAge):
    age = 2

class ArabianNights(Age2GoldenAge):
    """After passing, when passed over: +2 [Books]"""
    name = 'Arabian Nights'
    abbr = 'ArNt'
    offers_special_action = True

    def activate(self, player):
        self.match.log(f'[{self}] {player} chooses the special ability.')
        self.register_for_event('passed over', self.owned, self.gain_books)
        self.register_for_event('end of round', self.owned, self.remove_effect)
        self.owner.extra_cards.append(self)
        self.global_effect = True

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 2 [Books].')
        player.resources[Resource.BOOKS] += 2

    def remove_effect(self, player, **kwargs):
        self.owner.extra_cards.remove(self)
        self.global_effect = False
        self.unregister_all_events()

class Compass(Age2GoldenAge):
    name = 'Compass'
    abbr = 'Cmp'
    offers_stone = True

class DivinaCommedia(Age2GoldenAge):
    name = 'Divina Commedia'
    abbr = 'DvCm'
    offers_books = True

class Gunpowder(Age2GoldenAge):
    name = 'Gunpowder'
    abbr = 'Gpd'
    offers_stone = True

class HeavyPlough(Age2GoldenAge):
    name = 'Heavy Plough'
    abbr = 'HvPl'
    offers_stone = True

class MagnaCarta(Age2GoldenAge):
    name = 'Magna Carta'
    abbr = 'MnCt'
    offers_books = True

class Spectacles(Age2GoldenAge):
    name = 'Spectacles'
    abbr = 'Stc'
    offers_stone = True

class TheQuoran(Age2GoldenAge):
    name = 'The Quoran'
    abbr = 'Qrn'
    offers_books = True

class RomanceOfTheThreeKingdoms(Age2GoldenAge):
    name = 'Three Kingdoms'
    abbr = 'RTK'
    offers_books = True

class Age3GoldenAge(GoldenAge):
    age = 3

class Clocks(Age3GoldenAge):
    name = 'Clocks'
    abbr = 'Clk'
    offers_stone = True

class DonQuixote(Age3GoldenAge):
    name = 'Don Quixote'
    abbr = 'DnQx'
    offers_books = True

class GutenbergBible(Age3GoldenAge):
    name = 'Gutenberg Bible'
    abbr = 'GbBb'
    offers_books = True

class LeVite(Age3GoldenAge):
    """3 new [Architects]; This round you pay 1 [Stone] less per [Architect]"""
    name = 'Le Vite'
    abbr = 'LeVt'
    offers_special_action = True

    def activate(self, player):
        self.match.log(f'[{self}] {player} chooses the special ability.')
        self.register_for_event('hire discount', self.owned, self.hire_discount)
        self.register_for_event('end of round', self.owned, self.remove_effect)
        self.match.log(f'[{self}] 3 additional [Architects] available.')
        self.match.architects += 3

    def hire_discount(self, player, **kwargs):
        self.match.log(f'[{self}] {player} pays up to 1 less [Stone] per [Architect] this round.')
        return 1

    def remove_effect(self, player, **kwargs):
        self.unregister_all_events()

class Microscope(Age3GoldenAge):
    name = 'Microscope'
    abbr = 'Mcs'
    offers_stone = True

class Principia(Age3GoldenAge):
    name = 'Principia'
    abbr = 'Pcp'
    offers_books = True

class RomeoAndJuliet(Age3GoldenAge):
    name = 'Romeo and Juliet'
    abbr = 'RmJl'
    offers_books = True

class Telescope(Age3GoldenAge):
    name = 'Telescope'
    abbr = 'Tls'
    offers_stone = True

class Thermometer(Age3GoldenAge):
    name = 'Thermometer'
    abbr = 'Tmm'
    offers_stone = True

class Age4GoldenAge(GoldenAge):
    age = 4

class Candide(Age4GoldenAge):
    name = 'Candide'
    abbr = 'Cdd'
    offers_books = True

class DasKapital(Age4GoldenAge):
    name = 'Das Kapital'
    abbr = 'DsKp'
    offers_books = True

class Dynamite(Age4GoldenAge):
    name = 'Dynamite'
    abbr = 'Dnm'
    offers_stone = True

class Electricity(Age4GoldenAge):
    name = 'Electricity'
    abbr = 'Etc'
    offers_stone = True

class Kalevala(Age4GoldenAge):
    name = 'Kalevala'
    abbr = 'Klv'
    offers_books = True

class OriginOfSpecies(Age4GoldenAge):
    name = 'Origin of Species'
    abbr = 'OgSc'
    offers_books = True

class SpinningJenny(Age4GoldenAge):
    name = 'Spinning Jenny'
    abbr = 'SnJn'
    offers_stone = True

class UncleTomsCabin(Age4GoldenAge):
    """All: Remove Buildings with deployment cost of 1 [Stone]"""
    name = 'Uncle Tom\'s Cabin'
    abbr = 'UTC'
    offers_special_action = True

    def activate(self, player):
        self.match.log(f'[{self}] {player} chooses the special ability.')
        any_buildings_removed = False
        for player in self.match.players[::-1]:
            cards_to_remove = [card for card in player.building_cards() if card.deployment_cost == -1]
            for card in cards_to_remove:
                self.match.log(f'[{self}] {player} removes "{card}"')
                player.remove(card)
                any_buildings_removed = True
        if not any_buildings_removed:
            self.match.log(f'[{self}] No buildings were removed.')

class Vaccine(Age4GoldenAge):
    name = 'Vaccine'
    abbr = 'Vcn'
    offers_stone = True

class Age1NaturalWonder(NaturalWonder):
    age = 1

class MountArarat(Age1NaturalWonder):
    """When discovered: Others: -3 [Food]"""
    name = 'Mount Ararat'
    abbr = 'MtAr'
    exploration_turns = 1
    points = 0

    def placed(self):
        need_other_player_choice = False
        for player in self.match.players[::-1]:
            if player is not self.owner:
                if player.losing_resources_needs_choice(Resources({Resource.FOOD: -3})):
                    need_other_player_choice = True
        if need_other_player_choice:
            options = [ConfirmAction()]
            if self.owner.remaining_main_actions <= 1:
                options.append(ConfirmCompleteAction())
            choice = self.match.get_move(self.owner, f'Confirm placing "{self}" before another player makes a choice?', tuple(options))
            self.owner.need_confirmation = choice.action_type is not ActionType.CONFIRM_AND_COMPLETE_TURN
        for player in self.match.players[::-1]:
            if player is not self.owner:
                self.match.log(f'[{self}] {player} loses 3 [Food].')
                player.lose_resources(Resources({Resource.FOOD: -3}))

class MountKailash(Age1NaturalWonder):
    name = 'Mount Kailash'
    abbr = 'MtKl'
    exploration_turns = 3
    points = 2

class SiwaOasis(Age1NaturalWonder):
    """Buy Colony: +3 [Books]"""
    name = 'Siwa Oasis'
    abbr = 'SwOs'
    exploration_turns = 1
    points = 0

    def discovered(self):
        self.register_for_event('buying card', self.buying_colony, self.gain_books)

    def buying_colony(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_colony()

    def gain_books(self, player, **kwargs):
        self.match.log(f'[{self}] {player} gains 3 [Books].')
        player.resources[Resource.BOOKS] += 3

class ThePillarOfHercules(Age1NaturalWonder):
    """When discovered: +7 [Military] until end of round"""
    name = 'The Pillar of Hercules'
    abbr = 'PlHc'
    exploration_turns = 1
    points = 0

    def discovered(self):
        self.match.log(f'[{self}] {self.owner} gains 7 [Military] until the end of the round.')
        self.owner.resources[Resource.MILITARY] += 7
        self.register_for_event('end of round', self.owned, self.reduce_military)

    def reduce_military(self, player, **kwargs):
        self.match.log(f'[{self}] {player} loses 7 [Military].')
        player.resources[Resource.MILITARY] -= 7
        self.unregister_all_events()

class Vesuvius(Age1NaturalWonder):
    """End of each age: Return 1 [Worker]"""
    name = 'Vesuvius'
    abbr = 'Vsv'
    exploration_turns = 2
    points = 4
    production_value = Resources({Resource.FOOD: 1})

    def discovered(self):
        self.register_for_event('end of age', self.owned, self.return_worker)

    def return_worker(self, player, **kwargs):
        self.match.log(f'[{self}] {player} must return 1 [Worker].')
        player.return_worker()

class Age2NaturalWonder(NaturalWonder):
    age = 2

class AuroraBorealis(Age2NaturalWonder):
    """When discovered: +2 [Gold]"""
    name = 'Aurora Borealis'
    abbr = 'ArBr'
    exploration_turns = 1
    points = 1

    def discovered(self):
        self.match.log(f'[{self}] {self.owner} gains 2 [Gold].')
        self.owner.resources[Resource.GOLD] += 2

class GrandBanks(Age2NaturalWonder):
    name = 'Grand Banks'
    abbr = 'GrBk'
    exploration_turns = 2
    points = 0
    production_value = Resources({Resource.FOOD: 2})

class Hawaii(Age2NaturalWonder):
    """When discovered: Take 1 [Worker], place [Marker] on population track"""
    name = 'Hawaii'
    abbr = 'Hwi'
    exploration_turns = 4
    points = -1

    def buying(self):
        if not self.owner.may_take_workers(from_extra=False):
            raise InvalidMove(f'[{self}] Need at least 1 [Worker] on a population track to buy.')

    def placed(self):
        available_workers = {}
        for (index, worker_pool) in enumerate(self.owner.worker_pools):
            available_workers[index] = worker_pool.ungrown_workers
        self.owner.take_worker(from_extra=False, update_immediate_production=False)
        for (index, worker_pool) in enumerate(self.owner.worker_pools):
            if worker_pool.ungrown_workers < available_workers[index]:
                self.match.log(f'[{self}] {self.owner} marks the {worker_pool.resource_cost_per_worker} population track.')
                worker_pool.mark()

class Sahara(Age2NaturalWonder):
    """War: +4 [Military]"""
    name = 'Sahara'
    abbr = 'Shr'
    exploration_turns = 1
    points = 1

    def discovered(self):
        self.register_for_event('extra war military', self.owned, self.extra_war_military)

    def extra_war_military(self, player, **kwargs):
        self.match.log(f'[{self}] {player} has an extra 4 [Military] against war.')
        return 4

class Siberia(Age2NaturalWonder):
    """Covers 2 wonder spaces"""
    name = 'Siberia'
    abbr = 'Sbr'
    exploration_turns = 2
    points = 2
    production_value = Resources({Resource.STONE: 2})

    def placed(self):
        siberia2 = [card(self.match) for card in all_extension_cards if card.name == 'Siberia 2'][0]
        siberia2.reset()
        siberia2.assign_owner(self.owner)
        self.owner.place_wonder_or_natural_wonder(siberia2)

class Siberia2(ExtensionCard):
    """...is a vast region"""
    name = 'Siberia 2'
    abbr = 'Sbr2'
    progress_card_type = ProgressCardType.NATURAL_WONDER

class Age3NaturalWonder(NaturalWonder):
    age = 3

class CapeOfGoodHope(Age3NaturalWonder):
    """Buy Colony: Requires -4 [Military]"""
    name = 'Cape of Good Hope'
    abbr = 'CGH'
    exploration_turns = 1
    points = 1

    def discovered(self):
        self.register_for_event('colony discount', self.owned, self.colony_discount)

    def colony_discount(self, player, **kwargs):
        self.match.log(f'[{self}] {player} requires 4 [Military] less to buy colonies.')
        return 4

class GrandCanyon(Age3NaturalWonder):
    """Final Scoring: +1 [Point] per other Natural Wonder"""
    name = 'Grand Canyon'
    abbr = 'GrCy'
    exploration_turns = 2
    points = 0

    def bonus_points(self, projected=False):
        bonus = len(self.owner.natural_wonder_cards()) - 1
        if not projected:
            self.match.log(f'[{self}] {self.owner} gains {bonus} [Point{s_if_not_1(bonus)}] for having {bonus} other natural wonder{s_if_not_1(bonus)}.')
        return bonus

class GreatBarrierReef(Age3NaturalWonder):
    """Action, 1 per round: -1 [Point], +5 [Food]"""
    name = 'Great Barrier Reef'
    abbr = 'GBR'
    exploration_turns = 3
    points = 2

    def action_available(self, player):
        return player is self.owner and self.markers < 1 and player.points >= 1

    def activate(self, player):
        self.markers += 1
        self.match.log(f'[{self}] {player} pays 1 [Point] and gains 5 [Food].')
        player.points -= 1
        player.resources[Resource.FOOD] += 5

class GreatPlains(Age3NaturalWonder):
    """This Wonder space may be used for a Building or Military"""
    name = 'Great Plains'
    abbr = 'GrPl'
    exploration_turns = 1
    points = 0

    def discovered(self):
        self.register_for_event('coverable cards', self.placing_building_military, self.coverable)
        self.register_for_event('cover card', self.is_self_and_building_military, self.true)

    def placing_building_military(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_building_military()

    def coverable(self, player, **kwargs):
        return self

    def is_self_and_building_military(self, player, **kwargs):
        return player is self.owner and kwargs['card'].is_building_military() and kwargs['old_card'] is self

class SpiceIslands(Age3NaturalWonder):
    """Growth: [Food] / [Stone] / [Gold] bonus: +4 same resource"""
    name = 'Spice Islands'
    abbr = 'SpIl'
    exploration_turns = 2
    points = 0

    def discovered(self):
        self.register_for_event('extra growth resources', self.owned, self.extra_growth_resources)
        self.register_for_event('received extra growth resources', self.owned, self.log_extra_growth_resources)

    def extra_growth_resources(self, player, **kwargs):
        return 4

    def log_extra_growth_resources(self, player, **kwargs):
        growth = kwargs['growth']
        for resource_type in (Resource.FOOD, Resource.STONE, Resource.GOLD):
            if growth[resource_type]:
                self.match.log(f'[{self}] {player} gains an extra 4 {resource_type}.')
                return

class Age4NaturalWonder(NaturalWonder):
    age = 4

class NorthwestPassage(Age4NaturalWonder):
    """When discovered: Return 2 [Workers]"""
    name = 'Northwest Passage'
    abbr = 'NwPs'
    exploration_turns = 2
    points = 4

    def buying(self):
        if self.owner.grown_workers < 2:
            raise InvalidMove(f'[{self}] Need at least 2 [Workers] to buy.')

    def placed(self):
        self.owner.return_worker(no_confirmation=True)
        self.owner.return_worker(no_confirmation=True)

class Titusville(Age4NaturalWonder):
    """Final Scoring: [Stone] x2"""
    name = 'Titusville'
    abbr = 'Ttv'
    exploration_turns = 2
    points = 1

    def discovered(self):
        self.register_for_event('extra scoring stone', self.owned, self.extra_scoring_stone)

    def extra_scoring_stone(self, player, **kwargs):
        stone = self.owner.resources[Resource.STONE]
        if not kwargs['projected']:
            self.match.log(f'[{self}] {player} gains {stone} [Stone] for scoring.')
        return stone

class Uluru(Age4NaturalWonder):
    """When discovered: 1 [Point] per player who has passed"""
    name = 'Uluru'
    abbr = 'Ulr'
    exploration_turns = 4
    points = 0

    def discovered(self):
        points = len([player for player in self.match.players if player.passed])
        self.match.log(f'[{self}] {self.owner} gains {points} [Point{s_if_not_1(points)}] for {points} passed player{s_if_not_1(points)}.')
        self.owner.points += points

class VictoriaFalls(Age4NaturalWonder):
    """When discovered: Draw 20 cards, place colonies as row 4, discard others; Action, All: 4 [Gold] to buy card from row 4"""
    name = 'Victoria Falls'
    abbr = 'VtFl'
    exploration_turns = 2
    points = 2

    def discovered(self):
        drawn_cards = self.match.draw_cards(20)
        self.match.log(f'[{self}] Cards drawn:')
        colonies_drawn = []
        for card in drawn_cards:
            self.match.log(f'[{self}] "{card}"')
            if card.is_colony():
                colonies_drawn.append(card)
        if colonies_drawn:
            self.match.progress_board.append(colonies_drawn)
        else:
            self.match.log(f'[{self}] No colonies drawn.')

all_progress_cards = []
subclasses = [ProgressCard]
while subclasses:
    next_subclasses = []
    for cls in subclasses:
        if cls.__subclasses__():
            next_subclasses.extend(cls.__subclasses__())
        elif cls not in all_progress_cards and not cls.starting_card:
            all_progress_cards.append(cls)
    subclasses = next_subclasses

def progress_sort_key(card):
    return (card.age, card.name)

all_progress_cards.sort(key=progress_sort_key)
progress_card_abbrs = {card.abbr: card.name for card in all_progress_cards}
progress_card_abbrs['AhLc_Nerf'] = 'Abraham Lincoln'

all_extension_cards = []
subclasses = [ExtensionCard]
while subclasses:
    next_subclasses = []
    for cls in subclasses:
        if cls.__subclasses__():
            next_subclasses.extend(cls.__subclasses__())
        elif cls not in all_extension_cards:
            all_extension_cards.append(cls)
    subclasses = next_subclasses

def extension_sort_key(card):
    return card.name

all_extension_cards.sort(key=extension_sort_key)
extension_card_abbrs = {card.abbr: card.name for card in all_extension_cards}
