from time import time
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import json
import numpy as np
from busqueda import solucion
import seaborn as sns

class Experiment :
    '''
    Compares given models on a number of measures over a testsuit of spaces.
    '''

    def __init__(self):
        # Reserve attribute for the test suite
        self.test_suite = []
        self.test_suite_names = []
        # Reserve attribute for generated data
        self.data = None
        self.tabla = None

    def load_space(self, space, env_name:str='space', class_name:str=None, step:int=0):
        '''
        Loads an space for running the experiment.
        
        Input:
            - space, an space object.
            - env_name (optional), a string with the space name.
            - step, number of steps to solve the space.
        '''
        self.test_suite = [[space]]
        self.test_suite_names = [env_name]
        self.test_suite_classes = [class_name]
        self.test_suite_pasos = [step]

    def load_test_suite(self, file_name:str):
        '''
        Loads an space for running the experiment.
        
        Input:
            - file_name, the name of a file with the test suite.
        '''
        # Load test suite from file
        f = open(file_name)
        env_data = json.load(f)
        # Initialize list of spaces
        spaces = []
        classes = []
        names = []
        steps = []
        # Create spaces from data
        for test in env_data:
            # Imports class
            exec(f'from ambientes import {test["env_class"]}')
            # Creates space of the given class
            exec(f'env = {test["env_class"]}()')
            # Modifies spaceal parameters according to data
            for parameter in test["parameters"].keys():
                value = test["parameters"].get(parameter)
                try:
                    exec(f'env.{parameter} = {value}')
                except:
                    exec(f'env.{parameter} = "{value}"')
            # Add space to list
            exec('spaces.append([env])')
            classes.append(test["env_class"])
            names.append(test["name"])
            try:
                steps.append(test["pasos"])
            except:
                pass
        self.test_suite = spaces
        self.test_suite_classes = classes
        self.test_suite_names = names
        self.test_suite_pasos = steps

    def hallar_tabla(self, medida:str='tiempo_CPU'):
        '''
        Obtiene una tabla de comparación de las medidas dadas sobre
        las funciones aplicadas al test suite.

        Input:
            - medidas, una lista que puede incluir:
                * 'tiempos_CPU'
                * 'Num_pasos'
                * 'Costo_camino'
        '''
        dict_medidas = {}
        assert(medida in ['tiempo_CPU', 'Num_pasos', 'Costo_camino'])
        if self.data is None:
            print('Error: ¡Se requiere comparar las funciones primero!\nCorra compara_funciones() sobre una\nlista de funciones.')
            return
        # Create aggregation dictionary
        if 'tiempo_CPU' in [medida]:
            dict_medidas["tiempo_CPU"] = ['mean', 'std']
        if 'Num_pasos' in [medida]:
            dict_medidas["Num_pasos"] = ['mean', 'std']            
        if 'Costo_camino' in [medida]:
            dict_medidas["Costo_camino"] = ['mean', 'std']            
        # Create aggregated dataframe
        if len(self.data.Paso.unique()) == 1:
            df = self.data.groupby('Función').agg(dict_medidas)
        else:
            df = self.data.groupby(['Función', 'Paso']).agg(dict_medidas)
        df = pd.DataFrame(df.to_records())
        # Include best performance column
        best_performance = df[f"('{medida}', 'mean')"].min()
        df["Best"] = df[f"('{medida}', 'mean')"].apply(lambda x: '*' if x == best_performance else '')
        self.tabla = df
        # self.tabla = pd.concat([self.tabla, df], axis=1, ignore_index=True)
        # self.tabla = pd.merge(self.tabla, df[['Función', 'Best']], left_on='Función', right_on='Función')

    def plots(self, medida:str='tiempo_CPU'):
        '''
        Dibuja los gráficos de las medidas de las funciones
        aplicadas al test suite.

        Input:
            - medidas, una lista que puede incluir:
                * 'tiempos_CPU'
                * 'Num_pasos'
                * 'Costo_camino'
        '''
        if len(self.data.Paso.unique()) > 1:
            self.hallar_tabla(medida=medida)
