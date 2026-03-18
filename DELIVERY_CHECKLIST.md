# DELIVERY CHECKLIST — Trend-Radar / Market Wow Radar

## Estado del activo
- [ ] README buyer-facing revisado
- [ ] `HANDOFF.md` presente
- [ ] `OPERATIONS.md` presente
- [ ] `SALE_ASSETS.md` presente
- [ ] `.env.example` presente y limpio
- [ ] `.env` excluido del repo
- [ ] `requirements.txt` presente
- [ ] `setup.sh` validado
- [ ] `demo.sh` validado
- [ ] `sanity_check.sh` validado

## Repo y seguridad
- [ ] `.gitignore` protege `.env`, `.venv/` y `out/`
- [ ] no hay secretos reales en el repo
- [ ] no hay credenciales expuestas en documentación o logs compartidos
- [ ] el repo es entendible para un tercero

## Demo y operabilidad
- [ ] `./setup.sh` funciona
- [ ] `./demo.sh` genera `out/latest.md`
- [ ] `./demo.sh` genera `out/latest.json`
- [ ] `./sanity_check.sh` pasa
- [ ] `run_daily.sh` está documentado
- [ ] cron documentado en `OPERATIONS.md`

## Transferencia
- [ ] está claro qué se incluye en la venta
- [ ] está claro qué no se incluye en la venta
- [ ] dependencias externas explicadas
- [ ] límites del activo explicados
- [ ] riesgos operativos explicados
- [ ] buyer ideal claramente descrito

## Cierre comercial
- [ ] propuesta de valor entendible en menos de 10 segundos
- [ ] activo posicionable como asset transferible
- [ ] narrativa comercial consistente con el estado real del producto
- [ ] no se vende como SaaS completo si no lo es

## Antes de entregar
- [ ] revisar outputs recientes en `out/`
- [ ] decidir si el histórico de `out/` se incluye o no
- [ ] decidir si se entrega por repo completo o export
- [ ] definir precio, perímetro y soporte post-venta
