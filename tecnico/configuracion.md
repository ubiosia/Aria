# Configuración

Variables de entorno usadas por ARIA, sin valores reales — solo nombre, propósito y notas sobre cómo se cargan. Ninguna clave, token o contraseña de este proyecto se reproduce en este repositorio, ni siquiera parcial o enmascarada.

## Variables principales

| Variable | Propósito |
|---|---|
| `GROQ_API_KEY` | Clave de API para el proveedor de inferencia en la nube usado por el agente de trading cuando `TRADING_MODE=CLOUD`. |
| `GROQ_API_KEY_TECNOLOGIA` | Clave de API equivalente, usada por el agente de tecnología. |
| `GROQ_API_KEY_IA` | Clave de API equivalente, usada por el agente de IA. |
| `TRADING_MODE` | Controla si el agente de trading responde con el modelo local (RAG) o con el proveedor en la nube. Valores usados: `LOCAL` o `CLOUD`. |
| `ARIA_DISABLE_WHISPER` | Desactiva el reconocimiento de voz cuando no hace falta (por ejemplo, en pruebas automatizadas). |
| `ARIA_SKILLS_DISCOVERY` | Activa el descubrimiento automático de nuevas capacidades (skills/handlers) sin tener que registrarlas a mano. |

## Dónde viven

Las variables se definen en un archivo `.env` dentro de la carpeta del proyecto, no versionado en git. Algunas se exportan también desde `~/.bashrc` cuando necesitan persistir en cualquier terminal nueva, no solo en el proceso que carga el `.env` directamente.

## Un problema real de configuración, documentado como advertencia

Una variable exportada en `~/.bashrc` tiene prioridad sobre lo que diga el archivo `.env` en cada terminal nueva que se abre — y esa prioridad no es evidente a simple vista. Hubo un caso real donde `TRADING_MODE` se cambió en el `.env` pero el sistema seguía comportándose como si tuviera el valor viejo, porque una línea olvidada en `.bashrc` seguía exportando el valor anterior en cada terminal. La lección: si una variable no parece tomar el valor esperado, verificar primero si existe una exportación duplicada en `.bashrc` antes de asumir un bug en el código.

Otro caso real: cargar un archivo `.env` con `source` no siempre funciona si el archivo tiene comillas o valores de ejemplo sin completar — puede hacer falta extraer el valor explícitamente (por ejemplo, con `grep` y `cut`) en vez de confiar en que el `source` interprete el archivo como se espera.

## Dominios permitidos (Módulo 9, Fase 3)

La búsqueda web acotada del sistema no consulta la web en general — cada caso de uso conectado tiene una fuente específica, y el conjunto de dominios permitidos se mantiene en un archivo de configuración separado (`dominios_permitidos.json`), no en variables de entorno. Ver [`/tecnico/arquitectura.md`](arquitectura.md) para el detalle de cómo se usa.

---

*Nota editorial: los nombres de variables y los dos problemas de configuración documentados en este archivo están tomados con cita textual de manuales técnicos internos del proyecto. Ningún valor real de clave, token o contraseña se reproduce aquí, siguiendo la regla de privacidad del repositorio — incluso los que aparecían truncados o parcialmente visibles en la fuente original se omitieron por completo.*
