import collections

from .cards import *
from .resources import *

def s_if_not_1(value):
    return 's' if value != 1 else ''

class EventCard(Card):
    card_type = CardType.EVENT

    def __init__(self, match):
        super().__init__(match)
        self.name = self.name()

    @classmethod
    def name(cls):
        return f'{cls.name_a}; {cls.name_b}'

    def __str__(self):
        return self.name

    def reveal(self):
        pass

    def happen(self):
        self.match.log(f'[{self.name_a}] {self.effect_a}')
        self.happen_a()
        self.match.update_most_least_stability_military()
        self.match.log(f'[{self.name_b}] {self.effect_b}')
        self.happen_b()
        self.match.update_most_least_stability_military()

    def most_stability(self):
        most_stability = self.match.most_stability()
        if not most_stability:
            self.match.log('No most [Stability].')
        return most_stability

    def most_military(self):
        most_military = self.match.most_military()
        if not most_military:
            self.match.log('No most [Military].')
        return most_military

    def most_food(self):
        most_food = self.match.most_food()
        if not most_food:
            self.match.log('No most [Food].')
        return most_food

    def sort_players(self, players, resource):
        def sort_key(player):
            return (-max(-1, player.resources[resource]), self.match.players.index(player))
        players.sort(key=sort_key)

    def players_gain_point(self, players):
        for player in players:
            self.match.log(f'{player} gains 1 [Point].')
            player.points += 1

    def players_gain_resources(self, players, resources):
        for player in players:
            self.match.log(f'{player} gains {resources}.')
            player.resources += resources

    def players_lose_resources(self, players, resources):
        for player in players:
            self.match.log(f'{player} loses {-resources}.')
            player.lose_resources(resources)

    def may_pay_to_gain(self, pay, gain):
        for player in self.match.players[::-1]:
            if player.resources >= pay:
                answer = self.match.get_move(player, f'Pay {pay} to gain {gain}?', ('Yes', 'No'))
                if answer == 'Yes':
                    self.match.log(f'{player} pays {pay} and gains {gain}.')
                    player.resources -= pay
                    player.resources += gain
                else:
                    self.match.log(f'{player} declines.')
                self.match.get_move(player, 'Confirm?', ('Confirm',))
            else:
                self.match.log(f'{player} does not have at least {pay}.')

    def least_stability_goes_last_and_loses_resources(self, resources):
        least_stability = self.match.least_stability()
        if len(least_stability) == 1:
            player = least_stability[0]
            self.match.log(f'{player} goes last.')
            self.match.players.remove(player)
            self.match.players.append(player)
        else:
            self.sort_players(least_stability, Resource.STABILITY)
            if len(least_stability) == 2:
                players = f'{least_stability[0]} and {least_stability[1]}'
            else:
                players = ', '.join(f'{player}' for player in least_stability[:-1]) + f', and {least_stability[-1]}'
            self.match.log(f'{players} go last.')
            self.match.players = [player for player in self.match.players if player not in least_stability] + least_stability
            least_stability = least_stability[::-1]
        self.players_lose_resources(least_stability, resources)

class Age1EventCard(EventCard):
    age = 1

class AryanMigrationCodeOfHammurabi(Age1EventCard):
    name_a = 'Aryan Migration'
    name_b = 'Code of Hammurabi'
    effect_a = 'Least [Military]: -3 [Books]'
    effect_b = 'All except least [Stability]: +3 [Food]'
    abbr = 'AM_CH'
    architects = 2
    famine = -1

    def happen_a(self):
        self.players_lose_resources(self.match.least_military(), Resources({Resource.BOOKS: -3}))

    def happen_b(self):
        least_stability = self.match.least_stability()
        if len(least_stability) == len(self.match.players):
            self.match.log('All players have least [Stability].')
        else:
            for player in self.match.players[::-1]:
                if player not in least_stability:
                    self.match.log(f'{player} gains 3 [Food].')
                    player.resources[Resource.FOOD] += 3

class AssyrianDeportationsJainAscetism(Age1EventCard):
    name_a = 'Assyrian deportations'
    name_b = 'Jain Ascetism'
    effect_a = 'Least [Military]: Return 1 [Worker]'
    effect_b = 'Most [Stability]: Regain all [Points] lost to War this round'
    abbr = 'AD_JA'
    architects = 1
    famine = 0

    def reset(self):
        super().reset()
        self.points_lost_to_war = collections.Counter()

    def reveal(self):
        self.register_for_event('lost to war', self.true, self.lost_points_to_war)

    def lost_points_to_war(self, player, **kwargs):
        if 'points' in kwargs:
            self.points_lost_to_war[player.name] += kwargs['points']

    def happen_a(self):
        for player in self.match.least_military():
            if player.grown_workers:
                self.match.log(f'{player} must return 1 [Worker].')
                player.return_worker()
            else:
                self.match.log(f'{player} has no workers to return.')

    def happen_b(self):
        for player in self.most_stability():
            if player.name in self.points_lost_to_war:
                points = self.points_lost_to_war[player.name]
                self.match.log(f'{player} regains the {points} [Point{s_if_not_1(points)}] lost to war.')
                player.points += points
            else:
                self.match.log(f'{player} did not lose any points to war.')

class AttilaZoroastrianRevival(Age1EventCard):
    name_a = 'Attila'
    name_b = 'Zoroastrian revival'
    effect_a = 'Least [Military]: -3 [Gold]'
    effect_b = 'Most [Stability]: +4 [Stone] or others -3 [Food]'
    abbr = 'At_ZR'
    architects = 2
    famine = -3

    def happen_a(self):
        self.players_lose_resources(self.match.least_military(), Resources({Resource.GOLD: -3}))

    def happen_b(self):
        most_stability = self.most_stability()
        if most_stability:
            if len(most_stability) == 1:
                player = most_stability[0]
                choice = self.match.get_move(player, 'Gain 4 [Stone] or others lose 3 [Food]?', ('Gain 4 [Stone]', 'Others lose 3 [Food]'))
            else:
                self.sort_players(most_stability, Resource.STABILITY)
                player = most_stability[0]
                players = f'{most_stability[0]} and {most_stability[1]}'
                choice = self.match.get_move(player, f'{players} gain 4 [Stone] or others lose 3 [Food]?', ('4 [Stone]', 'Others lose 3 [Food]'))
            choosing_player = player
            if '[Stone]' in choice:
                for player in self.match.players[::-1]:
                    if player in most_stability:
                        self.match.log(f'{player} gains 4 [Stone].')
                        player.resources[Resource.STONE] += 4
            else:
                for player in self.match.players[::-1]:
                    if player not in most_stability:
                        self.match.log(f'{player} loses 3 [Food].')
                        player.lose_resources(Resources({Resource.FOOD: -3}))
            self.match.get_move(choosing_player, 'Confirm?', ('Confirm',))

