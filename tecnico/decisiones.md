# Decisiones de arquitectura

Este documento reúne las decisiones de diseño que marcaron el rumbo del proyecto, con el razonamiento real detrás de cada una — no una lista de opciones técnicas abstractas, sino lo que efectivamente se decidió y por qué, incluyendo los casos en que la decisión fue pragmática antes que ideal.

## Por qué WSL2 y no Ubuntu nativo

La decisión de fondo, contada con honestidad, empieza con una confusión: al arrancar el proyecto se asumía que la máquina tenía Ubuntu en dual-boot. Al verificar el entorno real con `wsl --list --verbose`, apareció que en realidad era WSL2 — Ubuntu corriendo dentro de Windows, no una instalación nativa aparte. La lección que quedó de ese momento se anotó explícitamente: antes de instalar nada, verificar el entorno real con comandos de diagnóstico, nunca asumir.

Una vez aclarado ese punto, la comparación quedó planteada en términos simples: WSL2 es más cómodo para empezar, porque Ubuntu corre sin reiniciar la máquina; una instalación nativa en dual-boot rinde mejor con la GPU, aproximadamente un 10% más rápido, pero exige arrancar directamente en Linux cada vez. La decisión tomada fue quedarse con WSL2 por comodidad, dejando la migración a una instalación nativa como una mejora futura — no como una tarea pendiente urgente.

Esa mejora futura se evaluó formalmente más adelante, unas semanas después de la instalación inicial, y la conclusión fue no migrar: mover meses de trabajo y de datos ya indexados a una configuración nueva representaba un riesgo concreto de pérdida, frente a una ganancia de rendimiento que no era crítica para el uso real del sistema. La decisión se marcó como definitiva, sin plan de revisarla salvo que apareciera una razón nueva y de peso.

## Por qué separar ARIA y SabriBot

ARIA y un proyecto de trading automatizado distinto —hoy conocido como SabriBot— convivieron desde etapas tempranas en la misma máquina, en carpetas y entornos completamente separados por regla explícita. Esa separación no fue una formalidad: nació de un incidente real, temprano en el proyecto, donde el trabajo terminó aplicándose por error sobre la terminal del sistema equivocado durante varios minutos, sin que nada avisara del error hasta que las respuestas dejaron de tener sentido.

Con el tiempo, esa separación lógica pasó a plantearse también como separación física. El razonamiento documentado es doble: por un lado, ARIA es un asistente generalista —memoria personal, biblioteca de conocimiento, trading solo como una de varias funciones— mientras que SabriBot es, específicamente, un sistema de trading real. Mezclar ambos en la misma máquina y el mismo entorno multiplica el riesgo de que un error en uno afecte al otro, algo particularmente delicado cuando uno de los dos maneja decisiones de mercado reales. Por otro lado, separar físicamente permite que cada sistema se optimice para lo que realmente necesita, sin tener que compartir recursos de hardware entre un asistente de uso diario y un sistema que corre con expectativas de disponibilidad distintas.

El plan concreto, documentado pero no ejecutado al cierre del material disponible, consiste en usar la máquina secundaria ("Pruebas") como el nuevo servidor de trabajo diario de ARIA, y transformar la máquina principal actual en la máquina dedicada a SabriBot. Antes de ejecutar esa migración, el propio plan establece terminar primero los pendientes reales de ARIA en curso — empezando por el Módulo 9 de autonomía, que se explica más abajo.

## Los límites de la autonomía

ARIA no tomó capacidades de autonomía todas de una vez. El crecimiento se ordenó, de forma deliberada, en fases sucesivas — un Módulo 9 dedicado, con fases numeradas de la 0 a la 4, donde cada una se da por completa y estable en producción antes de habilitar la siguiente.

Las primeras fases (0, 1 y 2) llevan tiempo en producción sin cambios. La Fase 3 —búsqueda web acotada— es la más reciente: en vez de darle a ARIA acceso libre a internet, cada caso de uso se conecta de forma explícita y puntual (tipo de cambio de moneda, precio de la plata, un índice de sentimiento de mercado), contra una lista fija de dominios permitidos, no contra la web en general. Cada caso nuevo que se agrega pasa, además, por un período de prueba real antes de considerarse estable — dos semanas de uso sin incidentes de contenido no confiable, como mínimo, antes de sumar el siguiente caso.

Ese mismo criterio de cautela aparece, con más fuerza todavía, en lo que se decidió no construir. ARIA no ejecuta operaciones de trading reales bajo ninguna circunstancia — cualquier decisión de mercado la toma Alejandro, nunca el sistema. Se descartó explícitamente un modo de agentes autónomos más ambicioso, pensado para planificar y ejecutar tareas por su cuenta sin supervisión directa, con nombre interno de proyecto ("Modo Jefe"): no llegó a construirse. También se descartaron los webhooks públicos y el arranque automático del sistema al iniciar Windows — dos formas de reducir fricción que, a cambio, hubieran ampliado la superficie de exposición del sistema sin una necesidad real que lo justificara.

El criterio de fondo, repetido en distintas decisiones a lo largo del proyecto, es el mismo: sumar autonomía de a un paso verificable por vez, con evidencia real de que cada paso funciona antes de dar el siguiente, en vez de construir capacidades amplias de entrada y confiar en que se comporten bien.

---

*Nota editorial: la decisión de WSL2 y su razonamiento están documentados con cita textual completa, incluyendo la confusión inicial sobre el dual-boot y la lección aprendida de verificar el entorno antes de asumirlo. La separación ARIA/SabriBot combina un hecho documentado temprano (el incidente de la terminal equivocada, narrado en `/historia/02_los_primeros_tropiezos.md`) con el plan de arquitectura de largo plazo documentado en la Sesión 121, todavía sin ejecutar. Los límites de autonomía y las capacidades descartadas están tomados de los manuales de sesión de agosto de 2026 y coinciden con la lista de "descartado explícitamente" de `/meta/estado_actual.md`.*
