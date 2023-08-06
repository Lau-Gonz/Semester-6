from time import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols

def obtiene_tiempos(fun, args, num_it=10):
    tiempos_fun = []
    for i in range(num_it):
        arranca = time()
        x = fun(*args)
        para = time()
        tiempos_fun.append(para - arranca)
    return tiempos_fun

def compara_funciones(funs, arg, nombres, N=10):
    nms = []
    ts = []
    for i, fun in enumerate(funs):
        nms += [nombres[i] for x in range(N)]
        ts += obtiene_tiempos(fun, [arg], N)
    data = pd.DataFrame({'Función':nms, 'Tiempo':ts})
    return data

def compara_funciones_sobreargumentos(funs, args, nombres, N=10):
    data_list = []
    for i, arg in enumerate(args):
        nms = []
        argumentos = []
        ts = []
        for i, fun in enumerate(funs):
            nms += [nombres[i] for x in range(N)]
            argumentos += [i for x in range(N)]
            ts += obtiene_tiempos(fun, [arg], N)
        data_list.append(pd.DataFrame({'Función':nms, 'Num_argumento':argumentos, 'Tiempo':ts}))
    return pd.concat(data_list)
