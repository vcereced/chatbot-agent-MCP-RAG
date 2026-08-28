# Arquitectura del proyecto

## Objetivo

Este proyecto implementa un agente conversacional distribuido en microservicios, con una arquitectura pensada para ser:

- modular,
- reutilizable,
- extensible,
- escalable,
- portable frente a cambios de base de datos, proveedor de IA o capa de persistencia.

La idea principal es separar claramente el dominio, la infraestructura y la coordinación del flujo para evitar acoplar la lógica de negocio a una implementación concreta de modelo, almacenamiento o herramienta.

---

## Principios arquitectónicos

### 1. Desacoplamiento por capas

Cada microservicio sigue una estructura similar basada en capas:

- app/main.py
- app/config.py
- app/api/
- app/service/ o app/services/
- app/clients/
- app/repositories/ o app/registry/

Esto permite:

- aislar responsabilidades,
- reutilizar módulos,
- sustituir implementaciones sin romper la lógica principal,
- migrar con menos riesgo.

### 2. Contratos compartidos en shared

Los contratos del sistema viven en la carpeta `shared`. Ahí se definen:

- modelos de dominio,
- request/response schemas,
- definiciones de herramientas,
- datos de conversaciones,
- resultados del LLM,
- errores comunes.

Esto evita que cada servicio tenga su propia interpretación del mismo concepto y reduce el riesgo de incompatibilidades.

### 3. Microservicios con responsabilidades bien delimitadas

Cada servicio tiene un objetivo claro:

- `agent`: orquestación del flujo del agente
- `llm`: integración con el modelo de lenguaje
- `memory`: almacenamiento y recuperación del historial
- `tools-executor`: ejecución de herramientas
- `nginx`: frontend y routing HTTP
- `ollama`: motor de inferencia local

### 4. Migrabilidad

El diseño está enfocado a poder cambiar:

- la base de datos de memoria,
- el proveedor de IA,
- el modelo LLM,
- la implementación de herramientas,
- la capa de presentación,

sin tener que reescribir el núcleo del agente.

---

## Visión de alto nivel

La aplicación se compone de varios servicios independientes que colaboran para responder una conversación.

```text
Cliente / Web / Browser
          |
          v
       nginx
          |
          v
       agent
      / | \
     /  |  \
    v   v   v
  llm memory tools-executor
    |      |        |
    |      |        +----> herramientas registradas
    |      +--------------> historial de conversaciones
    +----------------------> modelo de IA / Ollama
```

---

## Servicios del sistema

### 1. Agent

Es el servicio principal y el punto de coordinación.

Responsabilidades:

- recibir mensajes del cliente,
- obtener o crear la conversación,
- invocar al servicio de memoria,
- llamar al servicio LLM,
- decidir si hay que ejecutar herramientas,
- reenganchar el resultado del tool al flujo del modelo,
- guardar la respuesta final,
- exponer la sesión por WebSocket si procede.

En este servicio, la lógica del agente se compone de varias capas:

- `api`: entrada HTTP/WebSocket
- `service`: lógica de negocio del agente
- `clients`: clientes HTTP a otros servicios
- `runtime`: manejo de sesiones y eventos
- `conversation`: gestión del estado de una conversación

### 2. LLM

Este servicio encapsula la integración con el modelo de lenguaje.

Responsabilidades:

- construir payloads para el proveedor,
- transformar mensajes y herramientas al formato requerido,
- invocar al modelo,
- convertir la respuesta del proveedor a un contrato estándar del dominio.

La idea es que el resto del sistema no conozca directamente la API de Ollama o de otro proveedor.

### 3. Memory

Es la capa de persistencia del estado de la conversación.

Responsabilidades:

- guardar historial,
- recuperar conversaciones,
- crear o reutilizar sesiones,
- mantener el contexto de la interacción.

La capa de memoria está diseñada para poder cambiar de almacenamiento sin afectar la lógica del agente.

### 4. Tools Executor

Es el servicio responsable de ejecutar herramientas.

Responsabilidades:

- registrar herramientas disponibles,
- ejecutar una herramienta por nombre,
- validar argumentos,
- controlar timeouts,
- devolver resultados normalizados.

La arquitectura de herramientas se apoya en un registry para facilitar la extensión.

### 5. Nginx

Sirve como puerta de entrada y front-end. En este proyecto actúa como capa de presentación y proxy para la UI y la API.

### 6. Ollama

Es el motor de inferencia local que se usa como backend del LLM. Conecta el servicio `llm` con el modelo elegido.

---

## Estructura por capas dentro de cada microservicio

Cada microservicio se organiza con una estructura base similar a esta:

```text
microservicio/
├── requirements.txt
├── Dockerfile
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   └── router.py
│   ├── service/
│   │   └── logic.py
│   ├── clients/
│   │   └── external_client.py
│   ├── repositories/
│   │   └── persistence.py
│   └── domain/
│       └── models.py
```

### main.py

