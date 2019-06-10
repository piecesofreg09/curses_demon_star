import basic_settings
from basic_settings import set_color_decor
import math
import random

class Enemy:
    '''
    The class of an individual enemy
    with pos and other attributes, separated
    '''
    
    total_count = 0
    
    def __init__(self, stdscr, pos, reso, topedo_freq=5, speed=1.0):
        self.stdscr = stdscr
        self.reso = reso
        self.pos = pos
        self.topedo_freq = topedo_freq
        self.speed = speed
        self.count = random.randint(0, round(self.topedo_freq / 2))
        
        Enemy.total_count += 1
        
        # this to_eliminate is used during updating of enemies
        self.to_eliminate = False
    
    def draw_enemy(self):
        y, x = self.pos
        y = math.floor(y)
        x = math.floor(x)
        self.stdscr.addstr(y, x, '|   |')
        self.stdscr.addstr(y - 1, x, '|---|')
        self.stdscr.addstr(y + 1, x, '|---|')
        
    def update_pos_one_step(self, topedoes):
        self.pos[0] += self.speed
        self.count += 1
        if self.count == self.topedo_freq:
            self.count = 0
            self.emit_topedo(topedoes)
        
        # if the enemy has run out of the screen area,
        # eliminate it
        height = self.reso[0]
        if self.pos[0] > (height - 4):
            self.to_eliminate = True
            
    def emit_topedo(self, topedoes):
        # emit a topedo at the position of the enemy
        topedo_pos = [self.pos[0] + 2, self.pos[1] + 2]
        topedo_emitted = Topedo(self.stdscr, topedo_pos, self.reso)
        topedoes.append(topedo_emitted)
        
    
class Topedo:
    '''
    The class of an individual topedo
    '''
    
    def __init__(self, stdscr, pos, reso, speed=2.5):
        self.stdscr = stdscr
        self.pos = pos
        self.topedo_speed = speed
        self.reso = reso
        # this to_eliminate is used during updating of topedoes
        self.to_eliminate = False
    
    def draw_topedo(self):
        y, x = self.pos
        y = math.floor(y)
        x = math.floor(x)
        self.stdscr.addstr(y, x, 'v')
    
    def update_pos_one_step(self):
        self.pos[0] += self.topedo_speed
        
        # if the topedo has run out of the screen area,
        # eliminate it
        height = self.reso[0]
        if self.pos[0] > (height - 4):
            self.to_eliminate = True

class Enemies:
    '''
    The class for all the enemies appeared
    '''
    
    color_changable = False
    
    def __init__(self, stdscr, reso, color_changable):
        self.enemies = []
        self.topedoes = []
        self.stdscr = stdscr
        self.reso = reso
        self.color_changable = color_changable
    
    @set_color_decor(6)
    def create_one_enemy(self, pos):
        height = self.reso[0]
        self.stdscr.addstr(height - 1, 0, ' one enemy created')
        one_enemy = Enemy(self.stdscr, pos, self.reso)
        one_enemy.draw_enemy()
        self.enemies.append(one_enemy)
        
        self.display_enemies()
        
    @set_color_decor(6)
    def update_enemies(self):
        
        # update the position of each enemy/enemies
        # update the counter of each enemy
        for i, ene in enumerate(self.enemies):
            ene.update_pos_one_step(self.topedoes)
            if not ene.to_eliminate:
                ene.draw_enemy()
                
        enemies_new = [ene for ene in self.enemies
            if not ene.to_eliminate]
        
        self.display_enemies()
        
        self.enemies = enemies_new
        
    
    @set_color_decor(1)
    def update_topedoes(self):
        to_eliminate = []
        
        for i, topedo in enumerate(self.topedoes):
            topedo.update_pos_one_step()
            if not topedo.to_eliminate:
                topedo.draw_topedo()
        
        topedoes_new = [topedo for topedo in self.topedoes
            if not topedo.to_eliminate]
        
        self.topedoes = topedoes_new
        
    
    def display_enemies(self):
        '''Display only the first three enemies on console'''
        height = self.reso[0]
        
        to_display = self.enemies[:5]
        to_display_sep_str = ['[{}, {}] '.format(round(ene.pos[1]), round(ene.pos[0])) for ene in to_display]
        to_display_str = ''.join(to_display_sep_str)
        self.stdscr.addstr(height - 3, 0, 
            "{} enemy/enemies at {}".format(len(self.enemies), to_display_str))