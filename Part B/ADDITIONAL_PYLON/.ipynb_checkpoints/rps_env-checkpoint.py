from gym import Env
from gym.spaces import Discrete, Box

from state import *
import tensorflow as tf
import numpy as np
import random

INVALID_ACTION_REWARD = -10
VALID_ACTION_REWARD = 10
WIN_REWARD = 100
LOSS_REWARD = -100
EAT_TOKEN = 10

class RoPaSci360(Env):
    def __init__(self,
                player = 'upper',
                opponent = 'random',
                log = 'True'):
        
        # Constants
        self.max_turns = 360
        self.log = log
                
        #
        # Observation + Action spaces
        # ---------------------------
        #  Observations: RoPaSci board containing 61 hexes, with 9 types of maximum number of tokens for each player.
        #  Actions: (Every board position) * (Every board position)
        #
        # Note: not every action is legal
        #
        self.action_space = Discrete(61 * 61)
        self.observation_space = Box(-9, 9, 61)
        
        self.player = player
        self.opponent = opponent
        
        # reset and build state
        self.reset()
        
    def reset(self):
        self.state = GameState()
        self.state.turn_number = 0
        self.state.game_state = 'running'
        self.state.upper_inv = 0
        self.state.lower_inv = 0
        
        self.upper = list()
        self.lower = list()
        self.upper_throws = 9
        self.upper_throws = 9
                
        return self.state
        
    def step(self, action):
        assert self.action_space.contains(action), "ACTION ERROR {}".format(action)
        
        
    def render(self):
        pass
    