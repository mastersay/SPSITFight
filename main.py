from kivy.app import App
# from functools import partial
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
# from kivy.logger import Logger, LoggerHistory
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
    player_name_txtIn = ObjectProperty(None)
    submit_button = ObjectProperty(None)
    warning_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(OpenScreen, self).__init__(**kwargs)


class MainScreen(Screen):
    fight_button = ObjectProperty(None)
    boss_fight_button = ObjectProperty(None)
    programming_upgrade_btn: ObjectProperty(None)
    design_upgrade_btn: ObjectProperty(None)
    creativity_upgrade_btn: ObjectProperty(None)
    heal_buy_btn: ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)


    def upgrade(self):
        print(App.get_running_app().main_hero)


class FightScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass


kv = Builder.load_file('AppDesign.kv')


class Design(App):
    def __init__(self, **kwargs):
        super(Design, self).__init__(**kwargs)
        self.main_hero = MainHero()

    def build(self):
        return kv

    # how to access ids
    def submit_btn(self):
        if self.root.ids.open_screen.player_name_txtIn.text:
            if len(self.root.ids.open_screen.player_name_txtIn.text) < 18:
                self.main_hero.nick = self.root.ids.open_screen.player_name_txtIn.text
                print(self.main_hero.nick)
                self.root.current = 'MainScreen'
                self.root.ids.open_screen.player_name_txtIn.focus = False
            else:
                print("Name can't exceed 18 characters!")
                self.root.ids.open_screen.warning_label.text = "Name can't exceed 18 characters!"
        else:
            self.root.current = 'MainScreen'
            self.root.ids.open_screen.player_name_txtIn.focus = False
        print(self.main_hero.nick)


if __name__ == "__main__":
    Design().run()
