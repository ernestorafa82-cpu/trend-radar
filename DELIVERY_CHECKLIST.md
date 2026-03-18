# DELIVERY CHECKLIST — Trend-Radar / Market Wow Radar

## Estado del activo
- [x] README buyer-facing revisado
- [x] `HANDOFF.md` presente
- [x] `OPERATIONS.md` presente
- [x] `SALE_ASSETS.md` presente
- [x] `.env.example` presente y limpio
- [x] `.env` excluido del repo
- [x] `requirements.txt` presente
- [x] `setup.sh` validado
- [x] `demo.sh` validado
- [x] `sanity_check.sh` validado

## Repo y seguridad
- [x] `.gitignore` protege `.env`, `.venv/` y `out/`
- [x] no hay secretos reales en el repo
- [x] no hay credenciales expuestas en documentación o logs compartidos
- [x] el repo es entendible para un tercero

## Demo y operabilidad
- [x] `./setup.sh` funciona
- [x] `./demo.sh` genera `out/latest.md`
- [x] `./demo.sh` genera `out/latest.json`
- [x] `./sanity_check.sh` pasa
- [x] `run_daily.sh` está documentado
- [x] cron documentado en `OPERATIONS.md`

## Transferencia
- [x] está claro qué se incluye en la venta
- [x] está claro qué no se incluye en la venta
- [x] dependencias externas explicadas
- [x] límites del activo explicados
- [x] riesgos operativos explicados
- [x] buyer ideal claramente descrito

## Cierre comercial
- [x] propuesta de valor entendible en menos de 10 segundos
- [x] activo posicionable como asset transferible
- [x] narrativa comercial consistente con el estado real del producto
- [x] no se vende como SaaS completo si no lo es

## Antes de entregar
- [x] revisar outputs recientes en `out/`
- [x] decidir si el histórico de `out/` se incluye o no
- [x] decidir si se entrega por repo completo o export
- [x] definir precio, perímetro y soporte post-venta

## Decisión actual sobre outputs
- no incluir el histórico completo de `out/` por defecto en la venta base
- tratar el histórico como material opcional, solo si aporta valor en la negociación
- mantener el foco comercial en el asset y su operativa, no en ficheros históricos

## Decisión actual sobre modalidad de entrega
- entregar por repositorio GitHub como opción principal
- ofrecer export completo del repo en `.zip` solo si el comprador lo pide
- mantener commits, tag y trazabilidad como parte del valor del activo

## Decisión actual sobre oferta base
- ofrecer el activo con enfoque **asset + handoff corto** como opción comercial principal
- usar como rango orientativo de partida **2.500 € – 4.000 €**
- dejar el soporte post-venta fuera del precio base salvo pacto expreso
- ofrecer soporte limitado de transición solo como extra opcional

