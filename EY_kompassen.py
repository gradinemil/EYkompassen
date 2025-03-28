from flask import Flask, render_template, request
import json
import os

app = Flask(__name__, template_folder="templates")

questions = {
    1: {"text": "Hur hanterar du helst nya situationer?", "options": [
        {"label": "Jag gillar att ta ett steg tillbaka och få överblick först", "value": "strategy:2,consulting:1"},
        {"label": "Jag tar itu med detaljerna först", "value": "assurance:2,tax:1"},
        {"label": "Jag brainstormar med andra och söker kreativa lösningar", "value": "consulting:2,strategy:1"},
        {"label": "Jag gillar när det finns tydliga ramar och instruktioner att följa", "value": "tax:2,assurance:1"},
    ]},
    2: {"text": "Vilken typ av projekt låter mest intressant?", "options": [
        {"label": "Förbättra befintliga processer och system", "value": "consulting:2,assurance:1"},
        {"label": "Bidra till beslut som formar framtiden", "value": "strategy:3"},
        {"label": "Projekt där man får tolka information noggrant", "value": "tax:2,assurance:1"},
        {"label": "Granska och säkra information", "value": "assurance:3"},
    ]},
    3: {"text": "Vad motiverar dig mest?", "options": [
        {"label": "Att tänka kreativt och hitta nya vägar framåt", "value": "strategy:2,consulting:1"},
        {"label": "Att ha tydliga riktlinjer och säkra att allt stämmer", "value": "assurance:2,tax:1"},
        {"label": "Att lösa problem i samarbete med andra", "value": "consulting:2,strategy:1"},
        {"label": "Att fördjupa mig i detaljer och påverka med kunskap", "value": "tax:3"},
    ]},
    4: {"text": "Hur beskriver du din arbetsstil bäst?", "options": [
        {"label": "Logisk, strukturerad och ansvarsfull", "value": "assurance:2,tax:1"},
        {"label": "Kreativ, kommunikativ och öppen för förändring", "value": "consulting:2,strategy:1"},
        {"label": "Målinriktad, analytisk och helhetsorienterad", "value": "strategy:2,consulting:1"},
        {"label": "Noggrann, systematisk och gillar tydliga riktlinjer", "value": "tax:2,assurance:1"},
    ]},
    5: {"text": "Vilket påstående stämmer bäst in på dig?", "options": [
        {"label": "Jag gillar att förbättra saker och optimera lösningar", "value": "consulting:2,strategy:1"},
        {"label": "Jag är nyfiken på samband och vill förstå helheten", "value": "strategy:2,assurance:1"},
        {"label": "Jag vill skapa trygghet och se till att allt stämmer", "value": "assurance:2,tax:1"},
        {"label": "Jag drivs av att förstå komplexa lagar och regler", "value": "tax:3"},
    ]},
    6: {"text": "Hur hanterar du osäkerhet?", "options": [
        {"label": "Jag gillar att skapa struktur i komplexa situationer", "value": "assurance:2,tax:1"},
        {"label": "Jag tycker om att vara kreativ när läget är otydligt", "value": "strategy:2,consulting:1"},
        {"label": "Jag försöker förstå helheten och planera därefter", "value": "strategy:2"},
        {"label": "Jag kollar gärna med experter och följer riktlinjer", "value": "tax:2,assurance:1"},
    ]},
    7: {"text": "Vad tycker du är roligast att arbeta med?", "options": [
        {"label": "Att ta mig an kluriga problem med struktur och analys", "value": "strategy:3"},
        {"label": "Att utveckla digitala eller tekniska lösningar", "value": "consulting:2,strategy:1"},
        {"label": "Att analysera data för att säkerställa korrekthet", "value": "assurance:3"},
        {"label": "Att gå på djupet och förstå viktiga dokument eller avtal", "value": "tax:3"},
    ]},
    8: {"text": "Hur vill du att din roll ska påverka andra?", "options": [
        {"label": "Skapa tydlighet och pålitlighet i siffror och rapporter", "value": "assurance:2"},
        {"label": "Göra komplexa beslut lättare att förstå och fatta", "value": "strategy:2,consulting:1"},
        {"label": "Hjälpa organisationer att utvecklas och växa", "value": "consulting:2,strategy:1"},
        {"label": "Hjälpa till att allt fungerar som det ska i vardagen", "value": "tax:2,assurance:1"},
    ]},
    9: {"text": "I vilken typ av arbetsmiljö trivs du bäst?", "options": [
        {"label": "Ett ordnat och förutsägbart arbetsklimat", "value": "assurance:2,tax:2"},
        {"label": "En fartfylld miljö med nya idéer och variation", "value": "consulting:2,strategy:1"},
        {"label": "En tänkande miljö där långsiktighet och logik är viktigt", "value": "strategy:2,consulting:1"},
        {"label": "En miljö där det är viktigt att allt blir rätt", "value": "assurance:3"},
    ]},
    10: {"text": "Vilken typ av samarbete föredrar du?", "options": [
        {"label": "Jag trivs bäst i små team med tydliga roller", "value": "tax:2,assurance:1"},
        {"label": "Jag gillar att jobba med olika människor och tänka tillsammans", "value": "consulting:2,strategy:1"},
        {"label": "Jag föredrar att arbeta självständigt och ta ansvar för mina delar", "value": "assurance:2"},
        {"label": "Jag tycker om att ha inflytande och vara med där beslut tas", "value": "strategy:3"},
    ]},
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    chart_data = {}
    top_match = None

    if request.method == "POST":
        scores = {"strategy": 0, "consulting": 0, "assurance": 0, "tax": 0}
        for i in range(1, 11):
            response = request.form.get(f"q{i}")
            if response:
                parts = response.split(',')
                for part in parts:
                    key, val = part.split(':')
                    scores[key] += int(val)

        total = sum(scores.values())
        if total > 0:
            percentages = {k: round(v / total * 100) for k, v in scores.items()}
            sorted_matches = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
            result = " ".join([f"{k}:{v}" for k, v in sorted_matches])
            chart_data = json.dumps(percentages)
            top_match = (
                'Strategy & Transactions' if sorted_matches[0][0] == 'strategy' else
                'Tax & Law' if sorted_matches[0][0] == 'tax' else
                sorted_matches[0][0].capitalize()
            )

    return render_template("index.html", result=result, questions=questions, chart_data=chart_data, top_match=top_match)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
