
import numpy as np
from numpy.random import binomial
from brain_utils import *

class Area():
    def __init__(self, n, p):
        """Brain area
        n: number of neurons in a area
        p: probability of connections
        """
        self.n = int(n)
        self.p = p
        self.connectome = binomial(1, self.p, size=(self.n, self.n)).astype(float)

class Fiber():
    def __init__(self, n, p, b, set_zero=True):
        """Brain Fiber
        n: number of neurons in each area
        p: probability of connections
        """
        self.n = int(n)
        self.p = p
        self.b = b
        self.connectome = binomial(1, self.p, size=(self.n, self.n)).astype(float)
        self.from_winners = []
        self.to_winners = []

    def get_stimulus(self, key):
        if key == 'from':
            activated = self.connectome[:, self.to_winners]
            stimulus = np.sum(activated, axis=1)
        elif key == 'to':
            activated = self.connectome[self.from_winners, :]
            stimulus = np.sum(activated, axis=0)
        return stimulus
    
    def update(self, new_winners, b, key):
        if key == 'from':
            self.from_winners = new_winners
            if len(self.to_winners) != 0:
                self.connectome[new_winners, self.to_winners] *= (1+b)
        elif key == 'to':
            self.to_winners = new_winners
            if len(self.from_winners) != 0:
                self.connectome[self.from_winners, new_winners] *= (1+b)

class Concept(Area):
    def __init__(self, n, p, attribute='None'):
        super().__init__(n, p)
        self.attribute = attribute

class Stimulus():
    def __init__(self, k, n, p, attribute='None', set_zero=False):
        """Stimulus, hard-coded search results
        k: number of neurons for the stimulus
        n: number of neurons for the stimulated area
        p: probability of connections
        name: name of the stimulus
        """
        self.k = int(k)
        self.n = int(n)
        self.p = p
        self.attribute = attribute
        self.weights = binomial(self.k, self.p, self.n).astype(float)
        if set_zero:
            self.weights = np.zeros(self.n).astype(float)
    
    def update(self, new_winners, b):
        self.weights[new_winners] *= (1+b)

class Memory():
    def __init__(self, k, n, p, b, T):
        """
        k: number of firing neurons in each step
        n: number of neurons in a area
        p: probability of connections
        b: beta for platicity updates
        T: time step to converge a assembly
        """
        self.k = int(k)
        self.n = int(n)
        self.p = p
        self.b = b
        self.T = int(T)
        self.concepts = {}
    
    def add_concept(self, attribute, n_engrams):
        concept = Concept(self.n, self.p, attribute)
        self.concepts[attribute] = concept
        stimulus = Stimulus(self.k, self.n, self.p)
        for _ in range(n_engrams):
            self.project(concept, stimulus)
        return concept
    
    def project_single_step(self, winners, area, stimulus=None, fiber_info=None):

        fiber, key = None, None
        if fiber_info is not None:
            fiber, key = fiber_info
        # calculate inputs into each of n neurons
        inputs = np.zeros(self.n)
        if stimulus is not None:
            inputs += stimulus.weights
        if fiber is not None:
            inputs += inputs + fiber.get_stimulus(key)
        inputs += np.sum(area.connectome[winners], axis=0)
        # identify top k winners 	
        new_winners = np.argsort(inputs)[-self.k:]
        if stimulus is not None:
            stimulus.update(new_winners, self.b)
        if fiber is not None:
            fiber.update(new_winners, self.b, key)
        if len(winners) != 0:
            area.connectome[winners, new_winners] *= (1+self.b)
        return new_winners

    def project(self, area, stimulus):
        winners = []
        logger = ConvergenceLogger()
        # for each time step
        for t in range(self.T):
            new_winners = self.project_single_step(winners, area, stimulus)
            # update winners
            logger.update(new_winners)
            winners = new_winners
        # print(logger.num_new_winners)

    def reciprocal_project(self, stimulus, wm_area, concept, fiber, time_step):
        
        # fiber = Fiber(self.n, self.p, self.b) # concept <-> area
        logger_area = ConvergenceLogger()
        logger_concept = ConvergenceLogger()
        wm_winners, concept_winners = [], []

        for t in range(time_step):
            new_wm_winners = self.project_single_step(
                wm_winners, wm_area, stimulus, fiber_info=(fiber, 'to'))
            fiber.to_winners = new_wm_winners
            new_concept_winners = self.project_single_step(
                concept_winners, concept, stimulus=None, fiber_info=(fiber, 'from'))
            fiber.from_winners = new_concept_winners

            logger_area.update(new_wm_winners)
            logger_concept.update(new_concept_winners)
            wm_winners = new_wm_winners
            concept_winners = new_concept_winners

        return concept_winners
        
    def stimulate_WM(self, stimulus, fiber, time_step):
        """stimulate WM
        stimulus: Stimulus instance
        time_step: number of time steps
        attribute: attribute of the new concept
        """

        if not stimulus.attribute in self.concepts.keys():
            print(f"No existing concepts found for stimulus {stimulus.attribute}.")
            return
        concept = self.concepts[stimulus.attribute]
        WM_area = Area(self.n, self.p)
        concept_winners = self.reciprocal_project(stimulus, WM_area, concept, fiber, time_step)
        return concept_winners