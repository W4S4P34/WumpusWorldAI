##########################
#    Custom Libraries    #

##########################
#   Built-in Libraries   #
import pygame as pg


class Text(pg.sprite.Sprite):
    # Constructor
    def __init__(self, text, font, color):
        # Call the parent class (Sprite) constructor
        pg.sprite.Sprite.__init__(self)
        """ Self attributes """
        self.font = font
        self.color = color
        self.text = self.font.render(text, 1, self.color)
        self.text_rect = self.text.get_rect()

    def update(self, text):
        self.text = self.font.render(text, 1, self.color)
        new_text_rect = self.text.get_rect()

        current_position = tuple(self.text_rect[0], self.text_rect[1])
        current_rect = tuple(new_text_rect[2], new_text_rect[3])

        self.text_rect = pg.Rect(current_position, current_rect)
