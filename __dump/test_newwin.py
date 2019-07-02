import curses

def init_sc(stdscr_default, y, x):
    print(stdscr_default.getmaxyx())
    stdscr_default.clear()
    stdscr_default.refresh()
    curses.initscr()
    win = curses.newwin(y, x)
    win.nodelay(1)
    height, width = win.getmaxyx()
    reso = [height, width]
    print(reso)
    return win

def draw_menu(stdscr_default):
    k = 0
    stdscr = init_sc(stdscr_default, 20, 15)
    print(stdscr.getmaxyx())
    stdscr2 = init_sc(stdscr_default, 15, 8)
    print(stdscr2.getmaxyx())
    while (k != ord('q')):
        stdscr.clear()
        stdscr.refresh()
        
        k = stdscr.getch()

def game():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    game()