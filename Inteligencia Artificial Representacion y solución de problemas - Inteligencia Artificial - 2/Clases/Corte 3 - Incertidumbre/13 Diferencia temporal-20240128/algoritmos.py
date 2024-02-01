import numpy as np
import random
from time import sleep
from IPython.display import clear_output

dash_line = '-'*20

def policy_eval(env, policy:np.array, gama:float=1.0, theta:float=0.01, verbose:int=0) -> np.array:
    """
    Evalúa una política para un entorno.
    Input:
        - env: transition dynamics of the environment.
            env.P[s][a] [(prob, next_state, reward, done)].
            env.nS is number of states in the environment.
            env.nA is number of actions in the environment.
        - policy: vector de longitud env.nS que representa la política
        - gama: Gamma discount factor.
        - theta: Stop iteration once value function change is
            less than theta for all states.
        - verbose: 0 no imprime nada, 
                   1 imprime la iteración del valor
    Output:
        Vector de longitud env.nS que representa la función de valor.
    """
    
    def expected_value(s:int) -> float:
        # Calcular el valor esperado as per backup diagram
        value = 0
        a = policy[s]
        for prob, next_state, reward, done in env.P[s][a]:
            value += prob * (reward + gama * V[next_state])
        return value
    
    # Start with a (all 0) value function
    V = np.zeros(env.nS)
    if verbose == 1:
        print('V; delta; check')
        print(V)
    # Stop if change is below a threshold
    continuar = True
    while continuar:
        delta = 0
        for s in range(env.nS):
            v = V[s]
            V[s] = expected_value(s)
            delta = max(delta, np.absolute(v - V[s]))
        continuar = not delta < theta
        if verbose == 1:
            print(f'{V}; {delta}; {delta < theta}')
    return V


def value_iteration(env, discount_factor=1.0, theta=0.01, verbose=0):
    """
    Mejoramiento de una política.
    Input:
        - env: OpenAI env. env.P -> transition dynamics of the environment.
            env.P[s][a] [(prob, next_state, reward, done)].
            env.nS is number of states in the environment.
            env.nA is number of actions in the environment.
        - discount_factor: Gamma discount factor.
        - theta: Stop iteration once value function change is
            less than theta for all states.
        - verbose: 0 no imprime nada, 
                   1 imprime la iteración de la política,
                   2 imprime también la iteración del valor
    Output:
        Vector de longitud env.nS que representa la política óptima.
    """ 
    
    def expected_value(s, a, env, V):
        value = 0
        # Calcular el valor esperado as per backup diagram
        for prob, next_state, reward, done in env.P[s][a]:
            value += prob * (reward + discount_factor * V[next_state])
        return value
    
    V = np.zeros(env.nS)
    continuar = True
    if verbose == 1:
        print('V; delta; continue')
        print(f'{V}; {100}; {continuar}')
    while continuar:
        delta = 0
        for s in range(env.nS):
            v = V[s]
            V[s] = np.max([expected_value(s, a, env, V) for a in range(env.nA)])
            delta = max(delta, np.absolute(v - V[s]))
        continuar = not delta < theta
        if verbose == 1:
            print(f'{V}; {delta}; {continuar}')
    policy = [np.argmax([expected_value(s, a, env, V) for a in range(env.nA)]) for s in range(env.nS)]
    return policy


def deterministic_sim(env, policy:np.array, verbose:bool=True, max_steps:int=10000) -> tuple:
    '''
    Toma un entorno y simula un episodio siguiendo 
    una política determinista.
    Se asume que el entorno puede comenzar en cualquier estado
    para implementar la suposición EXPLORING START
    Input:
        - env, un entorno en formato estándar gym
        - policy, una política determinista, policy[state] = action
        - verbose, booleano para mostrar la simulación
        - max_steps, entero con la cantidad máxima de pasos
    '''
    state = np.random.randint(env.nS)
    env.state = state
    states = [state]
    actions = []
    rewards = [np.nan]
    done = False
    counter = 0
    while not done:
        action = policy[state]
        actions.append(action)
        if verbose:
            print('')
            print(dash_line)
            print(f'\tThe state is => {state}')
            print(f'\tAgent takes action => {action}')
        state, reward, done = env.step(action)
        states.append(state)
        rewards.append(reward)
        if verbose:
            print(f'\tThe state obtained is => {state}')
            print(f'\tThe reward obtained is => {reward}')
            print(f'\tEnvironment is finished? => {done}')            
        counter += 1
        if counter > max_steps:
            break
    actions.append(np.nan)
    return states, actions, rewards


