import sys, os, curses, math, random, joblib, pickle, logging
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN, BUTTON_CTRL
import numpy as np
import pandas as pd

from pytablewriter import MarkdownTableWriter

import basic_settings
from Enemies import Enemies
from Fighter import Fighter
from collisions_update import collision
from generate_input_data_survive import SurvivalDataUpdaterWriter, SurvivalPredicter
from generate_input_data_score import ScoreDataUpdaterWriter, ScorePredicter


color_changable = True
# nf_global_survival_training means the fighter is firing or not
# nf = True means no fires
nf_global_survival_training = False
enemy_freq_sur_train = 8

# this bit sets on the score training or prediction of using #trained predicter from survival training or not
# if yon_sctraining_using_svt is set as True, during score training
# we will use the predicter generated from survival training
# if yon_sctraining_using_svt is set False, random movements will be used
yon_sctraining_using_svt = True

# firing frequency it means one fire out of 4 movements, random
fire_freq_during_score = 4
fire_freq_during_survival = 4

# default window size
default_win_size = [44, 80]

move_direction_maps = {'U': np.array([-1.0, 0.0]),
    'D': np.array([1.0, 0.0]),
    'L': np.array([0.0, -1.0]),
    'R': np.array([0.0, 1.0]),
    'N': np.array([0.0, 0.0])}

def logging_training_pre_post_results():
    '''
    Settings for the logging of the training results. 
    '''
    logger = logging.getLogger('training_results')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(os.path.join(os.curdir, 
        'Data', 'training_results.log'))
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \n %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    
def logging_training_no_interrupt():
    '''
    Settings for the logging of the training results. 
    '''
    logger = logging.getLogger('no_interrupt')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(os.path.join(os.curdir,
        'Data', 'no_interrupt.log'))
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \n %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

def init_screen(stdscr):
    stdscr.clear()
    stdscr.refresh()
    curses.initscr()
    basic_settings.set_color_pairs()
    stdscr.nodelay(1)
    height, width = stdscr.getmaxyx()
    reso = [height, width]
    
    height, width = default_win_size
    reso = default_win_size
    win = curses.newwin(default_win_size[0], default_win_size[1])
    win.nodelay(1)
    win.keypad(True)
    return [height, width, reso, win]

def init_game_stats(stdscr, reso, color_changable,
    cursor_y, cursor_x, starting_lives):
    
    stats = {'score': 0, 'lives': starting_lives}
    lives = stats['lives']
    lives_old = stats['lives']
    enemies_obj = Enemies(stdscr, reso, color_changable)
    fighter_obj = Fighter(stdscr, reso, color_changable, 
        cursor_y, cursor_x)
    
    return lives, lives_old, stats, enemies_obj, fighter_obj

def cursor_update(k, cursor_x, cursor_y, reso):
    if k == 'D':
        cursor_y = cursor_y + 1
    elif k == 'U':
        cursor_y = cursor_y - 1
    elif k == 'R':
        cursor_x = cursor_x + 1
    elif k == 'L':
        cursor_x = cursor_x - 1
    else:
        pass
    
    height, width = reso
    
    cursor_x = max(8, cursor_x)
    cursor_x = min(width - 8, cursor_x)

    cursor_y = max(10, cursor_y)
    cursor_y = min(height - 4, cursor_y)
    
    return cursor_x, cursor_y

def draw_game_over(stdscr, height):
    stdscr.clear()
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(20, 5, ' ***     *       *   *    *****   **  *     * ***** ***')
    stdscr.addstr(21, 5, '*       * *     * * * *   *      *  *  *   *  *     *  *')
    stdscr.addstr(22, 5, '*   **  * *     * * * *   *     *    * *   *  *     *  *')
    stdscr.addstr(23, 5, '*    * *****   *   *   *  ***** *    *  * *   ***** ***')
    stdscr.addstr(24, 5, ' *  *  *   *   *   *   *  *      *  *   * *   *     *  *')
    stdscr.addstr(25, 5, '  **  *     * *         * *****   **     *    ***** *   **')
    stdscr.attroff(curses.A_BOLD)
    statusbarstr = "Press 'q' to exit"
    stdscr.addstr(height - 1, 0, statusbarstr)

def render_status_bar(stdscr, statusbarstr, height, width):
    basic_settings.set_color_pair_with_gate(stdscr, 1, True, True)
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(height - 1, 0, statusbarstr)
    stdscr.addstr(height - 1, len(statusbarstr), 
        " " * (width - len(statusbarstr) - 1))
    stdscr.attroff(curses.A_BOLD)
    basic_settings.set_color_pair_with_gate(stdscr, 1, True, False)