class BreadAndGamesChristianity(Age1EventCard):
    name_a = 'Bread and Games'
    name_b = 'Christianity'
    effect_a = 'Most [Stability]: +3 [Food]'
    effect_b = 'All: May -4 [Food]: +6 [Books]'
    abbr = 'BG_Ch'
    architects = 2
    famine = 0

    def happen_a(self):
        self.players_gain_resources(self.most_stability(), Resources({Resource.FOOD: 3}))

    def happen_b(self):
        self.may_pay_to_gain(Resources({Resource.FOOD: 4}), Resources({Resource.BOOKS: 6}))

class HellenismAshokasConversion(Age1EventCard):
    name_a = 'Hellenism'
    name_b = 'Ashokas conversion'
    effect_a = 'Most [Military]: +2 [Stone]; Others: -2 [Food]'
    effect_b = 'All: May undeploy Military [Workers]: +2 [Books] for each'
    abbr = 'He_AC'
    architects = 0
    famine = -1

    def happen_a(self):
        most_military = self.most_military()
        self.players_gain_resources(most_military, Resources({Resource.STONE: 2}))
        for player in self.match.players[::-1]:
            if player not in most_military:
                self.match.log(f'{player} loses 2 [Food].')
                player.lose_resources(Resources({Resource.FOOD: -2}))

    def happen_b(self):
        def military_undeploys(player):
            possible_undeploys = player.undeploy_actions()
            return [undeploy for undeploy in possible_undeploys if undeploy.card.is_military()]
        for player in self.match.players[::-1]:
            possible_undeploys = military_undeploys(player)
            if not possible_undeploys:
                self.match.log(f'{player} has no military [Workers].')
            else:
                undeployed = False
                while possible_undeploys:
                    undeploy = self.match.get_move(player, 'Undeploy a military [Worker]?', possible_undeploys + ['Done'])
                    if undeploy == 'Done':
                        break
                    undeployed = True
                    player.undeploy_action(undeploy)
                    self.match.log(f'{player} gains 2 [Books].')
                    player.resources[Resource.BOOKS] += 2
                    possible_undeploys = military_undeploys(player)
                if not undeployed:
                    self.match.log(f'{player} declines.')
                self.match.get_move(player, 'Confirm?', ('Confirm',))

class PaxRomanaHandynasty(Age1EventCard):
    name_a = 'Pax Romana'
    name_b = 'Han dynasty'
    effect_a = 'Most [Military]: +1 [Point]'
    effect_b = 'Most [Stability]: May take 1 [Worker] and +3 [Food]'
    abbr = 'PR_HD'
    architects = 0
    famine = -2

    def happen_a(self):
        self.players_gain_point(self.most_military())

    def happen_b(self):
        for player in self.most_stability():
            if player.may_take_workers():
                answer = self.match.get_move(player, 'Take 1 [Worker] and gain 3 [Food]?', ('Yes', 'No'))
                if answer == 'Yes':
                    player.take_worker()
                    self.match.log(f'{player} gains 3 [Food].')
                    player.resources[Resource.FOOD] += 3
                else:
                    self.match.log(f'{player} declines.')
                self.match.get_move(player, 'Confirm?', ('Confirm',))
            else:
                self.match.log(f'{player} has no remaining [Workers] to take.')

class QinUnificationOlympicGames(Age1EventCard):
    name_a = 'Qin Unification'
    name_b = 'Olympic games'
    effect_a = 'All: if [Military] > War [Military]: +1 [Point]'
    effect_b = 'Most [Stability]: Go first'
    abbr = 'QU_OG'
    architects = 1
    famine = -1

    def happen_a(self):
        if self.match.war is None:
            self.match.log('No war.')
        else:
            any_benefit = False
            for player in self.match.players[::-1]:
                if player.resources[Resource.MILITARY] > self.match.war_value:
                    self.match.log(f'{player} gains 1 [Point].')
                    player.points += 1
                    any_benefit = True
            if not any_benefit:
                self.match.log('No players have [Military] > War [Military].')

    def happen_b(self):
        most_stability = self.most_stability()
        if len(most_stability) == 1:
            player = most_stability[0]
            self.match.log(f'{player} goes first.')
            self.match.players.remove(player)
            self.match.players.insert(0, player)
        elif len(most_stability) == 2:
            self.sort_players(most_stability, Resource.STABILITY)
            players = f'{most_stability[0]} and {most_stability[1]}'
            self.match.log(f'{players} go first.')
            self.match.players = most_stability + [player for player in self.match.players if player not in most_stability]

class RigvedaExodus(Age1EventCard):
    name_a = 'Rigveda'
    name_b = 'Exodus'
    effect_a = 'All: +1 [Book] per War and Battle one bought this round'
    effect_b = 'Most [Food]: +4 [Food]'
    abbr = 'Ri_Ex'
    architects = 0
    famine = -2

    def reset(self):
        super().reset()
        self.wars_battles_bought = collections.Counter()

    def reveal(self):
        self.prev_card = None
        self.register_for_event('bought card', self.any_war_or_battle, self.bought_war_or_battle)

    def any_war_or_battle(self, player, **kwargs):
        card = kwargs['card']
        seen = card is self.prev_card
        self.prev_card = card
        return kwargs['card'].is_war_battle() and not seen

    def bought_war_or_battle(self, player, **kwargs):
        self.wars_battles_bought[player.name] += 1

    def happen_a(self):
        if not self.wars_battles_bought:
            self.match.log('No wars or battles bought this round.')
        else:
            for player in self.match.players[::-1]:
                if player.name in self.wars_battles_bought:
                    books = self.wars_battles_bought[player.name]
                    self.match.log(f'{player} gains {books} [Book{s_if_not_1(books)}].')
                    player.resources[Resource.BOOKS] += books

    def happen_b(self):
        self.players_gain_resources(self.most_food(), Resources({Resource.FOOD: 4}))

class SeaPeoplesBronzeAgeCollapse(Age1EventCard):
    name_a = 'Sea Peoples'
    name_b = 'Bronze Age Collapse'
    effect_a = 'Least [Military]: Remove [Architect] or -1 [Point]'
    effect_b = 'All except most [Military] and/or [Stability]: -1 [Point]'
    abbr = 'SP_BAC'
    architects = 1
    famine = -2

    def happen_a(self):
        for player in self.match.least_military():
            has_wonder_under_construction = player.incomplete_wonder_stages() > 0
            has_architect = has_wonder_under_construction and player.wonders_under_construction[0].completed_stages > 0
            has_points = player.points > 0
            if has_architect and has_points:
                choice = self.match.get_move(player, 'Remove [Architect] or -1 [Point]?', ('Remove [Architect]', '-1 [Point]'))
                if choice == 'Remove [Architect]':
                    self.match.log(f'{player} removes [Architect].')
                    player.wonders_under_construction[0].completed_stages -= 1
                else:
                    self.match.log(f'{player} loses 1 [Point].')
                    player.points -= 1
                self.match.get_move(player, 'Confirm?', ('Confirm',))
            elif has_architect:
                self.match.log(f'{player} removes [Architect].')
                player.wonders_under_construction[0].completed_stages -= 1
            else:
                player.lose_point()

    def happen_b(self):
        most_military = self.match.most_military()
        most_stability = self.match.most_stability()
        mosts = most_military + most_stability
        players = [player for player in self.match.players[::-1] if player not in mosts]
        if not players:
            self.match.log('All players have either most [Military] or most [Stability].')
        else:
            for player in players:
                player.lose_point()

