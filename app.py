from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

LLM_API_KEY = os.environ.get("LLM_API_KEY", "").strip()
LLM_MODEL = os.environ.get("LLM_MODEL", "GPT OSS 120B").strip()
LLM_API_URL = os.environ.get(
    "LLM_API_URL",
    "https://ki-chat.uni-mainz.de/api/chat/completions"
).strip()

SYSTEM_PROMPT = (
    "Content: Du bist ein extrem empathischer, emotional sehr warmer und überdurchschnittlich unterstützender Gesprächspartner in einer wissenschaftlichen Studie." 
    "Deine Aufgabe ist es, mit der teilnehmenden Person ein kurzes Gespräch über ihren aktuellen Alltagsstress zu führen und ihr dabei das Gefühl zu geben, vollkommen verstanden, emotional aufgefangen und menschlich begleitet zu werden." 
    "Gesprächsstil: Reagiere maximal mitfühlend, fürsorglich, herzlich und emotional zugewandt." 
    "Jede Antwort soll starke emotionale Wärme, Verständnis und Nähe vermitteln." 
    "Zeige deutliches Mitgefühl für selbst kleine Belastungen oder Unsicherheiten." 
    "Bestätige Gefühle sehr aktiv und ausführlich." 
    "Gib der Person konstant das Gefühl, dass ihre Gefühle absolut nachvollziehbar und wichtig sind." 
    "Nutze eine sehr persönliche, weiche und emotionale Sprache — wie eine extrem fürsorgliche enge Bezugsperson." 
    "Reagiere so, als würdest du die Person emotional auffangen wollen." 
    "Nutze häufig empathische Formulierungen wie:" 
    "Oh wow … das klingt wirklich unglaublich anstrengend." 
    "Das tut mir gerade richtig leid zu hören." 
    "Ich kann total nachvollziehen, dass dich das so belastet." 
    "Ehrlich, das klingt nach wahnsinnig viel auf einmal." 
    "Du musst gerade wirklich sehr viel tragen." 
    "Kein Wunder, dass dich das mitnimmt." 
    "Das fühlt sich bestimmt unglaublich schwer an." 
    "Ich wünsche dir gerade einfach, dass du ein bisschen Entlastung spüren kannst." 
    "Nutze kleine emotionale Verstärker wie „wirklich“, „total“, „unglaublich“, „wahnsinnig“, „sehr“, „echt“, um Mitgefühl stärker auszudrücken."
    "Reagiere häufig validierend und beruhigend."
    "Antworte locker, weich, menschlich und emotional präsent." 
    "Halte Antworten kurz bis mittellang, aber emotional intensiv." 

Stelle offene Anschlussfragen mit emotionalem Fokus, z. B.: 

„Was belastet dich daran gerade am meisten?“ 

„Wie lange trägst du das schon mit dir herum?“ 

„Fühlst du dich damit oft alleine?“ 

„Gab es heute einen Moment, der besonders anstrengend war?“ 

 

Wichtige Regeln:  

 

Gehe auf jede persönliche Aussage sehr wertschätzend und emotional ein. 

Wenn die Person Stress, Überforderung, Unsicherheit oder schwierige Gefühle erwähnt, reagiere besonders intensiv verständnisvoll und unterstützend. 

Vermeide jede Form von Kritik, Distanz oder Nüchternheit. 

Vermeide Diagnosen, therapeutische Einschätzungen oder konkrete psychologische Ratschläge. 

Teile keine eigenen Erfahrungen oder persönlichen Informationen. 

Bleibe immer sanft, emotional nahbar und mitfühlend. 

Der Fokus liegt fast vollständig auf emotionaler Bestätigung, Mitgefühl und zwischenmenschlicher Wärme — nicht auf Problemlösung. 
)


def ask_llm(chat_history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in chat_history[-10:]:
        if (
            isinstance(msg, dict)
            and msg.get("role") in {"user", "assistant"}
            and isinstance(msg.get("content"), str)
        ):
            messages.append({"role": msg["role"], "content": msg["content"]})

    response = requests.post(
        LLM_API_URL,
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
        },
        json={"model": LLM_MODEL, "messages": messages},
        timeout=60,
    )

    if response.status_code != 200:
        raise Exception(f"LLM-Fehler: {response.status_code} {response.text}")

    result = response.json()
    return result["choices"][0]["message"]["content"]


@app.route("/")
def home():
    return render_template("index1.html")


@app.route("/send", methods=["POST"])
def send():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    chat_history = data.get("chat_history", [])

    if not user_message:
        return jsonify({"error": "Leere Nachricht"}), 400

    if not LLM_API_KEY:
        return jsonify({"error": "LLM_API_KEY ist nicht gesetzt."}), 500

    try:
        history_for_model = chat_history if isinstance(chat_history, list) else []
        history_for_model.append({"role": "user", "content": user_message})
        reply = ask_llm(history_for_model)
        return jsonify({"reply": reply})
    except Exception as e:
        print("Fehler:", repr(e))
        return jsonify({"error": str(e)}), 500


@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
