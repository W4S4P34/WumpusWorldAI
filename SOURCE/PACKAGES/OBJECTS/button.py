##########################
#    Custom Libraries    #
from ..SETTINGS import gameflags as flags
from ..SETTINGS import gamehandler as handle
##########################
#   Built-in Libraries   #
import pygame as pg


class Button(pg.sprite.Sprite):
    # Constructor
    def __init__(self, image_flag=None):
        # Call the parent class (Sprite) constructor
        pg.sprite.Sprite.__init__(self)
        """ Init Handler """
        self.handler = handle.Handler()
        """ Self attributes """
        self.image_flag = image_flag
        self.image, self.rect = self.handler.load_image(flags.TYPE_MISC, self.image_flag)
        self.is_hover = False

    def switch(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            if not self.is_hover:
                self.is_hover = True
                self.image.fill((25, 25, 25, 0), special_flags=pg.BLEND_RGBA_SUB)
        else:
            self.is_hover = False
            self.image, _ = self.handler.load_image(flags.TYPE_MISC, self.image_flag)
