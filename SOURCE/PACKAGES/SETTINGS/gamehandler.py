##########################
#    Custom Libraries    #
from . import gamesettings as settings
from . import gameflags as flags
##########################
#   Built-in Libraries   #
import os
import pygame as pg


class Handler():
    def __init__(self):
        pass

    def load_image(self, type, name):
        """" Load image and return image object """
        fullname = os.path.join(settings.PATH, flags.F_ASSET, type, name)
        try:
            image = pg.image.load(fullname)
            if image.get_alpha() is None:
                image = image.convert()
            else:
                image = image.convert_alpha()
        except pg.error as message:
            print('Cannot load image:', fullname)
            raise SystemExit(message)
        return image, image.get_rect()

    def read_file(self):
        pass
