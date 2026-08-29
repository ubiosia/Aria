# Capítulo 4 — El bug del precio del oro

La pregunta era simple: "¿cuál es el precio del oro?". La respuesta, invariablemente, hablaba de Bitcoin.

No una vez. Cada vez. Sin importar cómo se formulara la pregunta, sin importar el canal —la interfaz web, Telegram, la línea de comandos—, ARIA contestaba con el precio de una criptomoneda que nadie había mencionado. No era una respuesta rara ni un error visible: era una respuesta completa, con número, con porcentaje de variación, con la seguridad de quien no duda. Solo que hablaba del metal equivocado.

Ese tipo de error —uno que responde con total confianza, solo que a la pregunta que no era— ya era, para entonces, un patrón conocido en el proyecto. Lo nuevo, esta vez, fue lo que se encontró al ir a buscar la causa: no había un solo responsable. Había tres.

## Tres capas queriendo lo mismo

Cuando se abrió el código para entender qué pasaba, apareció algo que ningún bug anterior había mostrado con tanta claridad: tres piezas distintas del sistema, escritas en momentos distintos y con objetivos distintos, competían por la misma palabra —"precio"— sin saber que las otras dos existían.

La primera pieza, apenas detectaba la palabra "precio" en cualquier pregunta, la mandaba directo a una búsqueda en internet, sin mirar nada más. La segunda —el enrutador que decidía a qué parte del sistema debía ir cada consulta— tenía a "precio" anotada como una de las palabras que activaban el dominio de trading, un dominio que, ante la duda, siempre asumía que se hablaba de Bitcoin, porque era el activo con el que se había construido originalmente. Y la tercera pieza, la única que sí sabía buscar específicamente el precio del oro, existía en el código, funcionaba bien cuando llegaba a ejecutarse... pero estaba escrita para correr después de las otras dos. Nunca llegaba a tiempo. Las primeras dos ya habían respondido —mal— antes de que la tercera tuviera oportunidad de hacerlo bien.

Ninguna de las tres piezas estaba, en sí misma, mal escrita. El problema no vivía adentro de ninguna de ellas: vivía en el espacio entre las tres, en la falta de una que supiera de la existencia de las otras dos.

La primera respuesta, como suele pasar, fue un parche de urgencia: una condición nueva, agregada por delante de todo lo demás, que reconocía palabras como "oro", "xau" o "gold" y las mandaba directo a la fuente correcta antes de que cualquier otra pieza del sistema tuviera chance de interceptarlas. Funcionaba. Pero todos, incluido quien lo escribió, sabían que era un remiendo: la próxima vez que alguien preguntara por plata, o por petróleo, o por cualquier otro activo que las piezas viejas no reconocieran, el mismo problema iba a volver a aparecer, con otro nombre.

## Tres caminos, una decisión

Frente a un parche que resuelve el síntoma sin tocar la causa, había que elegir cómo seguir. Se plantearon, con la frialdad de quien no quiere decidir por impulso, tres caminos posibles.

El primero era simplemente seguir parchando: cada vez que apareciera un activo nuevo con el mismo problema, agregar una excepción más. Rápido, de bajo riesgo inmediato, pero con una deuda que crece sin límite visible, escondida hasta el próximo caso.

El segundo era reordenar: hacer que la pieza que sí sabía responder bien —la tercera, la que llegaba tarde— pasara a ejecutarse primero, antes que las otras dos tuvieran oportunidad de opinar. Un cambio acotado, pero que necesitaba probarse con cuidado antes de confiar en él.

El tercero era más ambicioso: rehacer de raíz todo el sistema de decisión, con un único lugar que ordenara con claridad qué pregunta va a dónde, sin piezas sueltas compitiendo entre sí. La solución más prolija, a largo plazo. También la de mayor riesgo, y la que más tiempo iba a llevar en un proyecto que todavía estaba creciendo rápido en otras direcciones.

