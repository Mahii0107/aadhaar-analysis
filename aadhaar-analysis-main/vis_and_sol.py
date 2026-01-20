import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
from utils import *
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="UIDAI National Aadhaar Dashboard",
    page_icon="🇮🇳",
    layout="wide"
)

st.title("UIDAI Aadhaar National Analytics Dashboard and Early Warning system📊")
# st.markdown("Comprehensive analysis of Aadhaar **Enrollment, Demographics & Biometrics** across India")

@st.cache_data
def load_data():
    enrol = pd.read_csv("cleaned_data_enrol.csv")
    demo = pd.read_csv("demographic_cleaned.csv")
    bio = pd.read_csv("biometric_data.csv")
    return enrol, demo, bio

enrol_df, demo_df, bio_df = load_data()

st.sidebar.header("Choose your preference:")

dataset = st.sidebar.radio(
    "Choose:",
    ["Enrollment Analytics", "Demographics Analytics", "Biometrics Analytics","Enrollment Forecast" ,"Solution: Early Warning System"]
)

if dataset == "Enrollment Analytics":
    st.markdown("Comprehensive analysis of Aadhaar **Enrollment** across India")
    df = enrol_df.copy()
    df["date"] = pd.to_datetime(df["date"])

    st.sidebar.header("Filters")
    date_range = st.sidebar.date_input(
        "Date Range",
        [df["date"].min(), df["date"].max()]
    )

    if len(date_range) == 2:
        df = df[(df["date"] >= pd.to_datetime(date_range[0])) &
                (df["date"] <= pd.to_datetime(date_range[1]))]

    states = st.sidebar.multiselect(
        "Select State",
        df["state_final"].unique()
    )
    if states:
        df = df[df["state_final"].isin(states)]

    districts = st.sidebar.multiselect(
        "Select District",
        df["district_clean"].unique()
    )
    if districts:
        df = df[df["district_clean"].isin(districts)]

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Enrolments", f"{df['total_enrolments'].sum():,.0f}")
    k2.metric("Total States", df["state_final"].nunique())
    k3.metric("Total Districts", df["district_clean"].nunique())

    col1, col2 = st.columns(2)

    # State-wise enrolments
    state_enrol = df.groupby("state_final", as_index=False)["total_enrolments"].sum()
    with col1:
        st.subheader("State-wise Enrolments")
        fig1 = px.bar(state_enrol, x="state_final", y="total_enrolments", color="state_final")
        st.plotly_chart(fig1, use_container_width=True)

    # Age-wise distribution
    age_df = pd.DataFrame({
        "Age Group": ["0-5", "5-17", "18+"],
        "Enrollments": [
            df["age_0_5"].sum(),
            df["age_5_17"].sum(),
            df["age_18_greater"].sum()
        ]
    })
    with col2:
        st.subheader("Age Group Distribution")
        fig2 = px.pie(age_df, names="Age Group", values="Enrollments", hole=0.5)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    # Monthly trend
    month_df = df.groupby("month", as_index=False)["total_enrolments"].sum()
    with col3:
        st.subheader("Monthly Enrollment Trend")
        fig3 = px.bar(month_df, x="month", y="total_enrolments")
        st.plotly_chart(fig3, use_container_width=True)

    # District top 10
    top_dist = (
        df.groupby("district_clean", as_index=False)["total_enrolments"]
        .sum()
        .sort_values(by="total_enrolments", ascending=False)
        .head(10)
    )
    with col4:
        st.subheader("Top 10 Districts")
        fig4 = px.funnel(top_dist, x="total_enrolments", y="district_clean", orientation="h")
        st.plotly_chart(fig4, use_container_width=True)

    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("Number of Enrollments")
        date_trend = (
        df['date'].value_counts().sort_index().reset_index()
        )
        fig = px.line(
        date_trend,
        x='date',
        y='count',
        markers=True,
        )
        fig.update_layout(
        xaxis_title="Date",
        template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col6: 
        st.subheader("State-wise Aadhaar Enrolments Heatmap")
        state_data = df.groupby('state_final', as_index=False)['total_enrolments'].sum()
        heat = state_data.set_index('state_final')
        fig = px.imshow(
        heat,
        color_continuous_scale="Purples",
        aspect="auto", 
        text_auto=True,
        height = 700,
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

elif dataset == "Demographics Analytics":
    st.markdown("Comprehensive analysis of Aadhaar **Demographics** data across India")
    df = demo_df.copy()
    st.sidebar.header("Filters")

    states = st.sidebar.multiselect("Select State", df["state_final"].unique())
    if states:
        df = df[df["state_final"].isin(states)]

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Population Records", f"{len(df):,}")
    k2.metric("States Covered", df["state_final"].nunique())
    k3.metric("Districts Covered", df["district_clean"].nunique())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Age-group Distribution of Aadhaar Updates")
        age_df = df[["age_5_17_count", "age_17_plus_count"]].sum().reset_index()
        age_df.columns = ["Age Group", "Count"]
        fig1 = px.pie(
        age_df,
        names="Age Group",
        values="Count",
        hole=0.5
        )
        fig1.update_layout(template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # daily updates
        st.subheader("Daily Aadhar updates over time")
        daily_demo_updates = df.groupby('date')['total_updates'].sum().reset_index()
        daily_demo_updates = pd.DataFrame(daily_demo_updates)
        fig2 = px.line(
            daily_demo_updates, 
            x = 'date', 
            y = 'total_updates',
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("State-wise Total Updates")
        fig3 = px.bar(df.groupby("state_final", as_index=False).size(),x="state_final", y='size')
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Top 10 states with highest Updates")
        fig4 = px.funnel(df.groupby("state_final")["total_updates"].sum().sort_values(ascending=False))
        fig4.update_traces(textinfo='none')
        st.plotly_chart(fig4, use_container_width=True)
    
    st.subheader("Hierarchy of Updates: State & District")
    fig_tree = px.treemap(
        df, 
        path=['state_final', 'district_clean'], 
        values='total_updates',
        color='total_updates',
        color_continuous_scale='Blues',
        hover_data=['age_5_17_count', 'age_17_plus_count']
    )
    fig_tree.update_layout(margin=dict(t=30, l=10, r=10, b=10))
    st.plotly_chart(fig_tree, use_container_width=True)

elif dataset == "Biometrics Analytics":
    st.markdown("Comprehensive analysis of Aadhaar **Biometrics** data across India")
    df = bio_df.copy()
    st.sidebar.header("Filters")
    states = st.sidebar.multiselect("Select State", df["state_final"].unique())
    if states:
        df = df[df["state_final"].isin(states)]

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Biometric Records", f"{len(df):,}")
    k2.metric("States Covered", df["state_final"].nunique())
    k3.metric("Districts Covered", df["district_final"].nunique())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total Biometrics by state")
        fig1 = px.histogram(df, x="state_final", y = "total_biometric")
        fig1.update_xaxes(title_text="State")
        fig1.update_yaxes(title_text="Total Biometrics")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2: 
        st.subheader("Age group wise distribution")
        age_totals = df[["bio_age_5_17", "bio_age_17_"]].sum().reset_index()
        age_totals.columns = ["Age Group", "Total Biometrics"]
        fig2 = px.pie(
        age_totals,
        names="Age Group",
        values="Total Biometrics",
        hole=0.5,
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)

    with col3: 
        st.subheader("Monthly Biometric Trend")
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.strftime('%B %Y')
        monthly_df = df.groupby(['month'])['total_biometric'].sum().reset_index()
        fig_monthly = px.bar(
        monthly_df, 
        x='total_biometric', 
        y='month', 
        orientation='h',
        text_auto='.2s', # Adds shortened labels like 1.2k
        color='total_biometric',
        color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col4: 
        st.subheader("Top 10 Districts by Biometrics")
        top_districts = df.groupby('district_final')['total_biometric'].sum().nlargest(10).reset_index()
        fig_dist = px.funnel(
        top_districts, 
        x='total_biometric', 
        y='district_final', 
        text='total_biometric'
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    
    st.subheader("Adult vs. Child Update Correlation")
    fig_scatter = px.scatter(
    df, 
    x="bio_age_5_17", 
    y="bio_age_17_", 
    color="state_final",       
    size="total_biometric",    
    hover_name="district_final",
    size_max=15,
    labels={
    "bio_age_5_17": "Child Updates (5-17)",
    "bio_age_17_": "Adult Updates (17+)"
    }
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

elif dataset == "Enrollment Forecast":
    st.title("📈 Enrollment Forecast")

    forecast = pd.read_csv("enrollment_forecast.csv")
    forecast['date'] = pd.to_datetime(forecast['date'])

    avg_pred = int(forecast['predicted_enrolments'].mean())
    peak_pred = int(forecast['predicted_enrolments'].max())

    col1, col2 = st.columns(2)
    col1.metric("Avg Predicted Enrollments", avg_pred)
    col2.metric("Peak Predicted Enrollments", peak_pred)

    st.line_chart(
        forecast.set_index('date')['predicted_enrolments']
    )
    peak_pred = forecast['predicted_enrolments'].max()

    historical = enrol_df.groupby('date')['total_enrolments'].sum().reset_index()
    historical_avg = historical['total_enrolments'].mean()

    threshold = historical_avg * 1.3  # 30% surge threshold

    st.subheader("⚠️ Enrollment Surge Detection")

    if peak_pred > threshold:
        st.error("🚨 Predicted enrollment surge detected. Advance planning recommended.")
    else:
        st.success("✅ Enrollment levels expected to remain stable.")


else: 
    st.set_page_config(page_title="Aadhaar Early Warning System", layout="wide")
    st.title("🚨 Aadhaar Early-Warning & Quality Monitoring System 🚨")

    @st.cache_data
    def load_data():
        enrol = pd.read_csv("cleaned_data_enrol.csv")
        demo = pd.read_csv("demographic_cleaned.csv")
        bio = pd.read_csv("Biometric_data.csv")
        enrol = clean_columns(enrol)
        demo = clean_columns(demo)
        bio = clean_columns(bio)
        return enrol, demo, bio


    enrol_df, demo_df, bio_df = load_data()
    state = st.selectbox("Select State", sorted(enrol_df['state_final'].unique()))
    district = st.selectbox(
        "Select District",
        sorted(enrol_df[enrol_df['state_final'] == state]['district_clean'].unique())
    )

    enrol_d = enrol_df[(enrol_df['state_final'] == state) & (enrol_df['district_clean'] == district)]
    demo_d = demo_df[(demo_df['state_final'] == state) & (demo_df['district_clean'] == district)]
    bio_d = bio_df[(bio_df['state_final'] == state) & (bio_df['district_final'] == district)]

    load_pct, e_flag = enrolment_load(enrol_d, enrol_df, state)
    d_flag = demographic_check(demo_d)
    failure_rate, b_flag = biometric_quality(bio_d)
    alerts = generate_alerts(e_flag, d_flag, b_flag)

    st.subheader(f"🗺️ District: **{district}**, State: **{state}**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Enrolment Load (%)", load_pct, e_flag)
    col2.metric("Demographic Status", d_flag)
    col3.metric("Biometric Quality Failure Rate", failure_rate)

    st.subheader("🚨 System Alerts")

    for a in alerts:
        st.warning(a)

    with st.expander("View Raw Data"):
        st.write("Enrolment Data", enrol_d)
        st.write("Demographic Data", demo_d)
        st.write("Biometric Data", bio_d)