import constantes
import regrecion_lineal
import rsi
import json
import urllib.request
import time
import math
import sys
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def LeerSiguienteDato():
    url = "https://api.bitfinex.com/v1/pubticker/btcusd"
    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode())
        return float(data['last_price'])
    except urllib.error.HTTPError as e:
        print(e.code)

def Abrir_archivo_lista_precios():          #Devuelve archivo
    archivo = open('market-price.csv','r')
    return archivo

def LeerSiguienteDatoDesdeArchivo(archivo):   #Lee siguiente linea desde la posicion 11 para evitar leer fecha 
    try:
        return float(archivo.readline()[11:])
    except ValueError:
        return -10

def CargarPrimerosDatos(archivo):
    precios = []
    for i in range(constantes.TICKS):
        precios.append(float(LeerSiguienteDatoDesdeArchivo(archivo)))
    return precios

def CalcularPorcentaje(montoInicial, montoFinal):
    return (((montoFinal * 100) / montoInicial) - 100)

archivo = Abrir_archivo_lista_precios()
archivoRegistroSalida = open('Registro salida','w')
archivoParaGraficar = open('15_489_1_61_28.txt','w')

compras = []  #Declaramos arreglo de compras
ventas = []   #Declaramos arreglo de ventas
contadorDeTicks = 15

class EstadoDeCuenta:
    def __init__(self, capitalInicial):
        self.capitalInicial = capitalInicial
        self.capitalDisponible = capitalInicial
        self.capitalMonSecundaria = 0
    def mostrarBalance(self):
        print("Balance: " + "Capital moneda secundaria: " + str('%.4f'%self.capitalMonSecundaria) + " BTC ||" + " Capital disponible: " + str('%.2f'%self.capitalDisponible) + " USD")


class Compra:
    cantComprasTotales = 0
    billetera = EstadoDeCuenta(constantes.DINERO_INICIAL)
    def __init__(self, precio, angulo, tickCompra):
        self.precio = precio
        self.angulo = angulo
        self.ID = Compra.cantComprasTotales
        self.tickCompra = tickCompra
        self.tickVenta = 0
        self.tiempo_de_vida = 0
        Compra.billetera.capitalDisponible -= round(constantes.MONEDA_SECUNDARIA_POR_OPERACION * precios[-1] , 4)
        Compra.billetera.capitalMonSecundaria += round(constantes.MONEDA_SECUNDARIA_POR_OPERACION , 4)
        Compra.cantComprasTotales += 1
    def PorcentajeDeGananciaActual(self, precioActual):
        return CalcularPorcentaje(self.precio, precioActual)
    def CalcularTiempoDeVida(self, tick):
        self.tiempo_de_vida = tick - self.tickCompra
        return self.tiempo_de_vida
    def CerrarCompra(self, tickVenta, precioVenta):
        self.tickVenta = tickVenta
        self.CalcularTiempoDeVida(tickVenta)
        Compra.billetera.capitalDisponible += round(precios[-1] * constantes.MONEDA_SECUNDARIA_POR_OPERACION , 4)
        Compra.billetera.capitalMonSecundaria -= round(constantes.MONEDA_SECUNDARIA_POR_OPERACION , 4)
        ventas.append(Venta(precioVenta, self))
        compras.pop(compras.index(self))
        del(self)
        



class Venta:
    def __init__(self, precio, compra):
        self.precioVenta = precio
        self.compra = compra
        self.porcentajeGanancia = CalcularPorcentaje(compra.precio, precio)
        
        
    
        



arregloEjeX_capitalDisponible = []
arregloEjeY_capitalDisponible = []
arregloEjeY_capitalMonSecundaria = []

precios = CargarPrimerosDatos(archivo)           #cargamos 15 valores en la lista
r = rsi.RSI_inicial(precios, 0, 0)
precios.pop(0)          #Sacamos el primer valor de la lista para luego agregar otro valor al final
siguienteDato = LeerSiguienteDatoDesdeArchivo(archivo)
precios.append(siguienteDato)
r = rsi.RSI(precios, r[1], r[2])



