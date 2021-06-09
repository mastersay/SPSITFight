import asyncio
import random
# import threading
import time
from kivy.app import App
from kivy.base import *
from functools import partial
from kivy.uix.togglebutton import ToggleButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import *
from kivy.lang import Builder, parser
from kivy.uix.label import Label
from kivy.core.window import Window
# from kivy.logger import Logger, LoggerHistory
from kivy.event import EventDispatcher
from kivy.clock import Clock, mainthread
from kivy.animation import Animation
from enemies import BossHero, BasicEnemy
from random import choice
import json
from os import stat
import asynckivy

# Player avatar
class MainHero(EventDispatcher):
    nick = StringProperty()
    lvl = NumericProperty()
    coins = NumericProperty()
    max_health = NumericProperty()
    health = NumericProperty()
    heal = DictProperty()
    programming_stat = NumericProperty()
    design_stat = NumericProperty()
    creativity_stat = NumericProperty()
    boss_kills = NumericProperty(max=4)

    def __init__(self, save, **kwargs):
        super(MainHero, self).__init__(**kwargs)
        # on lvl change recalculate some properties
        self.bind(lvl=lambda *largs: self.recompute())
        # name of player
        self.nick = "Player"
        # player lvl
        self.lvl = 1
        # amount of coins
        self.coins = 10

        # player stats
        # killed bosses
        self.boss_kills = 0

        # fight stats
        self.programming_stat = 1
        self.design_stat = 1
        self.creativity_stat = 1
        if save:
            for name, prop in self.properties().items():
                if name != 'health' and name != 'max_health':
                    prop.set(self, save[name])
                    print(self.programming_stat)
            else:
                self.heal = {'heal': save['heal']['heal'], 'max_heal': self.lvl}
        else:
            # player max health
            self.max_health = self.lvl * 10
            # player health
            self.health = self.max_health
            # amount of healing for health
            self.heal = {'heal': 0, 'max_heal': self.lvl}

    # func to recalculate properties
    def recompute(self):
        self.max_health = self.lvl * 10
        self.health = self.max_health
        self.heal = {'heal': self.heal.get('heal'), 'max_heal': self.lvl}


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

    player_action_pick = StringProperty(allownone=True)
    player_action_buttons = ListProperty(ToggleButtonBehavior.get_widgets('player_action'))

    def __init__(self, **kwargs):
        super(FightScreen, self).__init__(**kwargs)
        # self.af_init = Clock.schedule_once(self.after_init)
        self.af_init = Clock.create_trigger(self._init)
        self.af_init()
        self.player_action_pick = None

    # Schedule after init
    def _init(self, dt):
        self.app = App.get_running_app()

    # Update values on screen, on pre enter, prepare starting_hit animation
    def on_pre_enter(self, *args):
        self.starting_hit = choice(["Player", "Enemy"])
        # self.starting_hit = "Enemy"
        move_col = (0, 1, 0, 1)
        if self.starting_hit == "Enemy":
            move_col = (1, 0, 0, 1)
        self.starting_hit_anim = Animation(duration=1, font_size=130)
        self.starting_hit_label = Label(text="Enemies turn" if self.starting_hit == "Enemy" else "Your turn",
                                        color=move_col)
        self.add_widget(self.starting_hit_label)

    async def fight(self, *args):
        try:
            self.starting_hit_label.parent.remove_widget(self.starting_hit_label)
        except: pass
        hero_alive = True
        enemy_alive = True

        def enemy_move():
            # Enemy attack stat
            enemy_attack_stat = self.enemy.attack()
            # Enemy stat value
            enemy_attack = self.enemy.stats[self.enemy.attack()]
            # Possible damage
            damage = enemy_attack - getattr(self.app.main_hero, enemy_attack_stat)
            # print(enemy_attack_stat, enemy_attack, damage)
            if damage >= 0:
                if self.app.main_hero.health - damage > 0:
                    self.app.main_hero.health -= damage
                else:
                    nonlocal hero_alive
                    hero_alive = False
                    self.app.main_hero.health = 0
                # print(self.app.main_hero.health)
            else:
                pass  # TODO: warning that enemy is weaker than hero
            return hero_alive

        # async def which_button():
        #     future = asyncio.get_event_loop().create_future()
        #     buttons = ToggleButtonBehavior.get_widgets('player_action')
        #
        #     def set_result(button):
        #         for button in buttons:
        #             button.unbind(set_result)
        #             future.set_result(button)  # or whatever you want from the button
        #
        #     for button in buttons:
        #         button.bind(on_press=set_result)
        #
        #     return future

        async def player_move():
            # Enemy stat value
            buttons = ToggleButtonBehavior.get_widgets('player_action')
            await asynckivy.or_from_iterable(
                asynckivy.event(button, 'state') for button in buttons)

            # print(self.enemy.stats, self.player_action_pick)
            try:
                enemy_attack = self.enemy.stats[self.player_action_pick]
                damage = getattr(self.app.main_hero, self.player_action_pick) - enemy_attack
                # print(self.player_action_pick, enemy_attack, damage)
                if damage >= 0:
                    if self.enemy.health - damage > 0:
                        self.enemy.health -= damage
                    else:
                        nonlocal enemy_alive
                        enemy_alive = False
                        self.enemy.health = 0
                    # print(self.enemy.health)
                else:
                    pass  # TODO: warning that player is weaker than enemy

                for button in buttons:
                    button.state = 'normal'
                return enemy_alive
            except KeyError:
                if self.app.main_hero.heal['heal'] != 0:
                    gained_damage = self.app.main_hero.max_health - self.app.main_hero.health
                    if gained_damage == 0:
                        return await player_move()
                    else:
                        if gained_damage <= self.app.main_hero.heal['heal']:
                            self.app.main_hero.health += gained_damage
                            self.app.main_hero.heal['heal'] -= gained_damage
                        else:
                            self.app.main_hero.health += self.app.main_hero.heal['heal']
                            self.app.main_hero.heal['heal'] = 0
                        return enemy_alive

                else:
                    return await player_move()
            # Possible damage

        if self.starting_hit == "Enemy":
            while True:
                print(self.app.main_hero.health, self.enemy.health)
                time.sleep(0.1)
                if not enemy_move():
                    print("Player dead")  # TODO: Died warning for player
                    break
                elif not await player_move():
                    print("Enemy dead")  # TODO: Died warning for enemy
                    self.app.root.current = 'MainScreen'
                    self.reward()
                    break
        else:
            while True:
                print(self.app.main_hero.health, self.enemy.health)
                time.sleep(0.1)
                if not await player_move():
                    print("Enemy dead")  # TODO: Died warning for enemy
                    self.app.root.current = 'MainScreen'
                    self.reward()
                    break
                elif not enemy_move():
                    print("Player dead", self.app.main_hero.health)  # TODO: Died warning for player
                    break
        self.app.root.current = 'MainScreen'

    def reward(self):
        if self.enemy.__class__ == BossHero:
            self.app.main_hero.lvl += 3
            self.app.main_hero.coins += random.randint(self.app.main_hero.lvl * 5, self.app.main_hero.lvl * 12)
            self.app.main_hero.boss_kills += 1
        else:
            print(self.app.main_hero.coins)
            self.app.main_hero.coins += random.randint(self.app.main_hero.lvl * 3,
                                                       self.app.main_hero.lvl * random.randint(5, 8))
            self.app.main_hero.lvl += 1
            print(self.app.main_hero.coins)

        # Execute animation on screen open

    def on_enter(self, *args):
        # self.starting_hit_anim = Animation(duration=1,) font_size=130, color=col)
        self.starting_hit_anim.start(widget=self.starting_hit_label)
        self.starting_hit_anim.bind(on_complete=lambda *largs: asynckivy.start_soon(self.fight()))

    def on_pre_leave(self, *args):
        self.app.main_hero.health = self.app.main_hero.max_health
        try:
            self.remove_widget(self.starting_hit_label)
        except:
            pass
        for btn in ToggleButtonBehavior.get_widgets('player_action'):
            btn.state = 'normal'

    def boss_enemy(self):
        # Set enemy to boss
        try:
            self.enemy = self.app.boss_enemies[self.app.main_hero.boss_kills]
            self.app.root.current = 'FightScreen'
        except IndexError:
            # self.app.root.current = 'MainScreen'
            # print(self.app.root.ids.boss_fight_button.disabled

            self.anim = Animation(duration=1, font_size=90)
            self.anim_label = Label(text="All Bosses Defeated", color='red')
            self.anim.start(widget=self.anim_label)
            time.sleep(0.1)
            self.app.root.ids.main_screen.add_widget(self.anim_label)
            self.anim.bind(on_complete=lambda *largs: self.temp())

    def temp(self):
        try:
            self.app.root.ids.main_screen.remove_widget(self.anim_label)
            # self.anim_label.parent.remove_widget(self.anim_label)
        except AttributeError:
            pass

    def basic_enemy(self):
        # Set and construct BasicEnemy
        self.enemy = BasicEnemy(self.app.main_hero.lvl)
        lowest_stat = min(self.app.main_hero.programming_stat, self.app.main_hero.design_stat,
                          self.app.main_hero.creativity_stat)
        print(self.enemy.stats)
        print(all(a <= lowest_stat for a in self.enemy.stats.values()))
        if all(a <= lowest_stat for a in self.enemy.stats.values()):
            print(lowest_stat + 1)
            self.enemy.stats['programming_stat'] += lowest_stat

    def player_action(self, action):
        self.player_action_pick = action
        # self.t()


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
        self.main_hero = MainHero(self.on_start())
        # self.main_hero = MainHero({})

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
                self.root.ids.openx_screen.warning_label.text = "Name can't exceed 18 characters!"
        else:
            self.root.current = 'MainScreen'
            self.root.ids.open_screen.player_name_txtIn.focus = False

    def on_start(self):
        Clock.schedule_once(lambda *largs: scrn(), -1)

        def scrn():
            try:
                if stat('progress_save.json').st_size > 0:
                    self.root.current = 'MainScreen'
                print("here")
            except FileNotFoundError:
                pass

        try:
            with open("progress_save.json", "r") as file:
                try:
                    js = json.load(file)
                except json.JSONDecodeError:
                    js = {}
                finally:
                    return js
        except FileNotFoundError:
            pass

    def on_stop(self):
        def json_pick(obj_w_props):
            dic = {name: obj_w_props.__getattribute__(name) for name in sorted(obj_w_props.properties(), key=len) if
                   name != 'health' and name != "max_health"}
            return dic

        with open("progress_save.json", "w") as file:
            file.write(json.dumps(json_pick(self.main_hero)))


# async def root_task(self):
#
#     async with trio.open_nursery() as nursery:
#         self.nursery = nursery
#
#         async def app_task():
#             await self.async_run(async_lib='trio')
#
#             nursery.cancel_scope.cancel()
#
#         nursery.start_soon(app_task)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(Design().run())
    loop.run_until_complete(Design().async_run(async_lib='asyncio'))
    loop.close()
