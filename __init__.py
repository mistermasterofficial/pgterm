import pygame as pg
import numpy as np
from copy import deepcopy
from threading import Thread
from queue import Queue

def thread(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper

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

        self.events = []

        self.set_font(bitmap_font)
    
    def set_font(self, bitmap_font):
        self.bitmap_font = bitmap_font

        self.surface = pg.Surface((self.text.shape[0]*self.bitmap_font.w,self.text.shape[1]*self.bitmap_font.h),pg.SRCALPHA)

    def update(self):
        pass

    def draw(self):
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

            self.fgcolor[:,:-1] = self.fgcolor[:,1:]
            self.fgcolor[:,-1] = self.cursor.fgcolor

            self.bgcolor[:,:-1] = self.bgcolor[:,1:]
            self.bgcolor[:,-1] = self.cursor.bgcolor

    def cursor_scroll(self):
        if self.cursor.check():
            if self.is_scroll:
                self.scroll(self.cursor.y)
                self.cursor.to_bottom()
            else:
                self.cursor.y -= 1

    def write(self, *text):
        text = "".join(list(text))
        shift = 0
        for t in range(len(text)):
            if t+shift>=len(text): break

            if text[t+shift:t+shift+2]=="\x1b[":
                code = ""
                shift += 2
                while not text[t+shift].isalpha():
                    code += text[t+shift]
                    shift += 1
                code += text[t+shift]
                self.ansi_esc_handler(code)
                continue

            match text[t+shift]:
                case "\n":
                    self.cursor.x = 0
                    self.cursor.y += 1
                case "\t":
                    self.cursor.x += 4
                case "\v":
                    self.cursor.y += 4
                case "\r":
                    self.cursor.x = 0
                case "\b":
                    self.cursor.x -= 1
                case "\f":
                    self.cursor.y += 1
                case _:
                    self.text[self.cursor.x,self.cursor.y] = text[t+shift]
                    self.fgcolor[self.cursor.x,self.cursor.y] = self.cursor.fgcolor
                    self.bgcolor[self.cursor.x,self.cursor.y] = self.cursor.bgcolor
                    self.cursor.x+=1
            
            self.cursor_scroll()
    
    def writeln(self, *text):
        self.write(*text,"\n")

    def set_fg_color(self, color):
        if type(color) is tuple or type(color) is list:
            self.cursor.fgcolor[0] = color[0]
            self.cursor.fgcolor[1] = color[1]
            self.cursor.fgcolor[2] = color[2]
        elif type(color) is pg.Color:
            self.cursor.fgcolor[0] = color.r
            self.cursor.fgcolor[1] = color.g
            self.cursor.fgcolor[2] = color.b

    def set_bg_color(self, color):
        if type(color) is tuple or type(color) is list:
            self.cursor.bgcolor[0] = color[0]
            self.cursor.bgcolor[1] = color[1]
            self.cursor.bgcolor[2] = color[2]
        elif type(color) is pg.Color:
            self.cursor.bgcolor[0] = color.r
            self.cursor.bgcolor[1] = color.g
            self.cursor.bgcolor[2] = color.b

    def ansi_esc_handler(self, code):
        args = code[:-1].split(";")
        mode = code[-1].lower()
        if hasattr(self, "ansi_esc_"+mode):
            getattr(self, "ansi_esc_"+mode)(args)

    def ansi_esc_h(self, args):
        if len(args)<=1:
            self.cursor.x = 0
            self.cursor.y = 0
        elif len(args)==2:
            self.ansi_esc_f(args)

    def ansi_esc_f(self, args):
        self.cursor.x = int(args[0])
        self.cursor.y = int(args[1])
        self.cursor_scroll()

    def ansi_esc_a(self, args):
        self.cursor.y -= int(args[0])
        self.cursor_scroll()

    def ansi_esc_b(self, args):
        self.cursor.y += int(args[0])
        self.cursor_scroll()

    def ansi_esc_c(self, args):
        self.cursor.x += int(args[0])
        self.cursor_scroll()

    def ansi_esc_d(self, args):
        self.cursor.x -= int(args[0])
        self.cursor_scroll()

    def ansi_esc_m(self, args):
        for a in args:
            colors = [
                "black",
                "darkred",
                "darkgreen",
                "darkyellow",
                "darkblue",
                "darkmagenta",
                "darkcyan",
                "gray",
                "",
                "default"
            ]
            
            if a=="0":
                self.set_fg_color(pg.Color("white"))
                self.set_bg_color(pg.Color("black"))
                continue

            if a[:-1]=="9" or a[:-1]=="10":
                colors = [
                    "darkgray",
                    "red",
                    "green",
                    "yellow",
                    "blue",
                    "magenta",
                    "cyan",
                    "white",
                    "",
                    "default"
                ]

            func = "set_"
            if a[:-1]=="3" or a[:-1]=="9":
                func += "fg_color"
                colors[-1] = "white"
            if a[:-1]=="4" or a[:-1]=="10":
                func += "bg_color"
                colors[-1] = "black"

            if hasattr(self, func):
                getattr(self, func)(pg.Color(colors[int(a[-1])]))

class CharImage:
    @staticmethod
    def get_bitmap_image(x, y, width, height, bitmap_width=16):
        src = ""

        for i in range(height):
            for j in range(width):
                src += chr((x+j)+(y+i)*bitmap_width)
            src += f"\x1b[{width}d"
            if i<width-1:
                src += "\x1b[1b"
            else:
                src += f"\x1b[{height-1}a"
        
        return src

    @staticmethod
    def get_ansi_art_image(filename, scaleY=2):
        with open(filename,"r") as f:
            data = f.readlines()
        result = ""
        for d in data:
            result += d*scaleY
        return result

class TerminalWindow(Terminal):
    def __init__(self, width, height, bitmap_font, display_flags=pg.SCALED, fps=60, events_queue_size=1):
        self.display_flags = display_flags
        super().__init__(width, height, bitmap_font)
        
        pg.mouse.set_visible(False)
        self.events_queue = Queue(maxsize=events_queue_size)
        self.clock = pg.Clock()
        self.fps = fps

        self.is_freeze = False

    def freeze(self):
        self.is_freeze = True

    def unfreeze(self):
        self.is_freeze = False

    def draw(self):
        if not self.is_freeze:
            super().draw()
        self.screen.fill((0,0,0))
        self.screen.blit(self.surface, (0,0))
        pg.display.flip()

    def set_font(self, bitmap_font):
        super().set_font(bitmap_font)
        self.set_mode(self.display_flags)
    
    def set_mode(self, display_flags):
        self.screen = pg.display.set_mode(self.surface.get_size(), display_flags)
        self.display_flags = display_flags
    
    def update(self):
        self.clock.tick(self.fps)
        self.events = pg.event.get()
        self.events_queue.put(self.events)
        for e in self.events:
            if e.type == pg.QUIT:
                self.run = False
        super().update()

    def get_events(self):
        return self.events_queue.get()

    def waitkey(self, key=None):
        clock = pg.Clock()

        while True:
            clock.tick(self.fps)
            events = self.get_events()

            for e in events:
                if e.type==pg.KEYDOWN and (key is None or e.key==key):
                    return
    
    def input(self, placeholder="", size=0, password_char=""):
        result = placeholder
        old_result = deepcopy(result)
        if size>0:
            result = result[:min(len(result),size)]
        cursor = len(result)
        old_cursor = deepcopy(cursor)
        max_size = len(result)
        is_visible = deepcopy(self.cursor.visible)
        clock = pg.Clock()

        self.cursor.x += cursor

        while True:
            clock.tick(self.fps)

            events = self.get_events()

            for e in events:
                if e.type==pg.KEYDOWN:
                    if e.key==pg.K_RETURN:
                        self.cursor.visible = False
                        self.cursor.x -= old_cursor
                        self.cursor.x += max_size
                        self.cursor.check()
                        self.cursor.visible = is_visible
                        self.writeln()
                        return result
                    elif e.key==pg.K_HOME:
                        cursor = 0
                    elif e.key==pg.K_END:
                        cursor = len(result)
                    elif e.key==pg.K_BACKSPACE:
                        result = result[:cursor-1]+result[cursor:]
                        cursor = max(cursor-1, 0)
                    elif e.key==pg.K_DELETE:
                        result = result[:cursor]+result[cursor+1:]
                    elif e.key==pg.K_LEFT:
                        cursor = max(0, cursor-1)
                    elif e.key==pg.K_RIGHT:
                        cursor = min(len(result), cursor+1)
                    elif len(pg.key.name(e.key))==1 or e.unicode:
                        new_result = result[:cursor]+e.unicode+result[cursor:]
                        if (size>0 and len(new_result)<=size) or size<=0:
                            result = new_result
                            max_size = max(max_size, len(result))
                            cursor+=1

            if password_char!="\0" and (result!=old_result or cursor!=old_cursor):
                self.freeze()
                self.cursor.visible = False
                self.cursor.x -= old_cursor
                self.cursor.check()
                for i in range(max_size):
                    if i<len(result):
                        if password_char!="":
                            self.write(password_char)
                        else:
                            self.write(result[i])
                    else:
                        self.write("\0")
                self.cursor.x -= max_size
                self.cursor.x += cursor
                self.cursor.check()
                self.cursor.visible = is_visible
                old_cursor = deepcopy(cursor)
                old_result = deepcopy(result)
                self.unfreeze()

    def script(self):
        pass

    def mainloop(self):
        thread(self.script)(self)
        while self.run:
            self.update()
            self.draw()
        pg.quit()

if __name__=="__main__":
    root = TerminalWindow(50,40,BitmapFont("IBM_EGA_8x8.png",8,8),display_flags=pg.SCALED|pg.FULLSCREEN)

    root.writeln("Hello, World!\nПривет, мир!")
    root.write("\x1b[31m▓▒░\v\r")
    root.writeln("←↑→↓↔↕↨▀▄█▌▐■□▪▫▬▲►▼◄○●◘◙◦")
    root.write("0123456789ABC\tDEF\r")

    root.write(CharImage.get_bitmap_image(0,80,4,4))

    root.write("\v\x1b[h")

    root.writeln(CharImage.get_ansi_art_image("ansi_picture.txt"))

    def program(terminal):
        while True:
            terminal.set_fg_color(pg.Color("white"))
            terminal.set_bg_color(pg.Color("blue"))
            terminal.write(">> ")
            terminal.set_fg_color(pg.Color("white"))
            terminal.set_bg_color(pg.Color("black"))
            if terminal.input().lower()=="exit":
                terminal.run = False
    
    root.script = program
    root.mainloop()
