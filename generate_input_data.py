import pickle
import pandas as pd
import numpy as np
import math

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
    
    fighter_x, fighter_y = fighter.pos
    move_two_digits = move_map[move[0]]
    
    data.append(temp_topedoes + temp_enemies + [fighter_x, fighter_y] + move_two_digits)
    if lives_old > lives:
        target.append(0)
    else:
        target.append(1)
    
    
def write_basic(data, target):
    data_dir = os.path.join(os.curdir, 'Data')
    with open(data_dir, 'rb') as out_file:
        ot = {'data': pd.DataFrame(data), 'target': pd.DataFrame(target)}
        pickle.dump(ot, input_file)
    
    pass

def generate_more():
    pass