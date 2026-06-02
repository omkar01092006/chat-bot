from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "serene-mind-secret-2024"

# ── Mood Data ─────────────────────────────────────────────────────────────────
MOODS = {
    "happy":    {"emoji": "😊", "color": "#FFD166", "level": 5, "label": "Happy"},
    "calm":     {"emoji": "😌", "color": "#06D6A0", "level": 4, "label": "Calm"},
    "neutral":  {"emoji": "😐", "color": "#A0C4FF", "level": 3, "label": "Neutral"},
    "anxious":  {"emoji": "😰", "color": "#FF9F1C", "level": 2, "label": "Anxious"},
    "sad":      {"emoji": "😢", "color": "#6B9FD4", "level": 2, "label": "Sad"},
    "stressed": {"emoji": "😤", "color": "#FF6B6B", "level": 2, "label": "Stressed"},
    "tired":    {"emoji": "😴", "color": "#B8A9C9", "level": 2, "label": "Tired"},
    "angry":    {"emoji": "😠", "color": "#EF476F", "level": 1, "label": "Angry"},
    "grateful": {"emoji": "🙏", "color": "#80ED99", "level": 5, "label": "Grateful"},
    "excited":  {"emoji": "🤩", "color": "#F7B731", "level": 5, "label": "Excited"},
}

# ── Coping Strategies ─────────────────────────────────────────────────────────
STRATEGIES = {
    "anxious": [
        {"title": "Box Breathing", "emoji": "🫁",
         "desc": "Inhale for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat 4 times. This activates your parasympathetic nervous system."},
        {"title": "5-4-3-2-1 Grounding", "emoji": "🌿",
         "desc": "Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. Anchors you to the present moment."},
        {"title": "Progressive Muscle Relaxation", "emoji": "💪",
         "desc": "Starting from your toes, tense each muscle group for 5 seconds then release. Work up to your face. Releases physical tension."},
    ],
    "sad": [
        {"title": "Gentle Movement", "emoji": "🚶",
         "desc": "A 10-minute walk outside can shift your mood. You don't need a workout — just gentle movement and fresh air."},
        {"title": "Reach Out", "emoji": "💬",
         "desc": "Text or call someone you trust. You don't have to share everything — even a lighthearted chat helps you feel less alone."},
        {"title": "Comfort Ritual", "emoji": "☕",
         "desc": "Make a warm drink, wrap yourself in a blanket, put on soft music. Being kind to your body helps your mind."},
    ],
    "stressed": [
        {"title": "Brain Dump", "emoji": "📝",
         "desc": "Write every worry down without filtering. Getting it out of your head and onto paper reduces mental load significantly."},
        {"title": "2-Minute Rule", "emoji": "⏱",
         "desc": "If something takes less than 2 minutes, do it now. Clear the small tasks and your stress load feels lighter."},
        {"title": "Mindful Pause", "emoji": "🧘",
         "desc": "Set a 5-minute timer. Sit still, breathe, and do nothing. This resets your nervous system like restarting a computer."},
    ],
    "angry": [
        {"title": "Cold Water Reset", "emoji": "💧",
         "desc": "Splash cold water on your face or hold ice in your hands. Cold temperature activates the dive reflex, slowing your heart rate."},
        {"title": "Physical Release", "emoji": "🏃",
         "desc": "Go for a run, do jumping jacks, or punch a pillow. Your body is primed for action — give it a safe outlet."},
        {"title": "Delay Response", "emoji": "⏳",
         "desc": "If reacting to a person or situation, wait 24 hours before responding. Anger fades; your words remain."},
    ],
    "tired": [
        {"title": "Power Nap Protocol", "emoji": "😴",
         "desc": "20 minutes is the sweet spot. Set an alarm, lie down (but don't fully sleep), and let your body drift. Any longer causes grogginess."},
        {"title": "Energy Snack", "emoji": "🍌",
         "desc": "Banana + a small handful of nuts gives you steady energy for 2–3 hours without a crash. Avoid sugar spikes."},
        {"title": "Hydration Check", "emoji": "💧",
         "desc": "Fatigue is the first sign of dehydration. Drink a full glass of water right now. Many people are chronically mildly dehydrated."},
    ],
    "happy": [
        {"title": "Savour This Moment", "emoji": "✨",
         "desc": "Take 60 seconds to consciously notice what's making you happy. Savouring actively strengthens positive neural pathways."},
        {"title": "Spread the Good", "emoji": "💌",
         "desc": "Send a short, genuine compliment or thank-you to someone. Sharing happiness multiplies it."},
        {"title": "Capture It", "emoji": "📓",
         "desc": "Write 3 specific things you're grateful for right now. Gratitude journalling extends positive moods."},
    ],
    "calm": [
        {"title": "Deepen the Calm", "emoji": "🌊",
         "desc": "You're in a great state for creative work, difficult conversations, or making important decisions. Use this window wisely."},
        {"title": "Mindful Moment", "emoji": "🌸",
         "desc": "Take a slow walk and notice every small detail around you — textures, sounds, light. Extend your calm with presence."},
        {"title": "Body Scan", "emoji": "🧘",
         "desc": "Sit quietly and mentally scan from head to toe, noticing any tension and consciously releasing it. Deepen your sense of ease."},
    ],
    "grateful": [
        {"title": "Gratitude Letter", "emoji": "💌",
         "desc": "Write a letter to someone who has positively impacted your life. You don't have to send it — the writing itself is powerful."},
        {"title": "Expand Your Circle", "emoji": "🌍",
         "desc": "When feeling grateful, it's a great time to volunteer or help someone. Your goodwill has extra reach right now."},
        {"title": "Capture the Feeling", "emoji": "📖",
         "desc": "Journal what's behind your gratitude today in detail. On harder days, reading this back is like sunlight on clouds."},
    ],
    "excited": [
        {"title": "Channel the Energy", "emoji": "🎯",
         "desc": "Excitement is fuel. Tackle your most challenging task while you have this momentum — it's easier than you think right now."},
        {"title": "Share It", "emoji": "🎉",
         "desc": "Tell someone what you're excited about. Articulating excitement makes it more real and strengthens social bonds."},
        {"title": "Protect the Energy", "emoji": "🛡",
         "desc": "Avoid doom-scrolling or draining conversations while you feel great. Guard this state — it's precious."},
    ],
    "neutral": [
        {"title": "Mood Boost Walk", "emoji": "🌤",
         "desc": "A 15-minute walk in natural light is clinically shown to improve mood, energy, and focus. It's the most underrated intervention."},
        {"title": "Creative Spark", "emoji": "🎨",
         "desc": "Neutral is a great state to create. Doodle, write, play music, or cook something. The act of making things energises."},
        {"title": "Intention Setting", "emoji": "🎯",
         "desc": "Set one small intention for the rest of your day. Even tiny goals give direction and a sense of meaning."},
    ],
}

