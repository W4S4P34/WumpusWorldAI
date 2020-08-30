##########################
#    Custom Libraries    #
from . import scenebase as scene
from . import titlescene
from ..SETTINGS import gameflags as flags
from ..SETTINGS import gamesettings as settings
from ..SETTINGS import gamehandler as handle
from ..OBJECTS import mapcontroller
from ..OBJECTS import button
from ..OBJECTS import text
##########################
#   Built-in Libraries   #
import os
import pygame as pg


class GameOver(scene.SceneBase):
    def __init__(self, screen=None, score=0, time=0):
        super().__init__(screen)

        """ Init Handler """
        self.handler = handle.Handler()

        """ Add background """
        self.screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.screen.fill((0, 0, 0))

        """ Attributes """
        self.inc_score = 0
        self.inc_time = 0
        self.score = score
        self.time = time

        """ Buttons """
        # ----- Create buttons list
        self.button_list = []
        for _ in range(2):
            self.button_list.append(button.Button(flags.BUTTON_BG))

        # ----- Put buttons in right places
        distance_hor = 100      # Horizontal distance between buttons
        distance_ver = 0        # Vertical distance between buttons

        for idx, bt in enumerate(self.button_list):
            bt.rect.center = self.screen.get_rect().center

            row_idx = idx // 2
            col_idx = idx % 2

            if col_idx == 0:
                col_idx = -1
            else:
                col_idx = 1

            bt_width = bt.rect[2]
            bt_height = bt.rect[3]

            bt.rect.move_ip((col_idx * (bt_width + distance_hor), 170 + (row_idx * (bt_height + distance_ver))))

        """ Texts """
        pg.font.init()
        # ------ Title
        # ===== Font
        path = os.path.join(settings.PATH, flags.F_ASSET, flags.TYPE_FONT, flags.FONT_FIPPS)
        font = pg.font.Font(path, 30)
        # ===== Title text
        self.title = text.Text('Result', font, (255, 255, 255))
        self.title.text_rect.centerx = self.screen.get_rect().centerx
        self.screen.blit(self.title.text, self.title.text_rect)

        # ------ Texts for buttons
        self.text_list = []

        button_font = pg.font.Font(path, 20)

        for idx in range(len(self.button_list)):
            txt = ''
            if idx == 0:
                txt = 'Reset'
            elif idx == 1:
                txt = 'Exit'
            self.text_list.append(text.Text(txt, button_font, (255, 255, 255)))

        for idx, t in enumerate(self.text_list):
            t.text_rect.center = self.button_list[idx].rect.center
            t.text_rect.move_ip((5, 0))

        # ------ Texts list
        # ===== Font
        path = os.path.join(settings.PATH, flags.F_ASSET, flags.TYPE_FONT, flags.FONT_FIPPS)
        font = pg.font.Font(path, 20)
        # ===== Score header
        self.score_header = text.Text('Score: ', font, (255, 255, 255))
        self.score_header.text_rect.right = self.screen.get_rect().centerx
        self.score_header.text_rect.centery = self.screen.get_rect().centery
        self.score_header.text_rect.move_ip((0, -20))
        self.screen.blit(self.score_header.text, self.score_header.text_rect)
        # ===== Score
        self.score_text = text.Text(str(self.score), font, (255, 255, 255))
        self.score_text.text_rect.left = self.score_header.text_rect.right
        self.score_text.text_rect.centery = self.score_header.text_rect.centery
        self.screen.blit(self.score_text.text, self.score_text.text_rect)
        # ===== Time header
        self.time_header = text.Text('Time: ', font, (255, 255, 255))
        self.time_header.text_rect.right = self.screen.get_rect().centerx
        self.time_header.text_rect.centery = self.screen.get_rect().centery
        self.time_header.text_rect.move_ip((0, 20))
        self.screen.blit(self.time_header.text, self.time_header.text_rect)
        # ===== Time
        self.time_text = text.Text(str(self.score), font, (255, 255, 255))
        self.time_text.text_rect.left = self.time_header.text_rect.right
        self.time_text.text_rect.centery = self.time_header.text_rect.centery
        self.screen.blit(self.time_text.text, self.time_text.text_rect)

        """ Countdown """
        self.countdown = 1.5

        """ State """
        self.state = flags.GAMEOVER

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                for idx, bt in enumerate(self.button_list):
                    if bt.rect.collidepoint(pg.mouse.get_pos()):
                        if idx == 0:
                            self.SwitchToScene(titlescene.TitleScene(self.screen))
                        elif idx == 1:
                            self.Terminate()

    def Update(self, deltatime):
        ##################################################################################
        # Collisions
        for bt in self.button_list:
            bt.switch()
        ##################################################################################
        self.countdown -= deltatime
        if self.countdown <= 0:
            if self.inc_score != self.score:
                if self.inc_score < self.score:
                    self.inc_score += 10
                if self.inc_score > self.score:
                    self.inc_score -= 10
                else:
                    self.inc_score = self.score

            if self.inc_time < self.time:
                self.inc_time += 1

    def Render(self):
        """Interactive UI"""
        for bt in self.button_list:
            self.screen.blit(bt.image, bt.rect)
        for t in self.text_list:
            self.screen.blit(t.text, t.text_rect)
        """ Local Render """
        # ------------------------------------------------------------- #
        # ===== Score
        censor = pg.Surface(self.score_text.text.get_size())
        self.screen.blit(censor, self.score_text.text_rect)

        self.score_text.update(str(self.inc_score))

        self.screen.blit(self.score_text.text, self.score_text.text_rect)
        # ------------------------------------------------------------- #
        # ===== Time
        censor = pg.Surface(self.time_text.text.get_size())
        self.screen.blit(censor, self.time_text.text_rect)

        self.time_text.update(str(self.inc_time))

        self.screen.blit(self.time_text.text, self.time_text.text_rect)