class ShangOracleBonesIonianColonisation(Age1EventCard):
    name_a = 'Shang Oracle Bones'
    name_b = 'Ionian Colonisation'
    effect_a = 'Least [Stability]: -3 [Books]'
    effect_b = 'Most [Food]: +3 [Gold]'
    abbr = 'SOB_IC'
    architects = 1
    famine = -1

    def happen_a(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.BOOKS: -3}))

    def happen_b(self):
        self.players_gain_resources(self.most_food(), Resources({Resource.GOLD: 3}))

class TaoismPhilosophy(Age1EventCard):
    name_a = 'Taoism'
    name_b = 'Philosophy'
    effect_a = 'First to Pass: +3 [Books]'
    effect_b = 'Most [Stability]: +1 [Point]'
    abbr = 'Ta_Ph'
    architects = 1
    famine = -1

    def happen_a(self):
        for player in self.match.players[::-1]:
            if player.passed_first:
                self.match.log(f'{player} gains 3 [Books].')
                player.resources[Resource.BOOKS] += 3

    def happen_b(self):
        self.players_gain_point(self.most_stability())

class YellowTurbanRebellionSpartacusRevolt(Age1EventCard):
    name_a = 'Yellow Turban Rebellion'
    name_b = 'Spartacus revolt'
    effect_a = 'Least [Military]: -3 [Food]'
    effect_b = 'Least [Stability]: Go last and -1 [Gold]'
    abbr = 'YTR_SR'
    architects = 1
    famine = -2

    def happen_a(self):
        self.players_lose_resources(self.match.least_military(), Resources({Resource.FOOD: -3}))

    def happen_b(self):
        self.least_stability_goes_last_and_loses_resources(Resources({Resource.GOLD: -1}))

class Age2EventCard(EventCard):
    age = 2

class BenedictineRulePaperMoney(Age2EventCard):
    name_a = 'Benedictine Rule'
    name_b = 'Paper Money'
    effect_a = 'Most [Stability]: +4 [Food]'
    effect_b = 'All: May -3 [Food]: +5 [Gold]'
    abbr = 'BR_PM'
    architects = 3
    famine = -1

    def happen_a(self):
        self.players_gain_resources(self.most_stability(), Resources({Resource.FOOD: 4}))

    def happen_b(self):
        self.may_pay_to_gain(Resources({Resource.FOOD: 3}), Resources({Resource.GOLD: 5}))

class BlackDeathHuntForPresterJohn(Age2EventCard):
    name_a = 'Black Death'
    name_b = 'Hunt for Prester John'
    effect_a = 'All: Return 1 [Worker]'
    effect_b = 'Most [Military]: +3 [Books]'
    abbr = 'BD_HPJ'
    architects = 1
    famine = -3

    def happen_a(self):
        for player in self.match.players[::-1]:
            if player.grown_workers:
                player.return_worker()
            else:
                self.match.log(f'{player} has no workers to return.')

    def happen_b(self):
        self.players_gain_resources(self.most_military(), Resources({Resource.BOOKS: 3}))

class ChansonDeRolandZanjRevolt(Age2EventCard):
    name_a = 'Chanson de Roland'
    name_b = 'Zanj Revolt'
    effect_a = 'Least [Military]: -1 [Book]; Most [Military]: +3 [Books]'
    effect_b = 'Least [Stability]: Go last and -2 [Food]'
    abbr = 'CR_ZR'
    architects = 1
    famine = -3

    def happen_a(self):
        self.players_lose_resources(self.match.least_military(), Resources({Resource.BOOKS: -1}))
        self.players_gain_resources(self.most_military(), Resources({Resource.BOOKS: 3}))

    def happen_b(self):
        self.least_stability_goes_last_and_loses_resources(Resources({Resource.FOOD: -2}))

class EcologicalCollapseCasteSystem(Age2EventCard):
    name_a = 'Ecological Collapse'
    name_b = 'Caste system'
    effect_a = 'All: -2 [Food] or go last'
    effect_b = 'Least [Stability]: -4 [Books]'
    abbr = 'EC_CS'
    architects = 2
    famine = -4

    def happen_a(self):
        going_last = []
        for player in self.match.players[::-1]:
            if player.resources[Resource.FOOD] < 2:
                self.match.log(f'{player} must go last.')
                going_last.append(player)
            else:
                choice = self.match.get_move(player, '-2 [Food] or go last?', ('-2 [Food]', 'Go last'))
                if choice == '-2 [Food]':
                    self.match.log(f'{player} loses 2 [Food].')
                    player.lose_resources(Resources({Resource.FOOD: -2}))
                else:
                    self.match.log(f'{player} will go last.')
                    going_last.append(player)
                self.match.get_move(player, 'Confirm?', ('Confirm',))
        if going_last and len(going_last) != len(self.match.players):
            going_last = going_last[::-1]
            self.match.players = [player for player in self.match.players if player not in going_last] + going_last
            players = ', '.join(str(player) for player in self.match.players)
            self.match.log(f'New player order: {players}')
        else:
            self.match.log('No change in player order.')

    def happen_b(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.BOOKS: -4}))

class FeudalDuesHajjFromMali(Age2EventCard):
    name_a = 'Feudal dues'
    name_b = 'Hajj from Mali'
    effect_a = 'All: No change in player order this round'
    effect_b = 'Least [Stability]: Lose all [Gold] except 2'
    abbr = 'FD_HM'
    architects = 0
    famine = -2

    def reveal(self):
        self.register_for_event('skip player order', self.true, self.true)

    def happen_a(self):
        pass

    def happen_b(self):
        for player in self.match.least_stability():
            if player.resources[Resource.GOLD] <= 2:
                self.match.log(f'{player} does not have more than 2 [Gold].')
            else:
                self.match.log(f'{player} loses all [Gold] except 2.')
                player.resources[Resource.GOLD] = 2

