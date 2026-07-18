import pygame as pg
import numpy as np

class BitmapFont:
    def __init__(self, image_path, glyph_width, glyph_height):
        self.sprite_sheet = pg.image.load(image_path).convert_alpha()
        self.w = glyph_width
        self.h = glyph_height
        
        self.letters = {}
        letters_sequence = list(map(chr, list(range((self.sprite_sheet.get_width()//self.w)*(self.sprite_sheet.get_height()//self.h)))))
        
        for index, char in enumerate(letters_sequence):
            x = index%(self.sprite_sheet.get_width()//self.w) * self.w
            y = index//(self.sprite_sheet.get_width()//self.w) * self.h
            
            char_surface = pg.Surface((self.w, self.h), pg.SRCALPHA)
            char_surface.blit(self.sprite_sheet, (0, 0), (x, y, self.w, self.h))
            
            self.letters[char] = char_surface

    def render(self, char, color=(255, 255, 255)):
        text_surface = pg.Surface((self.w, self.h), pg.SRCALPHA)
        
        if char in self.letters:
            text_surface.blit(self.letters[char], (0, 0))
        
        color_surf = pg.Surface(text_surface.get_size(), pg.SRCALPHA)
        color_surf.fill(color)
        
        text_surface.blit(color_surf, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
                
        return text_surface

class Terminal:
    def __init__(self, width, height, bitmap_font_path="", bitmap_font_size=(8,8)):
        self.run = True

        self.text = np.full((width, height), "\0")
        self.fgcolor = np.full((width, height, 3), 0)
        self.bgcolor = np.full((width, height, 3), 0)

        self.cursor_pos = np.full((2),0)
        self.cursor_visible = False

        self.events = None

        self.set_font(bitmap_font_path, bitmap_font_size)
    
    def set_font(self, bitmap_font_path, bitmap_font_size):
        self.bitmap_font = BitmapFont(bitmap_font_path, bitmap_font_size[0], bitmap_font_size[1])

        self.surface = pg.Surface((self.text.shape[0]*self.bitmap_font.w,self.text.shape[1]*self.bitmap_font.h),pg.SRCALPHA)

    def update(self):
        self.events = pg.event.get()
        for e in self.events:
            if e.type == pg.QUIT:
                self.run = False

    def draw(self):
        self.surface.fill((0,0,0,0))
        for x in range(self.text.shape[0]):
            for y in range(self.text.shape[1]):
                surf = pg.Surface((self.bitmap_font.w, self.bitmap_font.h),pg.SRCALPHA)
                surf.fill(pg.Color(self.bgcolor[x][y][:]))
                surf.blit(self.bitmap_font.render(self.text[x][y],pg.Color(self.fgcolor[x][y][:])),(x*self.bitmap_font.w,y*self.bitmap_font.h))
        
    def mainloop(self):
        while self.run:
            self.update()
            self.draw()

class TerminalWindow(Terminal):
    def __init__(self, width, height, bitmap_font_path="", bitmap_font_size=(8, 8)):
        pg.init()

        pg.display.set_mode((1, 1), pg.HIDDEN)

        super().__init__(width, height, bitmap_font_path, bitmap_font_size)

        self.set_font(bitmap_font_path, bitmap_font_size)
        
        self.clock = pg.Clock()

    def draw(self):
        super().draw()
        self.screen.fill((0,0,0))
        self.screen.blit(self.surface, (0,0))

    def set_font(self, bitmap_font_path, bitmap_font_size):
        super().set_font(bitmap_font_path, bitmap_font_size)
        self.screen = pg.display.set_mode(self.surface.get_size(), pg.NOFRAME|pg.SCALED)
    
    def update(self):
        self.clock.tick(60)
        super().update()

    def mainloop(self):
        super().mainloop()
        pg.quit()

if __name__=="__main__":
    root = TerminalWindow(8,8,"bitmap_font.png",(8,8))
    root.mainloop()
