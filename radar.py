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

SOURCES = [
    # Startups / builders
    {"name": "hn", "kind": "json", "url": "https://hn.algolia.com/api/v1/search?tags=front_page"},
    {"name": "producthunt", "kind": "rss", "url": "https://www.producthunt.com/feed"},

    # Tech + AI news (RSS)
    {"name": "techcrunch", "kind": "rss", "url": "https://techcrunch.com/feed/"},
    {"name": "theverge", "kind": "rss", "url": "https://www.theverge.com/rss/index.xml"},

    # Business signals (RSS)    {"name": "ft_tech", "kind": "rss", "url": "https://www.ft.com/technology?format=rss"},

    # Google News RSS by topic (broad, multi-market)
    {"name": "gn_tech", "kind": "rss", "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB?hl=en&gl=US&ceid=US:en"},
    {"name": "gn_health", "kind": "rss", "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en&gl=US&ceid=US:en"},
    {"name": "gn_business", "kind": "rss", "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en&gl=US&ceid=US:en"},
    {"name": "gn_finance", "kind": "rss", "url": "https://news.google.com/rss/search?q=fintech+OR+payments+OR+banking&hl=en&gl=US&ceid=US:en"},
    {"name": "gn_cyber", "kind": "rss", "url": "https://news.google.com/rss/search?q=cybersecurity+OR+ransomware+OR+breach&hl=en&gl=US&ceid=US:en"},

    # Research / papers (RSS)
    {"name": "arxiv_cs", "kind": "rss", "url": "https://export.arxiv.org/rss/cs"},
    {"name": "arxiv_ai", "kind": "rss", "url": "https://export.arxiv.org/rss/cs.AI"},
]