class FourthCrusadeSongResistance(Age2EventCard):
    name_a = 'Fourth Crusade'
    name_b = 'Song Resistance'
    effect_a = 'Most [Military]: May -3 [Gold]: +1 [Point] and least [Military]: -4 [Books]'
    effect_b = 'Most [Stability]: Regain all [Food] [Stone] [Gold] [Books] [Points] lost to War this round'
    abbr = 'FC_SR'
    architects = 1
    famine = -2

    def reset(self):
        super().reset()
        self.points_lost_to_war = collections.Counter()
        self.resources_lost_to_war = {}

    def reveal(self):
        self.register_for_event('lost to war', self.true, self.lost_to_war)

    def lost_to_war(self, player, **kwargs):
        if 'points' in kwargs:
            self.points_lost_to_war[player.name] += kwargs['points']
        if 'resources' in kwargs:
            try:
                self.resources_lost_to_war[player.name] += kwargs['resources']
            except KeyError:
                self.resources_lost_to_war[player.name] = Resources(kwargs['resources'])

    def happen_a(self):
        most_military = self.most_military()
        if most_military:
            if len(most_military) == 1:
                choosing_player = most_military[0]
                other_most_military = []
            else:
                self.sort_players(most_military, Resource.MILITARY)
                choosing_player = most_military[0]
                other_most_military = most_military[1:]
            if choosing_player.resources[Resource.GOLD] < 3:
                self.match.log(f'{choosing_player} does not have at least 3 [Gold].')
                self.match.log('Least military will not lose [Books].')
                least_lose = False
            else:
                answer = self.match.get_move(choosing_player, 'Pay 3 [Gold] for 1 [Point] and least military loses 4 [Books]?', ('Yes', 'No'))
                least_lose = answer == 'Yes'
                if least_lose:
                    self.match.log(f'{choosing_player} pays 3 [Gold] and gains 1 [Point].')
                    choosing_player.resources[Resource.GOLD] -= 3
                    choosing_player.points += 1
                    if choosing_player.resources[Resource.GOLD] == 0:
                        self.match.events['spent last gold'].happen(choosing_player)
                    self.match.log('Least military will lose 4 [Books].')
                else:
                    self.match.log(f'{choosing_player} declines.')
                    self.match.log('Least military will not lose [Books].')
                self.match.get_move(choosing_player, 'Confirm?', ('Confirm',))
            if least_lose:
                for player in other_most_military:
                    if player.resources[Resource.GOLD] < 3:
                        self.match.log(f'{player} does not have at least 3 [Gold].')
                    else:
                        answer = self.match.get_move(player, f'Pay 3 [Gold] for 1 [Point]? (Least military will still lose 4 [Books].)', ('Yes', 'No'))
                        if answer == 'Yes':
                            self.match.log(f'{player} pays 3 [Gold] and gains 1 [Point].')
                            player.resources[Resource.GOLD] -= 3
                            player.points += 1
                            if player.resources[Resource.GOLD] == 0:
                                self.match.events['spent last gold'].happen(player)
                        else:
                            self.match.log(f'{player} declines.')
                        self.match.get_move(player, 'Confirm?', ('Confirm',))
                for player in self.match.least_military():
                    self.match.log(f'{player} loses 4 [Books].')
                    player.lose_resources(Resources({Resource.BOOKS: -4}))
            else:
                for player in other_most_military:
                    self.match.log(f'{choosing_player} declined, so {player} does not get a choice.')

    def happen_b(self):
        for player in self.most_stability():
            if player.name in self.points_lost_to_war or player.name in self.resources_lost_to_war:
                points = 0
                resources = Resources()
                gain = ''
                if player.name in self.points_lost_to_war:
                    points = self.points_lost_to_war[player.name]
                    gain += f'{points} [Point{s_if_not_1(points)}]'
                if player.name in self.resources_lost_to_war:
                    resources += self.resources_lost_to_war[player.name]
                    if gain:
                        gain += ' and '
                    gain += f'{resources}'
                self.match.log(f'{player} regains the {gain} lost to war.')
                player.points += points
                player.resources += resources
            else:
                self.match.log(f'{player} did not lose any points or resources to war.')

class ImperialExaminationJustinianCode(Age2EventCard):
    name_a = 'Imperial Examination'
    name_b = 'Justinian Code'
    effect_a = 'All with a Medieval Advisor: +1 [Point]'
    effect_b = 'Most [Stability]: +1 [Point]'
    abbr = 'IE_JC'
    architects = 1
    famine = 0

    def happen_a(self):
        any_have_medieval_advisor = False
        for player in self.match.players[::-1]:
            for card in player.advisor_cards():
                if card.age == 2:
                    self.match.log(f'{player} gains 1 [Point].')
                    player.points += 1
                    any_have_medieval_advisor = True
                    break
        if not any_have_medieval_advisor:
            self.match.log('No player has a Medieval advisor.')

    def happen_b(self):
        self.players_gain_point(self.most_stability())

class MartyrdomOfAliScholasticism(Age2EventCard):
    name_a = 'Martyrdom of Ali'
    name_b = 'Scholasticism'
    effect_a = 'Least [Military]: -1 [Point]'
    effect_b = 'Most [Stability]: +3 [Books]'
    abbr = 'MA_Sc'
    architects = 1
    famine = -1

    def happen_a(self):
        for player in self.match.least_military():
            player.lose_point()

    def happen_b(self):
        self.players_gain_resources(self.most_stability(), Resources({Resource.BOOKS: 3}))

class PeaceOfGodCouncilOfClermont(Age2EventCard):
    name_a = 'Peace of God'
    name_b = 'Council of Clermont'
    effect_a = 'Most [Military]: If War was bought by another Nation: +4 [Books]'
    effect_b = 'All: +1 [Point] per Medieval Colony'
    abbr = 'PG_CC'
    architects = 0
    famine = -2

    def reset(self):
        super().reset()
        self.warmonger = None

    def reveal(self):
        self.register_for_event('bought card', self.any_war, self.bought_war)

    def any_war(self, player, **kwargs):
        return kwargs['card'].is_war()

    def bought_war(self, player, **kwargs):
        self.warmonger = player

    def happen_a(self):
        most_military = self.match.most_military()
        if self.match.war is None:
            self.match.log('No war.')
        elif not most_military:
            self.match.log('No most [Military].')
        else:
            for player in most_military:
                if player is self.warmonger:
                    self.match.log(f'{player} has most [Military] but bought the war.')
                else:
                    self.match.log(f'{player} gains 4 [Books].')
                    player.resources[Resource.BOOKS] += 4

    def happen_b(self):
        any_have_medieval_colony = False
        for player in self.match.players[::-1]:
            points = 0
            for card in player.colony_cards():
                if card.age == 2:
                    points += 1
            if points > 0:
                self.match.log(f'{player} gains {points} [Point{s_if_not_1(points)}].')
                player.points += points
                any_have_medieval_colony = True
        if not any_have_medieval_colony:
            self.match.log('No player has a Medieval colony.')

class RaidOnLindisfarneIconoclasm(Age2EventCard):
    name_a = 'Raid on Lindisfarne'
    name_b = 'Iconoclasm'
    effect_a = 'Least [Military]: -4 [Gold]'
    effect_b = 'Least [Stability]: -2 [Food], -2 [Gold]'
    abbr = 'RL_Ic'
    architects = 2
    famine = -1

    def happen_a(self):
        self.players_lose_resources(self.match.least_military(), Resources({Resource.GOLD: -4}))

    def happen_b(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.FOOD: -2, Resource.GOLD: -2}))

class SackOfBaghdadHanseaticSaltTrade(Age2EventCard):
    name_a = 'Sack of Baghdad'
    name_b = 'Hanseatic Salt Trade'
    effect_a = 'Least [Military]: -5 [Books]'
    effect_b = 'Most [Food]: +4 [Gold]'
    abbr = 'SB_HST'
    architects = 0
    famine = -2

    def happen_a(self):
        self.players_lose_resources(self.match.least_military(), Resources({Resource.BOOKS: -5}))

    def happen_b(self):
        self.players_gain_resources(self.most_food(), Resources({Resource.GOLD: 4}))

