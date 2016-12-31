from matplotlib import pyplot
import numpy

class roll_state:
    def __init__(self, dice=[], score=0):
        self.dice = numpy.array(dice, dtype=numpy.int32)
        self.score = score
    
    def __str__(self):
        return "dice: " + str(self.dice) + " score: " + str(self.score)

def is_sequential(state):
    if len(state.dice) > 1:
        for i in range(len(state.dice[:-1])):
            if state.dice[i] + 1 != state.dice[i + 1]:
                return False
    return True

def score_runs(state):
    states = [state]
    if len(state.dice) >= 5:
        if is_sequential(state):
            states.append(roll_state([], state.score + 100*len(state.dice)))
    return states

def score_fives(state):
    states = [state]
    dice = list(state.dice)
    count = 0
    while (5 in dice) and (count < 2):
        i = dice.index(5)
        del dice[i]
        count += 1
        states.append(roll_state(dice, state.score + count*50))
    return states

def score_ones(state):
    states = [state]
    dice = list(state.dice)
    count = 0
    while (1 in dice) and (count < 2):
        i = dice.index(1)
        del dice[i]
        count += 1
        states.append(roll_state(dice, state.score + count*100))
    return states

def score_nofakind(state):
    counter = {}
    for die in state.dice:
        if die in counter:
            counter[die] += 1
        else:
            counter[die] = 1
    new_state = roll_state(state.dice, state.score)
    use_new_state = False
    for key, value in counter.items():
        if value > 2:
            use_new_state = True
            new_state.dice = [die for die in new_state.dice if die != key]
            if key == 1:
                new_state.score = new_state.score + 1000*2**(value - 3)
            else:
                new_state.score = new_state.score + 100*key*2**(value - 3)
    if use_new_state:
        return [state, new_state]
    else:
        return [state]

def get_options(state):
    states = score_runs(state)
    temp_states = []
    for state in states:
        temp_states = temp_states + score_fives(state)
    states = temp_states

    temp_states = []
    for state in states:
        temp_states = temp_states + score_ones(state)
    states = temp_states

    temp_states = []
    for state in states:
        temp_states = temp_states + score_nofakind(state)
    states = temp_states
    return states[1:]

def greedy_stgy():
    def choose_dice(state):
        states = sorted(get_options(state), key=lambda obj: obj.score)
        if len(states) > 0:
            return states[-1]
        else:
            return None
    return choose_dice

def max_dice_stgy(exp_low=49, exp_high=101, max_dice=6):
    def choose_dice(state):
        def srt(obj):
            if len(obj.dice) == 0:
                # Assume moderate score next roll
                return obj.score + exp_low*max_dice
            elif len(obj.dice) < 3:
                # Take anything
                return obj.score + exp_low*len(obj.dice)
            else:
                # Take better than 100 per die
                return obj.score + exp_high*len(obj.dice)
        states = sorted(get_options(state), key=srt)
        if len(states) > 0:
            return states[-1]
        else:
            return None
    return choose_dice

def score_cap_stgy(max_score=400):
    def stop_turn(num_dice, score):
        if score >= max_score:
            return True
        else:
            return False
    return stop_turn

def num_dice_stgy(min_dice=2):
    def stop_turn(num_dice, score):
        if num_dice <= min_dice:
            return True
        else:
            return False
    return stop_turn

def exp_gain_stgy(die_gain=100):
    def stop_turn(num_dice, score):
        if (score + die_gain*num_dice)*(1.0 - (2.0/3.0)**num_dice) < score:
            return True
        else:
            return False
    return stop_turn

def composite_stgy(min_score=400, min_dice=2):
    def stop_turn(num_dice, score):
        if (score >= min_score) and (num_dice <= min_dice):
            return True
        else:
            return False
    return stop_turn

def ncomposite_stgy(min_score=400, min_dice=2):
    def stop_turn(num_dice, score):
        if (score < min_score) or (num_dice < min_dice):
            return True
        else:
            return False
    return stop_turn

def nscore_cap_stgy(max_score=400):
    def stop_turn(num_dice, score):
        if score < max_score:
            return True
        else:
            return False
    return stop_turn

class zilch:
    def __init__(self, players, additive=True):
        # players is dict of distinct players
        self.players = players
        self.players_order = [player for player in self.players.values()]
        self.additive = additive
        self.end_condition = 10000
        self.tie_breaker = 5000
        numpy.random.shuffle(self.players_order)
    
    def play_game(self):
        roll = (None, 0) # Null roll
        end_condition = self.end_condition
        while True:
            end_game = False
            for player in self.players_order:
                if self.additive:
                    roll = player.take_turn(roll)
                else:
                    roll = player.take_turn()

                if player.score >= end_condition:
                    end_game = True
            
            if end_game:
                scores = [player.score for player in self.players_order]
                if len(scores) > 1:
                    if scores[-1] == scores[-2]:
                        end_condition += self.tie_breaker
                        continue
                        #break tie
                break
                #end game
        
        return self.players
            
class zilch_player:
    def __init__(self, num_dice = 6, strategy=None):
        self.score = 0
        self.num_dice = num_dice
        if strategy is None:
            self.strategy = (greedy_stgy(), score_cap_stgy(), num_dice_stgy())
        else:
            self.strategy = strategy
    
    def take_turn(self, roll=(None, 0)):
        if roll[0] is None:
            roll = (self.num_dice, 0)
        else:
            if self.strategy[2](roll[0], roll[1]):
                roll = (self.num_dice, 0)
    
        while True:
            roll = self.roll(roll[0], roll[1])

            if roll[0] is None:
                break
                #zilch
            
            if roll[0] == 0:
                roll = (self.num_dice, roll[1])
            
            if self.strategy[1](roll[0], roll[1]):
                break
                #scored

        self.score += roll[1]
        return roll
    
    def roll(self, num_dice, score=0):
        # num_dice random integers from 1 to 6
        dice = numpy.sort(numpy.random.randint(1, 7, (num_dice)))
        state = roll_state(dice)
        state = self.strategy[0](state)
        if state is not None:
            return len(state.dice), state.score + score
        else:
            return None, 0

data = []
for i in range(10000):
#    me = zilch_player(strategy=(max_dice_stgy(), composite_stgy(500, 2), ncomposite_stgy(1000, 2)))
    me = zilch_player(strategy=(greedy_stgy(), composite_stgy(300, 2), ncomposite_stgy(600, 2)))
    you = zilch_player(strategy=(greedy_stgy(), exp_gain_stgy(50), ncomposite_stgy(600, 2)))
    
    game = zilch({"me":me, "you":you}, additive=True)
    players = game.play_game()
    data.append([players["me"].score, players["you"].score])
#    data.append(game.play_game())

data = numpy.array(data)
data = numpy.array([1 if x>y else 0 for x, y in data])
print("me win rate: " + str(numpy.mean(data)))
print("error: " + str(numpy.std(data)/numpy.sqrt(len(data))))
