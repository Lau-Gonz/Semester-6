import numpy as np
from copy import deepcopy

def obtener_type(objeto):
    c = str(type(objeto))
    return c.split('.')[-1][:-2]

def sust(f, indice, v):
    f1 = deepcopy(f)
    if obtener_type(f) in ['Happens']:
        if v.tipo == 'evento':
            if f1.e_indice == indice:
                f1.e = v
        if v.tipo == 'instante':
            if f1.t_indice == indice:
                f1.t = v
    if obtener_type(f) in ['HoldsAt']:
        if v.tipo == 'fluente':
            if f1.f_indice == indice:
                f1.f = v
        if v.tipo == 'instante':
            if f1.t_indice == indice:
                f1.t = v
    if obtener_type(f) in ['Initiates', 'Terminates']:
        if v.tipo == 'evento':
            if f1.e_indice == indice:
                f1.e = v
        elif v.tipo == 'fluente':
            if f1.f_indice == indice:
                f1.f = v
        elif v.tipo == 'instante':
            if f1.t_indice == indice:
                f1.t = v
    if obtener_type(f) == 'Antes':
        if v.tipo == 'instante':
            if f1.t1_indice == indice:
                f1.t1 = v
            elif f1.t2_indice == indice:
                f1.t2 = v
    if obtener_type(f) == 'Negacion':
        f1.formula = sust(f.formula, indice, v)
    if obtener_type(f) == 'Regla':
        f1.antecedente = sust(f.antecedente, indice, v)
        f1.consecuente = sust(f.consecuente, indice, v)
    if obtener_type(f) == 'Y':
        formulas = [sust(sf, indice, v) for sf in f.formulas]
        f1.formulas = formulas
    if obtener_type(f) == 'Cuantificada':
        f1.formula = sust(f.formula, indice, v)
    return f1



class Tipo:
    def __init__(self, tipo):
        self.tipo = tipo

class Constante(Tipo):
    def __init__(self, tipo, nombre='', indice=0):
        super().__init__(tipo)
        self.nombre = nombre
        self.indice = indice

    def __str__(self):
        return self.nombre

class Fluente(Constante):
    def __init__(self, nombre, atomo, indice=0):
        super().__init__(tipo='fluente', nombre=nombre, indice=indice)
        self.formula = atomo

    def __str__(self):
        return f'f_{self.indice}'

class Evento(Constante):
    def __init__(self, nombre, sujeto='', objeto_d='', objeto_i='', lugar='', indice=0):
        super().__init__(tipo='evento', nombre=nombre, indice=indice)
        if sujeto != '':
            assert(sujeto.tipo in ['agente'])
        self.sujeto = sujeto
        self.objeto_d = objeto_d
        self.objeto_i = objeto_i
        if lugar != '':
            assert(lugar.tipo == 'lugar')
        self.lugar = lugar

    def __str__(self):
        return f'e_{self.indice}'

    def formular(self):
        formulas = [f'{self.nombre}({str(self)})']
        if self.sujeto != '':
            formulas.append(f'SUJETO({str(self)},{self.sujeto.nombre})')
        if self.objeto_d != '':
            formulas.append(f'OBJETO_D({str(self)},{self.objeto_d.nombre})')
        if self.objeto_i != '':
            formulas.append(f'OBJETO_I({str(self)},{self.objeto_i.nombre})')
        if self.lugar != '':
            formulas.append(f'EN({str(self)},{self.lugar.nombre})')
        return formulas

class Instante(Constante):
    def __init__(self, valor, indice=0):
        assert(valor == int(valor))
        super().__init__(tipo='instante', nombre=str(valor), indice=indice)
        self.valor = valor

    def __str__(self):
        return str(self.valor)

class Cuantificador(Tipo):
    def __init__(self, tipo, nombre, indice):
        super().__init__(tipo)
        assert(nombre in ['todo', 'existe'])
        self.nombre = nombre
        self.indice = indice