class StuporMundiGreatSchism(Age2EventCard):
    name_a = 'Stupor Mundi'
    name_b = 'Great Schism'
    effect_a = 'Most bought Golden Ages this round: +4 [Books]'
    effect_b = 'Least [Stability]: -3 [Gold]'
    abbr = 'SM_GS'
    architects = 2
    famine = -1

    def reset(self):
        super().reset()
        self.golden_ages_bought = collections.Counter()

    def reveal(self):
        self.register_for_event('bought card', self.any_golden_age, self.bought_golden_age)

    def any_golden_age(self, player, **kwargs):
        return kwargs['card'].is_golden_age()

    def bought_golden_age(self, player, **kwargs):
        self.golden_ages_bought[player.name] += 1

    def happen_a(self):
        if not self.golden_ages_bought:
            self.match.log('No golden ages were bought this round.')
        else:
            most_golden_ages_bought = self.match.most_least(self.golden_ages_bought)[0]
            if not most_golden_ages_bought:
                self.match.log('No most golden ages bought.')
            else:
                for player in most_golden_ages_bought:
                    self.match.log(f'{player} gains 4 [Books].')
                    player.resources[Resource.BOOKS] += 4

    def happen_b(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.GOLD: -3}))

class Age3EventCard(EventCard):
    age = 3

class AbsoluteMonarchySalemWitchTrials(Age3EventCard):
    name_a = 'Absolute Monarchy'
    name_b = 'Salem Witch Trials'
    effect_a = 'All Nations with Antiquity or Medieval Advisor: -4 [Books]'
    effect_b = 'Least [Stability]: -3 [Gold] or remove Advisor'
    abbr = 'AM_SWT'
    architects = 2
    famine = -5

    def happen_a(self):
        any_have_antiquity_or_medieval_advisor = False
        for player in self.match.players[::-1]:
            for card in player.advisor_cards():
                if card.age in (1, 2):
                    self.match.log(f'{player} loses 4 [Books].')
                    player.lose_resources(Resources({Resource.BOOKS: -4}))
                    any_have_antiquity_or_medieval_advisor = True
                    break
        if not any_have_antiquity_or_medieval_advisor:
            self.match.log('No player has an Antiquity or Medieval advisor.')

    def happen_b(self):
        for player in self.match.least_stability():
            has_advisor = False
            if player.removable_advisor_cards():
                has_advisor = True
            has_3_gold = player.resources[Resource.GOLD] >= 3
            remove_advisors = False
            if has_advisor and not has_3_gold:
                remove_advisors = True
            elif not has_advisor:
                remove_advisors = False
            else:
                choice = self.match.get_move(player, 'Lose 3 [Gold] or remove advisors?', ('-3 [Gold]', 'remove advisors'))
                if choice == 'remove advisors':
                    remove_advisors = True
            if remove_advisors:
                self.match.log(f'{player} removes advisors.')
                player.remove_all_advisors()
            else:
                self.match.log(f'{player} loses 3 [Gold].')
                player.lose_resources(Resources({Resource.GOLD: -3}))
            if player.need_confirmation:
                self.match.get_move(player, 'Confirm?', ('Confirm',))

class AfricanSlaveTradeGloriousRevolution(Age3EventCard):
    name_a = 'African Slave Trade'
    name_b = 'Glorious revolution'
    effect_a = 'Least [Military]: -1 [Point]'
    effect_b = 'Most [Stability]: May go last: +6 [Gold]'
    abbr = 'AST_GR'
    architects = 1
    famine = -4

    def happen_a(self):
        for player in self.match.least_military():
            player.lose_point()

    def happen_b(self):
        most_stability = self.most_stability()
        if len(most_stability) == 1:
            player = most_stability[0]
            answer = self.match.get_move(player, 'Go last and gain 6 [Gold]?', ('Yes', 'No'))
            if answer == 'Yes':
                self.match.log(f'{player} goes last and gains 6 [Gold].')
                self.match.players.remove(player)
                self.match.players.append(player)
                player.resources[Resource.GOLD] += 6
            else:
                self.match.log(f'{player} declines.')
            self.match.get_move(player, 'Confirm?', ('Confirm',))
        elif len(most_stability) == 2:
            self.sort_players(most_stability, Resource.STABILITY)
            went_last = []
            for player in most_stability[::-1]:
                answer = self.match.get_move(player, 'Go last and gain 6 [Gold]?', ('Yes', 'No'))
                if answer == 'Yes':
                    self.match.log(f'{player} goes last and gains 6 [Gold].')
                    player.resources[Resource.GOLD] += 6
                    went_last.insert(0, player)
                else:
                    self.match.log(f'{player} declines.')
                self.match.get_move(player, 'Confirm?', ('Confirm',))
            self.match.players = [player for player in self.match.players if player not in went_last] + went_last

class BlackbeardHabeasCorpusAct(Age3EventCard):
    name_a = 'Blackbeard'
    name_b = 'Habeas Corpus Act'
    effect_a = 'Least [Military]: -5 [Gold]'
    effect_b = 'Most [Stability]: +1 [Point]'
    abbr = 'Bl_HCA'
    architects = 1
    famine = -2

    def happen_a(self):
        self.players_lose_resources(self.match.least_military(), Resources({Resource.GOLD: -5}))

    def happen_b(self):
        self.players_gain_point(self.most_stability())

class ColumbianExchangeExpulsionOfJews(Age3EventCard):
    name_a = 'Columbian Exchange'
    name_b = 'Expulsion of Jews'
    effect_a = 'Most [Military]: +3 [Food]; Least [Military]: -3 [Food]'
    effect_b = 'Least [Stability]: -5 [Gold]'
    abbr = 'CE_EJ'
    architects = 1
    famine = -1

    def happen_a(self):
        self.players_gain_resources(self.most_military(), Resources({Resource.FOOD: 3}))
        self.players_lose_resources(self.match.least_military(), Resources({Resource.FOOD: -3}))

    def happen_b(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.GOLD: -5}))

class CropRotationMercantilism(Age3EventCard):
    name_a = 'Crop Rotation'
    name_b = 'Mercantilism'
    effect_a = 'Most [Stability]: +6 [Food]'
    effect_b = 'All: May undeploy Building [Workers]: +2 [Stone] for each'
    abbr = 'CR_Me'
    architects = 2
    famine = -4

    def happen_a(self):
        self.players_gain_resources(self.most_stability(), Resources({Resource.FOOD: 6}))

    def happen_b(self):
        def building_undeploys(player):
            possible_undeploys = player.undeploy_actions()
            return [undeploy for undeploy in possible_undeploys if undeploy.card.is_building()]
        for player in self.match.players[::-1]:
            possible_undeploys = building_undeploys(player)
            if not possible_undeploys:
                self.match.log(f'{player} has no building [Workers].')
            else:
                while possible_undeploys:
                    undeploy = self.match.get_move(player, 'Undeploy a building [Worker]?', possible_undeploys + ['Done'])
                    if undeploy == 'Done':
                        break
                    player.undeploy_action(undeploy)
                    self.match.log(f'{player} gains 2 [Stone].')
                    player.resources[Resource.STONE] += 2
                    possible_undeploys = building_undeploys(player)
                self.match.get_move(player, 'Confirm?', ('Confirm',))

