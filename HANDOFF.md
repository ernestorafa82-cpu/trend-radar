# HANDOFF — Content Trend Radar

## Qué es este activo
Content Trend Radar es un motor Python script-first que genera un brief diario con temas filtrados y priorizados para contenido en formato Markdown y JSON.

## Qué recibe el comprador
- código fuente del proyecto
- README inicial buyer-facing
- `.env.example`
- `requirements.txt`
- `setup.sh`
- `demo.sh`
- `sanity_check.sh`
- `run_daily.sh`
- generación de salida en `out/latest.md` y `out/latest.json`

## Flujo mínimo de uso
1. crear entorno con `./setup.sh`
2. copiar `.env.example` a `.env`
3. configurar `OPENAI_API_KEY`
4. ejecutar `./demo.sh`
5. validar con `./sanity_check.sh`

## Output del producto
- `out/latest.md`: brief diario legible para humano
- `out/latest.json`: salida estructurada para automatización o integración
- `out/latest.skool.md`: post listo para comunidad
- `out/latest.workbench.md`: hoja de trabajo para convertir temas en piezas
- `out/radar_YYYY-MM-DD.md|json`: histórico diario
- `out/cron.log`: log operativo

## Dependencias externas
- Python 3
- cuenta y API key de OpenAI
- conectividad a internet para consultar fuentes

## Qué está ya resuelto
- generación diaria demoable
- formato de reporte orientado a ideas de contenido
- instalación mínima reproducible
- wrapper de demo reproducible
- sanity check básico
- cron operativo vía `run_daily.sh`

## Límites actuales del activo
- depende de cuota/billing de OpenAI
- es un motor script-first, no una app SaaS multiusuario
- no incluye panel web, auth ni sistema de gestión de usuarios
- la calidad depende de fuentes externas y del modelo configurado
- requiere configuración manual inicial de `.env`

## Riesgos a explicitar al comprador
- cambios en APIs o fuentes externas
- coste variable por uso del modelo
- necesidad de mantener clave API y cron del entorno
- posible ruido o drift en algunas señales si cambian las fuentes

## Qué debe transferirse también
- acceso al repositorio
- acceso al entorno donde se ejecute el cron, si aplica
- ownership operativo de la API key y billing
- criterio editorial/comercial de uso del radar, si se vende como activo con posicionamiento

## Estado actual
Motor funcional, demoable y transferible a nivel técnico básico.
No está empaquetado como producto SaaS completo; está pensado para uso operativo interno o distribución del Top 10 ya generado.
