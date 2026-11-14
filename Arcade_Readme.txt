BOARDWALK ARCADE
Three games in one Python app

RUN
1. Install Python 3 with Tcl/Tk (included in the normal Windows Python installer).
2. Open this folder in a terminal.
3. Run: python game_arcade.py
No pip packages or internet connection are required.

PLAYERS
Choose 1, 2, 3 or 4 human players on the menu and optionally enter names.
1 human: play against Computer.
2-4 humans: share one computer and take turns.
Select any of the three games. Click Arcade to change games or player settings.
New round restarts the current game with the same players.

CONTROLS
Click Roll die or press Space.
Ludo: after rolling, click a highlighted token or its numbered sidebar button.
Treasure Race: click an answer when a clue appears.
Computer opponents take their turns automatically.
Click Rules in a game for its complete rules.

LUDO
Each player has four tokens. A 6 releases a token from base onto its start cell.
Roll and move around the board, then along your colored home lane.
An exact roll is required to finish a token. Bring all four home to win.
Landing on opponents on a non-star square sends them back to base.
A 6 or a capture grants another roll. Star squares are safe.
Classroom edition: no blockades and no three-sixes penalty; shared cells allowed.

SNAKES AND LADDERS
Start at 0, off the board. Roll a six-sided die and race to 100.
Green ladders move you up; pink snakes move you down.
You need the exact roll to reach 100. Overshooting leaves you in place.
Turns alternate even after a 6.

TREASURE RACE
Explore spaces 0-48 using a three-sided die.
G: collect a gem (once per player at that location).
M: receive a key and a gem on every visit.
T: move back 4 spaces.
Other spaces give a multiple-choice trail clue: correct = a gem;
incorrect = move back 2 spaces. Displaced moves do not activate another tile.
Reach the vault at 48 with 3 or more gems and a key to win.
No exact roll required. If supplies are missing, return to market 36 and
receive a gem and key; then try again.

IMPLEMENTATION
Python standard library: tkinter for graphics, random for dice, math for layout.
The Match class contains game rules; Arcade builds the interface.
Core concepts include variables, integers, strings, Booleans, conditions,
loops, lists, dictionaries, sets, functions, classes and event callbacks.
This graphical collection extends the earlier beginner console project.
The existing Treasure_Trail_Project.docx describes the earlier console game;
it does not document this new three-game arcade.
