# Especificación del prototipo v0.1

Documento técnico de trabajo, organizado como una descripción ODD abreviada. No reemplaza el protocolo que acompañará la versión final. Las decisiones nuevas son supuestos de simulación revisables.

## Propósito, entidades y escalas

Comparar cuatro asignaciones de tiempo y observar ventas, expansión externa y dependencia comercial del fundador. Hay una empresa con capacidad de servicio, un fundador y 500 personas repartidas en cinco comunidades. Un periodo representa un mes; el horizonte es 60 meses. La comparación usa 30 semillas, compartidas entre las cuatro estrategias. Ningún cliente existe en el mes cero.

Cada persona tiene comunidad, necesidad, afinidad con el producto, pertenencia a la red personal inicial, historial de contactos, origen de la primera oportunidad, indicador acumulado de contacto comercial del fundador, compras, satisfacción y energía de recomendación. Los estados son derivados: no contactado, prospecto contactado, cliente activo/inactivo y promotor satisfecho. No se implementa una máquina explícita con los siete estados sugeridos en la guía.

## Inicialización y redes

Se genera una red social modular no dirigida: probabilidad de vínculo 0,06 dentro de la comunidad y 0,004 entre comunidades. Se agrega un anillo dentro de cada comunidad para garantizar su conectividad interna. No se fuerza la conectividad global. La fuerza de cada relación social se distribuye uniformemente entre 0,4 y 0,9. Esta red y sus fuerzas permanecen fijas en v0.1.

Se eligen 50 contactos iniciales entre las tres primeras comunidades; su condición inicial nunca cambia. Sus vínculos directos con el fundador comienzan con fuerza uniforme 0,6–0,9. Necesidad y afinidad se extraen independientemente de Beta(2,2), sin cambio temporal. Son elecciones exploratorias, no estimaciones.

Los vínculos fundador-persona son dinámicos. Los vínculos comerciales de referido son dirigidos del recomendador al prospecto y registran creación, refuerzo o desaparición. Comprar mediante WOM no crea automáticamente un vínculo social directo con el fundador.

## Asignación y selección

| Estrategia | Venta | Mantenimiento | Referidos | Exploración |
|---|---:|---:|---:|---:|
| A | 70% | 20% | 5% | 5% |
| B | 20% | 10% | 10% | 60% |
| C | 35% | 15% | 40% | 10% |
| D | 30% | 20% | 30% | 20% |

El presupuesto es 40 horas. Una venta/contacto ocupa 1 h, mantenimiento 0,5 h, solicitud de referido 1 h y exploración 2 h. Se usan acciones enteras redondeando hacia abajo; las horas sobrantes y sin destinatarios no se reasignan. Se registra tiempo asignado, usado y no usado. Una exploración o solicitud fallida consume tiempo.

En A, la venta directa apunta exclusivamente a contactos iniciales todavía no compradores. En B–D apunta a cualquier vínculo actual del fundador todavía no comprador. Se contacta como máximo una vez por acción/canal en el mes, aunque varios canales pueden llegar a la misma persona. La venta directa no solicita recompras.

Mantenimiento selecciona los vínculos directos más débiles, con desempate aleatorio, y los refuerza en 0,15. Si el destinatario es un promotor activo, aumenta su energía en 0,08. Una interacción comercial directa refuerza el vínculo en 0,08.

Exploración selecciona no compradores sin vínculo directo activo; forma un vínculo con probabilidad 0,65 y confianza inicial 0,25. Puede reconectar un contacto perdido. La clasificación inicial de la persona se mantiene.

Solicitar un referido exige un cliente activo, satisfecho y con vínculo directo al fundador. La probabilidad de recomendación es 0,75 × satisfacción × energía. Se selecciona uniformemente un vecino social que no haya comprado; si no hay candidatos, se pierde esa oportunidad. La introducción crea o refuerza un vínculo directo fundador-prospecto.

El WOM espontáneo usa un proceso separado: probabilidad mensual 0,30 × satisfacción × energía por promotor, con un máximo de un destinatario social no comprador. No requiere tiempo ni vínculo directo del fundador. Una solicitud a otro prospecto no convierte retrospectivamente este canal en solicitado: los episodios se identifican por destinatario. Esta separación entre procesos es un supuesto que debe discutirse.

La confianza del referido (solicitado o espontáneo) es 0,25 + 0,30 × fuerza del vínculo social recomendador-prospecto, acotada a [0,1]. El parámetro 0,30 debe incluir cero en futuros experimentos de sensibilidad.

## Probabilidad de primera compra

Cada prospecto con al menos una exposición durante el mes tiene una sola evaluación de compra, independientemente del número de contactos. Se usa la mayor confianza entre exposiciones del mes:

```text
p = purchase_scale × necesidad × afinidad
    × (0.25 + 0.60 × confianza + 0.40 × influencia_social × fracción_vecinos_activos)
    × exp(−0.16 × contactos_recibidos_en_meses_anteriores)
    × max(0, 1 − 0.35 × influencia_social × fracción_vecinos_activos_insatisfechos)
```

El resultado se acota a [0,1]. La escala es 1 y la influencia social 0,5. Un prospecto sin exposición nueva no compra ese mes, aunque su origen e historial se conservan. La fatiga no se recupera en v0.1. Una repetición rechazada por capacidad tampoco se procesa automáticamente en el mes siguiente.

## Compras repetidas, capacidad y satisfacción