AFFIRMATIONS = [
    "Every feeling you have is valid. You're doing better than you think. 💙",
    "It takes courage to check in with yourself. That matters.",
    "You don't have to have it all figured out. Just one moment at a time.",
    "Your feelings are messengers, not your identity. You get to choose what to do with them.",
    "Being kind to yourself is not selfish — it's essential.",
    "Small steps still move you forward. You're doing the work.",
    "Whatever you're feeling right now, it will shift. Feelings are always temporary.",
    "Checking in with yourself is an act of self-respect. Well done.",
]

FOLLOW_UPS = {
    5: "That's wonderful to hear. Savouring positive moments helps make them last longer. 🌟",
    4: "Being in a good place is worth acknowledging. You're doing well.",
    3: "Neutral days are totally normal. Sometimes steady is exactly what we need.",
    2: "I'm sorry you're going through this. You're not alone, and it won't always feel this way. 💙",
    1: "That sounds really hard. Please be gentle with yourself right now. You matter. 💙",
}


# ── Session Helper ────────────────────────────────────────────────────────────
def get_log():
    if "mood_log" not in session:
        session["mood_log"] = []
    return session["mood_log"]


def detect_mood(text):
    text_lower = text.lower()
    # Direct keyword map
    keyword_map = {
        "happy": ["happy", "great", "good", "wonderful", "fantastic", "joyful", "glad", "delighted"],
        "calm": ["calm", "relaxed", "peaceful", "serene", "chill", "at ease", "tranquil"],
        "neutral": ["okay", "ok", "fine", "neutral", "alright", "so-so", "meh", "average", "normal"],
        "anxious": ["anxious", "anxiety", "worried", "nervous", "panic", "scared", "fearful", "uneasy"],
        "sad": ["sad", "unhappy", "down", "depressed", "blue", "low", "gloomy", "miserable", "crying"],
        "stressed": ["stressed", "stress", "overwhelmed", "too much", "pressure", "busy", "swamped"],
        "tired": ["tired", "exhausted", "fatigue", "sleepy", "drained", "worn out", "no energy"],
        "angry": ["angry", "anger", "mad", "furious", "irritated", "annoyed", "frustrated", "rage"],
        "grateful": ["grateful", "thankful", "blessed", "appreciate", "gratitude"],
        "excited": ["excited", "thrilled", "pumped", "stoked", "eager", "can't wait", "energised", "energized"],
    }
    for mood, keywords in keyword_map.items():
        if any(k in text_lower for k in keywords):
            return mood
    return None


