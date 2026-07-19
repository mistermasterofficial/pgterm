import pygame as pg

if __name__=="__main__":
    pg.init()

    font = pg.font.Font(input("font filename: "), int(input("font height: ")))
    font_width = int(input("font width: "))

    w = int(input("bitmap width: "))
    h = int(input("bitmap height: "))

    bitmap = pg.Surface((w*font_width, h*font.get_height()), pg.SRCALPHA)
    
    for i in range(w*h):
        x = (i%w)*font_width
        y = (i//w)*font.get_height()

        try:
            char = font.render(chr(i), False, pg.Color(255,255,255,255))
            bitmap.blit(char, (x,y))
        except:
            continue
        
    pg.image.save(bitmap, input("dest filename: "))