def random_enemy_rx_ry(height):
    rx = (width - 20) / np.random.randint(10, 15) * \
        (ene_total_count % np.random.randint(5, 11) + 1) + 10 + \
        np.random.choice([-1, 1]) * np.random.randint(0, 3)
    ry = np.random.randint(5, np.floor(height / 2))
    return [rx, ry]

def fire_random_array(freq):
    freq = int(np.ceil(freq))
    if freq >= 1:
        x = [True] + [False for i in range(freq - 1)]
    else:
        x = [False]
    return random.choice(x)

def draw_menu_survival_data(stdscr1):
    
    # counting system
    k = 0
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0
    move_passed = 0
    
    # initialize screen
    height, width, reso, stdscr = init_screen(stdscr1)
    
    # initialize game stats
    starting_lives = 30000
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    # initialize data generator
    updater = SurvivalDataUpdaterWriter(['short', 'pics'])
    
    # move_sets generates a random series of random steps
    # paired with fire or not choices
    move_sets = []
    nf = nf_global_survival_training
    for i in range(200000):
        if nf == True:
            fire_or = fire_random_array(0)
        else:
            fire_or = fire_random_array(fire_freq_during_survival)
        move_sets.append([random.choice(['D', 'U', 'L', 'R', 'N']),
            fire_or])
    
    
    
    while (k != ord('q')) and (move_sets) and (stats['lives'] > 0):
        
        # Initialization
        stdscr.clear()
        
        # get the movements from the move_sets list
        move = move_sets.pop()
        move_passed += 1
        
        # update data pre movements
        updater.update_mother_pre(reso, fighter_obj, 
            enemies_obj, move)
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        cursor_x, cursor_y = cursor_update(move[0], cursor_x, cursor_y, reso)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        
        # if the movement includes firing or not
        if move[1]:
            fighter_obj.fire_once([cursor_y - 2, cursor_x])
        
        # create enemy
        ene_appear_count += 1
        if ene_appear_count % enemy_freq_sur_train == 1:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, 
            cursor_y, len(move_sets), stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        # update data post movements
        lives = stats['lives']
        updater.update_mother_post(lives, lives_old)
        lives_old = lives
        
        # Refresh the screen
        stdscr.refresh()
        curses.napms(1)

        # Wait for next input
        k = stdscr.getch()
    
    else:
        k = stdscr.getch()
        updater.write_mother()
        
        logger = logging.getLogger('training_results')
        ot_str = 'Before survival training: \n' + \
            "number of movements: {} | score : {}, life consumed: {} \n".format(
                move_passed, stats['score'], starting_lives - stats['lives'])
        logger.info(ot_str)
        
        while (k != ord('q') and k != ord('Q')):
            draw_game_over(stdscr, height)
            k = stdscr.getch()
            
def draw_menu_survival_data_no_interrupt(stdscr1, move_counts):
    # counting system
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0
    move_passed = 0
    
    # initialize screen
    height, width, reso, stdscr = init_screen(stdscr1)
    
    # initialize game stats
    starting_lives = 30000
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    # initialize data generator
    updater = SurvivalDataUpdaterWriter([])
    
    # move_sets generates a random series of random steps
    # paired with fire or not choices
    move_sets = []
    nf = nf_global_survival_training
    for i in range(move_counts):
        if nf == True:
            fire_or = fire_random_array(0)
        else:
            fire_or = fire_random_array(fire_freq_during_survival)
        move_sets.append([random.choice(['D', 'U', 'L', 'R', 'N']),
            fire_or])
    
    
    
    while (move_sets) and (stats['lives'] > 0):
        
        # Initialization
        stdscr.clear()
        
        # get the movements from the move_sets list
        move = move_sets.pop()
        move_passed += 1
        
        # update data pre movements
        updater.update_mother_pre(reso, fighter_obj, 
            enemies_obj, move)
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        cursor_x, cursor_y = cursor_update(move[0], cursor_x, cursor_y, reso)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        
        # if the movement includes firing or not
        if move[1]:
            fighter_obj.fire_once([cursor_y - 2, cursor_x])
        
        # create enemy
        ene_appear_count += 1
        if ene_appear_count % enemy_freq_sur_train == 1:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, 
            cursor_y, len(move_sets), stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        # update data post movements
        lives = stats['lives']
        updater.update_mother_post(lives, lives_old)
        lives_old = lives
        
        # Refresh the screen
        stdscr.refresh()
        curses.napms(1)

        
    
    else:
        
        logger = logging.getLogger('training_results')
        ot_str = 'Before survival training: \n' + \
            "number of movements: {} | score : {}, life consumed: {} \n".format(
                move_passed, stats['score'], starting_lives - stats['lives'])
        logger.info(ot_str)
        
        return [move_passed, stats['score'], starting_lives - stats['lives']]

