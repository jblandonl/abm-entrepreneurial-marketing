# Diccionario de datos

Todos los datos son sintéticos. Una semilla identifica una réplica compartida por A–D. En CSV, vacío indica no definido/no aplicable; no equivale a cero.

## Archivos originales

| Archivo | Unidad de fila y cobertura |
|---|---|
| simulation_summary.csv | Corrida completa; 120 filas. |
| system_month.csv | Corrida-mes; 7.200 filas. |
| purchase_events.csv | Transacción, primera compra o recompra; 33.014 filas. |
| agents_final.csv | Corrida-persona al final; 60.000 filas. |
| nodes_trace.csv | Semilla 1001, estrategia-persona en meses 0, 12, 30 y 60. |
| social_edges_trace.csv | Red social fija de semilla 1001, común a las cuatro estrategias. |
| referral_edges_trace.csv | Vínculos de referido activos en las instantáneas, semilla 1001. |
| link_events_trace.csv | Creación/refuerzo/eliminación de vínculos, solo semilla 1001. |
| exposures_trace.csv | Exposición a un prospecto, solo semilla 1001; varias filas pueden compartir probabilidad de compra. |

## Campos compartidos y específicos

| Campo | Definición |
|---|---|
| active | Actividad en la instantánea. |
| active_customers | Compradores con menos de active_months meses desde su última compra. |
| active_customers_final | Clientes activos al cierre del horizonte. |
| active_final | 1 si está activo al cierre. |
| active_promoters | Clientes activos satisfechos con energía positiva al cierre. |
| active_referral_links | Número de vínculos comerciales de referido con fuerza al menos igual al umbral de conservación. |
| autonomous | 1 exclusivamente en primeras adquisiciones autónomas; 0 en recompras. |
| autonomous_acquisition | Clasificación de la primera adquisición en el registro final. |
| autonomous_acquisition_share | Primeras adquisiciones autónomas acumuladas / unique_customers. |
| autonomous_new | Primeras compras del mes con origen WOM espontáneo y sin contacto comercial previo del fundador. |
| autonomous_share | autonomous_new / new_customers; vacío si no hay nuevos clientes. |
| autonomy_active | 1 si la racha vigente alcanza al menos seis meses. |
| autonomy_censored | 1 si no hubo confirmación antes de terminar la observación. |
| autonomy_criteria_met | 1 si se cumplen los cinco criterios ese mes, sin exigir todavía la racha de seis. |
| autonomy_ever | 1 si alguna vez se completó la racha exigida. |
| autonomy_final | Clasificación de autonomía al cierre. |
| autonomy_first_month | Mes de primera confirmación; vacío si nunca ocurre. |
| autonomy_observation_month | Mes de confirmación o mes final en una corrida censurada. |
| autonomy_periods | Número de meses con autonomía confirmada y vigente; no longitud de una sola racha. |
| autonomy_streak | Meses consecutivos que cumplen los cinco criterios; se reinicia en cero ante un fallo. |
| bridging | 1 si el recomendador de origen y el cliente pertenecen a comunidades distintas; 0 si no aplica. |
| bridging_acquisition | Clasificación entre comunidades de la adquisición inicial. |
| bridging_new | Primeras compras cuyo recomendador de origen pertenece a otra comunidad. |
| channel | Canal de la exposición específica; puede diferir del origen histórico. |
| communities_final | Comunidades con clientes activos al cierre. |
| communities_reached | Número de comunidades con al menos un cliente activo en ese mes. |
| community | Comunidad 0–4 de la persona. |
| community_diversity | Entropía normalizada de clientes activos entre comunidades; [0,1], cero si no hay activos. |
| contacts_received | Exposiciones recibidas antes de comprar; puede haber varios canales en un mes. |
| cumulative_autonomous | Total acumulado de primeras adquisiciones autónomas. |
| cumulative_customers | Personas que han comprado alguna vez hasta el mes; stock. |
| cumulative_sales | Transacciones acumuladas hasta el mes; stock, no sumar entre meses. |
| customer | 1 si ha comprado alguna vez en la instantánea. |
| customer_origin_share | (requested_origin_new + wom_origin_new)/new_customers; no equivale a autonomía. |
| direct_origin_new | Primeras compras del mes cuyo origen histórico es venta directa. |
| diversity_final | Entropía normalizada de clientes activos al cierre. |
| early_sales | Transacciones de meses 1–12, incluidas recompras. |
| energy | Energía de recomendación actual en [0,1]. |
| event | created, reinforced o removed; el registro no incluye cada decremento de fuerza. |
| ever_customer | 1 si ha realizado alguna compra al cierre. |
| exploration_origin_new | Primeras compras del mes cuyo origen histórico es exploración. |
| external | 1 si la persona estaba fuera de la red personal inicial. |
| external_customers | Compradores únicos acumulados fuera de la red personal inicial. |
| external_share | external_customers / cumulative_customers; vacío si no hay clientes. |
| external_share_final | Proporción externa de compradores únicos acumulados al cierre. |
| first_purchase_month | Mes de primera compra; vacío si nunca compra. |
| fit | Afinidad individual fija en [0,1]. |
| founder_acquisition_share | Mensual: founder_new/new_customers. Resumen: total founder_new/clientes únicos. |
| founder_at_acquisition | Intervención histórica al momento de la primera compra; consultar ever_customer para no compradores. |
| founder_contact_ever | Hubo contacto comercial del fundador antes de comprar o mientras sigue siendo prospecto. |
| founder_degree | Personas con vínculo directo activo al fundador, compradoras o no. |
| founder_degree_final | Número de vínculos directos activos al cierre. |
| founder_involved | Intervención comercial previa a primera compra; 0 en recompras de autoservicio. |
| founder_involved_ever | Indicador acumulado de intervención comercial al procesar las exposiciones de ese mes. |
| founder_new | Primeras compras con alguna intervención comercial del fundador previa a adquirir. |
| founder_sales_share | Mensual: founder_new/sales. Resumen: total founder_new/total_sales; incluye recompras en denominador. |
| founder_strength | Fuerza del vínculo directo en la instantánea. |
| founder_tie_strength | Fuerza del vínculo directo al cierre; cero si inactivo. |
| graph_fingerprint | Huella de red y atributos iniciales; debe coincidir entre estrategias de la misma semilla. |
| hours_budget | Horas disponibles del mes (40 en el piloto, 0 tras interrupción opcional). |
| hours_explore | Horas utilizadas en intentos de exploración. |
| hours_maintain | Horas utilizadas en mantenimiento. |
| hours_refer | Horas utilizadas en solicitudes de referido. |
| hours_sell | Horas utilizadas en venta directa. |
| hours_unused | Presupuesto menos horas utilizadas; no se reasigna. |
| hours_used | Horas realmente utilizadas; en resumen suma de todos los meses. |
| initial_network | 1 si era contacto personal inicial; etiqueta inmutable. |
| initial_saturation | Contactos iniciales expuestos alguna vez por cualquier canal / contactos iniciales. No mide compradores. |
| last_purchase_month | Mes más reciente de compra; vacío si nunca compra. |
| layer | founder (vínculo directo) o referral (vínculo comercial dirigido). |
| mean_founder_tie_strength | Promedio de fuerza de vínculos directos activos; cero si no existen. |
| mechanism | Mecanismo que creó/reforzó/eliminó el vínculo. |
| month | Mes de simulación (1–60); las instantáneas incluyen mes 0. |
| need | Necesidad individual fija en [0,1]. |
| net_active_growth | Clientes activos al cierre menos los activos al cierre del mes anterior. |
| new_customers | Número de primeras compras durante el mes. |
| origin | Canal de la primera exposición; permanece fijo. repurchase para transacciones repetidas; none si sin exposición. |
| origin_month | Mes de la primera exposición, no necesariamente el mes de compra; 0 en eventos de recompra. |
| person_id | Identificador de persona 0–499, estable dentro de la semilla. |
| purchase_probability | Probabilidad única de primera compra del prospecto-mes, repetida en todas sus exposiciones de ese mes. |
| purchase_type | first: primera compra; repeat: recompra. |
| referrer | Identificador del recomendador de origen; −1 si no aplica. |
| repurchases | Número de compras de personas que ya compraron en meses anteriores. |
| requested_exposures | Introducciones efectivamente generadas por solicitudes durante el mes; no número de solicitudes. |
| requested_origin_new | Primeras compras del mes cuyo origen histórico es referido solicitado. |
| sales | Transacciones del mes: primeras compras + recompras. |
| satisfaction | Satisfacción fijada tras primera compra; vacío si no compra en agents_final, cero antes de compra en instantáneas. |
| seed | Semilla que identifica una réplica emparejada entre estrategias; no se suma. |
| source | Persona origen de vínculo; −1 identifica al fundador. |
| spontaneous_exposures | Exposiciones por WOM espontáneo del mes. |
| strategy | A contactos personales; B exploración; C referidos; D equilibrada. |
| strength | Fuerza del vínculo [0,1]. |
| target | Persona destinataria de vínculo. |
| total_sales | Transacciones de todos los meses. |
| trust | Confianza de esta exposición. |
| unique_customers | Número final de personas que compraron al menos una vez. |
| unmet_demand | Solicitudes de compra no atendidas por capacidad en el mes. |
| unmet_demand_total | Suma de solicitudes no atendidas por capacidad. |
| wom_origin_new | Primeras compras del mes cuyo origen histórico es WOM espontáneo; puede haber intervención posterior del fundador. |

## Análisis derivados

- `descriptive_statistics.csv`: estrategia, métrica, n válido, media, mediana, desviación estándar muestral, percentiles 5/95, mínimo y máximo.
- `strategy_means.csv`: medias por estrategia, con una fila por estrategia. Se promedian proporciones por corrida.
- `paired_differences.csv`: diferencias por semilla respecto de A, media de diferencias y límites 2,5%/97,5% de bootstrap de pares (2.000 remuestreos).
- `autonomy_thresholds.csv`: una corrida por variante de un umbral; `value` es el umbral modificado y los demás permanecen en 0,5. No son corridas nuevas.
- `plot_data.csv`: media, percentiles 10/90 y n válido de cada métrica por estrategia-mes. Las ventanas de 6 meses suman numeradores y denominadores dentro de cada corrida antes de calcular la proporción.

## Agregación correcta

Sume flujos (ventas, primeras compras, horas) cuando corresponda. Para stocks (clientes acumulados, vínculos, clientes activos) use el periodo pertinente; no sume meses. Una proporción acumulada se calcula con la suma de sus numeradores y denominadores dentro de la corrida, no con el promedio simple de proporciones mensuales. Para comparar estrategias, use las 30 corridas como réplicas.
