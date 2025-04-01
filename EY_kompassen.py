from flask import Flask, render_template_string, request
import json
import socket
import webbrowser
import threading
import time

app = Flask(__name__)

html_template = """
<!DOCTYPE html>
<html lang='sv'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>EY Kompassen</title>
  <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #2E2E38;
      margin: 0;
      padding: 0;
    }
    .container {
      max-width: 800px;
      margin: 20px auto;
      background: white;
      padding: 20px;
      border-radius: 16px;
      box-shadow: 0 10px 20px rgba(0,0,0,0.1);
      text-align: center;
    }
    h1 {
      font-size: 1.8em;
      margin-bottom: 10px;
    }
    .question {
      margin-bottom: 30px;
      opacity: 0;
      transform: translateY(20px);
      transition: all 0.5s ease;
    }
    .question.active {
      opacity: 1;
      transform: translateY(0);
    }
    select {
      width: 100%;
      padding: 10px;
      margin-top: 10px;
      font-size: 1em;
    }
    button {
      background-color: #00796b;
      color: white;
      padding: 12px 20px;
      font-size: 1em;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      margin: 20px 10px 0 10px;
    }
    button:hover {
      background-color: #004d40;
    }
    .result {
      margin-top: 40px;
    }
    #progressBar {
      width: 100%;
      background-color: #ddd;
      border-radius: 10px;
      overflow: hidden;
      height: 20px;
      margin-top: 20px;
    }
    #progressBarFill {
      height: 100%;
      width: 0;
      background-color: #00796b;
      transition: width 0.3s ease;
      color: white;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    #intro {
      display: block;
      text-align: center;
      padding: 60px 20px;
    }
    #intro h2 {
      font-size: 1.8em;
      margin-bottom: 10px;
    }
    #intro p {
      font-size: 1.2em;
      margin-bottom: 20px;
    }
    #warningMessage {
      display: none;
      color: red;
      font-weight: bold;
      margin-top: 20px;
      text-align: center;
    }
    @media (max-width: 600px) {
      .container {
        margin: 10px;
        padding: 15px;
      }
      h1 {
        font-size: 1.5em;
      }
      select {
        font-size: 1em;
      }
      button {
        width: 100%;
        margin: 10px 0;
      }
    }
  </style>
</head>
<body>
  <div class='container'>
    {% if not result %}
    <div id='intro'>
  <span style='font-size: 4rem; color: black;'>🧭</span>
  <h1>EY Kompassen</h1>
  <p>Ta reda på var du passar bäst in hos oss!</p>
  <p style='font-size: 1.1em; margin-bottom: 10px;'>EY (Ernst & Young) är ett av världens största revisions- och rådgivningsföretag med verksamhet i över 150 länder. Vi hjälper företag, organisationer och offentlig sektor att växa, effektivisera och hantera förändringar på ett hållbart och ansvarsfullt sätt. EY:s syfte är att "bygga en bättre arbetsvärld" genom att skapa långsiktigt värde för kunder, medarbetare och samhället.</p>
      <p style='font-size: 1.1em; margin-bottom: 10px;'>Hos oss kan du jobba i någon av dessa affärsområden:</p>
      <br>
       <ul style='list-style: none; padding: 0; font-size: 1em; text-align: left; max-width: 600px; margin: 0 auto;'>
        <br><li><strong>Assurance:</strong> Säkerställer att företag rapporterar rättvisande och transparent information till omvärlden. Det handlar om revision, hållbarhetsgranskning och rådgivning som skapar förtroende på marknaden.</li><br>
        <br><li><strong>Consulting:</strong> Arbetar med att hjälpa företag utvecklas genom innovation, transformation och digitalisering. Här kombinerar du teknik, strategi och mänskliga perspektiv för att förbättra kunders verksamhet i grunden.</li><br>
        <br><li><strong>Strategy & Transactions:</strong> Fokuserar på att skapa långsiktigt värde genom företagsstrategi, transaktioner, värderingar och investeringar. Du stödjer företag i att fatta rätt beslut vid tillväxt, omstrukturering eller köp/försäljning av bolag.</li><br>
        <br><li><strong>Tax & Law:</strong> Ger företag kvalificerad rådgivning inom skatt, moms, juridik och regelefterlevnad. Du hjälper klienter att förstå och hantera komplexa regelverk globalt och strategiskt.</li>
      </ul>
      <br>
  <p style='font-size: 1.1em; margin-bottom: 10px;'>EY kompassen är ett verktyg för att du ska få en inblick i vad vi arbetar med samt för ta reda på egenskaper du besitter som passar in i våra affärsområden. Ditt resultat ska endast ses som en indikation på vart du möjligen hade passat in hos oss.</p>
      <br>
      <button onclick='startQuiz()'>Starta testet</button>
    </div>
    {% endif %}

    <div id='quizSection' style='display:none;'>
      <span style='font-size: 4rem; color: black;'>🧭</span>
      <h1>EY Kompassen</h1>
      <p>En fråga i taget – svara så noggrant du kan!</p>
      <div style='text-align:left;margin-bottom:5px;font-weight:bold;' id='questionCounter'></div>
      <div id='progressBar'><div id='progressBarFill'></div></div>
      <form id='quizForm' method='post'>
        <div id='quiz-container'>
          {% for i, question in questions.items() %}
          <div class='question' data-question-id='{{ i }}'>
            <h2>{{ question['text'] }}</h2>
            <select name='q{{ i }}'>
              <option value='' disabled selected hidden>Välj ditt svar</option>
              {% for option in question['options'] %}
              <option value='{{ option['value'] }}'>{{ option['label'] }}</option>
              {% endfor %}
            </select>
          </div>
          {% endfor %}
        </div>
        <div id="warningMessage">Välj ett svarsalternativ innan du kan gå vidare till nästa</div>
        <div>
          <button type='button' onclick='prevQuestion()' id='prevBtn' style='display:none;'>Föregående</button>
          <button type='button' onclick='nextQuestion()' id='nextBtn'>Nästa</button>
          <button type='button' onclick='submitQuiz()' id='submitBtn' style='display:none;'>Se resultat</button>
        </div>
        <div style='text-align:center;'>
          <button onclick='window.location.href="/"'>Gör testet igen</button>
        </div>
      </form>
    </div>
    {% if result %}
    <div class='result'>
      <h2>Du matchar mest med: {{ top_match }}</h2>
      <div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 8px;'>
        {% for item in result.split() %}
          {% if ':' in item %}
            {% set label, value = item.split(':') %}
            <span style="padding: 6px 10px; border-radius: 8px; color: white; background-color:
              {% if label.lower() == 'strategy' %}rgba(255, 99, 132, 0.9)
              {% elif label.lower() == 'consulting' %}rgba(54, 162, 235, 0.9)
              {% elif label.lower() == 'assurance' %}rgba(255, 206, 86, 0.9)
              {% elif label.lower() == 'tax' %}rgba(75, 192, 192, 0.9)
              {% else %}gray{% endif %};">
              {% if label == 'strategy' %}Strategy & Transactions{% elif label == 'tax' %}Tax & Law{% else %}{{ label }}{% endif %}: {{ value }}%
            </span>
          {% endif %}
        {% endfor %}
      </div>
      <canvas id='resultChart' width='160' height='160' style='display:block; margin: 20px auto;'></canvas>
      <div style='margin-top: 30px; text-align: left;'>
  {% set descriptions = {
    'strategy': "<strong>Strategy & Transactions:</strong> Du är analytisk, målinriktad och gillar att tänka långsiktigt. Strategy inom EY fokuserar på att hjälpa företag fatta viktiga affärsbeslut och utforma framtidsstrategier. Du kan komma att arbeta med företagsförvärv, affärsmodeller, marknadsanalyser eller transformationsprojekt på hög nivå.",
    'consulting': "<strong>Consulting:</strong> Du är kommunikativ, kreativ och gillar variation. Consulting innebär att hjälpa organisationer förbättra sin verksamhet, ofta genom digitalisering, förändringsledning eller processoptimering. Du samarbetar nära kunder och driver förändring inom områden som teknik, HR, ekonomi eller hållbarhet.",
    'assurance': "<strong>Assurance:</strong> Du är noggrann, strukturerad och gillar att saker blir rätt. Inom Assurance arbetar du ofta med revision och kvalitetssäkring av finansiell information. Du hjälper företag skapa förtroende genom att granska årsredovisningar, interna kontroller och säkerställa att allt följer lagar och regler.",
    'tax': "<strong>Tax & Law:</strong> Du är detaljfokuserad, systematisk och gillar att förstå regler och lagar. Tax innebär att hjälpa företag och privatpersoner navigera i skattesystemet. Du kan arbeta med nationell och internationell beskattning, moms, transaktioner eller hållbar skattekonsultation i en ständigt föränderlig omvärld."
  } %}
  {% for item in result.split() %}
    {% set label = item.split(':')[0].lower() %}
    {% if label in descriptions %}
      <div style="padding: 12px; margin-bottom: 12px; border-radius: 8px; color: white; background-color:
        {% if label == 'strategy' %}rgba(255, 99, 132, 0.9)
        {% elif label == 'consulting' %}rgba(54, 162, 235, 0.9)
        {% elif label == 'assurance' %}rgba(255, 206, 86, 0.9)
        {% elif label == 'tax' %}rgba(75, 192, 192, 0.9)
        {% else %}gray{% endif %};">
  {{ descriptions[label]|safe }}
</div>
    {% endif %}
  {% endfor %}
</div>
      <br>
      <button onclick='window.location.href="/"'>Gör testet igen</button>
    </div>
    <script>
      const data = {{ chart_data | safe }};
      const ctx = document.getElementById('resultChart').getContext('2d');
      new Chart(ctx, {
        type: 'pie',
        data: {
          labels: Object.keys(data),
          datasets: [{
            data: Object.values(data),
            backgroundColor: [
              'rgba(255, 99, 132, 0.9)',
              'rgba(54, 162, 235, 0.9)',
              'rgba(255, 206, 86, 0.9)',
              'rgba(75, 192, 192, 0.9)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false }
          }
        }
      });
    </script>
    {% endif %}
  </div>
  <script>
    function startQuiz() {
      document.getElementById('intro').style.display = 'none';
      document.getElementById('quizSection').style.display = 'block';
      updateView();
    }
    let currentQuestion = 0;
    const questions = document.querySelectorAll('#quiz-container .question');
    const nextButton = document.getElementById('nextBtn');
    const prevButton = document.getElementById('prevBtn');
    const submitButton = document.getElementById('submitBtn');
    const progressFill = document.getElementById('progressBarFill');
    questions.forEach(q => {
      const select = q.querySelector('select');
      select.addEventListener('change', () => {
              document.getElementById('warningMessage').style.display = 'none';
      });
    });
    function updateView() {
      questions.forEach((q, i) => {
        q.classList.remove('active');
        q.style.display = 'none';
        if (i === currentQuestion) {
          q.style.display = 'block';
          setTimeout(() => q.classList.add('active'), 10);
        }
      });
      prevButton.style.display = currentQuestion > 0 ? 'inline-block' : 'none';
      nextButton.style.display = currentQuestion < questions.length - 1 ? 'inline-block' : 'none';
      submitButton.style.display = currentQuestion === questions.length - 1 ? 'inline-block' : 'none';
      progressFill.style.width = ((currentQuestion + 1) / questions.length * 100) + '%';
      document.getElementById('questionCounter').innerText = `Fråga ${currentQuestion + 1} av ${questions.length}`;
    }
    function nextQuestion() {
      const currentSelect = questions[currentQuestion].querySelector('select');
      const warning = document.getElementById('warningMessage');
      if (!currentSelect.value) {
        warning.style.display = 'block';
        return;
      }
      warning.style.display = 'none';
      if (currentQuestion < questions.length - 1) {
        currentQuestion++;
        updateView();
      }
    }
    function prevQuestion() {
      if (currentQuestion > 0) {
        currentQuestion--;
        updateView();
      }
    }
    function submitQuiz() {
      const currentSelect = questions[currentQuestion].querySelector('select');
      const warning = document.getElementById('warningMessage');
      if (!currentSelect.value) {
        warning.style.display = 'block';
        return;
      }
      warning.style.display = 'none';
      document.getElementById('quizForm').submit();
    }
  </script>
</body>
</html>
"""

