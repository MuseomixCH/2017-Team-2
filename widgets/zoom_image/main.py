# -*- coding: utf-8 -*-
import kivy
kivy.require('1.0.8')
from kivy.app import App

from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.lang import Builder

from kivy.graphics.transformation import Matrix
from kivy.vector import Vector
from kivy.animation import Animation
from math import radians
import os

base_dir = os.path.dirname(__file__)
kv = os.path.join(base_dir, 'main.kv')
Builder.load_file(kv)


####################################### ZOOM IMAGE  ##########################################

class ZIScatter(Scatter):
    zoom_image = ObjectProperty( Widget() )
    init_pos = ObjectProperty( (75,70) )

    def __init__(self,**kwargs):
        super(ZIScatter, self).__init__(**kwargs)
        self.anim = Animation() # Physics simple animation on touch up
        Clock.schedule_interval(self.clear_canvas, 0)
        Clock.schedule_interval(self.control_pos, 0)

    def clear_canvas(self, dt):
        self.canvas.clear()

    def is_leaving_its_box(self):
        #check if scatter is leaving its box
        s = self.scale
        x, y = self.pos
        w, h = self.size
        container = c = self.zoom_image
        #check every corner
        limitx = limity = False
        if (x > c.x or x + w*s < c.x + c.width) :
            limitx = True
        if (y > c.y or y + h*s < c.y + c.height):
            limity = True
        return (limitx, limity)

    def fix_after_leaving_its_box(self):
        #check if scatter is leaving its box
        s = self.scale
        x, y = self.pos
        w, h = self.size
        container = c = self.zoom_image
        #check every corner
        limitx = limity = False
        if x > c.x :
            x = c.x
        if x + w*s < c.x + c.width :
            x = c.x + c.width - w*s
        if y > c.y :
            y = c.y
        if y + h*s < c.y + c.height:
            y = c.y + c.height - h*s
        self.pos = (x,y)

    def control_pos(self, dt):
        if self.scale <= 1.03 :
            self.reset()
            pass
        #avoid scatter leaving its box while physics animation is going on (after touch up)
        if len(self._touches) > 0:
            return
        limitx, limity = self.is_leaving_its_box()
        if limitx == True or limity == True:
            self.anim.cancel(self)
            self.fix_after_leaving_its_box()

    def transform_with_touch(self, touch):
        init_pos = self.center
        init_scale = self.scale
        init_touch_len = len(self._touches)
        #super(ZIScatter, self).transform__with__touch(touch)

        # just do a simple one finger drag
        if len(self._touches) == 1 and self.scale >1.05 : #THIS IS NOT IN ORIGINAL SCATTER:
            # _last_touch_pos has last pos in correct parent space,
            # just like incoming touch
            dx = (touch.x - self._last_touch_pos[touch][0]) \
                    * self.do_translation_x
            dy = (touch.y - self._last_touch_pos[touch][1]) \
                    * self.do_translation_y
            self.apply_transform(Matrix().translate(dx, dy, 0))
            #return

        elif len(self._touches) == 1 and self.scale <1.05 : #THIS IS NOT IN ORIGINAL SCATTER:
            return

        else : #TO AVOID RETURN IN ORIGINAL SCATTER
            # we have more than one touch...
            points = [Vector(self._last_touch_pos[t]) for t in self._touches]

            # we only want to transform if the touch is part of the two touches
            # furthest apart! So first we find anchor, the point to transform
            # around as the touch farthest away from touch
            anchor = max(points, key=lambda p: p.distance(touch.pos))

            # now we find the touch farthest away from anchor, if its not the
            # same as touch. Touch is not one of the two touches used to transform
            farthest = max(points, key=anchor.distance)
            if points.index(farthest) != self._touches.index(touch):
                return

            # ok, so we have touch, and anchor, so we can actually compute the
            # transformation
            old_line = Vector(*touch.ppos) - anchor
            new_line = Vector(*touch.pos) - anchor

            angle = radians(new_line.angle(old_line)) * self.do_rotation
            self.apply_transform(Matrix().rotate(angle, 0, 0, 1), anchor=anchor)

            if self.do_scale:
                scale = new_line.length() / old_line.length()
                new_scale = scale * self.scale
                if new_scale < self.scale_min or new_scale > self.scale_max:
                    scale = 1.0
                self.apply_transform(Matrix().scale(scale, scale, scale),
                                 anchor=anchor)

        #avoid scatter leaving its box
        limitx, limity = self.is_leaving_its_box()
        if limitx or limity:
            #cancel previous apply_transform
            if init_touch_len == 1:
                ddx = ddy = 0
                if limitx: ddx = - dx
                if limity: ddy = - dy
                self.apply_transform(Matrix().translate(ddx, ddy, 0))
            else:
                if self.do_scale:
                    #self.apply_transform(Matrix().scale(scale/init_scale, scale/init_scale, scale/init_scale),
                    #             anchor=anchor)
                    # control
                    #limitx, limity = self.is_leaving_its_box()
                    #if limitx or limity:
                    self.fix_after_leaving_its_box()

    def on_touch_down(self, touch):
        ret = super(ZIScatter, self).on_touch_down(touch)
        x, y = touch.x, touch.y
        #if not self.zoom_image.image.collide_point(x,y):
        #    # did not touch the mask area
        #    return True

        # if the touch isnt on the widget we do nothing
        if self.zoom_image.collide_point(x, y):
            if touch.is_double_tap:
                self.reset()

        #if not self.parent.image.collide_point(x,y):
        #    # did not touch the mask area
        #    touch.ud["outside"] = True
        #    return False

        return ret

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super(ZIScatter, self).on_touch_up(touch)
        """
        x, y = touch.x, touch.y
        # if the touch isnt on the widget we do nothing
        if self.zoom_image.collide_point(x, y):
            super(ZIScatter, self).on_touch_up(touch)
        """

        ###TAKEN FROM ORIGINAL SCATTER
        x, y = touch.x, touch.y
        # if the touch isnt on the widget we do nothing, just try children
        if self.zoom_image.collide_point(x, y): #MODIFIED ORIGINAL SCATTER !!
          if not touch.grab_current == self:
            touch.push()
            touch.apply_transform_2d(self.to_local)
            if super(Scatter, self).on_touch_up(touch):
                touch.pop()
                return True
            touch.pop()

        # remove it from our saved touches
        if touch in self._touches and touch.grab_state:
            touch.ungrab(self)
            del self._last_touch_pos[touch]
            self._touches.remove(touch)

        # stop propagating if its within our bounds
        if self.collide_point(x, y):
            pass#eturn True #MODIFIED ORIGINAL SCATTER !!


        # physics behaviour on touch up, fade speed down on the same direction
        return False

        duration = d = 1.5
        dx = touch.dx * 3 * d
        dy = touch.dy * 3 * d
        #print dx, dy
        adx = abs(dx)
        ady = abs(dy)
        if adx > 0 and ady > 0:
                #if adx > 400 :
                #if ady > 400 :
                V = Vector(self.center)
                Vd = Vector( (dx,dy) )
                destination = V + Vd

                anim = Animation(center = destination, d = d, t = 'out_expo', s = 1 / 150. )
                self.anim.stop(self)
                self.anim = anim
                self.anim.start(self)
                self.previous_anim_dest = destination
        return False

    def reset(self):
        self.center = self.init_pos
        self.scale = 1