Punto de entrada del servicio. Define la app FastAPI y registra las rutas.

### config.py

Carga configuración, variables de entorno y parámetros del servicio.

### api/

Define los endpoints HTTP o WebSockets del servicio.

### service/

Contiene la lógica de negocio. Es la capa que orquesta la operación del servicio.

### clients/

Conecta con otros servicios del sistema o con proveedores externos.

### repositories/

Encapsula la persistencia o acceso al almacenamiento.

### shared/

Mantiene los contratos y tipos compartidos del dominio.

---

## Relación entre servicios

La interacción entre servicios es crítica para la claridad de la arquitectura.

### Agent → LLM

El agent manda el historial y las herramientas disponibles para obtener una respuesta del modelo.

### Agent → Memory

El agent recupera o crea la conversación y guarda el historial actualizado.

### Agent → Tools Executor

Cuando el LLM decide invocar una herramienta, el agent la ejecuta a través del servicio de herramientas.

### LLM → Ollama

El servicio LLM comunica el payload con el proveedor de inferencia.

### Nginx → Agent

La UI y el cliente web acceden al sistema a través del agent y del proxy HTTP.

---

## Flujo de ejecución completa

```text
Usuario
  |
  v
nginx
  |
  v
agent
  |
  +--> memory: recuperar o crear conversación
  |
  +--> llm: generar respuesta con contexto y tools
  |         |
  |         +--> si el modelo invoca tool
  |                      |
  |                      v
  |                tools-executor
  |                      |
  |                      +--> ejecutar herramienta
  |                      +--> devolver resultado normalizado
  |
  +--> guardar conversación actualizada
  |
  v
respuesta al cliente
```

Este flujo demuestra la separación clara entre:

- coordinación,
- inferencia,
- persistencia,
- ejecución de herramientas.

---

## Contratos y dominio compartido

La capa `shared` es la base de integración. Define el lenguaje común entre microservicios.

### Ejemplos de responsabilidad

- `shared/domain`: entidades del negocio (conversación, mensajes, resultados)
- `shared/llm`: contract para generar respuestas
- `shared/tools`: contracts para ejecutar herramientas
- `shared/memory`: datos para persistencia
- `shared/errors`: excepciones y errores reutilizables

Esto hace que cada microservicio no tenga que inventar su propio modelo del negocio y permite migrar implementaciones sin romper el contrato.

---

## Diseño de extensibilidad

### Cambiar modelo de IA

Se puede sustituir el proveedor de LLM modificando solo la capa `llm` y la implementación del adapter/provider. El resto del sistema sigue funcionando si se mantiene el contrato compartido.

### Cambiar base de datos

La capa `memory` puede cambiar de SQLite, PostgreSQL, Redis, MongoDB o una implementación en memoria, sin afectar el flujo del agent, siempre que se mantenga la interfaz y el dominio compartido.

### Añadir nuevas herramientas

Se puede ampliar el registry del servicio `tools-executor` y añadir una nueva herramienta sin tocar la lógica central del agente. Siempre que la herramienta respete la interfaz del dominio.

### Añadir nuevos microservicios

La estructura recomendada es una versión adaptada de la ya usada en este proyecto:

```text
nuevo_microservicio/
├── requirements.txt
├── Dockerfile
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── service/
│   ├── clients/
│   └── repositories/
```

---

## Ventajas de esta arquitectura

### Modularidad

Cada servicio encapsula su responsabilidad. No hay lógica mezclada en un único bloque monolítico.

### Reutilización

La estructura por capas permite reutilizar bloques en otros proyectos o en nuevos servicios.

### Escalabilidad

Se puede escalar vertical u horizontalmente cada servicio según el cuello de botella real.

### Mantenibilidad

Los cambios quedan localizados: si cambia el proveedor LLM, se trabaja en `llm`; si cambia el almacenamiento, en `memory`.

### Portabilidad

La arquitectura está preparada para cambiar infraestructura, adaptadores o persistencia sin cambiar la intención del negocio.

---

## Riesgos y consideraciones

Aunque esta arquitectura es limpia y extensible, requiere disciplina en la definición de contratos.

Los puntos a vigilar son:

- mantener la capa `shared` actualizada,
- evitar acoplar los servicios entre sí,
- definir claramente los schemas de entrada/salida,
- manejar errores y timeouts en cada capa,
- documentar cada servicio y su contrato.

---

## Conclusión

La arquitectura de este proyecto está diseñada como una base para un agente conversacional distribuido con alto nivel de separación de responsabilidades.

Su principal valor no es solo que funcione, sino que sea capaz de evolucionar sin romper el sistema:

- cambiar modelo de IA,
- cambiar base de datos,
- añadir herramientas,
- incorporar nuevos servicios,
- mantener la lógica del negocio desacoplada de la infraestructura.

Este enfoque hace que el proyecto sea más fácil de mantener, más seguro frente a cambios y más apropiado para crecer en equipos o proyectos reales.
