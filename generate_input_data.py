import pickle
import pandas as pd
import numpy as np
import math, os

move_map = {'U': [-1, 0], 'D': [1, 0], 
    'L': [0, -1], 'R': [0, 1], 'N': [0, 0]}

def update_basic(reso, fighter_obj, enemies_obj, lives, lives_old, move, data, target):
    
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
    
    data.append(temp_topedoes + temp_enemies + [fighter_x, fighter_y] + move_two_digits)
    if lives_old > lives:
        target.append(0)
    else:
        target.append(1)
    
    
def write_basic(data, target):
    data_dir = os.path.join(os.curdir, 'Data', 'basic_data.pkl')
    with open(data_dir, 'wb') as out_file:
        ot = {'data': pd.DataFrame(data), 'target': pd.DataFrame(target)}
        pickle.dump(ot, out_file)
    
    pass

def update_basic_short(reso, fighter_obj, enemies_obj, lives, lives_old, move, data, target):
    
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
    temp_2[(wing_length - left_wing): (wing_length + 1)] = temp_topedoes[(fighter_x - left_wing):(fighter_x + 1)]
    temp_2[(wing_length + 1):(wing_length + right_wing)] = temp_topedoes[(fighter_x + 1):(fighter_x + right_wing)]
    
    
    
    data.append(temp + move_two_digits)
    if lives_old > lives:
        target.append(0)
    else:
        target.append(1)
    
    
def write_basic_short(data, target):
    data_dir = os.path.join(os.curdir, 'Data', 'basic_data_short.pkl')
    with open(data_dir, 'wb') as out_file:
        ot = {'data': pd.DataFrame(data), 'target': pd.DataFrame(target)}
        pickle.dump(ot, out_file)
    
    pass


def update_basic_pics(reso, fighter_obj, enemies_obj, lives, lives_old, move, data, target):
    
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
    
    temp_topedoes = [i - fighter_y for i in temp_topedoes]
    
    for i, enemy in enumerate(enemies):
        posy, posx = enemy.pos
        posy = math.floor(posy)
        posx = math.floor(posx)
        if posy <= fighter_y:
            temp_enemies[posx] = max(temp_enemies[posx], posy)
    
    temp_enemies = [i - fighter_y for i in temp_enemies]
    
    move_two_digits = move_map[move[0]]
    
    wing_length = 7
    left_bound = max(fighter_x - wing_length, 0)
    right_bound = min(fighter_x + wing_length, width)
    
    left_wing = fighter_x - left_bound
    right_wing = right_bound - fighter_x
    
    temp = [0 for i in range(2 * wing_length + 1)]
    temp[(wing_length - left_wing): (wing_length + 1)] = temp_topedoes[(fighter_x - left_wing):(fighter_x + 1)]
    temp[(wing_length + 1):(wing_length + right_wing)] = temp_topedoes[(fighter_x + 1):(fighter_x + right_wing)]
    
    
    
    data.append(temp + move_two_digits)
    if lives_old > lives:
        target.append(0)
    else:
        target.append(1)
    
    
def write_basic_pics(data, target):
    data_dir = os.path.join(os.curdir, 'Data', 'basic_data_short.pkl')
    with open(data_dir, 'wb') as out_file:
        ot = {'data': pd.DataFrame(data), 'target': pd.DataFrame(target)}
        pickle.dump(ot, out_file)
    
    pass

def generate_more():
    pass