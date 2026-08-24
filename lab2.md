# Laboratorio #2 - Esquemas de detecciÃ³n y correcciÃ³n de errores

![Logo de la Universidad del Valle de Guatemala](output/laboratorio_2_2026_assets/pagina-1-imagen-1.png)

**Universidad del Valle de Guatemala**  
Facultad de IngenierÃ­a  
Departamento de Ciencias de la ComputaciÃ³n  
CC3067 Redes | Ciclo 2 de 2026

---

## I. Objetivo

El ruido y los errores de transmisiÃ³n ocurren en toda comunicaciÃ³n, y es parte de los retos al implementar este tipo de sistemas manejar adecuadamente las fallas que puedan ocurrir. Por lo tanto, a lo largo de la evoluciÃ³n del Internet se han desarrollado distintos mecanismos que sirven tanto para la detecciÃ³n como para la correcciÃ³n de errores.

Los objetivos principales son los siguientes:

- Comprender el funcionamiento de un modelo de capas y sus servicios.
- Implementar los algoritmos de detecciÃ³n y correcciÃ³n de errores.
- Analizar el funcionamiento de los esquemas de detecciÃ³n y correcciÃ³n.
- Experimentar la transmisiÃ³n de informaciÃ³n expuesta a un canal no confiable.
- Identificar las ventajas y desventajas de cada uno de los algoritmos.

## II. Condiciones y fechas de entrega

**Fecha de Entrega:** 12 de agosto, 2026.

- Incluir todo el cÃ³digo involucrado y cualquier elemento para su compilaciÃ³n (makefiles, etc).
- Incluir el enlace a su repositorio, el cual si es privado debe otorgar permisos de acceso al profesor y auxiliares.
- Incluir su reporte en formato PDF.
- Asegurarse de que el PDF sea formal y bien estructurado, acorde al nivel de un estudiante de 4to aÃ±o de IngenierÃ­a UVG.
- Subir cada archivo individualmente. No se permite entregar un archivo `.zip` con todo el contenido.

## I. Materiales

No existe ningÃºn material especifico para el desarrollo de este laboratorio.

## II. Ejercicios

### Ejercicio 1 (100 puntos)

En clase estudiamos que entre los servicios que ofrece la capa de Enlace se encuentran la detecciÃ³n y correcciÃ³n de errores, pues se asume que el medio en el que se transmite la data no es confiable. En este laboratorio se implementarÃ¡ al menos un algoritmo de cada uno de ellos y una aplicaciÃ³n para la transmisiÃ³n y recepciÃ³n de mensajes, con base a una arquitectura de capas con distintos servicios. El laboratorio se trabajarÃ¡ en parejas y, si el nÃºmero de estudiantes es impar, habrÃ¡ un Ãºnico trÃ­o.

### Arquitectura de Capas

La arquitectura cuenta con las siguientes capas y servicios:

![Diagrama de arquitectura de capas: emisor, receptor, aplicaciÃ³n, presentaciÃ³n, enlace, ruido y transmisiÃ³n](output/laboratorio_2_2026_assets/pagina-2-imagen-2.png)

#### DescripciÃ³n de los servicios

1. **APLICACIÃ“N**
   - **Solicitar mensaje:** solicita el texto a enviar al emisor. TambiÃ©n solicita el algoritmo a utilizar para comprobar la integridad.
   - **Mostrar mensaje:** muestra el mensaje al receptor (sin errores). Si se detectaron errores y no fue posible corregirlos, se debe indicar con un mensaje de error.

2. **PRESENTACION**
   - **Codificar mensaje:** codifica cada carÃ¡cter en ASCII binario. Por ejemplo, para el carÃ¡cter A el cÃ³digo binario ASCII es `01000001`.
   - **Decodificar mensaje:** si no se detectan errores, se debe decodificar el ASCII binario a los caracteres correspondientes. SI se detecta un error, se debe indicar de alguna forma a la capa de aplicaciÃ³n.

3. **ENLACE**
   - **Calcular integridad:** utilizando el algoritmo indicado en el servicio solicitar mensaje, calcular la informaciÃ³n de integridad. Concatenar la informaciÃ³n al mensaje binario original.
   - **Verificar integridad:** el algoritmo seleccionado debe calcular la informaciÃ³n del lado del receptor y compararla contra la proporcionada por el emisor para detectar posibles errores. Debe indicar esto a la capa de presentaciÃ³n. AquÃ­ es donde se deben integrar los algoritmos implementados en la primera parte del laboratorio.
   - **Corregir mensaje:** si el algoritmo tiene la capacidad de corregir los errores detectados, debe corregirlos.

