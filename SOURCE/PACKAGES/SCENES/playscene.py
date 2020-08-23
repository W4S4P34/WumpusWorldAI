##########################
#    Custom Libraries    #
from . import scenebase as scene
from . import titlescene
from ..SETTINGS import gameflags as flags
from ..SETTINGS import gamesettings as settings
# from ..SETTINGS import gamehandler as handle
from ..OBJECTS import button
from ..OBJECTS import text
##########################
#   Built-in Libraries   #
import os
import pygame as pg


class PlayScene(scene.SceneBase):
    def __init__(self, screen=None):
        super().__init__(screen)
        # Add background
        # The game scene is just a gray screen
        self.screen.fill((50, 50, 50))

        # Buttons
        """ Buttons list """
        """# Create buttons list #"""
        self.button_list = []
        for _ in range(2):
            self.button_list.append(button.Button(flags.BUTTON_BG))

        """# Put buttons in right places #"""
        distance_hor = 30      # Horizontal distance between buttons
        distance_ver = 0       # Vertical distance between buttons
        col_num = 2
        # row_num = 1

        for idx, bt in enumerate(self.button_list):
            bt.rect.center = self.screen.get_rect().center

            bt_width = bt.rect[2]
            bt_height = bt.rect[3]

            coef = 1
            if (idx % 2 == 0):
                coef = -1
            else:
                coef = 1

            bt.rect.move_ip(((bt_width + distance_hor) * coef,
                            128 + (idx // col_num) * (bt_height + distance_ver)))

        # Texts
        pg.font.init()
        """ Texts list """
        """# Game title #"""
        path = os.path.join(settings.PATH, flags.F_ASSET, flags.TYPE_FONT, flags.FONT_FIPPS)

        title_font = pg.font.Font(path, 35)

        self.title = text.Text('Not implement yet!', title_font, (255, 255, 255))
        self.title.text_rect.center = self.screen.get_rect().center
        self.screen.blit(self.title.text, self.title.text_rect)
        """# Buttons' texts list #"""
        self.text_list = []

        button_font = pg.font.Font(path, 20)

        for idx in range(len(self.button_list)):
            txt = ''
            if idx == 0:
                txt = 'Back'
            elif idx == 1:
                txt = 'Exit'
            self.text_list.append(text.Text(txt, button_font, (255, 255, 255)))

        for idx, t in enumerate(self.text_list):
            t.text_rect.center = self.button_list[idx].rect.center
            t.text_rect.move_ip((5, 0))

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                for idx, bt in enumerate(self.button_list):
                    if bt.rect.collidepoint(pg.mouse.get_pos()):
                        if idx == 0:
                            self.SwitchToScene(titlescene.TitleScene(self.screen))
                            bt.is_over = False
                        elif idx == 1:
                            self.Terminate()

    def Update(self, deltatime):
        ##################################################################################
        # Collisions
        for bt in self.button_list:
            bt.switch()
        ##################################################################################

    def Render(self):
        """Interactive UI"""
        for bt in self.button_list:
            self.screen.blit(bt.image, bt.rect)
        for t in self.text_list:
            self.screen.blit(t.text, t.text_rect)
