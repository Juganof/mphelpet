
import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from scraper import scrape_marktplaats
from ai_analysis import analyze_listings, suggest_responses_for_listing, MAX_SUG

load_dotenv()
app = Flask(__name__)

def collect_prefs(form):
    preferred_brands = form.get("preferred_brands","")
    return {
        "language": form.get("language", os.getenv("DEFAULT_LANGUAGE", "nl")),
        "max_budget": form.get("max_budget", "").strip(),
        "preferred_brands": [b.strip() for b in preferred_brands.split(",") if b.strip()],
        "distance_note": form.get("distance_note",""),
        "strategy": form.get("strategy","vriendelijk maar vastberaden"),
    }

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    analysis = ""
    recs = {}
    prefs = None
    keyword = ""

    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        prefs = collect_prefs(request.form)
        user_goal = f"Zoekwoord: {keyword}. Budget: {prefs.get('max_budget')}. Merken: {prefs.get('preferred_brands')}."
        try:
            results = scrape_marktplaats(keyword)
        except Exception as e:
            analysis = f"Fout bij ophalen resultaten: {e}"
            results = []

        try:
            if results:
                analysis = analyze_listings(results, user_goal)
                for i, item in enumerate(results[:MAX_SUG]):
                    recs[i] = suggest_responses_for_listing(item, prefs)
        except Exception as e:
            analysis = analysis + f"\n(AI-suggesties fout: {e})"

    return render_template("index.html",
                           results=results,
                           analysis=analysis,
                           recs=recs,
                           keyword=keyword,
                           prefs=prefs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
