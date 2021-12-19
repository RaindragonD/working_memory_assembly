
from brain import *

k = 1e2
n = 1e4
p = 0.1
b = 0.1
T = 10

mem = Memory(k, n, p, b, T)
mem.add_concept('Christos', 1)
stimulus = Stimulus(k, n, p, attribute='Project')
print('stimulate Project')
mem.stimulate_WM(stimulus, 10)
stimulus = Stimulus(k, n, p, attribute='Christos')
print('stimulate Christos')
mem.stimulate_WM(stimulus, 30)


"""
1. assembly in Concept  <-> Area <-> Stimulus
2. Area' <-> Stimulus
3. assembly in Concept <-> Area'
"""

"""
Test 1
A stimulus presented for t1
Present the stimulus again
"""

"""
Test 2
A stimulus presented for t2
Present the stimulus again
"""

