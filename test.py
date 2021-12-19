
from brain import *
import copy

k = 1e2
n = 1e4
p = 0.1
b = 0.1
T = 10


"""
1. assembly in Concept  <-> Area <-> Stimulus
2. Area' <-> Stimulus
3. assembly in Concept <-> Area'
"""

def test_memorization_time(num_engrams, t_mem, t_recall):
    mem = Memory(k, n, p, b, T)
    mem.add_concept('Christos', num_engrams)

    stimulus = Stimulus(k, n, p, attribute='Christos')
    fiber = Fiber(n, p, b) # concept <-> area
    fiber_copy = copy.deepcopy(fiber)
    stimulus_copy = copy.deepcopy(stimulus)
    concept_winners = mem.stimulate_WM(stimulus, fiber, t_mem)
    new_concept_winners = mem.stimulate_WM(stimulus_copy, fiber_copy, t_recall)
    intersection = np.intersect1d(concept_winners, new_concept_winners)
    print(f'num_engrams={num_engrams}, t_mem={t_mem}, t_recall={t_recall}: {len(intersection)}')

num_engrams = 5
for t_mem in range(1, 21):
    for t_recall in range(1, 21):
        test_memorization_time(num_engrams=num_engrams, t_mem=t_mem, t_recall=t_recall)