from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from functools import partial
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import *
from kivy.properties import ObjectProperty
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


class OpenScreen(Widget):
    name = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.main_hero = MainHero()
        super(OpenScreen, self).__init__(**kwargs)

    def submit_btn(self):
        if self.name.text:
            self.main_hero.nick = self.name.text
        print(self.main_hero.nick)


class Style(GridLayout):
    def add_hero_clean(self, instance, text_box, clean_text_box=True):
        if text_box.text:
            self.superheroes.add_superhero(text_box.text)
            if clean_text_box:
                text_box.text = ""
        print(self.superheroes.super_heroes)

    def __init__(self, **kwargs):
        super(Style, self).__init__(**kwargs)

        self.superheroes = MainHero()

        self.cols = 1
        self.rows = 2

        self.add_superhero_grid = GridLayout()
        self.add_superhero_grid.cols = 2
        self.add_superhero_grid.rows = 1

        self.add_superhero_grid.add_widget(Label(text="Add Superhero"))

        # self.name = TextInput(multiline=False)
        self.superhero_name = TextInput(multiline=False)
        self.add_superhero_grid.add_widget(self.superhero_name)

        self.add_widget(self.add_superhero_grid)

        self.submit_new_hero_grid = GridLayout()
        self.submit_new_hero_grid.cols = 1

        self.submit_new_hero_button = Button(text="Add new Superhero", font_size=30)
        self.submit_new_hero_button.bind(on_press=partial(self.add_hero_clean, text_box=self.superhero_name))
        self.submit_new_hero_grid.add_widget(self.submit_new_hero_button)

        self.add_widget(self.submit_new_hero_grid)

        # print(self.superheroes.super_heroes)


class Design(App):

    def build(self):
        return OpenScreen()


if __name__ == "__main__":
    Design().run()
    print("APP ENDED!")