def now_utc_date():
    # Backwards-compatible name; returns local day key in Europe/Madrid
    return datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d")

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
    """Lightweight quality filter to reduce noise before LLM."""
    allow_politics = os.getenv("RADAR_ALLOW_POLITICS", "0") == "1"
    good_kw = [
        "ai","agent","agents","model","llm","robot","robotics","biotech","drug","clinical","genomics",
        "fintech","payments","processor","banking","fraud","ransomware","breach","vulnerability","exploit",
        "regulation","law","compliance","open source","github","release","benchmark","swe-bench","chip","gpu"
    ]
    bad_kw = ["celebrity","gossip","sports","match","oscars","grammys"]

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
        # score keywords
        score = sum(1 for k in good_kw if k in tl)
        if score == 0:
            continue
        it["_gate_score"] = score
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
        "items": [{"id": i["id"], "title": i["title"], "item_url": i["url"], "source": i["source"], "confirmed_by": i.get("_confirmed_by", [])} for i in raw_items if i.get("url")][:60]
    }

    system = (
        "Eres un analista de tendencias multi-mercado (global). "
        "Devuelve SOLO JSON válido siguiendo el contrato exacto. "
        "REGLA CRITICA: NO inventes hechos. NO reescribas títulos. "
        "Debes seleccionar items SOLO desde INPUT usando su campo 'id'. "
        "NO inventes: si un item no existe en INPUT, no lo uses. "
        "Si no puedes inferir algo sin inventar, baja score y pon notes='uncertain'. "
        "Objetivo: separar señal de ruido y recomendar acción."
    )

    contract = """{
  "run_date":"YYYY-MM-DD",
  "items":[
    {
      "id":"",
      "title":"",
      "item_url":"",
      "category":"AI|Health|Fintech|Cyber|Regulation|Energy|Retail|Ops|Other",
      "source":{"name":"","url":""},
      "what_it_is":"",
      "why_it_matters":"",
      "signals":{"momentum":0,"market_urgency":0,"moat":0,"monetization":0,"strategic_fit":0},
      "score_total":0,
      "hype_risk":"LOW|MED|HIGH",
      "recommended_action":"IGNORE|WATCH|EXPLORE|ACT",
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

    out_json = os.path.join(OUT_DIR, f"radar_{date}.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(scored, f, ensure_ascii=False, indent=2)

    out_md = os.path.join(OUT_DIR, f"radar_{date}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# Trend Radar {date}\n\n")
        for idx, it in enumerate(scored["items"], 1):
            f.write(f"## {idx}. {it['title']}\n")
            f.write(f"- Score: **{it['score_total']}** | Action: **{it['recommended_action']}** | Hype: **{it['hype_risk']}**\n")
            f.write(f"- Category: {it['category']}\n")
            f.write(f"- Source: {it['source'].get('name')} | {it['source'].get('url')}\n")
            f.write(f"- Link: {it.get('item_url','')}\n")
            f.write(f"- What: {it['what_it_is']}\n")
            f.write(f"- Why: {it['why_it_matters']}\n")
            f.write(f"- Tags: {', '.join(it.get('tags', []))}\n")
            if it.get("notes"):
                f.write(f"- Notes: {it['notes']}\n")
            f.write("\n")

    print(f"OK: {out_json}")
    print(f"OK: {out_md}")

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
        suffix = f"\n  {url}" if url else ""
        return f"- [{action}] {title} ({src}){cb}{suffix}"


    items = scored.get("items", [])
    items_sorted = sorted(items, key=lambda x: x.get("score_total", 0), reverse=True)
    cats = [x.get("category", "Other") for x in items_sorted]
    top_cat = max(set(cats), key=cats.count) if cats else "Other"
    act = [x for x in items_sorted if x.get("recommended_action") == "ACT"][:3]
    watch = [x for x in items_sorted if x.get("recommended_action") == "WATCH"][:2]
    explore = [x for x in items_sorted if x.get("recommended_action") == "EXPLORE"][:1]

    lines = []
    bad = []
    for name, st in (health.get("sources") or {}).items():
        if (not st.get("ok")) or (st.get("count", 0) == 0):
            bad.append(f"{name}={'err' if not st.get('ok') else '0'}")
    health_txt = "OK" if not bad else "WARN (" + ", ".join(sorted(bad)) + ")"
    lines.append(f"Market Wow Radar — {date} — Health: {health_txt}")
    lines.append("")
    lines.append(f"Tema del día: {top_cat}")
    lines.append("")
    lines.append("TOP (ACT)")
    lines += [_tg_line(x) for x in act] if act else ["- (sin ACT hoy)"]
    lines.append("")
    lines.append("WATCH")
    lines += [_tg_line(x) for x in watch] if watch else ["- (sin WATCH hoy)"]
    lines.append("")
    lines.append("EXPLORE")
    lines += [_tg_line(x) for x in explore] if explore else ["- (sin EXPLORE hoy)"]
    lines.append("")

    # --- Killer insight (heuristic, no extra LLM) ---
    cats = [x.get("category", "Other") for x in items_sorted]
    top_cat = max(set(cats), key=cats.count) if cats else "Other"

    lines.append(f"Tema del día: {top_cat}")
    lines.append("")

    act_count = sum(1 for x in items_sorted if x.get("recommended_action") == "ACT")
    watch_count = sum(1 for x in items_sorted if x.get("recommended_action") == "WATCH")

    implication = f"Hoy domina {top_cat}: {act_count} ACT y {watch_count} WATCH sugieren señal accionable (no solo ruido)."

    top_titles = [x.get("title","").strip() for x in act[:2] if x.get("title")]
    if top_titles:
        next_step = f"Haz 1 verificación rápida: abre y resume en 3 bullets: {top_titles[0]}."
    else:
        next_step = "Revisa el TOP 3 y decide si activar un experimento de 1h (POC) o solo seguimiento."

    # we’ll inject these below

    lines.append("Killer insight")
    lines.append(f"- Implicación: {implication}")
    lines.append(f"- Próximo paso: {next_step}")
    lines.append("")
    lines.append("Full: out/latest.md")
    lines.append("JSON: out/latest.json")
    telegram_text = "\n".join(lines) + "\n"

    out_tg = os.path.join(OUT_DIR, f"radar_{date}.telegram.txt")
    with open(out_tg, "w", encoding="utf-8") as f:
        f.write(telegram_text)

    latest_tg = os.path.join(OUT_DIR, "latest.telegram.txt")
    try:
        if os.path.islink(latest_tg) or os.path.exists(latest_tg):
            os.remove(latest_tg)
        os.symlink(os.path.basename(out_tg), latest_tg)
    except Exception:
        # fallback on platforms without symlink permissions
        with open(latest_tg, "w", encoding="utf-8") as f:
            f.write(telegram_text)


if __name__ == "__main__":
    # Sanity check timezone day_key (Europe/Madrid)
    from datetime import datetime, timezone
    dt = datetime(2026, 2, 14, 23, 30, tzinfo=timezone.utc)
    madrid = dt.astimezone(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d")
    assert madrid == "2026-02-15", f"day_key tz regression: {madrid}"

    main()

