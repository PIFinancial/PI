import constantes
from math import pi , atan

def Reg_lin(lista):
    x = list(range(constantes.MUESTRAS_REGRESION))
    c = 0
    sumX = 0
    sumY = 0
    sumXY = 0
    sumX2 = 0
    for i in range(constantes.TICKS - constantes.MUESTRAS_REGRESION, constantes.TICKS):
        sumX += x[c]
        sumY += lista[i]
        sumXY += x[c] * lista[i]
        sumX2 += x[c] * x[c]
        c += 1
    b = ((constantes.MUESTRAS_REGRESION * sumXY) - (sumX * sumY)) / ((constantes.MUESTRAS_REGRESION * sumX2) - (sumX * sumX))
    #ordenada = (sumY - (b * sumX)) / constantes.MUESTRAS_REGRESION
    angulo = atan(b) * (180 / pi)
    return angulo
