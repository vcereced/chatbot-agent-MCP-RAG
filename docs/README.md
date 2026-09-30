# Chatbot Agent + tools + MCP + RAG
Este proyecto ejecuta un agente distribuido en microservicios, diseñado para ser modular, escalable y portable a distintos proveedores de IA, bdd y herramientas.


## Visión general
El proyecto está distribuido y por capas para no acoplarse. Los servicios se comunican con contratos compartidos en `shared/` y validados por `pydantic`.

- **Agent:** coordina el flujo e informa al frontend en tiempo real mediante WebSockets.
- **LLM:** integra proveedores de modelos de lenguaje, como Ollama en local o Google Gemini.
- **Memory:** recupera y guarda el historial de conversación. Actualmente, el almacenamiento es en memoria.
- **Tools Executor:** ejecuta herramientas locales y herramientas descubiertas en servidores MCP.
- **Nginx:** sirve el frontend y enruta las conexiones WebSocket y las peticiones HTTP correspondientes.
- **RAG:** procesa documentos y permite buscar información en ellos.

Puedes cambiar, manteniendo los contratos entre servicios:

- el almacenamiento de las conversaciones;
- el proveedor o el modelo de IA;
- la capa de presentación;
- la implementación de la búsqueda documental (RAG).

Puedes extender:

- el conjunto de herramientas locales;
- los servidores MCP conectados.


## Arquitectura general

```mermaid
flowchart TB

    %% =========================
    %% USER
    %% =========================
    USER[👤 User]
    
    %% =========================
    %% YOUR SYSTEM
    %% =========================
    subgraph SYSTEM["Chatbot-agent"]
        direction TB

        UI["Nginx / UI<br/>"]

        subgraph SERVICES["Docker Services"]
            direction TB

            AGENT["Agent Service<br/>ORCHESTRATOR"]
            LLM["LLM Service"]
            MEMORY["Memory Service"]
            TOOLS["Tools Executor Service"]

            OLLAMA["Ollama Service<br/>"]
            RAG["RAG Service<br/>"]
            FILES["MCP Filesystem<br/>"]
        end

        UI <--> AGENT

        AGENT <--> LLM
        AGENT <--> MEMORY
        AGENT <--> TOOLS

        LLM <--> OLLAMA
        TOOLS <--> RAG
        TOOLS <--> FILES
    end

    %% =========================
    %% EXTERNAL RESOURCES
    %% =========================
    subgraph EXTERNAL["EXTERNAL RESOURCES — ONLINE"]
        direction TB

        GOOGLE["Google API"]
        MCP["MCP Servers"]
    end

    %% =========================
    %% ENTRY POINT
    %% =========================
    USER <-->|"WebSocket<br/>:8080"| UI

    %% =========================
    %% EXTERNAL CONNECTIONS
    %% =========================
    LLM <-->|"HTTPS / API"| GOOGLE
    TOOLS <-->|"HTTPS / MCP"| MCP
```

#### Ej. Que hora es?


```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant L as LLM
    participant T as Tools
    participant M as Memory
  

    U->>A: Message(Que hora es?)
    A->>M: GetConversation()
    M-->>A: Conversation
    A->>T: GetTools()
    T-->>A: ListTools(Datetime(), read(), write()...
    A->>L: Conversation.append(Message,ListTools)
    L-->>A: Toolcall(Datetime())
    A->>T: ExecuteTool(Datetime())
    T-->>A: ToolResult(14:00:00)
 
    A->>L: Conversation.append(ToolResult)
    L-->>A: Response
    A->>M: SaveConversation()
    A->>U: Answer
```
Cuando el LLM solicita una herramienta, el agente ejecuta, añade resultado a la conversación y vuelve a consultar al LLM. Este loop se repite hasta obtener la solución o alcanzar el limite de iteraciones definido.

Un ejemplo interesante: conecta el MCP server https://mcp.kiwi.com que ofrece busqueda de vuelos. [Añadir MCP](#añadir-y-conectar-un-servidor-mcp). Pide al agente una ruta y podras obserbar en tiempo real como interactua n veces con los diferentes servicios.

## Requisitos previos

Antes de iniciar el proyecto, asegúrate de tener instalado:

- Docker
- Docker Compose v2
- Make
- Git

## Proveedor de IA

Por defecto, el proyecto usa Ollama con el modelo local `qwen2.5:3b`. Para elegir otro modelo local, define `OLLAMA_MODEL` en el archivo `.env` de la raíz. Ollama descargará el modelo si todavia no esta disponible. Se recomienda definir google gemini para levantar mas rapido el proyecto.
| Variable | Uso | Valor|
|---|---|---|
| `LLM_PROVIDER` | Proveedor del modelo | `ollama` |
| `OLLAMA_MODEL` | Modelo local por defecto. | `qwen2.5:3b` |

