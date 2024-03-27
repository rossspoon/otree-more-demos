from otree.api import *

doc = """
Shopping app (online grocery store)
"""


class Product(ExtraModel):
    sku = models.StringField()
    name = models.StringField()
    image_png = models.StringField()
    unit_price = models.CurrencyField()


def load_products():
    rows = read_csv(__name__ + '/catalog.csv', Product)
    for row in rows:
        row['image_path'] = 'grocery/{}.png'.format(row['image_png'])
    return rows


class C(BaseConstants):
    NAME_IN_URL = 'shop'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    PRODUCTS = load_products()
    # SKU = 'stock keeping unit' = product ID
    PRODUCTS_DICT = {row['sku']: row for row in PRODUCTS}


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    total_price = models.CurrencyField(initial=0)


class Item(ExtraModel):
    player = models.Link(Player)
    sku = models.StringField()
    name = models.StringField()
    quantity = models.IntegerField()
    unit_price = models.CurrencyField()


def total_price(item: Item):
    return item.quantity * item.unit_price


def to_dict(item: Item):
    return dict(
        sku=item.sku,
        name=item.name,
        quantity=item.quantity,
        total_price=total_price(item),
    )


def live_method(player: Player, data):
    if 'sku' in data:
        sku = data['sku']
        delta = data['delta']
        product = C.PRODUCTS_DICT[sku]
        matches = Item.filter(player=player, sku=sku)
        if matches:
            [item] = matches
            item.quantity += delta
            if item.quantity <= 0:
                item.delete()
        else:
            if delta > 0:
                Item.create(
                    player=player,
                    quantity=delta,
                    sku=sku,
                    name=product['name'],
                    unit_price=product['unit_price'],
                )
    items = Item.filter(player=player)
    item_dicts = [to_dict(item) for item in items]
    player.total_price = sum([total_price(item) for item in items])
    return {player.id_in_group: dict(items=item_dicts, total_price=player.total_price)}


# PAGES
class MyPage(Page):
    live_method = live_method


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(items=Item.filter(player=player))


page_sequence = [MyPage, Results]
