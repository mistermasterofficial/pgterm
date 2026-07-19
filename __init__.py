import pygame as pg
import numpy as np

class BitmapFont:
    def __init__(self, image_path, glyph_width, glyph_height):
        self.sprite_sheet = pg.image.load(image_path)
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
    def __init__(self, width, height, bitmap_font):
        self.run = True

        self.text = np.full((width, height), "\0")
        self.fgcolor = np.full((width, height, 3), 0)
        self.bgcolor = np.full((width, height, 3), 0)

        self.cursor_pos = np.full((2),0)
        self.cursor_visible = False
        self.is_scroll = True
        self.cursor_fgcolor = np.full((3),255)
        self.cursor_bgcolor = np.full((3),0)

        self.events = None

        self.set_font(bitmap_font)
    
    def set_font(self, bitmap_font):
        self.bitmap_font = bitmap_font

        self.surface = pg.Surface((self.text.shape[0]*self.bitmap_font.w,self.text.shape[1]*self.bitmap_font.h),pg.SRCALPHA)

    def update(self):
        self.events = pg.event.get()
        for e in self.events:
            if e.type == pg.QUIT:
                self.run = False

    def draw(self):
        self.surface.blit(self.bitmap_font.letters["o"],(0,0))
        for x in range(self.text.shape[0]):
            for y in range(self.text.shape[1]):
                surf = pg.Surface((self.bitmap_font.w, self.bitmap_font.h),pg.SRCALPHA)
                surf.fill(pg.Color(self.bgcolor[x][y][:]))
                surf.blit(self.bitmap_font.render(self.text[x][y],pg.Color(self.fgcolor[x][y][:])),(0,0))
                self.surface.blit(surf, (x*self.bitmap_font.w,y*self.bitmap_font.h))
        
    def mainloop(self):
        while self.run:
            self.update()
            self.draw()
    
    def scroll(self, num):
        for i in range(num):
            self.text[:,:-1] = self.text[:,1:]
            self.text[:,-1] = "\0"

    def write(self, text):
        for t in text:
            self.text[self.cursor_pos[0],self.cursor_pos[1]] = t
            self.fgcolor[self.cursor_pos[0],self.cursor_pos[1]] = self.cursor_fgcolor
            self.bgcolor[self.cursor_pos[0],self.cursor_pos[1]] = self.cursor_bgcolor

            self.cursor_pos[0]+=1
            if t=="\n" or self.cursor_pos[0]>=self.text.shape[0]:
                self.cursor_pos[0] = 0
                self.cursor_pos[1] += 1
                if self.cursor_pos[1]>=self.text.shape[1]:
                    self.cursor_pos[1] -= 1
                    if self.is_scroll:
                        self.scroll(1)
                    else:
                        self.cursor_pos[1] = 0

class TerminalWindow(Terminal):
    def __init__(self, width, height, bitmap_font):
        super().__init__(width, height, bitmap_font)

        self.set_font(bitmap_font)
        
        self.clock = pg.Clock()

    def draw(self):
        super().draw()
        self.screen.fill((0,0,0))
        self.screen.blit(self.surface, (0,0))
        pg.display.flip()

    def set_font(self, bitmap_font):
        super().set_font(bitmap_font)
        self.screen = pg.display.set_mode(self.surface.get_size())
    
    def update(self):
        self.clock.tick(60)
        super().update()

    def mainloop(self):
        super().mainloop()
        pg.quit()

if __name__=="__main__":
    pg.init()

    root = TerminalWindow(40,25,BitmapFont("bitmap_font.png",8,8))

    root.write("Hello, World!\nПривет, мир!")
    
    root.mainloop()
