from otree.api import *


doc = """
Public goods with punishment, roughly based on Fehr & Gaechter 2000. 
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = None
    NAME_IN_URL = 'punishment'
    NUM_ROUNDS = 6
    ENDOWMENT = cu(5)
    MAX_PUNISHMENT = 10
    PUNISHMENT_SCHEDULE = {
        0: 0,
        1: 1,
        2: 2,
        3: 4,
        4: 5,
        5: 7,
        6: 8,
        7: 10,
        8: 11,
        9: 12,
        10: 15,
    }
    

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    is_punishing = models.BooleanField(initial=False)
    total_punishment = models.CurrencyField()


def make_punishment_field(id_in_group):
    return models.IntegerField(
        min=0, max=C.MAX_PUNISHMENT,
        label="Punishment to player {}".format(id_in_group),
        initial=0
    )


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )
    punish_p1 = make_punishment_field(1)
    punish_p2 = make_punishment_field(2)
    punish_p3 = make_punishment_field(3)
    punish_p4 = make_punishment_field(4)
    punish_p5 = make_punishment_field(5)
    punish_p6 = make_punishment_field(6)
    punish_p7 = make_punishment_field(7)
    punish_p8 = make_punishment_field(8)
    punish_p9 = make_punishment_field(9)
    punish_p10 = make_punishment_field(10)
    cost_of_punishing = models.CurrencyField()
    punishment_received = models.IntegerField()
    pay_before_pun = models.CurrencyField()


def creating_session(subsession: Subsession):
    # if subsession.round_number > 1:
    #     return
    
    
    # make first half of the groups non-punishing
    # and second half punishing
    
    grps = subsession.get_groups()
    num_non_pun = C.NUM_ROUNDS // 2
    print(f"NUM_NON_PUN: {num_non_pun}")
    
    for grp in grps:
        grp.is_punishing = grp.round_number > num_non_pun



def get_self_field(player: Player):
    return 'punish_p{}'.format(player.id_in_group)


def punishment_fields(player: Player):
    return ['punish_p{}'.format(p.id_in_group) for p in player.get_others_in_group()]


def set_indiv_share(group: Group):
    multiplier = float(group.session.config.get('mult'))
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = group.total_contribution * multiplier / len(players)


def set_payoffs(group: Group):
    players = group.get_players()
    total_punish = 0
    
    for p in players:
        payoff_before_punishment = C.ENDOWMENT - p.contribution + group.individual_share
        p.pay_before_pun = payoff_before_punishment
        self_field = get_self_field(p)
        punishments_received = [getattr(other, self_field) for other in p.get_others_in_group()]
        p.punishment_received = min(10, sum(punishments_received))
        total_punish += sum(punishments_received)
        punishments_sent = [getattr(p, field) for field in punishment_fields(p)]
        p.cost_of_punishing = sum(C.PUNISHMENT_SCHEDULE[points] for points in punishments_sent)
        p.payoff = max(0, payoff_before_punishment * (1 - p.punishment_received / 10) - p.cost_of_punishing)

    group.total_punishment = total_punish
    
    

# PAGES

class Instructions(Page):

    @staticmethod
    def vars_for_template(player: Player):
        conv = int(1/player.session.config.get("real_world_currency_per_point"))
        return dict(
            mult = player.session.config.get("mult"),
            conv=conv
        )


class RoundStart(Page):
    
    @staticmethod
    def is_displayed(player: Player):
        num_non_pun = C.NUM_ROUNDS // 2
        rnd = player.round_number
        
        return rnd == 1 or rnd == num_non_pun + 1
    
    @staticmethod
    def vars_for_template(player: Player):
        num_non_pun = C.NUM_ROUNDS // 2
        
        return dict(
                num_non=num_non_pun,
                num_pun=C.NUM_ROUNDS - num_non_pun,
            )

class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']
    
    @staticmethod
    def vars_for_template(player: Player):
        n = len(player.group.get_players())
        mult = player.session.config.get('mult')
        
        return dict(num_players=n,
                    multiplier=mult,
                   )



class WaitPage1(WaitPage):
    after_all_players_arrive = set_indiv_share



class Punish(Page):
    form_model = 'player'
    get_form_fields = punishment_fields
    
    @staticmethod
    def is_displayed(player: Player):
        return player.group.is_punishing

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            other_players=player.get_others_in_group(), schedule=C.PUNISHMENT_SCHEDULE.items(),
        )



class WaitPage2(WaitPage):
    after_all_players_arrive = set_payoffs



class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        pun_pct = int(player.punishment_received * 10)
        pun_amt = int(player.pay_before_pun * (player.punishment_received / 10) )
        return dict(
            pun_pct=pun_pct,
            pun_amt=pun_amt,
            )
    

class FinalResults(Page):
    
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    
    @staticmethod
    def vars_for_template(player: Player):

        
        nonpun_contrib = []
        pun_contrib = []
        tot_non_pun_pay = 0
        tot_pun_pay = 0
        
        for p in player.in_all_rounds():
            g = p.group
            
            d = {'rnd': g.round_number,
                'contrib': p.contribution,
                'tcontrib': g.total_contribution,
                'pay': p.payoff,
                'totpun': g.total_punishment,
                }
            
            if g.is_punishing:
                pun_contrib.append(d)
                tot_pun_pay += p.payoff
            else:
                nonpun_contrib.append(d)
                tot_non_pun_pay += p.payoff

        final_points = tot_non_pun_pay + tot_pun_pay
        print(f"{player.participant.code}: points: {final_points} --  {final_points.to_real_world_currency(player.session)}")
        final_pay = final_points / 2
               
        return dict(
                nonpun=nonpun_contrib,
                pun = pun_contrib,
                tot_pun_pay=tot_pun_pay,
                tot_non_pun_pay=tot_non_pun_pay,
                final_points=final_points,
                final_pay=final_pay,
            )


page_sequence = [
    Instructions,
    RoundStart,
    Contribute,
    WaitPage1,
    Punish,
    WaitPage2,
    Results,
    FinalResults,
]
