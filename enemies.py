from kivy.properties import *
from kivy.event import EventDispatcher
from random import randint, choice, sample
from string import ascii_uppercase, ascii_lowercase


# Enemy boss avatar
class BossHero(EventDispatcher):
    enemies = []
    name = StringProperty()
    lvl = NumericProperty()
    health = NumericProperty()
    stats = DictProperty()

    def __init__(self, name: str, lvl: int, stats: dict):
        super(BossHero, self).__init__()
        self.name = name
        self.lvl = lvl
        self.health = lvl * 10
        self.programming_stat = stats['programming_stat']
        self.design_stat = stats['design_stat']
        self.creativity_stat = stats['creativity_stat']
        self.stats = stats
        self.__class__.enemies.append(self)

    # Enemy attack
    def attack(self):
        stat_values = sorted(self.stats.values())

        # Check if some stats have same values
        def difference_check() -> bool:
            return True if stat_values == sorted(set(stat_values)) else False

        # Search in dictionary by values
        def key_by_value(dictionary, search_by):
            if difference_check():
                for key, value in dictionary.items():
                    if value == search_by:
                        return key
            else:
                return [key for key, value in dictionary.items() if value == search_by]

        chance = randint(1, 100)
        if difference_check():
            if chance > 40:
                attack_pick = key_by_value(self.stats, max(stat_values))
            elif chance > 10:
                attack_pick = stat_values[1]
            else:
                attack_pick = key_by_value(self.stats, min(stat_values))
        else:
            if chance > 40:
                attack_pick = choice(key_by_value(self.stats, max(stat_values)))
            else:
                attack_pick = choice(key_by_value(self.stats, min(stat_values)))
        return attack_pick


class BasicEnemy(EventDispatcher):
    name = StringProperty()
    lvl = NumericProperty()
    health = NumericProperty()
    primary_stat, sc_stat, third_stat = StringProperty(), StringProperty(), StringProperty()
    stats = DictProperty()

    def __init__(self, hero_lvl: int):
        super(BasicEnemy, self).__init__()

        def ad_sub_generator(main_value: int, scale, operators=('+', '-')) -> int:
            return eval(f"{main_value}{choice(operators)}{scale}")

        self.name = choice(ascii_uppercase) + ''.join(choice(ascii_lowercase) for _ in range(randint(3, 6)))
        self.lvl = ad_sub_generator(hero_lvl, randint(0, round(hero_lvl / 10)))
        self.health = self.lvl * 10

        primary_stat, sc_stat, third_stat = sample(['programming_stat', 'design_stat', 'creativity_stat'], 3)
        self.stats = {
            primary_stat: ad_sub_generator(self.lvl, randint(round(self.lvl / 2), self.lvl), operators='+'),
            sc_stat: ad_sub_generator(self.lvl, randint(0, round(self.lvl / 2)), operators='+'),
            third_stat: ad_sub_generator(self.lvl, randint(0, self.lvl - 1))}

    # Enemy attack
    def attack(self) -> str:
        # Sorted fight stats
        stat_values = sorted(self.stats.values())

        # Check if some stats have same values
        def difference_check() -> bool:
            return True if stat_values == sorted(set(stat_values)) else False

        # Search in dictionary by values
        def key_by_value(dictionary, search_by):
            if difference_check():
                for key, value in dictionary.items():
                    if value == search_by:
                        return key
            else:
                return [key for key, value in dictionary.items() if value == search_by]

        chance = randint(1, 100)
        if difference_check():
            if chance > 50:
                attack_pick = key_by_value(self.stats, max(stat_values))
            elif chance > 20:
                attack_pick = stat_values[1]
            else:
                attack_pick = key_by_value(self.stats, min(stat_values))
        else:
            if chance > 50:
                attack_pick = choice(key_by_value(self.stats, max(stat_values)))
            else:
                attack_pick = choice(key_by_value(self.stats, min(stat_values)))
        return attack_pick


BossHero("First", 10, {'programming_stat': 15, 'design_stat': 8, 'creativity_stat': 11})
BossHero("Second", 20, {'programming_stat': 15, 'design_stat': 35, 'creativity_stat': 23})
