
import os
import json
import re
import google.generativeai as genai

LANG = os.getenv("DEFAULT_LANGUAGE", "nl")
MAX_SUG = int(os.getenv("MAX_SUGGESTIONS", "8"))

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-1.5-flash"

def _model():
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY ontbreekt. Zet deze in je Render env vars of .env.")
    return genai.GenerativeModel(MODEL_NAME)

def analyze_listings(listings, user_goal):
    try:
        model = _model()
    except Exception as e:
        return f"AI niet geactiveerd: {e}\nToch {len(listings)} resultaten gevonden."

    prompt = f"""
Je helpt iemand die kapotte koffiemachines koopt, repareert en doorverkoopt.
Doel: {user_goal}

- Kies de beste ~10 kandidaten.
- Geef per kandidaat 1 regel: model/merk (indien te raden), waarom interessant, risico's/onderdelen om te checken.
- Geef aan of prijs t.o.v. onderdelen/defect realistisch lijkt.
- Wees beknopt. Taal: {LANG}.

LISTINGS JSON:
{json.dumps(listings[:30], ensure_ascii=False)}
"""
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        return f"AI analysis error: {e}"

def _parse_price_eur(price_raw: str):
    if not price_raw:
        return None
    m = re.search(r"(\d+[.,]?\d*)", price_raw.replace("\u00a0", " "))
    if not m:
        return None
    try:
        val = float(m.group(1).replace(",", "."))
        return round(val, 2)
    except:
        return None

def suggest_responses_for_listing(listing, prefs):
    try:
        model = _model()
    except Exception as e:
        return {"opener": f"AI niet geactiveerd: {e}", "follow_up":"", "first_offer":"", "counter_offer":"","walkaway_line":"","quick_notes":""}

    target_price = None
    p = _parse_price_eur(listing.get("price_raw",""))
    if p:
        target_price = max(5.0, round(p * 0.5))  # start around 50% for repair project
    anchor = int(target_price) if target_price else 20

    prompt = f"""
Schrijf korte, nette berichten in {LANG} voor Marktplaats.
Context JSON:
{json.dumps({"listing": listing, "buyer_prefs": prefs, "target_price": target_price}, ensure_ascii=False)}

Lever als JSON met deze keys:
- opener
- follow_up
- first_offer
- counter_offer
- walkaway_line
- quick_notes  (3 bullets)

Richtlijnen:
- Wees beleefd, concreet en menselijk, maximaal 1-2 zinnen per bericht.
- Verwijs naar bekende issues (pomp, thermoblok, maalwerk, lekkage).
- Gebruik echte eurobedragen (bijv. €%s), geen placeholders.
""" % anchor

    try:
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start:end+1])
                for k in ["opener","follow_up","first_offer","counter_offer","walkaway_line","quick_notes"]:
                    data.setdefault(k, "")
                return data
            except Exception:
                pass
        return {"opener": text, "follow_up":"", "first_offer":"", "counter_offer":"","walkaway_line":"","quick_notes":""}
    except Exception as e:
        return {"opener": f"(AI error: {e})", "follow_up":"", "first_offer":"", "counter_offer":"","walkaway_line":"","quick_notes":""}
