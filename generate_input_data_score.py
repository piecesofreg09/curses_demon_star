import pickle
import pandas as pd
import numpy as np
import math, os
import logging
from collections import Counter
import joblib
import random

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

    def update_mother_pre(self, reso, fighter_obj, enemies_obj):
        self.update_d_pre += 1
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.update_funcs_pre[type_s](reso,
                    fighter_obj, enemies_obj)
        if self.update_d_pre % 5000 == 0:
            logger.info('%d pre records updated', self.update_d_pre)

    def update_mother_post(self, one_fire):
        self.update_d_post += 1
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.update_funcs_post[type_s](one_fire)
        
        if self.update_d_post % 5000 == 0:
            logger.info('%d post records updated', self.update_d_post)
        
    
    def write_mother(self):
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                self.write_funcs[type_s]()
        
        logger.info('%d pre - %d post - data writing into files', 
            self.update_d_pre, self.update_d_post)
    
    @classmethod
    def update_1_pre(self, reso, fighter_obj, enemies_obj):
        type_s = 'basic'
        
        fighter = fighter_obj
        fighter_y, fighter_x = fighter.pos
        
        temp_ene_fire = enemy_fire_1(reso, fighter_obj, enemies_obj)
        
        self.data[type_s].data.append(temp_ene_fire + [fighter_y])
        
        
        pass
    
    @classmethod
    def update_1_post(self, one_fire):
        type_s = 'basic'
        self.data[type_s].fire_target.append(one_fire)
        pass
    
    @classmethod
    def write_1(self):
        type_s = 'basic'
        
        #print(self.data[type_s].fire_target)
        
        self.data[type_s].target = [1 if i.targeted == True else 0 for i in self.data[type_s].fire_target]
        
        data_dir = os.path.join(os.curdir, 'Data', 'Score', 'data_basic.pkl')
        with open(data_dir, 'wb') as out_file:
            ot = {'data': pd.DataFrame(self.data[type_s].data), 'target': pd.DataFrame(self.data[type_s].target)}
            pickle.dump(ot, out_file)
        
        pass
    
    @classmethod
    def update_2_pre(self, reso, fighter_obj, enemies_obj):
        '''In this method, only the position above is saved
        '''
        type_s = 'short'
        
        height, width = reso
        enemies = enemies_obj.enemies
        fighter = fighter_obj
        fires = fighter_obj.fires
        
        wing_height = 20
        wing_size = 2
        ene_fire = [[0 for i in range(wing_height)] for i in range(2 * wing_size + 1)]
        
        fighter_y, fighter_x = fighter.pos
        
        for i, enemy in enumerate(enemies):
            posy, posx = enemy.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            if np.abs(posx - fighter_x) <= wing_size:
                if posy <= fighter_y and posy > fighter_y - wing_height:
                    ene_fire[posx - fighter_x + wing_size][fighter_y - posy] = 1
        
        for i, fire in enumerate(fires):
            posy, posx = fire.pos
            posy = math.floor(posy)
            posx = math.floor(posx)
            if np.abs(posx - fighter_x) <= wing_size:
                if posy <= fighter_y and posy > fighter_y - wing_height:
                    ene_fire[posx - fighter_x + wing_size][fighter_y - posy] = 2
        
        temp_ene_fire = pd.DataFrame(ene_fire)
        
        temp_ene_fire = temp_ene_fire.values.flatten().tolist()
        #print(temp_ene_fire)
        
        self.data[type_s].data.append(temp_ene_fire)
        pass
    
    @classmethod
    def update_2_post(self, one_fire):
        type_s = 'short'
        self.data[type_s].fire_target.append(one_fire)
        pass
    
    @classmethod
    def write_2(self):
        type_s = 'short'
        
        #print(self.data[type_s].fire_target)
        
        self.data[type_s].target = [1 if i.targeted == True else 0 for i in self.data[type_s].fire_target]
        
        data_dir = os.path.join(os.curdir, 'Data', 'Score', 'data_short.pkl')
        with open(data_dir, 'wb') as out_file:
            ot = {'data': pd.DataFrame(self.data[type_s].data), 'target': pd.DataFrame(self.data[type_s].target)}
            pickle.dump(ot, out_file)
        
        pass

    @classmethod
    def update_3_pre(self, reso, fighter_obj, enemies_obj):
        '''The column thing is bad
        '''
        
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
    def update_3_post(self, one_fire):
        type_s = 'pics'
        self.data[type_s].fire_target.append(one_fire)
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
    types = ['basic', 'short', 'pics']
    type_dict = {type_s:False for type_s in types}
    
    def __init__(self, options, using_st=True):
        self.predicter_funcs = {'basic': self.predict_1,
            'short': self.predict_2, 
            'pics': self.predict_3}
        # this sets which predicter to use
        self.using_st = using_st
        
        for type_s in self.types:
            if type_s in options:
                self.type_dict[type_s] = True
                logger.info('%s will be used to create predictions', type_s)
        pass
    
    def predict_m(self, reso, fighter_obj, enemies_obj):
        
        res = []
        for type_s in self.types:
            if self.type_dict[type_s] == True:
                temp = self.predicter_funcs[type_s](reso, fighter_obj, enemies_obj)
                res.extend(temp)
        print()
        print(res)
        #print(res)
        # the following step is trying to find out the most frequent elements, if
        # the frequencies are the same for some directions, a random
        # direction is then returned
        counting_res = Counter(res)
        most_freq = counting_res.most_common(1)[0][1]
        pot = []
        
        for dir, count in dict(counting_res).items():
            if count == most_freq:
                pot.append(dir)
        print(pot)
        
        return random.choice(pot)
        
    def predict_1(self, reso, fighter_obj, enemies_obj):
        
        predicter = joblib.load(os.path.join(os.curdir, 'Models', 
            'model_score_75_method_1.joblib'))
        
        fighter = fighter_obj
        fighter_y, fighter_x = fighter.pos
        
        temp_ene_fire = enemy_fire_1(reso, fighter_obj, enemies_obj)
        
        suggestion = predicter.predict([temp_ene_fire + [fighter_y]])
        return list(suggestion)
        
        pass
        
    def predict_2(self, reso, fighter_obj, enemies_obj):
        return None
        pass
        
    def predict_3(self, reso, fighter_obj, enemies_obj):
        return None
        pass
        
    
def enemy_fire_1(reso, fighter_obj, enemies_obj):
    height, width = reso
    enemies = enemies_obj.enemies
    fighter = fighter_obj
    fires = fighter_obj.fires
    
    wing_size = 2
    ene_fire = [[0 for i in range(height)] for i in range(2 * wing_size + 1)]
    
    fighter_y, fighter_x = fighter.pos
    
    for i, enemy in enumerate(enemies):
        posy, posx = enemy.pos
        posy = math.floor(posy)
        posx = math.floor(posx)
        if np.abs(posx - fighter_x) <= wing_size:
            ene_fire[posx - fighter_x + wing_size][posy] = 1
    
    for i, fire in enumerate(fires):
        posy, posx = fire.pos
        posy = math.floor(posy)
        posx = math.floor(posx)
        if np.abs(posx - fighter_x) <= wing_size:
            ene_fire[posx - fighter_x + wing_size][posy] = 2
    
    temp_ene_fire = pd.DataFrame(ene_fire)
    
    temp_ene_fire = temp_ene_fire.values.flatten().tolist()
    
    return temp_ene_fire
    
    pass
