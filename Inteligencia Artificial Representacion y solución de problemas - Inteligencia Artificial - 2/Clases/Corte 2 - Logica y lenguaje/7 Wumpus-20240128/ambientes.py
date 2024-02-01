import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnnotationBbox, OffsetImage, TextArea
import numpy as np
from random import choice, sample

def flatten(list_of_lists:list) -> list:
    '''
    Flattens a list of lists
    '''
    return [item for lista in list_of_lists for item in lista]

class Wumpus:

    def __init__(self, wumpus=None, oro=None, pozos=None, aleatorio=False):
        casillas = [(x, y) for x in range(4) for y in range(4)]
        casillas_sin_inicial = [casilla for casilla in casillas if casilla != (0,0)]
        if wumpus is None:
            self.wumpus = choice(casillas_sin_inicial)
        else:
            self.wumpus = wumpus
        self.wumpus_vivo = True
        self.hedor = self.adyacentes(self.wumpus)
        if oro is None:
            self.oro = choice(casillas)
        else:
            self.oro = oro
        self.oro_tomado = False
        if pozos is None:
            self.pozos = sample(casillas_sin_inicial, int(len(casillas_sin_inicial)*0.2))
        else:
            self.pozos = pozos
        self.brisa = flatten([self.adyacentes(c) for c in self.pozos])
        self.agente = (0, 0)
        self.flecha = True
        self.dir_agente = 'este'
        self.puntaje = 0
        self.done = False
        self.grito = False # para determinar cuándo el wumpus grita de agonía
        self.bump = False # para determinar cuándo el agente golpea un muro
        self.mensaje = ''
        self.aleatorio = aleatorio

    def reset(self):
        if self.aleatorio:
            casillas = [(x, y) for x in range(4) for y in range(4)]
            casillas_sin_inicial = [casilla for casilla in casillas if casilla != (0,0)]
            self.wumpus = choice(casillas_sin_inicial)
            self.oro = choice(casillas)
            self.pozos = sample(casillas_sin_inicial, int(len(casillas_sin_inicial)*0.2))        
        self.hedor = self.adyacentes(self.wumpus)
        self.brisa = flatten([self.adyacentes(c) for c in self.pozos])
        self.wumpus_vivo = True
        self.oro_tomado = False
        self.agente = (0, 0)
        self.flecha = True
        self.dir_agente = 'este'
        self.puntaje = 0
        self.done = False
        self.grito = False # para determinar cuándo el wumpus grita de agonía
        self.bump = False # para determinar cuándo el agente golpea un muro
        self.mensaje = ''
        return self.para_sentidos()

    def truncar(self, x):
        if x < 0:
            return 0
        elif x > 3:
            return 3
        else:
            return x

    def adyacentes(self, casilla):
        x, y = casilla
        adyacentes = [
            (self.truncar(x - 1), y), (self.truncar(x + 1), y),
            (x, self.truncar(y - 1)), (x, self.truncar(y + 1))
        ]
        adyacentes = [c for c in adyacentes if c != casilla]
        return adyacentes

    def pintar_todo(self):
        # Dibuja el tablero correspondiente al estado
        fig, axes = plt.subplots(figsize=(6, 6))

        # Dibujo el tablero
        step = 1./4
        offset = 0.001
        tangulos = []

        # Borde del tablero
        tangulos.append(patches.Rectangle((0,0),0.998,0.998,\
                                          facecolor='cornsilk',\
                                         edgecolor='black',\
                                         linewidth=2))

        # Creo las líneas del tablero
        for j in range(4):
            locacion = j * step
            # Crea linea horizontal en el rectangulo
            tangulos.append(patches.Rectangle(*[(0, locacion), 1, 0.008],\
                    facecolor='black'))
            # Crea linea vertical en el rectangulo
            tangulos.append(patches.Rectangle(*[(locacion, 0), 0.008, 1],\
                    facecolor='black'))

        for t in tangulos:
            axes.add_patch(t)

        # Cargando imagen del heroe
        arr_img_hero = plt.imread("./imagenes/hero_" + self.dir_agente + ".png", format='png')
        image_hero = OffsetImage(arr_img_hero, zoom=0.3)
        image_hero.image.axes = axes

        # Cargando imagen del Wumpus
        if self.wumpus_vivo:
            arr_img_wumpus = plt.imread("./imagenes/wumpus.png", format='png')
        else:
            arr_img_wumpus = plt.imread("./imagenes/wumpus_muerto.png", format='png')
        image_wumpus = OffsetImage(arr_img_wumpus, zoom=0.45)
        image_wumpus.image.axes = axes

        # Cargando imagen del hedor
        arr_img_stench = plt.imread("./imagenes/stench.png", format='png')
        image_stench = OffsetImage(arr_img_stench, zoom=0.35)
        image_stench.image.axes = axes

        # Cargando imagen del oro
        arr_img_gold = plt.imread("./imagenes/gold.png", format='png')
        image_gold = OffsetImage(arr_img_gold, zoom=0.25)
        image_gold.image.axes = axes

        # Cargando imagen del pozo
        arr_img_pit = plt.imread("./imagenes/pit.png", format='png')
        image_pit = OffsetImage(arr_img_pit, zoom=0.35)
        image_pit.image.axes = axes

        # Cargando imagen de la brisa
        arr_img_breeze = plt.imread("./imagenes/breeze.png", format='png')
        image_breeze = OffsetImage(arr_img_breeze, zoom=0.35)
        image_breeze.image.axes = axes

        offsetX = 0.125
        offsetY = 0.125

        for casilla in self.pozos:
            # Pintando un pozo
            X, Y = casilla
            ab = AnnotationBbox(
                image_pit,
                [(X*step) + offsetX, (Y*step) + offsetY],
                frameon=False)
            axes.add_artist(ab)

        for casilla in self.hedor:
            # Pintando el hedor
            X, Y = casilla
            ab = AnnotationBbox(
                image_stench,
                [(X*step) + offsetX, (Y*step) + offsetY - 0.075],
                frameon=False)
            axes.add_artist(ab)

        for casilla in self.brisa:
            # Pintando la brisa
            X, Y = casilla
            ab = AnnotationBbox(
                image_breeze,
                [(X*step) + offsetX, (Y*step) + offsetY + 0.075],
                frameon=False)
            axes.add_artist(ab)

        # Pintando el wumpus
        X, Y = self.wumpus
        ab = AnnotationBbox(
            image_wumpus,
            [(X*step) + offsetX, (Y*step) + offsetY],
            frameon=False)
        axes.add_artist(ab)

        # Pintando el heroe
        X, Y = self.agente
        ab = AnnotationBbox(
            image_hero,
            [(X*step) + offsetX, (Y*step) + offsetY],
            frameon=False)
        axes.add_artist(ab)

        # Pintando el oro
        if not self.oro_tomado:
            X, Y = self.oro
            ab = AnnotationBbox(
                image_gold,
                [(X*step) + offsetX, (Y*step) + offsetY],
                frameon=False)
            axes.add_artist(ab)

        axes.axis('off')
        plt.show()

    def render(self):
        # Dibuja el tablero correspondiente al estado
        fig, axes = plt.subplots(figsize=(6, 6))

        # Dibujo el tablero
        step = 1./4
        offset = 0.001
        tangulos = []

        # Borde del tablero
        tangulos.append(patches.Rectangle((0,0),0.998,0.998,\
                                            facecolor='cornsilk',\
                                            edgecolor='black',\
                                            linewidth=2))

        # Creo las líneas del tablero
        for j in range(4):
            locacion = j * step
            # Crea linea horizontal en el rectangulo
            tangulos.append(patches.Rectangle(*[(0, locacion), 1, 0.008],\
                    facecolor='black'))
            # Crea linea vertical en el rectangulo
            tangulos.append(patches.Rectangle(*[(locacion, 0), 0.008, 1],\
                    facecolor='black'))

        for t in tangulos:
            axes.add_patch(t)

        # Cargando imagen del heroe
        arr_img_hero = plt.imread("./imagenes/hero_" + self.dir_agente + ".png", format='png')
        image_hero = OffsetImage(arr_img_hero, zoom=0.3)
        image_hero.image.axes = axes

        # Cargando imagen del Wumpus
        if self.wumpus_vivo:
            arr_img_wumpus = plt.imread("./imagenes/wumpus.png", format='png')
        else:
            arr_img_wumpus = plt.imread("./imagenes/wumpus_muerto.png", format='png')
        image_wumpus = OffsetImage(arr_img_wumpus, zoom=0.45)
        image_wumpus.image.axes = axes

        # Cargando imagen del hedor
        arr_img_stench = plt.imread("./imagenes/stench.png", format='png')
        image_stench = OffsetImage(arr_img_stench, zoom=0.35)
        image_stench.image.axes = axes

        # Cargando imagen del oro
        arr_img_gold = plt.imread("./imagenes/gold.png", format='png')
        image_gold = OffsetImage(arr_img_gold, zoom=0.25)
        image_gold.image.axes = axes

        # Cargando imagen del pozo
        arr_img_pit = plt.imread("./imagenes/pit.png", format='png')
        image_pit = OffsetImage(arr_img_pit, zoom=0.35)
        image_pit.image.axes = axes

        # Cargando imagen de la brisa
        arr_img_breeze = plt.imread("./imagenes/breeze.png", format='png')
        image_breeze = OffsetImage(arr_img_breeze, zoom=0.35)
        image_breeze.image.axes = axes

        offsetX = 0.125
        offsetY = 0.125

        casilla = self.agente

        if casilla in self.pozos:
            # Pintando un pozo
            X, Y = casilla
            ab = AnnotationBbox(
                image_pit,
                [(X*step) + offsetX, (Y*step) + offsetY],
                frameon=False)
            axes.add_artist(ab)

        if casilla in self.hedor:
            # Pintando el hedor
            X, Y = casilla
            ab = AnnotationBbox(
                image_stench,
                [(X*step) + offsetX, (Y*step) + offsetY - 0.075],
                frameon=False)
            axes.add_artist(ab)

        if casilla in self.brisa:
            # Pintando la brisa
            X, Y = casilla
            ab = AnnotationBbox(
                image_breeze,
                [(X*step) + offsetX, (Y*step) + offsetY + 0.075],
                frameon=False)
            axes.add_artist(ab)

        if casilla == self.wumpus:
            # Pintando el wumpus
            X, Y = self.wumpus
            ab = AnnotationBbox(
                image_wumpus,
                [(X*step) + offsetX, (Y*step) + offsetY],
                frameon=False)
            axes.add_artist(ab)

        # Pintando el heroe
        X, Y = casilla
        ab = AnnotationBbox(
            image_hero,
            [(X*step) + offsetX, (Y*step) + offsetY],
            frameon=False)
        axes.add_artist(ab)

        if casilla == self.oro:
            # Pintando el oro
            if not self.oro_tomado:
                X, Y = self.oro
                ab = AnnotationBbox(
                    image_gold,
                    [(X*step) + offsetX, (Y*step) + offsetY],
                    frameon=False)
                axes.add_artist(ab)

        axes.axis('off')
        plt.show()

    def step(self, accion):
        reward = -1
        if accion == 'agarrar':
            if (self.oro == self.agente) and (self.oro_tomado == False):
                reward += 1000
                self.oro_tomado = True
        elif accion == 'adelante':
            x, y = self.agente
            if self.dir_agente == 'este':
                self.agente = (self.truncar(x + 1), y)
                self.bump = True if self.truncar(x + 1) == x else False
            if self.dir_agente == 'oeste':
                self.agente = (self.truncar(x - 1), y)
                self.bump = True if self.truncar(x - 1) == x else False
            if self.dir_agente == 'norte':
                self.agente = (x, self.truncar(y + 1))
                self.bump = True if self.truncar(y + 1) == y else False
            if self.dir_agente == 'sur':
                self.agente = (x, self.truncar(y - 1))
                self.bump = True if self.truncar(y - 1) == y else False
        elif accion == 'salir':
            if self.agente == (0, 0):
                self.done = True
                # print("¡Juego terminado!")
                # print("Puntaje:", self.puntaje)
                self.mensaje = "Juego terminado!\n Puntaje: " + str(self.puntaje)
                # self.pintar_todo()
        elif accion == 'voltearIzquierda':
            if self.dir_agente == 'este':
                self.dir_agente = 'norte'
            elif self.dir_agente == 'oeste':
                self.dir_agente = 'sur'
            elif self.dir_agente == 'norte':
                self.dir_agente = 'oeste'
            elif self.dir_agente == 'sur':
                self.dir_agente = 'este'
        elif accion == 'voltearDerecha':
            if self.dir_agente == 'este':
                self.dir_agente = 'sur'
            elif self.dir_agente == 'oeste':
                self.dir_agente = 'norte'
            elif self.dir_agente == 'norte':
                self.dir_agente = 'este'
            elif self.dir_agente == 'sur':
                self.dir_agente = 'oeste'
        elif accion == 'disparar':
            reward -= 10
            if self.flecha:
                self.flecha = False
                if self.wumpus_vivo:
                    x_wumpus, y_wumpus = self.wumpus
                    x_heroe, y_heroe = self.agente
                    if (self.dir_agente == 'este') and ((x_heroe < x_wumpus) and (y_heroe == y_wumpus)):
                        self.wumpus_vivo = False
                        self.grito = True
                    if (self.dir_agente == 'oeste') and ((x_heroe > x_wumpus) and (y_heroe == y_wumpus)):
                        self.wumpus_vivo = False
                        self.grito = True
                    if (self.dir_agente == 'norte') and ((y_heroe < y_wumpus) and (x_heroe == x_wumpus)):
                        self.wumpus_vivo = False
                        self.grito = True
                    if (self.dir_agente == 'sur') and ((y_heroe > y_wumpus) and (x_heroe == x_wumpus)):
                        self.wumpus_vivo = False
                        self.grito = True
        else:
            raise Exception('¡Acción incorrecta!', accion)
        if self.agente in self.pozos:
            reward -= 1000
            self.done = True
            self.mensaje = "¡Juego terminado!\n" + "El héroe a caído en un pozo\n" + "Puntaje: " + str(self.puntaje +reward)
            print("¡Juego terminado!")
            print("El héroe a caído en un pozo")
            print("Puntaje:", self.puntaje + reward)
            self.pintar_todo()
        elif (self.agente == self.wumpus) and self.wumpus_vivo:
            reward -= 1000
            self.done = True
            self.mensaje = "¡Juego terminado!\n" + "El héroe ha sido devorado por el Wumpus\n" + "Puntaje: " + str(self.puntaje + reward)
            print("¡Juego terminado!")
            print("El héroe ha sido devorado por el Wumpus")
            print("Puntaje:", self.puntaje + reward)
            self.pintar_todo()
        self.puntaje += reward
        new_state = self.para_sentidos()
        return new_state, reward, self.done

    def para_sentidos(self):
        # Lista de sensores [hedor, brisa, brillo, batacazo, grito]
        hedor = 'hedor' if self.agente in self.hedor else None
        brisa = 'brisa' if self.agente in self.brisa else None
        brillo = 'brillo' if ((self.agente == self.oro) and not self.oro_tomado) else None
        batacazo = 'batacazo' if self.bump else None
        grito = 'grito' if self.grito else None
        return [hedor, brisa, brillo, batacazo, grito]


