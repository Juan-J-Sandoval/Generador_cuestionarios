import json
from random import sample

def leerDatos(tipo):
    tipo=tipo
    respuestas= {}; respuestas['respuesta'] = []
    preguntas= {}; preguntas['pregunta'] = []
    if tipo == "cd":
        archivo = open('static/json/prCD.json')
        prCD = json.load(archivo)
        for item in prCD['index']:
            preguntas['pregunta'].append({
                    'p': item['q']
                })
            respuestas['respuesta'].append({
                    'r': item['a']
                })
    elif tipo == "html":
        archivo = open('static/json/prHTML.json')
        prHTML = json.load(archivo)
        for item in prHTML['index']:
            preguntas['pregunta'].append({
                    'p': item['q']
                })
            respuestas['respuesta'].append({
                    'r': item['a']
                })
    return preguntas, respuestas

def examen(preguntas, respuestas):
    preguntas = preguntas; respuestas=respuestas
    cacheR = {}
    contador = 0
    if len(preguntas['pregunta']) == len(respuestas['respuesta']):
        archivo = open('static/json/examen.json')
        examen = json.load(archivo)
        while contador < len(respuestas['respuesta']):
            cacheR = respuestas['respuesta'][:]
            examen['PR'].append({
                'p': preguntas['pregunta'][contador]['p'],
                'rs': [{
                    'r': respuestas['respuesta'][contador]['r'],
                }]
            })
            eliminar = cacheR[contador]
            cacheR.remove(eliminar)
            distractoras = sample(cacheR, k=3)
            longi = len(examen['PR']) - 1
            for x in distractoras:
                examen['PR'][longi]['rs'].append({
                    'r': x['r'],
                })
            contador += 1
        with open('static/json/examen.json', 'w') as file:
            json.dump(examen, file, indent=2)
    #return examen

def limpiarExamen():
    examen= {}; examen['PR'] = []
    with open('static/json/examen.json', 'w') as file:
        json.dump(examen, file, indent=2)