def draw_menu_after_survival(stdscr1):
    k = 0
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0
    move_passed = 0

    # initialize screen
    height, width, reso, stdscr = init_screen(stdscr1)
    
    # initialize game stats
    starting_lives = 30000
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    # initializer predicter/recommender
    nf = nf_global_survival_training
    recommender = SurvivalPredicter(['pics'], nf)
    
    
    
    while (k != ord('q')) and (stats['lives'] > 0):
        # Initialization
        stdscr.clear()
        
        if nf == True:
            fire_or = fire_random_array(0)
        else:
            fire_or = fire_random_array(fire_freq_during_survival)
        
        
        # get a prediction of the directions from the trained model
        move = [recommender.predict_m(reso, fighter_obj, enemies_obj), fire_or]
        move_passed += 1
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        cursor_x, cursor_y = cursor_update(move[0], cursor_x, cursor_y, reso)
        stdscr.move(cursor_y, cursor_x)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        # if the movement includes firing or not
        if move[1]:
            fighter_obj.fire_once([cursor_y - 2, cursor_x])
        
        # create enemy
        ene_appear_count += 1
        if ene_appear_count % enemy_freq_sur_train == 1:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, cursor_y,
                move_passed, stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        
        # Refresh the screen
        stdscr.refresh()
        curses.napms(1)

        # Wait for next input
        k = stdscr.getch()
    
    else:
        k = stdscr.getch()
        
        logger = logging.getLogger('training_results')
        ot_str = 'After survival training using models of : ' + \
            str(recommender.type_dict) + '\n' + \
            "number of movements: {} | score : {}, life consumed: {} \n".format(
                move_passed, stats['score'], starting_lives - stats['lives'])
        logger.info(ot_str)
        
        while (k != ord('q') and k != ord('Q')):
            draw_game_over(stdscr, height)
            k = stdscr.getch()
    
def draw_menu_after_survival_no_interrupt(stdscr1, move_counts):
    # counting system
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0
    move_passed = 0

    # initialize screen
    height, width, reso, stdscr = init_screen(stdscr1)
    
    # initialize game stats
    starting_lives = 30000
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    # initializer predicter/recommender
    nf = nf_global_survival_training
    recommender = SurvivalPredicter(['pics'], nf)
    
    
    
    while (move_passed <= move_counts) and (stats['lives'] > 0):
        # Initialization
        stdscr.clear()
        
        if nf == True:
            fire_or = fire_random_array(0)
        else:
            fire_or = fire_random_array(fire_freq_during_survival)
        
        
        # get a prediction of the directions from the trained model
        move = [recommender.predict_m(reso, fighter_obj, enemies_obj), fire_or]
        move_passed += 1
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        cursor_x, cursor_y = cursor_update(move[0], cursor_x, cursor_y, reso)
        stdscr.move(cursor_y, cursor_x)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        # if the movement includes firing or not
        if move[1]:
            fighter_obj.fire_once([cursor_y - 2, cursor_x])
        
        # create enemy
        ene_appear_count += 1
        if ene_appear_count % enemy_freq_sur_train == 1:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, cursor_y,
                move_passed, stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        
        # Refresh the screen
        stdscr.refresh()
        curses.napms(1)

    
    else:
        
        logger = logging.getLogger('training_results')
        ot_str = 'After survival training using models of : ' + \
            str(recommender.type_dict) + '\n' + \
            "number of movements: {} | score : {}, life consumed: {} \n".format(
                move_passed, stats['score'], starting_lives - stats['lives'])
        logger.info(ot_str)
        
        return [move_passed, stats['score'], starting_lives - stats['lives']]