class Situacion:
    def __init__(self):
        self.eventos = []
        self.fluentes = []
        self.instantes = []
        self.entidades = {}
        self.predicados = []
        self.tipos = []
        self.todos = []
        self.lens = []
        self.D = None

    def nueva_entidad(self, tipo, nombre):
        try:
            n = len(self.entidades[tipo])
            self.entidades[tipo].append(Constante(tipo, nombre, n))
        except:
            n = 0
            self.entidades[tipo] = [Constante(tipo, nombre, n)]
        self.actualizar()

    def nuevo_evento(self, nombre, sujeto='', objeto_d='', objeto_i='', lugar=''):
        n = len(self.eventos)
        e = Evento(nombre.upper(), sujeto, objeto_d, objeto_i, lugar, n)
        self.eventos.append(e)
        self.actualizar()

    def nuevo_fluente(self, atomo, nombre=''):
        n = len(self.fluentes)
        if nombre == '':
            nombre = atomo.predicado.nombre
        f = Fluente(nombre, atomo)
        self.fluentes.append(f)
        self.actualizar()

    def nuevo_instante(self, valor=0):
        valores = [i.valor for i in self.instantes]
        if valor not in valores:
            n = len(self.instantes)
            f = Instante(valor, n)
            self.instantes.append(f)
        elif valor == 0:
            n = len(self.instantes)
            f = Instante(n, n)
            self.instantes.append(f)
        self.actualizar()

    def actualizar(self):
        self.tipos = list(self.entidades.keys())
        self.todos = [str(x) for x in self.eventos]
        self.todos += [str(x) for x in self.fluentes]
        self.todos += [str(x) for x in self.instantes]
        lista = [self.entidades[l] for l in self.tipos]
        lista = [item for sublist in lista for item in sublist]
        self.todos += [str(x) for x in lista]
        lista_e = [e.formular() for e in self.eventos]
        lista_e = [item for sublist in lista_e for item in sublist]
        lista_e = [x.split('(')[0] for x in lista_e]
        lista_e = list(set(lista_e))
        lista_f = list(set([f.formula.nombre for f in self.fluentes]))
        lista_EC = ['Happens', 'HoldsAt', 'Initiates', 'Terminates', 'Antes']
        self.predicados = lista_EC + lista_e + lista_f
        if not self.fluentes:
            m = 3
        else:
            m = max(max([len(x.formula.argumentos) for x in self.fluentes]), 3)
        self.lens = [len(self.predicados)] + [len(self.todos)]*m

    def crear_descriptor(self):
        self.actualizar()
        self.D = Descriptor(self.lens)

    def obtener_entidad(self, n):
        indice = n - len(self.eventos) - len(self.fluentes) - len(self.instantes)
        cortes = [len(self.entidades[tipo]) for tipo in self.tipos]
        for i, c in enumerate(cortes):
            if indice < c:
                return self.entidades[self.tipos[i]][indice]
        return None
        
    def formular(self,codigo):
        lista = self.D.inv(codigo)
        if lista[0] == 0:
            e = self.eventos[lista[1]]
            t = self.instantes[lista[2] - len(self.eventos) - len(self.fluentes)]
            return Happens(e.indice, t.indice, e, t)
        elif lista[0] == 1:
            f = self.fluentes[lista[1] - len(self.eventos)]
            t = self.instantes[lista[2] - len(self.eventos) - len(self.fluentes)]
            return HoldsAt(f.indice, t.indice, f, t)
        elif lista[0] == 2:
            e = self.eventos[lista[1]]
            f = self.fluentes[lista[2] - len(self.eventos)]
            t = self.instantes[lista[3] - len(self.eventos) - len(self.fluentes)]
            return Initiates(e.indice, f.indice, t.indice, e, f, t)
        elif lista[0] == 3:
            e = self.eventos[lista[1]]
            f = self.fluentes[lista[2] - len(self.eventos)]
            t = self.instantes[lista[3] - len(self.eventos) - len(self.fluentes)]
            return Terminates(e.indice, f.indice, t.indice, e, f, t)
        elif lista[0] == 4:
            t1 = self.instantes[lista[1] - len(self.eventos) - len(self.fluentes)]
            t2 = self.instantes[lista[2] - len(self.eventos) - len(self.fluentes)]
            return Antes(t1.indice, t2.indice, t1, t2)
        elif lista[0] > 4:
            pred = self.predicados[lista[0]]
            argumentos = [self.obtener_entidad(i) for i in lista[1:] if i > 0]
            tipos_argumentos = [x.tipo for x in argumentos]
            return Atomo(nombre=pred, tipos_argumentos=tipos_argumentos, argumentos=argumentos)

    def __str__(self):
        print('Instantes:', [i.nombre for i in self.instantes])
        cadena = '\nEntidades:\n'
        for tipo in self.entidades:
            cadena += f'\tTipo: {tipo}\n'
            for o in self.entidades[tipo]:
                cadena += '\t' + str(o) + '\n'
            cadena += '\n'
        cadena += 'Eventos:\n'
        for e in self.eventos:
            cadena += f'\t{str(e)}:\n'
            formulas = e.formular()
            for f in formulas:
                cadena += '\t' + str(f) + '\n'
            cadena += '\n'
        cadena += 'Fluentes:\n'
        for f in self.fluentes:
            cadena += f'\t{str(f)}: {str(f.formula)}\n'
        return cadena

