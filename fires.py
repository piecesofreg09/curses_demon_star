import basic_settings
import math

# fires

class fires:
    '''
    The class for the fires fired
    '''
    fire_attris = {'speed': 0.01}
    color_changable = False
    
    def __init__(self, stdscr, scrnresolution, color_changable):
        self.fires = []
        self.stdscr = stdscr
        self.scrnresolution = scrnresolution
        self.color_changable = color_changable
    
    def fire_once(self, y, x):
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, True)
        
        height = self.scrnresolution[0]
        
        fire_pos = [y - 3, x]
        self.draw_fire(fire_pos[0], fire_pos[1])
        self.fires.append(fire_pos)
        self.stdscr.addstr(height - 2, 0, "one fire at {}, {}".format(x, y))
        
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, False)
        
        
    def update_fires(self):
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, True)
        
        height = self.scrnresolution[0]
        speed = self.fire_attris['speed']
        to_eliminate = []
        for i in range(len(self.fires)):
            self.fires[i][0] -= speed
            posy = math.floor(self.fires[i][0])
            posx = math.floor(self.fires[i][1])
            if posy < 0:
                to_eliminate.append(i)
            else:
                self.draw_fire(posy, posx)
        fires_new = [self.fires[i] for i in range(len(self.fires)) if i not in to_eliminate]

        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, False)
        
        self.fires = fires_new
    
    def draw_fire(self, y, x):
        self.stdscr.addstr(y, x, '*')