def draw_menu_score_data(stdscr1):
    k = 0
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0
    move_passed = 0
    fire_fired = 0

    # initialize screen
    height, width, reso, stdscr = init_screen(stdscr1)
    
    # initialize game stats
    starting_lives = 30000
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    # initializer predicter/recommender
    # the global_survival_training digit is used for the predicter
    # to select the correct prediction model
    nf = nf_global_survival_training
    recommender = SurvivalPredicter(['pics'], nf)
    
    score_updater = ScoreDataUpdaterWriter(['basic', 'short'])
    
    
    while (k != ord('q')) and (stats['lives'] > 0) and move_passed <= 300000:
        # Initialization
        stdscr.clear()
        
        fire_or = fire_random_array(fire_freq_during_score)
        
        if yon_sctraining_using_svt:
            move_dir = recommender.predict_m(reso, fighter_obj, enemies_obj)
        else:
            move_dir = random.choice(['D', 'U', 'L', 'R', 'N'])
        # get a prediction of the directions from the trained model
        move = [move_dir, fire_or]
        move_passed += 1
        
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        cursor_x, cursor_y = cursor_update(move[0], cursor_x, cursor_y, reso)
        stdscr.move(cursor_y, cursor_x)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        
        # create enemy
        ene_appear_count += 1
        if ene_appear_count % enemy_freq_sur_train == 0:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        # if the movement includes firing or not
        if move[1]:
            score_updater.update_mother_pre(reso, fighter_obj, 
            enemies_obj)
            one_fire = fighter_obj.fire_once([cursor_y - 2, cursor_x])
            #print(one_fire)
            fire_fired += 1
            score_updater.update_mother_post(one_fire)
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, cursor_y,
                move_passed, stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        
        # Refresh the screen
        stdscr.refresh()
        curses.napms(1)

        # Wait for next input
        k = stdscr.getch()
    
    else:
        k = stdscr.getch()
        
        score_updater.write_mother()
        
        logger = logging.getLogger('training_results')
        if_using_srv_training = ('Using survival training predicter: ' + 
            str(yon_sctraining_using_svt) +  '\nUsing random steps: ' + 
            str(not yon_sctraining_using_svt) + '\n')
        ot_str = ('Before score training, \n' + if_using_srv_training + 
            "number of movements: {}, number of fires: {} \n".format(
                move_passed, fire_fired) + 
            "score : {}, life consumed: {} \n".format(
                stats['score'], starting_lives - stats['lives']))
        logger.info(ot_str)
        
        while (k != ord('q') and k != ord('Q')):
            draw_game_over(stdscr, height)
            k = stdscr.getch()
    pass

def draw_menu_score_data_no_interrupt(stdscr1, move_counts):
    
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0
    move_passed = 0
    fire_fired = 0

    # initialize screen
    height, width, reso, stdscr = init_screen(stdscr1)
    
    # initialize game stats
    starting_lives = 30000
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    # initializer predicter/recommender
    # the global_survival_training digit is used for the predicter
    # to select the correct prediction model
    nf = nf_global_survival_training
    recommender = SurvivalPredicter(['pics'], nf)
    
    score_updater = ScoreDataUpdaterWriter([])
    
    
    while (stats['lives'] > 0) and (move_passed <= move_counts):
        # Initialization
        stdscr.clear()
        
        fire_or = fire_random_array(fire_freq_during_score)
        
        if yon_sctraining_using_svt:
            move_dir = recommender.predict_m(reso, fighter_obj, enemies_obj)
        else:
            move_dir = random.choice(['D', 'U', 'L', 'R', 'N'])
        # get a prediction of the directions from the trained model
        move = [move_dir, fire_or]
        move_passed += 1
        
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        cursor_x, cursor_y = cursor_update(move[0], cursor_x, cursor_y, reso)
        stdscr.move(cursor_y, cursor_x)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        
        # create enemy
        ene_appear_count += 1
        if ene_appear_count % enemy_freq_sur_train == 0:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        # if the movement includes firing or not
        if move[1]:
            score_updater.update_mother_pre(reso, fighter_obj, 
            enemies_obj)
            one_fire = fighter_obj.fire_once([cursor_y - 2, cursor_x])
            fire_fired += 1
            score_updater.update_mother_post(one_fire)
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, cursor_y,
                move_passed, stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        
        # Refresh the screen
        stdscr.refresh()
        
    else:
        
        
        score_updater.write_mother()
        
        logger = logging.getLogger('training_results')
        if_using_srv_training = ('Using survival training predicter: ' + 
            str(yon_sctraining_using_svt) +  '\nUsing random steps: ' + 
            str(not yon_sctraining_using_svt) + '\n')
        ot_str = ('Before score training, \n' + if_using_srv_training + 
            "number of movements: {}, number of fires: {} \n".format(
                move_passed, fire_fired) + 
            "score : {}, life consumed: {} \n".format(
                stats['score'], starting_lives - stats['lives']))
        logger.info(ot_str)
        
        return [move_passed, fire_fired, 
            stats['score'], starting_lives - stats['lives']]
        
    pass

