"""Boardwalk Arcade: three local board games, using only Python's standard library.

Run: python game_arcade.py
One human plays against a computer; two to four humans share the keyboard/mouse.
"""
import math
import random
import tkinter as tk
from tkinter import ttk

BG = '#101827'
PANEL = '#1b2940'
INK = '#eef3fc'
MUTED = '#a9bad1'
COLORS = ['#fa7180', '#5ccef5', '#ffc968', '#9ce0a1']
GAMES = ['Ludo', 'Snakes and Ladders', 'Treasure Race']
SNAKES = {97: 78, 94: 73, 87: 24, 64: 60, 62: 19, 54: 34, 17: 7}
LADDERS = {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91}
SAFE = {0, 8, 13, 21, 26, 34, 39, 47}
TRACK = [(6,1),(6,2),(6,3),(6,4),(6,5),(5,6),(4,6),(3,6),
         (2,6),(1,6),(0,6),(0,7),(0,8),(1,8),(2,8),(3,8),
         (4,8),(5,8),(6,9),(6,10),(6,11),(6,12),(6,13),(6,14),
         (7,14),(8,14),(8,13),(8,12),(8,11),(8,10),(8,9),
         (9,8),(10,8),(11,8),(12,8),(13,8),(14,8),(14,7),
         (14,6),(13,6),(12,6),(11,6),(10,6),(9,6),(8,5),
         (8,4),(8,3),(8,2),(8,1),(8,0),(7,0),(6,0)]
LANES = [[(7,c) for c in range(1,7)], [(r,7) for r in range(1,7)],
         [(7,c) for c in range(13,7,-1)], [(r,7) for r in range(13,7,-1)]]
BASES = [[(r,c) for r in (2,4) for c in (2,4)],
         [(r,c) for r in (2,4) for c in (10,12)],
         [(r,c) for r in (10,12) for c in (10,12)],
         [(r,c) for r in (10,12) for c in (2,4)]]
QUESTIONS = [
    ('The river roars ahead. Which crossing is safest?', 'Stone bridge', 'Loose rocks', 0),
    ('A clue says: the sun guards the gold. Choose a chest.', 'Moon chest', 'Sun chest', 1),
    ('Your lantern goes out. What helps you find the trail?', 'Read the map', 'Walk blindly', 0),
    ('A locked gate blocks the route. What should you use?', 'A golden key', 'A leaf', 0),
    ('The sign says: follow flowing water. Which way?', 'Dry cave', 'River path', 1),
]


