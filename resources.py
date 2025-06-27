import enum

class Resource(enum.Enum):
    FOOD = enum.auto()
    STONE = enum.auto()
    GOLD = enum.auto()
    BOOKS = enum.auto()
    STABILITY = enum.auto()
    MILITARY = enum.auto()

    @classmethod
    def production(cls):
        return (cls.FOOD, cls.STONE, cls.GOLD, cls.BOOKS)

    @classmethod
    def immediate(cls):
        return (cls.STABILITY, cls.MILITARY)

    def __str__(self):
        return self.plural()

    def singular(self):
        if self is Resource.BOOKS:
            return '[Book]'
        return f'[{self.name.title()}]'

    def plural(self):
        return f'[{self.name.title()}]'

class Resources:
    def __init__(self, initial_values={}):
        self.resources = {resource_type: 0 for resource_type in Resource}
        for resource_type in initial_values:
            self.resources[resource_type] += initial_values[resource_type]

    def __getitem__(self, resource_type):
        return self.resources[resource_type]

    def __setitem__(self, resource_type, value):
        self.resources[resource_type] = value

    def __ge__(self, cost):
        for resource_type in Resource.production():
            if self.resources[resource_type] < cost.resources[resource_type]:
                return False
        return True

    def __iadd__(self, other):
        for resource_type in Resource:
            self.resources[resource_type] += other.resources[resource_type]
        return self

    def __isub__(self, other):
        for resource_type in Resource:
            self.resources[resource_type] -= other.resources[resource_type]
        return self

    def __neg__(self):
        return Resources({resource_type: -amount for (resource_type, amount) in self.resources.items()})

    def __rmul__(self, other):
        return Resources({resource_type: other * amount for (resource_type, amount) in self.resources.items() if amount})

    def __len__(self):
        return len([True for amount in self.resources.values() if amount])

    def __iter__(self):
        return (resource for (resource, amount) in self.resources.items() if amount)

    def __str__(self):
        if not self:
            return 'no resources'
        return ', '.join(f'{amount} {resource_type.singular() if amount == 1 else resource_type.plural()}' for (resource_type, amount) in self.resources.items() if amount)

    def production_str(self):
        return ', '.join(f'{self.resources[resource_type]} {resource_type if self.resources[resource_type] == 1 else resource_type.plural()}' for resource_type in Resource.production())

    def all_types_str(self):
        return ', '.join(f'{self.resources[resource_type]} {resource_type if self.resources[resource_type] == 1 else resource_type.plural()}' for resource_type in Resource)

    def production(self):
        return Resources({resource_type: self.resources[resource_type] for resource_type in Resource.production()})

    def immediate(self):
        return Resources({resource_type: self.resources[resource_type] for resource_type in Resource.immediate()})

    def positive(self):
        return Resources({resource_type: amount for (resource_type, amount) in self.resources.items() if amount > 0})

    def negative(self):
        return Resources({resource_type: amount for (resource_type, amount) in self.resources.items() if amount < 0})

    def total(self):
        return sum(self.resources.values())

    def state(self):
        return {str(resource_type): amount for (resource_type, amount) in self.resources.items() if amount}
