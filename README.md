# Market Wow Radar

**Asset script-first de market intelligence diaria** que convierte ruido informativo en un **brief Top 10 accionable**, listo para operar, demostrar y transferir.

**Ideal para:** founders, scouts, equipos de innovación y analistas.  
**No es:** una plataforma SaaS completa ni un lector genérico de RSS.

Market Wow Radar es un activo de inteligencia de mercado que convierte ruido informativo en un **brief diario accionable de alto valor**.

Está pensado para founders, scouts, equipos de innovación y analistas que necesitan detectar antes:
- tendencias con tracción
- cambios de mercado relevantes
- oportunidades accionables
- señales que merecen seguimiento real

Cada ejecución genera un **Top 10 diario** con recomendación clara:

- **ACT**
- **WATCH**
- **EXPLORE**

No es un lector genérico de RSS.  

Es una capa ligera de **market intelligence diaria**, diseñada para priorizar **señal sobre volumen**, reducir ruido y producir salidas fáciles de operar, demostrar y transferir.

---

## Qué hace este producto

Market Wow Radar recopila señales públicas de mercado, elimina ruido, agrupa historias repetidas y genera un **brief diario corto, priorizado y orientado a acción**.

En cada ejecución produce un radar listo para consumo operativo con:

- un brief en Markdown legible por humanos
- un JSON estructurado para reutilización o automatización
- un artefacto listo para Telegram
- una salida `latest.*` para acceso diario inmediato

Su función no es acumular noticias, sino **convertir información dispersa en una capa diaria de inteligencia útil para decidir qué merece atención, seguimiento o acción**.

---

## Por qué es útil

Este activo aporta valor porque reduce una tarea costosa y repetitiva: **convertir exceso de información en una lista diaria de señales que realmente merecen atención**.

Para el comprador, eso se traduce en:

- menos tiempo invertido en escaneo manual de fuentes
- más claridad sobre qué merece seguimiento o acción
- una rutina diaria de inteligencia de mercado fácil de operar
- una base reutilizable para scouting, research o ideación de producto
- un activo ligero que puede usarse tal cual o integrarse en un flujo mayor

No reemplaza criterio estratégico.  
Lo acelera, lo estructura y lo hace más repetible.

---

## Buyer ideal

El buyer más claro para este activo es alguien que necesita una **capa diaria de inteligencia de mercado** sin montar un equipo, producto o sistema pesado desde cero.

Encaja especialmente bien con:

- founders que escanean mercado y oportunidades con frecuencia
- scouts de startups, micro-VCs y perfiles de venture discovery
- equipos de innovación o strategy que necesitan una rutina diaria de señal
- product studios o analistas que quieren un radar ligero, operable y transferible

Es menos adecuado para quien busque:
- una plataforma SaaS completa con interfaz avanzada
- cobertura exhaustiva de todo el mercado
- sustitución total del análisis humano

Su mejor encaje es como **activo operativo ligero** para detectar antes qué merece atención, seguimiento o exploración.

---

## Estado actual del producto

Este repositorio representa hoy un **activo funcional y operable**, basado en scripts, listo para demostración y empaquetado, pero **no** una aplicación SaaS completa.

Su estado actual es:

- pipeline en Python con ejecución diaria
- operación simple en local o por cron
- outputs históricos incluidos en `out/`
- salidas en Markdown, JSON y formato Telegram
- sin interfaz web en este repositorio
- estructura ligera y relativamente fácil de entender

Esto lo posiciona mejor como:

- activo operativo para uso interno
- herramienta ligera de research o scouting
- capa diaria de señal para founders, scouts o equipos pequeños
- proyecto empaquetable y transferible a un comprador
- base funcional sobre la que otro operador puede continuar, ampliar o reposicionar

En otras palabras: hoy es más fuerte como **activo pequeño, claro y transferible** que como producto SaaS terminado.

---

## Diferenciales principales

### 1) Prioriza señal sobre ruido
No intenta mostrar “todo”.  
Su valor está en reducir volumen y destacar lo que merece atención real.

### 2) Agrupa historias repetidas
Cuando varias fuentes apuntan al mismo evento o tendencia, el sistema puede agruparlas y reforzar la señal con evidencia adicional.

### 3) Reduce riesgo de alucinación
El modelo no debería inventar títulos ni enlaces: el análisis se apoya en IDs reales de input y luego reconstruye títulos, URLs y fuentes desde los datos originales.

### 4) Entrega una salida orientada a decisión
No se limita a listar noticias.  
Produce un radar diario corto con recomendación explícita: **ACT / WATCH / EXPLORE**.

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

Esto permite combinar cobertura generalista, señal técnica, research temprano y descubrimiento de producto en un único radar diario.

---

## Cómo funciona

A alto nivel, el activo sigue un flujo simple y entendible:

1. recopila items desde fuentes públicas
2. elimina duplicados y ruido evidente
3. aplica filtros para priorizar señal útil
4. agrupa historias repetidas o relacionadas
5. clasifica y puntúa los items con ayuda de LLM
6. reconstruye títulos, enlaces y fuentes desde el input original
7. genera salidas finales en `out/`

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

### 4) Revisar el log de ejecución

```bash
tail -n 50 out/cron.log
```
