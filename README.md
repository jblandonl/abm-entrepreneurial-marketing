# Article 4 · Primer modelo en Python · v0.1.0

**Piloto exploratorio para estudiantes y coautores.** Los datos son sintéticos y los parámetros de comportamiento no están calibrados con observaciones de empresas. El propósito es examinar las reglas, aprender a analizar las salidas y orientar la siguiente versión del artículo.

## Qué se entregó

- Un modelo basado en agentes ejecutable en Python, sin NetLogo.
- Cuatro estrategias con el mismo presupuesto de 40 horas mensuales.
- 500 personas, cinco comunidades, 50 contactos iniciales y 60 meses por corrida.
- 30 semillas comunes por estrategia (1001–1030): **120 corridas**. La unidad de comparación es la corrida completa, no cada mes ni cada persona.
- **7.200 registros mensuales, 33.014 eventos de compra y 60.000 registros finales de agentes.**
- Dos figuras, resúmenes, diferencias pareadas, sensibilidad de clasificación y trazas de una semilla elegida antes de observar resultados.
- 15 pruebas automatizadas aprobadas y controles de integridad de las exportaciones.

## Primeros resultados para discutir

Medias de las 30 corridas por estrategia. Las proporciones son medias de proporciones por corrida, no una proporción agregada entre todas las personas.

| Estrategia | Ventas meses 1–12 | Clientes únicos al mes 60 | Clientes externos | Adquisición autónoma acumulada | Corridas con autonomía |
|---|---:|---:|---:|---:|---:|
| A · Contactos personales | 49,8 | 48,2 | 29,9% | 14,2% | 0/30 |
| B · Exploración externa | 32,9 | 105,1 | 84,8% | 5,9% | 0/30 |
| C · Referidos | 44,0 | 121,0 | 75,9% | 7,0% | 0/30 |
| D · Equilibrada | 40,1 | 122,0 | 78,3% | 6,9% | 0/30 |

Con estas reglas, A favorece las ventas iniciales; C y D incorporan más clientes durante los 60 meses. La expansión externa de B no equivale a autonomía. **Ninguna de las 120 corridas reúne simultáneamente los cinco criterios durante seis meses.** No se ajustaron los parámetros para obtener autonomía. La cifra no demuestra que la autonomía sea imposible en empresas reales ni bajo otras reglas.

La dependencia sobre ventas es mucho menor que la dependencia sobre primeras adquisiciones, porque las recompras se modelan como autoservicio. Para la comparación central, examine ambas y el número absoluto de adquisiciones autónomas. Una proporción alta con pocos clientes puede ser engañosa.

## Cómo empezar sin programar

1. Lea `METODOLOGIA.md` y `GUIA_ESTUDIANTES.md`.
2. Abra `results/simulation_summary.csv`: una fila por corrida.
3. Abra `results/system_month.csv` para estudiar trayectorias. Filtre una estrategia y una semilla antes de interpretar una historia individual.
4. Consulte `DICCIONARIO_DATOS.md` para las unidades y denominadores.
5. Compare sus cálculos con `results/analysis/strategy_means.csv` y las figuras.

Los CSV usan UTF-8 con BOM, separador coma y punto decimal. En Excel: **Datos → Desde texto/CSV**, seleccione UTF-8, coma y una configuración regional compatible con punto decimal cuando sea necesario. Las celdas vacías en proporciones representan un denominador cero; no deben sustituirse por cero.

## Cómo reproducir

Se verificó en Python 3.12.14. Abra una terminal en esta carpeta. Instale las dependencias en su propio entorno:

```bash
python -m pip install -r requirements.txt
python -m unittest -v
python run_pilot.py --repetitions 30 --seed-start 1001 --config config.json --output results_reproduced
python analyze.py --input results_reproduced
```

El simulador rechaza una carpeta de resultados no vacía para proteger los datos originales. `analyze.py` puede regenerar los derivados dentro de `analysis`; no modifica los CSV originales. Los tiempos de ejecución y metadatos del entorno pueden variar; los eventos y resultados numéricos deben coincidir usando estas versiones y configuración.

Para otro experimento, copie `config.json`, cambie un supuesto explícito y use otra carpeta de salida. Conserve las mismas semillas para comparaciones pareadas. Para una fase principal, la guía pide al menos 100 repeticiones por condición: aumentar el número no resuelve por sí solo los supuestos pendientes.

## Archivos

`model.py`: agentes, acciones, probabilidades, vínculos y métricas.

`run_pilot.py`: semillas, corridas y exportación. `analyze.py`: controles, resúmenes y figuras. `test_model.py`: pruebas de verificación. `config.json`: valores utilizados. `PARAMETROS.csv`: significado y procedencia de cada valor.

`results/analysis/01_pilot_overview.png`: comparación de trayectorias. Bandas = percentiles 10–90 entre corridas; no son intervalos de confianza.

`results/analysis/02_network_example.png`: estrategia D, semilla 1001, meses 0, 12 y 60. La semilla está fijada por el protocolo de exportación, no seleccionada por su desempeño. El color identifica la comunidad de los clientes; el contorno distingue contactos iniciales. Se conservan posiciones y red social.

`MANIFEST_SHA256.json` permite comprobar la integridad de los archivos del paquete.

## Alcance y siguiente decisión

Este prototipo fija la red social entre personas, mientras permite cambiar los vínculos directos del fundador y los vínculos comerciales de recomendación. Necesidad, afinidad y satisfacción posterior a la primera compra permanecen fijas. No incluye competencia, precios monetarios, incentivos ni entrada de nuevas personas.

El próximo paso es revisar los mecanismos y la clasificación con los estudiantes, especialmente la atribución conservadora de intervención del fundador, el desgaste de recomendaciones y la regla de seis meses. Después se diseña sensibilidad de comportamiento y se justifica cada parámetro con literatura o datos. No se recomienda insertar estas cifras como resultados finales del artículo.

## Fuentes de diseño

- [Guía del proyecto](https://docs.google.com/document/d/11UxkXIbxcsgFnO_7ICTCaXNBEnkAElqh6-KLBuvu7Go/edit).
- [Diseño conceptual v0.1](https://docs.google.com/document/d/16M0ybs3bzmS4vpmDCRkgOuWzcd2-ByEgwONUp3Rghlo/edit).
- [Ruta de trabajo](https://docs.google.com/document/d/1JunzmhnlFRZS22eCFna52Rtn4Mg6-Y_uj7c0MliE0is/edit).

Son fuentes de especificación del proyecto. No se atribuyen a ellas evidencias empíricas para los parámetros añadidos en este prototipo.
