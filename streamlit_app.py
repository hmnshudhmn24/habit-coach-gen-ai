# streamlit_app.py
import streamlit as st
import base64
from src.config import OPENAI_API_KEY, MODEL_DEVICE
from src.image_model import classify_image_bytes, map_labels_to_food, load_model
from src.nutrition import estimate_calories
from src import db
from src.llm import chat_with_coach
import io

# initialize DB
db.init_db()

st.set_page_config(page_title="AI Habit Coach (gen-ai)", page_icon="💪🍽️", layout="wide")
st.title("💪 AI Habit Coach — Photo → Nutrition + Habit Coaching")

st.sidebar.header("Your coach settings")
model_device = st.sidebar.selectbox("Model device", options=["cpu", "cuda"], index=0)
portion_grams = st.sidebar.slider("Default portion (grams)", min_value=50, max_value=800, value=200, step=50)

# two-column layout: left = image & meal, right = habit tracker + chat
col1, col2 = st.columns([2,1])

with col1:
    st.header("📸 Snap a meal (or upload a photo)")
    uploaded = st.file_uploader("Upload meal photo", type=["jpg","jpeg","png"])
    if uploaded:
        img_bytes = uploaded.read()
        st.image(img_bytes, use_column_width=True)
        st.info("Classifying meal...")
        # Ensure model loaded on selected device
        load_model(model_device)
        preds = classify_image_bytes(img_bytes, device=model_device, topk=5)
        food_info = map_labels_to_food(preds)
        st.markdown(f"**Detected:** {food_info['food']} (confidence {food_info['confidence']:.2f})")
        grams = st.number_input("Portion size (grams)", value=portion_grams)
        estimate = estimate_calories(food_info["food"], grams, food_info["kcal_per_100g"])
        st.markdown("### 🔢 Estimated nutrition")
        st.write(estimate)
        note = st.text_area("Add a note (optional)", value="")
        if st.button("✅ Log meal"):
            db.log_meal(food=food_info["food"], grams=grams, kcal=estimate["kcal"],
                        carbs_g=estimate["carbs_g"], protein_g=estimate["protein_g"],
                        fat_g=estimate["fat_g"], source="image_estimate", note=note)
            st.success("Meal logged ✅")

    st.markdown("---")
    st.header("🧾 Recent meals")
    meals = db.recent_meals(10)
    if meals:
        for m in meals:
            st.write(f"- {m['timestamp']}: **{m['food']}** — {m['kcal']} kcal ({m['grams']} g). Note: {m.get('note','')}")
    else:
        st.write("No meals logged yet.")

with col2:
    st.header("🎯 Habit Tracker")
    st.subheader("Add habit")
    new_habit = st.text_input("Habit name", "")
    if st.button("➕ Add habit"):
        if new_habit.strip():
            db.add_habit(new_habit.strip())
            st.success("Habit added!")
    st.subheader("Your habits")
    habits = db.list_habits()
    for h in habits:
        st.write(f"- [{h['id']}] {h['name']}")
        if st.button(f"Mark done ({h['id']})", key=f"done_{h['id']}"):
            db.log_habit(habit_id=h["id"], note="checked via UI")
            st.success(f"Logged {h['name']}")

    st.markdown("---")
    st.header("💬 Chat with Coach")
    # simple conversation state in session
    if "convo" not in st.session_state:
        st.session_state.convo = []
    for msg in st.session_state.convo:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Coach:** {content}")

    user_input = st.text_input("Say something to your coach (e.g., 'I ate a lot of pizza today — help me stay motivated')", key="user_input")
    if st.button("Send"):
        if user_input.strip():
            st.session_state.convo.append({"role": "user", "content": user_input})
            resp = chat_with_coach([{"role":"user","content": user_input}])
            text = resp.get("text", "No response — check API key.")
            st.session_state.convo.append({"role": "assistant", "content": text})
            st.experimental_rerun()

    st.markdown("---")
    st.header("📈 Progress & Logs")
    logs = db.recent_habit_logs(20)
    if logs:
        for l in logs:
            st.write(f"- {l['timestamp']}: habit_id={l['habit_id']} note={l.get('note','')}")
    else:
        st.write("No habit logs yet.")
