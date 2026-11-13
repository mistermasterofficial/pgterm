from terminal import *

if __name__=="__main__":
    root = TerminalWindow(50,40,default_font,display_flags=pg.SCALED|pg.FULLSCREEN)

    def program():
        root.writeln("Hello, World!\nПривет, мир!")
        root.write("\x1b[31m▓▒░\v\r\t")
        # root.writeln("←↑→↓↔↕↨▀▄█▌▐■□▪▫▬▲►▼◄○●◘◙◦")
        # root.write("0123456789ABC\tDEF\r")
    
        # root.write(CharImage.get_bitmap_image(0,80,4,4))
    
        # root.write("\v\x1b[h")

        # for i in range(8):
        #     root.write(f"\x1b[3{i}m█")
        # for i in range(8):
        #     root.write(f"\x1b[9{i}m█")
        # root.waitkey()

        root.radiobuttons_input(["start","credits","Lorem ipsum dolor adsfjkhajsdhfgsadfkhsdgfkahjsdgfskdhfjgaksdhjfgskdfhj","exit"])

        while True:
            root.set_fg_color(pg.Color("white"))
            root.set_bg_color(pg.Color("blue"))
            root.write(">> ")
            root.set_fg_color(pg.Color("white"))
            root.set_bg_color(pg.Color("black"))
            if root.input(placeholder="hello",password_char="*").lower()=="exit":
                root.run = False
    
    root.script = program
    root.mainloop()
