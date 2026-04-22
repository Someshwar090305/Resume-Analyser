import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
from pdf_reader import load_resume
from analyzer import extract_resume_info, extract_job_requirements, match_and_score
from groq import Groq
from groq import AuthenticationError as GroqAuthError, RateLimitError as GroqRateLimitError

load_dotenv()

SAMPLE_JD = """
Data Analyst – Entry Level

We are looking for a motivated Data Analyst to join our team.

Required Skills:
- Python (Pandas, NumPy)
- SQL and relational databases
- Data visualisation (Matplotlib, Seaborn, or Tableau)
- Machine Learning fundamentals
- Statistical analysis

Preferred Skills:
- Experience with cloud platforms (AWS or GCP)
- Docker and containerisation
- Git and version control
- Exposure to NLP or deep learning frameworks

Responsibilities:
- Analyse large datasets to extract actionable insights.
- Build and maintain automated reporting pipelines.
- Collaborate with cross-functional teams.
- Present findings via dashboards and visual reports.

Requirements:
- Bachelor's degree in Computer Science, Statistics, or related field.
- 0-2 years of experience (fresh graduates encouraged to apply).
"""

st.set_page_config(
    page_title="Resume Analyzer & Job Matcher",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #1a1a2e 100%);
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #4fc3f7, #81d4fa, #b3e5fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.3rem;
    letter-spacing: -1px;
}

.hero-sub {
    text-align: center;
    color: #90a4ae;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

.steps-row {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-bottom: 2.5rem;
}

.step-chip {
    background: rgba(79, 195, 247, 0.1);
    border: 1px solid rgba(79, 195, 247, 0.25);
    border-radius: 50px;
    padding: 0.4rem 1.1rem;
    color: #4fc3f7;
    font-size: 0.85rem;
    font-weight: 500;
}

.glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.2rem;
}

.section-label {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #4fc3f7;
    margin-bottom: 0.6rem;
}

.score-ring-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
}

.score-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.4rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.7rem;
    box-shadow: 0 0 40px rgba(79,195,247,0.3);
}

.score-label {
    font-size: 1.05rem;
    font-weight: 600;
    color: #eceff1;
}

.skill-chip {
    display: inline-block;
    border-radius: 30px;
    padding: 0.3rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 0.2rem;
}

.chip-green {
    background: rgba(39, 174, 96, 0.15);
    border: 1px solid rgba(39, 174, 96, 0.4);
    color: #2ecc71;
}

.chip-red {
    background: rgba(231, 76, 60, 0.15);
    border: 1px solid rgba(231, 76, 60, 0.4);
    color: #e74c3c;
}

.suggestion-card {
    background: rgba(79,195,247,0.07);
    border-left: 3px solid #4fc3f7;
    border-radius: 0 10px 10px 0;
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    color: #eceff1;
    font-size: 0.93rem;
}

.sug-number {
    display: inline-block;
    background: #4fc3f7;
    color: #0d1b2a;
    border-radius: 50%;
    width: 1.5rem;
    height: 1.5rem;
    line-height: 1.5rem;
    text-align: center;
    font-size: 0.78rem;
    font-weight: 700;
    margin-right: 0.6rem;
}

.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 1.2rem 0;
}

.warn-box {
    background: rgba(230,126,34,0.12);
    border: 1px solid rgba(230,126,34,0.3);
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
    color: #f0a500;
    font-size: 0.9rem;
    margin-bottom: 0.8rem;
}

.err-box {
    background: rgba(192,57,43,0.12);
    border: 1px solid rgba(192,57,43,0.35);
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
    color: #e74c3c;
    font-size: 0.9rem;
    margin-bottom: 0.8rem;
}

.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #eceff1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}

.stTextArea textarea:focus {
    border-color: rgba(79,195,247,0.5) !important;
    box-shadow: 0 0 0 2px rgba(79,195,247,0.12) !important;
}

.stFileUploader {
    border: 1.5px dashed rgba(79,195,247,0.3) !important;
    border-radius: 12px !important;
    background: rgba(79,195,247,0.04) !important;
    padding: 0.5rem !important;
}

