#!/usr/bin/env python3
import os, json, hashlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import requests
import feedparser
from openai import OpenAI

OUT_DIR = os.path.join(os.path.dirname(__file__), "out")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

MODEL = os.getenv("RADAR_MODEL", "gpt-5")
TOP_N = int(os.getenv("RADAR_TOP_N", "10"))
CREATOR_FOCUS = os.getenv("RADAR_CREATOR_FOCUS", "faceless ai tools, creator workflows, startups, automation")
AUDIENCE = os.getenv("RADAR_AUDIENCE", "creadores faceless y comunidades que quieren ideas prácticas")
PRIMARY_PLATFORM = os.getenv("RADAR_PLATFORM", "Skool")

SOURCES = [
    # Startups / builders
    {"name": "hn", "kind": "json", "url": "https://hn.algolia.com/api/v1/search?tags=front_page"},
    {"name": "producthunt", "kind": "rss", "url": "https://www.producthunt.com/feed"},

    # Tech + AI news (RSS)
    {"name": "techcrunch", "kind": "rss", "url": "https://techcrunch.com/feed/"},
    {"name": "theverge", "kind": "rss", "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "ft_tech", "kind": "rss", "url": "https://www.ft.com/technology?format=rss"},

    # Google News RSS by topic (broad, multi-market)
    {"name": "gn_tech", "kind": "rss", "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB?hl=en&gl=US&ceid=US:en"},
    {"name": "gn_health", "kind": "rss", "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en&gl=US&ceid=US:en"},
    {"name": "gn_business", "kind": "rss", "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFNkNk5Xc0tFeEtFSm5DVU1VY0lnQVAB?hl=en&gl=US&ceid=US:en"},
    {"name": "gn_finance", "kind": "rss", "url": "https://news.google.com/rss/search?q=fintech+OR+payments+OR+banking&hl=en&gl=US&ceid=US:en"},
    {"name": "gn_cyber", "kind": "rss", "url": "https://news.google.com/rss/search?q=cybersecurity+OR+ransomware+OR+breach&hl=en&gl=US&ceid=US:en"},

    # Research / papers (RSS)
    {"name": "arxiv_cs", "kind": "rss", "url": "https://export.arxiv.org/rss/cs"},
    {"name": "arxiv_ai", "kind": "rss", "url": "https://export.arxiv.org/rss/cs.AI"},
]


def now_utc_date():
    # Backwards-compatible name; returns local day key in Europe/Madrid
    return datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d")

def slugify(text: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return clean or "topic"

def audience_hint() -> str:
    return f"Foco del creador: {CREATOR_FOCUS}. Audiencia: {AUDIENCE}. Plataforma principal: {PRIMARY_PLATFORM}."

def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def fetch_items():
    items = []
    health = {"sources": {}}

    for src in SOURCES:
        src_name = src["name"]
        added = 0
        try:
            if src["kind"] == "json":
                r = requests.get(src["url"], timeout=20)
                r.raise_for_status()
                data = r.json()
                for hit in data.get("hits", [])[:50]:
                    title = (hit.get("title") or "").strip()
                    url = (hit.get("url") or hit.get("story_url") or "").strip()
                    if title and url:
                        items.append({"source": {"name": src_name, "url": src["url"]}, "title": title, "url": url})
                        added += 1
            else:
                feed = feedparser.parse(src["url"])
                for e in (feed.entries or [])[:50]:
                    title = (getattr(e, "title", "") or "").strip()
                    url = (getattr(e, "link", "") or "").strip()
                    if title and url:
                        items.append({"source": {"name": src_name, "url": src["url"]}, "title": title, "url": url})
                        added += 1

            health["sources"][src_name] = {"ok": True, "count": added, "error": None}

        except Exception as ex:
            items.append({"source": {"name": src_name, "url": src["url"]}, "title": f"[fetch_error] {src_name}", "url": "", "error": str(ex)})
            health["sources"][src_name] = {"ok": False, "count": 0, "error": str(ex)}

    return items, health


def dedupe(items):
    seen, out = set(), []
    for it in items:
        key = sha((it.get("title","") + "|" + it.get("url","")).lower())
        if key in seen:
            continue
        seen.add(key)
        it["id"] = key
        out.append(it)
    return out



def signal_gate(items):
    """Keep topics that are likely to become useful creator-facing content."""
    allow_politics = os.getenv("RADAR_ALLOW_POLITICS", "0") == "1"
    good_kw = [
        "ai", "agent", "agents", "model", "llm", "robot", "robotics", "biotech", "drug", "clinical", "genomics",
        "fintech", "payments", "processor", "banking", "fraud", "ransomware", "breach", "vulnerability", "exploit",
        "regulation", "law", "compliance", "open source", "github", "release", "benchmark", "swe-bench", "chip", "gpu",
        "launch", "raises", "raise", "funding", "series", "valuation", "startup", "creator", "video", "youtube",
        "tiktok", "shorts", "viral", "trend", "study", "report", "breakthrough", "tool", "app", "automation"
    ]
    bad_kw = ["celebrity","gossip","sports","match","oscars","grammys"]
    creator_focus_kw = [k.strip().lower() for k in CREATOR_FOCUS.split(",") if k.strip()]
    hook_kw = [
        "new", "first", "launch", "breakthrough", "secret", "warning", "risk", "ban", "replace", "beats",
        "faster", "cheaper", "viral", "trend", "explains", "future", "funding", "billion", "tool", "agent"
    ]
    explainer_kw = [
        "ai", "agent", "tool", "app", "startup", "funding", "robot", "drug", "chip", "gpu", "study", "report",
        "regulation", "breach", "open source", "launch", "automation", "benchmark"
    ]

    out = []
    for it in items:
        t = (it.get("title","") or "").strip()
        if len(t) < 18 or len(t) > 140:
            continue
        tl = t.lower()
        if any(b in tl for b in bad_kw):
            continue
        if (not allow_politics) and any(pw in tl for pw in ["election","trump","biden","parliament","senate","congress","war"]):
            # keep only if it also contains strong innovation keywords
            if not any(k in tl for k in ["regulation","compliance","energy","cyber","ai","semiconductor","chip"]):
                continue
        base_score = sum(1 for k in good_kw if k in tl)
        hook_score = sum(1 for k in hook_kw if k in tl)
        explainer_score = sum(1 for k in explainer_kw if k in tl)
        focus_score = sum(1 for k in creator_focus_kw if k in tl)
        if base_score == 0:
            continue
        it["_gate_score"] = (base_score * 2) + (hook_score * 3) + (explainer_score * 2) + (focus_score * 4)
        out.append(it)

    out.sort(key=lambda x: x.get("_gate_score",0), reverse=True)
    for it in out:
        it.pop("_gate_score", None)
    return out


def cluster_candidates(raw_items, limit=60):
    """Cluster by normalize_title(), keep best SOURCE_RANK item, and carry confirmed_by sources."""
    clusters = {}
    order = []
    for it in raw_items:
        key = normalize_title(it.get("title",""))
        if not key:
            continue
        src = (it.get("source",{}) or {}).get("name","?")
        rank = SOURCE_RANK.get(src, 10)
        if key not in clusters:
            clusters[key] = {"best": it, "best_rank": rank, "confirmed_by": set([src])}
            order.append(key)
        else:
            c = clusters[key]
            c["confirmed_by"].add(src)
            if rank > c["best_rank"]:
                c["best"] = it
                c["best_rank"] = rank

    out = []
    for key in order:
        c = clusters[key]
        best = dict(c["best"])
        best["_confirmed_by"] = sorted(list(c["confirmed_by"]))
        out.append(best)
        if len(out) >= limit:
            break
    return out

def select_candidates(raw_items, per_source_caps=None, limit=60):
    """Enforces source diversity caps before sending to the model."""
    per_source_caps = per_source_caps or {}
    counts = {}
    selected = []
    # stable order: keep original order but cap per source
    for it in raw_items:
        name = (it.get("source", {}) or {}).get("name", "unknown")
        cap = per_source_caps.get(name, per_source_caps.get("*", 10))
        n = counts.get(name, 0)
        if n >= cap:
            continue
        counts[name] = n + 1
        selected.append(it)
        if len(selected) >= limit:
            break
    return selected

import re

SOURCE_RANK = {
    'reuters_tech': 100,
    'ft_tech': 90,
    'techcrunch': 70,
    'theverge': 60,
    'hn': 50,
    'producthunt': 40,
    'arxiv_ai': 20,
    'arxiv_cs': 20,
}


def normalize_title(t: str) -> str:
    orig = (t or "").strip()
    low = orig.lower()
    # basic cleanup
    low = re.sub(r"[^a-z0-9\s]+", " ", low)
    low = re.sub(r"\b\d+[a-z]*\b", " ", low)
    low = re.sub(r"\s+", " ", low).strip()

    # entity: first token (works well for org/person headlines)
    entity = (low.split(" ")[0] if low else "")

    # event flags
    has_funding = any(w in low.split() for w in ["funding","round","series","valuation","valued","raises","raise"])

    if entity and has_funding:
        return f"{entity} funding_event"

    # fallback: previous token key (keeps general clustering)
    stop = set("a an the and or for to of in on with amid as at by from into over under latest valued billion bn m usd eur another new value post money".split())
    words = [w for w in low.split(" ") if w and w not in stop and len(w) > 2]
    return " ".join(words[:10])


def dedupe_scored_items(items):
    """Cross-source dedupe + keep best-ranked source + confirmation notes."""
    seen = {}
    out = []
    for it in items:
        key = normalize_title(it.get("title",""))
        if not key:
            continue
        src = (it.get("source",{}) or {}).get("name","?")
        rank = SOURCE_RANK.get(src, 10)

        if key not in seen:
            it["_confirmed_by"] = set([src])
            it["_rank"] = rank
            seen[key] = it
            out.append(it)
            continue

        kept = seen[key]
        kept.setdefault("_confirmed_by", set()).add(src)

        # if new item has better source rank, replace kept but keep confirmations
        if rank > kept.get("_rank", 0):
            it["_confirmed_by"] = kept.get("_confirmed_by", set())
            it["_confirmed_by"].add(src)
            it["_rank"] = rank
            seen[key] = it
            # replace in out list
            idx = out.index(kept)
            out[idx] = it

    # apply notes for confirmations
    for it in out:
        conf = sorted(list(it.get("_confirmed_by", set())))
        if len(conf) > 1:
            n = (it.get("notes") or "").strip()
            tail = f"confirmed_by={conf}"
            it["notes"] = (n + (" | " if n else "") + tail).strip()
        it.pop("_confirmed_by", None)
        it.pop("_rank", None)

    return out


def score_with_gpt(raw_items):
    client = OpenAI()

    prompt = {
        "run_date": now_utc_date(),
        "creator_focus": CREATOR_FOCUS,
        "audience": AUDIENCE,
        "platform": PRIMARY_PLATFORM,
        "items": [{"id": i["id"], "title": i["title"], "item_url": i["url"], "source": i["source"], "confirmed_by": i.get("_confirmed_by", [])} for i in raw_items if i.get("url")][:60]
    }

    system = (
        "Eres un analista de tendencias para creadores faceless y contenido corto. "
        "Devuelve SOLO JSON válido siguiendo el contrato exacto. "
        "REGLA CRITICA: NO inventes hechos. NO reescribas títulos. "
        "Debes seleccionar items SOLO desde INPUT usando su campo 'id'. "
        "NO inventes: si un item no existe en INPUT, no lo uses. "
        "Si no puedes inferir algo sin inventar, baja score y pon notes='uncertain'. "
        "Objetivo: separar señal de ruido y recomendar acción para contenido. "
        "Idioma de salida: escribe en español neutro todos los campos generados por ti. "
        "Mantén el campo 'title' exactamente como venga en INPUT, sin traducirlo ni reescribirlo. "
        "Escribe en español: 'what_it_is', 'why_it_matters', 'content_why_now', 'content_angle', 'hook', 'tags' y 'notes'. "
        "Mantén las enums y valores del contrato exactamente como están. "
        "Usa español correcto con tildes, eñes y caracteres Unicode reales. "
        "No sustituyas caracteres acentuados por ASCII ni por transliteraciones defectuosas como mFs, gesti3n o autonomDa. "
        "Prioriza historias que puedan convertirse en reels, shorts, carruseles o posts claros, curiosos y fáciles de explicar. "
        "Alinea la selección con el foco del creador, la audiencia y la plataforma indicados en INPUT."
    )

    contract = """{
  "run_date":"YYYY-MM-DD",
  "items":[
    {
      "id":"",
      "title":"",
      "item_url":"",
      "category":"AI|Tools|Startups|Business|Cyber|Science|Regulation|ConsumerTech|Other",
      "source":{"name":"","url":""},
      "what_it_is":"",
      "why_it_matters":"",
      "content_why_now":"",
      "content_angle":"",
      "best_format":"REEL|SHORT|CAROUSEL|THREAD|POST",
      "hook":"",
      "hook_variants":["",""],
      "talking_points":["","",""],
      "cta":"",
      "search_intent":"DISCOVER|EXPLAIN|OPINION|ALERT|CURATION",
      "audience_level":"GENERAL|SEMI_TECH|TECH",
      "signals":{"hook_strength":0,"novelty":0,"clarity":0,"shareability":0,"creator_fit":0},
      "score_total":0,
      "hype_risk":"LOW|MED|HIGH",
      "recommended_action":"SKIP|WATCH|DRAFT|POST",
      "tags":["",""],
      "notes":""
    }
  ]
}"""

    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": "CONTRATO:\n" + contract + "\n\nINPUT:\n" + json.dumps(prompt)}
        ],
        text={"format": {"type": "json_object"}}
    )
    return json.loads(resp.output_text)

