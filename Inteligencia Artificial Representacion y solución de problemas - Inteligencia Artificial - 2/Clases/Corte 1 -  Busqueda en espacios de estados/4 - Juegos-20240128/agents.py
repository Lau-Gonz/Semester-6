import numpy as np
import random
from juegos import ReyTorreRey
import regex as re
from datastruct import ArbolBusquedaJuego
from IPython.display import display, clear_output
from time import sleep


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
    def __init__(self, choices:list):
        super().__init__()
        self.choices = choices

    def program(self):
        # Creamos un plan con una acción aleatoria
        accion = random.choice(self.choices)
        self.plan.append(accion)


class PlfromAlgo(Agent) :
    '''
    Agente creado a partir de algoritmo (p.ej., minimax, alpha-search, etc.)
    '''
    def __init__(self, algorithm:any):
        super().__init__()
        self.algorithm = algorithm

    def program(self):
        state = self.states[-1]
        # El agente toma una acción de acuerdo al algoritmo
        action = self.algorithm(state)
        self.plan.append(action)


class ChessFinalist1(Agent):
    '''
    Agente para enfrentarse a final rey y torre contra rey solitario.
    Utiliza alfa-beta con cutoff y funciones de evaluación.
    '''
    def __init__(self, game:ReyTorreRey, jugador:str='blancas', max_lim:int=2, pesos:list=[1,1,1,1]):
        super().__init__()
        # El juego debe ser un juego de ajedrez ReyTorreRey
        self.game = game
        # El jugador puede ser 'blancas' o 'negras'
        self.jugador = jugador
        self.max_lim = max_lim
        # Pesos define la relevancia de las evaluaciones. En orden
        # las evaluaciones son:
        #       - Oposición de los reyes
        #       - Material
        #       - Rey negro en el borde
        #       - Rectángulo
        self.dict_material = {'K':9, 'R':5, 'k':-9}
        self.pesos = pesos
        self.debug = False

    def program(self):
        state = self.states[-1]
        # El agente toma una acción de acuerdo al alfa-beta con cutoff
        v, action = self._H_minimax_alfa_beta(state, 0, -np.infty, np.infty)
        # v, action = self._minimax_search(state)
        self.plan.append(action)

    def _minimax_search(self, estado):
        jugador = self.game.player(estado)
        # Determina cuál jugador tiene el turno
        if jugador == 'blancas':        
            valor, accion = self._max_value(estado, 0)
        else: # Juegan las O (MIN)
            valor, accion = self._min_value(estado, 0)
        if self.debug:
            print('\n')
            print('='*10)
            print(f'{jugador} juega en {accion} con valor {valor}')
            print('='*10)
        return valor, accion
    
    def _max_value(self, estado, d):
        jugador = self.game.player(estado)
        if self.debug:
            print('\n')
            print('='*10)
            print('\t'*d + jugador)
            print(f'Profundidad:{d}, ¿cutoff?:{self._is_cutoff(estado, d)} ({d}>={self.max_lim}?)')
            print('='*10)
        if self._is_cutoff(estado, d):
            return self._evaluar(estado), None
        v = -np.infty
        acciones = self.game.acciones(estado)
        if self.debug:
            print(estado)
            print(f'Acciones posibles: {[str(a) for a in acciones]}')
        for a in acciones:
            v2, a2 = self._min_value(self.game.resultado(estado, a), d+1)
            if self.debug:
                print(a, v2)
            if v2 > v:
                v = v2
                accion = a
        return v, accion

    def _min_value(self, estado, d):
        jugador = self.game.player(estado)
        if self.debug:
            print('\n')
            print('='*10)
            print('\t'*d + jugador)
            print(f'Profundidad:{d}, ¿cutoff?:{self._is_cutoff(estado, d)} ({d}>={self.max_lim}?)')
            print('='*10)
        if self._is_cutoff(estado, d):
            return self._evaluar(estado), None
        v = np.infty
        acciones = self.game.acciones(estado)
        if self.debug:
            print(estado)
            print(f'Acciones posibles: {[str(a) for a in acciones]}')
        for a in acciones:
            v2, a2 = self._max_value(self.game.resultado(estado, a), d+1)
            if self.debug:
                print(a, v2)
            if v2 < v:
                v = v2
                accion = a
        return v, accion

    def _H_minimax_alfa_beta(self, estado, d, alfa, beta):
        jugador = self.game.player(estado)
        if self.debug:
            print('\n')
            print('='*10)
            print('\t'*d + jugador)
            print(f'Profundidad:{d}, ¿cutoff?:{self._is_cutoff(estado, d)} ({d}>={self.max_lim}?)')
            print('='*10)
        if self._is_cutoff(estado, d):
            return self._evaluar(estado), None
        elif jugador == 'blancas':
            v = -np.infty
            for a in self.game.acciones(estado):
                board_resultado = self.game.resultado(estado, a)
                v2, a2 = self._H_minimax_alfa_beta(board_resultado, d+1, alfa, beta)
                if self.debug:
                    print(a, v2)
                if v2 > v:
                    v = v2
                    accion = a
                    alfa = max(alfa, v)
                if v >= beta:
                    if self.debug:
                        print('prunning beta...', a)
                    return v, accion
            return v, accion
        elif jugador == 'negras':
            v = np.infty
            for a in self.game.acciones(estado):
                board_resultado = self.game.resultado(estado, a)
                v2, a2 = self._H_minimax_alfa_beta(board_resultado, d+1, alfa, beta)
                if self.debug:
                    print(a, v2)
                if v2 < v:
                    v = v2
                    accion = a
                    beta = min(beta, v)
                if v <= alfa:
                    if self.debug:
                        print('prunning alfa...', a)
                    return v, accion
            return v, accion
        else:
            raise NameError(f"Oops! player={jugador}")  
               
    def _evaluar(self, estado):
        jugador_ = self.game.player(estado)
        if self.debug:
            print('Juega --->', jugador_)
        jugador = self._otro_jugador(jugador_)
        if self.game.es_terminal(estado):
            return self.game.utilidad(estado, jugador)
        if jugador == 'blancas':
            pesos = self.pesos
        elif jugador == 'negras':
            # El jugador negro solo debería tratar de estar en el centro
            pesos = [0,1,0,1]
        else:
            raise Exception(f'Oops! player={jugador}')
        valores = [
                    self._oposicion(estado),\
                    self._material(estado),\
                    self._rectangulo(estado),\
                    self._rey_borde(estado),\
                    ]
        evaluacion = np.dot(pesos, valores)
        if self.debug:
            print(pesos, valores)
            print(estado)
            print('evaluador', jugador, '->', evaluacion)
        return evaluacion 

    def _oposicion(self, estado):
        # Contamos oposición
        fila_rey_blanco, columna_rey_blanco = self._casilla_pieza(estado, 'K')
        fila_rey_negro, columna_rey_negro = self._casilla_pieza(estado, 'k')
        distancia_fila = np.abs(fila_rey_blanco - fila_rey_negro)
        distancia_columna = np.abs(columna_rey_blanco - columna_rey_negro)
        if distancia_fila == 0:
            oposicion = distancia_columna - 2
        elif distancia_columna == 0:
            oposicion = distancia_fila - 2
        else:
            oposicion = distancia_fila + distancia_columna
        return 10 * np.exp(-oposicion)

    def _material(self, estado):
        # Contamos material
        piezas = re.findall(r"[\w]+", str(estado))
        piezas = [self.dict_material[p] for p in piezas]
        material = np.sum(piezas)
        return material
    
    def _rectangulo(self, estado):
        # Contamos el área del rectánguno creado por la torre
        # y que rodea al rey negro
        pass
        # ----------------------------------------------------------
        # Este método se implementa como un ejericio en el notebook.
        # ----------------------------------------------------------
        return 0
    
    def _rey_borde(self, state):
        # Contamos rey negro en borde
        fila, columna = self._casilla_pieza(state, 'k')
        rey_negro_fila = (4 - fila if fila < 4 else (fila % 4) + 1) - 3 
        rey_negro_columna = (4 - columna if columna < 4 else (columna % 4) + 1) - 3
        rincon = max(rey_negro_fila, rey_negro_columna)
        return rincon
        # return 10 * np.exp(rincon)
         
    def _is_cutoff(self, estado, d):
        if self.game.es_terminal(estado):
            return True
        # Considering d a ply, so a round is two plies (2*d).
        # But only evaluate an odd number of plies downwards.
        elif 2*(d-1) + 1 >= self.max_lim: 
            return True
        else:
            return False
        
    def _casilla_pieza(self, estado, pieza):
        tablero = str(estado).split('\n')
        fila = [i for i in range(len(tablero)) if pieza in tablero[i]][0]
        columna = tablero[fila].replace(' ', '').find(pieza)
        return (fila, columna)
    
    def _otro_jugador(self, jugador):
        return 'blancas' if jugador == 'negras' else 'negras'