La decisión no se tomó en soledad. Se consultó a cinco colegas de inteligencia artificial, por separado, sin que uno viera lo que respondían los otros. El consenso fue fuerte a favor del segundo camino, con dos aportes que terminaron de darle forma a la solución final: no bastaba con reordenar, también había que limpiar las dos piezas viejas para que dejaran de competir por la palabra en primer lugar. Y le pusieron nombre al problema de fondo, uno que iba a quedar instalado en el vocabulario del proyecto de ahí en más: **route shadowing** —una regla genérica que, sin querer, tapa a una regla más específica que debería haber tenido prioridad.

La solución implementada, entonces, tuvo tres partes: la pieza correcta pasó a ejecutarse primero; se le quitó a la segunda pieza la palabra genérica "precio" de su lista de disparadores, dejándole solo nombres concretos de criptomonedas; y se eliminó el atajo automático de búsqueda web que la primera pieza activaba con solo ver esa palabra. El parche de emergencia, ya innecesario, se retiró. Se probó con siete preguntas distintas —oro, Bitcoin, análisis técnico, memoria personal, la hora, noticias, un simple saludo— y las siete respondieron por el camino correcto. El caso se dio por cerrado.

## El mismo fantasma, otra puerta

Diez días después, una noche de julio, alguien decidió no confiar en que el arreglo estuviera realmente completo solo porque las pruebas anteriores habían salido bien. Antes de dar por cerrada una tanda distinta de mejoras, se mandó una serie de preguntas reales por Telegram —un canal que no se había usado para validar el fix original—. Entre ellas, otra vez, la misma de siempre: "¿cuál es el precio del oro?".

Y otra vez, la respuesta fue Bitcoin.

El primer instinto fue sospechar de la pieza que ya se había arreglado en junio: revisarla línea por línea, con cuidado, buscando algo que se hubiera pasado por alto. No había nada mal ahí. El arreglo de la Sesión 34 seguía intacto, funcionando exactamente como se lo había dejado.

El problema, esta vez, estaba en otro lugar completamente distinto: una puerta de entrada rápida, pensada para responder preguntas simples de precio sin pasar por todo el sistema de decisión —un atajo construido con buena intención, para que esas consultas fueran instantáneas—, y que nadie había revisado cuando se corrigió el resto. Ese atajo interceptaba cualquier pregunta con la palabra "precio" antes de que llegara al núcleo del sistema, asumía que se trataba de una criptomoneda, y devolvía Bitcoin por defecto si no encontraba ninguna otra mencionada explícitamente. Exactamente el mismo síntoma que en junio. Exactamente la misma familia de error. Pero en una puerta distinta, construida después, que el arreglo original nunca tuvo la oportunidad de tocar porque todavía no existía cuando se hizo.

La corrección, esta vez, fue puntual: agregarle a ese atajo la misma lista de excepciones —oro, plata, y sus nombres técnicos— que ya protegía al resto del sistema. Bastaron unas pocas líneas. Pero el hallazgo importaba más que la corrección en sí: confirmaba que el patrón de fondo —varias partes del sistema, cada una con su propia idea de qué hacer con una palabra clave, sin ponerse de acuerdo entre sí— no había desaparecido con el primer arreglo. Solo se había escondido en un lugar que todavía no se había mirado.

Esa comprobación —que un mismo tipo de error puede reaparecer por una puerta distinta si la causa de fondo nunca se resuelve del todo— fue, más que el bug puntual del oro, lo que terminó de convencer a Alejandro de que el proyecto necesitaba, tarde o temprano, un único lugar central donde vivieran esas reglas de decisión, en vez de repartidas en media docena de archivos que nadie terminaba de mantener sincronizados entre sí. Ese trabajo, más ambicioso, iba a llegar pronto. Pero antes tenía que pasar algo más: ARIA tenía que aprender, en serio, a recordar.

---

*Nota editorial: los dos episodios de este capítulo están documentados con detalle técnico completo en los manuales de sesión del proyecto —el postmortem original en la Sesión 34 (23-24 de junio de 2026), con la consulta a cinco colegas de IA y el nombre "route shadowing", y la reaparición del mismo síntoma por una causa distinta en la Sesión 43 (4 de julio de 2026), encontrada mediante pruebas reales por Telegram. Ambos manuales forman parte del mismo documento compilado que reveló, tras una revisión más cuidadosa, el contenido de sesiones tempranas que en un primer borrador de este libro se habían dado por no disponibles.*
