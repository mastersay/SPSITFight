import kivy.event
from kivy.app import App
from functools import partial
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import *
from kivy.lang import Builder, parser
from kivy.uix.label import Label
from kivy.core.window import Window
# from kivy.logger import Logger, LoggerHistory
from kivy.event import EventDispatcher
from kivy.clock import Clock
from enemies import BossHero, BasicEnemy


# player avatar
class MainHero(EventDispatcher):
    nick = StringProperty()
    lvl = NumericProperty()
    coins = NumericProperty()
    health = NumericProperty()
    heal = DictProperty()
    programming_stat = NumericProperty()
    design_stat = NumericProperty()
    creativity_stat = NumericProperty()
    boss_kills = NumericProperty()

    def __init__(self, *args, **kwargs):
        super(MainHero, self).__init__(*args, **kwargs)
        # name of player
        self.nick = "Player"
        # player lvl
        self.lvl = 1
        # amount of coins
        self.coins = 100

        # player stats
        # player health
        self.health = self.lvl * 10
        # amount of healing for health
        self.heal = {'heal': 0, 'max_heal': self.lvl}

        # fight stats
        self.programming_stat = 1
        self.design_stat = 1
        self.creativity_stat = 1

        # killed bosses
        self.boss_kills = 0


class OpenScreen(Screen):
    player_name_txtIn = ObjectProperty(None)
    submit_button = ObjectProperty(None)
    warning_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(OpenScreen, self).__init__(**kwargs)


class MainScreen(Screen):
    coins_label = ObjectProperty(None)

    fight_button = ObjectProperty(None)
    boss_fight_button = ObjectProperty(None)

    programming_stat_label: ObjectProperty(None)
    programming_upgrade_btn: ObjectProperty(None)

    design_stat_label: ObjectProperty(None)
    design_upgrade_btn: ObjectProperty(None)

    creativity_stat_label: ObjectProperty(None)
    creativity_upgrade_btn: ObjectProperty(None)

    heal_stat_label: ObjectProperty(None)
    heal_buy_btn: ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.af_init = Clock.create_trigger(self._init)
        self.af_init()

    # Schedule after init
    def _init(self, dt):
        self.app = App.get_running_app()
        # self.programming_stat_label.text = f'Programming {self.app.main_hero.programming_stat}'
        # self.design_stat_label.text = f'Design {self.app.main_hero.design_stat}'
        # self.creativity_stat_label.text = f'Creativity {self.app.main_hero.creativity_stat}'
        # self.heal_stat_label.text = f"Heal {self.app.main_hero.heal['heal']}/{self.app.main_hero.heal['max_heal']}"
        # self.coins_label.text = f"Coins {self.app.main_hero.coins}"

    # Update values on screen, on pre enter
    def on_pre_enter(self, *args):
        self.af_init()

    # func for upgrade stats
    def upgrade(self, stat):
        # self.programming_stat_label.update()
        upgrade_price = 0
        if stat != "heal":
            if self.app.main_hero.coins >= getattr(self.app.main_hero, stat):
                upgrade_price = getattr(self.app.main_hero, stat)
                setattr(self.app.main_hero, stat, getattr(self.app.main_hero, stat) + 1)

                # print(self.app.a.__dict__)
                # self.__dict__

                stat_no_suffix = stat.removesuffix('_stat')
                # setattr(getattr(self, f'{stat}_label'), 'text',
                #         f"{stat_no_suffix[0].capitalize() + stat_no_suffix[1:]} {getattr(self.app.main_hero, stat)}")
        elif getattr(self.app.main_hero, 'heal')['heal'] < getattr(self.app.main_hero, 'heal')['max_heal']:
            if self.app.main_hero.coins >= self.app.main_hero.heal['max_heal']:
                upgrade_price = self.app.main_hero.heal['max_heal']
                self.app.main_hero.heal['heal'] += 1
                self.heal_stat_label.text = f"Heal " \
                                            f"{self.app.main_hero.heal['heal']}/{self.app.main_hero.heal['max_heal']}"
        self.app.main_hero.coins -= upgrade_price
        self.coins_label.text = f"Coins {self.app.main_hero.coins}"