class ChessFinalist2(ChessFinalist1):
    '''
    Agente para enfrentarse a final rey y torre contra rey solitario.
    Extiende ChessFinalist1, pero utiliza búsqueda de árboles Monte Carlo.
    '''
    def __init__(self, game:ReyTorreRey, jugador:str='blancas', max_lim:int=1, time_lim:float=20, sim_lim:int=50, beam_width:int=10):
        super().__init__(game=game, jugador=jugador, max_lim=max_lim) # Vamos a mirar solo tres jugadas adelante en la simulación 
        # El juego debe ser un juego de ajedrez ReyTorreRey
        self.game = game
        # El jugador puede ser 'blancas' o 'negras'
        self.jugador = jugador
        # Limit simulation length
        self.sim_lim = sim_lim
        # Limit time consumed by search
        self.time_lim = time_lim
        # Limit the number of acctions to consider
        self.beam_width = beam_width
        # Sleep time if showing simulation
        self.sleep_time = 0.2
        # Boolean to show seach tree behavior
        self.show_tree = False

    def program(self):
        state = self.states[-1]
        arbol = ArbolBusquedaJuego(state, \
                                   juego=self.game, \
                                   rollout_policy=self.play_policy, \
                                    sim_lim=self.sim_lim, \
                                    beam_width=self.beam_width, \
                                    ucb_constant=2,
                                        )
        time_out = 0
        while time_out < self.time_lim:
            # Selección
            nodo = arbol.seleccionar_ucb()
            # Expansión
            nodo_expandido = None
            max_tol = 10
            counter = 0
            while nodo_expandido is None:
                try:
                    nodo_expandido = arbol.expandir(nodo)
                except Exception as e:
                    print(nodo.estado, '\n', e)
                    raise Exception
                counter += 1
                if counter >= max_tol:
                    print('Warning: Expansión no exitosa.')
                    try:
                        action = arbol.get_argmax_acciones()
                        self.plan.append(action)
                        return
                    except Exception as e:
                        print(e)
                        raise Exception('¡Expansión fracasó!')
            # Simulación
            resultado = self.simulate_game(nodo_expandido.estado)
            # Backup
            arbol.backup_value(nodo_expandido, resultado['blancas'])
            if self.show_tree:
                clear_output(wait=True)
                print('accion --> valor')
                for a in arbol.dict_acciones.keys():
                    print(f'\t{a} --> {arbol.dict_acciones[a]}')
            time_out += 1
        action = arbol.get_argmax_acciones()
        self.plan.append(action)

    def play_policy(self, state):
        jugador = self.game.player(state)
        if self.game.es_terminal(state):
            return None
        if jugador == 'blancas':
            self.pesos = [1,1,1,1]
        elif jugador == 'negras':
            self.pesos = [0,1,0,1]
        else:
            raise Exception(f'Oops! player={jugador}')
        # El agente toma una acción de acuerdo al alfa-beta con cutoff
        v, action = self._H_minimax_alfa_beta(state, 0, -np.infty, np.infty)            
        return action

    def simulate_game(self, state, render:bool=False):
        if self.game.es_terminal(state):
            u = self.game.utilidad(state, self.game.player(state))
        else:
            u = None
            s = state
            d = 0
            while u is None:
                if d >= self.sim_lim:
                    u = 0
                    break
                u, s = self.get_result_from_policy(s)
                if render:
                    clear_output(wait=True)
                    display(s)
                    sleep(self.sleep_time)                    
                d += 1
        if u > 0:
            return {'blancas':1, 'negras':0}
        else:
            return {'blancas':0, 'negras':1} # Empatar le sirve a las negras
        
    def get_result_from_policy(self, state):
        jugador = self.game.player(state)
        if self.game.es_terminal(state):
            return self.game.utilidad(state, jugador), state
        if jugador == 'blancas':
            self.pesos = [1,1,4,0]
        elif jugador == 'negras':
            self.pesos = [0,1,0,1]
        else:
            raise Exception(f'Oops! player={jugador}')
        # El agente toma una acción de acuerdo al alfa-beta con cutoff
        v, action = self._H_minimax_alfa_beta(state, 0, -np.infty, np.infty)            
        return None, self.game.resultado(state, action)
