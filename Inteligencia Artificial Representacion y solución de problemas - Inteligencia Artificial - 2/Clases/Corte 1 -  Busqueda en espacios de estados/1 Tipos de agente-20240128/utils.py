'''
Helper functions to gather, process and visualize data
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from seaborn import lineplot, histplot
from tqdm import tqdm
from copy import deepcopy
from time import sleep
from IPython.display import clear_output
import json

class Episode :
    '''
    Runs the environment for a number of rounds and keeps tally of everything.
    '''

    def __init__(self, environment, agent, model_name:str, num_rounds:int, id:int=0):
        self.environment = environment
        self.agent = agent
        self.model_name = model_name
        self.num_rounds = num_rounds
        self.done = False
        self.T = 1
        self.id = id
        self.sleep_time = 0.3
        state = self.environment.reset()
        self.initial_state = state
        if agent is not None:
            self.agent.restart()
            self.agent.states.append(state)

    def play_round(self, verbose:int=0):
        '''
        Plays one round of the game.
        Input:
            - verbose, to print information.
                0: no information
                1: only number of simulation
                2: simulation information
                3: simulation and episode information
                4: simulation, episode and round information
        '''
        # Ask agent to make a decision
        action = self.agent.make_decision()
        self.agent.actions.append(action)
        # Runs the environment and obtains the next_state, reward, done
        next_state, reward, done = self.environment.step(action)
        # Print info
        if verbose > 3:
            state = self.agent.states[-1]
            print(f'\tThe state is => {state}')
            print(f'\tAgent takes action => {action}')
            print(f'\tThe state obtained is => {next_state}')
            print(f'\tThe reward obtained is => {reward}')
            print(f'\tEnvironment is finished? => {done}')
            print(f'\t{self.environment.agente}, {self.environment.dir_agente}')
        self.agent.states.append(next_state)
        self.agent.rewards.append(reward)
        self.agent.dones.append(done)
        self.T += 1
        self.done = done

    def run(self, verbose:int=0):
        '''
        Plays the specified number of rounds.
        '''
        for round in range(self.num_rounds):
            if not self.done:
                if verbose > 2:
                    print('\n' + '-'*10 + f'Round {round}' + '-'*10 + '\n')
                self.play_round(verbose=verbose)                
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
        '''
        # Include las item in actions list
        self.agent.actions.append(np.nan)
        # n1 = len(self.agent.states)
        # n2 = len(self.agent.actions)
        # n3 = len(self.agent.rewards)
        # n4 = len(self.agent.dones)
        # print(n1, n2, n3, self.T)
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
        return df

    def reset(self):
        '''
        Reset the episode. This entails:
            reset the environment
            restart the agent 
                  (new states, actions and rewards, 
                   but keep what was learned)
        '''
        state = self.environment.reset()
        self.initial_state = state
        self.agent.restart()
        self.agent.states.append(state)
        self.T = 1
        self.done = False

    def renderize(self):
        '''
        Plays the specified number of rounds.
        '''
        for round in range(self.num_rounds):
            if not self.done:
                self.play_round(verbose=0)                
                clear_output(wait=True)
                self.environment.render()
                sleep(self.sleep_time)
            else:
                break
   
    def simulate(self, num_episodes:int=1, file:str=None, verbose:int=0):
        '''
        Runs the specified number of episodes for the given number of rounds.
        Input:
            - num_episodes, int with the number of episodes.
            - file, string with the name of file to save the data on.
            - verbose, to print information.
                0: no information
                1: only number of simulation
                2: simulation information
                3: simulation and episode information
                4: simulation, episode and round information
        Output:
            - Pandas dataframe with the following variables:

                Variables:
                    * id_sim: a unique identifier for the simulation
                    * round: the round number
                    * action: the player's action
                    * reward: the player's reward
                    * done: whether the environment is active or not
                    * model: the model's name
        '''
        # Create the list of dataframes
        data_frames = []
        # Run the number of episodes
        for ep in range(num_episodes):
            if verbose > 1:
                print('\n' + '='*10 + f'Episode {ep}' + '='*10 + '\n')
            # Reset the episode
            self.reset()
            self.id = ep
            # Run the episode
            df = self.run(verbose=verbose)
            # print(self.agent.Q)
            # Include episode in list of dataframes
            data_frames.append(df)
        # Concatenate dataframes
        data = pd.concat(data_frames, ignore_index=True)
        if file is not None:
            data.to_csv(file)
        return data


