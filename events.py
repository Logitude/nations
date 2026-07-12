import enum
import re

from .resources import *

class Event:
    def __init__(self, match):
        self.match = match
        self.registered_events = []

    def register(self, card, condition, event):
        self.registered_events.append((card, condition, event))

    def unregister(self, card):
        for i in range(len(self.registered_events)):
            (registered_card, condition, event) = self.registered_events[i]
            if registered_card is card:
                del self.registered_events[i]
                break

class BasicEvent(Event):
    def happen(self, player, **kwargs):
        if not self.registered_events:
            return ()
        return_values = []
        for (card, condition, event) in self.registered_events[:]:
            if (card, condition, event) not in self.registered_events:
                continue
            if not condition(player, **kwargs):
                continue
            return_value = event(player, **kwargs)
            if return_value is not None:
                return_values.append(return_value)
        return tuple(return_values)

class ExtraEvent(Event):
    def happen(self, player, **kwargs):
        if not self.registered_events:
            return 0
        values = []
        for (card, condition, event) in self.registered_events[:]:
            if (card, condition, event) not in self.registered_events:
                continue
            if not condition(player, **kwargs):
                continue
            value = event(player, **kwargs)
            if value is not None:
                values.append(value)
        return sum(values)

class DiscountEvent(Event):
    def happen(self, player, **kwargs):
        cost = kwargs['cost']
        if not self.registered_events:
            return cost
        for (card, condition, event) in self.registered_events[:]:
            if (card, condition, event) not in self.registered_events:
                continue
            if not condition(player, **kwargs):
                continue
            cost -= event(player, **kwargs)
        cost = max(0, cost)
        return cost

class Events:
    def define_basic_event(self, name):
        self.events[name] = BasicEvent(self.match)

    def define_extra_event(self, name):
        self.events[name] = ExtraEvent(self.match)

    def define_discount_event(self, name):
        self.events[name] = DiscountEvent(self.match)

    def __init__(self, match):
        self.match = match
        self.events = {}

        self.define_basic_event('additional action')
        self.define_basic_event('additional buys')
        self.define_basic_event('additional production')
        self.define_basic_event('advisors on wonder spaces')
        self.define_basic_event('after bought card')
        self.define_basic_event('after event reveal')
        self.define_basic_event('after production')
        self.define_basic_event('before progress')
        self.define_basic_event('bought card')
        self.define_basic_event('bought golden age point')
        self.define_basic_event('buy card for gold')
        self.define_basic_event('buy from player')
        self.define_basic_event('buy with')
        self.define_basic_event('buying card')
        self.define_basic_event('choose event card')
        self.define_basic_event('colonies on wonder spaces')
        self.define_basic_event('cover card')
        self.define_basic_event('coverable cards')
        self.define_basic_event('defeated')
        self.define_basic_event('defer taking turmoil')
        self.define_basic_event('deployed')
        self.define_basic_event('discard gold turmoil')
        self.define_basic_event('discard immediately')
        self.define_basic_event('discover')
        self.define_basic_event('end of age')
        self.define_basic_event('end of round')
        self.define_basic_event('force least stability')
        self.define_basic_event('golden age choose books')
        self.define_basic_event('hire architect')
        self.define_basic_event('keep dynasty effects')
        self.define_basic_event('least military')
        self.define_basic_event('least stability')
        self.define_basic_event('lost to war')
        self.define_basic_event('make extra payment')
        self.define_basic_event('may not buy card')
        self.define_basic_event('no defeated effect')
        self.define_basic_event('no military upkeep')
        self.define_basic_event('no resource point loss')
        self.define_basic_event('not defeated')
        self.define_basic_event('pass')
        self.define_basic_event('passed over')
        self.define_basic_event('received extra growth resources')
        self.define_basic_event('remove with')
        self.define_basic_event('replaced card')
        self.define_basic_event('skip player order')
        self.define_basic_event('skip turn')
        self.define_basic_event('spared war point loss')
        self.define_basic_event('spent last gold')
        self.define_basic_event('take extra first action')
        self.define_basic_event('take worker')
        self.define_basic_event('updating most least stability military')
        self.define_basic_event('when removed')
        self.define_basic_event('wonder ready')

        self.define_extra_event('extra card cost')
        self.define_extra_event('extra colony military requirement')
        self.define_extra_event('extra famine')
        self.define_extra_event('extra growth resources')
        self.define_extra_event('extra payment')
        self.define_extra_event('extra player order military')
        self.define_extra_event('extra raid value')
        self.define_extra_event('extra scoring stone')
        self.define_extra_event('extra war food penalty')
        self.define_extra_event('extra war military')
        self.define_extra_event('extra war penalty')
        self.define_extra_event('extra wonder space')

        self.define_discount_event('card discount')
        self.define_discount_event('colony discount')
        self.define_discount_event('deploy discount')
        self.define_discount_event('golden age discount')
        self.define_discount_event('hire discount')

    def register(self, name, card, condition, event):
        self.events[name].register(card, condition, event)

    def unregister(self, name, card):
        self.events[name].unregister(card)

    def happen(self, name, player, **kwargs):
        return self.events[name].happen(player, **kwargs)
