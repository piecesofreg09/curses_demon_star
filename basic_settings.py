
import curses


def set_color_pairs():
    curses.start_color()
    
    #print(curses.COLORS)
    # the terminal can support up to 16 colors
    
    
    set_color_numbers()
    
    
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, 12, 13)
    
    

def set_color_numbers():
    if curses.can_change_color() and curses.has_colors():
        curses.init_color(12, 100, 100, 900)
        curses.init_color(13, 100, 400, 300)

def set_color_pair_with_gate(stdscr, num, color_changable, on_off):
    if color_changable:
        if on_off:
            stdscr.attron(curses.color_pair(num))
        else:
            stdscr.attroff(curses.color_pair(num))