class FightScreen(Screen):
    programming_stat_label = ObjectProperty(None)
    # programming_upgrade_btn: ObjectProperty(None)

    design_stat_label = ObjectProperty(None)
    # design_upgrade_btn: ObjectProperty(None)

    creativity_stat_label = ObjectProperty(None)
    # creativity_upgrade_btn: ObjectProperty(None)

    heal_stat_label = ObjectProperty(None)
    # heal_buy_btn: ObjectProperty(None)

    enemy_programming_stat_label = ObjectProperty(None)
    enemy_design_stat_label = ObjectProperty(None)
    enemy_creativity_stat_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(FightScreen, self).__init__(**kwargs)
        # self.af_init = Clock.schedule_once(self.after_init)
        self.af_init = Clock.create_trigger(self._init)
        self.af_init()

    # Schedule after init
    def _init(self, dt):
        self.app = App.get_running_app()
        # self.programming_stat_label.text = f'Programming {self.app.main_hero.programming_stat}'
        # self.design_stat_label.text = f'Design {self.app.main_hero.design_stat}'
        # self.creativity_stat_label.text = f'Creativity {self.app.main_hero.creativity_stat}'
        # self.heal_stat_label.text = f"Heal {self.app.main_hero.heal['heal']}"

    # Update values on screen, on pre enter
    def on_pre_enter(self, *args):
        self.af_init()

    def boss_enemy(self):
        # Labels with stats
        self.enemy_programming_stat_label.text \
            = f"Programming {self.app.boss_enemies[self.app.main_hero.boss_kills].programming_stat}"
        self.enemy_design_stat_label.text \
            = f"Design {self.app.boss_enemies[self.app.main_hero.boss_kills].design_stat}"
        self.enemy_creativity_stat_label.text \
            = f"Creativity {self.app.boss_enemies[self.app.main_hero.boss_kills].creativity_stat}"

    def basic_enemy(self):
        # Construct enemy
        enemy = BasicEnemy(self.app.main_hero.lvl)

        # Labels with stats
        self.enemy_programming_stat_label.text \
            = f"Programming {enemy.stats['programming_stat']}"
        self.enemy_design_stat_label.text \
            = f"Design {enemy.stats['design_stat']}"
        self.enemy_creativity_stat_label.text \
            = f"Creativity {enemy.stats['creativity_stat']}"


class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)
        # self.af_init = Clock.create_trigger(self._init)
        self.af_init = Clock.schedule_once(self._init)
        self.af_init()

    # Schedule after init
    def _init(self, dt):
        self.app = App.get_running_app()


class Design(App):
    main_hero = ObjectProperty()

    def __init__(self, **kwargs):
        super(Design, self).__init__(**kwargs)
        # self.main_hero = MainHero()
        self.boss_enemies = BossHero.enemies
        self.main_hero = MainHero()

        # self.a
        # self.preps.num = NumericProperty(self.main_hero.programming_stat, rebind=True)
        # global a
        # print(self.a.__dict__)
        # self.a.coins -= 20
        # print(self.main_hero.coins, self.a.coins)

        # num2 = NumericProperty(self.main_hero.programming_stat)
        # self.apply_property(l=NumericProperty(self.main_hero.programming_stat))

        def my_x_callback(obj, value):
            print('on object', obj, 'x changed to', value)

    # Construct app
    def build(self):
        # design constructor
        kv = Builder.load_file('AppDesign.kv')
        return kv

    # Login button and nick check
    def submit_btn(self):
        if self.root.ids.open_screen.player_name_txtIn.text:
            if len(self.root.ids.open_screen.player_name_txtIn.text) < 18:
                self.main_hero.nick = self.root.ids.open_screen.player_name_txtIn.text
                # print(self.main_hero.nick)
                self.root.current = 'MainScreen'
                self.root.ids.open_screen.player_name_txtIn.focus = False
            else:
                # print("Name can't exceed 18 characters!")
                self.root.ids.open_screen.warning_label.text = "Name can't exceed 18 characters!"
        else:
            self.root.current = 'MainScreen'
            self.root.ids.open_screen.player_name_txtIn.focus = False


if __name__ == "__main__":
    Design().run()