while(precios[-1] > 0):

    angulo = round(regrecion_lineal.Reg_lin(precios),4)    #Calculamos el angulo de la regresion lineal

    if (angulo > constantes.ANGULO_CORTE and r[0] > constantes.RSI_MAX):################################# Compra en mercado Alcista
        if(Compra.billetera.capitalDisponible >= constantes.MONEDA_SECUNDARIA_POR_OPERACION * precios[-1]):     
            compras.append(Compra(precios[-1], angulo, contadorDeTicks))          
    
    if(angulo < -constantes.ANGULO_CORTE and r[0] < constantes.RSI_MIN):################################## Venta en mercado Bajista
        if(compras != []):
            bandera = 0
            while bandera == 0:
                for c in compras:
                    porcentajeGanancia = c.PorcentajeDeGananciaActual(precios[-1])
                    if(porcentajeGanancia > constantes.PORCENTAJE_PARA_CERRAR_VENTA):
                        c.CerrarCompra(contadorDeTicks, precios[-1])
                        bandera = 1
                    elif (c.CalcularTiempoDeVida(contadorDeTicks) > constantes.TIEMPO_DE_VIDA_MAXIMO and porcentajeGanancia < -constantes.PORCENTAJE_PARA_CERRAR_COMPRA_CON_PERDIDA):
                        c.CerrarCompra(contadorDeTicks, precios[-1])
                        bandera = 1
                if bandera == 1:
                    bandera = 0
                else:
                    break
                   
    if (angulo < constantes.ANGULO_CORTE and angulo > -constantes.ANGULO_CORTE and r[0] > constantes.RSI_MAX):############ Compra en mercado Lateral
        if(Compra.billetera.capitalDisponible >= constantes.MONEDA_SECUNDARIA_POR_OPERACION * precios[-1]):     
            compras.append(Compra(precios[-1], angulo, contadorDeTicks))

    if (angulo < constantes.ANGULO_CORTE and angulo > -constantes.ANGULO_CORTE and r[0] < constantes.RSI_MIN):############## Venta en mercado Lateral
        if(compras != []):
            bandera = 0
            while bandera == 0:
                for c in compras:
                    porcentajeGanancia = c.PorcentajeDeGananciaActual(precios[-1])
                    if(porcentajeGanancia > constantes.PORCENTAJE_PARA_CERRAR_VENTA):
                        c.CerrarCompra(contadorDeTicks, precios[-1])
                        bandera = 1
                    elif (c.CalcularTiempoDeVida(contadorDeTicks) > constantes.TIEMPO_DE_VIDA_MAXIMO and porcentajeGanancia < -constantes.PORCENTAJE_PARA_CERRAR_COMPRA_CON_PERDIDA):
                        c.CerrarCompra(contadorDeTicks, precios[-1])
                        bandera = 1
                if bandera == 1:
                    bandera = 0
                else:
                    break

    contadorDeTicks += 1

    arregloEjeX_capitalDisponible.append(contadorDeTicks)
    arregloEjeY_capitalDisponible.append(Compra.billetera.capitalDisponible + (Compra.billetera.capitalMonSecundaria * precios[-1]))
    archivoParaGraficar.write(str(arregloEjeY_capitalDisponible[-1]) + "\n")
    

    precios.pop(0)          #Sacamos el primer valor de la lista para luego agregar otro valor al final
    siguienteDato = LeerSiguienteDatoDesdeArchivo(archivo)
    if  siguienteDato < 0:  # condicion de salida del bucle while al finalizar el archivo
        break
    else:                                         
        precios.append(siguienteDato)
    r = rsi.RSI(precios, r[1], r[2])   #Calculamos el RSI, la funcion devuelve una lista: [valor del rsi, media Ganancia, media Perdida]
    #time.sleep(1)
    

plt.plot(arregloEjeX_capitalDisponible, arregloEjeY_capitalDisponible)
plt.xlabel("Tiks (15 min)")
plt.ylabel("Dolares")
plt.show()


print("Porcentaje de Ganancia Total: " + '%.2f'%float(CalcularPorcentaje(Compra.billetera.capitalInicial, Compra.billetera.capitalDisponible + (Compra.billetera.capitalMonSecundaria * precios[-1]))) + " %")
print("Compras totales: " + str(Compra.cantComprasTotales))

Compra.billetera.mostrarBalance()