#            df = pd.DataFrame(self.tabla.to_records())
            fig, ax = plt.subplots(1,1, figsize=(5,3))
            sns.lineplot(data=self.tabla, hue='Función', x='Paso', y=f"('{medida}', 'mean')")
            ax.set_xlabel('Complejidad del problema\n(Num_pasos óptimos)')
            ax.legend(bbox_to_anchor=(1.25, 0.5), loc='center')
            if medida == 'tiempos_CPU':
                ax.set_ylabel('Tiempo CPU')
            if medida == 'Num_pasos':
                ax.set_ylabel('Núm. pasos')
            if medida == 'Costo_camino':
                ax.set_ylabel('Costo')
            # fig.savefig(f'{medida}.png', dpi=300)        
        else:
            k = len(self.data["Función"].unique())
            fig, ax = plt.subplots(1,1, figsize=(3*k,3))
            sns.boxplot(data=self.data, x='Función', y=medida)
        fig.savefig('figura.png', dpi=300, bbox_inches='tight')

    def compara_funciones(self, lista_funs:list, lista_nombres:list, num_it:int=10, lim_steps:int=None) -> pd.DataFrame:
        '''
        Cada función en la lista la corre con los respectivos argumentos en la lista
        de argumentos y obtiene los tiempos de CPU.
        Input:
            - lista_funs, una lista de funciones,
            - lista_args, una lista de listas de argumentos,
            - lista_nombres, una lista con los nombres de las funciones/parámetros
            - num_it, la cantidad de muestras
            - lim_steps, el límite de pasos para la solución del entorno
        Output:
            - Un dataframe de pandas con las siguientes variables:
                Función: el nombre de la función respectiva en lista_nombres
                tiempo_CPU: el tiempo en CPU
                Espacio: el nombre de la clase del espacio de estados 
                Nombre: el nombre del espacio de estados que se resuelve
                Paso: el número de pasos óptimo para la solución del entorno
                Num_pasos: el número de pasos obtenido, 
                Costo_camino: el costo del camino, 
                Solucion: la secuencia de acciones
            Por cada función hay num_it filas
        '''
        if lim_steps is None:
            limite = np.infty
        else:
            limite = lim_steps
        # inicializa dataframe
        data = pd.DataFrame({'Función':[], \
                            'tiempo_CPU':[], \
                            'Espacio':[], \
                            'Nombre':[], \
                            'Paso':[], \
                            'Num_pasos':[], \
                            'Costo_camino':[], \
                            'Solucion':[]
                                    })
        contador_state = -1
        for state in tqdm(self.test_suite, desc='Solving state space...'):
            contador_state += 1
            if self.test_suite_pasos[contador_state] <= limite:
                contador_funcion = -1   
                for fun in tqdm(lista_funs, desc='Running algorithm...'):
                    contador_funcion += 1
                    nms = []    # lista para los nombres de algoritmos
                    clss = []    # lista para els nombre de clase del espacio
                    sts = []    # lista para los nombres de espacios
                    stps = []   # lista para el número de pasos esperada
                    sols = []   # lista para las soluciones
                    pasos_sols = []   # lista para el número de pasos obtenidos
                    costo_sols = []   # lista para el costo de solución
                    ts = []     # lista para los tiempos
                    # Obtiene los tiempos y los resultados de la función i-ésima
                    # sobre la lista de argumentos i-ésima
                    resultados = self.obtiene_tiempos(fun, state, num_it)
                    ts += resultados[0]
                    sols += [solucion(x) if x is not None else None for x in resultados[1]]
                    pasos_sols += [len(solucion(x)) if x is not None else None for x in resultados[1]]
                    costo_sols += [x.costo_camino if x is not None else None for x in resultados[1]]
                    # Guarda los nombres i-ésimos en la lista_nombres
                    nms += [lista_nombres[contador_funcion]]*num_it
                    sts += [self.test_suite_names[contador_state]]*num_it
                    clss += [self.test_suite_classes[contador_state]]*num_it
                    stps += [self.test_suite_pasos[contador_state]]*num_it
                    # Crea el dataframe y lo incluye en la lista 
                    df = pd.DataFrame({'Función':nms, \
                                        'tiempo_CPU':ts, \
                                        'Espacio':clss, \
                                        'Nombre':sts, \
                                        'Paso':stps, \
                                        'Num_pasos':pasos_sols, \
                                        'Costo_camino':costo_sols, \
                                        'Solucion':sols
                                                    })
                    data = pd.concat([data, df], ignore_index=True)
            else:
#                print(f'State space {self.test_suite_names[contador_state]} has complexity {self.test_suite_pasos[contador_state]}, which is above limit {limite}. Skipping state space.')
                pass
        self.data = data

    def obtiene_tiempos(self, fun, args:list, num_it:int=10) -> list:
        '''Toma una función y la corre sobre un argumento
        tantas veces como num_it. Devuelve los tiempos de CPU.
        Input:
            - fun, una función
            - args, una lista de argumentos
            - num_it, la cantidad de muestras
        Output:
            - tiempos_fun, una lista con los tiempos de CPU
        '''
        tiempos_fun = []
        soluciones = []
        for i in range(num_it):
            arranca = time()         # Inicializa cronómetro
            x = fun(*args)           # Evalúa función
#            try:
#                x = fun(*args)           # Evalúa función
#            except Exception as e:
#                print(e)
#                x = None
            para = time()            # Detiene cronómetro
            tiempos_fun.append(para - arranca)
            soluciones.append(x)
        return tiempos_fun, soluciones
