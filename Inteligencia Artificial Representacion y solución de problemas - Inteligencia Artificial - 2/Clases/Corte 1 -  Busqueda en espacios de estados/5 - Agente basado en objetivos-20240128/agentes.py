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


class GoalBased(Agent):
    '''Agente que búsca un camino usando un mapa.'''
    def __init__(self):
        super().__init__()
        # Iniciamos un mapa vacío suficientemente grande
        self.dim = 26
        self.mapa = np.empty((self.dim,self.dim))*np.nan 
        # El agente inicia siempre en el centro de su mapa
        self.loc = (int(self.dim/2),int(self.dim/2)) 
        # Asumimos el agente comienza mirando a lo que cree que es el este
        self.direccion = 'este' 
        # Lista de direcciones, organizadas en contra de las manecillas del reloj
        # Observe que aumentar el índice en esta lista en uno módulo 4 es girar
        # contra las manecillas del reloj. Similarmente, disminuir el índice en
        # uno módulo 4 es girar a favor de las manecillas del reloj
        self.direcciones = ['este', 'norte', 'oeste', 'sur']
        # Creamos una lista de casillas visitadas
        self.visitadas = [self.loc]
        # Creamos una lista de casillas por visitar
        self.por_visitar = []

    def make_decision(self):
        '''
        Agent makes a decision according to its model.
        It also keeps track of its position.
        '''
        # print(f'Estoy en {self.loc} mirando hacia {self.direccion}')
        # Chequeamos si ya el agente no tiene un plan (lista de acciones)
        if len(self.plan) == 0:
            # Usamos el programa para crear un plan
            self.program()
        try:
            # La acción a realizar es la primera del plan
            action = self.plan.pop(0)
            # Determinamos nueva posición y direccion
            self.actualizar(action)
        except Exception as e:
            print('Visitadas', self.visitadas)
            print('Por visitar', self.por_visitar)
            print(f'Estoy en {self.loc} mirando hacia {self.direccion}')
            # ¡No hay plan!
            state = self.states[-1]
            raise Exception(f'¡Plan vacío! Revisar reglas en estado {state}\nPosible causa: {e}')
        # print(f'Mi acción es {action}')
        self.turn += 1
        return action

    def restart(self):
        super().restart()
        self.mapa = np.empty((self.dim,self.dim))*np.nan 
        self.loc = (int(self.dim/2),int(self.dim/2)) 
        self.direccion = 'este'
        self.visitadas = [self.loc]
        self.por_visitar = []

    def program(self):
        # Actualiza su mapa con las percepciones actuales
        self.percepciones_a_mapa()
        # Actualizamos casillas por visitar
        self.determinar_por_visitar()
        # print('Por visitar:', self.por_visitar)
        # Escogemos una casilla por visitar
        objetivo = self.por_visitar.pop()
        # print(f'actual:{self.loc}  --- objetivo:{objetivo}')
        # Creamos un entorno de búsqueda con
        # la posición actual y el objetivo
        R = Rejilla(self.loc, objetivo, self.mapa)
        # Encontramos la solución mediante búsqueda avara
        nodo_solucion = avara(R, R.heuristica)
        camino = [self.loc] + solucion(nodo_solucion)
        # Encontramos lista de acciones a partir del camino
        acciones = self.acciones_camino(camino, self.direccion)
        self.plan += acciones 

    def percepciones_a_mapa(self):
        '''
        Toma las percepciones y actualiza su mapa interno
        '''
        # Halla el estado actual
        state = self.states[-1]
        # Halla las coordenadas actuales
        x, y = self.loc
        # print(f'Estoy en {self.loc} y percibo {state}')
        # Dependiendo de dónde esté mirando, crea cuáles son las casillas
        # correspondientes al frente, izquerda, derecha y atrás
        if self.direccion == 'este':
            casillas = [(x+1,y), (x,y+1), (x,y-1), (x-1,y)]
        elif self.direccion == 'norte':
            casillas = ... # Aquí su código
        elif self.direccion == 'oeste':
            casillas = ... # Aquí su código
        elif self.direccion == 'sur':
            casillas = ... # Aquí su código
        # print(f'Mi orden de casillas es {casillas}')
        # Actualiza el mapa con la información de los sensores
        # 1 si el sensor está encendido (percibe un muro), 0 si no
        for i, casilla in enumerate(casillas):
            # Valor de la casilla: 1 si hay muro, 0 si no
            self.mapa[self.Car2Mat(casilla)] = 1 if state[i] else 0

    def determinar_por_visitar(self):
        '''
        Actualiza su lista de casillas por visitar
        '''
        # Halla coordenadas actuales
        x, y = self.loc
        # Creamos lista de adyacentes
        adyacentes = [(x-1,y), (x,y-1), (x,y+1), (x+1,y)]
        # Creamos lista de casillas adyacentes sin muro
        candidatos = [casilla for casilla in adyacentes if self.mapa[self.Car2Mat(casilla)] == 0]
        # print('Adyacentes sin muro:', candidatos)
        # Las opciones no pueden ser casillas visitadas ...
        candidatos = [casilla for casilla in candidatos if casilla not in self.visitadas]
        # Añadir a lista de casillas por visitar
        for casilla in candidatos:
            if casilla not in self.por_visitar:
                self.por_visitar.append(casilla)

    def actualizar(self, action):
        # Halla el estado actual
        state = self.states[-1]
        # print(action, state, self.loc, self.direccion)
        # posicion actual
        x, y = self.loc 
        # Primer caso: acción es adelante y el frente no está bloqueado
        if action == 'adelante':
            if not state[0]:
                if self.direccion == 'este':
                    self.loc = (x+1, y)
                if self.direccion == 'oeste':
                    self.loc = ... # Aquí su código
                if self.direccion == 'norte':
                    self.loc = ... # Aquí su código
                if self.direccion == 'sur':
                    self.loc = ... # Aquí su código
            m = self.mapa.shape[0]
            assert(all([0<=x<m, 0<=y<m])), f'¡Actualización inválida! ({x}, {y}) {state}'
        # Segundo caso: acción es girar 90 grados a favor de las manecillas del reloj
        elif action == 'voltearDerecha':
            ind_actual = self.direcciones.index(self.direccion)
            self.direccion = self.direcciones[(ind_actual - 1) % 4]
        # Tercer caso: acción es girar 90 grados en contra de las manecillas del reloj
        elif action == 'voltearIzquierda':
            ind_actual = self.direcciones.index(self.direccion)
            self.direccion = self.direcciones[(ind_actual + 1) % 4]
        else:
            raise Exception(f'¡Acción desconocida! ({action})')
        # Añadimos casilla visitada
        if self.loc not in self.visitadas:
            self.visitadas.append(self.loc)

    def voltear(self, direccion_inicial, direccion_final):
        acciones = []
        if direccion_inicial == direccion_final:
            return acciones
        else:
            if direccion_final == 'este':
                if direccion_inicial == 'norte':
                    acciones.append('voltearDerecha')
                elif direccion_inicial == 'sur':
                    acciones.append('voltearIzquierda')
                elif direccion_inicial == 'oeste':
                    acciones.append('voltearDerecha')
                    acciones.append('voltearDerecha')
            elif direccion_final == 'norte':
                if direccion_inicial == 'este':
                    acciones.append('voltearIzquierda')
                elif direccion_inicial == 'sur':
                    acciones.append('voltearIzquierda')
                    acciones.append('voltearIzquierda')
                elif direccion_inicial == 'oeste':
                    acciones.append('voltearDerecha')
            elif direccion_final == 'oeste':
                if direccion_inicial == 'este':
                    acciones.append('voltearIzquierda')
                    acciones.append('voltearIzquierda')
                elif direccion_inicial == 'sur':
                    acciones.append('voltearDerecha')
                elif direccion_inicial == 'norte':
                    acciones.append('voltearIzquierda')
            elif direccion_final == 'sur':
                if direccion_inicial == 'este':
                    acciones.append('voltearDerecha')
                elif direccion_inicial == 'norte':
                    acciones.append('voltearDerecha')
                    acciones.append('voltearDerecha')
                elif direccion_inicial == 'oeste':
                    acciones.append('voltearIzquierda')
        return acciones

    def acciones_camino(self, camino, direccion):
            acciones = []
            for i in range(len(camino) - 1):
                x1, y1 = camino[i]
                x2, y2 = camino[i + 1]
                diferencia_x = x2 - x1
                diferencia_y = y2 - y1
                if (diferencia_x != 0) and (diferencia_y != 0):
                    raise Exception("Camino incorrecto!: No debe incluir diagonales.")
                elif diferencia_x > 0:
                    acciones +=self.voltear(direccion, 'este')
                    direccion = 'este'
                elif diferencia_x < 0:
                    acciones += self.voltear(direccion, 'oeste')
                    direccion = 'oeste'
                elif diferencia_y > 0:
                    acciones += self.voltear(direccion, 'norte')
                    direccion = 'norte'
                elif diferencia_y < 0:
                    acciones += self.voltear(direccion, 'sur')
                    direccion = 'sur'
                acciones.append('adelante')
            return acciones
    
    def Car2Mat(self, casilla):
        '''
        Transformación de coordenadas cartecianas a matriciales.
        '''
        a, b = casilla
        return (self.dim-1-b, a)