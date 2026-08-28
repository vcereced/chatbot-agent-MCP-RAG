# API del proyecto

## Puertos y accesos

### Expuestos al host

`http://localhost:8080` (nginx)

### Internos de Docker

- `http://agent:8000`
- `http://llm:8000`
- `http://memory:8000`
- `http://tools-executor:8000`

Esto mantiene la separación entre la capa visible para usuarios y la infraestructura interna de integración entre microservicios.

---
### Health check

los servicios también expone rutas simples:

- `GET /`
- `GET /health`

Estas rutas sirven para comprobar que la app responde y para comprobar estado del servicio.

---

## Contratos compartidos entre microservicios

Estos son los contratos que se intercambian entre servicios y que definen la integración del sistema. No son modelos de dominio puros, sino payloads de comunicación entre `agent`, `llm`, `memory` y `tools-executor`.

### 1. Agent contract

Archivo: `shared/shared/agent/chat.py`

```python
class ChatRequest(BaseModel):
    type: Literal["message", "cancel"]
    conversation_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
```

Uso:

- el cliente o la capa de presentación envía un `ChatRequest` al agente
- el agente devuelve un `ChatResponse` con la respuesta final de la conversacion

### 2. LLM contract

Archivo: `shared/shared/llm/generate.py`

```python
class GenerateRequest(BaseModel):
    messages: list[Message]
    tools: list[ToolDefinition] | None

class GenerateResponse(BaseModel):
    result: GenerateResult
```

Dónde `GenerateResult` se define como:

```python
class GenerateResult(BaseModel):
    text: str | None = None
    tool_call: ToolCall | None = None
```

Y `ToolCall`:

```python
class ToolCall(BaseModel):
    name: str
    arguments: dict[str, object]
```

Esto es clave porque el modelo puede responder con:

- texto directo en `result.text`, o
- una llamada a una herramienta en `result.tool_call`

### 3. Memory contract

Archivo: `shared/shared/memory/conversation.py`

```python
class GetOrCreateConversationRequest(BaseModel):
    conversation_id: str | None = None

class GetOrCreateConversationResponse(BaseModel):
    conversation: Conversation

class SaveConversationRequest(BaseModel):
    conversation: Conversation

class SaveConversationResponse(BaseModel):
    success: bool
```

Uso:

- el agente pide la conversación actual o la crea
- el agente guarda la conversación actualizada

### 4. Tools contract

Archivo: `shared/shared/tools/execute.py`

```python
class ExecuteToolRequest(BaseModel):
    tool_call: ToolCall

class ExecuteToolResponse(BaseModel):
    tool_result: ToolResult
```

Archivo: `shared/shared/tools/list_tools.py`

```python
class ListToolsResponse(BaseModel):
    tools: list[ToolDefinition]
```

Uso:

- el agente envia la intención del modelo a `tools-executor`
- el servicio devuelve el resultado estructurado de la herramienta
- el agente puede consultar qué herramientas están disponibles

---

## 1. Agent service

El servicio `agent` es la capa de orquestación del sistema. Es el punto de entrada principal del flujo del chatbot.

`/ws`

Se usa para mantener una sesión en tiempo real entre el cliente y el agente.


```text
ws://localhost:8080/ws
```

Este endpoint es el más importante para la experiencia en tiempo real del chat. El agente recibe mensajes del cliente, procesa la conversación y va enviando eventos de progreso por WebSocket.


## 2. LLM service

El servicio `llm` recibe una petición de generación desde el agente y la traduce a la llamada al provider del modelo.

### `POST /generate`

Genera una respuesta con el modelo LLM.

#### Request

```json
{
  "messages": [
    { "role": "user", "content": "Hola" }
  ],
  "tools": []
}
```

#### Response

El servicio responde con un objeto `GenerateResponse` cuyo campo `result` puede ser:

- un texto libre (`result.text`), o
- una llamada a herramienta (`result.tool_call`)

```json
{
  "result": {
    "text": "La respuesta final del modelo",
    "tool_call": null
  }
}
```

O bien:

```json
{
  "result": {
    "text": null,
    "tool_call": {
      "name": "calculator",
      "arguments": {
        "expression": "2 + 2"
      }
    }
  }
}
```

---

## 3. Memory service

El servicio `memory` gestiona el historial y la conversación.

### `POST /conversations/get_or_create`

Obtiene o crea una conversación según su `conversation_id`.

#### Request

```json
{
  "conversation_id": "abc123"
}
```

#### Response

```json
{
  "conversation": {
    "id": "abc123",
    "messages": []
  }
}
```

### `POST /conversations/save`

Guarda una conversación completa.

#### Request

```json
{
  "conversation": {
    "id": "abc123",
    "messages": []
  }
}
```

#### Response

```json
{
  "success": true
}
```

---

## 4. Tools Executor service

Este servicio ejecuta herramientas registradas del agente.

### `POST /execute`

Ejecuta una herramienta por nombre y argumentos.

#### Request

```json
{
  "tool_call": {
    "name": "calculator",
    "arguments": {
      "expression": "2 + 2"
    }
  }
}
```

#### Response

```json
{
  "tool_result": {
    "tool_name": "calculator",
    "success": true,
    "result": 4,
    "execution_time_ms": 12.5
  }
}
```

### `GET /tools`

Devuelve las herramientas disponibles en el registry.

#### Response

```json
{
  "tools": [
    {
      "name": "calculator",
      "description": "Perform arithmetic operations",
      "arguments": {}
    }
  ]
}
```

---

## 5. Nginx / frontend

El frontend público se sirve desde:

```text
http://localhost:8080
```

Esta URL no es el backend directo, sino la capa de presentación y proxy del sistema.

La idea del front es consumir la funcionalidad del `agent`, normalmente a través de WebSocket

---

## Flujo real de una petición desde el navegador

```text
Usuario en localhost:8080/ws
        |
        v
    nginx (front)
        |
        v
      agent
        |
        +--> memory
        |
        +--> llm
        |
        +--> tools-executor
        |
        +--> respuesta final al cliente
```
---




