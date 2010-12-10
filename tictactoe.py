from copy import deepcopy

#These values are not arbitrary; logic based on math & index wrap-around below.
[UNPLAYED, HUMAN, COMPUTER] = 0, 1, -1

#The board is a dict of (row, col) -> status
POSITIONS = tuple([(i,j) for i in range(3) for j in range(3)])

#strategic positions:
LINES = [tuple([(i,j) for i in range(3)]) for j in range(3)] + \
             [tuple([(i,j) for j in range(3)]) for i in range(3)] + \
             [tuple([(i,i) for i in range(3)])] + \
             [tuple([(2-i,i) for i in range(3)])]
CORNERS = [(0,0),(0,2),(2,2),(2,0)]
SIDES = [(1,0),(1,2),(2,1),(0,1)]
CENTER = (1,1)

#for output
TEMPLATE = """
+-----------+
| %s | %s | %s |
|---+---+---|
| %s | %s | %s |
|---+---+---|
| %s | %s | %s |
+-----------+
"""

class Game(object):
    def __init__(self, first_player=None, initial_board=None, input_source=None):
        """
        g.Game(first_player=tictactoe.HUMAN)
        g.play()
        """
        #shims for testing:
        if initial_board:
            self.board = initial_board
        else:
            self.board = dict([((i,j), 0) for i in range(3) for j in range(3)])
        if input_source is None:
            self.input_source = lambda g: int(raw_input("Your move.  Choose 1-9: "))-1
        else:
            self.input_source = input_source

        if first_player == COMPUTER:
            self.turn = 1
        else:
            self.turn = 0
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
            print "We draw - It's wafer thin."
        elif self.winner == -1:
            print "I win - Bring me a shubbery."
        else:
            print "I - LOSE?! - It's just a flesh wound."
            import pdb; pdb.set_trace()
        return self.winner

    def apply(self, board, move, who):
        board[move] = who
        return board

    def trial(self, board, move, who):
        return self.apply(deepcopy(board), move, who)
        
    def human(self):
        def get_value():
            try:
                position = self.input_source(self)
            except ValueError:
                print "Invalid position"
                return False
            if position < 0 or 8 < position:
                print "Out of bounds."
                return False
            position = divmod(position, 3)
            if not self.is_unplayed(self.board, position):
                print "Already taken."
                return False
            return position
            
        while True:
            self.display()
            position = get_value()
            if position:
                break

        self.apply(self.board, position, HUMAN)

    def check_done(self):
        self.winner = self.winner or self.find_winner()
        if self.winner:
            return True
        #is the board full?
        if not filter(lambda v: v==0, self.board.values()):
            self.winner = 0
            return True
        return False

    def find_winner(self):
        for line in LINES:
            fill = sum([self.board[position] for position in line])
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
                break
        else:
            raise DeprecationWarning, "I have failed."
        self.apply(self.board, move, COMPUTER)

    def played_by(self, board, position, who):
        return board[position] == who

    def is_unplayed(self, board, position):
        return self.played_by(board, position, UNPLAYED)

    def other_player(self, who):
        return -1 * who
        
    def impl(self, name):
        print "self.impl %s" % name

    def collect_line(self, board, line):
        ret = [[],[],[]] #unplayed, human, comp
        for position in line:
            ret[board[position]].append(position)
        return ret
    def collect_lines(self, board):
        ret = {}
        for line in LINES:
            ret[line] = self.collect_line(board, line)
        return ret
    def collect_available(self):
        ret = []
        for position in POSITIONS:
            if self.board[position] == UNPLAYED:
                ret.append(position)
        return ret

    def find_win_lines(self, board, who):
        for line, collection in self.collect_lines(board).items():
            if len(collection[who]) == 2 and len(collection[UNPLAYED]) == 1:
                yield collection[UNPLAYED][0], line

    def try_win(self, who):
        position = None
        for position, line in self.find_win_lines(self.board, who):
            break
        return position
    def try_block(self, who):
        return self.try_win(self.other_player(who))

    def find_forks(self, board, who):
        for position in POSITIONS:
            if board[position] == UNPLAYED:
                board_maybe = self.trial(board, position, who)
                if len(list(self.find_win_lines(board_maybe, who))) >= 2:
                    yield position

    def try_fork(self, who):
        for position in self.find_forks(self.board, who):
            return position

    def _find_seconds(self, board, who):
        for line, collection in self.collect_lines(board).items():
            if len(collection[self.other_player(who)]) == 0 and len(collection[who]) == 1:
                yield collection[UNPLAYED][0], collection[UNPLAYED][1]
                yield collection[UNPLAYED][1], collection[UNPLAYED][0]
            
    def try_force_defense(self, who):
        for position, completion in self._find_seconds(self.board, who):
            board_maybe = self.trial(self.board, position, who)
            gives_win = len(list(self.find_win_lines(board_maybe, self.other_player(who))))
            if gives_win:
                continue
            for fork in self.find_forks(board_maybe, self.other_player(who)):
                if fork == completion:
                    break
            else:
                #no fork was found, so this is a good defensive force.
                return position
        
    def try_block_fork(self, who):
        original_forks = len(list(self.find_forks(self.board, self.other_player(who))))
        if not original_forks:
            return
        for position in self.collect_available():
            board_maybe = self.trial(self.board, position, who)
            future_forks = len(list(self.find_forks(board_maybe, self.other_player(who))))
            if future_forks < original_forks:
                return position

    def try_opposite(self, who):
        for i,corner in enumerate(CORNERS):
            if self.played_by(self.board, corner, self.other_player(who)):
                opposite = CORNERS[(i+2) % 4]
                if self.played_by(self.board, opposite, UNPLAYED):
                    return opposite

    def _try_list(self, positions, who):
        for position in positions:
            if self.played_by(self.board, position, UNPLAYED):
                return position
    def try_center(self, who):
        return self._try_list([CENTER], who)
    def try_corner(self, who):
        return self._try_list(CORNERS, who)
    def try_side(self, who):
        return self._try_list(SIDES, who)

    def display(self, board=None):
        if board is None:
            board = self.board
        positions = tuple([[str(3*position[0]+position[1]+1), self.human_display, self.computer_display][board[position]] for position in POSITIONS])
        print TEMPLATE % positions


#inspired by dgouldin's test generator.
current_branch = None
games_played = 0
def test():
    #I'm a bit nervous here, because it seems there should be 9! possible games (ignoring symmetries), but we're playing far fewer than that.
    global current_branch
    global games_played
    def get_first_available(branch, positions):
        for position in positions:
            if position not in branch['branches']:
                branch['branches'][position] = {
                    'exhausted': False,
                    'branches': {},
                }
        for position in positions:
            if not branch['branches'][position]['exhausted']:
                return position
        return None

    def make_play(game):
        global current_branch
        available_positions = game.collect_available()
        position = get_first_available(current_branch, available_positions)
        if position is None:
            current_branch['exhausted'] = True
            position = available_positions[0]
        current_branch = current_branch['branches'][position]
        return (position[0] * 3) + position[1]
        
    for first in [HUMAN, COMPUTER]:
        root = {
            'branches': {},
            'exhausted': False,
        }
        while not root['exhausted']:
            current_branch = root
            game = Game(first_player=first, input_source=make_play)
            games_played += 1
            if game.play() == HUMAN:
                import pdb;pdb.set_trace()
            current_branch['exhausted'] = True

def play():
    g = Game()
    g.play()

if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 1:
        print "Choose 'play' or 'test'"
        sys.exit(1)
    if sys.argv[-1] == 'play':
        play()
    else:
        test()