class ZoomImage(FloatLayout):
    scatter = ObjectProperty( ZIScatter() )
    source = StringProperty( '105_01.jpg' )
    im = ObjectProperty( None )
    image = ObjectProperty(None)

    def __init__(self,**kwargs):
        super(ZoomImage, self).__init__(**kwargs)
        self.bind(source=self.refresh)

    def reset(self):
        self.scatter.reset()

    def refresh(self, instance, val):
        if self.im:
            self.im.source = self.source




class ZIScatter2(ZIScatter):
    zoom_image = ObjectProperty(None)

    def on_touch_up(self, touch):
        ret = super(ZIScatter2, self).on_touch_up(touch)
        x,y = touch.pos
        x,y = self.to_local(x,y)
        ghost_widget = self.zoom_image.get_focus_pos_size()
        if ghost_widget.collide_point(x,y):
            self.zoom_image.on_focus()
        else:
            self.zoom_image.on_unfocus()
        return ret


class ZoomImageWithFocusRectangle(ZoomImage):
    focus_pos = ObjectProperty((0.2,0.2)) #relative to scatter size: x and y between 0,1
    focus_size_hint = ObjectProperty((.5,.5)) #relative to scatter size
    focus = ObjectProperty(Image(source=""))
    focus_source = StringProperty("272_01.jpg")

    def get_focus_pos_size(self, *args):
        s = self.scatter
        rx, ry = self.focus_pos
        rw, rh = self.focus_size_hint
        sw, sh = s.size
        pos = (rx * sw, ry * sh)
        size = (rw * sw, rh * sh)
        self.ghost_widget = gw = Widget(pos=pos, size=size)

        return gw

    def on_focus(self, *kwargs):
        print "on_focus"

    def on_unfocus(self, *kwargs):
        print "on_unfocus"



######################################## APP LAUNCHER ###########################################

class ZiApp(App):

    def build(self):
        #print '# Launch Fresco APP'
        #self.zoomi = ZoomImage(size = (350,350), pos = (100,200) )
        self.zoomi = ZoomImageWithFocusRectangle(size = (350,350), pos = (100,200) )
        return self.zoomi


if __name__ in ('__main__','__android__'):
    ZiApp().run()
