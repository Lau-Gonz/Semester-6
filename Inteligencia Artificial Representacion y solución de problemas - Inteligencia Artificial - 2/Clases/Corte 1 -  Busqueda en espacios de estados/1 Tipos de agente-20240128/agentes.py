import numpy as np
import random

class Agent :
    '''
    Defines the basic methods for the agent.
    '''

    def __init__(self):
        self.plan = []
        self.states = []
        self.actions = []
        self.rewards = [np.nan]
        self.dones = [False]
        self.turn = 0

    def make_decision(self):
        '''
        Agent makes a decision according to its model.
        '''
        # Chequeamos si ya el agente no tiene un plan (lista de acciones)
        if len(self.plan) == 0:
            # Usamos el programa para crear un plan
            self.program()
        try:
            # La acción a realizar es la primera del plan
            action = self.plan.pop(0)
        except:
            # ¡No hay plan!
            state = self.states[-1]
            raise Exception(f'¡Plan vacío! Revisar reglas en estado {state}')
        self.turn += 1
        return action

    def program(self):
        '''
        Debe ser modificada por cada subclase
        '''
        pass

    def reset(self):
        self.restart()

    def restart(self):
        '''
        Restarts the agent for a new trial.
        '''
        self.plan = []
        self.states = []
        self.actions = []
        self.rewards = [np.nan]
        self.dones = [False]
        self.turn = 0


class Random(Agent):
    '''Agente que deambula aleatoriamente.'''
    def __init__(self):
        super().__init__()
        self.choices = ['voltearIzquierda', 'voltearDerecha', 'adelante']

    def program(self):
        # Creamos un plan con una acción aleatoria
        self.plan.append(random.choice(self.choices))


class TableDriven(Agent):
    '''Agente con un programa basado en una tabla.'''
    def __init__(self):
        super().__init__()
        self.tabla = {}

    def program(self):
        state = self.states[-1]
        try:
            # Obtenemos un plan de la tabla
            self.plan += self.tabla[tuple(state)]
        except:
            raise Exception(f'¡Tabla incompleta! No contempla el estado {state}')
        

class RuleBased(Agent):
    '''Agente con un programa que implementa reglas condición-acción.'''
    def __init__(self):
        super().__init__()
        self.reglas = {}

    def program(self):
        state = self.states[-1]
        for antecedente in self.reglas:
            if eval(antecedente):
                # Obtenemos un plan con la primera regla
                # cuyo antecedente evalúe verdadero
                self.plan += self.reglas[antecedente]
                break

    