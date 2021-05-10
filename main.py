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
from kivy.animation import Animation
from enemies import BossHero, BasicEnemy
from random import choice


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

    def __init__(self):
        super(MainHero, self).__init__()
        # name of player
        self.nick = "Player"
        # player lvl
        self.lvl = 5
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

    # method for upgrade stats
    def upgrade(self, stat):
        upgrade_price = 0
        if stat != "heal":
            if self.app.main_hero.coins >= getattr(self.app.main_hero, stat):
                upgrade_price = getattr(self.app.main_hero, stat)
                setattr(self.app.main_hero, stat, getattr(self.app.main_hero, stat) + 1)
        elif getattr(self.app.main_hero, 'heal')['heal'] < getattr(self.app.main_hero, 'heal')['max_heal']:
            if self.app.main_hero.coins >= self.app.main_hero.heal['max_heal']:
                upgrade_price = self.app.main_hero.heal['max_heal']
                self.app.main_hero.heal['heal'] += 1
        self.app.main_hero.coins -= upgrade_price
        # self.coins_label.text = f"Coins {self.app.main_hero.coins}"


class FightScreen(Screen):
    programming_stat_label = ObjectProperty(None)
    # programming_upgrade_btn: ObjectProperty(None)

    design_stat_label = ObjectProperty(None)
    # design_upgrade_btn: ObjectProperty(None)

    creativity_stat_label = ObjectProperty(None)
    # creativity_upgrade_btn: ObjectProperty(None)

    heal_stat_label = ObjectProperty(None)
    # heal_buy_btn: ObjectProperty(None)

    # enemy_programming_stat_label = ObjectProperty(None)
    # enemy_design_stat_label = ObjectProperty(None)
    # enemy_creativity_stat_label = ObjectProperty(None)
    enemy = ObjectProperty(rebind=True, defaultvalue=BasicEnemy(999))
    starting_hit_label = ObjectProperty(None)
    starting_hit = StringProperty()
    starting_hit_anim = ObjectProperty()

    def __init__(self, **kwargs):
        super(FightScreen, self).__init__(**kwargs)
        # self.af_init = Clock.schedule_once(self.after_init)
        self.af_init = Clock.create_trigger(self._init)
        self.af_init()

    # Schedule after init
    def _init(self, dt):
        self.app = App.get_running_app()

    # Update values on screen, on pre enter, prepare starting_hit animation
    def on_pre_enter(self, *args):
        self.af_init()
        self.starting_hit = choice(["Player", "Enemy"])
        move_col = (0, 1, 0, 1)
        if self.starting_hit == "Enemy":
            move_col = (1, 0, 0, 1)
        self.starting_hit_anim = Animation(duration=1, font_size=130)
        self.starting_hit_label = Label(text="Enemies turn" if self.starting_hit == "Enemy" else "Your turn",
                                        color=move_col)
        self.add_widget(self.starting_hit_label)

    # Execute animation on screen open
    def on_enter(self, *args):
        # self.starting_hit_anim = Animation(duration=1,) font_size=130, color=col)
        self.starting_hit_anim.start(widget=self.starting_hit_label)
        self.starting_hit_anim.bind(
            on_complete=lambda x, y: self.starting_hit_label.parent.remove_widget(self.starting_hit_label))

    def boss_enemy(self):
        # Set enemy to boss
        self.enemy = self.app.boss_enemies[self.app.main_hero.boss_kills]

    def basic_enemy(self):
        # Set and construct BasicEnemy
        self.enemy = BasicEnemy(self.app.main_hero.lvl)


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