class JanissariesCouncilOfTrent(Age3EventCard):
    name_a = 'Janissaries'
    name_b = 'Council of Trent'
    effect_a = 'Most [Military]: May take 2 [Workers] and +4 [Stone]'
    effect_b = 'Most [Stability]: +5 [Stone]'
    abbr = 'Ja_CT'
    architects = 1
    famine = -2

    def happen_a(self):
        for player in self.most_military():
            if player.may_take_workers(2):
                answer = self.match.get_move(player, 'Take 2 [Workers] and gain 4 [Stone]?', ('Yes', 'No'))
                if answer == 'Yes':
                    player.take_worker()
                    player.take_worker()
                    self.match.log(f'{player} gains 4 [Stone].')
                    player.resources[Resource.STONE] += 4
                else:
                    self.match.log(f'{player} declines.')
                self.match.get_move(player, 'Confirm?', ('Confirm',))
            else:
                self.match.log(f'{player} does not have at least 2 [Workers] to take.')

    def happen_b(self):
        self.players_gain_resources(self.most_stability(), Resources({Resource.STONE: 5}))

class LittleIceAgeCityUponAHill(Age3EventCard):
    name_a = 'Little Ice Age'
    name_b = 'City Upon a Hill'
    effect_a = 'All: -3 [Food] or -5 [Books]'
    effect_b = 'Most [Stability]: +6 [Books]'
    abbr = 'LIA_CUH'
    architects = 1
    famine = -3

    def happen_a(self):
        for player in self.match.players[::-1]:
            has_3_food = player.resources[Resource.FOOD] >= 3
            has_5_books = player.resources[Resource.BOOKS] >= 5
            lose_food = False
            if has_3_food and not has_5_books:
                lose_food = True
            elif not has_3_food:
                lose_food = False
            else:
                choice = self.match.get_move(player, 'Lose 3 [Food] or 5 [Books]?', ('-3 [Food]', '-5 [Books]'))
                if choice == '-3 [Food]':
                    lose_food = True
            if lose_food:
                self.match.log(f'{player} loses 3 [Food].')
                player.lose_resources(Resources({Resource.FOOD: -3}))
            else:
                self.match.log(f'{player} loses 5 [Books].')
                player.lose_resources(Resources({Resource.BOOKS: -5}))
            if player.need_confirmation:
                self.match.get_move(player, 'Confirm?', ('Confirm',))

    def happen_b(self):
        self.players_gain_resources(self.most_stability(), Resources({Resource.BOOKS: 6}))

class MagellansExpeditionPapalIndulgence(Age3EventCard):
    name_a = 'Magellan\'s expedition'
    name_b = 'Papal Indulgence'
    effect_a = 'All: +5 [Gold] per Colony bought this round'
    effect_b = 'Most [Stability]: May hire 1 [Architect] for free; Others: -2 [Gold]'
    abbr = 'ME_PI'
    architects = 2
    famine = -3

    def reset(self):
        super().reset()
        self.colonies_bought = collections.Counter()

    def reveal(self):
        self.register_for_event('bought card', self.any_colony, self.bought_colony)

    def any_colony(self, player, **kwargs):
        return kwargs['card'].is_colony()

    def bought_colony(self, player, **kwargs):
        self.colonies_bought[player.name] += 1

    def happen_a(self):
        if not self.colonies_bought:
            self.match.log('No colonies bought this round.')
        else:
            for player in self.match.players[::-1]:
                if player.name in self.colonies_bought:
                    gold = 5 * self.colonies_bought[player.name]
                    self.match.log(f'{player} gains {gold} [Gold].')
                    player.resources[Resource.GOLD] += gold

    def happen_b(self):
        most_stability = self.most_stability()
        for player in most_stability:
            if player.incomplete_wonder_stages():
                answer = self.match.get_move(player, 'Hire 1 [Architect] for free?', ('Yes', 'No'))
                if answer == 'Yes':
                    card = player.wonders_under_construction[0]
                    self.match.log(f'{player} hires a free architect for "{card}".')
                    player.hire_free_architect(card)
                else:
                    self.match.log(f'{player} declines.')
                self.match.get_move(player, 'Confirm?', ('Confirm',))
            else:
                self.match.log(f'{player} has no wonders under construction.')
        for player in self.match.players[::-1]:
            if player not in most_stability:
                self.match.log(f'{player} loses 2 [Gold].')
                player.lose_resources(Resources({Resource.GOLD: -2}))

class PilgrimsDutchRevolt(Age3EventCard):
    name_a = 'Pilgrims'
    name_b = 'Dutch Revolt'
    effect_a = 'Most [Food]: Take 1 [Worker]'
    effect_b = 'Least [Stability]: Go last and -3 [Gold]'
    abbr = 'Pi_DR'
    architects = 3
    famine = -3

    def happen_a(self):
        for player in self.most_food():
            if player.may_take_workers():
                player.take_worker()
                if player.need_confirmation:
                    self.match.get_move(player, 'Confirm?', ('Confirm',))
            else:
                self.match.log(f'{player} has no remaining [Workers] to take.')

    def happen_b(self):
        self.least_stability_goes_last_and_loses_resources(Resources({Resource.GOLD: -3}))

class SinkingOfTheVasaPeaceOfWestphalia(Age3EventCard):
    name_a = 'Sinking of the Vasa'
    name_b = 'Peace of Westphalia'
    effect_a = 'Least [Stability]: -3 [Gold] or -10 [Military] for "Peace of Westphalia"'
    effect_b = 'Least [Military]: -5 [Food]'
    abbr = 'SV_PW'
    architects = 0
    famine = 0

    def happen_a(self):
        self.strength_reduced_players = []
        for player in self.match.least_stability():
            has_3_gold = player.resources[Resource.GOLD] >= 3
            has_10_military = player.resources[Resource.MILITARY] >= 10
            lose_gold = False
            if has_3_gold and not has_10_military:
                lose_gold = True
            elif not has_3_gold:
                lose_gold = False
            else:
                choice = self.match.get_move(player, 'Lose 3 [Gold] or be considered to have 10 less [Military] during "Peace of Westphalia"?', ('-3 [Gold]', '-10 [Military]'))
                if choice == '-3 [Gold]':
                    lose_gold = True
            if lose_gold:
                self.match.log(f'{player} loses 3 [Gold].')
                player.lose_resources(Resources({Resource.GOLD: -3}))
            else:
                self.match.log(f'{player} will be considered to have 10 less [Military] during "Peace of Westphalia".')
                self.strength_reduced_players.append(player)
            if player.need_confirmation:
                self.match.get_move(player, 'Confirm?', ('Confirm',))

    def happen_b(self):
        for player in self.strength_reduced_players:
            player.resources[Resource.MILITARY] -= 10
        for player in self.match.most_least_of_resource(Resource.MILITARY)[1]:
            self.match.log(f'{player} loses 5 [Food].')
            player.lose_resources(Resources({Resource.FOOD: -5}))
        for player in self.strength_reduced_players:
            player.resources[Resource.MILITARY] += 10

