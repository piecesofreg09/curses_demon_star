import numpy as np
import math


def collision(enemies_obj, fighter_obj, stats):
    check_ene_fire_group(enemies_obj, fighter_obj, stats)
    check_ene_fighter_group(enemies_obj, fighter_obj, stats)
    check_topedo_fighter_group(enemies_obj, fighter_obj, stats)
    
    

def check_ene_fire_group(enemies_obj, fighter_obj, stats):
    fires = fighter_obj.fires
    enemies = enemies_obj.enemies
    
    for ene_id, ene in enumerate(enemies):
        for fire_id, fire in enumerate(fires):
            if single_ene_fire(ene, fire):
                stats['score'] += 1
    
def single_ene_fire(ene, fire):
    
    ene_y = math.floor(ene.pos[0])
    ene_x = math.floor(ene.pos[1])
    
    fire_y = math.floor(fire.pos[0])
    fire_x = math.floor(fire.pos[1])
    
    
    if (fire_y - ene_y) <= (1 + 1e-2) and (fire_y - ene_y) >= (-1 - 1e-2):
        if (fire_x - ene_x) >= (-2 - 1e-2) and (fire_x - ene_x) <= (2 + 1e-2):
            ene.to_eliminate = True
            fire.to_eliminate = True
            fire.targeted = True
            return True

    return False
    
def check_ene_fighter_group(enemies_obj, fighter_obj, stats):
    enemies = enemies_obj.enemies
    fighter = fighter_obj
    
    for ene_id, ene in enumerate(enemies):
        if single_ene_fighter(ene, fighter):
            stats['lives'] -= 1
    
def single_ene_fighter(ene, fighter):
    ene_y = math.floor(ene.pos[0])
    ene_x = math.floor(ene.pos[1])
    
    fighter_y = math.floor(fighter.pos[0])
    fighter_x = math.floor(fighter.pos[1])
    
    
    if (fighter_y - ene_y) <= (4 + 1e-2) and (fighter_y - ene_y) >= (-2 - 1e-2):
        if (fighter_x - ene_x) >= (-4 - 1e-2) and (fighter_x - ene_x) <= (4 + 1e-2):
            ene.to_eliminate = True
            return True
    return False
    
    
def check_topedo_fighter_group(enemies_obj, fighter_obj, stats):
    topedoes = enemies_obj.topedoes
    fighter = fighter_obj
    
    for top_id, top in enumerate(topedoes):
        if single_topedo_fighter(top, fighter):
            stats['lives'] -= 1
    
def single_topedo_fighter(top, fighter):
    top_y = math.floor(top.pos[0])
    top_x = math.floor(top.pos[1])
    
    fighter_y = math.floor(fighter.pos[0])
    fighter_x = math.floor(fighter.pos[1])
    
    
    if (fighter_y - top_y) <= (2 + 1e-2) and (fighter_y - top_y) >= (-1 - 1e-2):
        if (fighter_x - top_x) >= (-2 - 1e-2) and (fighter_x - top_x) <= (2 + 1e-2):
            top.to_eliminate = True
            return True
    return False