class Plot :
    '''
    Gathers a number of frequently used visualizations.
    '''

    def __init__(self, data:pd.DataFrame):
        self.data = data

    def plot_rewards(self, file:str=None) -> plt.axis:
        '''
        Plots the reward per episode.
        Input:
            - file, string with the name of file to save the plot on.
        Output:
            - axis, a plt object, or None.
        '''
        models = self.data.model.unique()
        vs_models = True if len(models) > 1 else False
        fig, ax = plt.subplots(figsize=(4,3.5))
        data = self.data.copy()
        if 'simulation' in data.columns:
            data = data.groupby(['model', 'simulation', 'episode'])['reward'].sum().reset_index()
        else:
            data = data.groupby(['model', 'episode'])['reward'].sum().reset_index()
        ax.set_xlabel('Episode')
        ax.set_ylabel('Total reward')
        ax.grid()
        if vs_models:
            try:
                ax = lineplot(x='episode', y='reward', hue='model', data=data, errorbar=('ci', 95))
            except:
                ax = lineplot(x='episode', y='reward', hue='model', data=data)
        else:
            try:
                ax = lineplot(x='episode', y='reward', data=data, errorbar=('ci', 95))
            except:
                ax = lineplot(x='episode', y='reward', data=data)
        if file is not None:
            plt.savefig(file, dpi=300, bbox_inches="tight")
        return ax
    
    def plot_round_reward(self, file:str=None) -> plt.axis:
        '''
        Plots the reward per round, averaged over episodes.
        Input:
            - file, string with the name of file to save the plot on.
        Output:
            - axis, a plt object, or None.
        '''
        models = self.data.model.unique()
        vs_models = True if len(models) > 1 else False
        fig, ax = plt.subplots(figsize=(4,3.5))
        ax.set_xlabel('Round')
        ax.set_ylabel('Av. Reward')
        ax.grid()
        if vs_models:
            try:
                ax = lineplot(x='round', y='reward', hue='model', data=self.data, errorbar=('ci', 95))
            except:
                ax = lineplot(x='round', y='reward', hue='model', data=self.data)
        else:
            try:
                ax = lineplot(x='round', y='reward', data=self.data, errorbar=('ci', 95))
            except:
                ax = lineplot(x='round', y='reward', data=self.data)
        if file is not None:
            plt.savefig(file, dpi=300, bbox_inches="tight")
        return ax

    def plot_histogram_rewards(self, file:str=None) -> plt.axis:
        '''
        Plots a histogram with the sum of rewards per episode.
        Input:
            - file, string with the name of file to save the plot on.
        Output:
            - axis, a plt object, or None.
        '''
        models = self.data.model.unique()
        vs_models = True if len(models) > 1 else False
        fig, ax = plt.subplots(figsize=(4,3.5))
        ax.set_xlabel('Sum of rewards')
        ax.set_ylabel('Frequency')
        ax.grid()
        if vs_models:
            try:
                df = self.data.groupby(['model', 'episode']).reward.sum().reset_index()
                ax = histplot(x='reward', hue='model', data=df, errorbar=('ci', 95))
            except:
                df = self.data.groupby(['model', 'episode']).reward.sum().reset_index()
                ax = histplot(x='reward', hue='model', data=df)
        else:
            try:
                df = self.data.groupby('episode').reward.sum().reset_index()
                ax = histplot(x='reward', data=df, errorbar=('ci', 95))
            except:
                df = self.data.groupby('episode').reward.sum().reset_index()
                ax = histplot(x='reward', data=df)
        if file is not None:
            plt.savefig(file, dpi=300, bbox_inches="tight")
        df = self.data.groupby(['model','episode']).reward.sum().reset_index()
        total_reward = df.groupby('model').reward.mean()
        print('Average sum of rewards:\n', total_reward)
        df = self.data.groupby(['model','episode']).done.sum().reset_index()
        success = df.groupby('model').done.mean()*100
        print('\nSuccess percentage:\n', success)
        return ax
    
