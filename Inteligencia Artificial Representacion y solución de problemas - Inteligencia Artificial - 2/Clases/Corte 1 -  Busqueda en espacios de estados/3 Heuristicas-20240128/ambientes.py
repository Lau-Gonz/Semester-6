import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnnotationBbox, OffsetImage, TextArea
import numpy as np
import copy
from time import sleep
from IPython.display import clear_output
import networkx as nx
#plt.rcParams["figure.figsize"] = (10,10)


class OchoReinas:
	'''
	Problema de las ocho reinas, el cual consiste en poner ocho reinas en un tablero de ajerdez de tal manera que ninguna pueda atacar a las demás.
	Estado inicial: Tablero vacío.
	Posibles acciones: Dado un estado con k reinas (k<8), las acciones aplicables son poner una reina en una de las casillas vacías que no es atacada por ninguna de las otras reinas.
	Función de transiciones: Toma un tablero con k reinas (k<8) y devuelve un tablero con k+1 reinas.
	Prueba de satisfacción del objetivo: Verificar la condición de si un tablero dado contiene ocho reinas en el cual niguna puede atacar a otra.
	Función de costo: Cantidad de acciones realizadas (siempre devolverá el valor de 8 en cualquier solución).
	'''
	def __init__(self):
		self.estado_inicial = np.matrix([[0]*8]*8)

	def render(self, estado):
		# Dibuja el tablero correspondiente al estado
		# Input: estado, que es una 8-lista de 8-listas
		fig, axes = plt.subplots(figsize=(5,5))

		# Dibujo el tablero
		step = 1./8
		offset = 0.001
		tangulos = []

		# Borde del tablero
		tangulos.append(patches.Rectangle((0,0),0.998,0.998,\
		facecolor='cornsilk',\
		edgecolor='black',\
		linewidth=2))

		# Creo los cuadrados oscuros en el tablero
		for i in range(4):
			for j in range(4):
				tangulos.append(
				patches.Rectangle(
				(2 * i * step, 2 * j * step), \
				step - offset, \
				step,\
				facecolor='lightslategrey')\
				)
				tangulos.append(
				patches.Rectangle(
				(step + 2 * i * step, (2 * j + 1) * step), \
				step - offset, \
				step,\
				facecolor='lightslategrey')\
				)

		# Creo las líneas del tablero
		for j in range(8):
			locacion = j * step
			# Crea linea horizontal en el rectangulo
			tangulos.append(patches.Rectangle(*[(0, locacion), 1, 0.008],\
			facecolor='black'))
			# Crea linea vertical en el rectangulo
			tangulos.append(patches.Rectangle(*[(locacion, 0), 0.008, 1],\
			facecolor='black'))

		for t in tangulos:
			axes.add_patch(t)

		# Cargando imagen de la reina
		arr_img = plt.imread("./imagenes/8Reinas/reina.png", format='png')
		imagebox = OffsetImage(arr_img, zoom=0.048)
		imagebox.image.axes = axes

		offsetX = 0.065
		offsetY = 0.065
		for i in range(8):
			for j in range(8):
				if estado[j, i] == 1:
					# print("Reina en (" + str(i) + ", " + str(j) + ")")
					Y = 7 - j
					X = i
					# print("(" + str(X) + ", " + str(Y) + ")")
					ab = AnnotationBbox(
					imagebox,
					[(X*step) + offsetX, (Y*step) + offsetY],
					frameon=False)
					axes.add_artist(ab)

		axes.axis('off')
		return axes

	def acciones_aplicables(self, estado):
		# Devuelve una lista de parejas que representan
		# las casillas vacías en las que es permitido
		# poner una reina adicional
		# Input: estado, que es una np.matrix(8x8)
		# Output: lista de indices (x,y)
		indices = [(x, y) for x in range(8) for y in range(8)]
		indices_bloqueados = []
		# Chequeamos primero que haya menos de ocho reinas
		if estado.sum() >= 8:
			return []
		else:
			# Bloqueamos índices por cada reina encontrada
			for x in range(8):
				for y in range(8):
					if estado[y, x]==1:
						# print("\nReina encontrada en", x, y)
						# Encuentra una reina
						# Elimina la fila
						# print("Bloqueando filas...")
						indices_bloqueados += [(i, y) for i in range(8)]
						# Elimina la columna
						#print("Bloqueando columnas...")
						indices_bloqueados += [(x, i) for i in range(8)]
						# Elimina las diagonales \
						# print("\n\tBloqueando diagonales...")
						m = min(x, y)
						xB, yB = x - m, y - m
						M = 8 - max(xB, yB)
						# print("\t\t", end="")
						for i in range(M):
							xC = xB + i
							yC = yB + i
							# print("(" + str(xC) + ", " + str(yC) + ")", end=", ")
							indices_bloqueados.append((xC, yC))
						# Elimina las transversales /
						# print("\n\tBloqueando transversales...")
						m = min(7 - x, y)
						xB, yB = x + m, y - m
						# print("\t\t", end="")
						for i in range(xB):
							xC = xB - i
							yC = yB + i
							# print("(" + str(xC) + ", " + str(yC) + ")", end=", ")
							indices_bloqueados.append((xC, yC))
		return [indice for indice in indices if indice not in indices_bloqueados]

	def transicion(self, estado, indices):
		# Devuelve el tablero incluyendo una reina en el indice
		# Input: estado, que es una np.matrix(8x8)
		#        indice, de la forma (x,y)
		# Output: estado, que es una np.matrix(8x8)
		acciones = self.acciones_aplicables(estado)
		assert(indices in acciones), f'¡La acción {indices} no puede resolverse sin conflicto! Las acciones posibles son {acciones}'
		s = copy.deepcopy(estado)
		x = indices[0]
		y = indices[1]
		s[y, x] = 1
		return s

	def test_objetivo(self, estado):
		# Devuelve True/False dependiendo si el estado
		# resuelve el problema
		# Input: estado, que es una np.matrix(8x8)
		# Output: True/False
		# print("Determinando si hay exactamente ocho reinas...")
		num_reinas = estado.sum()
		if num_reinas != 8:
			# print("Numero incorrecto de reinas!")
			return False
		else:
			# print("Determinando si las reinas no se atacan...")
			# print("Buscando reina por fila...")
			filas = [i[0] for i in estado.sum(axis=1).tolist()]
			if any(i>1 for i in filas):
				# print("Dos reinas en la misma fila!")
				return False
			else:
				# print("Buscando reina por columna...")
				columnas = estado.sum(axis=0).tolist()[0]
				if any(j>1 for j in columnas):
					# print("Dos reinas en la misma columna!")
					return False
				else:
					for x in range(8):
						for y in range(8):
							if estado[y, x]==1:
								# print("Reina encontrada en (" + str(x) + ", " + str(y) + ")")
								# print("Buscando otra reina en la misma diagonal...")
								dif = np.abs(x-y)
								offset_x = 0
								offset_y = 0
								for i in range(1, 8 - dif):
									if (y + i) == 8:
										offset_x = - (x + i)
										offset_y = dif
									if (x + i) == 8:
										offset_x = dif
										offset_y = - (y + i)
									xB = (x + i + offset_x) % 8
									yB = (y + i + offset_y) % 8
									if estado[yB, xB] == 1:
										#print("Dos reinas en la misma diagonal!")
										return False

								# print("Buscando otra reina en la misma transversal...")
								dif1 = np.abs((7-x)-y)
								# print("\n Dif", dif1)
								offset_x = 0
								offset_y = 0
								for i in range(1, 8 - dif1):
									xB = (x + i + offset_x) % 8
									yB = (y - i + offset_y) % 8
									# print("(" + str(xB) + ", " + str(yB) + ")", end="")
									if estado[yB, xB]==1:
										# print("Dos reinas en la misma transversal!")
										return False
									if yB == 0:
										offset_x = - (x + i + 1)
										offset_y = x + i + 1
									if xB == 7:
										offset_x = y - (i + 1) - 7
										offset_y = 8 - (y - i)

		return True

	def costo(self, estado, accion):
		return 1

	def codigo(self, estado):
		return str(estado.flatten())[2:-2]
    
    