def main():
    date = now_utc_date()
    fetched, health = fetch_items()
    raw = dedupe(fetched)
    raw_map = {i["id"]: i for i in raw}
    # Source diversity caps (tune later)
    caps = {
        'hn': 20,
        'producthunt': 10,
        'techcrunch': 8,
        'theverge': 8,
        'reuters_tech': 8,
        'ft_tech': 8,
        'arxiv_cs': 8,
        'arxiv_ai': 8,
        '*': 10,
    }
        # Signal gate: reduce noise before source caps
    raw_filtered = signal_gate(raw)
    raw_for_model = select_candidates(raw_filtered, per_source_caps=caps, limit=60)
    raw_for_model = cluster_candidates(raw_for_model, limit=60)
    confirmed_map = {i['id']: i.get('_confirmed_by', []) for i in raw_for_model if 'id' in i}
    scored = score_with_gpt(locals().get('raw_for_model', raw))
    # Hard safety: rebuild title/item_url/source from raw input by id
    for it in scored.get("items", []):
        rid = it.get("id")
        src = raw_map.get(rid)
        if src:
            it["title"] = src.get("title","")
            it["item_url"] = src.get("url","")
            it["source"] = src.get("source", it.get("source", {}))
            conf = locals().get("confirmed_map", {}).get(rid, [])
            if conf and len(conf) > 1:
                n = (it.get("notes") or "").strip()
                tail = f"confirmed_by={conf}"
                it["notes"] = (n + (" | " if n else "") + tail).strip()
        else:
            it["notes"] = (it.get("notes","") + " | dropped: unknown id").strip(" |")
    scored["items"] = sorted(scored.get("items", []), key=lambda x: x.get("score_total", 0), reverse=True)
    scored["items"] = dedupe_scored_items(scored.get("items", []))
    scored["items"] = scored.get("items", [])[:TOP_N]
    for it in scored["items"]:
        it.setdefault("content_why_now", "")
        it.setdefault("content_angle", "")
        it.setdefault("best_format", "POST")
        it.setdefault("hook", "")
        it.setdefault("hook_variants", [])
        it.setdefault("talking_points", [])
        it.setdefault("cta", "")
        it.setdefault("search_intent", "DISCOVER")
        it.setdefault("audience_level", "GENERAL")
        it.setdefault("signals", {})
        it["signals"].setdefault("hook_strength", 0)
        it["signals"].setdefault("novelty", 0)
        it["signals"].setdefault("clarity", 0)
        it["signals"].setdefault("shareability", 0)
        it["signals"].setdefault("creator_fit", 0)
    for idx, it in enumerate(scored["items"], 1):
        it["rank"] = idx

    import tempfile

    out_json = os.path.join(OUT_DIR, f"radar_{date}.json")
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=f"radar_{date}.", suffix=".json.tmp", dir=OUT_DIR)
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(scored, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, out_json)  # atomic
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

    out_md = os.path.join(OUT_DIR, f"radar_{date}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# Content Trend Radar {date}\n\n")
        f.write(f"> {audience_hint()}\n\n")
        for idx, it in enumerate(scored["items"], 1):
            f.write(f"## {idx}. {it['title']}\n")
            f.write(f"- Score: **{it['score_total']}** | Action: **{it['recommended_action']}** | Hype: **{it['hype_risk']}**\n")
            f.write(f"- Category: {it['category']}\n")
            f.write(f"- Source: {it['source'].get('name')}\n")
            f.write(f"- Link: {it.get('item_url','')}\n")
            what = it.get("what_it_is", "")
            why = it.get("why_it_matters", "")
            why_now = it.get("content_why_now", "")
            angle = it.get("content_angle", "")
            hook = it.get("hook", "")
            if not why:
             it["notes"] = (it.get("notes","") + " | missing_field=why_it_matters").strip(" |")

            f.write(f"- What: {what}\n")
            f.write(f"- Why: {why}\n")
            f.write(f"- Why now for content: {why_now}\n")
            f.write(f"- Suggested angle: {angle}\n")
            f.write(f"- Best format: {it.get('best_format', 'POST')}\n")
            f.write(f"- Search intent: {it.get('search_intent', 'DISCOVER')}\n")
            f.write(f"- Audience level: {it.get('audience_level', 'GENERAL')}\n")
            f.write(f"- Hook: {hook}\n")
            hook_variants = [x for x in it.get("hook_variants", []) if x]
            if hook_variants:
                f.write("- Hook variants: " + " | ".join(hook_variants) + "\n")
            talking_points = [x for x in it.get("talking_points", []) if x]
            if talking_points:
                f.write("- Talking points: " + " | ".join(talking_points) + "\n")
            cta = (it.get("cta") or "").strip()
            if cta:
                f.write(f"- CTA: {cta}\n")
            s = it.get("signals", {})
            f.write(
                "- Content signals: "
                f"hook={s.get('hook_strength', 0)} | "
                f"novelty={s.get('novelty', 0)} | "
                f"clarity={s.get('clarity', 0)} | "
                f"shareability={s.get('shareability', 0)} | "
                f"creator_fit={s.get('creator_fit', 0)}\n"
            )
            f.write(f"- Tags: {', '.join(it.get('tags', []))}\n")

            notes = (it.get("notes") or "").strip()
            if notes and notes.lower() != "uncertain":
                f.write(f"- Notes: {notes}\n")
            f.write("\n")

    print(f"OK: {out_json}")
    print(f"OK: {out_md}")

    def build_skool_post(items_sorted, top_cat):
        lines = []
        lines.append(f"# Top 10 de ideas para hoy ({date})")
        lines.append("")
        lines.append(f"Hoy el radar viene cargado de **{top_cat}**.")
        lines.append(f"Foco: **{CREATOR_FOCUS}**.")
        lines.append("")
        lines.append("He filtrado las señales pensando en temas que se puedan convertir rápido en contenido.")
        lines.append("")
        for idx, it in enumerate(items_sorted, 1):
            action = it.get("recommended_action", "WATCH")
            format_name = it.get("best_format", "POST")
            hook = (it.get("hook") or "").strip()
            angle = (it.get("content_angle") or "").strip()
            lines.append(f"## {idx}. {it.get('title','').strip()}")
            lines.append(f"- Acción: **{action}**")
            lines.append(f"- Formato sugerido: **{format_name}**")
            if hook:
                lines.append(f"- Hook: {hook}")
            if angle:
                lines.append(f"- Ángulo: {angle}")
            lines.append(f"- Link: {it.get('item_url','').strip()}")
            lines.append("")
        lines.append("Si queréis, de uno de estos temas saco después hooks, guion o carrusel.")
        return "\n".join(lines) + "\n"

    def build_creator_workbench(items_sorted):
        lines = []
        lines.append(f"# Creator Workbench {date}")
        lines.append("")
        lines.append(f"- Plataforma principal: {PRIMARY_PLATFORM}")
        lines.append(f"- Audiencia: {AUDIENCE}")
        lines.append(f"- Foco: {CREATOR_FOCUS}")
        lines.append("")
        for idx, it in enumerate(items_sorted, 1):
            lines.append(f"## {idx}. {it.get('title','').strip()}")
            lines.append(f"- Acción: {it.get('recommended_action', 'WATCH')}")
            lines.append(f"- Formato: {it.get('best_format', 'POST')}")
            lines.append(f"- Search intent: {it.get('search_intent', 'DISCOVER')}")
            lines.append(f"- Hook principal: {it.get('hook','').strip()}")
            for n, hook_variant in enumerate([x for x in it.get('hook_variants', []) if x], 1):
                lines.append(f"- Hook alternativo {n}: {hook_variant}")
            for n, point in enumerate([x for x in it.get('talking_points', []) if x], 1):
                lines.append(f"- Talking point {n}: {point}")
            cta = (it.get("cta") or "").strip()
            if cta:
                lines.append(f"- CTA: {cta}")
            lines.append(f"- Prompt rápido: Convierte este tema en un {it.get('best_format', 'POST').lower()} para {AUDIENCE} usando este hook: {it.get('hook','').strip()}")
            lines.append("")
        return "\n".join(lines) + "\n"

    # --- latest pointers (copy) ---
    latest_json = os.path.join(OUT_DIR, "latest.json")
    latest_md = os.path.join(OUT_DIR, "latest.md")

    # copy to stable names (avoid symlink issues)
    with open(out_json, "r", encoding="utf-8") as src, open(latest_json, "w", encoding="utf-8") as dst:
        dst.write(src.read())

    with open(out_md, "r", encoding="utf-8") as src, open(latest_md, "w", encoding="utf-8") as dst:
        dst.write(src.read())

    # --- Telegram digest v1 (no delivery yet) ---
    def _tg_line(it):
        action = it.get("recommended_action", "WATCH")
        title = (it.get("title") or "").strip()
        src = ((it.get("source") or {}).get("name") or "").strip()
        hook = (it.get("hook") or "").strip()
        best_format = (it.get("best_format") or "POST").strip()
        notes = (it.get("notes") or "")
        cb = ""
        if "confirmed_by=" in notes:
            # show only the count (avoid long lists)
            try:
                inside = notes.split("confirmed_by=", 1)[1]
                # inside like "['hn','ft_tech']" or similar
                n = inside.count("'") // 2  # rough but stable enough
                if n > 0:
                    cb = f" — confirmed_by:{n}"
            except Exception:
                pass
        # keep lines compact
        if len(title) > 160:
            title = title[:157] + "…"
        url = (it.get("item_url") or "").strip()
        hook_line = f"\n  hook: {hook}" if hook else ""
        format_line = f"\n  format: {best_format}" if best_format else ""
        suffix = f"\n  {url}" if url else ""
        return f"- [{action}] {title} ({src}){cb}{hook_line}{format_line}{suffix}"


    items = scored.get("items", [])
    items_sorted = sorted(items, key=lambda x: x.get("score_total", 0), reverse=True)
    cats = [x.get("category", "Other") for x in items_sorted]
    top_cat = max(set(cats), key=cats.count) if cats else "Other"
    post = [x for x in items_sorted if x.get("recommended_action") == "POST"][:3]
    draft = [x for x in items_sorted if x.get("recommended_action") == "DRAFT"][:3]
    watch = [x for x in items_sorted if x.get("recommended_action") == "WATCH"][:2]
    skip = [x for x in items_sorted if x.get("recommended_action") == "SKIP"][:1]

    lines = []
    bad = []
    for name, st in (health.get("sources") or {}).items():
        if (not st.get("ok")) or (st.get("count", 0) == 0):
            bad.append(f"{name}={'err' if not st.get('ok') else '0'}")
    health_txt = "OK" if not bad else "WARN (" + ", ".join(sorted(bad)) + ")"
    lines.append(f"Content Trend Radar — {date} — Health: {health_txt}")
    lines.append("")
    lines.append(f"Tema del día: {top_cat}")
    lines.append("")
    lines.append("TOP (POST)")
    lines += [_tg_line(x) for x in post] if post else ["- (sin POST hoy)"]
    lines.append("")
    lines.append("DRAFT")
    lines += [_tg_line(x) for x in draft] if draft else ["- (sin DRAFT hoy)"]
    lines.append("")
    lines.append("WATCH")
    lines += [_tg_line(x) for x in watch] if watch else ["- (sin WATCH hoy)"]
    lines.append("")
    lines.append("SKIP")
    lines += [_tg_line(x) for x in skip] if skip else ["- (sin SKIP hoy)"]
    lines.append("")

    # --- Killer insight (heuristic, no extra LLM) ---
    cats = [x.get("category", "Other") for x in items_sorted]
    top_cat = max(set(cats), key=cats.count) if cats else "Other"

    post_count = sum(1 for x in items_sorted if x.get("recommended_action") == "POST")
    draft_count = sum(1 for x in items_sorted if x.get("recommended_action") == "DRAFT")
    watch_count = sum(1 for x in items_sorted if x.get("recommended_action") == "WATCH")

    implication = (
        f"Hoy domina {top_cat}: {post_count} POST, {draft_count} DRAFT y {watch_count} WATCH "
        "sugieren temas con potencial real para contenido, no solo ruido informativo."
    )

    top_titles = [x.get("title","").strip() for x in post[:2] if x.get("title")]
    if top_titles:
        next_step = f"Convierte primero este tema en un hook y un guion corto: {top_titles[0]}."
    else:
        next_step = "Revisa el TOP 3 y elige uno para convertirlo en reel, carrusel o post antes de seguir buscando más ideas."

    # we’ll inject these below

    lines.append("Killer insight")
    lines.append(f"- Implicación: {implication}")
    lines.append(f"- Próximo paso: {next_step}")
    lines.append("")
    lines.append("Full: out/latest.md")
    lines.append("JSON: out/latest.json")
    telegram_text = "\n".join(lines) + "\n"

    skool_text = build_skool_post(items_sorted, top_cat)
    workbench_text = build_creator_workbench(items_sorted)

    out_tg = os.path.join(OUT_DIR, f"radar_{date}.telegram.txt")
    with open(out_tg, "w", encoding="utf-8") as f:
        f.write(telegram_text)

    out_skool = os.path.join(OUT_DIR, f"radar_{date}.skool.md")
    with open(out_skool, "w", encoding="utf-8") as f:
        f.write(skool_text)

    out_workbench = os.path.join(OUT_DIR, f"radar_{date}.workbench.md")
    with open(out_workbench, "w", encoding="utf-8") as f:
        f.write(workbench_text)

    latest_tg = os.path.join(OUT_DIR, "latest.telegram.txt")
    try:
        if os.path.islink(latest_tg) or os.path.exists(latest_tg):
            os.remove(latest_tg)
        os.symlink(os.path.basename(out_tg), latest_tg)
    except Exception:
        # fallback on platforms without symlink permissions
        with open(latest_tg, "w", encoding="utf-8") as f:
            f.write(telegram_text)

    latest_skool = os.path.join(OUT_DIR, "latest.skool.md")
    latest_workbench = os.path.join(OUT_DIR, "latest.workbench.md")

    with open(out_skool, "r", encoding="utf-8") as src, open(latest_skool, "w", encoding="utf-8") as dst:
        dst.write(src.read())

    with open(out_workbench, "r", encoding="utf-8") as src, open(latest_workbench, "w", encoding="utf-8") as dst:
        dst.write(src.read())


if __name__ == "__main__":
    # Sanity check timezone day_key (Europe/Madrid)
    from datetime import datetime, timezone
    dt = datetime(2026, 2, 14, 23, 30, tzinfo=timezone.utc)
    madrid = dt.astimezone(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d")
    assert madrid == "2026-02-15", f"day_key tz regression: {madrid}"

    main()
