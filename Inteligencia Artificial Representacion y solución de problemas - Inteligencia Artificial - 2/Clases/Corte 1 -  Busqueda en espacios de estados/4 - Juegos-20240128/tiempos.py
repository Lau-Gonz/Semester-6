from time import time
import pandas as pd

def obtiene_tiempos(fun, args:list, num_it:int=10) -> list:
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
    for i in range(num_it):
        arranca = time()         # Inicializa cronómetro
        x = fun(*args)           # Evalúa función
        para = time()            # Detiene cronómetro
        tiempos_fun.append(para - arranca)
    return tiempos_fun

def compara_funciones(lista_funs:list, lista_args:list, lista_nombres:list, num_it:int=10) -> pd.DataFrame:
    '''
    Cada función en la lista la corre con los respectivos argumentos en la lista
    de argumentos y obtiene los tiempos de CPU.
    Input:
        - lista_funs, una lista de funciones,
        - lista_args, una lista de listas de argumentos,
        - lista_nombres, una lista con los nombres de las funciones/parámetros
    Output:
        - Un dataframe de pandas con las siguientes variables:
            Función: el nombre de la función respectiva en lista_nombres
            tiempo_CPU: el tiempo en CPU
          Por cada función hay num_it filas
    '''
    data_list = []    # inicializa lista de dataframes
    for i, fun in enumerate(lista_funs):
        nms = []    # lista para los nombres
        ts = []     # lista para los tiempos
        # Obtiene los tiempos de la función i-ésima sobre la lista de argumentos i-ésima
        ts += obtiene_tiempos(fun, lista_args[i], num_it) 
        # Guarda los nombres i-ésimos en la lista_nombres
        nms += [lista_nombres[i]]*num_it
        # Crea el dataframe y lo incluye en la lista 
        data_list.append(pd.DataFrame({'Función':nms, 'tiempo_CPU':ts}))
    return pd.concat(data_list, ignore_index=True)
