
import curses


def set_color_pairs():
    curses.start_color()
    
    #print(curses.COLORS)
    # the terminal can support up to 16 colors
    
    
    set_color_numbers()
    
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, 12, curses.COLOR_BLACK)
    curses.init_pair(5, 13, curses.COLOR_BLACK)
    
    

def set_color_numbers():
    if curses.can_change_color() and curses.has_colors():
        curses.init_color(12, 247, 255, 0) # yellow
        curses.init_color(13, 189, 189, 189) # grey

def set_color_pair_with_gate(stdscr, num, color_changable, on_off):
    if color_changable:
        if on_off:
            stdscr.attron(curses.color_pair(num))
        else:
            stdscr.attroff(curses.color_pair(num))

def set_color_decor(num):
    # decorator for the setting of colors, wrapped around functions
    # that needs color setting
    def set_color(func):
        def wrapper(*args, **kwargs):
            
            set_color_pair_with_gate(args[0].stdscr, 
                num, args[0].color_changable, True)
            func(*args, **kwargs)
            set_color_pair_with_gate(args[0].stdscr, 
                num, args[0].color_changable, False)
            
        return wrapper
        
    return set_color
            
    
            
            
            
            
            
            
            
            
            
            