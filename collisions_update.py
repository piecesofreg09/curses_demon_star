import numpy as np
import math


def collision(enemies_obj, fires_obj, fighter_obj):
    check_ene_fire_group(enemies_obj, fires_obj)
    check_ene_fighter_group()


def check_ene_fire_group(enemies_obj, fires_obj):
    fires = fires_obj.fires
    enemies = enemies_obj.enemies
    
    for ene_id, ene in enumerate(enemies):
        ene_posy = math.floor(ene[0])
        ene_posx = math.floor(ene[1])
        
        for fire_id, fire in enumerate(fires):
            fire_posy = math.floor(fire[0])
            fire_posx = math.floor(fire[1])
    
def single_ene_fire(ene, fire):
    
    
def check_ene_fighter_group(enemies_obj, fighter_obj):
    enemies = enemies_obj.enemies
    fighter = fighter_obj.pos