class Predicado:
    def __init__(self, nombre, tipos_argumentos):
        self.nombre = nombre
        self.aridad = len(tipos_argumentos)
        self.tipos_argumentos = tipos_argumentos

class Formula:
    def __init__(self):
        pass

    def __str__(self):
        return str(self)

    def codificar(self, sit):
        if type(self) == Atomo:
            indice = sit.predicados.index(self.nombre)
            n = len(sit.lens) - len(self.argumentos) - 1
            ns = [sit.todos.index(str(x)) for x in self.argumentos]
            return sit.D.P([indice] + ns + [0]*n)
        elif type(self) == Happens:
            n = len(sit.lens) - 3
            ne = sit.todos.index(str(self.e))
            nt = sit.todos.index(str(self.t))
            return sit.D.P([0,ne,nt] + [0]*n)
        elif type(self) == HoldsAt:
            n = len(sit.lens) - 3
            nf = sit.todos.index(str(self.f))
            nt = sit.todos.index(str(self.t))
            return sit.D.P([1,nf,nt] + [0]*n)
        elif type(self) == Initiates:
            n = len(sit.lens) - 4
            ne = sit.todos.index(str(self.e))
            nf = sit.todos.index(str(self.f))
            nt = sit.todos.index(str(self.t))
            return sit.D.P([2,ne,nf,nt] + [0]*n)
        elif type(self) == Terminates:
            n = len(sit.lens) - 4
            ne = sit.todos.index(str(self.e))
            nf = sit.todos.index(str(self.f))
            nt = sit.todos.index(str(self.t))
            return sit.D.P([3,ne,nf,nt] + [0]*n)
        elif type(self) == Antes:
            n = len(sit.lens) - 3
            nt1 = sit.todos.index(str(self.t1))
            nt2 = sit.todos.index(str(self.t2))
            return sit.D.P([4,nt1,nt2] + [0]*n)
        elif type(self) == Negacion:
            return '-' + self.formula.codificar(sit)
        elif type(self) == Regla:
            return "(" + self.antecedente.codificar(sit) + '⇒' + self.consecuente.codificar(sit) + ")"
        elif type(self) == Y:
            lista = [f.codificar(sit) for f in self.formulas]
            return Ytoria(lista)
        elif type(self) == O:
            lista = [f.codificar(sit) for f in self.formulas]
            return Otoria(lista)
        elif type(self) == Cuantificada:
            if self.q.tipo in ['evento', 'fluente', 'instante']:
                lista = eval(f'self.sit.{self.q.tipo}s')
                assert(len(lista) > 0)
                n = self.q.indice
                cuantif = '∧' if self.q.nombre == 'todo' else '∨'
                formulas = [sust(self.formula, n, x) for x in lista]
            if len(formulas) > 1:
                if cuantif == '∧':
                    return Ytoria([f.codificar(sit) for f in formulas])
                elif cuantif == '∨':
                    return Otoria([f.codificar(sit) for f in formulas])
            else:
                return formulas[0].codificar(sit)

