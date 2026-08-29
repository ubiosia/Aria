# Capacidades — qué hace ARIA, en concreto

Resumen completo, sin tecnicismos de arquitectura interna, de lo que ARIA puede hacer hoy. Para cómo está construido por dentro, ver [`arquitectura.md`](arquitectura.md).

## Núcleo de conversación

Responde preguntas generales usando un modelo de lenguaje local (`llama3.1:8b`, corriendo vía Ollama, sin depender de internet para pensar). Cuando la pregunta cae dentro de un dominio con biblioteca indexada (trading, tecnología, IA, programación), busca primero en esa biblioteca y responde con ese contenido específico, citando la fuente; si no hay contenido relevante indexado, responde con el conocimiento general del modelo.

## Canales de acceso

**Interfaz web (Gradio):** el canal principal de uso diario, con toggle para activar o desactivar la búsqueda web, y donde se prueban primero la mayoría de las funciones nuevas.

**Telegram:** un canal aparte, con algunas funciones exclusivas de este canal: comandos específicos como `/transcribe` (transcripción de audio con un modelo dedicado), `/start` y `/stats`, botones de feedback (👍/👎) en cada respuesta normal para calificarla, un "modo invitado" con reglas de acceso distintas al uso personal, y alertas automáticas del sistema de monitoreo (`watchdog.py`) que avisan por este canal si el sistema falla repetidamente. La visión multimodal por Telegram (analizar una imagen enviada) estuvo planificada como capacidad futura, sin confirmar como cerrada en el material disponible.

## Voz

**Reconocimiento de voz (Whisper, con aceleración por GPU):** transcribe audio a texto en menos de un segundo por cada ocho segundos de grabación. El micrófono físico se graba del lado de Windows y se pasa a Linux por una carpeta compartida, por una limitación real de WSL2 con el hardware de audio.

**Síntesis de voz (Piper, 100% offline):** convierte cualquier respuesta de ARIA en un archivo de audio, con una voz en español elegida específicamente por Alejandro.

## Memoria personal

Guarda datos que se le enseñan directamente o que detecta y guarda sola durante la conversación (aprendizaje automático), organizados por categoría. Distingue preguntas de afirmaciones — no guarda algo solo porque se mencionó en forma de pregunta. Soporta datos con vencimiento (recordar algo "por dos horas", por ejemplo). Las consultas sobre datos personales sensibles (dónde vive Alejandro, quién es su familia) usan una búsqueda directa y determinística en la base de datos, no el modelo de lenguaje, para evitar el riesgo de que un dato sensible se invente o se interprete mal. Ver [`/historia/05_memoria_y_conocimiento.md`](../historia/05_memoria_y_conocimiento.md).

## Memoria episódica (historial de conversaciones)

Guarda un resumen de cada sesión de conversación, para poder responder después a preguntas como "¿de qué hablamos la semana pasada?". Estuvo rota en la práctica durante buena parte del proyecto (ver [`/historia/05_memoria_y_conocimiento.md`](../historia/05_memoria_y_conocimiento.md) y el capítulo planeado sobre módulos en `/historia/00_indice.md`) y fue reparada más adelante.

## Biblioteca de conocimiento (RAG)

Búsqueda semántica sobre una biblioteca de casi mil archivos distintos, con 606.064 fragmentos de texto indexados a la fecha más reciente confirmada (Sesión 120, 22/08/2026) — una cifra que fluctuó bastante a lo largo del proyecto, llegando a un pico de 1,4 millones a mediados de agosto antes de una limpieza masiva de duplicados acumulados; ver el detalle completo en [`arquitectura.md`](arquitectura.md). Organizada por dominio:

- **Trading:** libros de referencia (Murphy, Elder, Douglas, y muchos más), más el contenido propio generado a partir del curso de Sabri Conessa (ver [`/historia/06_como_aria_aprendio_a_operar.md`](../historia/06_como_aria_aprendio_a_operar.md)).
- **Programación:** libros y documentación técnica de distintos lenguajes y herramientas.
- **IA / Machine Learning:** bibliografía de referencia del área (Bishop, Sutton & Barto, entre otros).
- **Tecnología general:** cientos de documentos adicionales, sumados y reorganizados varias veces a lo largo del proyecto.

Puede leer y resumir transcripciones de videos de YouTube, indexando el contenido para consultas futuras.

## Autonomía acotada (Módulo 9)

En período de prueba formal desde el 23 de agosto de 2026 (no cerrado como funcionalidad definitiva). Casos de uso reales conectados: consulta de tipo de cambio de moneda, precio de la plata, e índice de sentimiento de mercado (Fear and Greed Index) — cada uno contra una fuente externa específica y fija, no contra la web en general. Ver [`/tecnico/decisiones.md`](decisiones.md) para los límites explícitos de esta autonomía.

## Trading

Puede responder preguntas sobre mercados usando su biblioteca indexada y funciones puntuales de precio en tiempo real (criptomonedas, oro, plata). **ARIA no ejecuta ninguna operación de trading real bajo ninguna circunstancia** — cualquier decisión de mercado la toma Alejandro, nunca el sistema. Esto es un límite de diseño explícito, no una limitación técnica pendiente de resolver.

## Funciones puntuales

A través de un mecanismo de reconocimiento de comandos directos (function calling), sin pasar por la biblioteca de conocimiento: hora actual, cálculos matemáticos (incluyendo operaciones dichas en palabras, no solo símbolos), precio de criptomonedas en tiempo real, estado del sistema (uso de GPU, memoria, etc.), listado de archivos modificados recientemente, y un análisis técnico básico de trading con indicadores (RSI, EMA, MACD).

## Otras capacidades puntuales documentadas

- **Recordatorios** con hora automática.
- **Resumen semanal** y **rutina matutina** automatizados (mencionados como capacidades activas en configuración, sin desarrollo narrativo propio en este repositorio).
- **Guardado de resultados de búsqueda web** en la biblioteca indexada, para no tener que rebuscar lo mismo dos veces.

---

*Nota editorial: cada capacidad de este documento está tomada con cita textual de manuales técnicos y de sesión del proyecto. Dos elementos mencionados en configuración (`resumen_semanal`, `rutina_matutina`, `pagos_recurrentes`) se listan como activos según su propio archivo de configuración, pero no tienen desarrollo narrativo verificado en el material disponible más allá de su nombre — se incluyen con esa salvedad, no se omiten ni se completan con una descripción inventada de su funcionamiento.*
