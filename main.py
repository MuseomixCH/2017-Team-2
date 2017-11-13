# -*- coding: utf-8 -*-

#### Python code written by Arnaud Waels
#### PROTOTYPE MADE DURING MUSEOMIX 2017 IN LAUSANE
#### waels@devocite.com
#### triselectif@gmx.com

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty, DictProperty, StringProperty, BooleanProperty
from kivy.logger import Logger
from kivy.clock import Clock

from widgets.zoom_image.main import ZoomImageWithFocusRectangle


class MapLayer(FloatLayout):
    source = StringProperty("")
    name = StringProperty("")

class Map(FloatLayout):
    map_layers = DictProperty(None) # sources and properties
    _map_layers = DictProperty({}) # objects
    current_layer_name = StringProperty("")

    def __init__(self, **kwargs):
        ret = super(Map,self).__init__(**kwargs)
        Clock.schedule_once(self.load_layers,1)
        return ret

    def load_layers(self, *args):
        #main layers
        for name, source in self.map_layers.iteritems():
            self._map_layers[name] = ml = MapLayer(
                    name=name,
                    source=source,
                    opacity=0
                    )
            self.add_widget(ml)
            print name

        self.bind(current_layer_name=self.show_layer)

    def show_layer(self, instance, name):
        self.hide_all()
        self.hide_all()
        self.hide_all()
        self.hide_all()
        self.hide_all()
        Logger.info("Map: show layer %s" % name)

        # show current
        current = self._map_layers[name]
        current.opacity = 1

    def hide_all(self, *args):
        for name, layer in self._map_layers.iteritems():
            layer.opacity = 0


class GameScreen(ZoomImageWithFocusRectangle):
    #properties = DictProperty({"background_image":None, "focus_pos":None, "focus_size_hint":None})
    game = ObjectProperty(None)
    #game_screen_next = ObjectProperty(None)
    active = BooleanProperty(False)
    step2 = BooleanProperty(False)
    name = StringProperty("")
    map_name = StringProperty("")

    def start(self):
        self.active = True

    def show_explanation(self):
        pass

    def hide_explanation(self):
        pass

    def next(self, *args):
        self.game.next_step()

    def stop(self):
        self.active = False

    def on_focus(self, *args):
        print "on_focus"
        self.reset()

        #switch to second image
        self.step2 = True

        # update map layer
        app = App.get_running_app()
        app.main_layout._map.current_layer_name = "%s%s" % (self.map_name,"2")
        Clock.schedule_once(self.activate, 15)

    def on_unfocus(self, *args):
        print "on_unfocus"
        # update map layer
        app = App.get_running_app()
        app.main_layout._map.current_layer_name = self.map_name

    def activate(self, *args):
        self.active = False

    def restart(self, *args):
        # reinit
        # back to first screen
        self.active = True
        self.step2 = False
        self.reset()


class GameWithKeyboard(FloatLayout): # USB NFC reader behaves like a keyboard
    buffer = StringProperty("")
    # THIS SCENARIO IS BASED ON AN INTERACTIVE RING
    # warn by the visitor
    # that interacts with printed images (one of them has an USB receiver hidden under it)
    # IMPORTANT : choose an USB NFC reader that sends a keyboard message (like a supermarket scanner)
    # it's not the case for every NFC receiver

    def __init__(self, **kwargs):
        super(GameWithKeyboard, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        self.buffer += key
        print self.buffer
        map_name = "echoppe2"
        app = App.get_running_app()
        app.main_layout._map.current_layer_name = "%s" % map_name


class Game(GameWithKeyboard):
    #_map = ObjectProperty(None)
    #games_screens = DictProperty({})
    gamescreen1 = ObjectProperty(None) #GameScreen instance
    gamescreen2 = ObjectProperty(None)
    gamescreen3 = ObjectProperty(None)
    gamescreen4 = ObjectProperty(None)
    current = StringProperty("")

    def start(self, *args):
        self.gamescreen1.start()
        self.gamescreen2.start()
        self.gamescreen3.start()

    def start_game(self, game_id):
        pass

    def stop_game(self, game_id):
        #restart
        pass

    def show_game(self, game_id):
        pass

    def hide_game(self, game_id):
        pass

    def next_step(self):
        pass

    def restart(self, *args):
        # restart the whole thing, all Screens
        self.gamescreen1.restart()
        Clock.unschedule(self.gamescreen1.activate)
        self.gamescreen2.restart()
        Clock.unschedule(self.gamescreen2.activate)
        self.gamescreen3.restart()
        Clock.unschedule(self.gamescreen3.activate)


class VenicePietroApp(App):

    def build(self):

        from widgets.viewport import Viewport
        #size = (1920, 1080)
        size = (1920*3,1080*2)
        self.root = root = Viewport(size=size)

        self.main_layout = ml = Game()
        ml.start()
        root.add_widget(ml)
        return root

if __name__ == '__main__':
    VenicePietroApp().run()
