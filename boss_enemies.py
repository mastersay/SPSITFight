from random import randint, choice


class BossHero:
    enemies = []

    def __init__(self, name: str, lvl: int, stats: dict):
        self.name = name
        self.health = lvl * 10
        self.programming_stat = stats['programming_stat']
        self.design_stat = stats['design_stat']
        self.creativity_stat = stats['creativity_stat']
        self.stats = stats
        self.__class__.enemies.append(self)

    def attack(self):
        stat_values = sorted(self.stats.values())

        def difference_check():
            return True if stat_values == sorted(set(stat_values)) else False

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


BossHero("First", 10, {'programming_stat': 10, 'design_stat': 5, 'creativity_stat': 8})
BossHero("Second", 20, {'programming_stat': 15, 'design_stat': 35, 'creativity_stat': 20})