class Atomo(Formula):
    def __init__(self, nombre, tipos_argumentos, argumentos):
        self.nombre = nombre[0].upper() + nombre[1:].lower()
        self.predicado = Predicado(self.nombre, tipos_argumentos)
        assert(len(tipos_argumentos) == len(argumentos))
        for i, a in enumerate(argumentos):
            assert(a.tipo == tipos_argumentos[i]), f'{a.tipo}; {tipos_argumentos[i]}'
        self.argumentos = argumentos

    def __str__(self):
        cadena = self.predicado.nombre + '('
        inicial = True
        for a in self.argumentos:
            if inicial:
                cadena += str(a)
                inicial = False
            else:
                cadena += ',' + str(a)
        return cadena + ')'

class Happens(Formula):
    def __init__(self, e_indice, t_indice, e=None, t=None):
        self.e_indice = e_indice
        self.t_indice = t_indice
        self.e = e
        self.t = t

    def __str__(self):
        e = f'ev{self.e_indice}' if not self.e else str(self.e)
        t = f'ti{self.t_indice}' if not self.t else str(self.t)
        return f'Happens({e},{t})'

class HoldsAt(Formula):
    def __init__(self, f_indice, t_indice, f=None, t=None):
        self.f_indice = f_indice
        self.t_indice = t_indice
        self.f = f
        self.t = t

    def __str__(self):
        f = f'flu{self.f_indice}' if not self.f else str(self.f)
        t = f'ti{self.t_indice}' if not self.t else str(self.t)
        return f'HoldsAt({f},{t})'


class Initiates(Formula):
    def __init__(self, e_indice, f_indice, t_indice, e=None, f=None, t=None):
        self.e_indice = e_indice
        self.f_indice = f_indice
        self.t_indice = t_indice
        self.e = e
        self.f = f
        self.t = t

    def __str__(self):
        e = f'ev{self.e_indice}' if not self.e else str(self.e)
        f = f'flu{self.f_indice}' if not self.f else str(self.f)
        t = f'ti{self.t_indice}' if not self.t else str(self.t)
        return f'Initiates({e},{f},{t})'


class Terminates(Formula):
    def __init__(self, e_indice, f_indice, t_indice, e=None, f=None, t=None):
        self.e_indice = e_indice
        self.f_indice = f_indice
        self.t_indice = t_indice
        self.e = e
        self.f = f
        self.t = t

    def __str__(self):
        e = f'ev{self.e_indice}' if not self.e else str(self.e)
        f = f'flu{self.f_indice}' if not self.f else str(self.f)
        t = f'ti{self.t_indice}' if not self.t else str(self.t)
        return f'Terminates({e},{f},{t})'


class Antes(Formula):
    def __init__(self, t1_indice, t2_indice, t1=None, t2=None):
        self.t1_indice = t1_indice
        self.t2_indice = t2_indice
        self.t1 = t1
        self.t2 = t2

    def __str__(self):
        t1 = f'ti{self.t1_indice}' if not self.t1 else str(self.t1)
        t2 = f'ti{self.t2_indice}' if not self.t2 else str(self.t2)
        return f'{t1}<{t2}'

class Y(Formula):
    def __init__(self, formulas):
        assert(len(formulas) > 1)
#        types = ['Formula', 'Atomo', 'Happens', 'HoldsAt', 'Initiates', 'Terminates', 'Antes']
#        for f in formulas:
#            assert(obtener_type(f) in types)
        self.formulas = formulas

    def __str__(self):
        return Ytoria([str(f) for f in self.formulas])

class O(Formula):
    def __init__(self, formulas):
        assert(len(formulas) > 1)
