from logica import LPQuery
from ambientes import Rejilla
from busqueda import avara, solucion
from random import choice
import numpy as np

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
	
class Heroe(Agent):

	def __init__(self):
		super().__init__()
		self.loc = (0,0)
		self.direccion = 'este'
		self.base = LPQuery(self.reglas())
		self.seguras = []
		self.visitadas = []
		self.por_visitar = []
		self.direcciones = ['este', 'norte', 'oeste', 'sur']

	def restart(self):
		super().restart()
		self.loc = (0,0)
		self.direccion = 'este'
		self.base = LPQuery(self.reglas())
		self.seguras = []
		self.visitadas = []
		self.por_visitar = []
	   
	def make_decision(self):
		'''
		Agent makes a decision according to its model.
		'''
		# Actualiza las casillas visitadas con la casilla actual
		if self.loc not in self.visitadas:
			self.visitadas.append(self.loc)
		# print('Visitadas ->', self.visitadas)
		# Actualiza las casillas seguras con la casilla actual
		if self.loc not in self.seguras:
			self.seguras.append(self.loc)
		# Halla el estado actual
		estado = self.states[-1]
		# Determina si percibe un brillo
		brillo = estado[2]
		if brillo:
			salida = (0,0)
			acciones = self.planear_ruta(salida)
			self.plan = ['agarrar'] + acciones + ['salir']
		# Reinicia la base de conocimiento
		self.reiniciar_base()
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
		A = self.loc
		self.actualizar(action)
		B = self.loc
		# print(f'{action}: {A} => {B}')
		self.turn += 1
		return action

	def program(self):
		'''
		Programa de agente de acuerdo a diagrama de flujo.
		'''
		self.determinar_por_visitar()
		V = self.por_visitar
#		print('Por visitar', V)
		if len(V) > 0:
#			print('%%%%%>', len(V), V)
			objetivo = self.por_visitar.pop()
#			print('objetivo', objetivo)
			acciones = self.planear_ruta(objetivo)
		else:
			salida = (0,0)
			acciones = self.planear_ruta(salida) + ['salir']
#			print('%%>', acciones)
		self.plan = acciones
	
	def planear_ruta(self, objetivo:tuple) -> list:
		'''
		Toma un objetivo y devuelve una lista
		de acciones que determinan la ruta para ir 
		desde la ubicación actual al objetivo.
		'''
		# Creamos un entorno de búsqueda con
		# la posición actual y el objetivo
		R = Rejilla(self.loc, objetivo, self.visitadas + [objetivo])
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
		orden = [f'hedor{c}', f'brisa{c}', f'brillo{c}', f'batacazo{c}', f'grito{c}']
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
	
	def reiniciar_base(self):
		# Backup de los hechos
		hechos = self.base.hechos
		reglas_ = self.reglas()
		self.base = LPQuery(reglas_)
		# Determina las percepciones 
		c = self.interp_percepto()
		hechos += c.split('&')
		# Actualiza los hechos
		for hecho in hechos:
			self.base.tell(hecho)

	def determinar_por_visitar(self):
		'''
		Actualiza la lista de casillas por visitar.
		Usa las casillas adyacentes a la ubicación actual
		para encontrar las que sean seguras y no hayan
		sido visitadas para incluirlas en la lista.
		'''
		# Encontramos las casillas adyacentes seguras 
		# a la ubicación actual
		adyacentes_seg = self.adyacentes_seguras()
#		print('Adyacentes seguras', adyacentes_seg)
		# Actualiza las casillas seguras
		for c in adyacentes_seg:
			if c not in self.seguras:
				self.seguras.append(c)
		# Incluimos dichas casillas en por_visitar
		# si no han sido visitadas
		for c in adyacentes_seg:
			if c not in self.visitadas:               
				if c not in self.por_visitar:
					self.por_visitar.append(c)

	def adyacentes_seguras(self):    
		'''
		Encuentra la lista de casillas adyacentes
		que sean seguras
		'''
		casillas_seguras = []
		for c in self.adyacentes(self.loc):
			objetivo = f'segura{c}'
			res = self.base.ask(objetivo, verbose=False)
			if res == 'exito':
				casillas_seguras.append(c)
		return casillas_seguras

	def reglas(self):

		def brisa_pozo():
			formulas = []
			casillas = self.adyacentes(self.loc)
			for c in casillas:
				formulas += [
					f'-brisa{self.loc}>-pozo{c}',                
				]
			return formulas

		def hedor_wumpus():    
			casillas = self.adyacentes(self.loc)
			formulas = []
			for c in casillas:
				x1, y1 = c
				formulas += [
					f'-hedor{self.loc}>-wumpus{c}',                
				]
			return formulas

		def casilla_segura():   
			casillas = [(x,y) for x in range(4) for y in range(4)]
			formulas = []
			for c in casillas:
				formulas += [
					f'-pozo{c}&-wumpus{c}>segura{c}',                
				]
			return formulas

		return brisa_pozo() + hedor_wumpus() + casilla_segura()

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
		elif action in ['salir', 'agarrar', 'disparar']:
			pass
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


