import basic_settings
from basic_settings import set_color_decor
import math

class Fire:
    '''
    The class of an individual fire
    the constructor has three inputs, stdscr, pos, reso, which applies to Topedo and Enemy too
    '''
    def __init__(self, stdscr, pos, reso, speed=2.5):
        self.stdscr = stdscr
        self.reso = reso
        self.pos = pos
        self.speed = speed
        
        # this to_eliminate is used during updating of fires
        self.to_eliminate = False
    
    def draw_fire(self):
        y, x = self.pos
        y = math.floor(y)
        x = math.floor(x)
        self.stdscr.addstr(y, x, '^')
        
        
    def update_pos_one_step(self):
        self.pos[0] -= self.speed
        
        # if the fire has run out of the screen area,
        # eliminate it
        height = self.reso[0]
        if self.pos[0] < 0:
            self.to_eliminate = True


class Fighter:
    
    fighter_attris = {'speed': 1}
    color_changable = True
    
    def __init__(self, stdscr, reso, color_changable, y, x):
        self.pos = [y, x]
        self.stdscr = stdscr
        # combine the fires file and fighter file together
        self.fires = []
        self.reso = reso
        self.color_changable = color_changable
        self.draw_fighter()
        self.display_fighter()
        
    def move_fighter(self, y, x):
        
        self.pos = [y, x]
        
        self.draw_fighter()
        self.display_fighter()
        
    @set_color_decor(1)
    def draw_fighter(self):
        y, x = self.pos
        
        self.stdscr.addstr(y - 2, x - 2, '=====')
        self.stdscr.addstr(y - 1, x - 2, '=====')
        self.stdscr.addstr(y, x - 2, '=====')
    
    @set_color_decor(6)
    def fire_once(self, pos):
        height = self.reso[0]
        one_fire = Fire(self.stdscr, [pos[0] - 1, pos[1]], self.reso)
        one_fire.draw_fire()
        self.fires.append(one_fire)
    
    @set_color_decor(6)
    def update_fires(self):
        for i, fire in enumerate(self.fires):
            fire.update_pos_one_step()
            if not fire.to_eliminate:
                fire.draw_fire()
                
        fires_new = [fire for fire in self.fires if not fire.to_eliminate]
        
        self.fires = fires_new
    
    def display_fighter(self):
        height = self.reso[0]
        
        self.stdscr.addstr(height - 4, 0, 
            "Fighter at [{}, {}]".format(round(self.pos[1]), round(self.pos[0])))
        
        
        