import sys, os, curses, math, random, joblib
#from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN, BUTTON_CTRL
import numpy as np


import basic_settings
from Enemies import Enemies
from Fighter import Fighter
from collisions_update import collision
from generate_input_data_survive import SurvivalDataUpdaterWriter, SurvivalPredicter
from generate_input_data_score import ScoreDataUpdaterWriter, ScorePredicter

color_changable = True

move_direction_maps = {'U': np.array([-1.0, 0.0]),
    'D': np.array([1.0, 0.0]),
    'L': np.array([0.0, -1.0]),
    'R': np.array([0.0, 1.0]),
    'N': np.array([0.0, 0.0])}

def init_screen(stdscr):
    stdscr.clear()
    stdscr.refresh()
    curses.initscr()
    basic_settings.set_color_pairs()
    stdscr.nodelay(1)

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

def draw_game_over(stdscr):
    stdscr.addstr(20, 5, ' ***     *       *   *    *****   **  *     * ***** ***')
    stdscr.addstr(21, 5, '*       * *     * * * *   *      *  *  *   *  *     *  *')
    stdscr.addstr(22, 5, '*   **  * *     * * * *   *     *    * *   *  *     *  *')
    stdscr.addstr(23, 5, '*    * *****   *   *   *  ***** *    *  * *   ***** ***')
    stdscr.addstr(24, 5, ' *  *  *   *   *   *   *  *      *  *   * *   *     *  *')
    stdscr.addstr(25, 5, '  **  *     * *         * *****   **     *    ***** *   **')

def draw_menu_survival_data(stdscr):
    k = 0
    cursor_x = 40
    cursor_y = 40
    

    init_screen(stdscr)
    height, width = stdscr.getmaxyx()
    reso = [height, width]

    stats = {'score': 0, 'lives': 30000}
    lives = stats['lives']
    lives_old = stats['lives']
    enemies_obj = Enemies(stdscr, reso, color_changable)
    fighter_obj = Fighter(stdscr, reso, color_changable, cursor_y, cursor_x)
    
    updater = SurvivalDataUpdaterWriter(['short', 'pics'])
    
    ene_total_count = 0
    ene_appear_count = 0
    

    # move_sets generates a random series of random steps
    # paired with fire or  not choices
        
    for i in range(0):
        move_sets.append([random.choice(['D', 'D', 'R', 
            'R', 'R', 'L', 'D', 'D', 'N', 'N', 'R', 'L',
            'L', 'U', 'U']), random.choice([True, False, False, False])])
    
    for i in range(0):
        move_sets.append([random.choice(['L', 'R', 'R', 
            'L', 'L', 'U', 'U', 'R', 'U', 'D', 'N', 
            'D']), random.choice([True, False, False, False])])
        
    for i in range(600000):
        move_sets.append([random.choice(['D', 'U', 'L', 'R', 'N']),
            random.choice([True, False, False, False])])

    while (k != ord('q')) and (move_sets) and (stats['lives'] > 0):
        
        # Initialization
        stdscr.clear()
        
        # get the movements from the move_sets list
        move = move_sets.pop()
        
        updater.update_mother_pre(reso, fighter_obj, 
            enemies_obj, move)
        
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
        if ene_appear_count % 2 == 1:
            ene_total_count += 1
            ry = np.floor(height / 10)
            '''
            rx = (width - 20) / np.random.randint(10, 15) * \
                (ene_total_count % np.random.randint(5, 11) + 1) + 10 + \
                np.random.choice([-1, 1]) * np.random.randint(0, 3)
            '''
            #ry = np.random.randint(5, np.floor(height / 2))
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
                len(move_sets), stats['score'], stats['lives'])
        basic_settings.set_color_pair_with_gate(stdscr, 1, True, True)
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(height - 1, 0, statusbarstr)
        stdscr.addstr(height - 1, len(statusbarstr), 
            " " * (width - len(statusbarstr) - 1))
        basic_settings.set_color_pair_with_gate(stdscr, 1, True, False)
        stdscr.attroff(curses.A_BOLD)
        
        
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
        
        while (k != ord('q') and k != ord('Q')):
            stdscr.clear()
            stdscr.attron(curses.A_BOLD)
            draw_game_over(stdscr)
            stdscr.attroff(curses.A_BOLD)
            
            statusbarstr = "Press 'q' to exit"
            stdscr.addstr(height-1, 0, statusbarstr)
            
            k = stdscr.getch()
            

def draw_menu_after_survival(stdscr):
    k = 0
    cursor_x = 40
    cursor_y = 40
    

    init_screen(stdscr)
    height, width = stdscr.getmaxyx()
    reso = [height, width]

    stats = {'score': 0, 'lives': 30000}
    enemies_obj = Enemies(stdscr, reso, color_changable)
    fighter_obj = Fighter(stdscr, reso, color_changable, cursor_y, cursor_x)
    
    recommender = joblib.load('model_svc_survive.joblib')
    
    ene_total_count = 0
    ene_appear_count = 0
    
    while (k != ord('q')) and (stats['lives'] > 0):
        # Initialization
        stdscr.clear()
        
        # get the movements from the move_sets list
        for move in :
            input_dim = []
            recommender()
        move = move_sets.pop()
        
        
        
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
        if ene_appear_count % 2 == 1:
            ene_total_count += 1
            ry = np.floor(height / 10)
            '''
            rx = (width - 20) / np.random.randint(10, 15) * \
                (ene_total_count % np.random.randint(5, 11) + 1) + 10 + \
                np.random.choice([-1, 1]) * np.random.randint(0, 3)
            '''
            #ry = np.random.randint(5, np.floor(height / 2))
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
                len(move_sets), stats['score'], stats['lives'])
        basic_settings.set_color_pair_with_gate(stdscr, 1, True, True)
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(height - 1, 0, statusbarstr)
        stdscr.addstr(height - 1, len(statusbarstr), 
            " " * (width - len(statusbarstr) - 1))
        basic_settings.set_color_pair_with_gate(stdscr, 1, True, False)
        stdscr.attroff(curses.A_BOLD)
        
        
        # Refresh the screen
        stdscr.refresh()
        curses.napms(1)

        # Wait for next input
        k = stdscr.getch()
    
    else:
        k = stdscr.getch()
        updater.write_mother()
        
        while (k != ord('q') and k != ord('Q')):
            stdscr.clear()
            stdscr.attron(curses.A_BOLD)
            draw_game_over(stdscr)
            stdscr.attroff(curses.A_BOLD)
            
            statusbarstr = "Press 'q' to exit"
            stdscr.addstr(height-1, 0, statusbarstr)
            
            k = stdscr.getch()
    
    

def draw_menu_score_data(stdscr):
    pass

def draw_menu_after_score(stdscr):
    pass

def draw_menu(stdscr):
    pass
    
def survival_data():
    curses.wrapper(draw_menu_survival_data)

def game_after_survival_training():
    curses.wrapper(draw_menu_after_survival)

def score_data():
    curses.wrapper(draw_menu_score_data)
    
def game_after_score_training():
    curses.wrapper(draw_menu_after_score)

def game():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        game()
    else:
        if sys.argv[1] == 'sv_t':
            survival_data()
        elif sys.argv[1] == 'sv_g':
            game_after_survival_training()
        elif sys.argv[1] == 'sc_t':
            score_data()
        elif sys.argv[1] == 'sc_g':
            game_after_score_training()
        elif sys.argv[1] == 'simple':
            game()
    
    
    
    
    
    