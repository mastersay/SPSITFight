from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from functools import partial
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import *


# player avatar
class MainHero:
    def __init__(self):
        # name of player
        self.nick = ""
        # player lvl
        self.lvl = 1

        # player stats
        # player health
        self.health = self.lvl * 10
        # amount of healing for health
        self.heal = {0: self.lvl}

        # fight stats
        self.logic_stat = 1
        self.graphic_stat = 1
        self.nwm0 = 1

class Open_screen(Widget):
    def __init__(self, **kwargs):
        super(Open_screen, self).__init__(**kwargs)

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
        return Open_screen()


if __name__ == "__main__":
    Design().run()
    print("APP ENDED!")