def draw_menu_after_score(stdscr1):
    k = 0
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0
    move_passed = 0
    fire_fired = 0

    # initialize screen
    height, width, reso, stdscr = init_screen(stdscr1)
    
    # initialize game stats
    starting_lives = 30000
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    # initializer predicter/recommender
    # the global_survival_training digit is used for the predicter
    # to select the correct prediction model
    nf = nf_global_survival_training
    recommender = SurvivalPredicter(['pics'], nf)
    
    score_updater = ScoreDataUpdaterWriter([])
    score_recommender = ScorePredicter(['basic'])
    
    
    while (k != ord('q')) and (stats['lives'] > 0) and move_passed <= 30000:
        # Initialization
        stdscr.clear()
        
        # Generate direction
        if yon_sctraining_using_svt:
            move_dir = recommender.predict_m(reso, fighter_obj, enemies_obj)
        else:
            move_dir = random.choice(['D', 'U', 'L', 'R', 'N'])
        move_passed += 1
        
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        cursor_x, cursor_y = cursor_update(move_dir, cursor_x, cursor_y, reso)
        stdscr.move(cursor_y, cursor_x)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        
        # create enemy
        ene_appear_count += 1
        if ene_appear_count % enemy_freq_sur_train == 0:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        
        # predict based on score predictor
        fire_or = score_recommender.predict_m(reso, fighter_obj, enemies_obj)
        if fire_or:
            one_fire = fighter_obj.fire_once([cursor_y - 2, cursor_x])
            fire_fired += 1
        
        
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, cursor_y,
                move_passed, stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()
    
    else:
        k = stdscr.getch()
        
        logger = logging.getLogger('training_results')
        if_using_srv_training = ('Using survival training predicter: ' + 
            str(yon_sctraining_using_svt) +  '\nUsing random steps: ' + 
            str(not yon_sctraining_using_svt) + '\n')
        ot_str = ('After score training, \n' + if_using_srv_training + 
            "number of movements: {}, number of fires: {} \n".format(
                move_passed, fire_fired) + 
            "score : {}, life consumed: {} \n".format(
                stats['score'], starting_lives - stats['lives']))
        logger.info(ot_str)
        
        while (k != ord('q') and k != ord('Q')):
            draw_game_over(stdscr, height)
            k = stdscr.getch()
    pass
    
def draw_menu_after_score_no_interrupt(stdscr1, move_counts):
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0
    move_passed = 0
    fire_fired = 0

    # initialize screen
    height, width, reso, stdscr = init_screen(stdscr1)
    
    # initialize game stats
    starting_lives = 30000
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    # initializer predicter/recommender
    # the global_survival_training digit is used for the predicter
    # to select the correct prediction model
    nf = nf_global_survival_training
    recommender = SurvivalPredicter(['pics'], nf)
    
    score_updater = ScoreDataUpdaterWriter([])
    score_recommender = ScorePredicter(['basic'])
    
    while (stats['lives'] > 0) and (move_passed <= move_counts):
        # Initialization
        stdscr.clear()
        
        
        # Generate direction
        if yon_sctraining_using_svt:
            # get a prediction of the directions from the trained model
            move_dir = recommender.predict_m(reso, fighter_obj, enemies_obj)
        else:
            move_dir = random.choice(['D', 'U', 'L', 'R', 'N'])
        move_passed += 1
        
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        cursor_x, cursor_y = cursor_update(move_dir, cursor_x, cursor_y, reso)
        stdscr.move(cursor_y, cursor_x)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        
        # create enemy
        ene_appear_count += 1
        if ene_appear_count % enemy_freq_sur_train == 0:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        # predict based on score predictor
        fire_or = score_recommender.predict_m(reso, fighter_obj, enemies_obj)
        if fire_or:
            one_fire = fighter_obj.fire_once([cursor_y - 2, cursor_x])
            fire_fired += 1
            
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, cursor_y,
                move_passed, stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        
        # Refresh the screen
        stdscr.refresh()
        
    else:
        
        logger = logging.getLogger('training_results')
        if_using_srv_training = ('Using survival training predicter: ' + 
            str(yon_sctraining_using_svt) +  '\nUsing random steps: ' + 
            str(not yon_sctraining_using_svt) + '\n')
        ot_str = ('After score training, \n' + if_using_srv_training + 
            "number of movements: {}, number of fires: {} \n".format(
                move_passed, fire_fired) + 
            "score : {}, life consumed: {} \n".format(
                stats['score'], starting_lives - stats['lives']))
        logger.info(ot_str)
        
        return [move_passed, fire_fired, 
            stats['score'], starting_lives - stats['lives']]
        
    pass

