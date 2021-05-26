import asyncio
import threading
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
import trio


async def async_event(ed, name, *, filter=None, return_value=None):
    def _callback(*args, **kwargs):
        nonlocal callback_parameter

        if (filter is not None) and not filter(*args, **kwargs):
            return

        callback_parameter = (args, kwargs,)

        ed.unbind_uid(name, bind_id)

        event.set()

        return return_value

    callback_parameter = None

    bind_id = ed.fbind(name, _callback)

    assert bind_id > 0
    event = trio.Event()

    await event.wait()

    return callback_parameter


# Player avatar
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
        # player max health
        self.max_health = self.lvl * 10
        # player health
        self.health = self.max_health
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
        # self.starting_hit = choice(["Player", "Enemy"])
        self.starting_hit = "Enemy"
        move_col = (0, 1, 0, 1)
        if self.starting_hit == "Enemy":
            move_col = (1, 0, 0, 1)
        self.starting_hit_anim = Animation(duration=1, font_size=130)
        self.starting_hit_label = Label(text="Enemies turn" if self.starting_hit == "Enemy" else "Your turn",
                                        color=move_col)
        self.add_widget(self.starting_hit_label)

    async def fight(self, *args):
        # pass
        self.starting_hit_label.parent.remove_widget(self.starting_hit_label)
        hero_alive = True
        enemy_alive = True

        def enemy_move():
            # Enemy attack stat
            enemy_attack_stat = self.enemy.attack()
            # Enemy stat value
            enemy_attack = self.enemy.stats[self.enemy.attack()]
            # Possible damage
            damage = enemy_attack - getattr(self.app.main_hero, enemy_attack_stat)
            print(enemy_attack_stat, enemy_attack, damage)
            if damage >= 0:
                if self.app.main_hero.health - damage > 0:
                    self.app.main_hero.health -= damage
                else:
                    nonlocal hero_alive
                    hero_alive = False
                    self.app.main_hero.health = 0
                print(self.app.main_hero.health)
            else:
                pass  # TODO: warning that enemy is weaker than hero
            return hero_alive

        async def which_button():
            future = asyncio.get_event_loop().create_future()
            buttons = ToggleButtonBehavior.get_widgets('player_action')

            def set_result(button):
                for button in buttons:
                    button.unbind(set_result)
                    future.set_result(button)  # or whatever you want from the button

            for button in buttons:
                button.bind(on_press=set_result)

            return future

        async def player_move():
            # Enemy stat value
            button = await which_button()
            print(button)
            print(self.enemy.stats, self.player_action_pick)
            # time.sleep(0.5)
            # if self.player_action_pick is None:
            #     time.sleep(1)
            #     Clock.create_trigger(player_move())

            enemy_attack = self.enemy.stats[self.player_action_pick]

            # Possible damage
            damage = getattr(self.app.main_hero, self.player_action_pick) - enemy_attack
            print(self.player_action_pick, enemy_attack, damage)
            if damage >= 0:
                if self.enemy.health - damage > 0:
                    self.enemy.health -= damage
                else:
                    nonlocal enemy_alive
                    enemy_alive = False
                    self.enemy.health = 0
                print(self.enemy.health)
            else:
                pass  # TODO: warning that player is weaker than enemy
            return enemy_alive

        # def chceck(dt):
        #     while True:
        #         player_action = ToggleButtonBehavior.get_widgets('player_action')
        #         for btn in player_action:
        #             print(btn.state)
        #             if btn.state == 'down':
        #                 btn.state = "normal"
        #                 return player_move()
        # @mainthread

        def check():

            # future = asyncio.get_event_loop().create_future()
            while True:
                time.sleep(0.2)

                for btn in self.player_action_buttons:

                    print(btn.state, btn)
                    if btn.state == 'down':
                        btn.state = 'normal'
                        return player_move()

        # Clock.schedule_once(lambda dt: check())
        # eve = Clock.create_trigger(lambda dt: check())
        # eve()
        # t = threading.Thread(target=check)
        # t.daemon = True
        # event = Clock.create_trigger(lambda dt: check(), 1)
        # event = check
        # event = Clock.create_trigger(lambda dt: check())
        # t = threading.Thread(target=event)
        if self.starting_hit == "Enemy":
            # t.daemon = True
            # starter = 0
            while enemy_alive and hero_alive:
                # print(f"im here {event.callback}")
                # if not t.is_alive():
                # if starter == 0:
                #     t.start()
                # starter = 1
                if not enemy_move():
                    print("Player dead")  # TODO: Died warning for player
                    break

                # elif not player_move():
                #     print("Enemy dead")
                #     pass

                elif not await player_move():
                    print("Enemy dead")  # TODO: Died warning for enemy
                    # event.idle()

                    # self.t = Clock.create_trigger(chceck)
                    break
                print("before join")
                # t2 = threading.Event
                # Clock.schedule_once(lambda dt: t.join())
                # Clock.stop_clock()
            # else:
            #     App.get_running_app().on_pause()
            # t.join()
            # t.join()

            # t.join()

        else:
            print("Player move")

    # Execute animation on screen open
    def on_enter(self, *args):
        # self.starting_hit_anim = Animation(duration=1,) font_size=130, color=col)
        self.starting_hit_anim.start(widget=self.starting_hit_label)

        # def start_fight(*args):
        #     t_f = threading.Thread(target=self.fight)
        #     t_f.start()
        #     t_f.join()

        self.starting_hit_anim.bind(on_complete=self.fight)

    def on_pre_leave(self, *args):
        self.app.main_hero.health = self.app.main_hero.max_health
        for btn in ToggleButtonBehavior.get_widgets('player_action'):
            btn.state = 'normal'

    def boss_enemy(self):
        # Set enemy to boss
        self.enemy = self.app.boss_enemies[self.app.main_hero.boss_kills]

    def basic_enemy(self):
        # Set and construct BasicEnemy
        self.enemy = BasicEnemy(self.app.main_hero.lvl)

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

    async def root_task(self):

        async with trio.open_nursery() as nursery:
            self.nursery = nursery

            async def app_task():
                await self.async_run(async_lib='trio')

                nursery.cancel_scope.cancel()

            nursery.start_soon(app_task)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(Design().run)
    loop.run_until_complete(Design().async_run(async_lib='asyncio'))
    loop.close()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(async_runTouchApp(Design, async_lib='asyncio'))
    # loop.run_until_complete(Design().async_run(async_lib='asyncio'))
    # loop.close()
    # loop.close()
    # Design().run()
    # trio.run(Design().root_task)
