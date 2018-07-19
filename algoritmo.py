import constantes
import regrecion_lineal
import rsi
import json
import urllib.request
import time
import math
import sys

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

compras = []  #Declaramos arreglo de compras
ventas = []   #Declaramos arreglo de ventas
contadorDeTicks = 15
repeticiones = 0



class Compra:
    cantComprasTotales = 0
    def __init__(self, precio, angulo, tickCompra, EstadoDeCuenta):
        self.precio = precio
        self.angulo = angulo
        self.ID = Compra.cantComprasTotales
        self.tickCompra = tickCompra
        self.tickVenta = 0
        self.tiempo_de_vida = 0
        self.billetera = EstadoDeCuenta
        billetera.capitalDisponible -= constantes.MONEDA_SECUNDARIA_POR_OPERACION * precios[-1]
        billetera.capitalMonSecundaria += constantes.MONEDA_SECUNDARIA_POR_OPERACION
        Compra.cantComprasTotales += 1
    def PorcentajeDeGananciaActual(self, precioActual):
        return CalcularPorcentaje(self.precio, precioActual)
    def CalcularTiempoDeVida(self, tick):
        self.tiempo_de_vida = tick - self.tickCompra
        return self.tiempo_de_vida
    def CerrarCompra(self, tickVenta, precioVenta):
        self.tickVenta = tickVenta
        self.CalcularTiempoDeVida(tickVenta)
        ventas.append(Venta(precioVenta, self,billetera))
        compras.pop(compras.index(self))
        del(self)
        



class Venta:
    def __init__(self, precio, compra, EstadoDeCuenta):
        self.precioVenta = precio
        self.compra = compra
        self.porcentajeGanancia = CalcularPorcentaje(compra.precio, precio)
        EstadoDeCuenta.capitalDisponible += precios[-1] * constantes.MONEDA_SECUNDARIA_POR_OPERACION
        EstadoDeCuenta.capitalMonSecundaria -= constantes.MONEDA_SECUNDARIA_POR_OPERACION
        
class EstadoDeCuenta:
    def __init__(self, capitalInicial):
        self.capitalInicial = capitalInicial
        self.capitalDisponible = capitalInicial
        self.capitalMonSecundaria = 0
    def mostrarBalance(self):
        print("Balance: " + "Capital moneda secundaria: " + str('%.4f'%self.capitalMonSecundaria) + " BTC ||" + " Capital disponible: " + str('%.2f'%self.capitalDisponible) + " USD")
    
        


billetera = EstadoDeCuenta(5000)

precios = CargarPrimerosDatos(archivo)           #cargamos 15 valores en la lista
r = rsi.RSI_inicial(precios, 0, 0)


while(precios[-1] > 0):

    angulo = regrecion_lineal.Reg_lin(precios)      #Calculamos el angulo de la regresion lineal

    if (angulo > constantes.ANGULO_CORTE and r[0] > constantes.RSI_MAX):################################# Compra en mercado Alcista
        if(billetera.capitalDisponible > constantes.MONEDA_SECUNDARIA_POR_OPERACION * precios[-1]):     
            compras.append(Compra(precios[-1], angulo, contadorDeTicks, billetera))          
    
    if(angulo < -constantes.ANGULO_CORTE and r[0] < constantes.RSI_MIN):################################## Venta en mercado Bajista
        if(compras != []):
            for c in compras:
                porcentajeGanancia = c.PorcentajeDeGananciaActual(precios[-1])
                if(porcentajeGanancia > constantes.PORCENTAJE_PARA_CERRAR_VENTA):
                    c.CerrarCompra(contadorDeTicks, precios[-1])
                elif (c.CalcularTiempoDeVida(contadorDeTicks) > constantes.TIEMPO_DE_VIDA_MAXIMO and porcentajeGanancia < -constantes.PORCENTAJE_PARA_CERRAR_COMPRA_CON_PERDIDA):
                    c.CerrarCompra(contadorDeTicks, precios[-1])
                   
    if (angulo < constantes.ANGULO_CORTE and angulo > -constantes.ANGULO_CORTE and r[0] > constantes.RSI_MAX):############ Compra en mercado Lateral
        if(billetera.capitalDisponible > constantes.MONEDA_SECUNDARIA_POR_OPERACION * precios[-1]):     
            compras.append(Compra(precios[-1], angulo, contadorDeTicks, billetera))

    if(angulo < constantes.ANGULO_CORTE and angulo > -constantes.ANGULO_CORTE and r[0] < constantes.RSI_MIN):############## Venta en mercado Lateral
        if(compras != []):
            for c in compras:
                porcentajeGanancia = c.PorcentajeDeGananciaActual(precios[-1])
                if(porcentajeGanancia > constantes.PORCENTAJE_PARA_CERRAR_VENTA):
                    c.CerrarCompra(contadorDeTicks, precios[-1])
                elif (c.CalcularTiempoDeVida(contadorDeTicks) > constantes.TIEMPO_DE_VIDA_MAXIMO and porcentajeGanancia < -constantes.PORCENTAJE_PARA_CERRAR_COMPRA_CON_PERDIDA):
                    c.CerrarCompra(contadorDeTicks, precios[-1])

    contadorDeTicks += 1

    precios.pop(0)                                          #Sacamos el primer valor de la lista para luego agregar otro valor al final
    precios.append(LeerSiguienteDatoDesdeArchivo(archivo))
    repeticiones += 1
    r = rsi.RSI(precios, r[1], (r[2]))                       #Calculamos el RSI, la funcion devuelve una lista: [valor del rsi, media Ganancia, media Perdida]
    #time.sleep(1)



print("Porcentaje de Ganancia Total: " + '%.2f'%float(CalcularPorcentaje(billetera.capitalInicial, billetera.capitalDisponible + (billetera.capitalMonSecundaria * precios[-2]))))
billetera.mostrarBalance()