Las personas que ya compraron pueden recomprar mediante autoservicio con probabilidad 0,10 × necesidad × (0,4 + 0,6 × satisfacción). Se evalúan aun si están inactivas, por lo que una recompra puede reactivarlas. No se permite primera compra y recompra en el mismo mes. Todas las solicitudes de compra compiten por 30 plazas mensuales, con prioridad aleatoria común a nivel persona-mes.

La satisfacción inicial es 0,65 × calidad + 0,35 × afinidad + ruido Normal(0; 0,10) − penalización por congestión; se acota a [0,1]. La calidad es 0,85. La penalización es 0,10 × fracción de solicitudes no atendidas. En el piloto la capacidad no llegó a limitar ventas; sí se comprobó esa restricción con pruebas extremas.

Un promotor es un cliente activo con satisfacción ≥0,72 y energía positiva. La energía comienza en 1 para estos clientes, pierde 0,08 por mes y puede recuperarse con mantenimiento o recompra (+0,25). Se acota a [0,1]. La satisfacción permanece fija después de la primera compra. Un cliente está activo si su última compra ocurrió hace menos de nueve meses. Una satisfacción <0,45 activa la contribución negativa del WOM en vecinos.

## Atribución y dependencia

Se registra por separado red inicial, origen de oportunidad e intervención del fundador. El origen corresponde a la primera exposición registrada; entre exposiciones en un mismo mes el desempate es aleatorio. No se redefine al comprar más tarde. El indicador de intervención conserva cualquier contacto directo, exploración exitosa o referido solicitado anterior a la primera compra.

**La atribución es deliberadamente conservadora:** el episodio abarca desde el primer contacto hasta la primera compra, sin caducidad del contacto del fundador. Si primero hubo contacto del fundador y después una recomendación espontánea, la adquisición sigue siendo dependiente. El estudiante debe examinar alternativas con una ventana temporal explícita; no se presenta esta regla como una estimación causal empírica.

Una primera compra es autónoma si su origen es WOM espontáneo y nunca hubo intervención comercial del fundador antes de comprar. Las recompras no cuentan como adquisiciones autónomas. La dependencia sobre ventas incluye primeras compras dependientes en el numerador y todas las transacciones en el denominador. La dependencia sobre adquisiciones usa solamente primeras compras en ambos términos; por construcción esta última complementa la proporción autónoma en v0.1.

## Orden mensual

1. Identificar clientes activos y promotores al inicio del mes.
2. Distribuir las horas; venta directa, mantenimiento, referidos solicitados y exploración.
3. Generar WOM espontáneo de los promotores existentes al inicio.
4. Agrupar exposiciones, conservar origen e intervención y evaluar una primera compra por prospecto.
5. Evaluar recompras, ordenar solicitudes y aplicar capacidad.
6. Registrar compras y satisfacción inicial. Los nuevos clientes recomiendan a partir del mes siguiente.
7. Debilitar vínculos sin interacción, actualizar energía, actividad e indicadores.
8. Evaluar autonomía y exportar.

Los vínculos directos y de referido sin interacción pierden 0,025 puntos por mes; se eliminan por debajo de 0,05. Los eventos históricos no se borran al desaparecer un vínculo. Las condiciones de actividad se evalúan al inicio para recomendar y al cierre para los indicadores.

## Autonomía y análisis

Durante seis meses consecutivos se exige: adquisición autónoma >50%; clientes acumulados externos >50%; aumento neto de clientes activos >0; dependencia sobre ventas <50%; y clientes activos en al menos tres comunidades. Con cero en el denominador, la proporción queda no definida y el mes no cumple. La confirmación ocurre en el sexto mes; si una condición falla se pierde la clasificación vigente. Las corridas sin confirmación se censuran al horizonte.

`autonomy_thresholds.csv` cambia un umbral porcentual a la vez (0,4/0,5/0,6), manteniendo los restantes en 0,5. Mayor umbral de autonomía/externalidad es más exigente; mayor umbral de dependencia máxima es menos exigente. Esto reanaliza los mismos datos; no constituye sensibilidad de comportamiento ni nuevas simulaciones.

Se informan media, mediana, desviación estándar y percentiles 5 y 95 por estrategia. Las gráficas usan percentiles 10–90. Las diferencias B–A, C–A y D–A se calculan por semilla; los intervalos percentiles de bootstrap (2.000 remuestreos de pares) describen incertidumbre de Monte Carlo bajo estas reglas, no incertidumbre sobre empresas reales. No se tratan 7.200 meses como 7.200 réplicas independientes.

## Reproducibilidad y validación pendiente

Las semillas comparten red inicial, atributos y números aleatorios por persona-mes en compra, recompra, capacidad y satisfacción. Las selecciones de destinatarios dependen de conjuntos que cambian entre estrategias; compartir semillas no significa trayectorias idénticas. Las huellas de inicialización se exportan para comprobar el emparejamiento. La semilla 1001 registra trazas detalladas; los demás casos conservan resumen, periodos, todas las compras y estado final de cada agente.

Las pruebas verifican implementación y coherencia. **No hay calibración ni validación empírica.** Quedan pendientes revisión de expertos/estudiantes, contraste bibliográfico, sensibilidad de comportamiento (incluida influencia social 0,2/0,5/0,8), posibles cambios en relaciones entre personas y justificación de todos los valores exploratorios. No se entrenó ni optimizó el modelo para reproducir un orden específico de estrategias.