class Experiment :
    '''
    Compares given models on a number of measures over a testsuit of environments.
    '''

    def __init__(self, \
                num_rounds:int, \
                num_episodes:int, \
                num_simulations:int=1):
        '''
        Input:
            - num_rounds, int with the number of rounds per episode.
            - num_episodes, int with the number of episodes per simulation.
            - num_simulations (optional), int with the number of times the environment should be
                restarted and run the episodes again.
        '''
        self.num_rounds = num_rounds
        self.num_episodes = num_episodes
        self.num_simulations = num_simulations
        # Reserve attribute for the test suite
        self.test_suite = []
        self.test_suite_names = []
        # Reserve attribute for generated data
        self.data = None

    def load_env(self, environment, env_name:str='Environment'):
        '''
        Loads an environment for running the experiment.
        
        Input:
            - environment, an environment object.
            - env_name (optional), a string with the environment name.
        '''
        self.test_suite = [environment]
        self.test_suite_names = [env_name]

    def load_test_suite(self, file_name:str):
        '''
        Loads an environment for running the experiment.
        
        Input:
            - file_name, the name of a file with the test suite.
        '''
        # Load test suite from file
        f = open(file_name)
        env_data = json.load(f)
        # Initialize list of environments
        environments = []
        names = []
        # Create environments from data
        for test in env_data:
            # Imports class
            exec(f'from ambientes import {test["env_class"]}')
            # Creates environment of the given class
            exec(f'env = {test["env_class"]}()')
            # Modifies environmental parameters according to data
            for parameter in test["parameters"].keys():
                value = test["parameters"].get(parameter)
                exec(f'env.{parameter} = {value}')
            # Add environment to list
            exec('environments.append(env)')
            names.append(test["name"])
        self.test_suite = environments
        self.test_suite_names = names

    def run_experiment(self, \
                       agents:list, \
                       names:list, \
                       measures:list, \
                       verbose:int=0):
        '''
        For each agent, runs the simulation the stipulated number of times,
        obtains the data and shows the plots on the given measures.
        Input:
            - agents, list of agent objects.
            - names, list of names of the models implemented by the agents.
            - measures, list of measures, which could contain the following strings:
                * 'reward'
                * 'round_reward'
                * 'histogram'
             - verbose, to print information.
                0: no information
                1: only number of simulation
                2: simulation information
                3: simulation and episode information
                4: simulation, episode and round information
        '''
        # Determines if test suite is already created/loaded
        msg = """Error: Test suite cannot be empty!
        Load a test suite from file using load_test_suite()
        or include an environment from object using load_env().
        """
        assert(len(self.test_suite)), msg
        # Creates the list of dataframes
        data_frames = []
        counter = -1
        for environment in tqdm(self.test_suite, desc='Testing agents over environment'):
            counter += 1
            # Iterate over simulations
            for k in tqdm(range(self.num_simulations), desc='\t Running simulations'):
                if verbose > 0:
                    print('\n' + '*'*10 + f' Simulation {k} ' + '*'*10 + '\n')
                # Iterate over episodes
                for ep in range(self.num_episodes):
                    # Initialize Episode
                    sim_core = Episode(environment=environment, \
                                agent=None, \
                                model_name=None,\
                                num_rounds=self.num_rounds)
                    sim_core.id = ep
                    counter_agent = -1
                    for agent in agents:
                        counter_agent += 1
                        # Copy Episode and place agent
                        sim = deepcopy(sim_core)
                        # Reset agent for new learning history
                        agent.restart()
                        sim.agent = agent
                        sim.agent.states.append(sim.initial_state)
                        sim.model_name = names[counter_agent]
                        if verbose > 0:
                            print('\n' + '%'*10 + f' Agent {names[counter_agent]} ' + '%'*10 + '\n')
                        # Run episode over agent
                        df = sim.run(verbose=False)
                        df['environment'] = self.test_suite_names[counter]
                        df['simulation'] = k
                        df['agent'] = names[counter_agent]
                        data_frames.append(df)
        # Consolidate data
        data = pd.concat(data_frames, ignore_index=True)
        self.data = data
        # Create plots
        for m in measures:
            if m == 'reward':
                ax = Plot(data).plot_rewards(m)
            if m == 'round_reward':
                ax = Plot(data).plot_round_reward(m)
            if m == 'histogram':
                ax = Plot(data).plot_histogram_rewards(m)
            try:
                ax.set_title(m)
            except:
                pass
            plt.show()