Como alternativa, puedes usar Google Gemini. Configura tu clave de API en `.env`.Al usar Gemini no levanta ni descarga Ollama y su modelo por defecto.

| Variable | Uso | Valor|
|---|---|---|
| `LLM_PROVIDER` | Proveedor del modelo | `google` |
| `GOOGLE_API_KEY` | Clave necesaria para usar Google Gemini. | tu api key |
| `GOOGLE_MODEL` | Modelo de Google Gemini. | `gemini-2.5-flash` |

## Ejecutar

```bash
git clone https://github.com/vcereced/chatbot-agent-MCP-RAG.git
cd chatbot-agent-MCP-RAG
make up
```
Despues abre en el navegador: 
```bash
http://localhost:8080
``` 
Para detener los servicios, ejecuta `make down` o `docker compose down`.

## Testing
Los tests de `tests/` se ejecutan con Pytest en un servicio temporal `test-runner`. `make test` levanta los servicios necesarios excepto Ollama y usa `fake-llm` para simular respuestas del proveedor de IA de forma determinista. No necesitas iniciar Ollama ni configurar una clave de Google.


Ejecuta desde la raíz:

```bash
make test
```
El comando solo muestra `TESTS PASSED` o `TESTS FAILED`. 
`test-runner` espera a que los servicios dependientes superen sus `healthchecks` antes iniciar el testing. Para ver la salida detallada de Pytest, ejecuta:
```bash
make test-verbose
```
`make test` también puede usarse en un workflow de CI para validar los cambios automáticamente.

## Observabilidad

Logs estructurados con identificadores para trazar el flujo entre servicios:

- `session_id` identifica una conexión WebSocket para agrupar los logs de una sesión.
- `run_id` identifica una ejecución concreta del agente. Se incluye en los eventos WebSocket y se propaga a las llamadas HTTP internas para correlacionar sus logs.
- `conversation_id` identifica la conversación y su historial.

## Tecnologías utilizadas

| Categoría | Tecnologías |
|---|---|
| Backend | Python 3.x, FastAPI, Uvicorn, WebSockets, Pydantic, Pydantic Settings,HTTPX, Make |
| IA y llm | Ollama, Google GenAI, MCP |
| RAG | ChromaDB, PyMuPDF, Sentence Transformers |
| Infraestructura | Docker, Docker Compose, Nginx |
| Testing | Pytest, pytest-asyncio |


## Desarrollo y extensión

### Añadir un nuevo microservicio

Se recomienda mantener la misma estructura base:

```text
nuevo_servicio/
├── requirements.txt
│   Dockerfile
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── service/
│   ├── clients/
│   └── domain/
```

### Añadir una herramienta local

1. Crea un archivo en `tools-executor/app/tools/` e implementa la herramienta como una subclase de `BaseTool`. Debe definir:
   - `get_definition()`, que devuelve su nombre, descripción y esquema de argumentos.
   - `execute(arguments)`, que ejecuta la herramienta de forma asíncrona.

2. Importa la nueva clase en `tools-executor/app/main.py` y regístrala dentro del bloque `# Local tools` de `lifespan`:

   ```python
   from app.tools.nueva_herramienta import NuevaTool

   # Local tools
   registry = ToolRegistry()
   registry.register(CalculatorTool())
   registry.register(DateTimeTool())
   registry.register(RAGSearchTool())
   registry.register(NuevaTool())

### Añadir y Conectar un servidor MCP

El proyecto puede conectarse a servidores MCP locales o online, siempre que sean compatibles con el transporte MCP Streamable HTTP (no stdio) y que el servicio `tools-executor` pueda acceder a ellos.

1. **Servidor local en Docker Compose:** añade el servicio MCP a docker-compose.yml y añadirlo en `depends_on` de `tools-executor`.

2. Añade una entrada a `mcp_servers` dentro de Settings en [tools-executor/app/config.py](../tools-executor/app/config.py):

   ```python
   MCPConfig(
       name="nombre_mcp_server",
       url="http://mcp-nuevo-servicio:8000/mcp",
   ),
   MCPConfig(
       name="otro_MCP_server",
       url="http://mcp-nuevo-servicio2:8000/mcp",
   ),
   ```
3. Configura la URL según dónde se ejecute el servidor:
   - En Docker Compose, usa el nombre del servicio, por ejemplo `http://mcp-github:8000/mcp`.
   - Para un servidor online, usa su endpoint MCP público.

4.    Después de configurar el servidor, levanta los servicios:

      ```bash
      docker compose up --build tools-executor
      ```

      Al iniciar, `tools-executor` se conecta a los servidores configurados locales y online y descubre sus herramientas para ofrecerlas al agente. Si el servidor online requiere autenticacion no conectara.

