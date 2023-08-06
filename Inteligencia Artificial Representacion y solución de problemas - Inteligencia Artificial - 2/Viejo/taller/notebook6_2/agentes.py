from logica import *
from entornos import *
from random import choice
from busqueda import *

class Agente:

	def __init__(self):
		self.perceptos = []
		self.acciones = []
		self.tabla = {}
		self.reglas = []
		self.base = LPQuery([])
		self.turno = 1
		self.loc = (0,0)

	def reaccionar(self, DEB=False):
		if len(self.acciones) == 0:
			self.programa(DEB)
		a = self.acciones.pop(0)
		self.turno += 1
		return a

	def interp_percepto(self, mundo):
		if mundo == 'laberinto':
			orden = ['frn_bloq_', 'izq_bloq_', 'der_bloq_', 'atr_bloq_']
		elif mundo == 'wumpus':
			orden = ['hedor_', 'brisa_', 'brillo_', 'batacazo_', 'grito_']
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

# METODOS DE ESTIMACIÓN DE ESTADO
	def estimar_estado(self, W):
		self.base.TELL(f'segura({self.loc[0]},{self.loc[1]})')
		cas_seguras = self.adyacentes_seguras()
		self.base.TELL('Y'.join([f'segura({c[0]},{c[1]})' for c in cas_seguras]))
		nueva_dir = self.nueva_direccion()
		self.base.TELL(nueva_dir)
		nueva_pos = self.nueva_posicion()
		self.base.TELL(nueva_pos)
		formulas = [d for d in self.base.datos if f'_{self.turno}' in d]
		formulas += [s for s in self.base.datos if 'segura' in s]
		formulas += self.fluentes_mapa_mental()
		formulas += self.brisa_pozo()
		formulas += self.hedor_wumpus()
		formulas += self.casilla_segura()
		formulas += self.casillas_visitadas()
		self.perceptos = W.para_sentidos()
		formulas += [self.interp_percepto(mundo='wumpus')]
		self.base = LPQuery(formulas)

	def casillas_visitadas(self):
		turno = self.turno
		# Guardamos las casillas visitadas
		visitadas = []
		casillas = [(x,y) for x in range(4) for y in range(4)]
		for c in casillas:
			x, y = c
			consulta = ASK(f'visitada({x},{y})_{turno}', 'success', self.base)
			if consulta:
				visitadas.append(f'visitada({x},{y})_{turno}')
		return visitadas

	def nueva_posicion(self):
		casillas = [self.loc] + self.adyacentes(self.loc)
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

	def solo_direccion(self):
		direcciones = ['o', 'e', 's', 'n']
		dir_direcciones = {'o':'oeste', 'e':'este', 's':'sur', 'n':'norte'}
		for d in direcciones:
			direccion = f'mirando_{d}_{self.turno}'
			if direccion in self.base.datos:
				return dir_direcciones[d]
		raise Exception('¡No se encontró dirección!')

	def cache(self):
		turno = self.turno
		casilla_actual = self.loc
		direccion = self.solo_direccion()
		cas_seguras = self.adyacentes_seguras()
		cas_seguras = [c for c in cas_seguras if c != casilla_actual]
		cas_visitadas = self.casillas_visitadas()
		cas_visitadas = [tuple([int(s[9]),int(s[11])]) for s in cas_visitadas]
		return turno, casilla_actual, direccion, cas_seguras, cas_visitadas

	def truncar(self, x):
		if x < 0:
			return 0
		elif x > 3:
			return 3
		else:
			return x

	def adyacentes(self, casilla):
		x, y = casilla
		adyacentes = [(self.truncar(x - 1), y), (self.truncar(x + 1), y),	(x, self.truncar(y - 1)), (x, self.truncar(y + 1))]
		adyacentes = [c for c in adyacentes if c != casilla]
		return adyacentes

	def brisa_pozo(self):
		turno = self.turno
		casillas = self.adyacentes(self.loc)
		x, y = self.loc
		formulas = []
		for c in casillas:
			x1, y1 = c
			formulas += [f'en({x},{y})_{turno}Y-brisa_{turno}>-pozo({x1},{y1})']
		return formulas

	def hedor_wumpus(self):
		turno = self.turno
		casillas = self.adyacentes(self.loc)
		x, y = self.loc
		formulas = []
		for c in casillas:
			x1, y1 = c
			formulas += [f'en({x},{y})_{turno}Y-hedor_{turno}>-wumpus({x1},{y1})']
		return formulas

	def casilla_segura(self):
		casillas = [(x,y) for x in range(4) for y in range(4)]
		formulas = []
		for c in casillas:
			x, y = c
			formulas += [f'-pozo({x},{y})Y-wumpus({x},{y})>segura({x},{y})']
		return formulas

	def fluentes_mapa_mental(self):
		turno = self.turno
		x, y = self.loc
		formulas = [
		# ACCIONES QUE NO CAMBIAN LA POSICIÓN
		f'en({x},{y})_{turno}YvoltearIzquierda_{turno}>en({x},{y})_{turno+1}',
		f'en({x},{y})_{turno}YvoltearDerecha_{turno}>en({x},{y})_{turno+1}',
		f'en({x},{y})_{turno}Yagarrar_{turno}>en({x},{y})_{turno+1}',
		# ACCIÓN QUE CAMBIA LA POSICIÓN
		f'en({x},{y})_{turno}Ymirando_o_{turno}Yadelante_{turno}>en({x-1},{y})_{turno+1}',
		f'en({x},{y})_{turno}Ymirando_e_{turno}Yadelante_{turno}>en({x+1},{y})_{turno+1}',
		f'en({x},{y})_{turno}Ymirando_s_{turno}Yadelante_{turno}>en({x},{y-1})_{turno+1}',
		f'en({x},{y})_{turno}Ymirando_n_{turno}Yadelante_{turno}>en({x},{y+1})_{turno+1}',
		# ACCIONES QUE NO CAMBIAN LA DIRECCIÓN
		f'mirando_o_{turno}Yadelante_{turno}>mirando_o_{turno+1}',
		f'mirando_s_{turno}Yadelante_{turno}>mirando_s_{turno+1}',
		f'mirando_e_{turno}Yadelante_{turno}>mirando_e_{turno+1}',
		f'mirando_n_{turno}Yadelante_{turno}>mirando_n_{turno+1}',
		f'mirando_o_{turno}Yagarrar_{turno}>mirando_o_{turno+1}',
		f'mirando_s_{turno}Yagarrar_{turno}>mirando_s_{turno+1}',
		f'mirando_e_{turno}Yagarrar_{turno}>mirando_e_{turno+1}',
		f'mirando_n_{turno}Yagarrar_{turno}>mirando_n_{turno+1}',
		# ACCIONES QUE CAMBIAN LA DIRECCIÓN
		f'mirando_o_{turno}YvoltearIzquierda_{turno}>mirando_s_{turno+1}',
		f'mirando_s_{turno}YvoltearIzquierda_{turno}>mirando_e_{turno+1}',
		f'mirando_e_{turno}YvoltearIzquierda_{turno}>mirando_n_{turno+1}',
		f'mirando_n_{turno}YvoltearIzquierda_{turno}>mirando_o_{turno+1}',
		f'mirando_o_{turno}YvoltearDerecha_{turno}>mirando_n_{turno+1}',
		f'mirando_n_{turno}YvoltearDerecha_{turno}>mirando_e_{turno+1}',
		f'mirando_e_{turno}YvoltearDerecha_{turno}>mirando_s_{turno+1}',
		f'mirando_s_{turno}YvoltearDerecha_{turno}>mirando_o_{turno+1}',
		]
		casillas = [(x,y) for x in range(4) for y in range(4)]
		for c in casillas:
			x, y = c
			formulas += [f'en({x},{y})_{turno}>visitada({x},{y})_{turno}', f'visitada({x},{y})_{turno}>visitada({x},{y})_{turno+1}']
		return formulas

	def adyacentes_seguras(self):
		casillas_seguras = []
		x, y = self.loc
		for a in self.adyacentes((x,y)) + [self.loc]:
			i, j = a
			objetivo = f'segura({i},{j})'
			res = ASK(objetivo, 'success', self.base)
			if res:
				casillas_seguras.append((i,j))
		return casillas_seguras

	def todas_seguras(self):
		casillas = [(x,y) for x in range(4) for y in range(4)]
		casillas_seguras = []
		for c in casillas:
			x, y = c
			objetivo = f'segura({x},{y})'
			if ASK(objetivo, 'success', self.base):
				casillas_seguras.append((x,y))
		return casillas_seguras

	def programa(self, DEB=False):
		acciones = []
		turno, casilla_actual, direccion, cas_seguras, cas_visitadas = self.cache()
		if DEB:
			print('Turno acutal:', turno)
			print('Casilla actual:', casilla_actual)
			print('Dirección actual:', direccion)
			print('Casillas adyacentes seguras:', cas_seguras)
			print('Casillas visitadas:', cas_visitadas)
		if ASK(f'brillo_{turno}','success',self.base):
			if DEB:
				print('¡Oh, el oro!')
			acciones.append('agarrar')
			R = Rejilla(casilla_actual, (0,0), self.todas_seguras())
			camino = greedy_search(R, manhattan)
			camino = [casilla_actual] + solucion(camino)
			acciones += acciones_camino(camino, direccion)
			acciones.append('salir')
		else:
			opciones = [casilla for casilla in cas_seguras if casilla not in cas_visitadas]
			if DEB:
				print('Casillas opcionales:', opciones)
			if len(opciones) > 0:
				casilla_ir = choice(opciones)
				if DEB:
					print('El agente quiere ir a la casilla', casilla_ir)
				camino = [casilla_actual, casilla_ir]
				acciones = acciones_camino(camino, direccion)
			elif len(cas_seguras) > 0:
				casilla_ir = choice(cas_seguras)
				if DEB:
					print('El agente quiere devolverse a la casilla', casilla_ir)
				camino = [casilla_actual, casilla_ir]
				acciones = acciones_camino(camino, direccion)
			else:
				print("¡Caso no contemplado!")
		self.acciones += acciones
