# ARIA V8 — Asistente de IA personal, local y sin nube

[![Verificación](https://github.com/ubiosia/Aria/actions/workflows/verificacion.yml/badge.svg)](https://github.com/ubiosia/Aria/actions/workflows/verificacion.yml)

> ¿Primera vez acá? Empezá por [`START_HERE.md`](START_HERE.md).

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
| [`/historia/`](historia/) | El viaje completo, contado en capítulos (1-7 y 11 escritos; 8-10 planeados). |
| [`/tecnico/`](tecnico/) | Respuestas rápidas sin historia: instalación, arquitectura, decisiones, bugs con causa y fix. |
| [`/meta/`](meta/) | Datos duros: estado actual, línea de tiempo, glosario con referencia de sesión, agradecimientos. |
| [`/codigo/`](codigo/) | Código real de ARIA, sanitizado, más un core mínimo ejecutable (marcado como tal donde no es código real). |
| [`/tests/`](tests/) | Tests automatizados (enrutamiento, memoria) — corren en CI en cada push. |

## Correr el core mínimo

Este repositorio no es solo documentación — se puede clonar y correr una versión mínima real:

```
git clone https://github.com/ubiosia/Aria.git
cd Aria
./arrancar_aria.sh "que es un arbol binario"      # Linux/WSL2
arrancar_aria.bat "que es un arbol binario"       # Windows
```

Eso arma un entorno virtual, instala solo lo que el core mínimo necesita (`requirements-core.txt`: `chromadb` + `ollama`, sin las dependencias de voz que sí lleva la instalación completa), rutea la pregunta con el mismo enrutador real que usa ARIA en producción (`codigo/config_dominios.py`), y busca contexto en ChromaDB antes de pasárselo a un modelo de Ollama. Sin Ollama corriendo o sin contenido indexado todavía, vas a ver mensajes claros en vez de un error — el enrutamiento se puede ver funcionando igual. Detalle completo, incluida la verificación funcional de qué se probó y qué no: [`/codigo/README.md`](codigo/README.md).

## Cómo seguir leyendo, según lo que busques

| | Si buscás esto... | Empezá acá |
|---|---|---|
| 🟢 | Un resumen rápido, sin comprometerte a leer todo | Ya lo tenés arriba, en la ficha del proyecto |
| 🟡 | El viaje completo, capítulo a capítulo, con los tropiezos incluidos | [`/historia/00_indice.md`](historia/00_indice.md) |
| 🔵 | Respuestas técnicas puntuales — instalación, arquitectura, decisiones, bugs con causa y fix | [`/tecnico/`](tecnico/) |
| 🟣 | Los datos duros — estado real del sistema, línea de tiempo, glosario, agradecimientos | [`/meta/`](meta/) |

¿Buscás código real y no solo la historia detrás? → [`/codigo/`](codigo/). ¿Te dan ganas de aportar algo? → [`CONTRIBUTING.md`](CONTRIBUTING.md) — este es un proyecto abierto, no un capítulo cerrado.

Este repo tiene verificación automática (CI) — ver el badge arriba. Corre en cada push: sintaxis de `/codigo/` y los tests de [`/tests/`](tests/).

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

## Legado — cómo continuar este proyecto

Este trabajo no está terminado. Se detuvo en un momento real, por cansancio genuino de meses de trabajo sostenido por una sola persona — no porque no quedara nada más por hacer.

Si leíste esto y tenés ideas, correcciones, o querés retomar alguna parte del proyecto donde quedó, escribime (o mirá [`CONTRIBUTING.md`](CONTRIBUTING.md) para el detalle de las formas concretas de ayudar):

📧 **ubiosia@gmail.com**

Algunas formas concretas en las que podés aportar:
- Señalar errores o inconsistencias que encuentres en la documentación
- Proponer mejoras técnicas a la arquitectura descrita
- Compartir tu propia experiencia si construiste algo parecido
- Retomar cualquiera de los capítulos o módulos marcados como "planeados, no escritos todavía"

No hace falta pedir permiso para explorar, aprender o inspirarte en este trabajo — para eso está publicado. Si además querés avisarme qué hiciste con él, me va a interesar genuinamente saberlo.
