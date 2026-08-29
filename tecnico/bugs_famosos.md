# Bugs famosos

Los bugs de este proyecto que dejaron una lección duradera, no solo una corrección puntual. Casi todos comparten un mismo patrón de fondo: un sistema que responde con total normalidad, sin ningún error visible, mientras hace algo distinto de lo que debería. El patrón tiene nombre propio dentro del proyecto — **route shadowing** — y aparece primero, con mayor claridad, en el primero de estos casos.

## El bug del precio del oro (y el nombre "route shadowing")

**Síntoma:** preguntarle a ARIA por el precio del oro devolvía, de forma consistente, el precio de Bitcoin.

**Causa real:** tres piezas distintas del sistema competían por la palabra "precio" sin saber que las otras existían. Una la mandaba directo a una búsqueda web. Otra la enrutaba al dominio de trading, que por defecto asumía que se hablaba de Bitcoin. Una tercera pieza sí sabía buscar el precio del oro correctamente, pero estaba escrita para ejecutarse después de las otras dos — nunca llegaba a tiempo.

**Solución:** reordenar para que la pieza correcta se ejecutara primero, y limpiar las dos piezas viejas para que dejaran de competir por la palabra genérica. Consultado con cinco colegas de inteligencia artificial por separado, de ahí salió el nombre para el patrón de fondo: **route shadowing** — una regla genérica que, sin querer, tapa a una regla más específica que debería tener prioridad.

**La reaparición:** diez días después, el mismo síntoma volvió a aparecer — pero por una causa completamente distinta: un atajo de respuesta rápida, en un punto de entrada distinto del sistema, que nadie había tocado al arreglar el problema original. La lección que dejó esta segunda vuelta fue tan importante como la primera: un mismo patrón de bug puede reaparecer por una puerta distinta si la causa de fondo — reglas de decisión repartidas en varios lugares sin coordinación central — nunca se resuelve del todo.

*Sesiones 34 (23-24/06/2026) y 43 (04/07/2026). Ver [`/historia/04_el_bug_del_precio_del_oro.md`](../historia/04_el_bug_del_precio_del_oro.md) para el relato completo.*

## El volcado de memoria personal

**Síntoma:** preguntarle a ARIA algo puntual sobre datos personales —por ejemplo, dónde vive Alejandro— no devolvía una respuesta directa, sino todos los datos guardados en la memoria personal del sistema, uno detrás de otro.

**Causa real, encontrada recién en un tercer intento de diagnóstico:** un atajo interceptaba cualquier pregunta sobre memoria personal antes de que el enrutamiento general del sistema tuviera oportunidad de decidir nada, y ese atajo solo sabía hacer una cosa — mostrar todo lo guardado, sin distinguir una pregunta puntual de un pedido genérico. Los dos primeros diagnósticos, en sesiones distintas, no llegaron a ver esa pieza: uno concluyó que no había bug, sino diseño intencional; el otro encontró una parte del problema, pero no la causa completa.

**Solución:** en lugar de resolverlo con el modelo de lenguaje, se optó por una búsqueda directa y determinística en la base de datos — sin ningún paso intermedio que pudiera inventar o malinterpretar un dato personal sensible.

*Sesiones 56 a 58 (julio de 2026). Ver [`/historia/05_memoria_y_conocimiento.md`](../historia/05_memoria_y_conocimiento.md) para el relato completo, incluyendo un antecedente relacionado pero distinto de Sesiones 33-35.*

## El libro que se indexó casi vacío

**Síntoma:** un libro de programación procesado con OCR pasó la ingesta sin ningún error visible, pero terminó indexado con una fracción mínima de su contenido real.

**Causa real:** el proceso de OCR generaba un archivo de texto por cada página escaneada, nombrado con el número de página. El script de consolidación esperaba ese número con cuatro dígitos de relleno (por ejemplo, `pagina-0001.txt`), porque así se había armado para un libro anterior de más de mil páginas — pero este libro tenía menos páginas y sus archivos usaban tres dígitos (`pagina-001.txt`). El script no encontraba coincidencias exactas para casi ninguna página, y terminaba consolidando solo una línea por archivo en vez del texto completo: el resultado fueron 407 líneas indexadas en lugar de las cerca de 21.000 esperadas. Sin ningún mensaje de error — el proceso "funcionó", solo que casi no indexó nada real.

**Solución:** generar el número de página de forma explícita en el momento (`printf %04d` o el formato que correspondiera a cada libro), en vez de asumir un formato heredado de un proceso anterior sin verificarlo primero.

*Documentado en el manual de Sesiones 40 a 46 (julio de 2026).*

---

*Nota editorial: los tres bugs de este documento están verificados con cita textual directa contra los manuales de sesión correspondientes. Dos candidatos adicionales mencionados originalmente para este documento no se incluyeron: uno, descrito como "el OCR de Murphy que indexaba solo números de página", no coincide con lo documentado — el libro de John Murphy sí se indexó correctamente vía OCR (Sesión 108, 1.552 fragmentos de buena calidad); el bug real de numeración de páginas por OCR ocurrió con otro libro distinto (un libro de ejercicios de programación, ver el tercer caso de este documento). El otro candidato, "el EA de Sabri cargado tres veces en el mismo símbolo", no se pudo verificar con ninguna cita en el material disponible — no se incluye hasta que aparezca una fuente concreta.*
