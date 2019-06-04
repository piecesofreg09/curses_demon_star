import sys,os
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN, BUTTON_CTRL
import numpy as np
import math

import basic_settings
from fires import fires
from enemies import enemies
from fighter import fighter

color_changable = False
blocks_example = '■■■■■■■██████'
fire_attris = {'speed': 0.01}
enemy_attris = {'speed': 0.02}
move_direction_maps = {'U': np.array([-1.0, 0.0]),
    'D': np.array([1.0, 0.0]),
    'L': np.array([0.0, -1.0]),
    'R': np.array([0.0, 1.0])}

def init_screen(stdscr):
    stdscr.clear()
    stdscr.refresh()
    curses.initscr()
    basic_settings.set_color_pairs()
    stdscr.nodelay(1)



def draw_menu(stdscr):
    k = 0
    cursor_x = 40
    cursor_y = 40

    init_screen(stdscr)
    height, width = stdscr.getmaxyx()
    scrnresolution = [height, width]

    # the list of fires contains the positions of the fires
    #fires = []
    # the list of enemies contains the positions of the centers
    # of the enemies
    #enemies = []
    fires_obj = fires(stdscr, scrnresolution, color_changable)
    enemies_obj = enemies(stdscr, scrnresolution, color_changable)
    fighter_obj = fighter(stdscr, scrnresolution, color_changable, cursor_y, cursor_x)



    # move_sets generates a random series of random steps
    # paired with fire or  not choices
    move_sets = [['U', True], ['L', False], ['L', False], ['D', False],
        ['U', True], ['R', False], ['L', False], ['L', False],
        ['U', True], ['R', False], ['R', False], ['L', False],
        ['U', True], ['D', False], ['D', False], ['R', False],
        ['D', True], ['D', False], ['L', False], ['L', False],
        ['U', True], ['L', False], ['L', False], ['R', False]]

    while (k != ord('q')):

        # Initialization
        stdscr.clear()
        

        # get the positions of the key, then restrict it to be within the screen area
        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        cursor_x = max(0, cursor_x)
        cursor_x = min(width-1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height-1, cursor_y)


        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y )

        start_y = int((height // 2) - 2)



        # Render status bar
        basic_settings.set_color_pair_with_gate(stdscr, 1, True, True)
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        basic_settings.set_color_pair_with_gate(stdscr, 1, True, False)
        stdscr.attroff(curses.A_BOLD)




        # move cursor, move fighter
        stdscr.move(cursor_y, cursor_x)
        #moveFighter(stdscr, cursor_y, cursor_x)
        fighter_obj.move_fighter(cursor_y, cursor_x)
        # update the list of fired bullets
        #fires = updateFire(stdscr, fires, scrnresolution, enemies)
        fires_obj.update_fires()
        
        #enemies = updateEnemies(stdscr, fires, scrnresolution, enemies)
        enemies_obj.update_enemies()
        # initiate a new bullets
        if k == 122:
            #fires = fire(stdscr, cursor_y, cursor_x, fires, start_y, scrnresolution)
            fires_obj.fire_once(cursor_y, cursor_x)
        
        if k == 120:
            #enemies = createEnemy(stdscr, 20, 30, enemies, scrnresolution)
            ry = np.random.randint(5, np.floor(height / 2))
            rx = np.random.randint(3, width - 3)
            #print([ry, rx])
            enemies_obj.create_enemy(ry, rx)
        
        # Refresh the screen
        stdscr.refresh()


        # Wait for next input
        k = stdscr.getch()

def moveFighter(stdscr, y, x):

    basic_settings.set_color_pair_with_gate(stdscr, 1, color_changable, True)


    stdscr.addstr(y - 2, x, '■')
    stdscr.addstr(y - 1, x - 2, '■■■')
    stdscr.addstr(y, x - 4, '■■■■■')

    basic_settings.set_color_pair_with_gate(stdscr, 1, color_changable, False)

def fire(stdscr, y, x, fires, start_y, scrnresolution):

    basic_settings.set_color_pair_with_gate(stdscr, 1, color_changable, True)

    height = scrnresolution[0]
    fire_pos = [y - 3, x]
    stdscr.addstr(fire_pos[0], fire_pos[1], '■')
    fires.append(fire_pos)

    stdscr.addstr(height - 2, 0, "one fire at {}, {}".format(x, y))

    basic_settings.set_color_pair_with_gate(stdscr, 1, color_changable, False)
    return fires

def createEnemy(stdscr, y, x, enemies, scrnresolution):
    basic_settings.set_color_pair_with_gate(stdscr, 1, color_changable, True)

    height = scrnresolution[0]
    fire_pos = [y, x]
    stdscr.addstr(y, x, '■■■')
    stdscr.addstr(y - 1, x, '■■■')
    stdscr.addstr(y + 1, x, '■■■')
    
    enemies.append(fire_pos)

    stdscr.addstr(height - 3, 0, "one enemy at {}, {}".format(x, y))

    basic_settings.set_color_pair_with_gate(stdscr, 1, color_changable, False)
    
    return enemies

def updateEnemies(stdscr, fires, scrnresolution, enemies):
    speed = enemy_attris['speed']
    height = scrnresolution[0]
    to_eliminate = []
    for i in range(len(enemies)):
        enemies[i][0] += speed
        posy = math.floor(enemies[i][0])
        posx = enemies[i][1]
        if posy > height - 4 :
            to_eliminate.append(i)
        else:
            stdscr.addstr(posy, posx, '■■■')
            stdscr.addstr(posy - 1, posx, '■■■')
            stdscr.addstr(posy + 1, posx, '■■■')
    enemies_new = [enemies[i] for i in range(len(enemies)) if i not in to_eliminate]
    return enemies_new

def contactWithEnemy(posy, posx, enemies):
    for enemy in enemies:
        return

def updateFire(stdscr, fires, scrnresolution, enemies):

    basic_settings.set_color_pair_with_gate(stdscr, 1, color_changable, True)

    
    height = scrnresolution[0]
    speed = fire_attris['speed']
    to_eliminate = []
    for i in range(len(fires)):
        fires[i][0] -= speed
        posy = math.floor(fires[i][0])
        posx = fires[i][1]
        if posy < 0 or contactWithEnemy(posy, posx, enemies):
            to_eliminate.append(i)
        else:
            stdscr.addstr(posy, posx, '■')
    fires_new = [fires[i] for i in range(len(fires)) if i not in to_eliminate]

    basic_settings.set_color_pair_with_gate(stdscr, 1, color_changable, False)

    return fires_new

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
