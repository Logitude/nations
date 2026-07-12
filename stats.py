class Stats:
    def __init__(self, other_stats=None):
        self.stats = {}
        if other_stats is not None:
            all_stat_types = set()
            for other in other_stats:
                all_stat_types |= set(other.stats.keys())
            for stat_type in all_stat_types:
                for other in other_stats:
                    if stat_type in other.stats:
                        for thing in other.stats[stat_type]:
                            self.collect(stat_type, thing, other.stats[stat_type][thing])

    def collect(self, stat_type, thing, increment=1):
        if stat_type not in self.stats:
            self.stats[stat_type] = {}
        if thing not in self.stats[stat_type]:
            self.stats[stat_type][thing] = 0
        self.stats[stat_type][thing] += increment

    def report(self, f):
        for stat_type in sorted(self.stats.keys()):
            print(f'{stat_type}:', file=f)
            for (amount, thing) in sorted([(amount, thing) for (thing, amount) in self.stats[stat_type].items()], reverse=True):
                print(f'  {thing}: {amount}', file=f)

class NoStats:
    def __init__(self, *args, **kwargs):
        pass

    def collect(self, *args, **kwargs):
        pass

    def report(self, *args, **kwargs):
        pass
