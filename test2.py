import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN, BUTTON_CTRL

def init_screen(stdscr):
    stdscr.clear()
    stdscr.refresh()
    curses.initscr()
    #stdscr.nodelay(1)
    
def draw_menu(stdscr):
    k = 0
    init_screen(stdscr)
    y1 = 10
    y2 = 30
    while (k != ord('q')):
        stdscr.clear()
        
        if k == curses.KEY_DOWN:
            y1 = y1 + 1
            y2 = y2 - 1
        if k == curses.KEY_UP:
            y1 = y1 - 1
            y2 = y2 + 1
        draw_one(stdscr, y1)
        draw_two(stdscr, y2)
        
        # Refresh the screen
        stdscr.refresh()
        # Wait for next input
        k = stdscr.getch()

def draw_one(stdscr, y):
    stdscr.addstr(y, 1, 'O')
    stdscr.addstr(y, 3, 'O')
    stdscr.addstr(y, 5, 'O')

def draw_two(stdscr, y):
    stdscr.addstr(y, 13, '==')
    stdscr.addstr(y, 15, '==')
    stdscr.addstr(y, 17, '==')

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()