class Rejilla:
    '''
    Problema del tránsito por la rejilla
    desde donde está el héroe hasta una
    casilla objetivo
    Parámetros:
        - inicial, una casilla de la forma (x,y)
        - objetivo, una casilla de la forma (x,y)
        - seguras, una lista de casillas seguras
    '''
    
    def __init__(self, inicial, objetivo, seguras):
        self.estado_inicial = inicial
        self.estado_objetivo = objetivo
        self.seguras = seguras
        self.max = 3
    
    def adyacentes(self, casilla):
        def truncar(x):
            if x < 0:
                return 0
            elif x > self.max:
                return self.max
            else:
                return x
        x, y = casilla
        adyacentes = [
            (truncar(x-1), y), (truncar(x+1), y),
            (x, truncar(y-1)), (x, truncar(y+1))
        ]
        adyacentes = [c for c in adyacentes if c != casilla]
        return adyacentes
    
    def acciones_aplicables(self, estado):
        return [c for c in self.adyacentes(estado) if c in self.seguras]
    
    def transicion(self, estado, accion):
        return accion
       
    def test_objetivo(self, estado):
        return estado == self.estado_objetivo

    def heuristica(self, estado):
        x1, y1 = self.estado_objetivo
        x2, y2 = estado
        return np.sqrt((x1-x2)**2 + (y1-y2)**2)

    def costo(self, estado, accion):
        return 1
    
    def codigo(self, estado):
        x, y = estado
        return f"{x}-{y}"