questions = {
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
        {"label": "Jag tycker om att ha inflytande och vara med i beslutsfattning", "value": "strategy:3"},
    ]},
    1: {"text": "Hur hanterar du helst nya situationer?", "options": [
        {"label": "Jag gillar att ta ett steg tillbaka och få överblick först", "value": "strategy:2,consulting:1"},
        {"label": "Jag tar itu med detaljerna först", "value": "assurance:2,tax:1"},
        {"label": "Jag brainstormar med andra och söker kreativa lösningar", "value": "consulting:2,strategy:1"},
        {"label": "Jag gillar när det finns tydliga instruktioner och ramar att följa", "value": "tax:2,assurance:1"},
    ]},
    2: {"text": "Vilken typ av projekt låter mest intressant?", "options": [
        {"label": "Förbättra och utveckla befintliga processer och system", "value": "consulting:2,assurance:1"},
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
        {"label": "Jag söker gärna stöd hos andra och följer riktlinjer", "value": "tax:2,assurance:1"},
    ]},
    7: {"text": "Vad tycker du är roligast att arbeta med?", "options": [
        {"label": "Att analysera och försöka kluriga problem", "value": "strategy:3"},
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

    return render_template_string(html_template, result=result, questions=questions, chart_data=chart_data, top_match=top_match)

if __name__ == "__main__":
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    url = f"http://127.0.0.1:{port}"
    print(f"✅ EY Kompassen körs nu på: {url}")

    def open_browser():
        time.sleep(3)
        webbrowser.open(url)

    threading.Thread(target=open_browser).start()
    app.run(debug=False, port=port)




