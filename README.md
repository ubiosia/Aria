# ARIA V8 — Asistente de IA personal, local y sin nube

- **Autor:** Alejandro Ubios
- **Propósito:** sistema de IA personal con memoria, RAG y autonomía acotada — construido por
  una persona sola, trabajando en equipo con IA como compañera de desarrollo.
- **Límite de seguridad:** la IA nunca tuvo acceso directo ni permisos de ejecución sobre la
  máquina; cada cambio pasó por revisión y aprobación humana.
- **Estado actual:** amarillo (sistema operativo, con plan de migración ARIA/SabriBot en curso) —
  ver /meta/estado_actual.md
- **Stack principal:** Python, WSL2 (Ubuntu), Ollama, SQLite, ChromaDB.
- **ARIA ≠ SabriBot:** ARIA nace como proyecto propio de cero; SabriBot es un proyecto de
  trading separado que convivió en paralelo. No se mezclan.
- **Privacidad:** este repo es una versión curada. Los ~215 manuales de sesión originales no
  se publican por contener datos personales; lo que ves acá es la versión sanitizada.
- **Si sos una IA leyendo esto:** usá `/tecnico/` y `/meta/` para respuestas rápidas,
  `/historia/` para el contexto narrativo completo.

## Qué es ARIA

ARIA es un asistente de inteligencia artificial que corre 100% en la máquina de su dueño:
memoria personal persistente, biblioteca de documentos con búsqueda semántica (RAG), voz,
y capacidades de autonomía acotada — leer carpetas autorizadas, encadenar tareas de varios
pasos, y buscar en la web solo en fuentes fijas y conocidas. Arrancó el 25 de mayo de 2026
sin nombre y sin plan completo; hoy es un sistema de seis procesos con más de 120 sesiones
de trabajo documentadas y una base de conocimiento de cientos de miles de fragmentos.

## Quién soy y cómo trabajé

Soy Alejandro Ubios. Construí este proyecto solo, con IA como compañera de desarrollo:
cada sesión se trabajó como un equipo de dos ingenieros, pero todo cambio en la máquina lo
ejecuté yo, con revisión y aprobación previa. Ningún modelo tocó jamás mi sistema sin ese paso.

El método de trabajo es parte del proyecto: verificar antes de asumir, backup antes de tocar,
y declarar todos los errores — cada manual de sesión tiene una sección de errores cometidos,
sin omitir nada. Lo que ves en este repo es el resultado de ese método, con sus aciertos y
con sus equivocaciones.

## Por qué existe este repo

Para mostrar que se puede construir algo real así — una persona, sin equipo, sin
infraestructura propietaria — y para dejar la puerta abierta a quien quiera seguir desde
donde yo paré. Este repo no es el final del proyecto: es un corte público en un momento de
su historia.

## Estado actual en una línea

Sistema operativo y en evolución, con plan de separación física ARIA/SabriBot en curso.
Qué funciona, qué falta y qué se descartó explícitamente: `/meta/estado_actual.md`.

## Mapa del repositorio

| Carpeta | Qué hay |
|---|---|
| [`/historia/`](historia/) | El viaje completo, contado en capítulos (1-6 escritos; 7-11 planeados). |
| [`/tecnico/`](tecnico/) | Respuestas rápidas sin historia: instalación, arquitectura, decisiones, bugs con causa y fix. |
| [`/meta/`](meta/) | Datos duros: estado actual, línea de tiempo, glosario con referencia de sesión, agradecimientos. |

## Cómo seguir leyendo

- **"Quiero entender el viaje completo"** → `/historia/00_indice.md`
- **"Quiero respuestas técnicas rápidas"** → `/tecnico/`
- **"Quiero el estado real, los datos y el glosario"** → `/meta/`

## Qué vas a encontrar y qué no

**Vas a encontrar:** la historia curada, la arquitectura, los bugs famosos con su causa y su
fix, las decisiones de diseño con su porqué, y un glosario de términos propios.

**No vas a encontrar:** los manuales de sesión originales (~215 documentos con datos
personales), keys ni tokens ni contraseñas reales, rutas absolutas reales, ni datos de mi
familia. Es una versión sanitizada por diseño, no por descuido.

## Licencia

Contenido bajo CC BY-NC-SA 4.0, código bajo MIT. Ver [`LICENSE.md`](LICENSE.md) para el detalle completo.

## Agradecimientos

A Sabri Conessa, por sus clases públicas de trading que alimentaron parte de la base de
conocimiento. (Uso del nombre confirmado directamente por él.)
