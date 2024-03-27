import itertools
import random
from otree.api import *

foods_intro = [dict(is_intro=True, block='foods')]
drinks_intro = [dict(is_intro=True, block='drinks')]


class Stimulus(ExtraModel):
    optionA = models.StringField()
    optionB = models.StringField()
    optionC = models.StringField()


def load_stimuli(name):
    rows = read_csv('randomize_stimuli/{}.csv'.format(name), Stimulus)
    # add a 'source' column so we know which spreadsheet it came from
    return [dict(row, block=name) for row in rows]


def randomize_trials(name):
    rows = load_stimuli(name)
    random.shuffle(rows)
    return rows


def multiple_blocks():
    """Append blocks, e.g.:
    1 2 3 4 5 6 a b c d e f
    """
    return foods_intro + load_stimuli('foods') + drinks_intro + load_stimuli('drinks')


def randomize_blocks():
    """
    Randomize between blocks, like
        1 2 3 4 5 6 a b c d e f
    or:
        a b c d e f 1 2 3 4 5 6
    """
    blocks = [
        foods_intro + load_stimuli('foods'),
        drinks_intro + load_stimuli('drinks'),
    ]
    random.shuffle(blocks)

    combined_list = []
    for block in blocks:
        combined_list.extend(block)
    return combined_list


def randomize_within_blocks():
    """
    Blocks are in fixed order, but we randomize within them, like:

        a e c b f d 1 6 3 5 2 4
    """
    return foods_intro + randomize_trials('foods') + drinks_intro + randomize_trials('drinks')


def randomize_merged():
    """
    Randomize all questions together in no particular order, like:

        e 6 b f 1 d c 3 a 2 4 5
    """
    combined = load_stimuli('foods') + load_stimuli('drinks')
    random.shuffle(combined)
    return combined


def alternate_blocks():
    """
    Interleave blocks, like:

        a 1 b 2 c 3 d 4 e 5 f 6
    """
    foods = load_stimuli('foods')
    drinks = load_stimuli('drinks')
    combined = []
    for i in range(len(foods)):
        combined.append(foods[i])
        combined.append(drinks[i])
    return combined