class JarrasAgua:

	'''
	Problema de las jarras de agua: Suponga que usted cuenta con dos jarras de agua, una de tres litros y otra de cuatro, y que también cuenta con acceso a una llave de agua para llenar las jarras. ¿Cómo puede obtener exáctamente dos litros de agua en la jarra de cuatro litros?
	'''
	def __init__(self):
		self.estado_inicial = (0,0)

	def render(self, estado):
		# Dibuja el estado de las jarras
		# Input: estado, que es una pareja (x,y)
		fig, axes = plt.subplots()

		x, y = estado

		# Cargando imagen de la jarra de 4 litros
		jarra4 = plt.imread("./imagenes/Agua/jarra.png")
		imagebox = OffsetImage(jarra4, zoom=0.8)
		imagebox.image.axes = axes
		ab = AnnotationBbox(
		imagebox,
		[0.2, 0.45],
		frameon=False
		)
		axes.add_artist(ab)
		offsetbox = TextArea(str(x), textprops={'fontsize':'x-large'})
		ab = AnnotationBbox(offsetbox, (0.2,0))
		axes.add_artist(ab)

		# Cargando imagen de la jarra de 3 litros
		jarra3 = plt.imread("./imagenes/Agua/jarra.png")
		imagebox = OffsetImage(jarra3, zoom=0.7)
		imagebox.image.axes = axes
		ab = AnnotationBbox(
		imagebox,
		[0.7, 0.42],
		frameon=False
		)
		axes.add_artist(ab)
		offsetbox = TextArea(str(y), textprops={'fontsize':'x-large'})
		ab = AnnotationBbox(offsetbox, (0.7,0))
		axes.add_artist(ab)

		if x>0:
			# Llenando la jarra de 4 litros
			aguaX = plt.imread("./imagenes/Agua/agua" + str(x) + ".png")
			imagebox = OffsetImage(aguaX, zoom=0.4)
			y_offsets = [0.25, 0.32, 0.39, 0.45]
			imagebox.image.axes = axes
			ab = AnnotationBbox(
			imagebox,
			[0.2, y_offsets[x-1]],
			frameon=False
			)
			axes.add_artist(ab)

		if y>0:
			# Llenando la jarra de 3 litros
			aguaY = plt.imread("./imagenes/Agua/agua" + str(y) + ".png")
			imagebox = OffsetImage(aguaY, zoom=0.34)
			y_offsets = [0.3, 0.36, 0.41]
			imagebox.image.axes = axes
			ab = AnnotationBbox(
			imagebox,
			[0.7, y_offsets[y-1]],
			frameon=False
			)
			axes.add_artist(ab)

		axes.axis('off')
		return axes

	def pintar_accion(self, estado, accion):
		# Dibuja el estado de las jarras
		# Input: estado, que es una pareja (x,y)
		fig, axes = plt.subplots()

		x, y = estado

		# Cargando imagen de la jarra de 4 litros
		jarra4 = plt.imread("./imagenes/Agua/jarra.png")
		imagebox = OffsetImage(jarra4, zoom=0.8)
		imagebox.image.axes = axes
		ab = AnnotationBbox(
		imagebox,
		[0.2, 0.45],
		frameon=False
		)
		axes.add_artist(ab)
		offsetbox = TextArea(str(x), textprops={'fontsize':'x-large'})
		ab = AnnotationBbox(offsetbox, (0.2,0))
		axes.add_artist(ab)

		# Cargando imagen de la jarra de 3 litros
		jarra3 = plt.imread("./imagenes/Agua/jarra.png")
		imagebox = OffsetImage(jarra3, zoom=0.7)
		imagebox.image.axes = axes
		ab = AnnotationBbox(
		imagebox,
		[0.7, 0.42],
		frameon=False
		)
		axes.add_artist(ab)
		offsetbox = TextArea(str(y), textprops={'fontsize':'x-large'})
		ab = AnnotationBbox(offsetbox, (0.7,0))
		axes.add_artist(ab)

		if x>0:
			# Llenando la jarra de 4 litros
			aguaX = plt.imread("./imagenes/Agua/agua" + str(x) + ".png")
			imagebox = OffsetImage(aguaX, zoom=0.4)
			y_offsets = [0.25, 0.32, 0.39, 0.45]
			imagebox.image.axes = axes
			ab = AnnotationBbox(
			imagebox,
			[0.2, y_offsets[x-1]],
			frameon=False
			)
			axes.add_artist(ab)

		if y>0:
			# Llenando la jarra de 3 litros
			aguaY = plt.imread("./imagenes/Agua/agua" + str(y) + ".png")
			imagebox = OffsetImage(aguaY, zoom=0.34)
			y_offsets = [0.3, 0.36, 0.41]
			imagebox.image.axes = axes
			ab = AnnotationBbox(
			imagebox,
			[0.7, y_offsets[y-1]],
			frameon=False
			)
			axes.add_artist(ab)

		if accion == 1:
			imagen = "./imagenes/Agua/flecha_derecha.png"
			xy = [0.1, 0.97]

		if accion == 2:
			imagen = "./imagenes/Agua/flecha_izquierda.png"
			xy = [0.8, 0.95]

		if accion == 3:
			imagen = "./imagenes/Agua/flecha_izquierda.png"
			xy = [0, 0.97]

		if accion == 4:
			imagen = "./imagenes/Agua/flecha_derecha.png"
			xy = [0.85, 0.9]

		if accion == 5:
			imagen = "./imagenes/Agua/flecha_derecha.png"
			xy = [0.55, 0.9]

		if accion == 6:
			imagen = "./imagenes/Agua/flecha_izquierda.png"
			xy = [0.35, 0.97]

		# Pintando flecha
		flecha = plt.imread(imagen)
		imagebox = OffsetImage(flecha, zoom=0.1)
		imagebox.image.axes = axes
		ab = AnnotationBbox(
		imagebox,
		xy,
		frameon=False
		)
		axes.add_artist(ab)

		axes.axis('off')

		return axes

	def pintar_transicion(self, estado, accion):
		clear_output(wait=True)
		self.render(estado)
		plt.show()
		sleep(.5)
		clear_output(wait=True)
		self.pintar_accion(estado, accion)
		plt.show()
		sleep(.5)
		clear_output(wait=True)
		estado = self.transicion(estado, accion)
		self.render(estado)
		plt.show()
		sleep(.5)

	def acciones_aplicables(self, estado):
		# Devuelve una lista de números que representan
		# la acción permitida, de acuerdo a la codificación
		# presentada en al formalización del problema más arriba.
		# Input: estado, que es una pareja (x,y)
		# Output: lista de indices (x,y)
		x, y = estado
		acciones = [1, 2, 3, 4, 5, 6]
		if x == 0:
			acciones.remove(3)
			acciones.remove(5)
		if y == 0:
			acciones.remove(4)
			acciones.remove(6)
		if x == 4:
			acciones.remove(1)
		if y == 3:
			acciones.remove(2)
		return acciones

	def transicion(self, estado, accion):
		# Devuelve el estado correspondiente
		# Input: estado, que es una pareja (x,y)
		#        accion, entero de 1 a 6
		# Output: estado, que es una pareja (x,y)
		x, y = estado
		if accion == 1:
			return (4,y)
		if accion == 2:
			return (x,3)
		if accion == 3:
			return (0,y)
		if accion == 4:
			return (x,0)
		if accion == 5:
			d = x if y+x < 3 else 3-y
			return (x-d,y+d)
		if accion == 6:
			d = y if y+x < 4 else 4-x
			return (x+d,y-d)

	def test_objetivo(self, estado):
		# Devuelve True/False dependiendo si el estado
		# resuelve el problema
		# Input: estado, que es una np.matrix(8x8)
		# Output: True/False
		# print("Determinando si hay exactamente ocho reinas...")
		x, y = estado
		return x == 2

	def costo(self, estado, accion):
		return 1

	def codigo(self, estado):
		x, y = estado
		return f"{x}-{y}"

    
    
