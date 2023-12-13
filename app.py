from flask import Flask, render_template, request, jsonify
import mysql.connector
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(
    app, 
    # resources={ "/get_response": { "origins": "http://127.0.0.1:5500" }, "/init_chat": {"origins": "http://127.0.0.1:5500"} } 
)

# # Configura la conexión a tu base de datos MySQL
conexion = mysql.connector.connect(
    user='root',
    password='6528164mM',
    host='localhost',
    database='new_chatbot_db',
    port='3306'
)


# # Crea un cursor para ejecutar consultas
cursor = conexion.cursor()
activeChats = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init_chat', methods=['POST', 'OPTIONS'])
def init_chat():
    
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    if request.method == 'POST':
        newChat = { "stage": 0, "botMessage": "Hola bienvenido a Recomendender!\n Tu app para encontrar restaurantes en Barcelona", "userMessage": None, "userId": str(uuid.uuid4())}
        activeChats.append( newChat )
        return jsonify(newChat)

    return 'JSON posted'    

@app.route('/get_response', methods=['POST', 'OPTIONS'])
def get_response():
    
    if request.method == 'OPTIONS':
        # Manejar la solicitud OPTIONS devolviendo una respuesta vacía con el código 200
        return jsonify({}), 200

    if request.method == 'POST':
        try:
            content = request.get_json() 
            userId = content['userId']
            stage = content['stage']
            userMessage = content['userMessage']
            activeChat = findActiveChat( userId )
            if activeChat['stage'] != stage:
                raise Exception('Stage does not match with active chat')
            
            botResponse = getChatbotResponse( userMessage, stage, activeChat['userMessage'] )
            newChatState = updateActiveChat( userId, userMessage, botResponse, stage+1 )
            
            return jsonify(newChatState)

        except Exception as e:
            print( e )
            return jsonify({ 'error': str(e) })

    return jsonify({ 'error': 'not valid method' })


# Función para obtener el mensaje de bienvenida
def getInitMessage():
    # TODO: tirar una bienvenida random
    return 'Hola bienvenido al Recomender!'

# Función para obtener la respuesta del chatbot
def getChatbotResponse(userMessage, stage, lastMessage):
    botResponse = None
    if stage == 0:
        # Mensaje para la etapa 0
        botResponse = 'Para obtener tu recomendacion por favor\n Elige una de las siguientes opciones:\n\n1- Recomendar por nombre de restaurante\n2- Recomendar por tipo de comida'
    elif stage == 1:
        # Mensajes para la etapa 1
        if userMessage == '1':
            botResponse = 'Perfecto, por favor ingresa el nombre del restaurante que estás buscando.'
        elif userMessage == '2':
            botResponse = 'Excelente, por favor ingresa el tipo de comida que te gustaría comer.'
        else:
            botResponse = 'Lo siento, no he entendido. Por favor, elige 1 para recomendar por nombre de restaurante o 2 para recomendar por tipo de comida.'
    elif stage == 2:
        # Mensajes para la etapa 2
        if lastMessage == '1':
            print("usermessagerecibed1")
            # Buscar por nombre de restaurante
            query = f"SELECT * FROM ranking_reviews WHERE Restaurante LIKE '%{userMessage}%'"
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                print(f"Resultados de la consulta: {results}")

                if results:
                    restaurant_info = results[0]  # Supongo que el primer resultado es suficiente
                    recommendation = {
                        "Nombre": restaurant_info[1],
                        "Direccion": restaurant_info[2],
                        "Web": restaurant_info[3],
                        "Estrellas": restaurant_info[5]
                    }
                    botResponse = recommendation
                else:
                    botResponse = 'Lo siento, no encontré resultados para ese nombre de restaurante.'
            except Exception as e:
                print(f"Error en la consulta SQL: {e}")
                botResponse = 'Ocurrió un error al buscar el nombre del restaurante.'
        elif lastMessage == '2':
            print("usermessagerecibed2")
            # Buscar por tipo de comida
            query = f"SELECT * FROM ranking_reviews WHERE Tipo_de_comida LIKE '%{userMessage}%'"
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                print(f"Resultados de la consulta: {results}")

                if results:
                    # Procesar los resultados y devolver la recomendación
                    
                    recommendation = f"Aquí está la recomendación basada en el tipo de comida: {results[0]} "
                    botResponse = recommendation
                else:
                    botResponse = 'Lo siento, no encontré resultados para ese tipo de comida.'
            except Exception as e:
                print(f"Error en la consulta SQL: {e}")
                botResponse = 'Ocurrió un error al buscar el tipo de comida.'
    else:
        botResponse = 'Lo siento, no he entendido. Por favor, elige 1 para recomendar por nombre de restaurante o 2 para recomendar por tipo de comida.'
    return botResponse

    
def findActiveChat( userId ):
    activeChat = None
    for i, chat in enumerate(activeChats):
        if chat['userId'] == userId:
            activeChat = chat
    if activeChat == None:
        raise Exception('chat not found')
    
    return activeChat

def updateActiveChat( userId, newUserMessage, newBotMessage, newStage ):
    findActiveChat( userId )
    chatNewState = {"stage": newStage, "userMessage": newUserMessage, "botMessage": newBotMessage, "userId": userId }
    for i, chat in enumerate(activeChats):
        if chat['userId'] == userId:
            activeChats[i] = chatNewState
    return chatNewState



if __name__ == '__main__':
    app.run(debug=True)