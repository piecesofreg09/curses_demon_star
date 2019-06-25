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

class ScoreDataPack:
    def __init__(self, type_s):
        self.type_s = type_s
        self.data = []
        self.target = []
        self.fire_target = []

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
        
        Warning:
        **** currently only 'pics' mode is implemented ****
        '''
        self.update_funcs_pre = {'basic': self.update_1_pre,
            'short': self.update_2_pre, 
            'pics': self.update_3_pre}
        self.update_funcs_post = {'basic': self.update_1_post,
            'short': self.update_2_post, 
            'pics': self.update_3_post}
        self.write_funcs = {'basic': self.write_1,
            'short': self.write_2, 'pics': self.write_3}
        self.update_d_pre = 0
        self.update_d_post = 0
        
        for type_s in self.types:
            if type_s in options:
                self.type_dict[type_s] = True
                self.data[type_s] = ScoreDataPack(type_s)
                logger.info('%s will be written in the datasets', type_s)
        pass

    def update_mother_pre(self, reso, fighter_obj, enemies_obj, one_fire):
        self.update_d_pre += 1
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.update_funcs_pre[type_s](reso,
                    fighter_obj, enemies_obj, one_fire)
        if self.update_d_pre % 2000 == 0:
            logger.info('%d pre records updated', self.update_d_pre)

    def update_mother_post(self, lives, lives_old):
        self.update_d_post += 1
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.update_funcs_post[type_s](lives, lives_old)
        
        if self.update_d_post % 2000 == 0:
            logger.info('%d post records updated', self.update_d_post)
        
    
    def write_mother(self):
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.write_funcs[type_s]()
        
        logger.info('Writing data into files')
    
    @classmethod
    def update_1_pre(self, reso, fighter_obj, enemies_obj, one_fire):
        pass
        
    @classmethod
    def update_1_post(self, lives, lives_old):
        pass
    
    @classmethod
    def write_1(self):
        pass
    
    @classmethod
    def update_2_pre(self, reso, fighter_obj, enemies_obj, one_fire):
        pass
    
    @classmethod
    def update_2_post(self, lives, lives_old):
        pass
    
    @classmethod
    def write_2(self):
        pass

    @classmethod
    def update_3_pre(self, reso, fighter_obj, enemies_obj, one_fire):
        
        type_s = 'pics'
        
        
        height, width = reso
        enemies = enemies_obj.enemies
        fighter = fighter_obj
        
        # the number of enemies in one column is maximized to be 3
        enemy_max_per_col = 2
        temp_enemies = [[[None for i in range(enemy_max_per_col)], 0] for i in range(width)]
        
        fighter_y, fighter_x = fighter.pos
        
        for i, enemy in enumerate(enemies):
            posy, posx = enemy.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            if posy <= fighter_y and temp_enemies[posx][1] < enemy_max_per_col:
                idx = temp_enemies[posx][1]
                temp_enemies[posx][0][idx] = fighter_y - posy
                temp_enemies[posx][1] += 1
        
        temp_enemies = [i[0] for i in temp_enemies]
        
        temp_enemies = pd.DataFrame(temp_enemies)
        temp_enemies.fillna(200, inplace=True)
        temp = temp_enemies.values.flatten()
        temp = temp.tolist()
        #print(temp)
        
        self.data[type_s].data.append(temp + fighter.pos)
        self.data[type_s].fire_target.append(one_fire)
    
    @classmethod
    def update_3_post(self, lives, lives_old):
        pass
    
    @classmethod
    def write_3(self):
        
        type_s = 'pics'
        
        #print(self.data[type_s].fire_target)
        
        self.data[type_s].target = [1 if i.targeted == True else 0 for i in self.data[type_s].fire_target]
        
        
        data_dir = os.path.join(os.curdir, 'Data', 'Score', 'data_pics.pkl')
        with open(data_dir, 'wb') as out_file:
            ot = {'data': pd.DataFrame(self.data[type_s].data), 'target': pd.DataFrame(self.data[type_s].target)}
            pickle.dump(ot, out_file)
        
        pass

    def generate_more():
        pass
        
        
        
class ScorePredicter:
    pass
    