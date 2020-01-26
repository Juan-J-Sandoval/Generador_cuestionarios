from flask import Flask, render_template, request, json, session, url_for, escape, redirect
from flask_socketio import SocketIO, emit
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import wikipedia, MetodoHTML, MetodoCD, MetodoCuestionario
app = Flask(__name__)
socketio = SocketIO(app)
id = 'ide_de_watson_assistan';sesion = "";service =""


@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        tema = request.form['tema']
        try:
            pagina = wikipedia.page(tema).url
            MetodoCuestionario.limpiarExamen
            MetodoHTML.metadatos(tema)
            MetodoHTML.pregunta_respuesta(tema)
            MetodoCD.guardaDatos(tema)
            MetodoCD.idenTermEnDef()
            MetodoCD.idenPD()
            MetodoCD.pregunta_respuesta()
            preguntas, respuestas = MetodoCuestionario.leerDatos("cd")
            MetodoCuestionario.examen(preguntas, respuestas)
            preguntas, respuestas = MetodoCuestionario.leerDatos("html")
            MetodoCuestionario.examen(preguntas, respuestas)
            return redirect(url_for('chat', tema = tema))
        except wikipedia.exceptions.WikipediaException as e:
            return render_template('index.html', pagina = e)
    return render_template('index.html')

@app.route('/chat/<tema>', methods = ['GET', 'POST'])
def chat(tema):
    global id, sesion, service
    if request.method == 'POST':
        return redirect(url_for('index'))
    pagina = wikipedia.page(tema).url
    authenticator = IAMAuthenticator('Proporcionado_por_Watson')
    service = AssistantV2(version='2019-02-28', authenticator=authenticator)
    service.set_service_url('https://gateway.watsonplatform.net/assistant/api')
    response = service.create_session(assistant_id=id).get_result()
    sesion = response['session_id']
    return render_template('chat.html', pagina = pagina, tema = tema)

@socketio.on('mensaje')
def manipula_mensaje(msj):
    global id, sesion, service
    response = service.message(assistant_id=id, session_id = sesion,input={'message_type': 'text','text': msj}).get_result()
    bot_respon = response['output']['generic'][0]['text']
    print(bot_respon)
    emit('mensaje', bot_respon, broadcast=False)


if __name__ == '__main__':
    app.secret_key = 'Proporcionado_por_Watson'
    socketio.run(app, debug=True)
