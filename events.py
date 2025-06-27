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

events = []

def define_basic_event(name):
    events.append(type(re.sub(r'\W', r'', name.title()), (BasicEvent,), {'name': name}))

def define_extra_event(name):
    events.append(type(re.sub(r'\W', r'', name.title()), (ExtraEvent,), {'name': name}))

def define_discount_event(name):
    events.append(type(re.sub(r'\W', r'', name.title()), (DiscountEvent,), {'name': name}))

define_basic_event('additional action')
define_basic_event('additional buys')
define_basic_event('additional production')
define_basic_event('advisors on wonder spaces')
define_basic_event('after bought card')
define_basic_event('after event reveal')
define_basic_event('after production')
define_basic_event('before progress')
define_basic_event('bought card')
define_basic_event('bought golden age point')
define_basic_event('buy card for gold')
define_basic_event('buy from player')
define_basic_event('buy with')
define_basic_event('buying card')
define_basic_event('choose event card')
define_basic_event('colonies on wonder spaces')
define_basic_event('cover card')
define_basic_event('coverable cards')
define_basic_event('defeated')
define_basic_event('defer taking turmoil')
define_basic_event('deployed')
define_basic_event('discard gold turmoil')
define_basic_event('discard immediately')
define_basic_event('discover')
define_basic_event('end of age')
define_basic_event('end of round')
define_basic_event('force least stability')
define_basic_event('golden age choose books')
define_basic_event('hire architect')
define_basic_event('keep dynasty effects')
define_basic_event('least military')
define_basic_event('least stability')
define_basic_event('lost to war')
define_basic_event('make extra payment')
define_basic_event('may not buy card')
define_basic_event('no defeated effect')
define_basic_event('no military upkeep')
define_basic_event('no resource point loss')
define_basic_event('not defeated')
define_basic_event('pass')
define_basic_event('passed over')
define_basic_event('received extra growth resources')
define_basic_event('remove with')
define_basic_event('replaced card')
define_basic_event('skip player order')
define_basic_event('skip turn')
define_basic_event('spared war point loss')
define_basic_event('spent last gold')
define_basic_event('take extra first action')
define_basic_event('take worker')
define_basic_event('updating most least stability military')
define_basic_event('when removed')
define_basic_event('wonder ready')

define_extra_event('extra card cost')
define_extra_event('extra colony military requirement')
define_extra_event('extra famine')
define_extra_event('extra growth resources')
define_extra_event('extra payment')
define_extra_event('extra player order military')
define_extra_event('extra raid value')
define_extra_event('extra scoring stone')
define_extra_event('extra war food penalty')
define_extra_event('extra war military')
define_extra_event('extra war penalty')
define_extra_event('extra wonder space')

define_discount_event('card discount')
define_discount_event('colony discount')
define_discount_event('deploy discount')
define_discount_event('golden age discount')
define_discount_event('hire discount')
