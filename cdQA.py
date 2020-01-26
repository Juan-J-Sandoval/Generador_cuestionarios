import wikipedia, spacy, re, json, random
wikipedia.set_lang('es')
nlp = spacy.load('es_core_news_sm')
#ESCRIBE LOS DATOS EN LOS JSON'S
def guardaDatos(tema):
    tema = tema; e = False;
    sugerencias = wikipedia.search(tema, results=10, suggestion=False)
    data = {}
    data['terminos'] = []
    dato = {}
    dato['definiciones'] = []
    for sug in sugerencias:
        sug = sug.lower()
        try:
            resumen = wikipedia.summary(sug, tema)
            resumen = resumen.lower()
            resumen = re.sub(r"[[0-5][0-9]]​", "", resumen, 0, re.MULTILINE)  # elimina todos los numero de dos digitos dentro de []
            resumen = re.sub(r"\n", "", resumen, 0, re.MULTILINE)  # elimina los saltos de linea
            resumen = re.sub(r"\([^)]*\)", "", resumen, 0, re.MULTILINE)  # elimina lo que esta dentro de ()
            resumen = re.sub(r"\{([^}]+)\}", "", resumen, 0, re.MULTILINE)  # elimina lo que esta dentro de {}
            resumen = re.sub(r"  ", " ", resumen, 0, re.MULTILINE)  # elimina el doble espacio
            resumen = re.sub(r"    ", " ", resumen, 0, re.MULTILINE)  # quita trees espacios
        except wikipedia.exceptions.WikipediaException:
            e = True
        if e:
            dato['definiciones'].append({
                'd': ''
            })
            e = False
        else:
            dato['definiciones'].append({
                'd': resumen
            })
        sug = re.sub(r"\([^)]*\)", "", sug, 0, re.MULTILINE)
        data['terminos'].append({
            't': sug
        })
    with open('static/archivos/definiciones.json', 'w') as file:
        json.dump(dato, file, indent=2)
    with open('static/archivos/def.json', 'w') as file:
        json.dump(dato, file, indent=2)
    with open('static/archivos/terminos.json', 'w') as file:
        json.dump(data, file, indent=2)
    return
#IDENTIFICA LOS TERMINOS DENTRO DE LAS DEFINICIONES
def idenTermEnDef():
    diez = 0; cache = {}; cache['definiciones'] = []
    archivo = open('static/archivos/definiciones.json')
    datosD = json.load(archivo)
    archivo = open('static/archivos/terminos.json')
    datosT = json.load(archivo)
    while diez < 10:
        frase = ""; aux = 0; igual = False; cT=0; cD=0; T = nlp(datosT['terminos'][diez]['t']); D = nlp(datosD['definiciones'][diez]['d'])
        while cD < len(D[:]):
            if D[cD].lemma_ == T[0].lemma_:
                while cT < len(T[:]):
                    if D[cD].lemma_ == T[cT].lemma_:
                        igual = True
                        aux = cD + 1
                    else:
                        aux = 0
                        igual = False
                    cD += 1; cT += 1
            cD += 1
        diez += 1
        if igual:
            while aux < len(D[:]):
                frase += D[aux].text + " "
                aux += 1
        cache['definiciones'].append({
            'd': frase
        })
    with open('static/archivos/definiciones.json', 'w') as file:
        json.dump(cache, file, indent=2)
    return
#IDENTIFICA PATRON DEFINITORIO
def idenPD():
    cache = {}; cache['definiciones'] = []
    archivo = open('static/archivos/definiciones.json')
    datos = json.load(archivo)
    for definicion in datos['definiciones']:
        if definicion['d'] != "":
            D = nlp(definicion['d'])
            conD = 2; pd = False; frase = ""
            if D[0].pos_ == "AUX" and D[1].pos_ == "DET":
                while conD < len(D[:]):
                    frase += D[conD].text + " "
                    conD += 1
            elif D[0].pos_ == "CONJ" or D[0].text == "," or D[0].text == ":":
                while conD < len(D[:]):
                    aux = conD + 1
                    if D[conD].pos_ == "AUX" and D[aux].pos_ == "DET":
                        pd = True
                        conD = aux + 1
                    if pd:
                        frase += D[conD].text + " "
                    conD += 1
            cache['definiciones'].append({
                'd': frase
            })
        else:
            cache['definiciones'].append({
                'd': ''
            })
    with open('static/archivos/definiciones.json', 'w') as file:
        json.dump(cache, file, indent=2)
    return
#CREA JSON DE CUESTIONARIO
def cuestio():
    cuestionario = {}; cuestionario['index'] = []
    archivo = open('static/archivos/definiciones.json')
    datosD = json.load(archivo)
    archivo = open('static/archivos/terminos.json')
    datosT = json.load(archivo)
    posicion = 0
    for definicion in datosD['definiciones']:
        if definicion['d'] != "":
            cuestionario['index'].append({
                'q': datosT['terminos'][posicion]['t'],
                'a': definicion['d']
            })
        posicion += 1
    with open('static/archivos/preguntaRespuestaCD.json', 'w') as file:
        json.dump(cuestionario, file, indent=2)
    return
#RESPUESTAS ALEATORIAS
def respuestasCD():
    preguntas = []; c = 0
    respuestas = []
    evaluacion = {}; evaluacion['QA'] = []
    with open('static/archivos/preguntaRespuestaCD.json') as file:
        datos = json.load(file)
        for renglon in datos['index']:
            preguntas.append(renglon['q'])
            respuestas.append(renglon['a'])
    if len(respuestas) > 5:
        while c < len(preguntas[:]):
            pp = "¿Cual es la definición de " + preguntas[c] + "?"
            evaluacion['QA'].append({
                'p': pp,
                'rs': [{
                    'r': respuestas[c]
                }]
            })
            long = len(evaluacion['QA']) - 1
            for i in randomRespuestas(respuestas[c]):
                evaluacion['QA'][long]['rs'].append({
                    'r': i
                })
            c += 1
        with open('static/archivos/cuestionarioCD.json', 'w') as file:
            json.dump(evaluacion, file, indent=2)
    else:
        with open('static/archivos/cuestionarioCD.json', 'w') as file:
            json.dump(evaluacion, file, indent=2)
    return
#RANDOM
def randomRespuestas(quitar):
    rs = []
    with open('static/archivos/preguntaRespuestaCD.json') as file:
        datos = json.load(file)
        for renglon in datos['index']:
            rs.append(renglon['a'])
    rs.remove(quitar)
    for _ in range(0, 3):
        result = random.choice(rs)
        yield result
        rs.remove(result)