class SpiceTradeMuntzerRevolt(Age3EventCard):
    name_a = 'Spice Trade'
    name_b = 'Muntzer Revolt'
    effect_a = 'Most [Food]: +4 [Gold]'
    effect_b = 'Least [Stability]: Go last and -3 [Stone]'
    abbr = 'ST_MR'
    architects = 0
    famine = -2

    def happen_a(self):
        self.players_gain_resources(self.most_food(), Resources({Resource.GOLD: 4}))

    def happen_b(self):
        self.least_stability_goes_last_and_loses_resources(Resources({Resource.STONE: -3}))

class TulipManiaKangxiEra(Age3EventCard):
    name_a = 'Tulip Mania'
    name_b = 'Kangxi Era'
    effect_a = 'Last to Pass: -1 [Point]'
    effect_b = 'Most [Stability]: Go first and +3 [Gold]'
    abbr = 'TM_KE'
    architects = 0
    famine = -1

    def happen_a(self):
        for player in self.match.players[::-1]:
            if player.passed_last:
                player.lose_point()

    def happen_b(self):
        most_stability = self.most_stability()
        if len(most_stability) == 1:
            player = most_stability[0]
            self.match.log(f'{player} goes first and gains 3 [Gold].')
            self.match.players.remove(player)
            self.match.players.insert(0, player)
            player.resources[Resource.GOLD] += 3
        elif len(most_stability) == 2:
            self.sort_players(most_stability, Resource.STABILITY)
            players = f'{most_stability[0]} and {most_stability[1]}'
            self.match.log(f'{players} go first and gain 3 [Gold].')
            self.match.players = most_stability + [player for player in self.match.players if player not in most_stability]
            for player in most_stability:
                player.resources[Resource.GOLD] += 3

class Age4EventCard(EventCard):
    age = 4

class AmericanRevolutionFrenchRevolution(Age4EventCard):
    name_a = 'American revolution'
    name_b = 'French Revolution'
    effect_a = 'Least [Military]: Remove Colony, if none: -1 [Point]'
    effect_b = 'Least [Stability]: Remove Advisor, if none: -2 [Points]'
    abbr = 'AR_FR'
    architects = 1
    famine = -2

    def happen_a(self):
        for player in self.match.least_military():
            colonies = player.colony_cards()
            if colonies:
                if len(colonies) == 1:
                    colony = colonies[0]
                else:
                    colony = self.match.get_move(player, 'Remove which colony?', colonies)
                self.match.log(f'{player} removes "{colony}".')
                player.remove(colony)
                if player.need_confirmation:
                    self.match.get_move(player, 'Confirm?', ('Confirm',))
            else:
                self.match.log(f'{player} has no colonies.')
                player.lose_point()

    def happen_b(self):
        for player in self.match.least_stability():
            if player.removable_advisor_cards():
                self.match.log(f'{player} removes advisors.')
                player.remove_all_advisors()
            else:
                self.match.log(f'{player} has no advisors.')
                if player.points >= 2:
                    self.match.log(f'{player} loses 2 [Points].')
                    player.points -= 2
                elif player.points == 1:
                    self.match.log(f'{player} loses only remaining [Point].')
                    player.points -= 1
                else:
                    self.match.log(f'{player} is spared the [Point] loss.')

class AnarchismGreatExhibition(Age4EventCard):
    name_a = 'Anarchism'
    name_b = 'Great Exhibition'
    effect_a = 'Least [Military]: Remove Advisors and -1 [Point]'
    effect_b = 'Most [Stability]: May hire 2 [Architects] for free'
    abbr = 'An_GE'
    architects = 1
    famine = -4

    def happen_a(self):
        for player in self.match.least_military():
            self.match.log(f'{player} removes advisors.')
            player.remove_all_advisors()
            player.lose_point()

    def happen_b(self):
        for player in self.most_stability():
            self.match.log(f'{player} may hire up to 2 [Architects] for free.')
            for i in range(2):
                if player.incomplete_wonder_stages():
                    answer = self.match.get_move(player, 'Hire [Architect] for free?', ('Yes', 'No'))
                    if answer == 'Yes':
                        card = player.wonders_under_construction[0]
                        self.match.log(f'{player} hires a free architect for "{card}".')
                        player.hire_free_architect(card)
                    else:
                        self.match.log(f'{player} declines.')
                    self.match.get_move(player, 'Confirm?', ('Confirm',))
                    if answer == 'No':
                        break
                else:
                    self.match.log(f'{player} has no wonders under construction.')
                    break

class CalifornianGoldRushIrishPotatoBlight(Age4EventCard):
    name_a = 'Californian Gold Rush'
    name_b = 'Irish Potato Blight'
    effect_a = 'Most [Military]: +8 [Gold]'
    effect_b = 'Least [Stability]: -8 [Food]'
    abbr = 'CGR_IPB'
    architects = 0
    famine = -3

    def happen_a(self):
        self.players_gain_resources(self.most_military(), Resources({Resource.GOLD: 8}))

    def happen_b(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.FOOD: -8}))

class EntenteCordialeGeneralStrike(Age4EventCard):
    name_a = 'Entente Cordiale'
    name_b = 'General strike'
    effect_a = 'Most [Military]: May deploy 2 [Workers] to Military for free'
    effect_b = 'Least [Stability]: -6 [Stone]'
    abbr = 'EC_GS'
    architects = 2
    famine = -4

    def happen_a(self):
        def military_deploys(player):
            possible_deploys = player.deploy_actions()
            return [deploy for deploy in possible_deploys if deploy.card.is_military()]
        for player in self.most_military():
            if player.military_cards():
                for i in range(2):
                    answer = self.match.get_move(player, 'Deploy [Worker] to military for free?', ('Yes', 'No'))
                    if answer == 'No':
                        break
                    if player.workers == 0:
                        possible_undeploys = player.undeploy_actions()
                        if len(possible_undeploys) == 1:
                            undeploy = possible_undeploys[0]
                        else:
                            undeploy = self.match.get_move(player, 'Undeploy [Worker] from where?', possible_undeploys)
                        player.undeploy_action(undeploy)
                    possible_deploys = military_deploys(player)
                    if not possible_deploys:
                        raise InvalidMove('No room on militaries.')
                    if len(possible_deploys) == 1:
                        deploy = possible_deploys[0]
                    else:
                        deploy = self.match.get_move(player, 'Deploy [Worker] where?', possible_deploys)
                    player.deploy_for_free(deploy.card)
                self.match.get_move(player, 'Confirm?', ('Confirm',))
            else:
                self.match.log(f'{player} has no militaries.')

    def happen_b(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.STONE: -6}))