class Match:
    """Game rules independent of the graphical interface."""
    def __init__(self, game, names, solo=False, rng=None):
        self.game, self.names, self.solo = game, names, solo
        self.rng = rng or random.Random()
        self.turn = 0
        self.positions = [0] * len(names)
        self.tokens = [[-1] * 4 for _ in names]
        self.gems = [0] * len(names)
        self.keys = [False] * len(names)
        self.collected = [set() for _ in names]
        self.die = None
        self.pending = None
        self.winner = None
        self.message = 'Welcome! ' + names[0] + ' rolls first.'
        self.rounds = 0

    @property
    def ai(self):
        return self.solo and self.turn == 1

    def legal_tokens(self):
        if self.die is None:
            return []
        return [i for i, p in enumerate(self.tokens[self.turn])
                if (p == -1 and self.die == 6) or (0 <= p < 57 and p + self.die <= 57)]

    def roll(self, value=None):
        if self.winner is not None or self.die is not None or self.pending is not None:
            return False
        sides = 3 if self.game == GAMES[2] else 6
        self.die = self.rng.randint(1, sides) if value is None else value
        if not 1 <= self.die <= sides:
            self.die = None
            raise ValueError('Invalid die value')
        name, d = self.names[self.turn], self.die
        self.message = f'{name} rolled {d}. '
        if self.game == GAMES[0]:
            if self.legal_tokens():
                self.message += 'Choose a highlighted token.'
            else:
                self.message += 'No legal move.'
                self.finish_turn(extra=d == 6)
        elif self.game == GAMES[1]:
            target = self.positions[self.turn] + d
            if target > 100:
                self.message += 'An exact roll is needed to reach 100.'
            else:
                self.positions[self.turn] = target
                if target in SNAKES:
                    self.positions[self.turn] = SNAKES[target]
                    self.message += f'Snake! {target} slides to {SNAKES[target]}.'
                elif target in LADDERS:
                    self.positions[self.turn] = LADDERS[target]
                    self.message += f'Ladder! {target} climbs to {LADDERS[target]}.'
                else:
                    self.message += f'Moved to square {target}.'
                if self.positions[self.turn] == 100:
                    self.winner = self.turn
            self.finish_turn()
        else:
            self.positions[self.turn] = min(48, self.positions[self.turn] + d)
            self.land_treasure()
        return True

    def move_token(self, token):
        if token not in self.legal_tokens() or self.winner is not None:
            return False
        player, d = self.turn, self.die
        old = self.tokens[player][token]
        new = 0 if old == -1 else old + d
        self.tokens[player][token] = new
        captured = 0
        if new < 52:
            square = (player * 13 + new) % 52
            if square not in SAFE:
                for other, pieces in enumerate(self.tokens):
                    if other != player:
                        for i, p in enumerate(pieces):
                            if 0 <= p < 52 and (other * 13 + p) % 52 == square:
                                pieces[i] = -1
                                captured += 1
        self.message = f'{self.names[player]} moved token {token + 1}.'
        if captured:
            self.message += f' Captured {captured} token(s)!'
        if new == 57:
            self.message += ' Home!'
        if all(p == 57 for p in self.tokens[player]):
            self.winner = player
        self.finish_turn(extra=d == 6 or captured > 0)
        return True

    def finish_turn(self, extra=False):
        self.die = None
        self.rounds += 1
        if self.winner is not None:
            self.message += f' {self.names[self.winner]} wins!'
        elif extra:
            self.message += ' Roll again.'
        else:
            self.turn = (self.turn + 1) % len(self.names)

    def land_treasure(self):
        p, pos = self.turn, self.positions[self.turn]
        if pos == 48:
            if self.gems[p] >= 3 and self.keys[p]:
                self.winner = p
                self.message += 'The vault opens!'
            else:
                self.positions[p] = 36
                self.message += 'Vault needs 3 gems and a key. Return to the market at 36.'
                self.gems[p] += 1
                self.keys[p] = True
            self.finish_turn()
        elif pos in (7, 16, 25, 34, 43):
            if pos not in self.collected[p]:
                self.collected[p].add(pos)
                self.gems[p] += 1
                self.message += 'Found a gem!'
            else:
                self.message += 'This gem was already collected.'
            self.finish_turn()
        elif pos in (10, 22, 36):
            self.keys[p] = True
            self.gems[p] += 1
            self.message += 'Market: received a key and a gem.'
            self.finish_turn()
        elif pos in (12, 28, 40):
            self.positions[p] = max(0, pos - 4)
            self.message += 'Trap! Move back 4 spaces.'
            self.finish_turn()
        else:
            # Every other landing offers a clue, so each player can earn supplies.
            self.pending = self.rng.randrange(len(QUESTIONS))
            self.message += 'Answer the trail clue to earn a gem.'

    def answer(self, answer):
        if self.pending is None or self.winner is not None:
            return False
        correct = QUESTIONS[self.pending][3]
        if answer == correct:
            self.gems[self.turn] += 1
            self.message = f'{self.names[self.turn]} solved the clue! +1 gem.'
        else:
            self.positions[self.turn] = max(0, self.positions[self.turn] - 2)
            self.message = f'{self.names[self.turn]} missed the clue. Move back 2 spaces.'
        self.pending = None
        self.finish_turn()
        return True


