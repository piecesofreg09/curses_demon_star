import sys, os, curses, math, random
#from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN, BUTTON_CTRL
import numpy as np


import basic_settings, generate_input_data
from Enemies import Enemies
from Fighter import Fighter
from collisions_update import collision

color_changable = True
data_basic = []
target_basic = []

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
    
    cursor_x = max(2, cursor_x)
    cursor_x = min(width - 2, cursor_x)

    cursor_y = max(4, cursor_y)
    cursor_y = min(height - 4, cursor_y)
    
    return cursor_x, cursor_y

def draw_menu(stdscr):
    k = 0
    cursor_x = 40
    cursor_y = 40
    

    init_screen(stdscr)
    height, width = stdscr.getmaxyx()
    reso = [height, width]

    stats = {'score': 0, 'lives': 3000}
    lives = stats['lives']
    lives_old = stats['lives']
    enemies_obj = Enemies(stdscr, reso, color_changable)
    fighter_obj = Fighter(stdscr, reso, color_changable, cursor_y, cursor_x)
    
    ene_total_count = 0
    ene_appear_count = 0
    

    # move_sets generates a random series of random steps
    # paired with fire or  not choices
    
    move_sets = [['U', True], ['L', False], ['L', False], ['D', False],
        ['U', True], ['R', False], ['L', False], ['L', False],
        ['U', True], ['N', False], ['N', False], ['L', False],
        ['U', True], ['R', False], ['L', False], ['L', False],
        ['R', True], ['R', False], ['L', False], ['D', False],
        ['U', True], ['U', False], ['L', False], ['L', False],
        ['N', True], ['N', False], ['L', False], ['R', False],
        ['D', True], ['U', False], ['L', False], ['L', False],
        ['U', True], ['L', False], ['L', False], ['L', False]]
        
    for i in range(0):
        move_sets.append([random.choice(['D', 'D', 'R', 
            'R', 'R', 'L', 'D', 'D', 'N', 'N', 'R', 'L',
            'L', 'U', 'U']), random.choice([True, False, False, False])])
    
    for i in range(0):
        move_sets.append([random.choice(['L', 'R', 'R', 
            'L', 'L', 'U', 'U', 'R', 'U', 'D', 'N', 
            'D']), random.choice([True, False, False, False])])
        
    for i in range(200000):
        move_sets.append([random.choice(['D', 'U', 'L', 'R', 'N']),
            random.choice([True, False, False, False])])

    while (k != ord('q')) and (move_sets) and (stats['lives'] > 0):
        
        # Initialization
        stdscr.clear()
        
        move = move_sets.pop()
        
        cursor_x, cursor_y = cursor_update(move[0], cursor_x, cursor_y, reso)

        statusbarstr = "Press 'q' to exit " + \
            "| {}, {}, {} | score : {}, life left: {}".format(cursor_x, cursor_y,
                len(move_sets), stats['score'], stats['lives'])

        start_y = int((height // 2) - 2)

        stdscr.move(cursor_y, cursor_x)
        
        fighter_obj.move_fighter(cursor_y, cursor_x)
        
        # if the movement includes firing or not
        if move[1]:
            fighter_obj.fire_once([cursor_y - 2, cursor_x])
        
        ene_appear_count += 1
        if ene_appear_count % 10 == 1:
            
            ene_total_count += 1
            
            ry = np.floor(height / 10)
            rx = (width - 2) / 8 * (ene_total_count % 7 + 1)
            
            #ry = np.random.randint(5, np.floor(height / 2))
            #rx = np.random.randint(3, width - 3)
            pos = [ry, rx]
            enemies_obj.create_one_enemy(pos)
        
        collision(enemies_obj, fighter_obj, stats)
        fighter_obj.update_fires()
        
        enemies_obj.update_enemies()
        enemies_obj.update_topedoes()
        
        # Render status bar
        basic_settings.set_color_pair_with_gate(stdscr, 1, True, True)
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), 
            " " * (width - len(statusbarstr) - 1))
        basic_settings.set_color_pair_with_gate(stdscr, 1, True, False)
        stdscr.attroff(curses.A_BOLD)
        
        lives = stats['lives']
        
        generate_input_data.update_basic(reso, fighter_obj, enemies_obj, lives, lives_old, move, data_basic, target_basic)
        
        lives_old = lives
        
        # Refresh the screen
        stdscr.refresh()
        curses.napms(5)

        # Wait for next input
        k = stdscr.getch()
    
    else:
        k = stdscr.getch()
        generate_input_data.write_basic(data_basic, target_basic)
        while (k != ord('q') and k != ord('Q')):
            stdscr.clear()
            stdscr.attron(curses.A_BOLD)
            stdscr.addstr(20, 5, ' ***     *       *   *    *****   **  *     * ***** ***')
            stdscr.addstr(21, 5, '*       * *     * * * *   *      *  *  *   *  *     *  *')
            stdscr.addstr(22, 5, '*   **  * *     * * * *   *     *    * *   *  *     *  *')
            stdscr.addstr(23, 5, '*    * *****   *   *   *  ***** *    *  * *   ***** ***')
            stdscr.addstr(24, 5, ' *  *  *   *   *   *   *  *      *  *   * *   *     *  *')
            stdscr.addstr(25, 5, '  **  *     * *         * *****   **     *    ***** *   **')
            stdscr.attroff(curses.A_BOLD)
            k = stdscr.getch()
            
    
def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