def build_summary(log):
    if not log:
        return None
    counts = {}
    for entry in log:
        m = entry["mood"]
        counts[m] = counts.get(m, 0) + 1
    dominant = max(counts, key=counts.get)
    total = len(log)
    avg_level = sum(MOODS[e["mood"]]["level"] for e in log) / total
    return {
        "total": total,
        "dominant": dominant,
        "dominant_info": MOODS[dominant],
        "avg_level": round(avg_level, 1),
        "counts": {m: {"count": c, "info": MOODS[m]} for m, c in counts.items()},
        "log": log,
    }


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").strip()
    intent = data.get("intent", "")

    if not user_msg and not intent:
        return jsonify({"error": "empty"}), 400

    log = get_log()
    response = handle_message(user_msg, intent, log)

    # Persist log changes
    session["mood_log"] = log
    session.modified = True

    return jsonify(response)


@app.route("/log", methods=["GET"])
def get_mood_log():
    return jsonify({"log": get_log()})


def handle_message(text, intent, log):
    text_lower = text.lower()

    # ── Greet ──
    if intent == "greet" or any(w in text_lower for w in ["hello", "hi", "hey", "start", "begin"]):
        return {
            "type": "greeting",
            "message": "Hello, and welcome. 🌙\n\nI'm Serenity, your personal mood companion. I'm here to help you check in with yourself, understand what you're feeling, and offer gentle support.\n\nHow are you feeling right now?"
        }

    # ── Log mood by intent ──
    if intent == "log_mood":
        mood_key = data_from_intent = text_lower.replace("log_mood:", "").strip()
        if mood_key in MOODS:
            return log_mood_response(mood_key, log)

    # ── View summary ──
    if intent == "summary" or any(w in text_lower for w in ["summary", "history", "log", "my moods", "track", "review"]):
        summary = build_summary(log)
        if not summary:
            return {"type": "text", "message": "You haven't logged any moods yet today. Tell me how you're feeling and we can start tracking! 🌱"}
        return {"type": "summary", "summary": summary}

    # ── Coping strategies ──
    if intent == "strategies" or any(w in text_lower for w in ["strategy", "strategies", "tips", "help me", "what should i do", "how to cope", "advice"]):
        # Use last logged mood or detect from text
        last_mood = log[-1]["mood"] if log else None
        detected = detect_mood(text) or last_mood or "neutral"
        strats = STRATEGIES.get(detected, STRATEGIES["neutral"])
        mood_info = MOODS[detected]
        return {
            "type": "strategies",
            "mood": detected,
            "mood_info": mood_info,
            "strategies": strats,
            "message": f"Here are some strategies for when you're feeling {mood_info['label'].lower()}:"
        }

    # ── Affirmation ──
    if intent == "affirm" or any(w in text_lower for w in ["affirmation", "inspire", "motivate", "encourage", "uplift"]):
        return {"type": "affirmation", "message": random.choice(AFFIRMATIONS)}

    # ── Detect mood from free text ──
    detected_mood = detect_mood(text)
    if detected_mood:
        return log_mood_response(detected_mood, log)

    # ── Breathing exercise ──
    if any(w in text_lower for w in ["breath", "breathe", "breathing", "relax", "calm down", "panic"]):
        return {
            "type": "breathing",
            "message": "Let's do a simple breathing exercise together. Follow along at your own pace. 🫁"
        }

    # ── Thank you / positive ──
    if any(w in text_lower for w in ["thank", "thanks", "helpful", "helped"]):
        return {"type": "text", "message": "I'm really glad I could help. Remember, checking in with yourself regularly is one of the most caring things you can do. I'm always here. 💙"}

    # ── Fallback ──
    return {
        "type": "prompt",
        "message": "I'd love to support you. You can:\n\n• Tell me how you're feeling (e.g. *'I feel anxious'*)\n• Ask for **coping strategies**\n• Check your **mood summary**\n• Try a **breathing exercise**\n\nWhat would help most right now?"
    }


def log_mood_response(mood_key, log):
    mood = MOODS[mood_key]
    entry = {
        "mood": mood_key,
        "emoji": mood["emoji"],
        "label": mood["label"],
        "level": mood["level"],
        "time": datetime.now().strftime("%I:%M %p"),
        "color": mood["color"],
    }
    log.append(entry)

    follow_up = FOLLOW_UPS.get(mood["level"], FOLLOW_UPS[3])
    strats = STRATEGIES.get(mood_key, STRATEGIES["neutral"])

    return {
        "type": "mood_logged",
        "entry": entry,
        "follow_up": follow_up,
        "strategies": strats[:2],
        "affirmation": random.choice(AFFIRMATIONS),
        "log_count": len(log),
    }


if __name__ == "__main__":
    app.run(debug=True, port=5001)
