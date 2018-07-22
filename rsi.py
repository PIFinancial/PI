import constantes

def RSI_inicial(lista, mediaGanancia, mediaPerdida):

    for i in range(constantes.TICKS - 1):
        if (lista[i + 1] - lista[i] > 0):
            mediaGanancia += (lista[i + 1] - lista[i])
        if ((lista[i + 1] - lista[i]) < 0):
            mediaPerdida  += (-(lista[i + 1] - lista[i]))

    mediaGanancia = mediaGanancia / (constantes.TICKS - 1)
    mediaPerdida = mediaPerdida / (constantes.TICKS - 1)
    rsi_inicial = (100 - (100 * (1 / (1 + (mediaGanancia / mediaPerdida)))))

    datos_retornados = [rsi_inicial , mediaGanancia, mediaPerdida]

    return datos_retornados


def RSI(lista, mediaGanancia, mediaPerdida):

    if ((lista[-1] - lista[-2]) > 0):
        mediaGanancia = ((mediaGanancia * (constantes.TICKS - 2)) + (lista[-1] - lista[-2])) / (constantes.TICKS - 1)
        mediaPerdida = ((mediaPerdida * (constantes.TICKS - 2)) + (0)) / (constantes.TICKS - 1)
    
    if ((lista[-1] - lista[-2]) < 0):
        mediaGanancia = ((mediaGanancia * (constantes.TICKS - 2)) + (0)) / (constantes.TICKS - 1)
        mediaPerdida = ((mediaPerdida * (constantes.TICKS - 2)) + (-(lista[-1] - lista[-2]))) / (constantes.TICKS - 1)

    if ((lista[-1] - lista[-2]) == 0):
        mediaGanancia = ((mediaGanancia * (constantes.TICKS - 2)) + (0)) / (constantes.TICKS - 1)
        mediaPerdida = ((mediaPerdida * (constantes.TICKS - 2)) + (0)) / (constantes.TICKS - 1)
    
    rsi = (100 - (100 * (1 / (1 + (mediaGanancia / mediaPerdida)))))
    datos_retornados = [round(rsi,4) , round(mediaGanancia,4), round(mediaPerdida,4)]

    return datos_retornados
