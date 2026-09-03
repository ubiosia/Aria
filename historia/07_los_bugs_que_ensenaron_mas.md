# Capítulo 7 — Los bugs que enseñaron más

Hay errores que se corrigen y se olvidan. Y hay errores que, al corregirlos, obligan a mirar más atrás de lo cómodo — no "¿qué línea está mal?", sino "¿qué decisión de diseño hizo posible que esto pasara, y dónde más puede estar pasando ahora mismo, sin que nadie lo haya notado todavía?".

El más serio de esa segunda clase, en todo el proyecto, empezó con una pregunta inocente: "qué sabés de IA".

## Un ejemplo que se escapó de su lugar

A principios de julio, semanas después de que ARIA tuviera ya un dominio dedicado a Inteligencia Artificial —con su propia biblioteca curada de libros académicos—, alguien le preguntó eso mismo: qué sabía del tema. A veces, no siempre, la respuesta no tenía nada que ver con IA. Tenía nombre, tenía familia, tenía datos personales que no pintaban en absoluto en esa conversación.

La causa, una vez encontrada, resultó casi ridícula en su simpleza y alarmante en sus implicancias: un manual viejo del propio proyecto —de semanas atrás, de una etapa muy anterior— estaba indexado en la base de conocimiento con la categoría "ia" puesta por error. Y ese manual, como cualquier documentación técnica honesta de este proyecto, incluía un ejemplo de cómo respondía ARIA a una pregunta de memoria personal. Un ejemplo pensado para explicar cómo funcionaba el sistema, no para ser citado como si fuera conocimiento sobre Inteligencia Artificial. Pero para la máquina, categoría es categoría: si algo dice "ia", se busca ahí cuando preguntan por ia. El ejemplo se colaba en las respuestas, ocupando el lugar de un libro de verdad.

Se resolvió rápido, en dos frentes a la vez: se le enseñó al agente de IA a priorizar siempre la biblioteca curada por sobre el fondo general contaminado, y se recategorizaron a mano los más de mil trescientos fragmentos de ese manual viejo, sacándolos de "ia" y poniéndolos en una categoría que reflejara lo que realmente eran —documentación interna del proyecto, no material de consulta—.

Un arreglo limpio. Pero un arreglo que resolvía el síntoma, no todavía la pregunta de fondo: ¿por qué fue posible que un documento terminara mal etiquetado en primer lugar, y cuántos más como ese podían estar esperando, sin descubrir, en una base de datos que para entonces ya superaba el millón de fragmentos?

## La misma grieta, una semana después

La respuesta no tardó en llegar, y no fue tranquilizadora. Días más tarde, al terminar de construir un dominio nuevo —esta vez para contenido de programación—, apareció el mismo síntoma en un lugar distinto: preguntas técnicas de programación que deberían haber usado la biblioteca recién curada seguían devolviendo contenido genérico, mezclado, sin ninguna relación real con lo preguntado. Incluyendo, otra vez, ecos del mismo manual viejo.

Encontrar la causa esta vez costó más, porque las primeras hipótesis fallaron una detrás de otra: no era la caché de respuestas (se limpió dos veces, sin cambios), y una primera revisión del código pareció confirmar que el agente nuevo sí estaba bien registrado en el sistema —una conclusión que resultó ser un falso negativo, producto de haber probado una pieza aislada del sistema en vez del arranque completo real—. Recién con un registro de diagnóstico agregado a mano, sin ambigüedad posible, quedó confirmado: el agente de programación simplemente nunca se estaba llamando.

La causa raíz, cuando por fin apareció, era pequeña y estructural a la vez: en algún lugar del núcleo del sistema sobrevivía una lista fija, escrita a mano, de "categorías válidas" —una herencia de una versión mucho más antigua del código—, y esa lista nunca se había actualizado para incluir el dominio de programación cuando se creó. El sistema reconocía bien de qué hablaba la pregunta. Pero esa lista vieja, sin que nadie lo supiera, la descartaba en silencio antes de llegar al agente correcto, dejándola caer al fondo general del sistema —sin ningún filtro de categoría que la protegiera—.

Fue el mismo patrón exacto que ya había aparecido para IA, una semana antes, con un mecanismo distinto pero una raíz idéntica: **una regla de negocio importante, viviendo en un solo lugar hardcodeado del código, que nadie recuerda actualizar cuando el sistema crece.**

## Una tercera grieta, encontrada antes de que doliera

En medio de este mismo diagnóstico apareció una tercera pieza del mismo problema, esta vez descubierta antes de causar daño real, no después: el mecanismo que decide qué respuestas *no* deben guardarse en caché —pensado, en su momento, solo para proteger las respuestas de trading— tampoco cubría a los dominios nuevos de tecnología, IA y programación. Si una respuesta contaminada llegaba a generarse una sola vez, antes de corregir la causa de fondo, el sistema de caché la habría guardado y servido una y otra vez a cualquiera que preguntara lo mismo después —una respuesta incorrecta, convertida en la respuesta oficial del sistema, simplemente por haber sido la primera en llegar—.

