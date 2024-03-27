from otree.api import *


doc = """
A 'bots vs humans' game can be implemented simply by making a
1-player task and framing the server's calculations as a 'bot'
(e.g. random decisions or some dynamic logic that depends on the 
player's actions).
"""


class C(BaseConstants):
    NAME_IN_URL = 'bots_vs_humans_simple'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    PAYOFF_A = cu(300)
    PAYOFF_B = cu(200)
    PAYOFF_C = cu(100)
    PAYOFF_D = cu(0)
    CHOICES = [[True, 'Cooperate'], [False, 'Defect']]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=C.CHOICES,
        widget=widgets.RadioSelect,
    )
    bot_cooperate = models.BooleanField(choices=C.CHOICES)


def set_payoff(player: Player):
    payoff_matrix = {
        (False, True): C.PAYOFF_A,
        (True, True): C.PAYOFF_B,
        (False, False): C.PAYOFF_C,
        (True, False): C.PAYOFF_D,
    }
    player.payoff = payoff_matrix[(player.cooperate, player.bot_cooperate)]


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        import random

        player.bot_cooperate = random.choice([True, False])
        set_payoff(player)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            same_choice=player.cooperate == player.bot_cooperate,
            my_decision=player.field_display('cooperate'),
            bot_decision=player.field_display('bot_cooperate'),
        )


page_sequence = [Decision, Results]
