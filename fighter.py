import basic_settings
import math

class fighter:
    
    fighter_attris = {'speed': 1}
    color_changable = False
    
    def __init__(self, stdscr, scrnresolution, color_changable, y, x):
        self.pos = [y, x]
        self.stdscr = stdscr
        self.scrnresolution = scrnresolution
        self.color_changable = color_changable
        self.draw_fighter()
        self.display_fighter()
        
    def move_fighter(self, y, x):
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, True)
        
        self.pos = [y, x]
        self.draw_fighter()
        self.display_fighter()
        
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, False)
        
    def draw_fighter(self):
        y, x = self.pos
        
        self.stdscr.addstr(y - 2, x, '=')
        self.stdscr.addstr(y - 1, x - 1, '===')
        self.stdscr.addstr(y, x - 2, '=====')
        
        '''
        self.stdscr.addch(y - 2, x, '■')
        for i in range(3):
            self.stdscr.addch(y - 1, x - i, '■')
        for i in range(5):
            self.stdscr.addch(y, x - i, '■')
        '''
    
    def display_fighter(self):
        height = self.scrnresolution[0]
        
        self.stdscr.addstr(height - 4, 0, 
            "Fighter at [{}, {}]".format(round(self.pos[1]), round(self.pos[0])))
        
        
        
        