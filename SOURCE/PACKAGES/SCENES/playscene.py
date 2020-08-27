##########################
#    Custom Libraries    #
from . import scenebase as scene
# from . import titlescene
from ..SETTINGS import gameflags as flags
# from ..SETTINGS import gamesettings as settings
from ..SETTINGS import gamehandler as handle
from ..OBJECTS import mapcontroller
from ..OBJECTS import agentcontroller
from ..OBJECTS import character
# from ..OBJECTS import button
# from ..OBJECTS import text
##########################
#   Built-in Libraries   #
# import os
import pygame as pg


class PlayScene(scene.SceneBase):
    def __init__(self, screen=None):
        super().__init__(screen)

        """ Init Handler """
        self.handler = handle.Handler()

        # Add background
        self.default_map_size = (320, 320)
        self.screen = pg.display.set_mode(self.default_map_size)

        ground, ground_rect = self.handler.load_image(flags.TYPE_GROUND, flags.GROUND_CENSORED)
        for y_cor in range(10):
            for x_cor in range(10):
                self.screen.blit(ground, (x_cor * 32, y_cor * 32), ground_rect)

        # Character Init
        initpos = mapcontroller.MapController.GetInstance().cave
        self.character = character.Character(initpos)
        self.character_sprite = pg.sprite.Group(self.character)

        # Grounds
        self.old_ground, _ = self.handler.load_image(flags.TYPE_GROUND, flags.GROUND_REVEALED)
        self.new_ground, _ = self.handler.load_image(flags.TYPE_GROUND, flags.GROUND_REVEALED)

        # Buttons
        """ Buttons list """
        """# Create buttons list #"""
        self.button_list = []

        """# Put buttons in right places #"""

        # Texts
        pg.font.init()
        """ Texts list """
        """# Buttons' texts list #"""
        self.text_list = []

        # Gameplay
        self.countdown_timer = 0
        self.map_state = None

        # State
        self.state = flags.HOLD

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self, deltatime):
        # Holding
        if self.state == flags.HOLD:
            self.countdown_timer -= deltatime
            if self.countdown_timer <= 0:
                self.countdown_timer = 0
                self.state = flags.PLAYING
        # Playing
        elif self.state == flags.PLAYING:
            self.countdown_timer -= deltatime
            if self.countdown_timer <= 0:
                self.map_state = self.character.play(deltatime)
                self.character_sprite.update(deltatime)

                if self.map_state is not None:
                    self.old_ground, self.new_ground = self.handler.detect_local_change(self.map_state,
                                                                                        self.character.prev_pos,
                                                                                        self.character.pos)

    def Render(self):
        """Interactive UI"""
        for bt in self.button_list:
            self.screen.blit(bt.image, bt.rect)
        for t in self.text_list:
            self.screen.blit(t.text, t.text_rect)
        """Character Render"""
        if self.map_state is not None:
            self.screen.blit(self.old_ground, self.character.prev_pos)
            self.screen.blit(self.new_ground, self.character.pos)
            self.character_sprite.draw(self.screen)
