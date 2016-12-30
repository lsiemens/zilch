from matplotlib import pyplot
import numpy

class roll_state:
    def __init__(self, dice=[], score=0):
        self.dice = numpy.array(dice, dtype=numpy.int32)
        self.score = score
    
    def __str__(self):
        return "dice: " + str(self.dice) + " score: " + str(self.score)

def score_runs(state):
    states = [state]
    if len(state.dice) == 5:
        if numpy.array_equal(state.dice, numpy.arange(1, 6)):
            states = [roll_state([], state.score + 500)]
    if len(state.dice) == 6:
        if numpy.array_equal(state.dice, numpy.arange(1, 7)):
            states = [roll_state([], state.score + 600)]
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

def max_dice_stgy(exp_low=49, exp_high=101):
    def choose_dice(state):
        def srt(obj):
            if len(obj.dice) < 3:
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

#min 600 pts then down to 2 die

class player:
    def __init__(self, num_dice = 6, strategy=None):
        self.score = 0
        self.num_dice = num_dice
        if strategy is None:
            self.strategy = (greedy_stgy(), score_cap_stgy())
        else:
            self.strategy = strategy
    
    def take_turn(self):
        roll = (self.num_dice, 0)
        while roll[0] is not None:
            max_score = roll[1]
            if roll[0] == 0:
                num_dice = self.num_dice
            else:
                num_dice = roll[0]
            
            if self.strategy[1](num_dice, roll[1]):
                break

            roll = self.roll(num_dice, roll[1])
        return roll[1]
    
    def roll(self, num_dice, score=0):
        # num_dice random integers from 1 to 6
        dice = numpy.sort(numpy.random.randint(1, 7, (num_dice)))
        state = roll_state(dice)
        state = self.strategy[0](state)
        if state is not None:
            return len(state.dice), state.score + score
        else:
            return None, 0

d = []
b = numpy.arange(40, 140, 1)

for j in b:
    me = player(strategy=(greedy_stgy(), exp_gain_stgy(j)))
    data = numpy.array([me.take_turn() for i in range(100000)])
    
    print("num die: " + str(j))
    print(numpy.mean(data))
    d.append(numpy.mean(data))
    print(numpy.std(data, ddof=0)/numpy.sqrt(len(data)))
    print(numpy.std(data, ddof=0))
    print(data.max())
    print("")
    
    #bins = numpy.arange(-25, data.max()*2/3.0, 50)
    #f, (ax1, ax2) = pyplot.subplots(2, 1, sharex=True)
    
    #hist, bins2 = numpy.histogram(data, bins=bins, density=True)
    #ax1.bar(bins2[:-1], hist*50.0, numpy.diff(bins2))
    #ax2.hist(data, bins=bins, normed=True, cumulative=True)
    #pyplot.show(f)
    
pyplot.plot(b, d)
pyplot.show()    