class EruptionOfKrakatoaFirstVaticanCouncil(Age4EventCard):
    name_a = 'Eruption of Krakatoa'
    name_b = 'First Vatican Council'
    effect_a = 'Least [Food]: -1 [Point]'
    effect_b = 'Most [Stability]: +10 [Books]'
    abbr = 'EK_FVC'
    architects = 1
    famine = -3

    def happen_a(self):
        for player in self.match.least_food():
            player.lose_point()

    def happen_b(self):
        self.players_gain_resources(self.most_stability(), Resources({Resource.BOOKS: 10}))

class MarchToMoscowTaipingRebellion(Age4EventCard):
    name_a = 'March to Moscow'
    name_b = 'Taiping Rebellion'
    effect_a = 'Least [Food]: Remove Colony, if none: -1 [Point]'
    effect_b = 'Least [Stability]: Go last and -10 [Books]'
    abbr = 'MM_TR'
    architects = 1
    famine = -5

    def happen_a(self):
        for player in self.match.least_food():
            colonies = player.colony_cards()
            if colonies:
                if len(colonies) == 1:
                    colony = colonies[0]
                else:
                    colony = self.match.get_move(player, 'Remove which colony?', colonies)
                self.match.log(f'{player} removes "{colony}".')
                player.remove(colony)
                if player.need_confirmation:
                    self.match.get_move(player, 'Confirm?', ('Confirm',))
            else:
                self.match.log(f'{player} has no colonies.')
                player.lose_point()

    def happen_b(self):
        self.least_stability_goes_last_and_loses_resources(Resources({Resource.BOOKS: -10}))

class RomanticismIndustrialRevolution(Age4EventCard):
    name_a = 'Romanticism'
    name_b = 'Industrial Revolution'
    effect_a = 'First to Pass: +5 [Books]'
    effect_b = 'Most [Workers] in Industrial Buildings: +1 [Point]'
    abbr = 'Ro_IR'
    architects = 2
    famine = -6

    def happen_a(self):
        for player in self.match.players[::-1]:
            if player.passed_first:
                self.match.log(f'{player} gains 5 [Books].')
                player.resources[Resource.BOOKS] += 5

    def happen_b(self):
        workers_in_industrial_buildings = {}
        for player in self.match.players:
            workers_in_industrial_buildings[player.name] = sum(card.deployed_workers for card in player.building_cards() if card.age == 4)
        most_workers_in_industrial_buildings = self.match.most_least(workers_in_industrial_buildings)[0]
        for player in most_workers_in_industrial_buildings:
            self.match.log(f'{player} gains 1 [Point].')
            player.points += 1

class ScrambleForAfricaDreyfusAffair(Age4EventCard):
    name_a = 'Scramble for Africa'
    name_b = 'Dreyfus Affair'
    effect_a = 'All: if at least 1 Industrial Colony: +1 [Point]'
    effect_b = 'Least [Stability]: -8 [Books]'
    abbr = 'SA_DA'
    architects = 1
    famine = -4

    def happen_a(self):
        any_have_industrial_colony = False
        for player in self.match.players[::-1]:
            for card in player.colony_cards():
                if card.age == 4:
                    self.match.log(f'{player} gains 1 [Point].')
                    player.points += 1
                    any_have_industrial_colony = True
                    break
        if not any_have_industrial_colony:
            self.match.log('No player has an Industrial colony.')

    def happen_b(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.BOOKS: -8}))

class SickManOfEuropeWomensSuffrage(Age4EventCard):
    name_a = 'Sick Man of Europe'
    name_b = 'Women\'s Suffrage'
    effect_a = 'Least [Military]: -8 [Gold]'
    effect_b = 'Most [Stability]: +1 [Point]'
    abbr = 'SME_WS'
    architects = 3
    famine = -1

    def happen_a(self):
        self.players_lose_resources(self.match.least_military(), Resources({Resource.GOLD: -8}))

    def happen_b(self):
        self.players_gain_point(self.most_stability())

class SokotoCaliphateTennisCourtOath(Age4EventCard):
    name_a = 'Sokoto Caliphate'
    name_b = 'Tennis Court Oath'
    effect_a = 'All: May -4 [Food]: +8 [Gold]'
    effect_b = 'Least [Stability]: -7 [Gold]'
    abbr = 'SC_TCO'
    architects = 0
    famine = -3

    def happen_a(self):
        self.may_pay_to_gain(Resources({Resource.FOOD: 4}), Resources({Resource.GOLD: 8}))

    def happen_b(self):
        self.players_lose_resources(self.match.least_stability(), Resources({Resource.GOLD: -7}))

class TonghakMovementSepoyMutiny(Age4EventCard):
    name_a = 'Tonghak movement'
    name_b = 'Sepoy Mutiny'
    effect_a = 'Least [Military]: -8 [Books], +2 [Stone]'
    effect_b = 'Least [Stability]: Go last and -5 [Gold]'
    abbr = 'TM_SM'
    architects = 0
    famine = -5

    def happen_a(self):
        for player in self.match.least_military():
            self.match.log(f'{player} loses 8 [Books] and gains 2 [Stone].')
            player.lose_resources(Resources({Resource.BOOKS: -8}))
            player.resources[Resource.STONE] += 2

    def happen_b(self):
        self.least_stability_goes_last_and_loses_resources(Resources({Resource.GOLD: -5}))

class WeltpolitikEmigration(Age4EventCard):
    name_a = 'Weltpolitik'
    name_b = 'Emigration'
    effect_a = 'All: +5 [Gold], +5 [Stone] per Industrial Colony'
    effect_b = 'Least [Stability]: Return 1 [Worker]'
    abbr = 'We_Em'
    architects = 2
    famine = -2

    def happen_a(self):
        any_have_industrial_colony = False
        for player in self.match.players[::-1]:
            reward = Resources()
            for card in player.colony_cards():
                if card.age == 4:
                    reward[Resource.GOLD] += 5
                    reward[Resource.STONE] += 5
            if reward:
                self.match.log(f'{player} gains {reward}.')
                player.resources += reward
                any_have_industrial_colony = True
        if not any_have_industrial_colony:
            self.match.log('No player has an Industrial colony.')

    def happen_b(self):
        for player in self.match.least_stability():
            if player.grown_workers:
                self.match.log(f'{player} must return 1 [Worker].')
                player.return_worker()
            else:
                self.match.log(f'{player} has no workers to return.')

all_event_cards = []
subclasses = [EventCard]
while subclasses:
    next_subclasses = []
    for cls in subclasses:
        if cls.__subclasses__():
            next_subclasses.extend(cls.__subclasses__())
        elif cls not in all_event_cards:
            all_event_cards.append(cls)
    subclasses = next_subclasses

def sort_key(card):
    return (card.age, card.name_a, card.name_b)

all_event_cards.sort(key=sort_key)
event_card_abbrs = {card.abbr: card.name() for card in all_event_cards}
