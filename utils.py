import pandas as pd

def clean_columns(df):
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    return df

def enrolment_load(enrol_d, enrol_df, state):
    district_total = enrol_d['total_enrolments'].sum()
    state_total = enrol_df[enrol_df['state_final'] == state]['total_enrolments'].sum()

    load_pct = (district_total / state_total) * 100

    if load_pct > 5:
        flag = "🔴 High Load"
    elif load_pct > 2:
        flag = "🟡 Moderate Load"
    else:
        flag = "🟢 Normal"

    return round(load_pct, 2), flag

def demographic_check(demo_d):
    if 'age_5_17_count' not in demo_d.columns or 'age_17_plus_count' not in demo_d.columns:
        return "⚪ Data Missing"

    child = demo_d['age_5_17_count'].sum()
    adult = demo_d['age_17_plus_count'].sum()
    total_pop = child + adult
    child_ratio = child / total_pop if total_pop > 0 else 0

    if child_ratio > 0.15:
        flag = "🔴 Anomaly Detected (High Child %)"
    elif child_ratio > 0.10:
        flag = "🟡 Slight Imbalance"
    else:
        flag = "🟢 Normal"

    return flag

def biometric_quality(bio_d):
    total = bio_d['total_biometric'].sum()
    age_child = bio_d['bio_age_5_17'].sum()
    age_adult = bio_d['bio_age_17_'].sum()
    success = (age_child + age_adult)
    failure_rate = 1 - (success/total)

    if failure_rate>0.15:
        flag = "🔴 Poor Quality"
    elif failure_rate > 0.08:
        flag = "🟡 Needs Attention"
    else:
        flag = "🟢 Good Quality"

    return round(failure_rate, 2), flag

def generate_alerts(e_flag, d_flag, b_flag):
    alerts = []
    if "🔴" in e_flag:
        alerts.append("High enrolment load: open temporary camps.")
    if "🔴" in d_flag:
        alerts.append("Demographic anomaly: review data quality.")
    if "🔴" in b_flag:
        alerts.append("Biometric quality poor: operator training needed.")
    if not alerts:
        alerts.append("All Aadhaar indicators normal.")

    return alerts
