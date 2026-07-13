# Implementation Plans

Generated initially by the improve skill on 2026-07-10 and reconciled on
2026-07-12. Execute in the order below unless dependencies say otherwise. Each
executor: read the plan fully before starting, honor its STOP conditions, and
update your row when done.

## Execution order & status

| Plan | Title | Priority | Effort | Depends on | Status |
|------|-------|----------|--------|------------|--------|
| 001  | Consolidar el flujo util textual end-to-end | P1 | L | - | DONE |
| 002  | Saneamiento de rumbo y frontera portable de publicacion | P1 | M | 001 | DONE |
| 003  | Salida externa dry-run sin proveedor real | P1 | M | 002 | DONE |
| 004  | La generacion textual util se activa mediante un adaptador controlado | P1 | M | 003 | DONE |
| 005  | Prueba de valor del flujo textual local con entrada realista | P1 | S | 004 | DONE |
| 006  | Integracion IA real controlada detrás de ModelAdapter | P1 | M | 005 | DONE |
| 007  | Validacion real del producto textual | P1 | M | 006 | IMPLEMENTED_PRODUCT_GATE_NOT_MET |
| 008  | Recuperacion del producto completo y roadmap por incrementos | P1 | L | 006, 007 | TODO |

Status values: TODO | IN PROGRESS | DONE | IMPLEMENTED_PENDING_REAL_SMOKE | IMPLEMENTED_PRODUCT_GATE_NOT_MET | BLOCKED (with one-line reason) | REJECTED (with one-line rationale - finding fixed independently or approach abandoned)

## Dependency notes

- `001` no depende de otro plan, pero debe ejecutarse sin abrir frentes paralelos sobre audio, publicacion real o pipeline de contexto.
- `002` depende de `001` porque primero habia que cerrar el flujo textual offline/mock antes de fijar la frontera portable de publicacion.
- `003` depende de `002` porque la salida externa dry-run necesita la frontera portable ya declarada y el rumbo saneado.
- `004` depende de `003` porque la generacion textual debe evolucionar sin romper la frontera de publicacion ya establecida ni reintroducir acoplamiento real.
- `005` depende de `004` porque la prueba de valor necesita el adapter controlado ya estabilizado.
- `006` depende de `005` porque la integración real solo tiene sentido después de validar que el flujo local útil ya aporta valor suficiente. Se cerró con la evidencia real de Plan 007; su smoke legacy con aprobación anticipada quedó obsoleto.
- `007` depende de `006` porque la validación real del producto textual solo tiene sentido cuando la ruta real ya existe detrás de `ModelAdapter`. La implementación y evidencia técnica están completas, pero el gate editorial no se alcanzó.
- `008` usa los resultados de `006` y `007` para recuperar el producto completo por incrementos visibles, sin tratar las restricciones temporales de esos planes como límites permanentes.

## Decisiones históricas y vigencia

Las entradas siguientes documentan decisiones de los planes 001-007. No son
prohibiciones permanentes del producto: audio, visuales, publicación y analítica
siguen siendo capacidades previstas y se reevalúan por el roadmap de Plan 008.

- Audio o transcripción en las fases iniciales: diferidos hasta estabilizar el primer flujo, no descartados.
- Publicación real o `dry_run` externo en las fases iniciales: diferidos por seguridad y aprobación humana, no descartados.
