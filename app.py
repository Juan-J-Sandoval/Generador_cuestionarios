from flask import Flask, render_template, request, json, session
from flask_socketio import SocketIO, emit
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import cdQA, random, htmlQA
app = Flask(__name__)
socketio = SocketIO(app)
id = 'e64ee8ee-a226-4103-b66d-a95af43f60f0';sesion = "";service =""


@app.route('/', methods = ['GET', 'POST'])
def index():
    global id, sesion, service
    if request.method == 'POST':
        tema = request.form['tema']
        if htmlQA.identificar_temas(tema):
            exam = htmlQA.preguntas_respuestas(tema)
            pagina = htmlQA.link(tema)
            htmlQA.cuestionario()
            cdQA.guardaDatos(tema)
            cdQA.idenTermEnDef()
            cdQA.idenPD()
            cdQA.cuestio()
            cdQA.respuestasCD()
            session['cuestionario'] = False; session['posicionH'] = 0; session['posicionC'] = 0
            file = open('static/archivos/cuestionario.json')
            datosH = json.load(file)
            file = open('static/archivos/cuestionarioCD.json')
            datosC = json.load(file)
            session['datosH'] = datosH
            session['datosC'] = datosC
            authenticator = IAMAuthenticator('WByocHiKEyIkDh6YJ4coM6lRhBvjk1Me1lZZfk5_pr2A')
            service = AssistantV2(version='2019-02-28', authenticator=authenticator)
            service.set_service_url('https://gateway.watsonplatform.net/assistant/api')
            response = service.create_session(assistant_id=id).get_result()
            sesion = response['session_id']
            return render_template('examen.html', examen = exam, pagina = pagina, tema = tema)
        else:
            pagina = htmlQA.link(tema)
            return render_template('index.html', pagina = pagina)
    return render_template('index.html')

@socketio.on('mensaje')
def manipula_mensaje(msj):
    global id, sesion, service
    datosH = session['datosH']; datosC = session['datosC']
    response = service.message(assistant_id=id, session_id = sesion,input={'message_type': 'text','text': msj}).get_result()
    if session['cuestionario']:
        bot_respon = response['output']['generic'][0]['text']
        if len(response['output']['intents']) != 0:
            bot_intent = response['output']['intents'][0]['intent']
            if bot_intent != "RespCorrecta":
                emit('mensaje', bot_respon, broadcast=False)
            if bot_intent == "Despedida":
                session['cuestionario'] = False
                return
            elif bot_intent == "Contar":
                totalP = len(datosC["QA"]) + len(datosH["index"])
                totalC = session['posicionH'] + session['posicionC']
                total = totalP - totalC
                bot_respon += totalP
                bot_respon += "Te faltan: "
                bot_respon += total
        if session['posicionH'] < len(datosH["index"]):
                msj = datosH["index"][session['posicionH']]['p']
                emit('mensaje', msj, broadcast=False)
                resp = datosH["index"][session['posicionH']]['rs']
                random.shuffle(resp)
                random.shuffle(resp)
                c = 0
                while c < len(resp[:]):
                    if c == 0:
                        msj = "A) " + resp[c]['r']
                    elif c == 1:
                        msj = "B) " + resp[c]['r']
                    elif c == 2:
                        msj = "C) " + resp[c]['r']
                    elif c == 3:
                        msj = "D) " + resp[c]['r']
                    c += 1
                    emit('mensaje', msj, broadcast=False)
                session['posicionH'] += 1
        else:
            if session['posicionC'] < len(datosC["QA"]):
                msj = datosC["QA"][session['posicionC']]['p']
                emit('mensaje', msj, broadcast=False)
                resp = datosC["QA"][session['posicionC']]['rs']
                random.shuffle(resp)
                c = 0
                while c < len(resp[:]):
                    if c == 0:
                        msj = "A) " + resp[c]['r']
                    elif c == 1:
                        msj = "B) " + resp[c]['r']
                    elif c == 2:
                        msj = "C) " + resp[c]['r']
                    elif c == 3:
                        msj = "D) " + resp[c]['r']
                    c += 1
                    emit('mensaje', msj, broadcast=False)
                session['posicionC'] += 1
            else:
                session['cuestionario'] = False
                session['posicionC'] = 0
                service.delete_session(assistant_id=id, session_id=sesion).get_result()
                emit('mensaje', "cuestionario finalizado, si deseas otro tema ingresalo, gracias", broadcast=False)
    else:
        bot_respon = response['output']['generic'][0]['text']
        if len(response['output']['intents']) != 0:
            bot_intent = response['output']['intents'][0]['intent']
        else:
            bot_intent= "nada"
        if bot_intent == "AceptarExamen" or bot_intent == "SeguirExamen":
            session['cuestionario'] = True
            emit('mensaje', 'ingresa cualquier tecla para comenzar', broadcast=False)
        else:
            emit('mensaje', bot_respon, broadcast = False)
        if bot_intent == "Contar":
            totalP = len(datosC["QA"]) + len(datosH["index"])
            bot_respon = bot_respon + totalP
            print(bot_respon)
            emit('mensaje', bot_respon, broadcast=False)


if __name__ == '__main__':
    app.secret_key = 'TesisAcabaYA'
    socketio.run(app, debug=True)