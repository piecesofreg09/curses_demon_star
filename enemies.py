import basic_settings
import math

class enemies:
    '''
    The class for all the enemies appeared
    '''
    
    enemy_attris = {'speed': 0.015}
    color_changable = False
    
    def __init__(self, stdscr, scrnresolution, color_changable):
        self.enemies = []
        self.stdscr = stdscr
        self.scrnresolution = scrnresolution
        self.color_changable = color_changable
    
    def create_enemy(self, y, x):
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, True)

        fire_pos = [y, x]
        self.draw_enemy(fire_pos)
        self.enemies.append(fire_pos)
        
        self.display_enemies()
        
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, False)
        
    def update_enemies(self):
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, True)
        
        speed = self.enemy_attris['speed']
        height = self.scrnresolution[0]
        to_eliminate = []
        for i in range(len(self.enemies)):
            self.enemies[i][0] += speed
            posy = math.floor(self.enemies[i][0])
            posx = math.floor(self.enemies[i][1])
            if posy > height - 4 :
                to_eliminate.append(i)
            else:
                self.draw_enemy([posy, posx])
        enemies_new = [self.enemies[i] for i in range(len(self.enemies))
            if i not in to_eliminate]
        
        self.display_enemies()
        
        self.enemies = enemies_new
        
        basic_settings.set_color_pair_with_gate(self.stdscr, 1, self.color_changable, False)
    
    def update_topedo(self):
        
    
    def draw_enemy(self, pos):
        y, x = pos
        self.stdscr.addstr(y, x, '|   |')
        self.stdscr.addstr(y - 1, x, '|---|')
        self.stdscr.addstr(y + 1, x, '|---|')
    
    def draw_topedo(self, pos):
        y, x = pos
        self.stdscr.addstr(y, x, 'v')
    
    def display_enemies(self):
        '''Display only the first three enemies on console'''
        height = self.scrnresolution[0]
        
        to_display = self.enemies[:3]
        to_display_sep_str = ['[{}, {}] '.format(round(x), round(y)) for y, x in to_display]
        to_display_str = ''.join(to_display_sep_str)
        self.stdscr.addstr(height - 3, 0, 
            "{} enemy/enemies at {}".format(len(self.enemies), to_display_str))