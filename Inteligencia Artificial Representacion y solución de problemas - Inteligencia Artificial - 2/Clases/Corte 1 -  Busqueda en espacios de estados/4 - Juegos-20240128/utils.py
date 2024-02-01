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
        self.state = state
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
        # Make sure agent has the appropriate possible actions
        if hasattr(self.agent, 'choices'):
            try:
                possible_actions = self.environment.acciones_aplicables(self.state)
                self.agent.choices = possible_actions
            except Exception as e:
                print('Warning: Agent requires uptade of possible actions but environment did not provide them!')
                pass
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
        self.agent.states.append(next_state)
        self.agent.rewards.append(reward)
        self.agent.dones.append(done)
        self.state = next_state
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
        self.state = state
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
            df = self.data.groupby(['model', 'episode']).reward.sum().reset_index()
            try:
                ax = histplot(x='reward', hue='model', data=df, errorbar=('ci', 95))
            except:
                ax = histplot(x='reward', hue='model', data=df)
        else:
            df = self.data.groupby('episode').reward.sum().reset_index()
            try:
                ax = histplot(x='reward', data=df, errorbar=('ci', 95))
            except:
                ax = histplot(x='reward', data=df)
        if file is not None:
            plt.savefig(file, dpi=300, bbox_inches="tight")
        df = self.data.groupby(['model','episode']).reward.sum().reset_index()
        total_reward = df.groupby('model').reward.mean()
        print('Average sum of rewards:\n', total_reward)
        df = self.data.groupby(['model','episode']).done.sum().reset_index()
        success = df.groupby('model').done.mean()*100
        print('\nEpisode termination percentage:\n', success)
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
        Loads a test suit of environments for running the experiment.
        
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

    def load_game_test_suite(self, other_player:any, file_name:str):
        '''
        Loads a test suite of games and creates the environments for running the experiment.
        
        Input:
            - other_player, the other player to create an environment from.
            - file_name, the name of a file with the test suite.
        '''
        # Load game test suite from file
        f = open(file_name)
        game_data = json.load(f)
        # Load requirements
        reqs = game_data["reqs"]
        for req in reqs:
            exec(req)
        # Initialize list of environments
        environments = []
        names = []
        # Create environments from data
        for test in game_data["games"]:
            # Imports class
            exec(f'from juegos import {test["game_class"]}')
            # Creates game of the given class
            exec(f'game = {test["game_class"]}()')
            # Modifies game parameters according to data
            for parameter in test["parameters"].keys():
                value = test["parameters"].get(parameter)
                exec(f'game.{parameter} = {value}')
            # Creates environment of the given class
            exec('other_player.game = game')
            exec(f'env = EnvfromGameAndPl2(game,other_player)')
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
        # Creates empty list of dataframes
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
                    sim_core.id = counter * self.num_rounds + ep
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


class EnvfromGameAndPl2:
    '''
    Implementa un entorno a partir de un juego y del segundo jugador.
    '''
    def __init__(self, game:any, other_player:any):
        self.other_player = other_player
        self.initial_game = deepcopy(game)
        self.game = game
        self.state = self.game.estado_inicial

    def reset(self):
        self.game = deepcopy(self.initial_game)
        self.state = self.game.estado_inicial
        self.other_player.reset()
        self.other_player.states.append(self.state)
        return self.state

    def render(self):
        self.game.render(self.state)

    def test_objetivo(self, state):
        if not self.game.es_terminal(state):
            return False
        else:
            player = self.game.player(state)
            return self.utilidad(state, player) > 0
        
    def acciones_aplicables(self, state):
        return self.game.acciones(state)

    def step(self, action):
        state = self.state
        playing = self.game.player(state)
        # print(f'player {playing} in state {state} makes move {action}')
        # First player made a move. Get new state, reward, done
        try:
            new_state = self.game.resultado(state, action)
        except Exception as e:
            print(state)
            raise Exception(e)
        # print(f'obtains {new_state}')
        reward = self.game.utilidad(new_state, playing)
        reward = reward if reward is not None else 0
        done = self.game.es_terminal(new_state)
        # If not done, second player makes a move
        if not done:
            playing = self.game.player(new_state)
            # Actualize second player with previous move
            self.other_player.states.append(new_state)
            if hasattr(self.other_player, 'choices'):
                possible_actions = self.game.acciones(new_state)
                self.other_player.choices = possible_actions
            # Second player makes a move
            other_player_action = self.other_player.make_decision()
            if self.other_player.debug:
                print(f'Negras mueven en {other_player_action}')
            # print(f'player {playing} in state {new_state} makes move {other_player_action}')
            # Get new state, reward, done
            new_state = self.game.resultado(new_state, other_player_action)
            # print(f'obtains {new_state}')
            reward = self.game.utilidad(new_state, playing)
            reward = reward if reward is not None else 0
            done = self.game.es_terminal(new_state)
        # Bookkeeping
        self.state = new_state
        return new_state, reward, done   