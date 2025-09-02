# 💪 AI Habit Coach (Multi-Modal) — gen-ai

An interactive habit coach that can:
- 📸 Take a photo of your meal → estimate calories & simple macro breakdown
- 🗓️ Track daily habits (add/mark done) and display progress
- 🤖 Chat with a supportive AI coach (LLM) for motivation and quick advice
- 🧾 Persist logs in SQLite for simple tracking and export

This is a **prototype** combining a lightweight image classifier + nutrition heuristics + LLM coaching. The goal is a usable, local-first demo you can extend.



## ✨ Features

- Meal photo upload → image-based food detection (ImageNet-based prototype)  
- Heuristic calorie estimate with grams → calories & macros returned  
- Habit tracker: add habits, mark done, view recent logs  
- Chat coach powered by OpenAI (requires `OPENAI_API_KEY`)  
- Everything stored in a local SQLite DB (`./data/habits.db`)



## 🧰 Tech stack

- Streamlit UI  
- PyTorch + torchvision (pretrained ImageNet model for prototype detection)  
- OpenAI Chat for coach dialogue (configurable via `.env`)  
- SQLite (SQLAlchemy) for persistence  
- Python with small helper modules for nutrition & DB



## ⚙️ Installation

1. Clone:
```bash
git clone https://github.com/yourname/ai-habit-coach-gen-ai.git
cd ai-habit-coach-gen-ai
```

2. Create virtual environment & install:
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# edit .env: add OPENAI_API_KEY, DB_PATH (optional), MODEL_DEVICE
```

4. Run:
```bash
streamlit run streamlit_app.py
```

Open the Streamlit URL (usually `http://localhost:8501`).



## 🧭 How it works (overview)

1. **Image pipeline** — The app accepts a meal photo and runs a pretrained ImageNet model (mobilenet_v3) for a *prototype* label. We map common ImageNet labels to food items via a heuristic table and then estimate calories per 100g using a small heuristic table.

2. **Nutrition estimate** — Given the chosen portion grams (default 200g), the `nutrition` helper scales calories and estimates macros (carbs/protein/fat) using simple ratios. These are approximate.

3. **Habit tracking** — uses SQLite to persist habits, habit logs, and meal logs. Easy to query or export for further analysis.

4. **LLM coach** — chat interface sends messages to OpenAI ChatCompletion API with a "supportive coach" system prompt. The coach provides motivational, actionable responses.



## ✅ Caveats & limitations

- **Food recognition is a prototype**: ImageNet-based outputs are not food-specialized. For accurate food recognition use a dedicated model (Food101, CLIP-zero-shot with food prompts, or a fine-tuned model / cloud API).
- **Nutritional numbers are heuristic** — not medical grade. Use only for rough tracking.
- **OpenAI usage**: Chat calls go to OpenAI and incur costs. Do not send PII.
- **Portion estimation**: the app assumes user-input grams; automatic portion size estimation from an image is a separate advanced task (requires depth/size reference).



## 🔮 Next steps / improvements

- Integrate a **real food classifier** (Food101, Google Vision, or fine-tuned CLIP)
- Automatic portion-size estimation (use reference object or depth sensors)
- Better nutrient database (USDA FoodData Central API) → precise macros & micronutrients
- Personalization: user profiles, daily calorie goals, streaks & reminders
- Offline LLMs for coaching (if privacy is required)



## 🔒 Privacy & ethics

- Photos and logs are stored locally (SQLite). If deploying, ensure secure storage & opt-in.
- Be transparent: this is a *coaching* tool, not a medical or nutritionist substitute.
- Respect user privacy and do not send sensitive images or data to third-party APIs unless consented.

