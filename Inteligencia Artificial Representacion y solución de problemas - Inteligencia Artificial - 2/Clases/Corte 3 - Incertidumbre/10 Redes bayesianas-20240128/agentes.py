from ambientes import Rejilla
from busqueda import avara, solucion
from random import choice
import numpy as np
import pyAgrum as gum
from itertools import product

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
	
class HeroeUE(Agent):

	def __init__(self):
		super().__init__()
		self.loc = (0,0)
		self.direccion = 'este'
		self.direcciones = ['este', 'norte', 'oeste', 'sur']
		self.visitadas = []
		self.evidencia = {}

	def restart(self):
		super().restart()
		self.loc = (0,0)
		self.direccion = 'este'
		self.visitadas = []
		self.evidencia = {}
	   
	def make_decision(self):
		'''
		Agent makes a decision according to its model.
		'''
		# Actualiza las casillas visitadas con la casilla actual
		if self.loc not in self.visitadas:
			self.visitadas.append(self.loc)
		# Actualiza la evidencia
		self.actualizar_evidencia()
		# print('Evidencia:', self.evidencia)
		# Halla el estado actual
		estado = self.states[-1]
		# Determina si percibe un brillo
		brillo = estado[2]
		if brillo:
			salida = (0,0)
			acciones = self.planear_ruta(salida)
			self.plan = ['agarrar'] + acciones + ['salir']
		# Chequeamos si ya el agente no tiene un plan (lista de acciones)
		if len(self.plan) == 0:
			# Usamos el programa para crear un plan
			self.program()
			# print('->', self.plan)
		try:
			# La acción a realizar es la primera del plan
			action = self.plan.pop(0)
		except:
			# ¡No hay plan!
			state = self.states[-1]
			raise Exception(f'¡Plan vacío! Revisar reglas en estado {self.loc} -- {estado}')
		# Actualizamos posición y dirección del agente
		# de acuerdo a la acción
		self.actualizar(action)
		self.turn += 1
		return action

	def program(self):
		'''
		Programa de agente de acuerdo a diagrama de flujo.
		'''
		def maximo_aleatorio():
			'''
			Retorna la casilla con mayor utilidad esperada.
			Resuelve los empates de manera aleatoria.
			'''
			casillas = [c for c in self.adyacentes(self.loc)]
			# for c in casillas:
			# 	print('Pozo:', ie.posterior(f'Pozo{c}'))
			# print(ie.posteriorUtility("Casilla"))
			valores = ie.posteriorUtility("Casilla").tolist()
			indices = [i for i, x in enumerate(valores) if x == max(valores)]
			indice = choice(indices)
			return casillas[indice]

		# Creamos la red de decision para la casilla dada
		model = self.crear_red_decision()
		# Guardamos solo la evidencia que cae en las variables de la red de decisión
		evid = {v:self.evidencia[v] for v in self.evidencia.keys() if v in model.names()}
		# Hacemos la inferencia
		ie = gum.InfluenceDiagramInference(model)
		ie.setEvidence(evid)
		ie.makeInference()
		# Escogemos la acción con mayor utilidad esperada
		decision = maximo_aleatorio()
		acciones = self.acciones_camino([self.loc, decision])
		self.plan += acciones

	def actualizar_evidencia(self):
		# Determina las percepciones 
		hechos = self.interp_percepto().split('&')
		# Actualiza la lista de evidencia
		for hecho in hechos:
			if '-' in hecho:
				h = hecho[1:]
				self.evidencia[h] = 0
			else:
				self.evidencia[hecho] = 1
		self.evidencia[f'Pozo{self.loc}'] = 0

	def crear_red_decision(self):   
		'''
		Crea una red de decisión para la caverna centrada en una casilla
		'''

		'''Auxiliares para crear probabilidades condicionales'''
		def pozos_a_brisa(d):
			if 1 not in d.values():
				return [1,0]
			else:
				return [0,1]

		def oro_a_brillo(c1,c2):
			if c1 == c2:
				return [0,1]
			else:
				return [1,0]
		
		def utilidad(d):
			'''
			Define la utilidad dado un estado
			'''
			C = d['Casilla']
			if (d['Pozo'+str(C)] == 0) and (d['Oro'] == C):
				return 1
			elif (d['Pozo'+str(C)] == 0):
				return 0
			else:
				return -1

		# Inicalizamos la red de decisión
		model = gum.InfluenceDiagram()
		# Definimos lista de todas las casillas
		todas_casillas = [(x,y) for x in range(4) for y in range(4)]
		total_casillas = len(todas_casillas)
		# Casillas adyacentes a la actual
		casillas = self.adyacentes(self.loc)
		num_casillas = len(casillas)
		# Casillas adyacentes a las adyacentes
		aux = [self.adyacentes(c) for c in casillas]
		aux = [item for sublist in aux for item in sublist]
		casillas_adyacentes2 = list(set(aux))
		# Casillas adyacentes a las adyacentes de las adyacentes
		aux = [self.adyacentes(c) for c in casillas_adyacentes2]
		aux = [item for sublist in aux for item in sublist]
		casillas_adyacentes3 = list(set(aux))
		# Creando variables del oro y brillo
		oro = gum.LabelizedVariable('Oro','Oro',total_casillas)
		for i, c in enumerate(todas_casillas):
			oro.changeLabel(i,str(c))
			brillo_i = gum.LabelizedVariable('Brillo'+str(c),'Brillo'+str(c),2)
			model.addChanceNode(brillo_i)
		model.addChanceNode(oro)
		# Creando variables de pozo
		for c in casillas_adyacentes3:
			pozo_i = gum.LabelizedVariable('Pozo'+str(c),'Pozo'+str(c),2)
			model.addChanceNode(pozo_i)
		# Creando variables de brisa
		for c1 in casillas_adyacentes2:
			brisa_i = gum.LabelizedVariable('Brisa'+str(c1),'Brisa'+str(c1),2)
			model.addChanceNode(brisa_i)
		# Creando variables de casilla
		casilla = gum.LabelizedVariable('Casilla','Casilla a moverse',num_casillas)
		for i, c in enumerate(casillas):
			casilla.changeLabel(i,str(c))
		model.addDecisionNode(casilla)
		# Creando variable de utilidad
		ut_casilla = gum.LabelizedVariable('UtilityOfCasilla','Valor casilla',1)
		model.addUtilityNode(ut_casilla)
		# Creando aristas del grafo
		for c in todas_casillas:
			model.addArc('Oro', 'Brillo'+str(c))
		for c in casillas_adyacentes3:
			for c1 in self.adyacentes(c):
				if c1 in casillas_adyacentes2:
					model.addArc('Pozo'+str(c), 'Brisa'+str(c1))
		for c in casillas:
			model.addArc('Pozo'+str(c), 'UtilityOfCasilla')
		model.addArc('Oro', 'UtilityOfCasilla')
		model.addArc('Casilla', 'UtilityOfCasilla')   
		# Creando tabla de probabilidad ORO
		model.cpt('Oro').fillWith([1/total_casillas]*total_casillas)
		for c in todas_casillas:
			brillo = 'Brillo' + str(c)
			for c1 in todas_casillas:
				model.cpt(brillo)[{'Oro': str(c1)}] = oro_a_brillo(c,c1)
		# Creando tabla de probabilidad POZOS
		pozos = ['Pozo'+str(c) for c in casillas_adyacentes3]
		for pozo in pozos:
			model.cpt(pozo)[:]=[0.8,0.2]
		for c in casillas_adyacentes2:
			brisa = 'Brisa' + str(c)
			pozos_brisa = ['Pozo'+str(c1) for c1 in self.adyacentes(c)]
			opciones = list(product(*[[0,1] for p in pozos_brisa]))
			dicts_variables = [{pozos_brisa[i]:op[i] for i in range(len(pozos_brisa))} for op in opciones]
			for d in dicts_variables:
				model.cpt(brisa)[d] = pozos_a_brisa(d)        
		# WTF
		todas_casillas = [str(c) for c in todas_casillas]
		casillas = [str(c) for c in casillas]
		# Creando diccionarios para asignar utilidad
		pozos = ['Pozo'+str(c) for c in casillas]
		variables = ['Casilla','Oro'] + pozos
		opciones = list(product(casillas, todas_casillas, *[[0,1] for i in pozos]))
		dicts_variables = [{variables[i]:op[i] for i in range(len(variables))} for op in opciones]
		# Asignando la utilidad
		for d in dicts_variables:
			model.utility('UtilityOfCasilla')[d]=utilidad(d)
		return model

	def planear_ruta(self, objetivo:tuple) -> list:
		'''
		Toma un objetivo y devuelve una lista
		de acciones que determinan la ruta para ir 
		desde la ubicación actual al objetivo.
		'''
		# Creamos un entorno de búsqueda con
		# la posición actual y el objetivo
		R = Rejilla(self.loc, objetivo, self.visitadas)
		# Encontramos la solución mediante búsqueda avara
		nodo_solucion = avara(R)
		camino = [self.loc] + solucion(nodo_solucion)
		# Encontramos lista de acciones a partir del camino
		acciones = self.acciones_camino(camino)
		return acciones

	def interp_percepto(self):
		# Halla el estado actual
		estado = self.states[-1]
		# Halla la ubicación actual
		c = self.loc
		orden = [f'Hedor{c}', f'Brisa{c}', f'Brillo{c}', f'Batacazo{c}', f'Grito{c}']
		f = ''
		inicial = True
		for i, p in enumerate(estado):
			if p:
				if inicial:
					f = orden[i]
					inicial = False
				else:
					f = f + '&' + orden[i]
			else:
				if inicial:
					f = '-' + orden[i]
					inicial = False
				else:
					f = f + '&-' + orden[i]
		return f
	
	def adyacentes(self, casilla):
		def truncar(x):
			if x < 0:
				return 0
			elif x > 3:
				return 3
			else:
				return x

		x, y = casilla
		adyacentes = [
			(truncar(x - 1), y), (truncar(x + 1), y),
			(x, truncar(y - 1)), (x, truncar(y + 1))
		]
		adyacentes = [c for c in adyacentes if c != casilla]
		return adyacentes

	def actualizar(self, action):
		# Halla el estado actual
		state = self.states[-1]
		# print(action, state, self.loc, self.direccion)
		# posicion actual
		x, y = self.loc 
		# Primer caso: acción es adelante
		if action == 'adelante':
			if self.direccion == 'este':
				self.loc = (x+1, y)
			if self.direccion == 'oeste':
				self.loc = (x-1, y)
			if self.direccion == 'norte':
				self.loc = (x, y+1)
			if self.direccion == 'sur':
				self.loc = (x, y-1)
			m = 4
			assert(all([0<=x<m, 0<=y<m])), f'¡Actualización inválida! ({x}, {y}) {state}'
		# Segundo caso: acción es girar 90 grados a favor de las manecillas del reloj
		elif action == 'voltearDerecha':
			ind_actual = self.direcciones.index(self.direccion)
			self.direccion = self.direcciones[(ind_actual - 1) % 4]
			# Tercer caso: acción es girar 90 grados en contra de las manecillas del reloj
		elif action == 'voltearIzquierda':
			ind_actual = self.direcciones.index(self.direccion)
			self.direccion = self.direcciones[(ind_actual + 1) % 4]
		elif action in ['salir', 'agarrar']:
			pass
		else:
			raise Exception(f'¡Acción desconocida! ({action})')

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

	def acciones_camino(self, camino):
		direccion = self.direccion
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