#        types = ['Formula', 'Atomo', 'Happens', 'HoldsAt', 'Initiates', 'Terminates', 'Antes']
#        for f in formulas:
#            assert(obtener_type(f) in types)
        self.formulas = formulas

    def __str__(self):
        return Otoria([str(f) for f in self.formulas])

class Regla(Formula):
    def __init__(self, antecedente, consecuente):
        self.antecedente = antecedente
        self.consecuente = consecuente

    def __str__(self):
        return '(' + f'{str(self.antecedente)}⇒{str(self.consecuente)}' + ')'

class Negacion(Formula):
    def __init__(self, formula):
        self.formula = formula

    def __str__(self):
        return '-' + str(self.formula)

class Cuantificada(Formula):
    def __init__(self, cuantificador, formula, sit):
        self.q = cuantificador
        self.formula = formula
        self.sit = sit

    def __str__(self):
        if self.q.tipo in ['evento', 'fluente', 'instante']:
            lista = eval(f'self.sit.{self.q.tipo}s')
            assert(len(lista) > 0)
            n = self.q.indice
            cuantif = '∧' if self.q.nombre == 'todo' else '∨'
            formulas = [sust(self.formula, n, x) for x in lista]
        else:
            raise Exception('¡Oh, Oh, problemas!')
        if len(formulas) > 1:
            if cuantif == '∧':
                return Ytoria([str(f) for f in formulas])
            else:
                return Otoria([str(f) for f in formulas])
        else:
            return str(formulas[0])

class Descriptor :

    '''
    Codifica un descriptor de N argumentos mediante un solo caracter
    Input:  args_lista, lista con el total de opciones para cada
                     argumento del descriptor
            chrInit, entero que determina el comienzo de la codificación chr()
    Output: str de longitud 1
    '''

    def __init__ (self,args_lista,chrInit=256) :
        self.args_lista = args_lista
        assert(len(args_lista) > 0), "Debe haber por lo menos un argumento"
        self.chrInit = chrInit
        self.rango = [chrInit, chrInit + np.prod(self.args_lista)]

    def check_lista_valores(self,lista_valores) :
        for i, v in enumerate(lista_valores) :
            assert(v >= 0), "Valores deben ser no negativos"
            assert(v < self.args_lista[i]), f"Valor debe ser menor o igual a {self.args_lista[i]}"

    def codifica(self,lista_valores) :
        self.check_lista_valores(lista_valores)
        cod = lista_valores[0]
        n_columnas = 1
        for i in range(0, len(lista_valores) - 1) :
            n_columnas = n_columnas * self.args_lista[i]
            cod = n_columnas * lista_valores[i+1] + cod
        return cod

    def decodifica(self,n) :
        decods = []
        if len(self.args_lista) > 1:
            for i in range(0, len(self.args_lista) - 1) :
                n_columnas = np.prod(self.args_lista[:-(i+1)])
                decods.insert(0, int(n / n_columnas))
                n = n % n_columnas
        decods.insert(0, n % self.args_lista[0])
        return decods

    def P(self,lista_valores) :
        codigo = self.codifica(lista_valores)
        return chr(self.chrInit+codigo)

    def inv(self,codigo) :
        n = ord(codigo)-self.chrInit
        return self.decodifica(n)

def Ytoria(lista_forms):
    form = ''
    inicial = True
    for f in lista_forms:
        if inicial:
            form = f
            inicial = False
        else:
            form = '(' + form + '∧' + f + ')'
    return form

def Otoria(lista_forms):
    form = ''
    inicial = True
    for f in lista_forms:
        if inicial:
            form = f
            inicial = False
        else:
            form = '(' + form + '∨' + f + ')'
    return form

def max_letras(a):
    a = a.replace('∧', ',')
    a = a.replace('∨', ',')
    a = a.replace('⇒', ',')
    a = a.replace('(', '')
    a = a.replace('-', '')
    a = a.replace(')', '')
    a = a.split(',')
    a = [ord(x)-256 for x in a]
    a = list(set(a))
    a.sort()
    return max(a) + 1, a

