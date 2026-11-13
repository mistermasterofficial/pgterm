import pygame as pg
import numpy as np
from terminal import Terminal
from ansi_helper import *

def from_color_to_char(color: pg.Color, char_gradient="█▓▒░ "):
    lightcolors = Terminal.lightcolors
    colors = Terminal.colors
    all_colors = [pg.Color(c) for c in lightcolors+colors]

    ind = 0
    second_ind = 0
    min_r = float("inf")

    for c in range(len(all_colors)):
        r = (all_colors[c].r-color.r)**2+(all_colors[c].g-color.g)**2+(all_colors[c].b-color.b)**2
        r = np.sqrt(r)

        if min_r>r:
            min_r = r
            ind = c

    min_r = float("inf")

    for c in range(len(all_colors)):
        if c==ind:
            continue

        r = (all_colors[c].r-color.r)**2+(all_colors[c].g-color.g)**2+(all_colors[c].b-color.b)**2
        r = np.sqrt(r)

        if min_r>r:
            min_r = r
            second_ind = c

    max_r = np.sqrt((255**2)*3)

    r = (all_colors[ind].r-all_colors[second_ind].r)**2+(all_colors[ind].g-all_colors[second_ind].g)**2+(all_colors[ind].b-all_colors[second_ind].b)**2
    r = np.sqrt(r)

    char_ind = min(int(r/max_r*len(char_gradient)),len(char_gradient)-1)

    fg_color_char = "39"
    bg_color_char = "49"

    for c in range(len(colors)):
        if pg.Color(all_colors[ind])==pg.Color(colors[c]):
            bg_color_char = f"4{c}"
        if pg.Color(all_colors[second_ind])==pg.Color(colors[c]):
            fg_color_char = f"3{c}"

    for c in range(len(lightcolors)):
        if pg.Color(all_colors[ind])==pg.Color(lightcolors[c]):
            bg_color_char = f"10{c}"
        if pg.Color(all_colors[second_ind])==pg.Color(lightcolors[c]):
            fg_color_char = f"9{c}"

    return f"\x1b[{fg_color_char};{bg_color_char}m"+char_gradient[char_ind]

if __name__=="__main__":
    pg.init()

    source_img = pg.image.load(input("source image path: "))
    color_array = pg.surfarray.array3d(source_img)

    result_art = ""

    for i in range(source_img.get_height()):
        for j in range(source_img.get_width()):
            result_art += from_color_to_char(pg.Color(color_array[j][i]))
        result_art += "\n"

    with open(input("dest filename: "),"w",encoding="utf-8") as f:
        f.write(result_art)