div.stButton > button {
    background: linear-gradient(135deg, #1b4f8a, #2e86ab);
    color: #fff;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.65rem 2rem;
    width: 100%;
    transition: all 0.2s ease;
    cursor: pointer;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #2e86ab, #1b4f8a);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(46,134,171,0.35);
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #1b4f8a, #4fc3f7) !important;
    border-radius: 4px !important;
}

.stExpander {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title"> Resume Analyzer & Job Matcher</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">AI-powered resume analysis driven by Claude — get your match score in seconds</div>', unsafe_allow_html=True)

st.markdown("""
<div class="steps-row">
    <span class="step-chip">① Upload or paste your resume</span>
    <span class="step-chip">② Paste the job description</span>
    <span class="step-chip">③ Hit Analyse and get your score</span>
</div>
""", unsafe_allow_html=True)

if "resume_textarea" not in st.session_state:
    st.session_state.resume_textarea = ""
if "jd_textarea" not in st.session_state:
    st.session_state.jd_textarea = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "resume_json" not in st.session_state:
    st.session_state.resume_json = None
if "jd_json" not in st.session_state:
    st.session_state.jd_json = None
if "api_key_ok" not in st.session_state:
    st.session_state.api_key_ok = bool(os.getenv("GROQ_API_KEY"))

if not st.session_state.api_key_ok:
    st.markdown('<div class="err-box">⚠️ <strong>GROQ_API_KEY not set.</strong> Add it to your <code>.env</code> file and restart the app. Get a free key at <a href="https://console.groq.com" target="_blank">console.groq.com</a></div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown('<div class="section-label">📄 Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF or TXT",
        type=["pdf", "txt"],
        key="file_uploader",
        label_visibility="collapsed",
    )
    if uploaded_file is not None:
        extracted, err = load_resume(uploaded_file)
        if err:
            st.markdown(f'<div class="warn-box">⚠️ {err}</div>', unsafe_allow_html=True)
        else:
            st.session_state.resume_textarea = extracted
            st.success(f"✅ Extracted {len(extracted):,} characters from {uploaded_file.name}")

    st.text_area(
        "Or paste resume text",
        height=260,
        placeholder="Paste your full resume text here…",
        label_visibility="collapsed",
        key="resume_textarea",
    )

with col_right:
    st.markdown('<div class="section-label">💼 Job Description</div>', unsafe_allow_html=True)

    btn_col, _ = st.columns([1, 2])
    with btn_col:
        if st.button("Load Sample JD", key="sample_jd_btn"):
            st.session_state.jd_textarea = SAMPLE_JD

    st.text_area(
        "Paste job description",
        height=300,
        placeholder="Paste any job description here…",
        label_visibility="collapsed",
        key="jd_textarea",
    )

st.markdown("<br>", unsafe_allow_html=True)
_, btn_center, _ = st.columns([1, 2, 1])
with btn_center:
    analyse_clicked = st.button("🔍 Analyse Resume", key="analyse_btn")

if analyse_clicked:
    resume_val = st.session_state.get("resume_textarea", "").strip()
    jd_val = st.session_state.get("jd_textarea", "").strip()

    if len(resume_val) < 10:
        st.markdown('<div class="warn-box">⚠️ Resume appears too short. Please paste more content.</div>', unsafe_allow_html=True)
    elif len(jd_val) < 30:
        st.markdown('<div class="warn-box">⚠️ Job description is too short to analyse accurately.</div>', unsafe_allow_html=True)
    elif not os.getenv("GROQ_API_KEY"):
        st.markdown('<div class="err-box">❌ GROQ_API_KEY not set. Check your .env file.</div>', unsafe_allow_html=True)
    else:
        try:
            with st.spinner("🤖 Llama 3.3 is analysing your resume…"):
                resume_json = extract_resume_info(resume_val)
                st.session_state.resume_json = resume_json
                time.sleep(2)

                jd_json = extract_job_requirements(jd_val)
                st.session_state.jd_json = jd_json
                time.sleep(2)

                result = match_and_score(resume_json, jd_json)
                st.session_state.result = result

        except GroqAuthError:
            st.markdown('<div class="err-box">❌ Invalid Groq API key. Check your GROQ_API_KEY in .env.</div>', unsafe_allow_html=True)
        except GroqRateLimitError:
            st.markdown('<div class="warn-box">⚠️ Groq rate limit hit. Wait 30 seconds and retry.</div>', unsafe_allow_html=True)
        except ValueError as e:
            st.markdown(f'<div class="err-box">❌ Could not parse AI response. Raw error: {str(e)}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="err-box">❌ Unexpected error: {str(e)}</div>', unsafe_allow_html=True)

if st.session_state.result:
    res = st.session_state.result
    score = int(res.get("score", 0))
    matched = res.get("matched_skills", [])
    missing = res.get("missing_skills", [])
    suggestions = res.get("suggestions", [])

    if score >= 85:
        score_color = "linear-gradient(135deg, #27ae60, #2ecc71)"
        score_label = "Excellent Match"
        score_emoji = "🟢"
    elif score >= 70:
        score_color = "linear-gradient(135deg, #1b4f8a, #4fc3f7)"
        score_label = "Good Match"
        score_emoji = "🔵"
    elif score >= 50:
        score_color = "linear-gradient(135deg, #e67e22, #f39c12)"
        score_label = "Partial Match"
        score_emoji = "🟡"
    else:
        score_color = "linear-gradient(135deg, #c0392b, #e74c3c)"
        score_label = "Poor Match"
        score_emoji = "🔴"

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown('<div class="section-label" style="text-align:center; margin-bottom:1.2rem;">📊 Analysis Results</div>', unsafe_allow_html=True)

    r_col1, r_col2, r_col3 = st.columns([1, 1, 1], gap="large")

    with r_col1:
        st.markdown(f"""
        <div class="glass-card score-ring-wrapper">
            <div class="score-circle" style="background: {score_color};">
                {score}%
            </div>
            <div class="score-label">{score_emoji} {score_label}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100)

    with r_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">✅ Matched Skills</div>', unsafe_allow_html=True)
        if matched:
            chips_html = "".join(f'<span class="skill-chip chip-green">{s}</span>' for s in matched)
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#666; font-size:0.9rem;">No matched skills found.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r_col3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">❌ Missing Skills</div>', unsafe_allow_html=True)
        if missing:
            chips_html = "".join(f'<span class="skill-chip chip-red">{s}</span>' for s in missing)
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#666; font-size:0.9rem;">No critical skills missing. Great job!</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">💡 Improvement Suggestions</div>', unsafe_allow_html=True)
    for i, sug in enumerate(suggestions, 1):
        st.markdown(f"""
        <div class="suggestion-card">
            <span class="sug-number">{i}</span>{sug}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    exp_col1, exp_col2 = st.columns(2, gap="large")

    with exp_col1:
        with st.expander("🔍 Extracted Resume Data (JSON)"):
            st.json(st.session_state.resume_json)

    with exp_col2:
        with st.expander("🔍 Extracted Job Description Data (JSON)"):
            st.json(st.session_state.jd_json)
