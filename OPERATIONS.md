# OPERATIONS — Trend-Radar / Market Wow Radar

## Objetivo operativo
Ejecutar el radar diario, verificar que genera salida válida y poder diagnosticar fallos básicos sin depender del autor original.

## Preparación inicial
1. ejecutar `./setup.sh`
2. copiar `.env.example` a `.env`
3. configurar `OPENAI_API_KEY`
4. opcionalmente ajustar:
   - `RADAR_MODEL`
   - `RADAR_TOP_N`
   - `RADAR_ALLOW_POLITICS`

## Ejecución manual
```bash
./demo.sh
```

## Ejecución diaria
```bash
./run_daily.sh
```

## Validación rápida
```bash
./sanity_check.sh
```
## Outputs esperados
- `out/latest.md`
- `out/latest.json`
- histórico en `out/radar_YYYY-MM-DD.md` y `out/radar_YYYY-MM-DD.json`
- log operativo en `out/cron.log`

## Cron actual
El proyecto está preparado para ejecutarse por cron usando `run_daily.sh`.

Ejemplo:
```cron
15 8 * * * ~/trend-radar/run_daily.sh
```
## Troubleshooting básico

### 1. `ERROR: falta .venv`
No se ha ejecutado `./setup.sh`.

### 2. `ERROR: falta .env`
Falta crear `.env` a partir de `.env.example`.

### 3. `OPENAI_API_KEY configured: False`
La clave no está cargada en `.env`.

### 4. `insufficient_quota`
La cuenta de OpenAI no tiene cuota o saldo suficiente.

### 5. `model_not_found`
`RADAR_MODEL` está vacío o mal configurado.

### 6. no se actualiza `out/latest.*`
Revisar `out/cron.log` para ver el último error real.

## Dependencias operativas externas
- Python 3
- acceso a internet
- cuenta OpenAI con billing activo
- entorno con cron, si se quiere automatización diaria

## Criterio operativo recomendado
- no versionar `.env`
- no compartir claves API
- revisar periódicamente `out/cron.log`
- tratar cambios de fuentes externas como riesgo operativo normal


