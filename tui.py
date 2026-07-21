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
    
    def update(self, terminal):
        self.containers[self.current_container].update(terminal)
    
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
        self.selected_element = None
        self.is_focus = False
    
    def update(self, terminal):
        for e in self.terminal.events:
            if e.type==UIEvent.CHANGE_CONTAINER:
                self.selected_element = None
                self.is_focus = False
            if e.type==UIEvent.FOCUS:
                self.is_focus = True
            if e.type==UIEvent.UNFOCUS:
                self.is_focus = False
            if e.type==pg.KEYDOWN and e.key==pg.K_TAB and pg.key.get_mods() & (pg.KMOD_LSHIFT|pg.KMOD_RSHIFT) and not self.is_focus and self.selected_element is not None:
                pg.event.post(pg.Event(UIEvent.UNSELECT, element=self.selected_element))
                self.selected_element = self.elements[(self.elements.index(self.selected_element)-1)%len(self.selected_element)]
                pg.event.post(pg.Event(UIEvent.SELECT, element=self.selected_element))
            if e.type==pg.KEYDOWN and e.key==pg.K_TAB and not self.is_focus:
                pg.event.post(pg.Event(UIEvent.UNSELECT, element=self.selected_element))
                if self.selected_element is None:
                    self.selected_element = self.elements[-1]
                self.selected_element = self.elements[(self.elements.index(self.selected_element)+1)%len(self.selected_element)]
                pg.event.post(pg.Event(UIEvent.SELECT, element=self.selected_element))
            if e.type==pg.KEYDOWN and e.key==pg.K_RETURN and not self.is_focus and self.selected_element is None:
                pg.event.post(pg.Event(UIEvent.ENDUPDATE))
        
        for e in self.elements:
            e.update(terminal)

class Element:
    def __init__(self, root, x, y, width, height):
        self.x, self.y = x, y
        self.text = np.full((width, height), "\0")
        self.fgcolor = np.full((width, height, 3), 255)
        self.bgcolor = np.full((width, height, 3), 0)

        self.root = root
        self.root.elements.append(self)
    
    def update(self, terminal):
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