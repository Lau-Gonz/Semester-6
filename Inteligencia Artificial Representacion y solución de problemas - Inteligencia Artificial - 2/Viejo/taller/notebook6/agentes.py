from logica import LPQuery
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnnotationBbox, OffsetImage, TextArea
import numpy as np
from logica import *

class Laberinto:
	'''
	Laberinto: Rejilla con muros y pasadizos.
	'''
	def __init__(self, salida=(0,0), pos_inicial=(11,11), dir_agente='oeste', laberinto=None):

		# laberinto, una matriz numpy con 1 en la casilla con muro
		if laberinto is None:
			self.laberinto = np.matrix([[0,0,0,1,0,0,0,0,0,0,0,0],\
							[0,1,0,1,0,0,0,0,0,0,0,0],\
							[0,1,0,1,0,0,0,1,0,0,0,0],\
							[0,0,0,1,1,1,0,0,0,0,0,0],\
							[0,0,0,1,0,0,0,0,0,1,1,1],\
							[0,0,0,0,0,1,1,1,0,1,0,0],\
							[0,0,0,1,1,0,0,0,0,1,1,0],\
							[0,1,0,1,0,0,1,0,0,1,0,0],\
							[0,1,0,0,0,1,0,0,0,1,0,1],\
							[0,0,0,0,0,0,0,0,0,1,0,0],\
							[0,1,0,0,0,0,1,1,1,1,1,0],\
							[0,1,0,0,0,0,0,0,0,0,0,0]])
		else:
			self.laberinto = laberinto
		self.agente = pos_inicial
		self.dir_agente = dir_agente
		self.max = self.laberinto.shape[0]
		self.salida = salida
		self.activo = True

	def truncar(self, x):
	    if x < 0:
	        return 0
	    elif x > self.max - 1:
	        return self.max - 1
	    else:
	        return x

	def matrix2lista(self, m):
		lista = np.where(m == 1)
		ran = list(range(len(lista[0])))
		return [(lista[1][i], self.max-1-lista[0][i]) for i in ran]

	def pintar(self):
		# Dibuja el laberinto
		estado = self.agente
		fig, axes = plt.subplots(figsize=(8, 8))
		# Dibujo el tablero
		step = 1./self.max
		offset = 0.001
		tangulos = []
		# Borde del tablero
		tangulos.append(patches.Rectangle((0,0),0.998,0.998,\
                                          facecolor='cornsilk',\
                                         edgecolor='black',\
                                         linewidth=2))
		# Creo los muros
		muros = self.matrix2lista(self.laberinto)
		for m in muros:
			x, y = m
			tangulos.append(patches.Rectangle(*[(x*step,y*step), step,step],\
                    facecolor='black'))
		for t in tangulos:
			axes.add_patch(t)
		offsetX = 0.045
		offsetY = 0.04
		#Poniendo salida
		X, Y = (0,0)
		arr_img = plt.imread("./imagenes/Laberinto/salida.png", format='png')
		image_salida = OffsetImage(arr_img, zoom=0.025)
		image_salida.image.axes = axes
		ab = AnnotationBbox(
		    image_salida,
		    [(X*step) + offsetX, (Y*step) + offsetY],
		    frameon=False)
		axes.add_artist(ab)
		#Poniendo robot
		X, Y = estado
		imagen_robot = "./imagenes/Laberinto/robot_" + self.dir_agente + ".png"
		arr_img = plt.imread(imagen_robot, format='png')
		image_robot = OffsetImage(arr_img, zoom=0.125)
		image_robot.image.axes = axes
		ab = AnnotationBbox(
		    image_robot,
		    [(X*step) + offsetX, (Y*step) + offsetY],
		    frameon=False)
		axes.add_artist(ab)
		axes.axis('off')
		plt.show()

	def test_objetivo(self):
		# Devuelve True/False dependiendo si el agente está
		# en la salida
		return self.agente == self.salida

	def para_sentidos(self):
		# Devuelve una lista de muro o pasadizo dependiendo
		# de dónde está el agente
		# El orden de sensores es [derecha, arriba, izquierda, abajo]
		x, y = self.agente
		derecha = (x+1, y) if self.truncar(x+1) == x+1 else False
		arriba = (x, y+1) if self.truncar(y+1) == y+1 else False
		izquierda = (x-1, y) if self.truncar(x-1) == x-1 else False
		abajo = (x, y-1) if self.truncar(y-1) == y-1 else False
		if self.dir_agente == 'oeste':
			casillas = [izquierda, abajo, arriba, derecha]
		elif self.dir_agente == 'este':
			casillas = [derecha, arriba, abajo, izquierda]
		elif self.dir_agente == 'norte':
			casillas = [arriba, izquierda, derecha, abajo]
		elif self.dir_agente == 'sur':
			casillas = [abajo, derecha, izquierda, arriba]
		m = self.max - 1
		f = lambda c: self.laberinto[(m - c[1], c[0])]==1 if c != False else not c
		return [f(c) for c in casillas]

	def transicion(self, accion):
		x, y = self.agente
		m = self.max - 1
		direcciones = ['este', 'norte', 'oeste', 'sur']
		if accion == 'voltearIzquierda':
			ind_actual = direcciones.index(self.dir_agente)
			self.dir_agente = direcciones[(ind_actual + 1) % 4]
		elif accion == 'voltearDerecha':
			ind_actual = direcciones.index(self.dir_agente)
			self.dir_agente = direcciones[(ind_actual - 1) % 4]
		elif accion == 'adelante':
			if (self.dir_agente == 'oeste'):
				if (self.truncar(x-1) == x-1):
					correccion = (m - y, x-1)
					if (self.laberinto[correccion] == 0):
						self.agente = (x-1, y)
			elif (self.dir_agente == 'este'):
				if (self.truncar(x+1) == x+1):
					correccion = (m - y, x+1)
					if (self.laberinto[correccion] == 0):
						self.agente = (x+1, y)
			elif (self.dir_agente == 'norte'):
				if (self.truncar(y+1) == y+1):
					correccion = (m - (y+1), x)
					if (self.laberinto[correccion] == 0):
						self.agente = (x, y+1)
			elif (self.dir_agente == 'sur'):
				if (self.truncar(y-1) == y-1):
					correccion = (m - (y-1), x)
					if (self.laberinto[correccion] == 0):
						self.agente = (x, y-1)
		elif accion == 'salir':
			print('=>',self.agente)
			if self.test_objetivo():
				self.activo = False        
		else:
			raise Exception('¡Acción inválida:', accion)

