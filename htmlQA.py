import wikipedia, re, json, codecs, spacy, random
nlp = spacy.load('es_core_news_sm')
from bs4 import BeautifulSoup
wikipedia.set_lang('es')
def identificar_temas(tema):
    try:
        pagina = wikipedia.page(tema).html()
        pagina = BeautifulSoup(pagina, 'html.parser')
        a = codecs.open('static/archivos/html.txt', 'w', 'utf-8')
        a.write(pagina.prettify())
        a.close()
        data = {}
        data['Titulo'] = []
        for etiqueta in pagina.find_all():
            if etiqueta.name == "h2":
                titulo = etiqueta.get_text()
                titulo = re.sub(r"[([A-Z]\w+]", "", titulo, 0, re.MULTILINE)
                data['Titulo'].append({
                    'lista': [],
                    'Nombre': titulo,
                    'Subtitulos': []
                })
            elif etiqueta.name == "h3":
                subtitulo = etiqueta.get_text()
                subtitulo = re.sub(r"[([A-Z]\w+]", "", subtitulo, 0, re.MULTILINE)
                pos0 = len(data['Titulo'][:]) - 1
                data['Titulo'][pos0]['Subtitulos'].append({
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
                                if len(data['Titulo']) != 0:
                                    pos1 = len(data['Titulo'][:]) - 1
                                    if len(data['Titulo'][pos1]['Subtitulos'][:]) == 0:
                                        data['Titulo'][pos1]['lista'].append({
                                            'punto': punto
                                        })
                                    else:
                                        pos2 = len(data['Titulo'][pos1]['Subtitulos'][:]) - 1
                                        data['Titulo'][pos1]['Subtitulos'][pos2]['lista'].append({
                                            'punto': punto
                                        })
        with open('static/archivos/data.json', 'w') as file:
            json.dump(data, file, indent=2)
        return True
    except wikipedia.exceptions.DisambiguationError as e:
        return False
def short(respuesta):
    doc = nlp(respuesta)
    response = ""
    for token in doc:
        if token.text != ".":
            response= response + token.text + " "
        elif token.text == ".":
            return response
    return response
def preguntas_respuestas(tema):
    datos = {}
    datos['QA'] = []
    b = wikipedia.page(tema).html()
    pagina  =  BeautifulSoup (b,  'html.parser' )
    with open('static/archivos/data.json') as file:
        data = json.load(file)
        for titulo in data['Titulo']:
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
                                        respuesta = short(respuesta)
                                elif etiqueta.name == "li":
                                    for hijo in etiqueta.descendants:
                                        if hijo.name == "b":
                                            if hijo.get_text() == punto['punto']:
                                                respuesta = etiqueta.get_text()
                                                respuesta = short(respuesta)
                        datos['QA'].append({
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
                                    respuesta = short(respuesta)
                        datos['QA'].append({
                            'q': pregunta,
                            'a': respuesta
                        })
    with open('static/archivos/datos.json', 'w') as file:
        json.dump(datos, file, indent=2)
    return data
def link(tema):
    try:
        pagina = wikipedia.page(tema).url
    except wikipedia.exceptions.DisambiguationError as e:
        pagina = e
    return pagina
def cuestionario():
    preguntas = []; c = 0
    respuestas = []
    cuestionario = {}; cuestionario['index'] = []
    with open('static/archivos/datos.json') as file:
        datos = json.load(file)
        for renglon in datos['QA']:
            preguntas.append(renglon['q'])
            respuestas.append(renglon['a'])
    if len(respuestas) > 5:
        while c < len(respuestas[:]):
            cuestionario['index'].append({
                'p': preguntas[c],
                'rs': [{
                    'r': respuestas[c]
                }]
            })
            long = len(cuestionario['index']) - 1
            for i in aleatoridad(respuestas[c]):
                cuestionario['index'][long]['rs'].append({
                    'r': i
                })
            c += 1
        with open('static/archivos/cuestionario.json', 'w') as file:
            json.dump(cuestionario, file, indent=2)
    else:
        with open('static/archivos/cuestionario.json', 'w') as file:
            json.dump(cuestionario, file, indent=2)
    return True
def aleatoridad(quitar):
    rs =[]
    with open('static/archivos/datos.json') as file:
        datos = json.load(file)
        for renglon in datos['QA']:
            rs.append(renglon['a'])
    rs.remove(quitar)
    for _ in range(0,3):
        result = random.choice(rs)
        yield result
        rs.remove(result)