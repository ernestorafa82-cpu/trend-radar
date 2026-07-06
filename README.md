# Content Trend Radar

**Motor script-first para descubrir ideas diarias de contenido** a partir de señales de tecnología, negocio y cultura digital.

**Ideal para:** creadores faceless, comunidades, infoproductores y operadores de contenido.
**No es:** una plataforma SaaS completa ni un lector genérico de RSS.

Content Trend Radar convierte ruido informativo en un **Top 10 diario de temas con potencial de contenido**.

Está pensado para detectar antes:
- temas que generan curiosidad
- lanzamientos, giros y movimientos fáciles de explicar
- ideas que se puedan convertir en hook, reel, carrusel o post
- señales que ahorran horas de búsqueda manual

Cada ejecución genera un **Top 10 diario** con recomendación clara:

- **POST**
- **DRAFT**
- **WATCH**

No es un lector genérico de RSS.

Es una capa ligera de descubrimiento diario diseñada para priorizar **potencial de contenido sobre volumen**, reducir ruido y producir salidas listas para usar.

---

## Qué hace este producto

Content Trend Radar recopila señales públicas, elimina ruido, agrupa historias repetidas y genera un **brief diario corto, priorizado y orientado a creación de contenido**.

En cada ejecución produce un radar listo para consumo operativo con:

- un brief en Markdown legible por humanos
- un JSON estructurado para reutilización o automatización
- un artefacto listo para Telegram o Skool
- un post listo para comunidad en `latest.skool.md`
- una hoja de trabajo para desarrollar piezas en `latest.workbench.md`
- una salida `latest.*` para acceso diario inmediato

Su función no es acumular noticias, sino **convertir información dispersa en una lista diaria de temas que merecen convertirse en contenido**.

---

## Por qué es útil

Este activo aporta valor porque reduce una tarea costosa y repetitiva: **buscar cada mañana ideas con potencial real para publicar**.

Para el operador, eso se traduce en:

- menos tiempo invertido en escaneo manual de fuentes
- más claridad sobre qué tema merece convertirse en contenido hoy
- una rutina diaria simple para alimentar reels, shorts, carruseles o posts
- una base reutilizable para comunidades, creadores faceless o asistentes de contenido
- un sistema ligero que puede usarse tal cual o integrarse en un flujo mayor

No reemplaza criterio editorial.
Lo acelera, lo estructura y lo hace más repetible.

---

## Usuario ideal

El usuario más claro para este activo es alguien que necesita una **capa diaria de ideas frescas para contenido** sin montar un sistema pesado desde cero.

Encaja especialmente bien con:

- creadores faceless que necesitan temas diarios
- comunidades como Skool que quieren un Top 10 listo para publicar
- operadores de contenido que convierten tendencias en hooks y guiones
- asistentes o equipos pequeños que necesitan ideas nuevas sin perder horas buscando

Es menos adecuado para quien busque:
- una plataforma SaaS completa con interfaz avanzada
- cobertura exhaustiva de todo el mercado
- sustitución total del criterio humano

Su mejor encaje es como **motor operativo ligero** para detectar antes qué tema merece publicarse, prepararse o vigilarse.

---

## Estado actual del producto

Este repositorio representa hoy un **motor funcional y operable**, basado en scripts, listo para producir un ranking diario de ideas, pero **no** una aplicación SaaS completa.

Su estado actual es:

- pipeline en Python con ejecución diaria
- operación simple en local o por cron
- outputs generados en `out/` tras cada ejecución
- salidas en Markdown, JSON y formato Telegram
- export específico para Skool y workbench de creador
- sin interfaz web alineada todavía con este producto
- estructura ligera y relativamente fácil de entender

Esto lo posiciona mejor como:

- motor operativo para uso interno
- herramienta ligera para descubrir temas diarios
- capa diaria de señal para creadores, comunidades o equipos pequeños
- sistema base sobre el que se puede montar una experiencia más guiada
- base funcional sobre la que otro operador puede continuar o ampliar

En otras palabras: hoy es más fuerte como **motor de descubrimiento de ideas** que como producto terminado para usuarios no técnicos.

---

## Diferenciales principales

### 1) Prioriza señal sobre ruido
No intenta mostrar “todo”.
Su valor está en reducir volumen y destacar lo que merece atención real.

### 2) Agrupa historias repetidas
Cuando varias fuentes apuntan al mismo evento o tendencia, el sistema puede agruparlas y reforzar la señal con evidencia adicional.

### 3) Reduce riesgo de alucinación
El modelo no debería inventar títulos ni enlaces: el análisis se apoya en IDs reales de input y luego reconstruye títulos, URLs y fuentes desde los datos originales.

### 4) Entrega una salida orientada a publicación
No se limita a listar noticias.
Produce un radar diario corto con recomendación explícita: **POST / DRAFT / WATCH**, además de hook, hooks alternativos, formato sugerido, talking points y CTA.

### 5) Es ligero de operar y transferir
Funciona como una pipeline simple que genera artefactos a disco, lo que facilita entenderlo, ejecutarlo, revisarlo y entregarlo a un comprador.

---

## Fuentes cubiertas actualmente

El activo trabaja sobre una combinación de fuentes públicas orientadas a detectar señal en tecnología, mercado, research y startups.

Actualmente se apoya en categorías como:

### Medios de mercado y tecnología
- Hacker News
- TechCrunch
- The Verge
- FT Tech

### Agregación temática vía RSS
- Tech
- Finance
- Cyber
- Health

### Research
- arXiv AI
- arXiv CS

### Descubrimiento de startups
- Product Hunt

Esto permite combinar cobertura generalista, señal técnica, research temprano y descubrimiento de producto en un único radar diario orientado a contenido.

---

## Cómo funciona

A alto nivel, el sistema sigue un flujo simple y entendible:

1. recopila items desde fuentes públicas
2. elimina duplicados y ruido evidente
3. aplica filtros para priorizar temas con potencial de hook
4. agrupa historias repetidas o relacionadas
5. clasifica y puntúa los items con ayuda de LLM pensando en utilidad para contenido
6. reconstruye títulos, enlaces y fuentes desde el input original
7. genera salidas finales en `out/`
8. prepara un post publicable y una hoja de trabajo para convertir temas en piezas

El resultado es un radar diario corto, más consistente y más fácil de revisar que un flujo manual de lectura dispersa.

---

## Demo rápida

### 1) Ejecutar el radar

```bash
./run_daily.sh
```

### 2) Ver el último brief generado

```bash
cat out/latest.md
```

### 3) Ver la salida estructurada

```bash
cat out/latest.json
```

### 4) Ver el post listo para comunidad

```bash
cat out/latest.skool.md
```

### 5) Ver la hoja de trabajo para crear contenido

```bash
cat out/latest.workbench.md
```

### 6) Revisar el log de ejecución

```bash
tail -n 50 out/cron.log
```
