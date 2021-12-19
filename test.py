
from brain import *

k = 1e2
n = 1e4
p = 0.1
b = 0.1
T = 10

mem = Memory(k, n, p, b, T)
mem.add_concept('Christos', 5)
stimulus = Stimulus(k, n, p, attribute='Project')
print('stimulate Project')
mem.stimulate_WM(stimulus, 10)
stimulus = Stimulus(k, n, p, attribute='Christos')
print('stimulate Christos')
mem.stimulate_WM(stimulus, 10)


"""
Test 1
A stimulus presented consistently
Expect readout to find the created concept 
linked to the concepts presecribed by the stimulus
"""

"""
Test 2
A stimulus presented consistently
Provide the stimulus again
Expect the newly formed concept to fire
"""

"""
Test 3
A stimulus presented shortly
Don't expect the stimulus to converge
or link correctly to the concepts presecribed by the stimulus
"""

"""
Test 4
A stimulus presented shortly
Provide the stimulus again
Expect the newly formed concept to fire
"""
