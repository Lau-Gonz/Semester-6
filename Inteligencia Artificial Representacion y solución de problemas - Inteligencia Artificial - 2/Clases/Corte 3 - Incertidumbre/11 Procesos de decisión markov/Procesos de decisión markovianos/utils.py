'''
Helper functions to gather, process and visualize data
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from seaborn import lineplot, histplot, heatmap, color_palette
from tqdm.auto import tqdm
from copy import deepcopy
from time import sleep
from IPython.display import clear_output, display
import json
from gymnasium.utils.save_video import save_video
from typing import Union, List

def id_state(state):
    '''
    Default interpreter: do nothing.
    '''
    return state

def gym_interpreter1(state):
    '''
    Cleans the state and get only the state space.
    When states come from gymnasium, they contain 
    additional info besides the state space.
    '''
    if isinstance(state, tuple):
        if isinstance(state[1], dict):
            state = state[0]
        else:
            state = state
    else:
        state = state
    return state

class Episode :
    '''
    Runs the environment for a number of rounds and keeps tally of everything.
    '''

    def __init__(self, 
                 environment:any,
                 env_name:str, 
                 agent:any, 
                 model_name:str, 
                 num_rounds:int, 
                 id:int=0,
                 state_interpreter=id_state) -> None:
        self.environment = environment
        self.env_name = env_name
        self.agent = agent
        self.model_name = model_name
        self.num_rounds = num_rounds
        self.done = False
        self.T = 1
        self.id = id
        self.sleep_time = 0.3
        self._clean_state = state_interpreter
        state_ = self.environment.reset()
        state = self._clean_state(state_)
        self.initial_state = state
        if agent is not None:
            self.agent.restart()
            self.agent.states.append(state)

    def play_round(self, verbose:int=0, learn:bool=True) -> None:
        '''
        Plays one round of the game.
        Input:
            - verbose, to print information.
                0: no information
                1: only number of simulation
                2: simulation information
                3: simulation and episode information
                4: simulation, episode and round information
            - learn, a boolean to determine if agent learning is enabled.
        '''
        # Ask agent to make a decision
        try:
            action = self.agent.make_decision()
        except Exception as e:
            raise Exception('Oh oh', e)
        # Update records
        self.agent.actions.append(action)
        # Runs the environment and obtains the next_state, reward, done, info
        result = self.environment.step(action)            
        next_state = self._clean_state(result[0])
        reward = result[1]
        done = result[2]
        # Prints info
        if verbose > 3:
            state = self.agent.states[-1]
            print(f'\tThe state is => {state}')
            print(f'\tAgent takes action => {action}')
            print(f'\tThe state obtained is => {next_state}')
            print(f'\tThe reward obtained is => {reward}')
            print(f'\tEnvironment is finished? => {done}')
        # Agent learns
        if learn:
            # truncated = self.T >= self.num_rounds
            self.agent.update(next_state, reward, done)
        # Update records
        self.agent.states.append(next_state)
        self.agent.rewards.append(reward)
        self.agent.dones.append(done)
        # Update round counter
        self.T += 1
        # Update environment "is-finished?"
        self.done = done

    def run(self, verbose:int=0, learn:bool=True) -> pd.DataFrame:
        '''
        Plays the specified number of rounds.
        Input:
            - verbose, to print information.
                0: no information
                1: only number of simulation
                2: simulation information
                3: simulation and episode information
                4: simulation, episode and round information
            - learn, a boolean to determine if agent learning is enabled.
        '''
        for round in range(self.num_rounds):
            if not self.done:
                if verbose > 2:
                    print('\n' + '-'*10 + f'Round {round}' + '-'*10 + '\n')
                self.play_round(verbose=verbose, learn=learn)                
            else:
                break
        return self.to_pandas()

    def to_pandas(self) -> pd.DataFrame:
        '''
        Creates a pandas dataframe with the information from the current objects.
        Output:
            - pandas dataframe with the following variables:           
                Variables:
                    * episode: a unique identifier for the episode
                    * round: the round number
                    * action: the player's action
                    * reward: the player's reward
                    * done: whether the environment is active or not
                    * model: the model's name
                    * environment: the environment's name
        '''
        # Include las item in actions list
        self.agent.actions.append(np.nan)
        # n1 = len(self.agent.states)
        # n2 = len(self.agent.actions)
        # n3 = len(self.agent.rewards)
        # n4 = len(self.agent.dones)
        # print(n1, n2, n3, n4, self.T)
        data = {}
        data["episode"] = []
        data["round"] = []
        data["state"] = []
        data["action"] = []
        data["reward"] = []
        data["done"] = []
        for r in range(self.T):
            data["episode"].append(self.id)
            data["round"].append(r)
            data["state"].append(self.agent.states[r])
            data["action"].append(self.agent.actions[r])
            data["reward"].append(self.agent.rewards[r])
            data["done"].append(self.agent.dones[r])
        df = pd.DataFrame.from_dict(data)        
        df["model"] = self.model_name
        df["environment"] = self.env_name
        return df

    def reset(self) -> None:
        '''
        Reset the episode. This entails:
            reset the environment
            restart the agent 
                  (new states, actions and rewards, 
                   but keep Q and policy)
        '''
        state = self.environment.reset()
        state = self._clean_state(state)
        self.agent.restart()
        self.agent.states.append(state)
        self.T = 1
        self.done = False

    def renderize(self, to_video:bool=False, file:str=None) -> None:
        '''
        Plays the specified number of rounds.
        '''
        if to_video:
            assert(file is not None), 'A folder name must be provided with the argument file='
            rm = self.environment.render_mode
            assert(rm == 'rgb_array'), f'To create video, environment render mode should be rgb_array, not {rm}'
            frame_list = []
        # Initialize img object
        img = plt.imshow(np.array([[0, 0], [0, 0]]))
        for round in range(self.num_rounds):
            if not self.done:
                im = self.environment.render()
                if isinstance(im, np.ndarray):
                    if to_video:
                        frame_list.append(im)
                    img.set_data(im)
                    plt.axis('off')
                    display(plt.gcf())
                sleep(self.sleep_time)
                clear_output(wait=True)
                self.play_round(verbose=0, learn=False)                
            else:
                clear_output(wait=True)
                im = self.environment.render()
                if isinstance(im, np.ndarray):
                    if to_video:
                        frame_list.append(im)
                    img.set_data(im)
                    plt.axis('off')
                    display(plt.gcf())
                break
        if to_video:
            assert(len(frame_list) > 0), 'No frames saved. Check env.render() is providing np.ndarrays.'
            save_video(
                frames=frame_list,
                video_folder=file,
                fps=1/self.sleep_time
            )
