"""
Learning Engine visualizer, each implementation of the class will represent its inner state using matplotlib
Everytime, when the inner state changes, visualizer's update function could be called to change the front end
representation.
"""
import matplotlib.pyplot as plt
import time
import numpy as np
import matplotlib.mlab as mlab
import math

class ScVisualizer(object):
    """
    supports only one instance running at a time
    """
    # dimension of the figure can't be changed once the program runs.
    def __init__(self, scmodel, tp_dim=(10, 3), ylim=0.01):
        # every visualizer contains a window drawn in matplotlib
        self.scmodel = scmodel
        self.figure = plt.figure(figsize=tp_dim)
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.ylim = ylim
    def draw(self):
        """
        Update the plt's inner states and flush changes
        """
        self.axis.cla() # clear board
        self.update()
        self.axis.set_ylim([0, self.ylim])
        # flush board
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        # controlling frame rate ( Necessary!!! )
        plt.pause(0.001)

    def update(self):
        """
        Define updating graphics based on scmodel
        """
        raise NotImplementedError()

class ScVisualizerTest(ScVisualizer):
    """
    Testing visualizer
    """
    # overriding
    def update(self):
        num_mu = self.scmodel.mu
        # compute sigma
        num_sigma = math.sqrt(self.scmodel.var)
        array_x = np.linspace(num_mu - 3*num_sigma,num_mu + 3*num_sigma,100)
        array_y = mlab.normpdf(array_x,num_mu,num_sigma)
        self.axis.fill_between(array_x, array_y)
        self.axis.plot(array_x, array_y)

class ScModelTest():
    """
    Testing Model
    """
    def __init__(self):
        self.mu = 0
        self.var = 1
    
    def iterate(self):
        self.mu += 0.1
        self.var += 0.1

class ScVisualizerBayes(ScVisualizer):
    """
    Bayes visualizer
    """
    def plotState(self, state, f_color=False):
        """
        Plot a state to the screen
        """
        num_mean = state.mean
        num_sigma = state.std
        if num_sigma == 0:
            # this is just for hacking
            plt.plot([num_mean, num_mean], [0, self.ylim])
            return
        arr_x = np.linspace(num_mean-5*num_sigma, num_mean+5*num_sigma, 100)
        # normpdf uses mu, sigma for normal distribution function
        # to produce the y axis for x
        # should I consider prior?
        arr_y = mlab.normpdf(arr_x, num_mean, num_sigma)
        if f_color:
            self.axis.fill_between(arr_x, arr_y)
        self.axis.plot(arr_x, arr_y)

    # override
    def update(self):
        # get the normal distribution states
        rg_state = self.scmodel.states
        rg_state_minor = self.scmodel.minor_states
        for id_state in rg_state:
            # if a state is major mode, then we color the shade under curve.
            self.plotState(rg_state[id_state], True)
        for id_state in rg_state_minor:
            self.plotState(rg_state_minor[id_state])

def main():
    scm = ScModelTest()
    scv = ScVisualizerTest(scm, (10, 4))
    scv.draw()
    for i in xrange(0, 200):
        scm.iterate()
        scv.draw()
        time.sleep(0.01)

if __name__ == "__main__":
    main()
