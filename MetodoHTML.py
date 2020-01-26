import wikipedia, re, json, codecs, spacy, random
nlp = spacy.load('es_core_news_sm')
from bs4 import BeautifulSoup
wikipedia.set_lang('es')

#Extrae los datos de titulos subtitulos y listas (metadatos)
def metadatos(tema):
    pagina = wikipedia.page(tema).html()
    pagina = BeautifulSoup(pagina, 'html.parser')
    # Quitar estos comentarios para almacenar el HTML del tema
    #a = codecs.open('static/html.txt', 'w', 'utf-8')
    #a.write(pagina.prettify())
    #a.close()
    md = {}
    md['Titulo'] = []
    for etiqueta in pagina.find_all():
        if etiqueta.name == "h2":
            titulo = etiqueta.get_text()
            titulo = re.sub(r"[([A-Z]\w+]", "", titulo, 0, re.MULTILINE)
            md['Titulo'].append({
                'lista': [],
                'Nombre': titulo,
                'Subtitulos': []
            })
        elif etiqueta.name == "h3":
            subtitulo = etiqueta.get_text()
            subtitulo = re.sub(r"[([A-Z]\w+]", "", subtitulo, 0, re.MULTILINE)
            pos0 = len(md['Titulo'][:]) - 1
            md['Titulo'][pos0]['Subtitulos'].append({
                'NombreSub': subtitulo,
                'lista': []
            })
        elif etiqueta.name == "ul":
            for child in etiqueta.children:
                if child.name == "li":
                    punto = child.get_text()
                    index = re.match("[A-Z]", punto)
                    if index:
                        x = child.b
                        if x:
                            punto = x.get_text()
                            if len(md['Titulo']) != 0:
                                pos1 = len(md['Titulo'][:]) - 1
                                if len(md['Titulo'][pos1]['Subtitulos'][:]) == 0:
                                    md['Titulo'][pos1]['lista'].append({
                                        'punto': punto
                                    })
                                else:
                                    pos2 = len(md['Titulo'][pos1]['Subtitulos'][:]) - 1
                                    md['Titulo'][pos1]['Subtitulos'][pos2]['lista'].append({
                                        'punto': punto
                                    })
    with open('static/json/metadatos.json', 'w') as file:
        json.dump(md, file, indent=2)
    #Quitar este comentario para que la función devuelva el json
    #return md

#Acorta las respuestas extraídas de html y en un futuro mejorar con tecnicas de PLN
def analizar(respuesta):
    doc = nlp(respuesta)
    response = ""
    for token in doc:
        if token.text != ".":
            response= response + token.text + " "
        elif token.text == ".":
            return response
    return response

#Genera las preguntas de con los metadatos buscando género y número y busca las respuestas "correctas"
def pregunta_respuesta(tema):
    pr = {}
    pr['index'] = []
    b = wikipedia.page(tema).html()
    pagina  =  BeautifulSoup (b, 'html.parser' )
    with open('static/json/metadatos.json') as file:
        md = json.load(file)
        for titulo in md['Titulo']:
            if titulo['Nombre'] != "Enlaces externos" and titulo['Nombre'] != "Véase también" and titulo['Nombre'] != "Bibliografía" and titulo['Nombre'] != "Educación ética":
                # busca titulos que contienen listas
                if len(titulo['lista']) > 0:
                    for punto in titulo['lista']:
                        tt = nlp(punto['punto'])
                        #print(len(tt), " ",tt[0].tag_, " ", tt[0].text)
                        gF = re.search('Fem', tt[0].tag_)
                        gM = re.search('Masc', tt[0].tag_)
                        nS = re.search('Sing', tt[0].tag_)
                        nP = re.search('Plur', tt[0].tag_)
                        if gF:
                            if nS:
                                pregunta="De acuerdo a "+ titulo['Nombre'] + " ¿Que es la " + punto['punto'] + "?"
                            elif nP:
                                pregunta="Conforme a "+ titulo['Nombre'] +" ¿Que son las " + punto['punto'] + "?"
                        elif gM:
                            if nS:
                                pregunta="De acuerdo a "+ titulo['Nombre'] +" ¿Que es el " + punto['punto'] + "?"
                            elif nP:
                                pregunta="Conforme a "+ titulo['Nombre'] +" ¿Que son los " + punto['punto'] + "?"
                        else:
                            pregunta="¿Cual es la definición de " + punto['punto'] + "?"
                        #pregunta = "Según el tema "+ titulo['Nombre'] + " ¿Qué es "+ punto['punto'] + "?"
                        for etiqueta in pagina.find_all():
                                if etiqueta.get_text() == punto['punto']:
                                    if etiqueta.name == "li":
                                        padre = etiqueta.parent
                                        respuesta = padre.next_sibling.next_sibling.get_text()
                                        respuesta = analizar(respuesta)
                                elif etiqueta.name == "li":
                                    for hijo in etiqueta.descendants:
                                        if hijo.name == "b":
                                            if hijo.get_text() == punto['punto']:
                                                respuesta = etiqueta.get_text()
                                                respuesta = analizar(respuesta)
                        pr['index'].append({
                            'q': pregunta,
                            'a': respuesta
                        })
                # busca subtitulos que tiene listas
                if len(titulo['Subtitulos']) > 0:
                    for subt in titulo['Subtitulos']:
                        tt = nlp(subt['NombreSub'])
                        #print(len(tt), " ",tt[0].tag_, " ", tt[0].text)
                        gF = re.search('Fem', tt[0].tag_)
                        gM = re.search('Masc', tt[0].tag_)
                        nS = re.search('Sing', tt[0].tag_)
                        nP = re.search('Plur', tt[0].tag_)
                        if gF:
                            if nS:
                                pregunta="De acuerdo a "+ titulo['Nombre'] +" ¿Que es la " + subt['NombreSub']+ "?"
                            elif nP:
                                pregunta="Conforme a "+ titulo['Nombre'] +" ¿Que son las " + subt['NombreSub']+ "?"
                        elif gM:
                            if nS:
                                pregunta="De acuerdo a "+ titulo['Nombre'] +" ¿Que es el " + subt['NombreSub']+ "?"
                            elif nP:
                                pregunta="Conforme a "+ titulo['Nombre'] +" ¿Que son los " + subt['NombreSub']+ "?"
                        else:
                            pregunta="¿Cual es la definición de " + subt['NombreSub'] + "?"
                        #pregunta = "Con base en "+ titulo['Nombre'] + ", ¿Cuál es "+ subt['NombreSub']+ "?"
                        for etiqueta in pagina.find_all():
                            if etiqueta.get_text() == subt['NombreSub']:
                                if etiqueta.parent.name =="h3":
                                    siguiente = etiqueta.parent.next_sibling
                                    while siguiente.name != "p":
                                        siguiente = siguiente.next_sibling
                                    respuesta = siguiente.get_text()
                                    respuesta = analizar(respuesta)
                        pr['index'].append({
                            'q': pregunta,
                            'a': respuesta
                        })
    with open('static/json/prHTML.json', 'w') as file:
        json.dump(pr, file, indent=2)
    #Quitar este comentario para que la función devuelva el json
    #return pr