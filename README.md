# Demonstar AI

[Demonstar](http://www.mking.com/demonstar_game.html)
is an old space STG. I saw a lot of people has done AI on the game Snake. So I decided to do something on the game Demonstar.

Usage:

~~~
python game.py [option] [repeat_times]
options include: g, sv_t, sv_g, sc_t, sc_g
#Examples

python game.py                # simply play the game
python game.py sv_t           # survival training data collection
python game.py sv_t 5         # using automated survival training data collection, repeat 5 times
~~~


## 1. Writing the game

The game is written in curses on python 3.6. 


