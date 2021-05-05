from rps_env_v1 import *

import tensorflow as tf

def main():
    env = RoPaSci360()
    env.reset()
    
    #empty = (0, 0, 0)
    #before = (1, 0, 0)
    #after = (3, 0, 0)

    #env.pieces = env.update(env.pieces, player = 'upper', before = empty, after = before)
    #env.pieces = env.update(env.pieces, player = 'lower', before = empty, after = after)

    #print(env.validate_move(1, 0, 59, 'lower'))
    #print({'position': [0, 1], 'symbol': 1})
    #board, reward, done, info = env.step({'position': [0, 1], 'symbol': 1})
    #print(pieces, reward, done, info)
    #print(pieces)
    #print(reward, done, info)
    
    episodes = 10
    for episode in range(1, episodes+1):
        state = env.reset()
        done = False
        score = 0 

        while not done:
            #env.render()
            action = env.action_space.sample()
            board, reward, done, info = env.step(action)
            
            score+=reward
        print(info['turn'])
        print('Episode:{} Score:{}'.format(episode, score))
        
main()