def draw_menu(stdscr1):
    k = 0
    cursor_x = 40
    cursor_y = 40
    ene_total_count = 0
    ene_appear_count = 0

    height, width, reso, stdscr = init_screen(stdscr1)
    
    
    starting_lives = 30000
    
    lives, lives_old, stats, enemies_obj, fighter_obj = init_game_stats(
        stdscr, reso, color_changable, cursor_y, cursor_x, starting_lives)
    
    
    # move_sets generates a random series of random steps
    # paired with fire or  not choices
    
    move_passed = 0
    
    while (k != ord('q')) and (stats['lives'] > 0):
        
        # Initialization
        stdscr.clear()
        
        
        if k == KEY_DOWN:
            cursor_y = cursor_y + 1
            move_passed += 1
        elif k == KEY_UP:
            cursor_y = cursor_y - 1
            move_passed += 1
        elif k == KEY_RIGHT:
            cursor_x = cursor_x + 1
            move_passed += 1
        elif k == KEY_LEFT:
            cursor_x = cursor_x - 1
            move_passed += 1
        

        cursor_x = max(8, cursor_x)
        cursor_x = min(width - 8, cursor_x)

        cursor_y = max(10, cursor_y)
        cursor_y = min(height - 4, cursor_y)
        
        
        
        # update the cursor and the positions of the fighter
        # using the movement popped out the list
        
        stdscr.move(cursor_y, cursor_x)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        # if the movement includes firing or not
        # in the game mode, z is fire
        if k == 122:
            fighter_obj.fire_once([cursor_y - 2, cursor_x])
        
        # create enemy
        # in the game mode, x is create enemy
        ene_appear_count += 1
        #if k == 120:
        if ene_appear_count % 6 == 1:
            ene_total_count += 1
            ry = np.floor(height / 10)
            rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        # check collisions and then update the objects
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, 
            cursor_y, move_passed, stats['score'], stats['lives'])
        render_status_bar(stdscr, statusbarstr, height, width)
        
        
        # Refresh the screen
        stdscr.refresh()
        curses.napms(100)

        # Wait for next input
        k = stdscr.getch()
        #print(k)
    
    else:
        k = stdscr.getch()
        
        while (k != ord('q') and k != ord('Q')):
            draw_game_over(stdscr, height)
            k = stdscr.getch()
    pass
    
def survival_data():
    curses.wrapper(draw_menu_survival_data)

def survival_data_no_interrupt(repeat_times):
    move_counts = 12000
    data = [['Lives Consumed', 'Moves', 'Ratio']]
    for count in range(repeat_times):
        mp, sc, lil = curses.wrapper(
            draw_menu_survival_data_no_interrupt, move_counts)
        ratioo = float(lil) / float(mp)
        data.append([lil, mp, ratioo])
    data_np = pd.DataFrame(data)
    data_np_lack = pd.DataFrame(data[1:])
    data_np = data_np.append(data_np_lack.mean(axis=0), ignore_index=True)
    data_np = np.transpose(data_np)
    data_np_list = np.array(data_np).tolist()
    
    
    writer = MarkdownTableWriter()
    writer.table_name = "collecting data during survival training"
    writer.headers = [" "] + \
        [str(i + 1) for i in range(repeat_times)] + ["average"]
    writer.value_matrix = data_np_list
    table_output = writer.dumps()
    
    
    logger = logging.getLogger('no_interrupt')
    no_fire_stat = 'no_fires status: ' + \
        str(nf_global_survival_training) + '\n'
    enemy_freq_stat = 'enemy freq status: ' + \
        str(enemy_freq_sur_train) + '\n'
    ot_str = no_fire_stat + enemy_freq_stat + \
        'Before survival training: \n' + table_output
    logger.info(ot_str)
    
def game_after_survival_training():
    curses.wrapper(draw_menu_after_survival)
    