Se corrigió sumando los tres dominios de contenido curado a esa lista de exclusión, cerrando una puerta que, por suerte, todavía no se había usado para hacer daño.

## Lo que dijo el colega que faltaba decir

Con dos apariciones del mismo patrón en menos de diez días, un colega que revisó el trabajo de esas semanas hizo una observación incómoda pero necesaria, más allá de los dos bugs puntuales ya resueltos: con más de un millón de fragmentos ya indexados, y sin que nadie auditara ese volumen de forma sistemática, era razonable asumir que existían más documentos mal categorizados sin descubrir todavía. No una posibilidad remota — una probabilidad real, dado que ya habían aparecido dos casos del mismo origen sin buscarlos a propósito, solo porque alguien hizo la pregunta equivocada en el momento equivocado.

Ese señalamiento se tomó en serio. Se construyó una herramienta de auditoría dedicada —de solo lectura, sin ninguna capacidad de modificar nada por sí sola— y se corrió sobre toda la base de conocimiento. El resultado inicial fue contundente: 1.335 posibles fugas de datos personales detectadas. Antes de asumir que todas eran reales, se investigó cada una: la enorme mayoría resultaron ser falsos positivos —coincidencias de nombres genéricos, como el nombre de una autora de un libro de Python que por casualidad se parecía a un patrón de búsqueda de nombre personal—, pero no todas. El manual viejo, el mismo de siempre, seguía teniendo miles de fragmentos sueltos en la colección de producción, más allá de la recategorización parcial de la primera vez.

Esta vez no se lo recategorizó. Se lo retiró por completo: se identificaron con precisión los fragmentos exactos pertenecientes a ese archivo, se hizo un backup completo antes de tocar nada, y se borraron uno por uno por su identificador exacto —no por una búsqueda aproximada de texto, que podría haberse llevado por delante contenido real que no tenía nada que ver—. Una segunda corrida de la misma auditoría, después del retiro, confirmó el resultado: las fugas reales bajaron a cero. Lo que quedaba —1.199 resultados— se revisó fragmento por fragmento y se confirmó, esta vez sí con evidencia y no con una suposición tranquilizadora, que eran todos falsos positivos.

## Lo que este capítulo deja, más allá del bug puntual

Ninguno de los tres hallazgos individuales —el manual mal categorizado, la lista hardcodeada, la caché sin proteger— fue, por separado, un desastre. Cada uno se corrigió en su momento, con evidencia, sin apuro ni pánico. Lo que los vuelve un capítulo aparte, y no tres líneas más en una lista de errores, es lo que tienen en común puesto uno al lado del otro: los tres nacieron del mismo punto ciego —un sistema que crece agregando piezas nuevas (un dominio, un agente, una colección) sin que existiera, todavía, un mecanismo automático que verificara que todo lo demás también se hubiera actualizado en consecuencia—. Y los tres coincidieron, sin ser el mismo bug, en la superficie más sensible que un asistente personal puede tener: datos de la familia de alguien, filtrándose donde no correspondía, sin que nadie lo hubiera pedido ni lo hubiera notado hasta que alguien hizo la pregunta correcta.

La respuesta de fondo no fue solo arreglar los tres síntomas. Fue construir, por primera vez, una herramienta que audita en vez de esperar a que un usuario tropiece con el problema —y dejar, como costumbre nueva, la idea de que en un sistema que sigue creciendo, "ya lo arreglamos" y "ya lo auditamos, en algún momento, por completo" no son la misma frase.

---

*Nota editorial: este capítulo está reconstruido con cita textual directa de los manuales de las Sesiones 44 a 47 (5 al 7 de julio de 2026) — específicamente la sección 3.4 de la Sesión 44 (el descubrimiento original en el dominio de IA), las secciones de errores y "Parte 4" de análisis de arquitectura de las Sesiones 45-46 (la reaparición en el dominio de programación y el hallazgo del colega externo), y las secciones 3.1 a 3.3 de la Sesión 47 (la auditoría formal, el retiro completo del documento y el cierre de las tres partes del hallazgo). Las cifras citadas (1.338 fragmentos recategorizados, 1.335 y luego 1.199 hallazgos de auditoría, 3.568 fragmentos retirados) provienen todas de las tablas de estado de esos mismos manuales. Siguiendo un acuerdo explícito sobre el alcance de este capítulo, no se menciona acá el episodio de pérdida de datos que precedió al nacimiento del proyecto (narrado, en la medida documentada, en el Capítulo 1) — es un hecho distinto, de otro momento del proyecto, sin relación con el mecanismo de este bug.*
