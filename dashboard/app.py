import streamlit as st
import requests
import json
import pandas as pd
import pydeck as pdk

# 1. Page Configuration
st.set_page_config(
    page_title="CryoFlow | NASA Glacier & Water Intelligence",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean Vector SVG Icons
SVG_ICONS = {
    "water_drop": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>',
    "settings": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#334155" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "map": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 15 22 23 18 23 2 15 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="15" y1="6" x2="15" y2="22"/></svg>',
    "analytics": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "time": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "ai": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>',
    "award": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>',
    "info": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0369A1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
}

# 2. Strict CSS Theme Override (Solves white-on-white text & Streamlit dark mode conflicts)
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Force App Light Theme & Global Font */
    html, body, [class*="st-"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    /* Force High Contrast Dark Slate Color for Headers and Texts */
    h1, h2, h3, h4, h5, h6, label, p, span, div, .stMarkdown {
        color: #0F172A !important;
    }

    /* Sidebar Background and High Contrast Text */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] *, section[data-testid="stSidebar"] label {
        color: #0F172A !important;
        font-weight: 500 !important;
    }

    /* Inputs, Selectboxes, and DatePickers Text Visibility */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="input"] input {
        color: #0F172A !important;
        font-weight: 500 !important;
    }

    /* Hero Header Banner */
    .hero-container {
        background: linear-gradient(135deg, #0B132B 0%, #1C2541 100%);
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(11, 19, 43, 0.15);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #94A3B8 !important;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Professional Section Cards */
    .cryo-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 16px !important;
    }

    /* Metric Cards Fix */
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #475569 !important;
        font-weight: 600 !important;
    }

    /* Highlight Hook Card */
    .hook-card {
        background: #F0F9FF !important;
        border-left: 4px solid #0284C7 !important;
        border-radius: 6px !important;
        padding: 12px 14px !important;
        font-size: 13px !important;
        color: #0369A1 !important;
        line-height: 1.5 !important;
        margin-top: 12px !important;
        margin-bottom: 12px !important;
    }
    .hook-card * {
        color: #0369A1 !important;
    }

    /* Section Title Layout with SVG */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 18px;
        font-weight: 600;
        color: #0F172A !important;
        margin-bottom: 14px;
    }

    /* Step timeline box for Drop Journey */
    .step-box {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 16px !important;
        text-align: left !important;
    }
    .step-box h4 {
        margin: 0 0 6px 0 !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #0284C7 !important;
    }

    /* Certificate Card Styling */
    .cert-card {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%) !important;
        border: 2px dashed #0284C7 !important;
        padding: 24px !important;
        border-radius: 12px !important;
        text-align: center !important;
        margin-top: 16px !important;
    }
    .cert-card * {
        color: #0369A1 !important;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        height: 44px !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Multilingual Dictionary
TRANSLATIONS = {
    "uz": {
        "title": "CryoFlow",
        "subtitle": "NASA sun'iy yo'ldoshlari (MODIS) va AI yordamida Farg'ona vodiysi muzliklari hamda suv resurslarini monitoring qilish tizimi",
        "sidebar_header": "Boshqaruv va Parametrlar",
        "region_label": "Tadqiqot hududi:",
        "regions": {
            "Farg'ona tumanlari (Naryn daryosi havzasi)": {
                "coordinates": [[[73.5, 41.2], [74.5, 41.2], [74.5, 42.0], [73.5, 42.0], [73.5, 41.2]]]},
            "Namangan va Sirdaryo havzasi": {
                "coordinates": [[[71.0, 40.5], [72.0, 40.5], [72.0, 41.5], [71.0, 41.5], [71.0, 40.5]]]},
            "Andijon daryo tarmoqlari": {
                "coordinates": [[[72.1, 40.2], [72.5, 40.2], [72.5, 40.6], [72.1, 40.6], [72.1, 40.2]]]}
        },
        "farming_label": "Dehqonchilik sohasi:",
        "farming_types": ["Paxtakorlik", "Bog'dorchilik", "G'allachilik", "Sabzavotchilik"],
        "hook_msg": "<b>Shaxsiy fakt:</b> {region} hududidagi {farming} maydoningizni sug'oruvchi suvning <b>70% qismi</b> Tyan-Shan muzliklaridan quyiladi.",
        "map_title": "Geofazoviy Xarita va Suv Oqimi Vizualizatsiyasi",
        "results_title": "NASA MODIS Analitika Natijalari",
        "start_date": "Boshlanish sanasi",
        "end_date": "Tugash sanasi",
        "run_analysis": "NASA Tahlilini Boshlash",
        "tab_drop": "Tomchi Sayohati",
        "tab_time": "Vaqt Mashinasi",
        "tab_whatif": "'Agar...?' Simulyatori",
        "tab_advisor": "AI Maslahatchi",
        "tab_quiz": "Ekologik Quiz",
        "storytelling": "<b>Taqqoslama fakt:</b> So‘nggi 20 yilda erib yo‘qolgan muzlik suvi hajmi Toshkent shahridagi barcha yirik basseynlarni 5 yil davomida to‘ldirishga yetadi.",
        "quiz_q": "Farg‘ona vodiysidagi sug'orish kanallariga suvning qaysi qismi muzliklardan keladi?",
        "quiz_options": ["10-20%", "70-80%", "Faqat mahalliy yomg'irlardan"],
        "quiz_check": "Tekshirish",
        "quiz_success": "Muvaffaqiyatli! Siz 'Suvni tejash elchisi' sertifikatiga ega bo'ldingiz!",
        "quiz_error": "Noto'g'ri. Qayta urinib ko'ring!",
        "success_msg": "Analiz muvaffaqiyatli bajarildi!",
        "error_backend": "FastAPI бэкенд серверiga ulanib bo'lmadi. Server запущен эkanini tekshiring (`uvicorn app.main:app --reload`)."
    },
    "ru": {
        "title": "CryoFlow",
        "subtitle": "Мониторинг и прогнозирование состояния ледников и водных ресурсов Ферганской долины на основе спутников NASA (MODIS)",
        "sidebar_header": "Управление и параметры",
        "region_label": "Выберите регион исследования:",
        "regions": {
            "Бассейн р. Нарын (Ферганская долина)": {
                "coordinates": [[[73.5, 41.2], [74.5, 41.2], [74.5, 42.0], [73.5, 42.0], [73.5, 41.2]]]},
            "Верховья Сырдарьи (Наманган)": {
                "coordinates": [[[71.0, 40.5], [72.0, 40.5], [72.0, 41.5], [71.0, 41.5], [71.0, 40.5]]]},
            "Андижанский речной бассейн": {
                "coordinates": [[[72.1, 40.2], [72.5, 40.2], [72.5, 40.6], [72.1, 40.6], [72.1, 40.2]]]}
        },
        "farming_label": "Тип агрокультуры:",
        "farming_types": ["Хлопководство", "Садоводство", "Зерновые", "Овощеводство"],
        "hook_msg": "<b>Персональный факт:</b> 70% воды для вашего участка ({region}, {farming}) поступает напрямую из ледников Тянь-Шаня.",
        "map_title": "Геопространственная карта и траектория стока",
        "results_title": "Аналитика NASA MODIS",
        "start_date": "Начальная дата",
        "end_date": "Конечная дата",
        "run_analysis": "Запустить анализ NASA",
        "tab_drop": "Путешествие Капли",
        "tab_time": "Машина времени",
        "tab_whatif": "Симулятор 'Что, если...?'",
        "tab_advisor": "ИИ-Консультант",
        "tab_quiz": "Эко-Квиз",
        "storytelling": "<b>Наглядный факт:</b> Объем потерянной талой воды за 20 лет равен объему, способному наполнить все крупные бассейны Ташкента в течение 5 лет.",
        "quiz_q": "Какой процент поливной воды в Ферганской долине формируется таянием ледников?",
        "quiz_options": ["10-20%", "70-80%", "Только за счет местных дождей"],
        "quiz_check": "Проверить ответ",
        "quiz_success": "Верно! Вам присвоен статус 'Посол сбережения воды'!",
        "quiz_error": "Неверно. Попробуйте еще раз!",
        "success_msg": "Анализ успешно завершен!",
        "error_backend": "Не удалось подключиться к FastAPI бэкенду. Убедитесь, что сервер запущен (`uvicorn app.main:app --reload`)."
    },
    "en": {
        "title": "CryoFlow",
        "subtitle": "Satellite-powered glacier and water resource analytics platform for Central Asia (NASA MODIS)",
        "sidebar_header": "Control Panel",
        "region_label": "Select Target Region:",
        "regions": {
            "Naryn River Basin (Fergana Valley)": {
                "coordinates": [[[73.5, 41.2], [74.5, 41.2], [74.5, 42.0], [73.5, 42.0], [73.5, 41.2]]]},
            "Upper Syr Darya (Namangan)": {
                "coordinates": [[[71.0, 40.5], [72.0, 40.5], [72.0, 41.5], [71.0, 41.5], [71.0, 40.5]]]},
            "Andijan River System": {
                "coordinates": [[[72.1, 40.2], [72.5, 40.2], [72.5, 40.6], [72.1, 40.6], [72.1, 40.2]]]}
        },
        "farming_label": "Farming Sector:",
        "farming_types": ["Cotton", "Orchards", "Cereals", "Vegetables"],
        "hook_msg": "<b>Personalized Insight:</b> 70% of the irrigation water for your area ({region}, {farming}) originates directly from Tien Shan glaciers.",
        "map_title": "Geospatial Map & Flow Trajectory",
        "results_title": "NASA MODIS Analytics",
        "start_date": "Start Date",
        "end_date": "End Date",
        "run_analysis": "Run NASA Analysis",
        "tab_drop": "Drop Journey",
        "tab_time": "Time Machine",
        "tab_whatif": "'What-If' Simulator",
        "tab_advisor": "AI Water Advisor",
        "tab_quiz": "Eco Quiz",
        "storytelling": "<b>Insight:</b> The volume of melted glacier water lost over 20 years equals filling all major swimming pools in Tashkent for 5 years.",
        "quiz_q": "What proportion of irrigation water in Fergana Valley comes from mountain glaciers?",
        "quiz_options": ["10-20%", "70-80%", "Only local rainfall"],
        "quiz_check": "Submit Answer",
        "quiz_success": "Correct! You have been awarded the 'Water Conservation Ambassador' status!",
        "quiz_error": "Incorrect. Try again!",
        "success_msg": "Analysis completed successfully!",
        "error_backend": "Could not connect to FastAPI backend. Ensure server is running (`uvicorn app.main:app --reload`)."
    }
}

# 4. Sidebar Language Selector
lang_choice = st.sidebar.selectbox("Language / Til / Язык", options=["O'zbek", "Русский", "English"], index=1)
lang_map = {"O'zbek": "uz", "Русский": "ru", "English": "en"}
lang = lang_map[lang_choice]
t = TRANSLATIONS[lang]

API_URL = "http://127.0.0.1:8000/api/v1/cryo/analyze-glacier"

# 5. Clean Hero Header with SVG
st.markdown(
    f"""
    <div class="hero-container">
        <div>
            <h1 class="hero-title">{SVG_ICONS["water_drop"]} {t["title"]}</h1>
            <p class="hero-subtitle">{t["subtitle"]}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(f'<div class="section-header">{SVG_ICONS["settings"]} {t["sidebar_header"]}</div>',
                    unsafe_allow_html=True)
regions_dict = t["regions"]
selected_region = st.sidebar.selectbox(t["region_label"], list(regions_dict.keys()))
polygon_data = regions_dict[selected_region]

farming = st.sidebar.selectbox(t["farming_label"], t["farming_types"])

st.sidebar.markdown(
    f'<div class="hook-card">{t["hook_msg"].format(region=selected_region, farming=farming)}</div>',
    unsafe_allow_html=True
)

date_start = st.sidebar.date_input(t["start_date"], value=pd.to_datetime("2026-05-01"))
date_end = st.sidebar.date_input(t["end_date"], value=pd.to_datetime("2026-06-01"))
run_analysis = st.sidebar.button(t["run_analysis"], type="primary", use_container_width=True)

# 6. Main Columns Layout
col1, col2 = st.columns([1.3, 0.7])

with col1:
    st.markdown(f'<div class="section-header">{SVG_ICONS["map"]} {t["map_title"]}</div>', unsafe_allow_html=True)
    coords = polygon_data["coordinates"][0]
    lat_center = sum([p[1] for p in coords]) / len(coords)
    lon_center = sum([p[0] for p in coords]) / len(coords)

    view_state = pdk.ViewState(
        latitude=lat_center,
        longitude=lon_center,
        zoom=7.2,
        pitch=40,
        bearing=10
    )

    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=[{"polygon": coords}],
        get_polygon="polygon",
        get_fill_color=[14, 165, 233, 90],
        get_line_color=[2, 132, 199, 230],
        line_width_min_pixels=2,
        pickable=True
    )

    water_arcs = pd.DataFrame([
        {"from_name": "Ледник Тянь-Шань (4,200m)", "from_lon": 78.2, "from_lat": 42.1, "to_name": "Река Нарын",
         "to_lon": 74.0, "to_lat": 41.4, "color": [56, 189, 248]},
        {"from_name": "Река Нарын", "from_lon": 74.0, "from_lat": 41.4, "to_name": "Большой Ферганский Канал",
         "to_lon": 72.3, "to_lat": 40.9, "color": [2, 132, 199]},
        {"from_name": "Большой Ферганский Канал", "from_lon": 72.3, "from_lat": 40.9, "to_name": "Поля и Сады",
         "to_lon": lon_center, "to_lat": lat_center, "color": [16, 185, 129]}
    ])

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=water_arcs,
        get_source_position=["from_lon", "from_lat"],
        get_target_position=["to_lon", "to_lat"],
        get_source_color="color",
        get_target_color="color",
        get_width=5,
        pickable=True
    )

    r = pdk.Deck(
        layers=[polygon_layer, arc_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip={"text": "{from_name} ➔ {to_name}"}
    )
    st.pydeck_chart(r, use_container_width=True)

with col2:
    st.markdown(f'<div class="section-header">{SVG_ICONS["analytics"]} {t["results_title"]}</div>',
                unsafe_allow_html=True)

    if run_analysis:
        payload = {
            "polygon": {
                "type": "Polygon",
                "coordinates": polygon_data["coordinates"]
            },
            "date_start": date_start.strftime("%Y-%m-%d"),
            "date_end": date_end.strftime("%Y-%m-%d")
        }

        with st.spinner("Запрос к NASA CMR и обработка..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()

                    if data.get("status") == "success":
                        metrics = data.get("metrics", {})
                        trend = data.get("trend_analysis", {})

                        st.success(t["success_msg"])

                        st.metric(
                            label="Площадь снежного покрова",
                            value=f"{metrics.get('snow_covered_area_km2', 0)} км²",
                            delta=f"{trend.get('melt_rate_percentage', 0)}%"
                        )

                        st.metric(
                            label="Процент покрытия снежным слоем",
                            value=f"{metrics.get('snow_cover_percentage', 0)}%"
                        )

                        st.info(f"Общая площадь бассейна: {metrics.get('total_area_km2', 0)} км²")
                        st.caption(f"Состояние: **{trend.get('trend', 'N/A').upper()}**")
                    else:
                        st.warning("Спутниковые данные за указанный период не найдены.")
                else:
                    st.error(f"Ошибка бэкенда: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error(t["error_backend"])
    else:
        st.markdown(
            """
            <div class="cryo-card">
                <p style="color: #475569; font-size: 14px; margin: 0;">
                    Нажмите <b>«Запустить анализ NASA»</b> в панели слева для получения расчетов по спутниковым снимкам MODIS.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.metric("Площадь снега (демо)", "450.5 км²", "-12.4%")
        st.metric("Покрытие территории", "37.54%", "-4.2%")

# 7. Professional Tabs
st.markdown("<br>", unsafe_allow_html=True)
tab_drop, tab_time, tab_whatif, tab_advisor, tab_quiz = st.tabs([
    t["tab_drop"], t["tab_time"], t["tab_whatif"], t["tab_advisor"], t["tab_quiz"]
])

with tab_drop:
    st.markdown(f'<div class="section-header">{SVG_ICONS["water_drop"]} Путь талой капли (Drop Journey)</div>',
                unsafe_allow_html=True)
    st.write("Визуализация движения воды от альпийских ледников до оросительных каналов:")
    st.progress(100)

    col_step1, col_step2, col_step3 = st.columns(3)
    with col_step1:
        st.markdown(
            """
            <div class="step-box">
                <h4>1. Ледники Тянь-Шаня</h4>
                <p style="font-size:13px; color:#475569; margin:0;">Высота: 4,200 м. Сезонное таяние снежного покрова при повышении температуры.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_step2:
        st.markdown(
            """
            <div class="step-box">
                <h4>2. Река Нарын</h4>
                <p style="font-size:13px; color:#475569; margin:0;">Скорость стока: 420 м³/с. Прохождение гидроузлов и выработка энергии.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_step3:
        st.markdown(
            """
            <div class="step-box">
                <h4 style="color:#10B981;">3. Оросительные поля</h4>
                <p style="font-size:13px; color:#475569; margin:0;">Распределение воды через Большой Ферганский Канал на полив урожая.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

with tab_time:
    st.markdown(f'<div class="section-header">{SVG_ICONS["time"]} Машина времени (2000 - 2026)</div>',
                unsafe_allow_html=True)
    year = st.slider("Инспекционный год:", 2000, 2026, 2026)
    st.write(f"Инспекция ретроспективных снимков за **{year} год**")

    years = list(range(2000, 2027, 2))
    areas = [1500 - (y - 2000) * 16 + (y % 3) * 10 for y in years]
    df_chart = pd.DataFrame({"Год": years, "Площадь снежного слоя (км²)": areas})
    st.line_chart(df_chart.set_index("Год"))

    st.markdown(f'<div class="hook-card">{t["storytelling"]}</div>', unsafe_allow_html=True)

with tab_whatif:
    st.markdown(f'<div class="section-header">{SVG_ICONS["analytics"]} Симулятор "Что, если...?" (What-If)</div>',
                unsafe_allow_html=True)
    reduction = st.slider("Сокращение объема снежного покрова (%):", 0, 50, 20)

    st.info(f"Моделирование воздействия при таянии на **{reduction}%** выше нормы:")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Ожидаемый дефицит речного стока", f"{reduction * 1.65:.1f}%", "-7.5%")
    with col_b:
        risk_level = "Высокий (High Risk)" if reduction > 25 else "Умеренный (Moderate)"
        st.metric("Оценка риска для агросектора", risk_level)

with tab_advisor:
    st.markdown(f'<div class="section-header">{SVG_ICONS["ai"]} ИИ-Консультант по водосбережению</div>',
                unsafe_allow_html=True)
    st.write(f"**Агро-рекомендации для региона ({selected_region}) и культуры ({farming}):**")
    st.markdown(
        f"""
        <div class="cryo-card" style="border-left: 4px solid #10B981;">
            <h4 style="margin-top:0; color:#065F46;">🌱 Персональный совет по поливу</h4>
            <p style="font-size:14px; color:#1E293B; margin:0;">
                Для территории <b>{selected_region}</b> при выращивании культуры <b>{farming}</b> 
                рекомендуется внедрение утреннего капельного орошения. Это позволит сократить потери на испарение 
                и сберечь до <b>35% талой воды</b> из Тян-Шанских ледников.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with tab_quiz:
    st.markdown(f'<div class="section-header">{SVG_ICONS["award"]} Экологический Квиз и Именной Сертификат</div>',
                unsafe_allow_html=True)
    st.write(t["quiz_q"])
    correct_ans = t["quiz_options"][1]
    ans = st.radio("Ваш вариант ответа:", t["quiz_options"])

    if st.button(t["quiz_check"], type="primary"):
        if ans == correct_ans:
            st.success(t["quiz_success"])
            st.balloons()
            st.markdown(
                """
                <div class="cert-card">
                    <h2 style="color: #0369A1; margin: 0 0 10px 0;">СЕРТИФИКАТ ЭКО-ЭМБАССАДОРА</h2>
                    <p style="color: #475569; font-size: 15px; margin-bottom: 6px;">Выдан пользователю платформы <b>CryoFlow</b></p>
                    <h3 style="color: #0F172A; margin: 0 0 12px 0;">«ПОСОЛ СБЕРЕЖЕНИЯ ВОДЫ ФЕРГАНСКОЙ ДОЛИНЫ»</h3>
                    <p style="font-size: 13px; color: #0369A1; margin: 0;">За прохождение образовательного модуля по защите водных ресурсов Тянь-Шаня.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error(t["quiz_error"])