RULES = {
    GAMES[0]: 'LUDO • Bring all four tokens home\n\nRoll a 6 to release a token. Click a highlighted token or its numbered button to move. '
    'Land on an opponent to send their token to base. Star cells are safe. '
    'A 6 or a capture earns another roll. You need an exact roll to reach home.\n\n'
    'This classroom edition allows tokens to share cells and has no blockades or three-sixes penalty. '
    'Each player has four tokens and a separate home lane.',
    GAMES[1]: 'SNAKES AND LADDERS • First to square 100\n\nAll players begin off the board at 0. '
    'Roll and move automatically. Green ladders take you up; red snakes bring you down. '
    'You must roll the exact number to reach 100. An overshoot leaves you in place. '
    'Turns always alternate; rolling a 6 gives no extra turn.',
    GAMES[2]: 'TREASURE RACE • Open the vault\n\nRoll a three-sided die to explore 49 trail spaces. '
    'Solve clues for gems. G tiles hold one gem per player. M markets grant a key and a gem on each visit. '
    'T traps push you back 4 spaces. A wrong clue pushes you back 2.\n\n'
    'Reach the vault at 48 with at least 3 gems and a key to win. No exact roll is required. '
    'Without enough supplies, return to market 36 and receive a gem and key. '
    'Players may share squares. Displaced moves do not trigger another tile.'
}