class Agente:

	def __init__(self):
		self.perceptos = []
		self.acciones = []
		self.tabla = {}
		self.reglas = []
		self.base = LPQuery([])
		self.turno = 1
		self.loc = (0,0)

	def reaccionar(self):
		if len(self.acciones) == 0:
			self.programa()
		a = self.acciones.pop(0)
		self.turno += 1
		return a

	def interp_percepto(self):
		orden = ['frn_bloq_', 'izq_bloq_', 'der_bloq_', 'atr_bloq_']
		f = ''
		inicial = True
		for i, p in enumerate(self.perceptos):
			if p:
				if inicial:
					f = orden[i]+str(self.turno)
					inicial = False
				else:
					f = f + 'Y' + orden[i]+str(self.turno)
			else:
				if inicial:
					f = '-' + orden[i]+str(self.turno)
					inicial = False
				else:
					f = f + 'Y-' + orden[i]+str(self.turno)
		return f
    
	def programa(self):
		turno = self.turno
		if ASK(f'voltearDerecha_{turno}', 'success', self.base):
			self.acciones.append('voltearDerecha')
			self.base.TELL(f'voltearDerecha_{turno}')
		elif ASK(f'adelante_{turno}', 'success', self.base):
			self.acciones.append('adelante')
			self.base.TELL(f'adelante_{turno}')
		elif ASK(f'voltearIzquierda_{turno}', 'success', self.base):
			self.acciones.append('voltearIzquierda')
			self.base.TELL(f'voltearIzquierda_{turno}')
			raise Exception('¡Caso no considerado!', self.interp_percepto())
        
	def posicion_inicial(self, direccion):
		x, y = self.loc
		formulas = [f'mirando_{direccion}_1', 
					f'en({x},{y})_1',
					'-frn_visitada_1',
					'-frn_bloq_0',
					'-izq_bloq_0',
					'-der_bloq_0',
					'-atr_bloq_0',
					]
		return formulas

	def estimar_estado(self):
		turno = self.turno
		formulas = []
		FORMULAS = ['conocimiento', 'fluente_en', 'fluente_mirando', 'fluente_visitadas', 'fluente_frn_visitada', 'fluente_der_visitada', 'fluente_izq_visitada']
		for f in FORMULAS:
			try:
				formulas += eval(f'self.{f}()')
			except:
				pass
		formulas += [self.nueva_posicion()]
		formulas += [self.nueva_direccion()]
		formulas += self.cache()
		formulas += [self.interp_percepto()]
		self.base = LPQuery(formulas)

	def cache(self):
		turno = self.turno
		# Guardamos los perceptos del turno pasado
		aux = [x for x in self.base.hechos if f'_bloq_{turno-1}' in x]
		# Guardamos las casillas visitadas
		visitadas = []
		casillas = [(x,y) for x in range(12) for y in range(12)]
		for c in casillas:
			x, y = c
			consulta = ASK(f'visitada({x},{y})_{turno}', 'success', self.base)
			if consulta:
				visitadas.append(f'visitada({x},{y})_{turno}')
		return aux + visitadas

	def nueva_posicion(self):
		casillas = [self.loc] + adyacentes(self.loc)
		for c in casillas:
			x, y = c
			pos = f'en({x},{y})_{self.turno}'
			evaluacion = ASK(pos, 'success', self.base)
			if evaluacion:
				self.loc = (x,y)
				return pos
		raise Exception('¡No se encontró posición!')

	def nueva_direccion(self):
		direcciones = ['o', 'e', 's', 'n']
		for d in direcciones:
			direccion = f'mirando_{d}_{self.turno}'
			evaluacion = ASK(direccion, 'success', self.base)
			if evaluacion:
				return direccion
		raise Exception('¡No se encontró dirección!')
            
def adyacentes(c):
	x, y = c
	return [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]