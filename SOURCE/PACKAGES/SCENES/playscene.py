##########################
#    Custom Libraries    #
from . import scenebase as scene
from . import gameoverscene
# from . import titlescene
from ..SETTINGS import gameflags as flags
from ..SETTINGS import gamesettings as settings
from ..SETTINGS import gamehandler as handle
from ..OBJECTS import mapcontroller
from ..OBJECTS import agentcontroller
from ..OBJECTS import character
# from ..OBJECTS import button
from ..OBJECTS import text
##########################
#   Built-in Libraries   #
import os
import pygame as pg
import numpy as np


class PlayScene(scene.SceneBase):
    def __init__(self, screen=None):
        super().__init__(screen)

        """ Init Handler """
        self.handler = handle.Handler()

        """ Add background """
        self.default_map_size = tuple([mapcontroller.MapController.GetInstance().width * 48,
                                       mapcontroller.MapController.GetInstance().height * 48 + 64])
        self.screen = pg.display.set_mode(self.default_map_size)
        self.screen.fill((0, 0, 0))

        ground, ground_rect = self.handler.load_image(flags.TYPE_GROUND, flags.GROUND_CENSORED)
        for y_cor in range(10):
            for x_cor in range(10):
                self.screen.blit(ground, (x_cor * 48, y_cor * 48), ground_rect)

        """ Character init """
        self.char_initpos = mapcontroller.MapController.GetInstance().cave
        self.character = character.Character(self.char_initpos)
        self.character_sprite = pg.sprite.Group(self.character)

        """ Grounds init """
        self.old_ground = None
        self.new_ground = None

        self.target_ground = None
        self.affected_grounds = None

        self.new_ground, _ = self.handler.load_image(flags.TYPE_GROUND, flags.GROUND_ENTRANCE)

        """ Blit init """
        self.screen.blit(self.new_ground, self.character.pos)
        self.character_sprite.draw(self.screen)

        """ Gameplay objects """
        self.countdown_timer = 4
        self.timer = 0
        self.score = 0

        self.ready_flag = False

        """ Texts """
        pg.font.init()
        # ------ Texts list
        # ===== Font
        path = os.path.join(settings.PATH, flags.F_ASSET, flags.TYPE_FONT, flags.FONT_FIPPS)
        font = pg.font.Font(path, 20)
        # ===== Score header
        self.score_header = text.Text('Score: ', font, (255, 255, 255))
        self.score_header.text_rect.left = self.screen.get_rect().left
        self.score_header.text_rect.bottom = self.screen.get_rect().bottom
        self.score_header.text_rect.move_ip((32, -5))
        self.screen.blit(self.score_header.text, self.score_header.text_rect)
        # ===== Score
        self.score_text = text.Text(str(self.score), font, (255, 255, 255))
        self.score_text.text_rect.left = self.score_header.text_rect.right
        self.score_text.text_rect.centery = self.score_header.text_rect.centery
        self.screen.blit(self.score_text.text, self.score_text.text_rect)
        # ===== Time
        self.time_text = text.Text(str(self.countdown_timer), font, (255, 255, 255))
        self.time_text.text_rect.right = self.screen.get_rect().right
        self.time_text.text_rect.centery = self.score_header.text_rect.centery
        self.time_text.text_rect.move_ip((-32, 0))
        self.screen.blit(self.time_text.text, self.time_text.text_rect)

        """ State """
        self.state = flags.HOLD

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self, deltatime):
        # ----- Holding
        if self.state == flags.HOLD:
            self.countdown_timer -= deltatime
            if self.countdown_timer <= 0:
                self.ready_flag = True
                self.countdown_timer = 1.5
                self.state = flags.PLAYING
        # ----- Playing
        elif self.state == flags.PLAYING:
            self.countdown_timer -= deltatime
            if self.countdown_timer <= 0:
                self.ready_flag = False
                self.timer += deltatime

                self.character.play(deltatime)
                self.character_sprite.update(deltatime)

                if self.character.task != -1 and self.character.task is not None:
                    action, target = self.character.task

                    if action == agentcontroller.Action.move or action == agentcontroller.Action.pick:
                        self.old_ground, self.new_ground = \
                            self.handler.detect_local_change_target(self.character.map_state,
                                                                    self.character.prev_pos,
                                                                    self.character.pos)
                    elif action == agentcontroller.Action.shoot:
                        self.target_ground, self.affected_grounds = \
                            self.handler.detect_local_change_surroundings(self.character.map_state,
                                                                          target)

                    if self.character.score is not None:
                        self.score = self.character.score

                elif self.character.task is None:
                    self.countdown_timer = 2.5
                    self.state = flags.GAMEOVER
        # ----- Gameover
        elif self.state == flags.GAMEOVER:
            self.countdown_timer -= deltatime
            if self.countdown_timer <= 0:
                self.SwitchToScene(gameoverscene.GameOver(self.screen, self.score, self.timer))

    def Render(self):
        """ Interactive UI """

        """ Local Render """
        # ----- Holding state
        if self.state == flags.HOLD:
            # ------------------------------------------------------------- #
            # ===== Time
            censor = pg.Surface(self.time_text.text.get_size())
            self.screen.blit(censor, self.time_text.text_rect)

            self.time_text.update(str(int(self.countdown_timer)))
            self.time_text.text_rect.right = self.screen.get_rect().right
            self.time_text.text_rect.centery = self.score_header.text_rect.centery
            self.time_text.text_rect.move_ip((-32, 0))

            self.screen.blit(self.time_text.text, self.time_text.text_rect)

        # ----- Playing state
        elif self.state == flags.PLAYING:
            if self.ready_flag:
                # ------------------------------------------------------------- #
                # ===== Time
                censor = pg.Surface(self.time_text.text.get_size())
                self.screen.blit(censor, self.time_text.text_rect)

                self.time_text.update("GO!")
                self.time_text.text_rect.right = self.screen.get_rect().right
                self.time_text.text_rect.centery = self.score_header.text_rect.centery
                self.time_text.text_rect.move_ip((-32, 0))

                self.screen.blit(self.time_text.text, self.time_text.text_rect)
            else:
                # ------------------------------------------------------------- #
                # ===== Score
                censor = pg.Surface(self.score_text.text.get_size())
                self.screen.blit(censor, self.score_text.text_rect)

                self.score_text.update(str(int(self.score)))

                self.screen.blit(self.score_text.text, self.score_text.text_rect)
                # ------------------------------------------------------------- #
                # ===== Time
                censor = pg.Surface(self.time_text.text.get_size())
                self.screen.blit(censor, self.time_text.text_rect)

                self.time_text.update(str(int(self.timer)))
                self.time_text.text_rect.right = self.screen.get_rect().right
                self.time_text.text_rect.centery = self.score_header.text_rect.centery
                self.time_text.text_rect.move_ip((-32, 0))

                self.screen.blit(self.time_text.text, self.time_text.text_rect)
                # ------------------------------------------------------------- #
                # ===== Player
                if self.character.task != -1 and self.character.task is not None:
                    action, target = self.character.task

                    if action == agentcontroller.Action.move or action == agentcontroller.Action.pick:
                        char_curpos = np.array(self.character.pos) // 48
                        char_prevpos = np.array(self.character.prev_pos) // 48

                        char_curpos[[0, 1]] = char_curpos[[1, 0]]
                        char_prevpos[[0, 1]] = char_prevpos[[1, 0]]

                        if tuple(char_curpos) != self.char_initpos and tuple(char_prevpos) == self.char_initpos:
                            self.old_ground, _ = self.handler.load_image(flags.TYPE_GROUND, flags.GROUND_ENTRANCE)
                            self.screen.blit(self.old_ground, self.character.prev_pos)
                            self.screen.blit(self.new_ground, self.character.pos)
                            self.character_sprite.draw(self.screen)
                        else:
                            self.screen.blit(self.old_ground, self.character.prev_pos)
                            self.screen.blit(self.new_ground, self.character.pos)
                            self.character_sprite.draw(self.screen)
                    elif action == agentcontroller.Action.shoot:
                        target_pos = tuple([ele * 48 for ele in reversed(target)])
                        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                        for idx, direction in enumerate(directions):
                            direction = tuple(reversed(tuple([(coor + other_coor) * 48 for coor, other_coor in zip(target, direction)])))
                            directions[idx] = direction

                        self.screen.blit(self.target_ground, target_pos)
                        for idx, affected in enumerate(self.affected_grounds):
                            if not affected:
                                continue
                            else:
                                self.screen.blit(affected, directions[idx])
                        self.character_sprite.draw(self.screen)

        # ----- Gameover
        elif self.state == flags.GAMEOVER:
            # ------------------------------------------------------------- #
            # ===== Time
            censor = pg.Surface(self.time_text.text.get_size())
            self.screen.blit(censor, self.time_text.text_rect)

            self.time_text.update("GameOver")
            self.time_text.text_rect.right = self.screen.get_rect().right
            self.time_text.text_rect.centery = self.score_header.text_rect.centery
            self.time_text.text_rect.move_ip((-32, 0))

            self.screen.blit(self.time_text.text, self.time_text.text_rect)