class Arcade:
    def __init__(self, root):
        self.root = root
        root.title('Boardwalk Arcade | Python Game Collection')
        root.geometry('1180x840')
        root.minsize(1000, 760)
        root.configure(bg=BG)
        self.count = tk.IntVar(value=1)
        self.names = [tk.StringVar(value=f'Player {i+1}') for i in range(4)]
        self.epoch = 0
        self.match = None
        self.last_die = '—'
        self.show_menu()

    def label(self, parent, text, size=12, color=INK, **kwargs):
        return tk.Label(parent, text=text, font=('Segoe UI', size), bg=parent['bg'], fg=color, **kwargs)

    def button(self, parent, text, command, color='#324866', **kwargs):
        return tk.Button(parent, text=text, command=command, font=('Segoe UI', 11, 'bold'),
                         bg=color, fg=INK, activebackground='#48617e', activeforeground=INK,
                         relief='flat', padx=15, pady=10, cursor='hand2', **kwargs)

    def clear(self):
        self.epoch += 1  # Old computer-turn callbacks cannot affect a new screen.
        for child in self.root.winfo_children():
            child.destroy()

    def show_menu(self):
        self.clear()
        self.match = None
        outer = tk.Frame(self.root, bg=BG, padx=38, pady=30)
        outer.pack(fill='both', expand=True)
        self.label(outer, 'B O A R D W A L K', 13, '#72d8e6').pack(anchor='w')
        self.label(outer, 'One arcade. Three adventures.', 30).pack(anchor='w', pady=(8,4))
        self.label(outer, 'Built with Python  •  Local multiplayer  •  No downloads or accounts', 12, MUTED).pack(anchor='w')
        setup = tk.Frame(outer, bg=PANEL, padx=22, pady=18)
        setup.pack(fill='x', pady=24)
        self.label(setup, 'HOW MANY HUMAN PLAYERS?', 12).pack(anchor='w')
        counts = tk.Frame(setup, bg=PANEL); counts.pack(anchor='w', pady=10)
        for n in range(1,5):
            tk.Radiobutton(counts, text=f'  {n} player' + ('s  ' if n>1 else '  '),
                           variable=self.count, value=n, command=self.update_names,
                           bg=PANEL, fg=INK, selectcolor='#3c5270', activebackground=PANEL,
                           activeforeground=INK, font=('Segoe UI',12)).pack(side='left', padx=(0,20))
        self.name_bar = tk.Frame(setup,bg=PANEL); self.name_bar.pack(fill='x')
        self.name_widgets=[]
        for i in range(4):
            box=tk.Frame(self.name_bar,bg=PANEL);box.pack(side='left',expand=True,fill='x',padx=(0,12))
            self.label(box, f'PLAYER {i+1}',10,COLORS[i]).pack(anchor='w')
            entry=tk.Entry(box,textvariable=self.names[i],font=('Segoe UI',11),bg='#111f33',fg=INK,
                           insertbackground=INK,relief='flat',width=17)
            entry.pack(fill='x',ipady=8,pady=5); self.name_widgets.append(entry)
        self.setup_hint=self.label(setup,'',11,MUTED);self.setup_hint.pack(anchor='w',pady=(4,0))
        self.update_names()
        cards=tk.Frame(outer,bg=BG);cards.pack(fill='both',expand=True)
        summaries=['Four tokens. One home stretch.\nRelease, race and capture.',
                   'A familiar race to 100.\nClimb high. Watch your step.',
                   'Follow clues. Collect gems.\nFind a key and open the vault.']
        for i, game in enumerate(GAMES):
            card=tk.Frame(cards,bg=PANEL,padx=20,pady=24)
            card.grid(row=0,column=i,sticky='nsew',padx=(0,14) if i<2 else 0)
            cards.columnconfigure(i,weight=1,uniform='cards')
            self.label(card,f'0{i+1}',28,COLORS[i]).pack(anchor='w')
            self.label(card,game,19).pack(anchor='w',pady=(12,10))
            self.label(card,summaries[i],11,MUTED,justify='left').pack(anchor='w')
            self.button(card,'Play game  →',lambda g=game:self.start(g)).pack(side='bottom',fill='x',pady=(22,0))
        cards.rowconfigure(0,weight=1)
        self.label(outer,'Shared computer • Take turns using the mouse • Space rolls the die',11,MUTED).pack(pady=(20,0))
        self.root.unbind('<space>')

    def update_names(self):
        n=self.count.get()
        for i, entry in enumerate(self.name_widgets):
            entry.configure(state='normal' if i<n else 'disabled', disabledbackground='#192437',disabledforeground='#64748b')
        self.setup_hint.config(text='Solo mode: you versus Computer.' if n==1 else f'{n} people take turns on this computer.')

    def start(self, game, previous_names=None, solo=None):
        if previous_names is None:
            n=self.count.get()
            names=[v.get().strip()[:18] or f'Player {i+1}' for i,v in enumerate(self.names[:n])]
            if n==1:names.append('Computer')
            solo=n==1
        else:names=previous_names
        self.clear()
        self.match=Match(game,names,solo)
        self.last_die='—'
        self.history=[]
        head=tk.Frame(self.root,bg=BG,padx=22,pady=14);head.pack(fill='x')
        self.button(head,'← Arcade',self.show_menu).pack(side='left')
        self.label(head,game,23).pack(side='left',padx=22)
        self.button(head,'Rules',self.rules).pack(side='right')
        self.button(head,'New round',lambda:self.start(game,names,solo)).pack(side='right',padx=10)
        body=tk.Frame(self.root,bg=BG);body.pack(fill='both',expand=True,padx=22,pady=(0,20))
        sidebar=tk.Frame(body,bg=PANEL,width=265,padx=16,pady=15);sidebar.pack(side='right',fill='y',padx=(16,0));sidebar.pack_propagate(False)
        self.label(sidebar,'PLAYERS',11,MUTED).pack(anchor='w')
        self.player_labels=[]
        for i,name in enumerate(names):
            label=self.label(sidebar,'',12,COLORS[i],justify='left',anchor='w')
            label.pack(fill='x',pady=10);self.player_labels.append(label)
        self.dice_label=self.label(sidebar,'—',40);self.dice_label.pack(pady=(10,0))
        self.roll_button=self.button(sidebar,'Roll die  [Space]',self.roll,color='#235c70');self.roll_button.pack(fill='x',pady=8)
        self.controls=tk.Frame(sidebar,bg=PANEL);self.controls.pack(fill='x')
        self.label(sidebar,'LATEST MOVES',10,MUTED).pack(anchor='w',pady=(18,5))
        self.log=self.label(sidebar,'',10,MUTED,justify='left',anchor='nw',wraplength=228);self.log.pack(fill='both',expand=True)
        left=tk.Frame(body,bg=BG);left.pack(side='left',fill='both',expand=True)
        self.status=self.label(left,'',13,INK,anchor='w',justify='left',wraplength=740);self.status.pack(fill='x',pady=(0,10))
        self.canvas=tk.Canvas(left,bg='#162338',highlightthickness=0)
        self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Configure>',lambda e:self.draw())
        self.canvas.bind('<Button-1>',self.click_board)
        self.question_frame=tk.Frame(left,bg=BG);self.question_frame.pack(fill='x')
        self.root.bind('<space>',lambda e:self.roll())
        self.refresh()

    def rules(self):
        popup=tk.Toplevel(self.root);popup.title('Game rules');popup.configure(bg=PANEL)
        popup.transient(self.root)
        self.label(popup,RULES[self.match.game],12,justify='left',wraplength=570).pack(padx=26,pady=24)
        self.button(popup,'Got it',popup.destroy).pack(pady=(0,20))

    def record(self):
        self.history.insert(0,self.match.message)
        self.history=self.history[:5]

    def roll(self):
        m=self.match
        if not m or m.ai or m.winner is not None:return
        self.do_roll()

    def do_roll(self):
        m=self.match
        # Keep the displayed die after the rules engine advances the turn.
        if m.die is not None or m.pending is not None or m.winner is not None:return
        value=m.rng.randint(1,3 if m.game==GAMES[2] else 6)
        m.roll(value);self.last_die=str(value);self.record();self.refresh()

    def choose_token(self, token):
        m=self.match
        if m and not m.ai and m.move_token(token):
            self.record();self.refresh()

    def choose_answer(self, answer):
        if self.match and not self.match.ai and self.match.answer(answer):
            self.record();self.refresh()

    def refresh(self):
        m=self.match
        if m is None:return
        self.status.config(text=(f'WINNER • {m.names[m.winner]}!  Start a new round or return to the arcade.'
                                 if m.winner is not None else f'{m.names[m.turn]}’s turn  •  '+m.message))
        for i,label in enumerate(self.player_labels):
            marker='▶ ' if i==m.turn and m.winner is None else '  '
            if m.game==GAMES[0]:detail=f'{sum(p==57 for p in m.tokens[i])}/4 home'
            elif m.game==GAMES[1]:detail=f'Square {m.positions[i]} / 100'
            else:detail=f'Space {m.positions[i]} • {m.gems[i]} gems • Key: {"yes" if m.keys[i] else "no"}'
            label.config(text=marker+m.names[i]+'\n   '+detail)
        self.dice_label.config(text=self.last_die)
        ready=m.winner is None and not m.ai and m.die is None and m.pending is None
        self.roll_button.config(state='normal' if ready else 'disabled',text='Roll 1–3  [Space]' if m.game==GAMES[2] else 'Roll die  [Space]')
        for frame in (self.controls,self.question_frame):
            for child in frame.winfo_children():child.destroy()
        if m.game==GAMES[0] and m.die is not None:
            for token in m.legal_tokens():
                self.button(self.controls,f'Token {token+1}',lambda t=token:self.choose_token(t),
                            state='disabled' if m.ai else 'normal').pack(fill='x',pady=2)
        if m.pending is not None:
            q=QUESTIONS[m.pending]
            self.label(self.question_frame,q[0],12,wraplength=690).pack(pady=8)
            choices=tk.Frame(self.question_frame,bg=BG);choices.pack()
            for i in range(2):
                self.button(choices,q[i+1],lambda a=i:self.choose_answer(a),state='disabled' if m.ai else 'normal').pack(side='left',padx=8)
        self.log.config(text='\n\n'.join(self.history))
        self.draw()
        if m.ai and m.winner is None:
            epoch=self.epoch
            self.root.after(850,lambda:self.computer_turn(epoch))

    def computer_turn(self,epoch):
        if epoch!=self.epoch or not self.match or not self.match.ai:return
        m=self.match
        if m.winner is not None:return
        if m.pending is not None:
            # A fallible opponent: correct about three quarters of the time.
            correct=QUESTIONS[m.pending][3]
            m.answer(correct if m.rng.random()<.75 else 1-correct)
            self.record();self.refresh()
        elif m.die is not None:
            legal=m.legal_tokens()
            if legal:
                token=max(legal,key=lambda i:(m.tokens[m.turn][i]+m.die==57,
                          m.tokens[m.turn][i]==-1,m.tokens[m.turn][i]))
                m.move_token(token);self.record();self.refresh()
        else:self.do_roll()

    def draw(self):
        if not self.match or not hasattr(self,'canvas'):return
        c=self.canvas;c.delete('all');self.hit_tokens=[]
        w,h=c.winfo_width(),c.winfo_height()
        if w<20 or h<20:return
        if self.match.game==GAMES[0]:self.draw_ludo(w,h)
        else:self.draw_race(w,h)

    def token(self,x,y,r,player,text,highlight=False,token_id=None):
        c=self.canvas
        c.create_oval(x-r,y-r,x+r,y+r,fill=COLORS[player],outline='#ffffff' if highlight else '#101827',width=3 if highlight else 1.5)
        c.create_text(x,y,text=text,fill='#122034',font=('Segoe UI',max(8,int(r*.9)),'bold'))
        if token_id is not None:self.hit_tokens.append((x,y,r,token_id))

    def draw_ludo(self,w,h):
        c=self.canvas;m=self.match
        side=min(w-24,h-30);cell=side/15;ox=(w-side)/2;oy=(h-side)/2
        def center(rc):return ox+(rc[1]+.5)*cell,oy+(rc[0]+.5)*cell
        for player,(r,col) in enumerate([(0,0),(0,9),(9,9),(9,0)]):
            c.create_rectangle(ox+col*cell,oy+r*cell,ox+(col+6)*cell,oy+(r+6)*cell,fill=COLORS[player],outline=BG,width=2)
            c.create_rectangle(ox+(col+1)*cell,oy+(r+1)*cell,ox+(col+5)*cell,oy+(r+5)*cell,fill='#203047',outline='')
        for i,rc in enumerate(TRACK):
            x,y=center(rc);fill='#edf2f8'
            if i%13==0:fill=COLORS[i//13]
            c.create_rectangle(x-cell/2,y-cell/2,x+cell/2,y+cell/2,fill=fill,outline='#a0b0c4')
            if i in SAFE:c.create_text(x,y,text='★',fill='#65758d',font=('Segoe UI',int(cell*.43)))
        for player,lane in enumerate(LANES):
            for rc in lane:
                x,y=center(rc);c.create_rectangle(x-cell/2,y-cell/2,x+cell/2,y+cell/2,fill=COLORS[player],outline='#40536d')
        c.create_rectangle(ox+6*cell,oy+6*cell,ox+9*cell,oy+9*cell,fill='#30445c',outline='')
        c.create_text(ox+7.5*cell,oy+7.5*cell,text='HOME',fill=INK,font=('Segoe UI',max(8,int(cell*.36)),'bold'))
        occupied={}
        for player,pieces in enumerate(m.tokens):
            for token,p in enumerate(pieces):
                if p==-1:rc=BASES[player][token]
                elif p<52:rc=TRACK[(player*13+p)%52]
                else:rc=LANES[player][p-52]
                occupied.setdefault(rc,[]).append((player,token))
        for rc,pieces in occupied.items():
            x,y=center(rc)
            for j,(player,token) in enumerate(pieces):
                n=len(pieces);dx=0 if n==1 else ((j%2)-.5)*cell*.43
                dy=0 if n==1 else ((j//2)-(math.ceil(n/2)-1)/2)*cell*.32
                radius=cell*(.32 if n==1 else .23 if n<=4 else .16)
                self.token(x+dx,y+dy,radius,player,str(token+1),
                           player==m.turn and token in m.legal_tokens() and not m.ai,
                           token if player==m.turn else None)
        c.create_text(w/2,h-7,text='★ Safe square    •    Click a highlighted token to move',fill=MUTED,font=('Segoe UI',10))

    def draw_race(self,w,h):
        c=self.canvas;m=self.match;snakes=m.game==GAMES[1]
        size=10 if snakes else 7
        side=min(w-20,h-42);cell=side/size;ox=(w-side)/2;oy=10
        centers={}
        for row in range(size):
            for col in range(size):
                pos=row*size+(col if row%2==0 else size-1-col)+(1 if snakes else 0)
                x=ox+col*cell;y=oy+(size-1-row)*cell
                centers[pos]=(x+cell/2,y+cell/2)
                fill='#24374e' if (row+col)%2 else '#2d435c'
                tag=''
                if not snakes:
                    if pos in (7,16,25,34,43):fill='#376b63';tag='G'
                    elif pos in (10,22,36):fill='#77603c';tag='M'
                    elif pos in (12,28,40):fill='#6c3b4e';tag='T'
                    elif pos==48:fill='#4f4680';tag='VAULT'
                    elif pos==0:tag='START'
                c.create_rectangle(x,y,x+cell,y+cell,fill=fill,outline='#142238',width=1)
                c.create_text(x+6,y+5,text=str(pos),anchor='nw',fill=MUTED,font=('Segoe UI',max(8,int(cell*.17))))
                if tag:c.create_text(x+cell*.65,y+cell*.28,text=tag,fill=INK,font=('Segoe UI',max(8,int(cell*.14)),'bold'))
        if snakes:
            for start,end in LADDERS.items():
                x1,y1=centers[start];x2,y2=centers[end]
                dx,dy=x2-x1,y2-y1;length=math.hypot(dx,dy);nx=-dy/length*4;ny=dx/length*4
                for sign in (-1,1):c.create_line(x1+sign*nx,y1+sign*ny,x2+sign*nx,y2+sign*ny,fill='#79d7a1',width=2)
                for step in range(1,8):
                    t=step/8;x=x1+dx*t;y=y1+dy*t
                    c.create_line(x-nx,y-ny,x+nx,y+ny,fill='#79d7a1',width=2)
            for start,end in SNAKES.items():
                x1,y1=centers[start];x2,y2=centers[end]
                c.create_line(x1,y1,x1+cell*.7,y1+cell*.3,x2-cell*.7,y2-cell*.3,x2,y2,
                              fill='#fa7180',width=5,smooth=True,arrow='last')
                c.create_oval(x1-5,y1-5,x1+5,y1+5,fill='#ffc2ca',outline='')
        for p,pos in enumerate(m.positions):
            if snakes and pos==0:continue
            x,y=centers[pos]
            self.token(x+(p%2-.5)*cell*.32,y+(p//2-.5)*cell*.32,cell*.18,p,str(p+1))
        legend='Green = ladder up  •  Pink = snake down  •  Start at 0 (off board)' if snakes else 'G = gem  •  M = market / key  •  T = trap  •  Goal: 3 gems + key'
        c.create_text(w/2,oy+side+18,text=legend,fill=MUTED,font=('Segoe UI',10))

    def click_board(self,event):
        if not self.match or self.match.ai:return
        for x,y,r,token in reversed(self.hit_tokens):
            if (event.x-x)**2+(event.y-y)**2<r*r:
                self.choose_token(token);break


if __name__ == '__main__':
    root=tk.Tk()
    Arcade(root)
    root.mainloop()