def mc_evaluation_every(env, policy:np.array, alfa:float=0.1, gama:float=1, max_iter:int=500, max_steps=1000, V:np.array=None) -> np.array:
    '''
    Método Monte Carlo libre de modelo, el cual estima el valor de los estados de     un MDP generando una muestra de episodios con base en una política dada. 
    El estimado es EVERY VISIT
    Input:
        - env, un ambiente con atributos nA, nS, shape 
               y métodos reset(), step()
        - policy, una política determinista, policy[state] = action
        - alfa, real con el parámetro de step-size
        - gama, con el parámetro de factor de descuento
        - max_iter, entero con la cantidad máxima de episodios
        - max_steps, entero con la cantidad máxima de pasos
        - Opcional: V, un np.array que por cada s devuelve su valor estimado
    Output:
        - V, un np.array que por cada s devuelve su valor estimado
    '''
    if V is None:
        V = np.zeros(env.nS)
    for _ in range(max_iter):
        states, actions, rewards = deterministic_sim(env, policy, verbose=False)
        G = 0
        for t in range(len(states)-2, -1, -1):
            state, reward = states[t], rewards[t+1]
            G = gama*G + reward
            V[state] = V[state] + alfa*(G - V[state])
    return V

def td_0_evaluation_(env, policy:np.array, alfa:float=0.1, gama:float=1, max_iter:int=500, max_steps=1000, V:np.array=None) -> np.array:
    '''
    Método de diferencia temporal para estimar el valor de los 
    estados de un MDP generando una muestra de episodios con base en una política dada. 
    Input:
        - env, un ambiente con atributos nA, nS, shape 
               y métodos reset(), step()
        - policy, una política determinista, policy[state] = action
        - alfa, real con el parámetro de step-size
        - gama, con el parámetro de factor de descuento
        - max_iter, entero con la cantidad máxima de episodios
        - max_steps, entero con la cantidad máxima de pasos
        - Opcional: V, un np.array que por cada s devuelve su valor estimado
    Output:
        - V, un np.array que por cada s devuelve su valor estimado
    '''
    if V is None:
        V = np.zeros(env.nS)
    for _ in range(max_iter):
        state = np.random.randint(env.nS)
        env.state = state
        done = False
        counter = 0
        while not done:
            action = policy[state]
            next_state, reward, done = env.step(action)
            V[state] = V[state] + alfa*(reward + gama*V[next_state] - V[state])
            state = next_state
            counter += 1
            if counter > max_steps:
                break
    return V 


def comparar_evaluacion(env, policy:np.array, alfa:float=0.1, gama:float=1, max_iter:int=1000, max_steps=1000) -> tuple:
    '''
    Toma un entorno, una política y sus valores reales y encuentra los errores
    de aproximación por episodio de los métodos MC y TD.
    Input:
        - env, un ambiente con atributos nA, nS, shape 
               y métodos reset(), step()
        - policy, una política determinista, policy[state] = action
        - alfa, real con el parámetro de step-size
        - gama, con el parámetro de factor de descuento
        - max_iter, entero con la cantidad máxima de episodios
        - max_steps, entero con la cantidad máxima de pasos    
    Output:
        - mean_mc, que es una lista con los promedios sobre la diferencia
                   en valor absoluto del valor real y el aproximado, usando el
                   método Monte Carlo, por cada episodio.
        - mean_td, que es una lista con los promedios sobre la diferencia
                   en valor absoluto del valor real y el aproximado, usando el
                   método Monte Carlo, por cada episodio.               
    '''
    # Obtain true values
    true_V = policy_eval(env, policy)
    # Initialize value estimates
    V_mc = np.zeros(env.nS)
    V_td = np.zeros(env.nS)
    # Create lists with absolute errors
    mean_mc = []
    mean_td = []
    # Iterate for each episode
    for _ in range(max_iter):
        # Find the estimate up to the episode for MC
        V_mc = mc_evaluation_every(
            env, 
            policy, 
            alfa=alfa, 
            gama=gama,
            max_iter=1,
            max_steps=max_steps,
            V = V_mc
        )
        # Include error in list
        mean_mc.append(np.mean(np.abs(V_mc - true_V)))
        # Find the estimate up to the episode for MC
        V_td = td_0_evaluation_(
            env, 
            policy, 
            alfa=alfa, 
            gama=gama,
            max_iter=1,
            max_steps=max_steps,
            V = V_td
        )
        # Include error in list
        mean_td.append(np.mean(np.abs(V_td - true_V)))
    return mean_mc, mean_td