class ViajeRumania:

	'''
	Problema del viaje a Rumania: Planear el camino más corto de una ciudad inicial a una ciudad final.
	'''
	def __init__(self, estado_inicial='Arad', ciudad_objetivo='Bucharest'):
		self.estado_inicial = estado_inicial
		self.ciudad_objetivo = ciudad_objetivo
		self.rutas = {'Oradea':['Zerind', 'Sibiu'],\
		'Zerind':['Arad', 'Oradea'],\
		'Arad':['Timisoara', 'Sibiu', 'Zerind'],\
		'Timisoara':['Lugoj', 'Arad'],\
		'Lugoj':['Mehadia', 'Timisoara'],\
		'Mehadia':['Drobeta', 'Lugoj'],\
		'Drobeta':['Craiova', 'Mehadia'],\
		'Sibiu':['Fagaras', 'Rimnicu Vilcea', 'Arad', 'Oradea'],\
		'Rimnicu Vilcea':['Craiova', 'Pitesti', 'Sibiu'],\
		'Craiova':['Pitesti', 'Drobeta', 'Rimnicu Vilcea'],\
		'Fagaras':['Bucharest', 'Sibiu'],\
		'Pitesti':['Bucharest', 'Craiova', 'Rimnicu Vilcea'],\
		'Bucharest':['Giurgiu', 'Urziceni', 'Fagaras', 'Pitesti'],\
		'Giurgiu':['Bucharest'],\
		'Urziceni':['Vaslui', 'Hirsova', 'Bucharest'],\
		'Vaslui':['Iasi', 'Urziceni'],\
		'Iasi':['Neamt', 'Vaslui'],\
		'Neamt':['Iasi'],\
		'Hirsova':['Eforie', 'Urziceni'],\
		'Eforie':['Hirsova']
		}
		self.coordenadas = {'Oradea': (-378.39823252974577, 343.17197064259227),
		'Zerind': (-410.21550133104574, 288.6280812689352),
		'Arad': (-435.21478396063856, 232.9478608666603),
		'Timisoara': (-432.94212190340284, 114.76943389040338),
		'Lugoj': (-332.9449913850316, 69.31619274568916),
		'Mehadia': (-326.1270052133244, 14.772303372032118),
		'Drobeta': (-332.9449913850316, -42.04424805886064),
		'Sibiu': (-272.7194468682852, 182.94929560747468),
		'Rimnicu Vilcea': (-236.3568539525139, 115.90576491902122),
		'Craiova': (-217.03922646601035, -55.680220402274905),
		'Fagaras': (-130.67806829105334, 168.17699223544255),
		'Pitesti': (-109.0877787473141, 53.40755834503919),
		'Bucharest': (0.0, 0.0),
		'Giurgiu': (-37.49892394438922, -81.81583406048557),
		'Urziceni': (79.54317200324986, 29.544606744064236),
		'Vaslui': (152.2683578347926, 163.63166812097114),
		'Iasi': (103.40612360422482, 249.99282629592813),
		'Neamt': (7.9543172003249865, 294.3097364120245),
		'Hirsova': (188.63095075056395, 30.68093777268209),
		'Eforie': (229.53886778080675, -51.134896287803485)}
		self.distancias = {ciudad:{city:int(self._hallar_distancia(self.coordenadas[ciudad], self.coordenadas[city])) for city in self.rutas[ciudad]} for ciudad in self.rutas.keys()}
	
	def _hallar_distancia(self, x, y):
		return np.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)
        
	def render(self, estado):
		G = nx.Graph()
		G.add_nodes_from(self.coordenadas.keys())
		list_edges = [[(city, x, {'distancia':self.distancias[city][x]}) for x in self.rutas[city]] for city in self.rutas.keys()]
		list_edges = [item for sublist in list_edges for item in sublist]
		G.add_edges_from(list_edges, color='red')
		order = {ciudad:list(self.coordenadas[ciudad]) for ciudad in self.coordenadas.keys()}
		options = {
			'node_color': 'green',
			'node_size': 10,
			'verticalalignment':'bottom',
			'edge_color': 'red',
			'width': 1,
		}
		fig = plt.figure()
		ax = fig.add_subplot()
		circle1 = patches.Circle(self.coordenadas[estado], radius=15, color='green')
		nx.draw_networkx(G,pos=order, font_weight='bold', **options)
		edge_labels = nx.get_edge_attributes(G, 'distancia')
		nx.draw_networkx_edge_labels(G, order, edge_labels)
		ax.add_patch(circle1)
		# plt.savefig('Rumania.png', dpi=300)
		plt.show()

	def acciones_aplicables(self, estado):
		# Devuelve una lista de ciudades a las que se puede llegar
		# desde la ciudad descrita en estado
		# Input: estado, nombre de una ciudad
		# Output: lista de ciudades
		return self.rutas[estado]

	def transicion(self, estado, accion):
		# Devuelve la ciudad a la que se va
		# Input: estado, que es una ciudad
		#        accion, que es una ciudad
		# Output: accion, que es una ciudad
		return accion

	def test_objetivo(self, estado):
		# Devuelve True/False dependiendo si el estado
		# resuelve el problema
		# Input: estado, que es una ciudad
		# Output: True/False
		return estado == self.ciudad_objetivo

	def costo(self, estado, accion):
		# Devuelve la distancia desde estado hasta accion (que es una ciudad)
		# Input: 
		#        estado, que es una ciudad
		#        accion, que es una ciudad
		# Output: distancia de acuerdo al diccionario rutas
		return self.distancias[estado][accion]

	def codigo(self, estado):
		return estado

    
    
