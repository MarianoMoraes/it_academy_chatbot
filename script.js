document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('input-form').addEventListener('submit', function (e) {
        e.preventDefault();

        const userMessage = document.getElementById('input-field').value;
        const chatContainer = document.getElementById('conversation');
        const userMessageElement = document.createElement('div');
        userMessageElement.className = 'user-message';
        userMessageElement.innerHTML = `<p class="user-text">${userMessage}</p>`;
        chatContainer.appendChild(userMessageElement);

        document.getElementById('input-field').value = '';

        const { userId, stage } = JSON.parse(localStorage.getItem('chatData'));
        const activeChat = JSON.parse(localStorage.getItem('activeChat')) || {};
        const body = {
            userId,
            stage,
            userMessage,
            activeChat,
        };

        fetch('http://127.0.0.1:5000/get_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
            mode: 'cors',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data && typeof data === 'object') {
                if (data.error) {
                    const chatContainer = document.getElementById('conversation');
                    const chatMessage = document.createElement('div');
                    chatMessage.className = 'chatbot-message';
                    chatMessage.innerHTML = `<p class="chatbot-text">${data.error || ''}</p>`;
                    chatContainer.appendChild(chatMessage);
                } else {
                    const chatContainer = document.getElementById('conversation');

                    if (data.botMessage && typeof data.botMessage === 'object') {
                        // Procesar la respuesta estructurada del restaurante
                        const restaurantInfo = data.botMessage;
                        const chatMessage = document.createElement('div');
                        chatMessage.className = 'chatbot-message';

                        // Mostrar la información del restaurante en líneas separadas
                        chatMessage.innerHTML = `
                            <p class="chatbot-text">Nombre: ${restaurantInfo.Nombre}</p>
                            <p class="chatbot-text">Dirección: ${restaurantInfo.Direccion}</p>
                            <p class="chatbot-text">Web: ${restaurantInfo.Web}</p>
                            <p class="chatbot-text">Estrellas: ${restaurantInfo.Estrellas}</p>
                        `;
                        chatContainer.appendChild(chatMessage);
                    } else if (data.botMessage) {
                        const chatMessage = document.createElement('div');
                        chatMessage.className = 'chatbot-message';
                        chatMessage.innerHTML = `<p class="chatbot-text">${data.botMessage || ''}</p>`;
                        chatContainer.appendChild(chatMessage);
                    }
                    localStorage.setItem('chatData', JSON.stringify(data));
                }
            } else {
                console.error('La respuesta del servidor no contiene las propiedades esperadas.');
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

// Bloque adicional para la carga inicial del chat
(() => {
    fetch('http://127.0.0.1:5000/init_chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        mode: 'cors',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);

        if (data && typeof data === 'object') {
            const chatContainer = document.getElementById('conversation');
            const chatMessage = document.createElement('div');
            chatMessage.className = 'chatbot-message';
            chatMessage.innerHTML = `<p class="chatbot-text">${data.botMessage || ''}</p>`;
            chatContainer.appendChild(chatMessage);
            localStorage.setItem('chatData', JSON.stringify(data));
            localStorage.setItem('activeChat', JSON.stringify(data));
        } else {
            console.error('La respuesta del servidor no contiene las propiedades esperadas.');
        }
    })
    .catch(error => console.error('Error:', error));
})();
