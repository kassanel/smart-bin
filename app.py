import streamlit as st

from classifier import classify_waste
from database import add_waste, create_database, get_history, get_statistics

st.set_page_config(page_title="Smart Bin", page_icon="♻️", layout="centered")
create_database()

st.markdown("""
<style>
:root {
  --ink: #17332d;
  --muted: #667a72;
  --green: #247a55;
  --mint: #e5f4eb;
}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse at 8% 4%, rgba(198, 236, 216, .70), transparent 34%),
    radial-gradient(ellipse at 95% 18%, rgba(221, 237, 215, .65), transparent 30%),
    linear-gradient(160deg, #f5faf6 0%, #edf5ef 52%, #f8faf6 100%);
  color: var(--ink);
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.block-container { max-width: 900px; padding-top: 2.2rem; padding-bottom: 4rem; }
h1, h2, h3 { color: var(--ink); letter-spacing: -.025em; }
.hero {
  padding: 1.6rem 1.8rem 1.5rem;
  margin: .2rem 0 1.4rem;
  border: 1px solid rgba(36,122,85,.13);
  border-radius: 24px;
  background: linear-gradient(125deg, rgba(255,255,255,.94), rgba(232,246,237,.88));
  box-shadow: 0 14px 38px rgba(31,77,57,.08);
}
.hero-kicker {
  display: inline-block;
  padding: .32rem .72rem;
  border-radius: 999px;
  background: #e3f3e8;
  color: #276e50;
  font-size: .78rem;
  font-weight: 700;
  letter-spacing: .04em;
  text-transform: uppercase;
}
.hero h1 { margin: .65rem 0 .35rem; font-size: 2.25rem; }
.hero p { color: var(--muted); margin: 0; font-size: 1.02rem; }
div[data-testid="stForm"], div[data-testid="stFileUploader"] {
  border: 1px solid rgba(36,122,85,.14);
  border-radius: 18px;
  background: rgba(255,255,255,.76);
  padding: 1rem;
}
button[kind="primary"], [data-testid="stFormSubmitButton"] button {
  border-radius: 12px;
  border: 0;
  background: linear-gradient(100deg, #247a55, #31936a);
  color: white;
  font-weight: 700;
}
div[data-testid="stMetric"] {
  padding: .9rem 1rem;
  border: 1px solid rgba(36,122,85,.12);
  border-radius: 16px;
  background: rgba(255,255,255,.72);
}
div[data-testid="stTabs"] button { font-weight: 650; }
/* Контрастный текст на светлом фоне независимо от темы Streamlit */
[data-testid="stAppViewContainer"], .stMarkdown, .stMarkdown p,
[data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"],
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
  color: #17332d !important;
}
[data-testid="stAlert"] {
  background: #fff5d8 !important;
  border: 1px solid #e7cc82 !important;
  border-radius: 14px;
}
[data-testid="stAlert"] * {
  color: #26352d !important;
}
[data-testid="stAlert"][kind="success"] {
  background: #e8f5eb !important;
  border-color: #9bc9a8 !important;
}
hr { border-color: rgba(36,122,85,.14); }
.small-note { color: #667a72; font-size: .92rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <span class="hero-kicker">♻️ Умная сортировка</span>
  <h1>Smart Bin</h1>
  <p>Определите категорию отхода по описанию или фотографии.</p>
</div>
""", unsafe_allow_html=True)

COMPARTMENTS = {
    "Пластик": "Контейнер для пластика",
    "Бумага": "Контейнер для бумаги",
    "Металл": "Контейнер для металла",
    "Стекло": "Контейнер для стекла",
    "Органика": "Контейнер для органики",
    "Другое": "Проверьте местные правила",
    "Электронные устройства": "Отдельный пункт приёма электроники и батарей",
}

def show_result(category, confidence, source, label=None):
    st.markdown("### ✨ Результат")
    st.success(f"Категория: **{category}**")
    col1, col2 = st.columns(2)
    if confidence is None:
        col1.metric("Определение", "Уточнено вами")
    else:
        col1.metric("Оценка модели", f"{confidence * 100:.0f}%")
    col2.metric("Куда сдавать", COMPARTMENTS.get(category, COMPARTMENTS["Другое"]))
    if label:
        st.caption(f"Класс модели: {label}")
    if category == "Электронные устройства":
        st.warning("Наш контейнер не предназначен для утилизации электронных устройств и батарей. Пожалуйста, сдайте их в специализированный пункт приёма.")
    elif confidence is None:
        st.info("Категория указана вами, а не определена моделью.")
    elif confidence < 0.65 or category == "Другое":
        st.warning("Результат неуверенный. Проверьте маркировку и местные правила сортировки.")
    else:
        st.info("Процент модели не равен проверенной точности распознавания.")
    add_waste(source, category, confidence if confidence is not None else 0.0)

tab_text, tab_photo = st.tabs(["⌨️ По описанию", "📷 По фото"])

with tab_text:
    with st.form("text_classification"):
        waste = st.text_input("Что нужно отсортировать?", placeholder="Например: пластиковая бутылка или электронное устройство")
        submitted = st.form_submit_button("Определить категорию", use_container_width=True)
    if submitted:
        if not waste.strip():
            st.warning("Введите описание отхода.")
        else:
            category, confidence = classify_waste(waste)
            show_result(category, confidence, waste.strip())

with tab_photo:
    uploaded_file = st.file_uploader("Загрузите фотографию отхода", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Загруженное изображение", use_container_width=True)
        contains_electronics = st.checkbox("На фото электронное устройство или предмет с аккумулятором")
        if st.button("Определить по фото", use_container_width=True):
            if contains_electronics:
                show_result("Электронные устройства", None, f"Уточнено вручную: {uploaded_file.name}")
            else:
                try:
                    from vision_classifier import classify_image
                    category, confidence, ai_class = classify_image(uploaded_file)
                    show_result(category, confidence, f"Фото: {ai_class}", ai_class)
                    st.warning("Для сложных предметов и устройств с батареями фото-модель может ошибиться. Уточните состав отхода перед сортировкой.")
                except Exception as exc:
                    st.error("Не удалось запустить распознавание фото. Проверьте установку зависимостей и доступ к модели.")
                    st.caption(f"Подробности: {exc}")

st.divider()
st.markdown("### 📊 Статистика сортировки")
statistics = get_statistics()
total = sum(count for _, count in statistics)
if total:
    st.metric("Всего операций", total)
    for category, count in statistics:
        st.write(f"**{category}:** {count} ({count / total:.0%})")
        st.progress(count / total)
else:
    st.info("Пока нет данных о сортировке.")

st.markdown("### 🕘 Последние операции")
history = get_history(10)
if history:
    for waste_text, category, confidence, created_at in history:
        if waste_text.startswith("Уточнено вручную:"):
            st.write(f"**{waste_text}** → {category} · уточнено вручную · {created_at}")
        else:
            st.write(f"**{waste_text}** → {category} · оценка {confidence:.0%} · {created_at}")
else:
    st.write("История пока пустая.")




