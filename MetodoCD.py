import wikipedia, spacy, re, json, random
wikipedia.set_lang('es')
nlp = spacy.load('es_core_news_sm')

#Escribe los términos y definiciones en json respectivamente
def guardaDatos(tema):
    tema = tema; e = False;
    sugerencias = wikipedia.search(tema, results=10, suggestion=False)
    termin = {}
    termin['terminos'] = []
    defini = {}
    defini['definiciones'] = []
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
            defini['definiciones'].append({
                'd': ''
            })
            e = False
        else:
            defini['definiciones'].append({
                'd': resumen
            })
        sug = re.sub(r"\([^)]*\)", "", sug, 0, re.MULTILINE)
        termin['terminos'].append({
            't': sug
        })
    with open('static/json/definiciones.json', 'w') as file:
        json.dump(defini, file, indent=2)
    with open('static/json/terminos.json', 'w') as file:
        json.dump(termin, file, indent=2)
    #return #definitermin

#Identifica los términos dentro de las definiciones
def idenTermEnDef():
    diez = 0; cache = {}; cache['definiciones'] = []
    archivo = open('static/json/definiciones.json')
    defini = json.load(archivo)
    archivo = open('static/json/terminos.json')
    termin = json.load(archivo)
    while diez < 10:
        frase = ""; aux = 0; igual = False; cT=0; cD=0; T = nlp(termin['terminos'][diez]['t']); D = nlp(defini['definiciones'][diez]['d'])
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
    with open('static/json/definiciones.json', 'w') as file:
        json.dump(cache, file, indent=2)
    #return cache

#Identifica patron definitorio
def idenPD():
    cache = {}; cache['definiciones'] = []
    archivo = open('static/json/definiciones.json')
    defini = json.load(archivo)
    for definicion in defini['definiciones']:
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
    with open('static/json/definiciones.json', 'w') as file:
        json.dump(cache, file, indent=2)
    #return cache

#Crea cuestionario con pregunta respuesta correcta
def pregunta_respuesta():
    cuestionario = {}; cuestionario['index'] = []
    archivo = open('static/json/definiciones.json')
    defini = json.load(archivo)
    archivo = open('static/json/terminos.json')
    termin = json.load(archivo)
    posicion = 0
    for definicion in defini['definiciones']:
        pregunta = "¿Cuál es la definición de " + termin['terminos'][posicion]['t'] + "?"
        if definicion['d'] != "":
            cuestionario['index'].append({
                'q': pregunta,
                'a': definicion['d']
            })
        posicion += 1
    with open('static/json/prCD.json', 'w') as file:
        json.dump(cuestionario, file, indent=2)
    #return cuestionario