from .utils import *

def stat_name(thing):
    name = thing
    try:
        name = thing.name
        if thing.abbr == 'RTK':
            name = 'Romance of the Three Kingdoms'
        if thing.abbr == 'AhLc_Nerf':
            name = 'Nerfed Abraham Lincoln'
    except AttributeError:
        pass
    return name

player_counts = [0, 2, 3, 4, 5, 6]

global_stats = ['Player Count']
stats_order = [
    'Nation Available',
    'Nation Drafted',
    'Nation Won',
    'Card Available',
    'Card Bought'
]
for i in range(1, 33):
    stats_order.append(f'Card Bought {ordinal(i)}')

class Stats:
    def __init__(self, other_stats=None):
        self.stats = {player_count: {} for player_count in player_counts}
        if other_stats is not None:
            for player_count in player_counts:
                all_stat_types = set()
                for other in other_stats:
                    all_stat_types |= set(other.stats[player_count].keys())
                for stat_type in all_stat_types:
                    if stat_type not in self.stats[player_count]:
                        self.stats[player_count][stat_type] = {}
                    for other in other_stats:
                        if stat_type in other.stats[player_count]:
                            for thing in other.stats[player_count][stat_type]:
                                if thing not in self.stats[player_count][stat_type]:
                                    self.stats[player_count][stat_type][thing] = 0
                                self.stats[player_count][stat_type][thing] += other.stats[player_count][stat_type][thing]

    def collect(self, match, stat_type, thing, increment=1):
        if stat_type in global_stats:
            player_count = 0
        else:
            player_count = len(match.players)
        if stat_type not in self.stats[player_count]:
            self.stats[player_count][stat_type] = {}
        thing_name = stat_name(thing)
        if thing_name not in self.stats[player_count][stat_type]:
            self.stats[player_count][stat_type][thing_name] = 0
        self.stats[player_count][stat_type][thing_name] += increment

    def compute_aggregate(self):
        self.stats['3-plus'] = {}
        for stat_type in list(self.stats[0]):
            if stat_type not in global_stats:
                del self.stats[0][stat_type]
        for player_count in player_counts[1:]:
            for aggregate_player_count in (0, '3-plus'):
                if aggregate_player_count == '3-plus' and player_count < 3:
                    continue
                for stat_type in self.stats[player_count]:
                    if stat_type not in self.stats[aggregate_player_count]:
                        self.stats[aggregate_player_count][stat_type] = {}
                    for thing in self.stats[player_count][stat_type]:
                        if thing not in self.stats[aggregate_player_count][stat_type]:
                            self.stats[aggregate_player_count][stat_type][thing] = 0
                        self.stats[aggregate_player_count][stat_type][thing] += self.stats[player_count][stat_type][thing]

    def report(self, f):
        self.compute_aggregate()
        print('All Player Counts:', file=f)
        for stat_type in global_stats:
            print(f'  {stat_type}:', file=f)
            for (amount, thing) in sorted([(amount, thing) for (thing, amount) in self.stats[0][stat_type].items()], reverse=True):
                if isinstance(amount, int):
                    print(f'    {thing}: {amount}', file=f)
                else:
                    print(f'    {thing}: {amount:0.1f}', file=f)
        self.report_for_player_count(0, f)
        for player_count in player_counts[1:] + ['3-plus']:
            print(f'{player_count}-player:', file=f)
            self.report_for_player_count(player_count, f)

    def report_for_player_count(self, player_count, f):
        for stat_type in stats_order:
            if stat_type not in self.stats[player_count]:
                continue
            print(f'  {stat_type}:', file=f)
            for (amount, thing) in sorted([(amount, thing) for (thing, amount) in self.stats[player_count][stat_type].items()], reverse=True):
                if isinstance(amount, int):
                    print(f'    {thing}: {amount}', file=f)
                else:
                    print(f'    {thing}: {amount:0.1f}', file=f)
        self.report_percentages(player_count, 'Nation Available', 'Nation Drafted', f)
        self.report_percentages(player_count, 'Nation Drafted', 'Nation Won', f)
        self.report_percentages(player_count, 'Card Available', 'Card Bought', f)
        for i in range(1, 33):
            self.report_percentages(player_count, 'Card Available', f'Card Bought {ordinal(i)}', f)

    def report_percentages(self, player_count, available_stat_type, chosen_stat_type, f):
        if available_stat_type not in self.stats[player_count] or chosen_stat_type not in self.stats[player_count]:
            return
        print(f'  {chosen_stat_type} %:', file=f)
        percentages = [(amount / self.stats[player_count][available_stat_type][thing], thing) for (thing, amount) in self.stats[player_count][chosen_stat_type].items()]
        for (amount, thing) in sorted(percentages, reverse=True):
            print(f'    {thing}: {amount * 100:0.1f}%', file=f)

class NoStats:
    def __init__(self, *args, **kwargs):
        pass

    def collect(self, *args, **kwargs):
        pass

    def report(self, *args, **kwargs):
        pass