class Rompecabezas:

    def __init__(self, estado_inicial=np.reshape(np.random.choice(9, 9, replace=False), (3,3)), objetivo=np.matrix([[0,1,2], [3,4,5], [6,7,8]])):
        self.estado_inicial = estado_inicial
        self.objetivo = objetivo

    def render(self, estado):
        if isinstance(estado, list):
            estado = np.matrix(estado)
        # Dibuja el tablero correspondiente al estado
        # Input: estado, que es una np.matrix
        fig, axes = plt.subplots()
        # Dibujo el tablero
        step = 1./3
        offset = 0.001
        tangulos = []
        # Borde del tablero
        tangulos.append(patches.Rectangle((0,0),0.998,0.998,\
            facecolor='cornsilk',\
            edgecolor='black',\
            linewidth=2))
        # Creo las lÃ­neas del tablero
        for j in range(8):
            locacion = j * step
            # Crea linea horizontal en el rectangulo
            tangulos.append(patches.Rectangle(*[(0, locacion), 1, 0.008],\
            facecolor='black'))
            # Crea linea vertical en el rectangulo
            tangulos.append(patches.Rectangle(*[(locacion, 0), 0.008, 1],\
            facecolor='black'))
        for t in tangulos:
            axes.add_patch(t)
        # Cargando numeros
        offsetX = 0.135
        offsetY = 0.11
        for i in range(1,9):
            x, y = np.where(estado.T == i)
            X = x[0]
            Y = y[0]
            axes.text(X*step+offsetX, (2-Y)*step+offsetY, str(i), fontsize=42)
            axes.axis('off')
        return axes

    def pintar_camino(self, camino):
        estados = [self.estado_inicial]
        for transicion in camino:
        	estados.append(self.transicion(estados[-1], transicion))
        for estado in estados:
        	clear_output(wait=True)
        	self.render(estado)
        	plt.show()
        	sleep(1)

    def acciones_aplicables(self, estado):
        # Devuelve una lista de fichas que es posible mover
        # y en qué dirección
        # Input: estado, que es una np.matrix(8x8)
        # Output: lista de parejas ((x1,y1), (x2,y2))
        # Es decir, la ficha en la posición (x1,y1) puede moverse a (x2,y2)
        if isinstance(estado, list):
            estado = np.matrix(estado)
        y, x = np.where(estado == 0)
        y = y[0]
        x = x[0]
        if x == 0:
            if y == 0:
                return [((x + 1, y), (x, y)),
                        ((x, y + 1), (x, y))
                       ]
            elif y == 2:
                return [((x + 1, y), (x, y)),
                        ((x, y - 1), (x, y))
                       ]
            else:
                return [((x + 1, y), (x, y)),
                        ((x, y + 1), (x, y)),
                        ((x, y - 1), (x, y))
                       ]
        if x == 2:
            if y == 0:
                return [((x - 1, y), (x, y)),
                        ((x, y + 1), (x, y))
                       ]
            elif y == 2:
                return [((x - 1, y), (x, y)),
                        ((x, y - 1), (x, y))
                       ]
            else:
                return [((x - 1, y), (x, y)),
                        ((x, y + 1), (x, y)),
                        ((x, y - 1), (x, y))
                       ]
        else:
            if y == 0:
                return [((x - 1, y), (x, y)),
                        ((x + 1, y), (x, y)),
                        ((x, y + 1), (x, y))
                       ]
            elif y == 2:
                return [((x - 1, y), (x, y)),
                        ((x + 1, y), (x, y)),
                        ((x, y - 1), (x, y))
                       ]
            else:
                return [((x - 1, y), (x, y)),
                        ((x + 1, y), (x, y)),
                        ((x, y + 1), (x, y)),
                        ((x, y - 1), (x, y))
                       ]

    def transicion(self, estado, indices):
        # Devuelve el tablero moviendo la ficha en indice
        # Input: estado, que es una np.matrix(8x8)
        #        indice, de la forma ((x1,y1), (x2,y2))
        # Output: estado, que es una np.matrix(8x8)
        if isinstance(estado, list):
            estado = np.matrix(estado)
        s = copy.deepcopy(estado)
        x1, y1 = indices[0]
        x2, y2 = indices[1]
        s[y2, x2] = estado[y1, x1]
        s[y1, x1] = 0
        return s

    def test_objetivo(self, estado):
        # Devuelve True/False dependiendo si el estado
        # resuelve el problema
        # Input: estado, que es una np.matrix(8x8)
        # Output: True/False
        k = list(np.reshape(estado, (9,1)))
        k = [x[0] for x in k]
        o = list(np.reshape(self.objetivo, (9,1)))
        o = [x[0] for x in o]
        return (k == o)

    def costo(self, estado, accion):
        return 1

    def codigo(self, estado):
        inicial = True
        for fila in estado:
            for simbolo in fila:
            	if inicial:
            		cadena = str(simbolo)
            		inicial = False
            	else:
            		cadena += "-" + str(simbolo)
        return cadena
