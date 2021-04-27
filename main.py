from kivy.app import App
# from functools import partial
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from random import randint, choice


# player avatar
class MainHero:
    def __init__(self):
        # name of player
        self.nick = "Player"
        # player lvl
        self.lvl = 1

        # player stats
        # player health
        self.health = self.lvl * 10
        # amount of healing for health
        self.heal = {'heal': 0, 'max_heal': self.lvl}

        # fight stats
        self.programming_stat = 1
        self.design_stat = 1
        self.creativity_stat = 1


#  TODO: NPC class

# enemy boss avatars
class BossHero:
    def __init__(self, name: str, lvl: int, stats: dict):
        self.name = name

        self.health = lvl * 10
        self.programming_stat = stats['programming_stat']
        self.design_stat = stats['design_stat']
        self.creativity = stats['creativity_stat']
        self.stats = stats

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


class OpenScreen(Screen):
    player_name = ObjectProperty(None)
    submit_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.main_hero = MainHero()
        super(OpenScreen, self).__init__(**kwargs)

    def submit_btn(self):
        if self.player_name.text:
            if len(self.player_name.text) < 18:
                self.main_hero.nick = self.player_name.text
                print(self.main_hero.nick)
                return True
            else:
                print("Name can't exceed 18 characters!")
                self.submit_button.text = "Name can't exceed 18 characters!"
                return False
        print(self.main_hero.nick)
        return True


class MainScreen(Screen):
    pass


class FightScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass


kv = Builder.load_file('AppDesign.kv')


class Design(App):
    def build(self):
        return kv
    # how to access ids
    def submit_btn(self):
        text = self.root.ids.openScreen.main_hero.nick
        print(text)
        return True


if __name__ == "__main__":
    Design().run()