def game_after_survival_training_no_interrupt(repeat_times):
    move_counts = 12000
    data = [['Lives Consumed', 'Moves', 'Ratio']]
    for count in range(repeat_times):
        mp, sc, lil = curses.wrapper(
            draw_menu_after_survival_no_interrupt, move_counts)
        ratioo = float(lil) / float(mp)
        data.append([lil, mp, ratioo])
    data_np = pd.DataFrame(data)
    data_np_lack = pd.DataFrame(data[1:])
    data_np = data_np.append(data_np_lack.mean(axis=0), ignore_index=True)
    data_np = np.transpose(data_np)
    data_np_list = np.array(data_np).tolist()
    
    
    writer = MarkdownTableWriter()
    writer.table_name = "collecting data after survival training"
    writer.headers = [" "] + \
        [str(i + 1) for i in range(repeat_times)] + ["average"]
    writer.value_matrix = data_np_list
    table_output = writer.dumps()
    
    
    logger = logging.getLogger('no_interrupt')
    no_fire_stat = 'no_fires status: ' + \
        str(nf_global_survival_training) + '\n'
    enemy_freq_stat = 'enemy freq status: ' + \
        str(enemy_freq_sur_train) + '\n'
    ot_str = no_fire_stat + enemy_freq_stat + \
        'After survival training: \n' + table_output
    logger.info(ot_str)

def score_data():
    curses.wrapper(draw_menu_score_data)
    
def score_data_no_interrupt(repeat_times):
    
    move_counts = 12000
    data = [['Lives Consumed', 'Score', 'Fires', 'Moves',
        'Ratio(Lives / Mov)', 'Ratio(Score / Mov)', 'Ratio(Score / Fires)', 'Ratio(Score/F/M, %)']]
    for count in range(repeat_times):
        mp, frs, sc, lil = curses.wrapper(
            draw_menu_score_data_no_interrupt, move_counts)
        ratio_lm = float(lil) / float(mp)
        ratio_sm = float(sc) / float(mp)
        ratio_sf = float(sc) / float(frs)
        ratio_sfm = float(sc) / float(frs) / float(mp) * 100
        data.append([lil, sc, frs, mp,
            ratio_lm, ratio_sm, ratio_sf, ratio_sfm])
    data_np = pd.DataFrame(data)
    data_np_lack = pd.DataFrame(data[1:])
    data_np = data_np.append(data_np_lack.mean(axis=0), ignore_index=True)
    data_np = np.transpose(data_np)
    data_np_list = np.array(data_np).tolist()
    
    
    writer = MarkdownTableWriter()
    writer.table_name = "collecting data during score training"
    writer.headers = [" "] + \
        [str(i + 1) for i in range(repeat_times)] + ["average"]
    writer.value_matrix = data_np_list
    table_output = writer.dumps()
    
    
    logger = logging.getLogger('no_interrupt')
    enemy_freq_stat = 'enemy freq status: ' + \
        str(enemy_freq_sur_train) + '\n'
    survial_training = ('using survival training: ' +
        str(yon_sctraining_using_svt) + '\n')
    ot_str = survial_training + enemy_freq_stat + \
        'Before score training: \n' + table_output
    logger.info(ot_str)
    
def game_after_score_training():
    curses.wrapper(draw_menu_after_score)
    
def game_after_score_training_no_interrupt(repeat_times):
    
    move_counts = 120
    data = [['Lives Consumed', 'Score', 'Fires', 'Moves',
        'Ratio(Lives / Mov)', 'Ratio(Score / Mov)', 'Ratio(Score / Fires)', 'Ratio(Score/F/M, %)']]
    for count in range(repeat_times):
        mp, frs, sc, lil = curses.wrapper(
            draw_menu_after_score_no_interrupt, move_counts)
        ratio_lm = float(lil) / float(mp)
        ratio_sm = float(sc) / float(mp)
        ratio_sf = float(sc) / float(frs)
        ratio_sfm = float(sc) / float(frs) / float(mp) * 100
        data.append([lil, sc, frs, mp,
            ratio_lm, ratio_sm, ratio_sf, ratio_sfm])
    data_np = pd.DataFrame(data)
    data_np_lack = pd.DataFrame(data[1:])
    data_np = data_np.append(data_np_lack.mean(axis=0), ignore_index=True)
    data_np = np.transpose(data_np)
    data_np_list = np.array(data_np).tolist()
    
    
    writer = MarkdownTableWriter()
    writer.table_name = "collecting data after score training"
    writer.headers = [" "] + \
        [str(i + 1) for i in range(repeat_times)] + ["average"]
    writer.value_matrix = data_np_list
    table_output = writer.dumps()
    
    
    logger = logging.getLogger('no_interrupt')
    enemy_freq_stat = 'enemy freq status: ' + \
        str(enemy_freq_sur_train) + '\n'
    survial_training = ('using survival training: ' +
        str(yon_sctraining_using_svt) + '\n')
    ot_str = survial_training + enemy_freq_stat + \
        'After score training: \n' + table_output
    logger.info(ot_str)

