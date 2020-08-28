##########################
#    Custom Libraries    #
from . import gamesettings as settings
from . import gameflags as flags
from ..OBJECTS import mapcontroller
##########################
#   Built-in Libraries   #
import os
import pygame as pg
import numpy as np


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

    def detect_local_change(self, map_state, prev_pos, pos):
        old_ground = None
        new_ground = None

        prev = np.array(prev_pos)
        cur = np.array(pos)

        prev = prev // 48
        cur = cur // 48

        prev_ground = map_state[prev[1], prev[0]]
        cur_ground = map_state[cur[1], cur[0]]

        if prev_ground == int(mapcontroller.State.B):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_BREEZE)
        elif prev_ground == int(mapcontroller.State.S):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_STENCH)
        elif prev_ground == int(mapcontroller.State.BS):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_BREEZESTENCH)
        elif prev_ground == int(mapcontroller.State.G):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_GOLD)
        elif prev_ground == int(mapcontroller.State.GB):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_GOLDBREEZE)
        elif prev_ground == int(mapcontroller.State.GS):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_GOLDSTENCH)
        elif prev_ground == int(mapcontroller.State.GBS):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_GOLDBREEZESTENCH)
        elif prev_ground == int(mapcontroller.State.P):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_PIT)
        elif prev_ground == int(mapcontroller.State.W):
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_WUMPUS)
        else:
            old_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_REVEALED)

        if cur_ground == int(mapcontroller.State.B):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_BREEZE)
        elif cur_ground == int(mapcontroller.State.S):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_STENCH)
        elif cur_ground == int(mapcontroller.State.BS):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_BREEZESTENCH)
        elif cur_ground == int(mapcontroller.State.G):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_GOLD)
        elif cur_ground == int(mapcontroller.State.GB):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_GOLDBREEZE)
        elif cur_ground == int(mapcontroller.State.GS):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_GOLDSTENCH)
        elif cur_ground == int(mapcontroller.State.GBS):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_GOLDBREEZESTENCH)
        elif cur_ground == int(mapcontroller.State.P):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_PIT)
        elif cur_ground == int(mapcontroller.State.W):
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_WUMPUS)
        else:
            new_ground, _ = self.load_image(flags.TYPE_GROUND, flags.GROUND_REVEALED)

        return old_ground, new_ground
