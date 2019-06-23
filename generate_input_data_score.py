import pickle
import pandas as pd
import numpy as np
import math, os
import logging

move_map = {'U': [-1, 0], 'D': [1, 0], 
    'L': [0, -1], 'R': [0, 1], 'N': [0, 0]}

# logging comes from https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('data_generation_score_training.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \n %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

class DataPack:
    def __init__(self, type_s):
        self.type_s = type_s
        self.data = []
        self.target = []

class ScoreDataUpdaterWriter:
    '''
    This is the class of data updater and writer
    Different types of data can be generated and written to system based
        on the choices provided with options
    '''
    
    # preset types are these three types
    types = ['basic', 'short', 'pics']
    type_dict = {type_s:False for type_s in types}
    data = {type_s:None for type_s in types}
    
    
    def __init__(self, options):
        '''
        Initiate the data updater and writer with the three options:
        'basic', 'short', 'pics'
        '''
        self.update_funcs_pre = {'basic': self.update_basic_pre,
            'short': self.update_basic_short_pre, 
            'pics': self.update_basic_pics_pre}
        self.update_funcs_post = {'basic': self.update_basic_post,
            'short': self.update_basic_short_post, 
            'pics': self.update_basic_pics_post}
        self.write_funcs = {'basic': self.write_basic,
            'short': self.write_basic_short, 'pics': self.write_basic_pics}
        self.update_d_pre = 0
        self.update_d_post = 0
        
        for type_s in self.types:
            if type_s in options:
                self.type_dict[type_s] = True
                self.data[type_s] = DataPack(type_s)
                logger.info('%s will be written in the file', type_s)
        pass

    def update_mother_pre(self, reso, fighter_obj, enemies_obj, move):
        self.update_d_pre += 1
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.update_funcs_pre[type_s](reso,
                    fighter_obj, enemies_obj, move)
        if self.update_d_pre % 20 == 0:
            logger.info('%d pre records updated', self.update_d_pre)

    def update_mother_post(self, lives, lives_old):
        self.update_d_post += 1
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.update_funcs_post[type_s](lives, lives_old)
        
        if self.update_d_post % 20 == 0:
            logger.info('%d post records updated', self.update_d_post)
        
    
    def write_mother(self):
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.write_funcs[type_s]()
        
        logger.info('Writing data into files')
    
    @classmethod
    def update_basic_pre(self, reso, fighter_obj, enemies_obj, move):
        type_s = 'basic'
        height, width = reso
        topedoes = enemies_obj.topedoes
        enemies = enemies_obj.enemies
        fighter = fighter_obj
        
        temp_topedoes = [0 for i in range(width)]
        temp_enemies = [0 for i in range(width)]
        
        for i, topedo in enumerate(topedoes):
            posy, posx = topedo.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            temp_topedoes[posx] = max(temp_topedoes[posx], posy)
            
        for i, enemy in enumerate(enemies):
            posy, posx = enemy.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            temp_enemies[posx] = max(temp_enemies[posx], posy)
        
        fighter_y, fighter_x = fighter.pos
        move_two_digits = move_map[move[0]]
        
        self.data[type_s].data.append(temp_topedoes + temp_enemies + [fighter_x, fighter_y] + move_two_digits)
        
    @classmethod
    def update_basic_post(self, lives, lives_old):
        type_s = 'basic'
        if lives_old > lives:
            self.data[type_s].target.append(0)
        else:
            self.data[type_s].target.append(1)
    
    @classmethod
    def write_basic(self):
        type_s = 'basic'
        data_dir = os.path.join(os.curdir, 'Data', 'basic_data.pkl')
        with open(data_dir, 'wb') as out_file:
            ot = {'data': pd.DataFrame(self.data[type_s].data), 'target': pd.DataFrame(self.data[type_s].target)}
            pickle.dump(ot, out_file)
        
        pass
    
    
    @classmethod
    def update_basic_short_pre(self, reso, fighter_obj, enemies_obj, move):
        
        type_s = 'short'
        
        height, width = reso
        topedoes = enemies_obj.topedoes
        enemies = enemies_obj.enemies
        fighter = fighter_obj
        
        temp_topedoes = [0 for i in range(width)]
        temp_enemies = [0 for i in range(width)]
        
        fighter_y, fighter_x = fighter.pos
        
        for i, topedo in enumerate(topedoes):
            posy, posx = topedo.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            
            if posy <= fighter_y:
                temp_topedoes[posx] = max(temp_topedoes[posx], posy)
        
        temp_topedoes = [i - fighter_y for i in temp_topedoes]
        
        for i, enemy in enumerate(enemies):
            posy, posx = enemy.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            if posy <= fighter_y:
                temp_enemies[posx] = max(temp_enemies[posx], posy)
        
        temp_enemies = [i - fighter_y for i in temp_enemies]
        
        move_two_digits = move_map[move[0]]
        
        wing_length = 4
        left_bound = max(fighter_x - wing_length, 0)
        right_bound = min(fighter_x + wing_length, width)
        
        left_wing = fighter_x - left_bound
        right_wing = right_bound - fighter_x
        
        temp_1 = [0 for i in range(2 * wing_length + 1)]
        temp_1[(wing_length - left_wing): (wing_length + 1)] = temp_topedoes[(fighter_x - left_wing):(fighter_x + 1)]
        temp_1[(wing_length + 1):(wing_length + right_wing)] = temp_topedoes[(fighter_x + 1):(fighter_x + right_wing)]
        
        temp_2 = [0 for i in range(2 * wing_length + 1)]
        temp_2[(wing_length - left_wing): (wing_length + 1)] = temp_enemies[(fighter_x - left_wing):(fighter_x + 1)]
        temp_2[(wing_length + 1):(wing_length + right_wing)] = temp_enemies[(fighter_x + 1):(fighter_x + right_wing)]
        
        temp = temp_1 + temp_2
        
        self.data[type_s].data.append(temp + move_two_digits)
        
    
    @classmethod
    def update_basic_short_post(self, lives, lives_old):
        type_s = 'short'
        if lives_old > lives:
            self.data[type_s].target.append(0)
        else:
            self.data[type_s].target.append(1)
    
    @classmethod
    def write_basic_short(self):
        type_s = 'short'
        data_dir = os.path.join(os.curdir, 'Data', 'basic_data_short.pkl')
        with open(data_dir, 'wb') as out_file:
            ot = {'data': pd.DataFrame(self.data[type_s].data), 'target': pd.DataFrame(self.data[type_s].target)}
            pickle.dump(ot, out_file)
        
        pass

    @classmethod
    def update_basic_pics_pre(self, reso, fighter_obj, enemies_obj, move):
        
        type_s = 'pics'
        
        # window size is the window to look above
        # height should be small than 10
        
        window_size = [10, 14]
        window_height, window_width = window_size
        
        height, width = reso
        topedoes = enemies_obj.topedoes
        enemies = enemies_obj.enemies
        fighter = fighter_obj
        
        temp_topedoes = [0 for i in range(width)]
        temp_enemies = [0 for i in range(width)]
        
        fighter_y, fighter_x = fighter.pos
        
        for i, topedo in enumerate(topedoes):
            posy, posx = topedo.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            
            if posy <= fighter_y:
                temp_topedoes[posx] = max(temp_topedoes[posx], posy)
        
        temp_topedoes = [min((fighter_y - i), window_height) for i in temp_topedoes]
        
        for i, enemy in enumerate(enemies):
            posy, posx = enemy.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            if posy <= fighter_y:
                temp_enemies[posx] = max(temp_enemies[posx], posy)
        
        temp_enemies = [min((fighter_y - i), window_height) for i in temp_enemies]
        
        move_two_digits = move_map[move[0]]
        
        
        
        wing_length = 5
        left_bound = max(fighter_x - wing_length, 0)
        right_bound = min(fighter_x + wing_length, width)
        
        left_wing = fighter_x - left_bound
        right_wing = right_bound - fighter_x
        
        temp_1 = [0 for i in range(2 * wing_length + 1)]
        temp_1[(wing_length - left_wing): (wing_length + 1)] = temp_topedoes[(fighter_x - left_wing):(fighter_x + 1)]
        temp_1[(wing_length + 1):(wing_length + right_wing)] = temp_topedoes[(fighter_x + 1):(fighter_x + right_wing)]
        
        temp_2 = [0 for i in range(2 * wing_length + 1)]
        temp_2[(wing_length - left_wing): (wing_length + 1)] = temp_enemies[(fighter_x - left_wing):(fighter_x + 1)]
        temp_2[(wing_length + 1):(wing_length + right_wing)] = temp_enemies[(fighter_x + 1):(fighter_x + right_wing)]
        
        temp = temp_1 + temp_2
        
        
        self.data[type_s].data.append(temp + move_two_digits)
        
    
    @classmethod
    def update_basic_pics_post(self, lives, lives_old):
        type_s = 'pics'
        if lives_old > lives:
            self.data[type_s].target.append(0)
        else:
            self.data[type_s].target.append(1)
    
    @classmethod
    def write_basic_pics(self):
        type_s = 'pics'
        data_dir = os.path.join(os.curdir, 'Data', 'basic_data_pics.pkl')
        with open(data_dir, 'wb') as out_file:
            ot = {'data': pd.DataFrame(self.data[type_s].data), 'target': pd.DataFrame(self.data[type_s].target)}
            pickle.dump(ot, out_file)
        
        pass

    def generate_more():
        pass
        
        
        
class ScorePredicter:
    pass
    