4. **RUIDO**
   - **Aplicar ruido:** el ruido no es una capa como tal, pero a fin de simular interferencias, se tratarÃ¡ como una capa del lado del emisor y se aplicarÃ¡ ruido a la trama proporcionada por la capa de enlace. La forma de determinar si cada bit sufre un cambio se basarÃ¡ en cierta probabilidad expresada en errores por bits transmitido (por ejemplo, 1/100 es un error por cada 100 bits). Esta tasa debe ser solicitada el momento de enviar un mensaje. Recuerde que la informaciÃ³n de redundancia (p. ej., bits de paridad) tambiÃ©n estÃ¡ sujeta al ruido.

5. **TRANSMISION**
   - **Enviar informaciÃ³n:** envÃ­a la trama de informaciÃ³n a travÃ©s de sockets mediante el puerto elegido.
   - **Recibir informaciÃ³n:** recibe la trama de informaciÃ³n a travÃ©s de sockets mediante el puerto elegido. El receptor siempre debe estar â€œescuchandoâ€ en el puerto elegido a la espera de recibir data.

La aplicaciÃ³n del lado del emisor debe implementarse en un lenguaje de programaciÃ³n distinto del del receptor.

### Algoritmos para implementar

Se deberÃ¡n implementar al menos dos algoritmos (uno por integrante). De estos algoritmos, como mÃ­nimo, uno debe ser de correcciÃ³n de errores y otro de detecciÃ³n de errores. Se deben implementar tanto el emisor como el receptor para cada algoritmo e integrarlos en la capa de enlace de la arquitectura solicitada.

Lista de algoritmos sugeridos (pueden implementar otros):

- **CorrecciÃ³n de errores**
  - **CÃ³digos de Hamming**
    - Para cualquier $Codigo(n, m)$ que cumpla $(m + r + 1) <= 2^r$.
  - **CÃ³digos convolucionales (Algoritmo de Viterbi)**
    - Para cualquier trama de longitud $k$. La tasa de cÃ³digo es $M:1$ (por cada bit de entrada, salen $m$ bits de salida).

- **DetecciÃ³n de errores**
  - **Fletcher checksum**
    - Para cualquier trama de longitud $k$, con bloques de 8, 16 o 32 (las tres opciones, configurables). $k$ debe responder al bloque utilizado (mayor que el bloque, se agregan bits de padding en caso el mensaje sea menor).
  - **CRC-32**
    - Para cualquier trama de longitud $n$, $M_n(x)$ y el polinomio estÃ¡ndar para CRC-32 (uno de 32 bits, investigar cual es), donde $n > 32$ (o agregar bits de padding si es menor a eso).

### Pruebas

Utilizando los algoritmos implementados, realizar pruebas de envÃ­o y recepciÃ³n que evidencien su funcionamiento. Para estas pruebas, cada grupo deberÃ¡ elegir cÃ³mo las realizarÃ¡ y generar grÃ¡ficas que respalden estos datos. La cantidad y el contenido de las grÃ¡ficas quedan a discreciÃ³n del grupo; no obstante, deben ser realizadas variando el tamaÃ±o de las cadenas enviadas, la probabilidad de error, el algoritmo utilizado y el overhead (cantidad de informaciÃ³n extra que debe ser enviada como redundancia para que el algoritmo sea efectivo).

Algunas preguntas que pueden ayudar a la discusiÃ³n son:

- Â¿QuÃ© algoritmo tuvo un mejor funcionamiento?
- Â¿QuÃ© algoritmo es mÃ¡s flexible para aceptar mayores tasas de errores?
- Â¿CuÃ¡ndo es mejor utilizar un algoritmo de detecciÃ³n errores en lugar de uno de correcciÃ³n de errores?

### Reporte

Al finalizar el laboratorio debe realizarse un reporte grupal donde se incluyan las siguientes secciones:

1. Nombres y carnÃ©s
2. TÃ­tulo de la prÃ¡ctica
3. DescripciÃ³n de la prÃ¡ctica
4. Resultados
5. DiscusiÃ³n
6. Comentario grupal sobre el tema
7. Conclusiones
8. Citas y Referencias

### Rubrica

- ImplementaciÃ³n de la arquitectura: 20%
- ImplementaciÃ³n de algoritmo de detecciÃ³n, y comunicaciÃ³n con receptor: 30%
- Reporte: 50%
  - Formato: 5%
  - Pruebas: 15%
  - DiscusiÃ³n: 20%
  - Conclusiones: 10%