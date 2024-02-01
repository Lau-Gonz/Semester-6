import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnnotationBbox, OffsetImage, TextArea
import numpy as np
import random

class Laberinto:
	'''
	Laberinto: Rejilla con muros y pasadizos.
	'''
	def __init__(self, salida=(0,0), pos_inicial=(11,11), dir_agente='oeste', aleatorio=False):

		# laberinto, una matriz numpy con 1 en la casilla con muro
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
		self.max = self.laberinto.shape[0]
		self.salida = salida
		self.pos_inicial = pos_inicial
		self.agente = pos_inicial
		self.dir_agente_ = dir_agente
		self.dir_agente = dir_agente
		self.aleatorio = aleatorio
		if self.aleatorio:
			self.reset()

	def reset(self):
		if not isinstance(self.laberinto, np.matrix):
			self.laberinto = np.matrix(self.laberinto)
		if self.aleatorio:
			y, x = np.where(self.laberinto == 0)
			casillas_vacias = [(x[i], self.max-1 - y[i]) for i in range(len(x))]
			casillas_vacias = [casilla for casilla in casillas_vacias if casilla != (0,0)]
			self.pos_inicial = random.choice(casillas_vacias)			
			a, b = self.pos_inicial
			assert(self.laberinto[self.max-1 - b, a] == 0), f'({a}, {b}) ---> [{b}, {self.max-1 - b}] ---> {self.laberinto[self.max-1 - b, a]}'
		self.agente = self.pos_inicial
		if self.aleatorio:
			self.dir_agente_ = random.choice(['este', 'oeste', 'norte', 'sur'])
		self.dir_agente = self.dir_agente_
		state = self.para_sentidos()
		return state

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

	def render(self):
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
		# Devuelve True/False dependiendo si el agente está en la salida
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

	def step(self, accion):
		state = self.para_sentidos()
		x, y = self.agente
		direcciones = ['este', 'norte', 'oeste', 'sur']
		if accion == 'voltearIzquierda':
			ind_actual = direcciones.index(self.dir_agente)
			self.dir_agente = direcciones[(ind_actual + 1) % 4]
		elif accion == 'voltearDerecha':
			ind_actual = direcciones.index(self.dir_agente)
			self.dir_agente = direcciones[(ind_actual - 1) % 4]
		elif accion == 'adelante':
			if not state[0]:
				if self.dir_agente == 'este':
					self.agente = (x+1, y)
				if self.dir_agente == 'oeste':
					self.agente = (x-1, y)
				if self.dir_agente == 'norte':
					self.agente = (x, y+1)
				if self.dir_agente == 'sur':
					self.agente = (x, y-1)
		else:
			raise Exception('¡Acción inválida:', accion)
		new_state = self.para_sentidos()
		reward = -1
		done = self.test_objetivo()
		return new_state, reward, done
