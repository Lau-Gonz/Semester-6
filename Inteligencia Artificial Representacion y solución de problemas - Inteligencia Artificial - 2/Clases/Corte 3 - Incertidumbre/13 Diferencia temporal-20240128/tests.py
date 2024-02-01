import numpy as np

def test_sarsa(agent:any) -> bool:
    agent.Q = np.array([[ -5.50820817,  -5.38453973,  -5.75821615,  -5.38624223],
       [ -4.78456803,  -4.57387003,  -5.69896813,  -4.65687427],
       [ -3.84345967,  -3.84534566,  -4.88739752,  -3.85821414],
       [ -2.82845878,  -2.88324432,  -2.23066851,  -3.41999235],
       [ -6.37178089,  -6.93428985, -10.01180627,  -7.06062573],
       [ -3.23425315,  -3.10335906, -40.951     ,  -3.17813105],
       [ -1.94690502,  -2.04937362, -19.        ,  -2.02652624],
       [ -1.43285233,  -1.88781884,  -0.9998955 ,  -4.82076797],
       [ -7.57089976, -46.8559    ,  -9.8676952 ,  -7.85099899],
       [  0.        ,   0.        ,   0.        ,   0.        ],
       [  0.        ,   0.        ,   0.        ,   0.        ],
       [  0.        ,   0.        ,   0.        ,   0.        ]])
    agent.seed = 0
    agent.debug = True
    action = 1
    agent.actions.append(action)
    state = 4
    agent.states.append(state)
    next_action = agent.make_decision()
    next_state = 5
    reward = -1
    done = False
    agent.update(next_state, reward, done)
    test_value = agent.Q[state, action]
    return np.isclose(test_value, -10.43596)

def test_q(agent:any) -> bool:
    agent.Q = np.array([[ -5.50820817,  -5.38453973,  -5.75821615,  -5.38624223],
       [ -4.78456803,  -4.57387003,  -5.69896813,  -4.65687427],
       [ -3.84345967,  -3.84534566,  -4.88739752,  -3.85821414],
       [ -2.82845878,  -2.88324432,  -2.23066851,  -3.41999235],
       [ -6.37178089,  -6.93428985, -10.01180627,  -7.06062573],
       [ -3.23425315,  -3.10335906, -40.951     ,  -3.17813105],
       [ -1.94690502,  -2.04937362, -19.        ,  -2.02652624],
       [ -1.43285233,  -1.88781884,  -0.9998955 ,  -4.82076797],
       [ -7.57089976, -46.8559    ,  -9.8676952 ,  -7.85099899],
       [  0.        ,   0.        ,   0.        ,   0.        ],
       [  0.        ,   0.        ,   0.        ,   0.        ],
       [  0.        ,   0.        ,   0.        ,   0.        ]])
    agent.seed = 0
    agent.debug = True
    action = 1
    agent.actions.append(action)
    state = 4
    agent.states.append(state)
    next_action = agent.make_decision()
    next_state = 5
    reward = -1
    done = False
    agent.update(next_state, reward, done)
    test_value = agent.Q[state, action]
    return np.isclose(test_value, -6.65119)