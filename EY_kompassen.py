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
      background-color: #000000;
      color: white;
      margin: 0;
      padding: 0;
    }
    .container {
      max-width: 800px;
      margin: 20px auto;
      background: #2E2E38;
      color: white;
      padding: 20px;
      border-radius: 16px;
      box-shadow: 0 10px 20px rgba(0,0,0,0.1);
      text-align: center;
    }
    h1 {
      color: #FFE600;
    }
    h2 {
      color: white;
      margin-bottom: 6px;
    }
    h3, p, li, label, select, option, span {
      color: white;
    }
    .question {
      margin-bottom: 30px;
      background-color: #2E2E38;
      padding: 20px;
      border-radius: 12px;
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
      background-color: #2E2E38;
      color: white;
      border: 1px solid #fff;
    }
    button {
      background-color: #FFE600;
      color: black;
      padding: 12px 20px;
      font-size: 1em;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      margin: 20px 10px 0 10px;
      transition: background-color 0.2s ease-in-out;
    }
    button:hover {
      background-color: #FFF2AF;
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
      background-color: #FFE600;
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
  <h1>The EY compass</h1>
  <p>Shape your future with confidence!</p>
  <p style='font-size: 1.1em; margin-bottom: 10px;'>EY (Ernst & Young) is one of the worlds biggest auditing and consulting firms with services in over 150 countries. Here at EY we help companies, organizations and the public sector to grow, streamline and manage change in a responsible and sustainable way. EY:s purpoose is "building a better working world" by creating long-term value for customers, employees and society.</p>
      <p style='font-size: 1.1em; margin-bottom: 10px;'>With us you can work in one of these business areas:</p>
      <br>
       <ul style='list-style: none; padding: 0; font-size: 1em; text-align: left; max-width: 600px; margin: 0 auto;'>
        <br><li><strong>Assurance:</strong> Ensures that companies report accurate and transparent information to the outside world. It involves auditing, sustainability reviews and providing advice that builds trust in the market. You can work in accounting, auditing or as a payroll consultant.</li><br>
        <br><li><strong>Consulting:</strong> Working to help businesses evolve through innovation, transformation and digitalization. You'll combine technology, strategy and human perspectives to fundamentally improve clients' businesses. You can work as a consultant in business, tech or cyber security.</li><br>
        <br><li><strong>EY-Parthenon:</strong> Focus on creating long-term value through corporate strategy, transactions, valuations and investments. You support companies in making the right decisions when growing, restructuring or buying/selling companies. You can work as an analyst or consultant.</li><br>
        <br><li><strong>Tax & Law:</strong> Provides businesses with expert tax, VAT, legal and compliance advice. You will help clients understand and manage complex regulations globally and strategically. You can work as a tax consultant or business lawyer.</li>
      </ul>
      <br>
  <p style='font-size: 1.1em; margin-bottom: 10px;'>The EY compass is a tool to help you get an insight into what we work with and to find out what business area your characteristics would be a great fit for. Your result schould only be seen as an indication where you could be the best fit, its not foolproof.</p>
      <br>
      <button onclick='startQuiz()'>Start test</button>
    </div>
    {% endif %}

    <div id='quizSection' style='display:none;'>
      <span style='font-size: 4rem; color: black;'>🧭</span>
      <h1>The EY compass</h1>
      <p>Shape your future with confidence!</p>
      <div style='text-align:left;margin-bottom:5px;font-weight:bold;' id='questionCounter'></div>
      <div id='progressBar'><div id='progressBarFill'></div></div>
      <form id='quizForm' method='post'>
        <div id='quiz-container'>
          {% for i, question in questions.items() %}
          <div class='question' data-question-id='{{ i }}'>
            <h2>{{ question['text'] }}</h2>
            <select name='q{{ i }}'>
              <option value='' disabled selected hidden>Choose your answer</option>
              {% for option in question['options'] %}
              <option value='{{ option['value'] }}'>{{ option['label'] }}</option>
              {% endfor %}
            </select>
          </div>
          {% endfor %}
        </div>
        <div id="warningMessage">Choose an answer option before you can proceed</div>
        <div>
          <button type='button' onclick='prevQuestion()' id='prevBtn' style='display:none;'>Previous</button>
          <button type='button' onclick='nextQuestion()' id='nextBtn'>Next</button>
          <button type='button' onclick='submitQuiz()' id='submitBtn' style='display:none;'>See result</button>
        </div>
        <div style='text-align:center;'>
          <button onclick='window.location.href="/"'>Redo the test</button>
        </div>
      </form>
    </div>
    {% if result %}
    <div class='result'>
      <span style='font-size: 4rem; color: black;'>🧭</span>
      <h1>The EY compass</h1>
      <p>Shape your future with confidence!</p>
      <h2>Your best match is: {{ top_match }}</h2>
      <div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 8px;'>
        {% for item in result.split() %}
          {% if ':' in item %}
            {% set label, value = item.split(':') %}
            <span style="padding: 6px 10px; border-radius: 8px; color: white; background-color:
              {% if label.lower() == 'strategy' %}rgb(45, 183, 87)
              {% elif label.lower() == 'consulting' %}rgb(24, 140, 229)
              {% elif label.lower() == 'assurance' %}rgb(117, 14, 92)
              {% elif label.lower() == 'tax' %}rgb(114, 75, 195)
              {% else %}gray{% endif %};">
              {% if label == 'strategy' %}EY-Parthenon{% elif label == 'tax' %}Tax & Law{% elif label == 'assurance' %}Assurance{% elif label == 'consulting' %}Consulting{% else %}{{ label }}{% endif %}: {{ value }}%
            </span>
          {% endif %}
        {% endfor %}
      </div>
      <canvas id='resultChart' width='160' height='160' style='display:block; margin: 20px auto;'></canvas>
      <div style='margin-top: 30px; text-align: left;'>
  {% set descriptions = {
    'strategy': "<strong>EY-Parthenon:</strong> You are analytical, goal-orientated and like to think long-term. Strategy at EY focuses on helping companies make key business decisions and shape future strategies. You may work on acquisitions, business models, market analyses or high-level transformation projects.",
    'consulting': "<strong>Consulting:</strong> You are communicative, creative and like variety. Consulting means helping organisations improve their business, often through digitalisation, change management or process optimisation. You work closely with clients and drive change in areas such as technology, HR, finance or sustainability.",
    'assurance': "<strong>Assurance:</strong> You are accurate, structured and like to get things right. In Assurance, you often work on auditing and quality assurance of financial information. You help companies build trust by reviewing annual reports, internal controls and ensuring compliance with laws and regulations.",
    'tax': "<strong>Tax & Law:</strong> You are detail-orientated, systematic and like to understand rules and laws. Tax involves helping businesses and individuals navigate the tax system. You may work on national and international taxation, VAT, transactions or sustainable tax consulting in an ever-changing world."
  } %}
  {% for item in result.split() %}
    {% set label = item.split(':')[0].lower() %}
    {% if label in descriptions %}
      <div style="padding: 12px; margin-bottom: 12px; border-radius: 8px; color: white; background-color:
        {% if label == 'strategy' %}rgb(45, 183, 87)
        {% elif label == 'consulting' %}rgb(24, 140, 229)
        {% elif label == 'assurance' %}rgb(117, 14, 92)
        {% elif label == 'tax' %}rgb(114, 75, 195)
        {% else %}gray{% endif %};">
  {{ descriptions[label]|safe }}
</div>
    {% endif %}
  {% endfor %}
</div>
      <br>
      <button onclick='window.location.href="/"'>Re-do the test</button>
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
              'rgb(45, 183, 87)',
              'rgb(24, 140, 229)',
              'rgb(117, 14, 92)',
              'rgb(114, 75, 195)'
            ],
            borderColor: [
              'rgb(45, 183, 87)',
              'rgb(24, 140, 229)',
              'rgb(117, 14, 92)',
              'rgb(114, 75, 195)'
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
      document.getElementById('questionCounter').innerText = `Question ${currentQuestion + 1} av ${questions.length}`;
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
    6: {"text": "What work enviroment do you enjoy the most?", "options": [
        {"label": "An organised and predictable working enviroment", "value": "assurance:2,tax:2"},
        {"label": "A fast paced enviroment with new ideas and variation", "value": "consulting:2,strategy:1"},
        {"label": "An enviroment where long-term thinking and logic is important", "value": "strategy:2,consulting:1"},
        {"label": "An enviroment where precision and corectness is in focus", "value": "assurance:3"},
    ]},
    5: {"text": "What type of cooperation do you prefer?", "options": [
        {"label": "I prefer to work in small teams with clear roles", "value": "tax:2,assurance:1"},
        {"label": "I like to work with different people and together figure out solutions", "value": "consulting:2,strategy:1"},
        {"label": "I prefer to work independently and take responsibility for my parts", "value": "assurance:2"},
        {"label": "I like to make an impact and be part of making decisions", "value": "strategy:3"},
    ]},
    2: {"text": "How do you prefer to handle new situations?", "options": [
        {"label": "I like to take a step back and firstly look at the bigger picture", "value": "strategy:2,consulting:1"},
        {"label": "I'll deal with the details first", "value": "assurance:2,tax:1"},
        {"label": "I brainstorm with others and to seek creative solutions", "value": "consulting:2,strategy:1"},
        {"label": "I like when there are clear instructions and frameworks to follow", "value": "tax:2,assurance:1"},
    ]},
    7: {"text": "Which of these projects intrests you the most?", "options": [
        {"label": "lägg till projekt CONSULTING", "value": "consulting:2,assurance:1"},
        {"label": "lägg till projekt EY-P", "value": "strategy:3"},
        {"label": "lägg till projekt TAX", "value": "tax:2,assurance:1"},
        {"label": "lägg till projekt ASSURANCE", "value": "assurance:3"},
    ]},
    4: {"text": "How do you best decribe your workstyle?", "options": [
        {"label": "Logical, structured and responsible", "value": "assurance:2,tax:1"},
        {"label": "Creative, communicative and open to change", "value": "consulting:2,strategy:1"},
        {"label": "Target-oriented, analytical och holistic", "value": "strategy:2,consulting:1"},
        {"label": "Precise, systematical and detaljrerad", "value": "tax:2,assurance:1"},
    ]},
    1: {"text": "What do/did you study at university?", "options": [
        {"label": "Data or IT", "value": "consulting:1,strategy:1,assurance:1,tax:1"},
        {"label": "Economics, Business and/or Management", "value": "consulting:1,strategy:1,assurance:1,tax:1"},
        {"label": "Engineering or Tech", "value": "consulting:1,strategy:1,assurance:1,tax:1"},
        {"label": "Other", "value": "consulting:1,strategy:1,assurance:1,tax:1"},
    ]},
    3: {"text": "How do you deal with uncertainty?", "options": [
        {"label": "I like to create structure in complex situations", "value": "assurance:2,tax:1"},
        {"label": "I like being creative when the situation is unclear", "value": "strategy:2,consulting:1"},
        {"label": "I try to understand the bigger picture and plan accordingly", "value": "strategy:2"},
        {"label": "I seek support from others and follow guidelines", "value": "tax:2,assurance:1"},
    ]},
    9: {"text": "What do you enjoy working on most?", "options": [
        {"label": "To analyze and try solving complicated problems", "value": "strategy:3"},
        {"label": "To develop digital or technical solutions", "value": "consulting:2,strategy:1"},
        {"label": "Analysing data to ensure accuracy", "value": "assurance:3"},
        {"label": "To go in depth and understand important documents or agreements", "value": "tax:3"},
    ]},
    8: {"text": "How do you want your workrole to impact others?", "options": [
        {"label": "Bringing clarity and reliability to figures and reports", "value": "assurance:2"},
        {"label": "Help make complex and hard decisions easier to understand and to make", "value": "strategy:2,consulting:1"},
        {"label": "Help organisations and companies develop and grow", "value": "consulting:2,strategy:1"},
        {"label": "Helping to ensure that everything works properly in everyday life", "value": "tax:2,assurance:1"},
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
