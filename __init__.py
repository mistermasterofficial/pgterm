import pygame as pg
import numpy as np

pg.init()

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

    def render(self, text, color=(255, 255, 255)):
        text_surface = pg.Surface((self.w*len(text), self.h), pg.SRCALPHA)
        
        for index, char in enumerate(text):
            if char in self.letters:
                text_surface.blit(self.letters[char], (self.w*index, 0))
        
        color_surf = pg.Surface(text_surface.get_size(), pg.SRCALPHA)
        color_surf.fill(color)
        
        text_surface.blit(color_surf, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
                
        return text_surface

class TerminalCursor:
    def __init__(self, width, height):
        self.x, self.y = 0, 0
        self.width = width
        self.height = height

        self.fgcolor = np.full((3),255)
        self.bgcolor = np.full((3),0)

        self.visible = True
        self.blink_duration = 500
    
    def to_bottom(self):
        self.y = self.height-1
    
    def to_right(self):
        self.x = self.width-1
    
    def check(self):
        is_scroll = False
        if self.x>=self.width or self.x<0:
            self.y += self.x//self.width
            self.x = self.x % self.width
        self.y = max(0, self.y)
        if self.y>=self.height:
            self.y = min(self.y+1 - self.height, self.height)
            is_scroll = True
        return is_scroll

class Terminal:
    def __init__(self, width, height, bitmap_font):
        self.run = True

        self.text = np.full((width, height), "\0")
        self.fgcolor = np.full((width, height, 3), 255)
        self.bgcolor = np.full((width, height, 3), 0)

        self.cursor = TerminalCursor(width,height)
        self.is_scroll = True

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
                fgcolor = self.fgcolor[x][y][:]
                bgcolor = self.bgcolor[x][y][:]
                if self.cursor.x==x and self.cursor.y==y and self.cursor.visible and int((pg.time.get_ticks()%self.cursor.blink_duration)/self.cursor.blink_duration*2):
                    fgcolor, bgcolor = bgcolor, fgcolor
                surf = pg.Surface((self.bitmap_font.w, self.bitmap_font.h),pg.SRCALPHA)
                surf.fill(pg.Color(bgcolor))
                surf.blit(self.bitmap_font.render(self.text[x][y],pg.Color(fgcolor)),(0,0))
                self.surface.blit(surf, (x*self.bitmap_font.w,y*self.bitmap_font.h))
    
    def scroll(self, num):
        for i in range(num):
            self.text[:,:-1] = self.text[:,1:]
            self.text[:,-1] = "\0"

    def write(self, *text):
        text = "".join(list(text))
        for t in range(len(text)):
            match text[t]:
                case "\n":
                    self.cursor.x = 0
                    self.cursor.y += 1
                case "\t":
                    self.cursor.x += 4
                case "\v":
                    self.cursor.y += 4
                case "\r":
                    self.cursor.x = 0
                case _:
                    self.text[self.cursor.x,self.cursor.y] = text[t]
                    self.fgcolor[self.cursor.x,self.cursor.y] = self.cursor.fgcolor
                    self.bgcolor[self.cursor.x,self.cursor.y] = self.cursor.bgcolor
                    self.cursor.x+=1
            
            if self.cursor.check():
                if self.is_scroll:
                    self.scroll(self.cursor.y)
                    self.cursor.to_bottom()
                else:
                    self.cursor.y -= 1
    
    def writeln(self, *text):
        self.write(*text,"\n")
    
    def draw_charimage(self, charimage):
        x = self.cursor.x*1
        for i in range(charimage.shape[1]):
            for j in range(charimage.shape[0]):
                self.write(charimage[j, i])
            if i<charimage.shape[1]-1:
                self.writeln()
            self.cursor.x = x
        self.cursor.y -= charimage.shape[1]-1

class CharImage:
    @staticmethod
    def get(x, y, width, height, bitmap_width=16):
        src = np.full((width, height),"\0")

        for i in range(width):
            for j in range(height):
                src[i,j] = chr((x+i)+(y+j)*bitmap_width)
        
        return src
            

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
        self.screen = pg.display.set_mode(self.surface.get_size(), pg.SCALED)
    
    def update(self):
        self.clock.tick(60)
        super().update()

    def mainloop(self):
        while self.run:
            self.update()
            self.draw()
        pg.quit()

if __name__=="__main__":
    root = TerminalWindow(40,25,BitmapFont("IBM_EGA_8x8.png",8,8))

    root.writeln("Hello, World!\nПривет, мир!")
    root.write("▓▒░\v\r")
    root.writeln("←↑→↓↔↕↨▀▄█▌▐■□▪▫▬▲►▼◄○●◘◙◦")
    root.write("0123456789ABC\tDEF\r")

    root.draw_charimage(CharImage.get(0,80,4,4))
    
    root.mainloop()
