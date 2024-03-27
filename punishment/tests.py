from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield Instructions
        
        if self.player.round_number == 1 or self.player.round_number == (C.NUM_ROUNDS // 2) +1:
            yield RoundStart
            
        c = random.randint(0, C.ENDOWMENT)
        yield Contribute, dict(contribution = c)
        
        if self.player.group.is_punishing:
            
            feilds = punishment_fields(self.player)
            form = {f: random.randint(0,3) for f in feilds}
            #form = {f: 0 for f in feilds}
            yield Punish , form
        
        yield Results
