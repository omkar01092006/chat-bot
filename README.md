# 🌙 Serenity — Mental Health & Mood Tracker Chatbot

A Flask-powered mood companion with a night-sky aurora aesthetic.

## Features
- 😊 Log 10 moods with one click (happy, calm, anxious, sad, etc.)
- 💡 Tailored coping strategies per mood (3 per mood × 10 moods)
- 📊 Session mood summary with visual bar chart
- 🫁 Interactive guided box breathing exercise (4 rounds)
- ✨ Rotating affirmations
- 📋 Live sidebar mood log with timestamps
- 🌟 Animated starfield + aurora background

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open in browser
http://localhost:5001
```

## Example Interactions
- Click a mood chip → instant personalised response + strategies
- `"I feel anxious"` → logs anxious, gives breathing + coping tips
- `"Coping strategies"` → full strategy cards for your last mood
- `"Show my mood log"` → summary with visual mood bar chart
- `"Breathing exercise"` → animated 4-round box breathing timer
- `"Give me an affirmation"` → rotating motivational quote

## Moods Supported
Happy · Calm · Neutral · Grateful · Excited · Anxious · Sad · Stressed · Tired · Angry
