from copy import deepcopy
import numpy as np
import pygame as pg

class UIEvent:
    CHANGE_CONTAINER = pg.event.custom_type()
    STARTUPDATE = pg.event.custom_type()
    ENDUPDATE = pg.event.custom_type()
    SELECT = pg.event.custom_type()
    UNSELECT = pg.event.custom_type()
    FOCUS = pg.event.custom_type()
    UNFOCUS = pg.event.custom_type()

class ContainerGroup:
    def __init__(self, containers, current_container):
        self.containers = containers
        self.current_container = current_container

        self.stack = []
    
    def update(self, terminal, events):
        self.containers[self.current_container].update(terminal, events)
    
    def next_container(self, new_name):
        self.stack.append(self.current_container)
        self.current_container = new_name
        pg.event.post(pg.Event(UIEvent.CHANGE_CONTAINER))
    
    def undo(self):
        self.current_container = self.stack.pop()
        pg.event.post(pg.Event(UIEvent.CHANGE_CONTAINER))

class Container:
    def __init__(self):
        self.elements = []
        self.selectable_elements = []
        self.selected_element = None
        self.is_focus = False
    
    def update(self, terminal, events):
        for e in events:
            if e.type==UIEvent.CHANGE_CONTAINER:
                self.selected_element = None
                self.is_focus = False
            if e.type==UIEvent.FOCUS:
                self.is_focus = True
            if e.type==UIEvent.UNFOCUS:
                self.is_focus = False
            if e.type==pg.KEYDOWN and e.key==pg.K_TAB and pg.key.get_mods() & (pg.KMOD_LSHIFT|pg.KMOD_RSHIFT) and not self.is_focus and self.selected_element is not None:
                pg.event.post(pg.Event(UIEvent.UNSELECT, element=self.selected_element))
                self.selected_element = self.selectable_elements[(self.selectable_elements.index(self.selected_element)-1)%len(self.selectable_elements)]
                pg.event.post(pg.Event(UIEvent.SELECT, element=self.selected_element))
            if e.type==pg.KEYDOWN and e.key==pg.K_TAB and not pg.key.get_mods() & (pg.KMOD_LSHIFT|pg.KMOD_RSHIFT) and not self.is_focus:
                pg.event.post(pg.Event(UIEvent.UNSELECT, element=self.selected_element))
                if self.selected_element is None and len(self.selectable_elements)>0:
                    self.selected_element = self.selectable_elements[-1]
                self.selected_element = self.selectable_elements[(self.selectable_elements.index(self.selected_element)+1)%len(self.selectable_elements)]
                pg.event.post(pg.Event(UIEvent.SELECT, element=self.selected_element))
            if e.type==pg.KEYDOWN and e.key==pg.K_RETURN and not self.is_focus and self.selected_element is None:
                pg.event.post(pg.Event(UIEvent.ENDUPDATE))
        
        for e in self.elements:
            e.update(terminal, events)

class Element:
    def __init__(self, root, x, y, width, height):
        self.x, self.y = x, y
        self.text = np.full((width, height), "\0")
        self.fgcolor = np.full((width, height, 3), 255)
        self.bgcolor = np.full((width, height, 3), 0)

        self.root = root
        self.root.elements.append(self)

        self.is_selected = False
    
    def __del__(self):
        self.root.elements.remove(self)
        if self in self.root.selectable_elements:
            self.root.selectable_elements.remove(self)
        if self is self.root.selected_element:
            self.root.selected_element = None
        pg.event.post(pg.Event(UIEvent.UNFOCUS))
    
    def update(self, terminal, events):
        source_cursor = deepcopy(terminal.cursor)
        for x in range(self.text.shape[0]):
            for y in range(self.text.shape[1]):
                if self.text[x, y]!="\0":
                    terminal.cursor.x = self.x+x
                    terminal.cursor.y = self.y+y
                    terminal.cursor.fgcolor = self.fgcolor[x, y]
                    terminal.cursor.bgcolor = self.bgcolor[x, y]
                    if not terminal.cursor.check():
                        terminal.write(self.text[x, y])
        terminal.cursor = source_cursor

class Frame(Element):
    def __init__(self, root, x, y, width, height, color=[[255,255,255],[0,0,0]],
            top="\0",
            left="\0",
            right="\0",
            bottom="\0",
            topleft="\0",
            topright="\0",
            bottomleft="\0",
            bottomright="\0",
            sides=None):
        super().__init__(root, x, y, width, height)

        self.top = [top]+color
        self.left = [left]+color
        self.right = [right]+color
        self.bottom = [bottom]+color
        self.topleft = [topleft]+color
        self.topright = [topright]+color
        self.bottomleft = [bottomleft]+color
        self.bottomright = [bottomright]+color

        self.sides = [self.top,self.left,self.right,self.bottom,self.topleft,self.topright,self.bottomleft,self.bottomright]

        if sides is not None:
            for s in range(len(sides)):
                self.sides[s] = sides[s]

    def update(self, terminal, events):
        orig_text = deepcopy(self.text)
        orig_fgcolor = deepcopy(self.fgcolor)
        orig_bgcolor = deepcopy(self.bgcolor)

        self.text[0,0], self.fgcolor[0,0], self.bgcolor[0,0] = self.topleft[0], np.array(self.topleft[1]), np.array(self.topleft[2])
        self.text[-1,0], self.fgcolor[-1,0], self.bgcolor[-1,0] = self.topright[0], np.array(self.topright[1]), np.array(self.topright[2])
        self.text[0,-1], self.fgcolor[0,-1], self.bgcolor[0,-1] = self.bottomleft[0], np.array(self.bottomleft[1]), np.array(self.bottomleft[2])
        self.text[-1,-1], self.fgcolor[-1,-1], self.bgcolor[-1,-1] = self.bottomright[0], np.array(self.bottomright[1]), np.array(self.bottomright[2])

        self.text[1:-1,0], self.fgcolor[1:-1,0], self.bgcolor[1:-1,0] = self.top[0], np.array(self.top[1]), np.array(self.top[2])
        self.text[1:-1,-1], self.fgcolor[1:-1,-1], self.bgcolor[1:-1,-1] = self.bottom[0], np.array(self.bottom[1]), np.array(self.bottom[2])
        self.text[0,1:-1], self.fgcolor[0,1:-1], self.bgcolor[0,1:-1] = self.left[0], np.array(self.left[1]), np.array(self.left[2])
        self.text[-1,1:-1], self.fgcolor[-1,1:-1], self.bgcolor[-1,1:-1] = self.right[0], np.array(self.right[1]), np.array(self.right[2])

        super().update(terminal, events)

        self.text = orig_text
        self.fgcolor = orig_fgcolor
        self.bgcolor = orig_bgcolor

class ThinFrame(Frame):
    def __init__(self, root, x, y, width, height, color=[[255, 255, 255], [0, 0, 0]]):
        super().__init__(root, x, y, width, height, color=color, 
            top="─", 
            left="│", 
            right="│", 
            bottom="─", 
            topleft="┌", 
            topright="┐", 
            bottomleft="└", 
            bottomright="┘"
        )

class BoldFrame(Frame):
    def __init__(self, root, x, y, width, height, color=[[255, 255, 255], [0, 0, 0]]):
        super().__init__(root, x, y, width, height, color=color, 
            top="═", 
            left="║", 
            right="║",
            bottom="═", 
            topleft="╔", 
            topright="╗", 
            bottomleft="╚", 
            bottomright="╝"
        )