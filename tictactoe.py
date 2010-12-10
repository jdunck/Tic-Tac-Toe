from copy import deepcopy

HUMAN = 1
UNPLAYED = 0
COMPUTER = -1 * HUMAN #not arbitrary; logic based on math below.

POSITIONS = [(i,j) for i in range(3) for j in range(3)]
LINES = [[(i,j) for i in range(3)] for j in range(3)] + \
             [[(i,j) for j in range(3)] for i in range(3)] + \
             [[(i,i) for i in range(3)]] + \
             [[(2-i,i) for i in range(3)]]
CORNERS = [(0,0),(0,2),(2,2),(2,0)]
SIDES = [(1,0),(1,2),(2,1),(0,1)]
CENTER = (1,1)
TEMPLATE = """
+-----------+
| %s | %s | %s |
|---+---+---|
| %s | %s | %s |
|---+---+---|
| %s | %s | %s |
+-----------+
"""

class IllegalMove(Exception):
    pass

class Game(object):

    def __init__(self):
        self.state = dict([((i,j), 0) for i in range(3) for j in range(3)])
        self.turn = 0 #fixme: random chance
        self.human_display = "X"
        self.computer_display = "O"
        self.strategies = [self.try_win,
                           self.try_block,
                           self.try_fork,
                           self.try_force_defense,
                           self.try_block_fork,
                           self.try_center,
                           self.try_opposite,
                           self.try_corner,
                           self.try_side]
        self.winner = None
        

    def play(self):
        while not self.check_done():
            if self.turn % 2 == 0:
                self.human()
            else:
                self.comp()
            self.turn += 1
        
        self.display()
        if self.winner == 0:
            print "I do not lose."
        elif self.winner == -1:
            print "I WIN."
        else:
            print "He had very pointy teeth..."
            

    def apply(self, board, move, who):
        board[move] = who
        return board

    def trial(self, state, move, who):
        return apply(deepcopy(state), move, who)
        
    def human(self):
        while True:
            self.display()
            try:
                position = divmod(int(raw_input("Your move.  Choose 1-9: "))-1, 3)
            except ValueError:
                print "Invalid position"
                continue
            if not self.is_unplayed(self.state, position):
                print "Already taken."
                continue
            break

        self.apply(self.state, position, HUMAN)

    def check_done(self):
        self.winner = self.winner or self.find_winner()
        if self.winner:
            return True
        #is the board full?
        if not filter(lambda v: v==0, self.state.values()):
            self.winner = 0
            return True
        return False

    def find_winner(self):
        for line in LINES:
            fill = sum([self.state[position] for position in line])
            print line, fill
            if fill == 3:
                return HUMAN
            elif fill == -3:
                return COMPUTER
            else:
                pass

    def comp(self):
        for attempt in self.strategies:
            move = attempt(COMPUTER)
            if move:
                print attempt.__name__
                break
        else:
            raise DeprecationWarning, "I have failed."
        self.apply(self.state, move, COMPUTER)

    def played_by(self, board, position, who):
        return board[position] == who

    def is_unplayed(self, board, position):
        return self.played_by(board, position, UNPLAYED)

    def other_player(self, who):
        return -1 * who
        
    def impl(self, name):
        print "self.impl %s" % name
    def try_win(self, who):
        self.impl("win")
    def try_block(self, who):
        self.impl("block")
    def try_fork(self, who):
        self.impl("fork")
    def try_force_defense(self, who):
        self.impl("force defense (opt 1)")
    def try_block_fork(self, who):
        self.impl("block fork (opt 2)")

    def try_opposite(self, who):
        for i,corner in enumerate(CORNERS):
            if self.played_by(self.state, corner, self.other_player(who)):
                opposite = CORNERS[(i+2) % 4]
                if self.played_by(self.state, opposite, UNPLAYED):
                    return opposite

    def _try_list(self, positions, who):
        for position in positions:
            if self.played_by(self.state, position, UNPLAYED):
                return position
    def try_center(self, who):
        return self._try_list([CENTER], who)
    def try_corner(self, who):
        return self._try_list(CORNERS, who)
    def try_side(self, who):
        return self._try_list(SIDES, who)

    def display(self):
        positions = tuple([["?", self.human_display, self.computer_display][self.state[position]] for position in POSITIONS])
        print TEMPLATE % positions
        
if __name__ == '__main__':
    run()