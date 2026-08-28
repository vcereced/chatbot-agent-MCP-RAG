# Chatbot Agent + tools

Un agente conversacional que ejecuta tools distribuido por microservicios, diseñado para ser modular, reutilizable, escalable y fácil de adaptar a distintos proveedores de IA, persistencia o herramientas.

Este proyecto no es solo un chatbot: es una base para construir un agente conversacional distribuido con una arquitectura preparada para crecer y migrar sin romper el sistema.

---

## Visión general

Este proyecto implementa un chatbot con una arquitectura orientada a microservicios y capas:

- Agent: coordina, gestiona el flujo informando por Websockets al front, invoca a otros servicios y orquesta la interacción con herramientas.
- LLM: encapsula la integración con el modelo de lenguaje (en este caso, Ollama).
- Memory: gestiona la persistencia del estado de la conversación y el historial.
- Tools Executor: ejecuta herramientas externas o utilidades del sistema.
- Nginx: sirve la capa de frontend y actúa como entrada HTTP para la aplicación.
- Ollama: motor local de inferencia para el modelo de lenguaje.

La arquitectura está pensada para evolucionar sin acoplarse a un proveedor concreto. Puedes cambiar:

- la base de datos de memoria,
- el modelo de IA,
- el proveedor de LLM,
- la lógica de herramientas,
- la capa de presentación,

sin reescribir necesariamente la lógica principal del agente.

---

## Principios de diseño

### 1. Arquitectura distribuida por microservicios

Cada servicio tiene una responsabilidad clara y se comunica a través de contratos HTTP/JSON o de modelos compartidos.

### 2. Arquitectura por capas

Cada servicio sigue una estructura similar:

- app/main.py
- app/config.py
- app/api/
- app/service/
- app/clients/

Esto facilita:

- mantener una lógica consistente,
- localizar cambios por responsabilidad,
- reutilizar módulos en otros proyectos,
- migrar piezas sin tocar la capa de dominio.

### 3. Contratos explícitos entre servicios

Los modelos y contratos compartidos viven en `shared/`, para evitar que cada microservicio defina su propia versión del mismo dominio.

Esto permite:

- mantener una representación única de la conversación,
- estandarizar mensajes, resultados y llamadas a herramientas,
- reducir errores de integración entre servicios.

### 4. Extensibilidad

La capa de herramientas es registrable y reutilizable. Si se añade una nueva herramienta, el agente puede descubrirla y usarla sin cambiar toda la lógica de coordinación.

### 5. Portabilidad

El servicio de LLM y la capa de almacenamiento están desacoplados de la lógica de negocio. Esto es el punto clave para migrar de una base de datos o de un proveedor de IA sin romper el comportamiento global.

---

## Arquitectura del proyecto

```text
┌─────────────────────┐
authoring / browser / ui
└──────────┬──────────┘
           │ WS
           ▼
┌─────────────────────┐
│       nginx          │
│   Frontend / proxy  │
└──────────┬──────────┘
           │
           ▼ WS
┌─────────────────────┐
│       agent          │
│   Orquestador       │
│  - router            │
│  - service           │
│  - clients           │
│  - ws/session        │
└─────┬───────┬───────┘
      │       │ HTTP
      │       ├───────────────► tools-executor
      │                       │
      │                       │ executes tools
      │ HTTP
      ├───────────────► llm
      │                 │ generate responses
      │ HTTP
      └───────────────► memory
                        │ persist conversation state
```

## Servicios y responsabilidades

### Agent

Responsable de:

- recibir mensajes del cliente,
- coordinar la interacción,
- invocar LLM y herramientas,
- manejar la conversación y el estado del flujo.

### LLM

Responsable de:

- serializar mensajes,
- encapsular llamadas a Ollama,
- transformar respuestas internas a contratos del dominio.

### Memory

Responsable de:

- guardar y recuperar conversaciones,
- mantener el historial,
- ofrecer operaciones CRUD o de lectura para el agente.

### Tools Executor

Responsable de:

- registrar herramientas,
- ejecutar lógica en funciones externas,
- manejar timeouts, errores y resultados estandarizados.

---

#### Shared

La capa `shared` es un punto clave de la arquitectura. Aquí se definen:

- modelos del dominio: mensajes, conversaciones, resultados, herramientas
- requests y responses para HTTP
- resultados de generación del LLM
- definiciones de herramienta
- errores comunes

Esto facilita que cada microservicio trabaje con tipos estandarizados.

---


## Flujo de conversación

El flujo general del agente se puede resumir así:

1. El usuario envía un mensaje desde la UI o desde una petición HTTP/WebSocket.
2. El servicio `agent` recibe la solicitud.
3. El agente obtiene o crea la conversación asociada.
4. Consulta la memoria para recuperar el contexto relevante.
5. Solicita al servicio `llm` una respuesta con el historial y las herramientas disponibles.
6. Si el modelo decide invocar una herramienta, el `agent` la ejecuta a través de `tools-executor`.
7. El resultado de la herramienta se incorpora al contexto de la conversación.
8. El modelo genera una respuesta final con la información obtenida.
9. El agente guarda la conversación y devuelve la respuesta al cliente.

Este modelo permite tener una lógica de agente bastante clara y una separación nítida entre:

- coordinación del flujo,
- generación del texto,
- ejecución de herramientas,
- persistencia del contexto.

---

## Desarrollo y extensión

### Añadir un nuevo microservicio

Se recomienda mantener la misma estructura base:

```text
nuevo_servicio/
├── requirements.txt
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── service/
│   ├── clients/
│   └── domain/
```

### Añadir una nueva herramienta

1. Crear la herramienta dentro de `tools-executor/app/tools/`.
2. Registrarla en el `/app/registry/tool_registry.py` y registralos en la clase ToolRegistry.

### Cambiar proveedor de IA

Solo afecta a la capa `llm` y a su adaptador/provider. El resto del proyecto no debería cambiar si el contrato compartido se mantiene.

### Cambiar base de datos

La capa `memory` puede cambiar sin afectar la lógica del agente, siempre que se respeten los contratos del dominio.

## Tecnologías utilizadas

- Python 3.x
- FastAPI
- Uvicorn
- Docker
- Docker Compose
- Ollama
- Nginx
- Pydantic
- WebSockets

---

## Requisitos previos

Antes de iniciar el proyecto, asegúrate de tener instalado:

- Docker
- Docker Compose
- Make
- Git
- Python 3.10+ (si quieres ejecutar servicios localmente fuera de contenedores)

---

## Variables de entorno

El proyecto usa variables de entorno para desacoplar la infraestructura de la lógica del negocio. En `docker-compose.yml` se configuran servicios como:

- `LLM_URL`
- `TOOLS_URL`
- `MEMORY_URL`
- `REQUEST_TIMEOUT`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OLLAMA_ENDPOINT`
- `TOOL_TIMEOUT_SECONDS`

Esto permite cambiar la ubicación del LLM, la persistencia o una herramienta sin tocar la lógica principal.

---

## Inicio rápido

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd chatbot-agent
```

### 2. Construir y levantar los servicios

```bash
docker compose up --build
```

o con el Makefile:

```bash
make build
```

### 3. Verificar servicios

```bash
docker compose ps
```

### 4. Ver logs

```bash
make logs
```

### 5. Parar la infraestructura

```bash
docker compose down
```

o

```bash
make down
```

---