def game():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    # set up logging system first
    logging_training_pre_post_results()
    logging_training_no_interrupt()
    
    '''
    the game can be entered into different mode
    1. game mode: only game with manual input
        ---: python script
        ---: python script g
    
    the following 4 modes works in the same manner, whether manually interrupted for data gathering, or automated
        ---: python script option (manually interrupted)
        ---: python script option 5 (automated)
    for example if option=sv_t
        ---: python script sv_t (manually interrupted)
        ---: python script sv_t 5 (automated)
    1. survival training: sv_t
    2. after survival training game: sv_g
    3. score training: sc_t
    4. after score training game: sc_g
    '''
    
    modes = ['sv_t', 'sv_g', 'sc_t', 'sc_g']
    funcs_name = ['interrupt', 'no_interrupt']
    funcs_interrupt = [survival_data, 
        game_after_survival_training, 
        score_data,
        game_after_score_training]
    funcs_no_interrupt = [survival_data_no_interrupt,
        game_after_survival_training_no_interrupt,
        score_data_no_interrupt,
        game_after_score_training_no_interrupt]
    
    funcs_int_dict = dict(zip(modes, funcs_interrupt))
    funcs_no_int_dict = dict(zip(modes, funcs_no_interrupt))
    funcs_grouped = dict(zip(funcs_name, [funcs_int_dict, funcs_no_int_dict]))
    
    
    if len(sys.argv) == 1:
        game()
    else:
        if sys.argv[1] == 'simple' or sys.argv[1] == 'g':
            game()
        elif sys.argv[1] in modes:
            if len(sys.argv) == 2:
                funcs_grouped['interrupt'][sys.argv[1]]()
            elif len(sys.argv) == 3:
                try:
                    repeat_times = int(sys.argv[2])
                except:
                    print('the repeat_times parameter is malformated' 
                        + ' a default value of 3 will be used')
                    repeat_times = 3
                funcs_grouped['no_interrupt'][sys.argv[1]](repeat_times)
                
    '''
    if len(sys.argv) == 1:
        game()
    else:
        if sys.argv[1] == 'sv_t':
            if len(sys.argv) == 2:
                survival_data()
            elif len(sys.argv) == 3:
                try:
                    repeat_times = int(sys.argv[2])
                except:
                    print('the repeat_times parameter is malformated' 
                        + ' a default value of 3 will be used')
                    repeat_times = 3
                survival_data_no_interrupt(repeat_times)
        elif sys.argv[1] == 'sv_g':
            if len(sys.argv) == 2:
                game_after_survival_training()
            elif len(sys.argv) == 3:
                try:
                    repeat_times = int(sys.argv[2])
                except:
                    print('the repeat_times parameter is malformated' 
                        + ' a default value of 3 will be used')
                    repeat_times = 3
                game_after_survival_training_no_interrupt(repeat_times)
            
        elif sys.argv[1] == 'sc_t':
            if len(sys.argv) == 2:
                score_data()
            elif len(sys.argv) == 3:
                try:
                    repeat_times = int(sys.argv[2])
                except:
                    print('the repeat_times parameter is malformated' 
                        + ' a default value of 3 will be used')
                    repeat_times = 3
                score_data_no_interrupt(repeat_times)
            
        elif sys.argv[1] == 'sc_g':
            if len(sys.argv) == 2:
                game_after_score_training()
            elif len(sys.argv) == 3:
                try:
                    repeat_times = int(sys.argv[2])
                except:
                    print('the repeat_times parameter is malformated' 
                        + ' a default value of 3 will be used')
                    repeat_times = 3
                game_after_score_training_no_interrupt(repeat_times)
            
        elif sys.argv[1] == 'simple' or sys.argv[1] == 'g':
            game()
    '''
    
    
    
    
    