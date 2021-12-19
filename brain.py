
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
        self.connectome = binomial(1, self.p, size=(self.n, self.n))

class Fiber():
    def __init__(self, n, p, b):
        """Brain Fiber
        n: number of neurons in each area
        p: probability of connections
        """
        self.n = int(n)
        self.p = p
        self.b = b
        self.connectome = binomial(1, self.p, size=(self.n, self.n))
    
    def update_winners(self, winners):
        self.winners = winners

    def get_stimulus(self, winners):
        activated = self.connectome(winners)
        stimulus = np.sum(activated, axis=0)
        return stimulus
    
    def update_weights(self, target_winners):
        for i in self.winners:
            for j in target_winners:
                self.connectome[i][j] *= (1+self.b)

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
        self.weights = binomial(self.k, self.p, self.n)
        if set_zero:
            self.weights = np.zeros(self.n).astype(float)

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
        for _ in range(n_engrams):
            stimulus = Stimulus(self.k, self.n, self.p)
            self.project(concept, stimulus)
        return concept
    
    def project_single_step(self, winners, area, stimulus, area_stimulus=None):
        # calculate inputs into each of n neurons
        inputs = np.copy(stimulus.weights)
        if area_stimulus is not None:
            inputs = inputs + area_stimulus.weights
        for i in winners:
            for j in range(self.n):
                inputs[j] += area.connectome[i][j]
        # identify top k winners 	
        new_winners = np.argsort(inputs)[-self.k:]
        for i in new_winners:
            stimulus.weights[i] *= (1+self.b)
            if area_stimulus is not None:
                area_stimulus.weights[i] *= (1+self.b)
        # plasticity: for winners, for previous winners, update edge weight
        for i in winners:
            for j in new_winners:
                area.connectome[i][j] *= (1+self.b)
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

    def reciprocal_project(self, stimulus, wm_area, concept, time_step):

        connectome_area_to_concept = Stimulus(self.n, self.n, self.p)
        connectome_concept_to_area = Stimulus(self.n, self.n, self.p, set_zero=True)
        logger_area = ConvergenceLogger()
        logger_concept = ConvergenceLogger()
        wm_winners, concept_winners = [], []

        for t in range(time_step):
            new_wm_winners = self.project_single_step(
                wm_winners, wm_area, stimulus, connectome_concept_to_area)
            new_concept_winners = self.project_single_step(
                concept_winners, concept, connectome_area_to_concept)
            logger_area.update(new_wm_winners)
            logger_concept.update(new_concept_winners)
            wm_winners = new_wm_winners
            concept_winners = new_concept_winners
        print(logger_area.num_new_winners)
        print(logger_concept.num_new_winners)
        
    def stimulate_WM(self, stimulus, time_step):
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
        self.reciprocal_project(stimulus, WM_area, concept, time_step)