import spacy, codecs, json
nlp = spacy.load('es_core_news_sm')
datos = {}
datos['supuestos'] = []
a = codecs.open('static/temas/10.txt', 'r', 'utf-8')
doc = a.read()
texto = nlp(doc)
a.close()
cadena = ""
bandera=False
bandera0=False
for token in texto:
    if bandera0 == True:
        bandera = False
        if token.text != ".":
            cadena += token.text
            cadena += " "
        else:
            datos['supuestos'].append({
                'cd': cadena
            })
            cadena = ""
            bandera0 = False
    elif bandera == True :
        if token.lemma_ == "uno":
            bandera0 = True
    elif token.lemma_ == "ser":
        bandera = True
with open('static/temas/10.json', 'w') as file:
    json.dump(datos, file, indent=2)