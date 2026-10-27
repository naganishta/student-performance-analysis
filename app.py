
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Student Insights | Performance Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. PROFESSIONAL DESIGN / CUSTOM CSS
# =====================================================
st.markdown("""
<style>
    .stApp {
        background-color: #F5F7FB;
    }

    [data-testid="stSidebar"] {
        background-color: #101828;
    }

    [data-testid="stSidebar"] * {
        color: #F2F4F7;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #101828;
    }

    [data-testid="stSidebar"] input {
        color: #101828 !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    .hero {
        background: linear-gradient(120deg, #101828, #1849A9);
        padding: 30px 32px;
        border-radius: 18px;
        margin-bottom: 24px;
        color: white;
    }

    .hero h1 {
        color: white;
        font-size: 34px;
        margin: 0;
        font-weight: 750;
    }

    .hero p {
        color: #D1E9FF;
        font-size: 15px;
        margin-top: 10px;
        margin-bottom: 0;
    }

    .section-heading {
        color: #101828;
        font-size: 23px;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 14px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #EAECF0;
        padding: 19px 20px;
        border-radius: 14px;
        box-shadow: 0 2px 7px rgba(16, 24, 40, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #475467;
    }

    div[data-testid="stMetricValue"] {
        color: #175CD3;
        font-weight: 750;
    }

    div[data-testid="stPlotlyChart"] {
        background: white;
        border: 1px solid #EAECF0;
        border-radius: 14px;
        padding: 10px;
    }

    .insight {
        background: #EFF8FF;
        border-left: 5px solid #2E90FA;
        padding: 16px 20px;
        border-radius: 8px;
        color: #1849A9;
        margin: 12px 0 20px 0;
    }

    .footer {
        text-align: center;
        color: #667085;
        font-size: 12px;
        padding-top: 28px;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 9px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. LOAD DATASET
# =====================================================
st.sidebar.markdown("# 🎓 Student Insights")
st.sidebar.caption("PERFORMANCE ANALYTICS")
st.sidebar.divider()

csv_path = Path(__file__).parent / "StudentsPerformance.csv"

uploaded_file = st.sidebar.file_uploader(
    "Upload student dataset",
    type=["csv"],
    help="Upload the StudentsPerformance.csv dataset."
)

try:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        st.title("Student Performance Analysis")
        st.info("Upload StudentsPerformance.csv in the sidebar to begin.")
        st.stop()

except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(f"Unable to read the dataset: {error}")
    st.stop()

# Required dataset columns
score_columns = ["math score", "reading score", "writing score"]
required_columns = [
    "gender",
    "lunch",
    "test preparation course",
    *score_columns
]

missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(
        "This CSV does not have the expected columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

# =====================================================
# 4. DATA CLEANING
# =====================================================
for col in score_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=score_columns).copy()

if df.empty:
    st.error("No valid student score records were found.")
    st.stop()

# NumPy is used to calculate each student's mean score.
df["Average Score"] = np.mean(
    df[score_columns].to_numpy(dtype=float),
    axis=1
).round(2)

# =====================================================
# 5. SIDEBAR FILTERS
# =====================================================
st.sidebar.subheader("🔎 Explore Students")

gender_options = sorted(df["gender"].dropna().unique().tolist())
lunch_options = sorted(df["lunch"].dropna().unique().tolist())
prep_options = sorted(
    df["test preparation course"].dropna().unique().tolist()
)

selected_gender = st.sidebar.multiselect(
    "Gender",
    gender_options,
    default=gender_options
)

selected_lunch = st.sidebar.multiselect(
    "Lunch type",
    lunch_options,
    default=lunch_options
)

selected_prep = st.sidebar.multiselect(
    "Test preparation",
    prep_options,
    default=prep_options
)

filtered_df = df[
    df["gender"].isin(selected_gender)
    & df["lunch"].isin(selected_lunch)
    & df["test preparation course"].isin(selected_prep)
].copy()

st.sidebar.divider()
st.sidebar.caption("Dataset: Students Performance in Exams")
st.sidebar.caption("Source: Kaggle • 1,000 original records")

# =====================================================
# 6. DASHBOARD HEADER
# =====================================================
st.markdown("""
<div class="hero">
    <h1>🎓 Student Performance Analysis</h1>
    <p>
        An interactive overview of academic scores, subject comparisons,
        and student performance patterns.
    </p>
</div>
""", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning(
        "No students match your selected filters. "
        "Adjust the sidebar filters to continue."
    )
    st.stop()

# =====================================================
# 7. KEY PERFORMANCE INDICATORS
# =====================================================
st.markdown(
    '<div class="section-heading">📊 Performance Overview</div>',
    unsafe_allow_html=True
)

avg_math = filtered_df["math score"].mean()
avg_reading = filtered_df["reading score"].mean()
avg_writing = filtered_df["writing score"].mean()
overall_average = filtered_df["Average Score"].mean()

k1, k2, k3, k4 = st.columns(4)

k1.metric("👥 Students", f"{len(filtered_df):,}")
k2.metric("➗ Average Math", f"{avg_math:.1f}/100")
k3.metric("📖 Average Reading", f"{avg_reading:.1f}/100")
k4.metric("✍️ Average Writing", f"{avg_writing:.1f}/100")

st.caption(
    f"Overall average across the three subjects: "
    f"{overall_average:.1f}/100. Values update with your filters."
)

# =====================================================
# 8. SUBJECT COMPARISON CHART
# =====================================================
st.markdown(
    '<div class="section-heading">📈 Academic Performance</div>',
    unsafe_allow_html=True
)

subject_labels = {
    "math score": "Math",
    "reading score": "Reading",
    "writing score": "Writing"
}

subject_df = (
    filtered_df[score_columns]
    .mean()
    .rename(index=subject_labels)
    .rename_axis("Subject")
    .reset_index(name="Average Score")
)

chart1, chart2 = st.columns(2)

with chart1:
    fig_subject = px.bar(
        subject_df,
        x="Subject",
        y="Average Score",
        color="Subject",
        text_auto=".1f",
        title="Average Score by Subject",
        color_discrete_sequence=["#2E90FA", "#12B76A", "#7A5AF8"]
    )

    fig_subject.update_layout(
        template="plotly_white",
        showlegend=False,
        yaxis_range=[0, 100],
        yaxis_title="Average score out of 100",
        xaxis_title="",
        margin=dict(l=15, r=15, t=60, b=15),
        height=370
    )

    st.plotly_chart(fig_subject, use_container_width=True)

# =====================================================
# 9. SCORE DISTRIBUTION CHART
# =====================================================
with chart2:
    fig_distribution = px.histogram(
        filtered_df,
        x="Average Score",
        nbins=20,
        title="Distribution of Average Scores",
        labels={"Average Score": "Student average score"},
        color_discrete_sequence=["#2E90FA"]
    )

    fig_distribution.update_layout(
        template="plotly_white",
        xaxis_title="Average score",
        yaxis_title="Number of students",
        margin=dict(l=15, r=15, t=60, b=15),
        height=370
    )

    st.plotly_chart(fig_distribution, use_container_width=True)

# =====================================================
# 10. SUBJECT SCORE SPREAD
# =====================================================
st.markdown(
    '<div class="section-heading">📉 Score Distribution by Subject</div>',
    unsafe_allow_html=True
)

long_df = filtered_df[score_columns].rename(
    columns=subject_labels
).melt(
    var_name="Subject",
    value_name="Score"
)

fig_box = px.box(
    long_df,
    x="Subject",
    y="Score",
    color="Subject",
    title="Compare Score Ranges and Medians",
    color_discrete_sequence=["#2E90FA", "#12B76A", "#7A5AF8"]
)

fig_box.update_layout(
    template="plotly_white",
    showlegend=False,
    yaxis_title="Score out of 100",
    xaxis_title="",
    margin=dict(l=15, r=15, t=60, b=15),
    height=390
)

st.plotly_chart(fig_box, use_container_width=True)

# =====================================================
# 11. AUTOMATIC INSIGHT
# =====================================================
best_subject = filtered_df[score_columns].mean().idxmax()
best_subject_name = subject_labels[best_subject]

st.markdown(
    f"""
    <div class="insight">
        <strong>💡 Key Insight</strong><br>
        Within the currently selected students, <strong>{best_subject_name}</strong>
        has the highest average score at
        <strong>{filtered_df[best_subject].mean():.1f}/100</strong>.
        This is a descriptive finding, not proof of what caused the scores.
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 12. STUDENT DATA TABLE
# =====================================================
st.markdown(
    '<div class="section-heading">🧑‍🎓 Student Records</div>',
    unsafe_allow_html=True
)

search_text = st.text_input(
    "Search student categories",
    placeholder="Try female, standard, completed, or none..."
)

table_df = filtered_df.copy()

if search_text:
    searchable = [
        "gender",
        "lunch",
        "test preparation course"
    ]

    search_mask = table_df[searchable].astype(str).apply(
        lambda column: column.str.contains(
            search_text,
            case=False,
            na=False,
            regex=False
        )
    ).any(axis=1)

    table_df = table_df[search_mask]

st.caption(f"Showing {len(table_df):,} matching records")

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# 13. DOWNLOAD FILTERED DATA
# =====================================================
download_data = table_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Student Data (CSV)",
    data=download_data,
    file_name="student_performance_filtered.csv",
    mime="text/csv"
)

# =====================================================
# 14. FOOTER
# =====================================================
st.markdown("""
<div class="footer">
    Student Insights • Student Performance Analysis Project<br>
    Built with Python, Pandas, NumPy, Streamlit and Plotly
</div>
""", unsafe_allow_html=True)
