from gym import Env
from gym.spaces import Discrete, Box

import tensorflow as tf
import numpy as np
import random

class RoPaSci360(Env):
    def __init__(self):
        self.n_players = 2

        self.action_space = Discrete(61) # There are possible of 61 positions where the pieces can be.
        #self.observation_space = Box(-18, 18, state) # Minimum of 0 and Maximum of 18 (Upper and Lower) pieces in each state.
    def step(self):
        pass
    def render(self):
        pass
    def reset(self):
        pass