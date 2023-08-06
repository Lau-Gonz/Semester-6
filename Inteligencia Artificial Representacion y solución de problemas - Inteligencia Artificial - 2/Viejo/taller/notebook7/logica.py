import numpy as np

class ClausulaDefinida :
    '''
    Implementación de las cláusulas definidas
    Input: clausula, que es una cadena de la forma p1 ∧ ... ∧ pn ⇒ q
    '''

    def __init__(self, clausula) :
        self.nombre = clausula
        indice_conectivo = clausula.find('⇒')
        if indice_conectivo > 0:
            antecedente = clausula[:indice_conectivo].split('∧')
            consecuente = clausula[indice_conectivo + 1:]
        else:
            antecedente = clausula.split('∧')
            consecuente = ''
        self.antecedente = antecedente
        self.consecuente = consecuente

    def __str__(self):
        return self.nombre

class LPQuery:

    '''
    Implementación de una base de conocimiento.
    Input:  base_conocimiento_lista, que es una lista de cláusulas definidas
                de la forma p1 ∧ ... ∧ pn ⇒ q
    '''

    def __init__(self, base_conocimiento_lista) :
        self.hechos = []
        self.reglas = []
        self.atomos = []
        for formula in base_conocimiento_lista:
            self.TELL(formula)

    def __str__(self) :
        cadena = 'Hechos:\n'
        for hecho in self.hechos:
            cadena += hecho + '\n'
        cadena += '\nReglas:\n'
        for regla in self.reglas:
            cadena += regla.nombre + '\n'
        return cadena

    def reglas_aplicables(self, consecuente):
        return [r for r in self.reglas if r.consecuente == consecuente]

    def test_objetivo(self, literal):
        return literal in self.hechos

    def TELL(self, formula):
        indice_conectivo = formula.find('⇒')
        if indice_conectivo > 0:
            clausula = ClausulaDefinida(formula)
            self.reglas.append(clausula)
            for a in clausula.antecedente:
            	if '-' in a:
            		atomo = a[1:]
            	else:
                	atomo = a
            	if atomo not in self.atomos:
            		self.atomos.append(a)
            if '-' in clausula.consecuente:
            	atomo = clausula.consecuente[1:]
            else:
            	atomo = clausula.consecuente
            if atomo not in self.atomos:
            	self.atomos.append(atomo)
        elif formula not in self.hechos:
            self.hechos.append(formula)
            if '-' in formula:
            	atomo = formula[1:]
            else:
            	atomo = formula
            if atomo not in self.atomos:
            	self.atomos.append(atomo)

def and_or_graph_search(objetivo, base):
    return or_search(objetivo, base, [])

def or_search(consecuente, base, camino):
    if base.test_objetivo(consecuente):
        return 'success'
    elif consecuente in camino:
        return 'failure'
    reglas = base.reglas_aplicables(consecuente)
    if not reglas:
        return 'failure'
    for regla in reglas:
        plan = and_search(regla.antecedente, base, [consecuente] + camino)
        if plan != 'failure':
            return 'success'
    return 'failure'

def and_search(literales, base, camino):
    for literal in literales:
        plan = or_search(literal, base, camino)
        if plan == 'failure':
            return 'failure'
    return 'success'

def ASK(objetivo, valor, base):
    ask = and_or_graph_search(objetivo, base)
    return (ask == valor)