def numero(x):
    if '-' in x:
        return - (ord(x[-1])-256)
    else:
        return ord(x)-256

def a_clausal(A):
    # Subrutina de Tseitin para encontrar la FNC de
    # la formula en la pila
    # Input: A (cadena) de la forma
    #                   p=-q
    #                   p=(q∧r)
    #                   p=(q∨r)
    #                   p=(q>r)
    # Output: B (cadena), equivalente en FNC
    assert(len(A)==4 or len(A)==7), f"Fórmula incorrecta! {A}"
    B = ''
    p = A[0]
    # print('p', p)
    if "-" in A:
        q = A[-1]
        # print('q', q)
        B = "-"+p+"∨-"+q+"∧"+p+"∨"+q
    elif "∧" in A:
        q = A[3]
        # print('q', q)
        r = A[5]
        # print('r', r)
        B = q+"∨-"+p+"∧"+r+"∨-"+p+"∧-"+q+"∨-"+r+"∨"+p
    elif "∨" in A:
        q = A[3]
        # print('q', q)
        r = A[5]
        # print('r', r)
        B = "-"+q+"∨"+p+"∧-"+r+"∨"+p+"∧"+q+"∨"+r+"∨-"+p
    elif "⇒" in A:
        q = A[3]
        # print('q', q)
        r = A[5]
        # print('r', r)
        B = q+"∨"+p+"∧-"+r+"∨"+p+"∧-"+q+"∨"+r+"∨-"+p
    elif "=" in A:
        q = A[3]
        # print('q', q)
        r = A[5]
        # print('r', r)
        #q∨-r∨-p∧-q∨r∨-p∧-q∨-r∨p∧q∨r∨p
        B = q+"∨"+"-"+r+"∨"+"-"+p+"∧"+"-"+q+"∨"+r+"∨"+"-"+p+"∧"+"-"+q+"∨"+"-"+r+"∨"+p+"∧"+q+"∨"+r+"∨"+p
    else:
        print(u'Error enENC(): Fórmula incorrecta!')
    B = B.split('∧')
    B = [c.split('∨') for c in B]
    return B

def tseitin(A):
    '''
    Algoritmo de transformacion de Tseitin
    Input: A (cadena) en notacion inorder
    Output: B (cadena), Tseitin
    '''
    # Creamos letras proposicionales nuevas
    m, l = max_letras(A)
    letrasp = [chr(x+256) for x in l]
    letrasp_tseitin = [chr(x) for x in range(m+256, m + 100000)]
    letrasp = letrasp + letrasp_tseitin
    L = [] # Inicializamos lista de conjunciones
    Pila = [] # Inicializamos pila
    i = -1 # Inicializamos contador de variables nuevas
    s = A[0] # Inicializamos símbolo de trabajo
    while len(A) > 0: # Recorremos la cadena
        # print("Pila:", Pila, " L:", L, " s:", s)
        if (s in letrasp) and (len(Pila) > 0) and (Pila[-1]=='-'):
            i += 1
            atomo = letrasp_tseitin[i]
            Pila = Pila[:-1]
            Pila.append(atomo)
            L.append(atomo + "=-" + s)
            A = A[1:]
            if len(A) > 0:
                s = A[0]
        elif s == ')':
            w = Pila[-1]
            O = Pila[-2]
            v = Pila[-3]
            Pila = Pila[:len(Pila)-4]
            i += 1
            atomo = letrasp_tseitin[i]
            L.append(atomo + "=(" + v + O + w + ")")
            s = atomo
        else:
            Pila.append(s)
            A = A[1:]
            if len(A) > 0:
                s = A[0]
    if i < 0:
        atomo = Pila[-1]
    else:
        atomo = letrasp_tseitin[i]
    B = [[[atomo]]] + [a_clausal(x) for x in L]
    B = [val for sublist in B for val in sublist]
    C = [[numero(x) for x in b] for b in B]
    return C
