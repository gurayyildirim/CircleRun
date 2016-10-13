# -*-coding:utf-8-*-
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty

from math import sin, cos, radians

from kivy.core.audio import SoundLoader
directionChangeSound = SoundLoader.load("buttonSound.wav")

# Temporary window size configuration
from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')


class PlayGround(FloatLayout):
    """docstring for PlayGround"""
    # Radius of main circle
    radius = NumericProperty()

    def __init__(self, **kwargs):
        super(PlayGround, self).__init__(**kwargs)

        # Container for all the objects
        self.circle = CircleObjects(size_hint_y=1, size_hint_x=None, pos_hint={
            'center_x': 0.5, 'center_y': 0.5})
        self.setCoins(40)
        self.add_widget(self.circle)

        pos_hint = self.find_ratio(90)
        self.user = UserObject(angle=90, pos_hint={'center_x': pos_hint[
            0], 'center_y': pos_hint[1]}, size_hint=(.1, .1))
        self.circle.add_widget(self.user)

    # It is only for debug purposes
    def on_touch_down(self, x):
        print "PlayGround; Radius: %s, Size: %s, Center: %s, Pos: %s" %\
            (self.radius, self.size, self.center, self.pos), x

    def find_ratio(self, angleInDegree):
        """Find position of corresponding degree"""
        angle = radians(angleInDegree)
        # Using +1 offset in order to put the result in the range of 0 and 1
        x = (cos(angle) + 1) / 2
        y = (sin(angle) + 1) / 2
        return x, y

    def setCoins(self, count):
        """
        Add objects around the circle with equal space.
        """
        angleBetweenCoins = 360.0 / count

        for i in range(count):
            # Calculate the relative position
            pos_hint = self.find_ratio(i * angleBetweenCoins)

            # This is start location of user
            if i == count / 4:
                continue

            # Create coin widget with .1 size ratio
            coinToAdd = Coin(pos_hint={'center_x': pos_hint[
                             0], 'center_y': pos_hint[1]}, size_hint=(.1, .1))
            # Add current coin to the circle
            self.circle.add_widget(coinToAdd)

    def update(self):
        self.circle.update(self.user)


class UserObject(Image):
    """docstring for UserObject"""
    # Direction of user object
    direction = NumericProperty(0)
    angle = NumericProperty(90)

    def __init__(self, angle, source="images/user.zip", anim_delay=.1,
                 **kwargs):
        super(UserObject, self).__init__(**kwargs)
        self.source = source
        self.anim_delay = anim_delay
        self.angle = angle
        self.difference = 2

    def changeDirection(self):
        self.direction = 0 if self.direction == 1 else 1
        print "New direction:", self.direction

    def on_angle(self, *ignore):
        pos_hint = self.parent.parent.find_ratio(self.angle)
        self.pos_hint = {'center_x': pos_hint[0], 'center_y': pos_hint[1]}

    def update(self):
        # print "user object updated"
        if self.direction == 0:
            self.angle -= self.difference
        elif self.direction == 1:
            self.angle += self.difference


class CircleObjects(FloatLayout):
    """docstring for Coins"""

    def __init__(self, **kwargs):
        super(CircleObjects, self).__init__(**kwargs)

    def update(self, user):
        for child in self.children:
            if type(child) == Coin:
                child.update()
                if user.collide_widget(child):
                    self.remove_widget(child)
                    self.parent.parent.score += 1
            elif type(child) == UserObject:
                # here is user object
                child.update()


class Coin(Image):
    """docstring for Coin"""

    def __init__(self, source="images/coinGold.png", size=0, **kwargs):
        super(Coin, self).__init__(source=source, **kwargs)
        self.source = source

    def update(self):
        pass


class Enemy(Image):
    def __init__(self, source="images/flyFly1.png", size=0):
        super(Coin, self).__init__(source=source)
        self.source = source
        if not size:
            self.size = self.texture_size


class Game(FloatLayout):
    """Main game structure"""

    def __init__(self):
        super(Game, self).__init__()
        self.buttonExpandAnimation = Animation(
            size_hint=(.35, .35), t="out_sine",
            d=.1)
        self.buttonShrinkAnimation = Animation(
            size_hint=(.3, .3), t="in_sine",
            d=.1)

        # Determine the game is started or not when the widget is created
        self.playing = False

        # Update method
        Clock.schedule_interval(self.update, 1 / 60.0)

        # Was used for continuous animation. No need anymore and
        # not working well
        # self.buttonPressAnimation = self.buttonExpandAnimation\
        #    + self.buttonShrinkAnimation
        # self.buttonPressAnimation.repeat = "True"

    def startTurn(self, button):
        self.buttonShrinkAnimation.cancel_all(button)
        self.buttonExpandAnimation.start(button)
        directionChangeSound.play()

        self.ids.pg.user.changeDirection()

        if not self.playing:
            self.playing = True

    def stopTurn(self, button):
        self.buttonExpandAnimation.cancel_all(button)
        self.buttonShrinkAnimation.start(button)

    def update(self, *ignore):
        # Return if the game is not continuing or has not started
        if not self.playing:
            return

        # Update the playground
        self.ids.pg.update()


class CircleRun(App):
    """docstring for CircleRun"""

    def __init__(self):
        super(CircleRun, self).__init__()

    # Do not close completely when app is backgrounded
    def on_pause(self):
        return True

    def build(self):
        appWindow = Game()
        return appWindow


if __name__ == '__main__':
    CircleRun().run()
