# Verificación del piloto

15 pruebas de `test_model.py` ejecutadas y aprobadas antes del piloto.

- Aprobada: Reproducibilidad con igual configuración y semilla.
- Aprobada: Conservación de condiciones iniciales comunes.
- Aprobada: Cero actividad del fundador sin clientes iniciales.
- Aprobada: Red cerrada sin adquisición externa.
- Aprobada: Restricción de capacidad.
- Aprobada: Escala de compra nula.
- Aprobada: Presupuesto temporal y rangos de estado.
- Aprobada: Primera compra única y recompra posterior.
- Aprobada: Conciliación mensual con eventos.
- Aprobada: Procedencia de adquisiciones autónomas.
- Aprobada: Persistencia del origen ante conversión tardía.
- Aprobada: Mantenimiento y conservación de vínculos.
- Aprobada: Influencia social nula en probabilidad.
- Aprobada: Cociente no definido impide clasificar autonomía.
- Aprobada: Interrupción de actividad del fundador.

También se conciliaron las exportaciones con eventos y estados finales: 120 corridas, 7.200 meses, 33.014 compras y 60.000 registros finales. El archivo `results/analysis/export_verification.json` documenta esos controles.

Estas comprobaciones verifican implementación y contabilidad; no constituyen validación empírica ni demuestran que los supuestos representen todas las empresas.
