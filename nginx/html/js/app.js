const chat = document.getElementById("chat");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-btn");

let conversationId = null;
let currentPlaceholder = null;

// Cola de estados recibidos desde el backend
let statusQueue = [];

// Indica si actualmente estamos mostrando un estado
let isShowingStatus = false;

// Respuesta final recibida del backend
let finalResponse = null;

// Indica que el backend ya ha terminado
let processingFinished = false;

// Tiempo mínimo que se muestra cada estado
const STATUS_DURATION = 2000;


// ============================================================
// WEBSOCKET
// ============================================================

const socket = new WebSocket(
    `ws://${window.location.host}/ws`
);


socket.onopen = () => {

    console.log("WebSocket conectado");

};


socket.onmessage = (event) => {

    const data = JSON.parse(event.data);

    console.log(data);

    switch (data.type) {

        case "started":
        case "status":

            enqueueStatus(data.message);

            break;


        case "finished":

            conversationId = data.conversation_id;

            finalResponse = data.message;

            processingFinished = true;

            processStatusQueue();

            break;


        case "error":

            // En caso de error no tiene sentido seguir
            // mostrando estados pendientes.
            statusQueue = [];

            finalResponse = data.message;

            processingFinished = true;

            processStatusQueue();

            break;

    }

};


socket.onclose = (event) => {

    console.log("CLOSE", event.code, event.reason);

};


socket.onerror = (event) => {

    console.log("ERROR", event);

};


// ============================================================
// INPUT
// ============================================================

sendButton.addEventListener("click", sendMessage);


input.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();

    }

});


// ============================================================
// SEND MESSAGE
// ============================================================

function sendMessage() {

    const text = input.value.trim();

    if (text === "") {
        return;
    }


    addUserMessage(text);

    input.value = "";


    // Resetear el estado de la conversación visual
    statusQueue = [];
    isShowingStatus = false;
    finalResponse = null;
    processingFinished = false;


    // Crear bubble del agente
    currentPlaceholder = createAgentPlaceholder();


    socket.send(JSON.stringify({

        type: "message",

        conversation_id: conversationId,

        message: text,

    }));

}


// ============================================================
// STATUS QUEUE
// ============================================================

function enqueueStatus(text) {

    if (!currentPlaceholder) {
        return;
    }


    // Evitar estados repetidos consecutivos.
    //
    // Ejemplo:
    //
    // Pensando
    // Pensando
    // Pensando
    //
    // Solo mostramos uno.
    const lastStatus = statusQueue[statusQueue.length - 1];

    if (lastStatus === text) {
        return;
    }


    statusQueue.push(text);

    processStatusQueue();

}


function processStatusQueue() {

    // Ya estamos mostrando un estado.
    if (isShowingStatus) {
        return;
    }


    if (!currentPlaceholder) {
        return;
    }


    // ========================================================
    // TODAVÍA HAY ESTADOS POR MOSTRAR
    // ========================================================

    if (statusQueue.length > 0) {

        const status = statusQueue.shift();

        showStatus(status);

        isShowingStatus = true;


        setTimeout(() => {

            isShowingStatus = false;

            processStatusQueue();

        }, STATUS_DURATION);


        return;
    }


    // ========================================================
    // NO QUEDAN ESTADOS
    //
    // Si además el backend ha terminado, mostramos la
    // respuesta final.
    // ========================================================

    if (processingFinished) {

        finishAgentPlaceholder(
            currentPlaceholder,
            finalResponse
        );


        currentPlaceholder = null;

        processingFinished = false;
        finalResponse = null;

    }

}


// ============================================================
// USER MESSAGE
// ============================================================

function addUserMessage(text) {

    const message = document.createElement("div");

    message.className = "message user";

    message.innerHTML = `
        <div class="bubble">
            ${escapeHtml(text)}
        </div>
    `;


    chat.appendChild(message);

    scrollToBottom();

}


// ============================================================
// AGENT PLACEHOLDER
// ============================================================

function createAgentPlaceholder() {

    const message = document.createElement("div");

    message.className = "message agent";

    message.innerHTML = `
        <img src="images/robot.svg" class="bubble-avatar">

        <div class="bubble status">

            <span class="status-dot"></span>

            <span class="status-text">
                Pensando...
            </span>

        </div>
    `;


    chat.appendChild(message);

    scrollToBottom();


    return message;

}


// ============================================================
// SHOW STATUS
// ============================================================

function showStatus(text) {

    if (!currentPlaceholder) {
        return;
    }


    const bubble =
        currentPlaceholder.querySelector(".bubble");

    const statusText =
        currentPlaceholder.querySelector(".status-text");


    if (!statusText) {
        return;
    }


    bubble.classList.add("status");

    statusText.textContent = text;


    scrollToBottom();

}


// ============================================================
// FINISH AGENT MESSAGE
// ============================================================

function finishAgentPlaceholder(message, text) {

    if (!message) {
        return;
    }


    const bubble =
        message.querySelector(".bubble");


    bubble.classList.remove("status");


    bubble.innerHTML = escapeHtml(text);


    scrollToBottom();

}


// ============================================================
// SCROLL
// ============================================================

function scrollToBottom() {

    chat.scrollTop = chat.scrollHeight;

}


// ============================================================
// HTML ESCAPING
// ============================================================

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}