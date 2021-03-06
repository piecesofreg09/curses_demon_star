# Demonstar AI

[Demonstar](http://www.mking.com/demonstar_game.html)
is an old space STG. I saw a lot of people has done AI on the game Snake. So I decided to do something on the game Demonstar.

Usage:

~~~
python game.py [option] [repeat_times]

options include: g, sv_t, sv_g, sc_t, sc_g

Examples:

python game.py                # simply play the game
python game.py sv_t           # survival training data collection
python game.py sv_t 5         # using automated survival training data collection, repeat 5 times
~~~

sv_t: **s**ur**v**ival **t**raining, generate the data to survival in the game
sv_g: after **s**ur**v**ival training, play the **g**ame for stats comparison
sc_t: **sc**ore **t**raining, generate the data to score higher
sc_g: after **sc**ore training, play the **g**ame for stats comparison

## 1. Writing the game

The game is written in curses on python 3.6. It is a simple shooting game. The blue rectangle stands for the fighter, the white rectangles stands for the enemeies. Blue 'v' going downwards are topedoes generated by the enemies, white '^' going upwards are fires shot by the fighter.

Moving the fighter requires input from keyboard, using up/down/left/right arrows. Shooting fire needs the input from keyboard of letter 'z'. On the bottom of the screen, the **score** (number of enemies eliminated) and the **life left** are shown.

<p align="center">
  <img src="https://github.com/piecesofreg09/curses_demon_star/blob/master/Pics/simple_game.PNG" width='450px' />
  <img src="https://github.com/piecesofreg09/curses_demon_star/blob/master/Pics/game_over.PNG" width='250px' />
</p>

Game strategy:

There are two components of the game. (1) avoid the enemies and the topedoes, (2) eliminate the enemies using fires. The first mission is then called **survival**

## 2. Training

### 2.1 Generating Data for survival

After creating the game, generating the data is easy. To train the 
