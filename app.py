import streamlit as st
import pandas as pd
import pickle
import json

model = pickle.load(open('model.pkl', 'rb'))
columns = json.load(open('columns.json', 'r'))
threshold = json.load(open('threshold.json', 'r'))['threshold']

st.set_page_config(page_title="Churn Predictor", page_icon="📡")
st.title("📡 Customer Churn Predictor")
st.write("Fill in the customer details below to predict whether they will churn.")

col1, col2 = st.columns(2)

with col1:
    tenure = st.slider("Tenure (months)", 0, 72, 12)
    monthly_charges = st.number_input("Monthly Charges ($)", 0.0, 150.0, 65.0)
    contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])

with col2:
    senior_citizen = st.selectbox("Senior Citizen", ["No", "Yes"])
    partner = st.selectbox("Has Partner", ["Yes", "No"])
    dependents = st.selectbox("Has Dependents", ["Yes", "No"])
    payment_method = st.selectbox("Payment Method", [
        "Electronic check", "Mailed check",
        "Bank transfer (automatic)", "Credit card (automatic)"
    ])

tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
total_charges = monthly_charges * tenure

input_dict = {
    'Tenure Months': tenure,
    'Monthly Charges': monthly_charges,
    'Total Charges': total_charges,
    'CLTV': 3000,
    'Senior Citizen_Yes': 1 if senior_citizen == "Yes" else 0,
    'Partner_Yes': 1 if partner == "Yes" else 0,
    'Dependents_Yes': 1 if dependents == "Yes" else 0,
    'Paperless Billing_Yes': 1 if paperless_billing == "Yes" else 0,
    'Contract_One year': 1 if contract == "One year" else 0,
    'Contract_Two year': 1 if contract == "Two year" else 0,
    'Internet Service_Fiber optic': 1 if internet_service == "Fiber optic" else 0,
    'Internet Service_No': 1 if internet_service == "No" else 0,
    'Tech Support_No internet service': 1 if tech_support == "No internet service" else 0,
    'Tech Support_Yes': 1 if tech_support == "Yes" else 0,
    'Payment Method_Credit card (automatic)': 1 if payment_method == "Credit card (automatic)" else 0,
    'Payment Method_Electronic check': 1 if payment_method == "Electronic check" else 0,
    'Payment Method_Mailed check': 1 if payment_method == "Mailed check" else 0,
}

input_df = pd.DataFrame(columns=columns)
input_df.loc[0] = 0
for key, value in input_dict.items():
    if key in input_df.columns:
        input_df[key] = value

if st.button("🔍 Predict Churn"):
    prob = model.predict_proba(input_df)[0][1]
    prediction = int(prob >= threshold)
    percentage = round(prob * 100, 1)

    st.divider()
    st.subheader("Prediction Result")
    st.progress(prob)

    if prediction == 1 and prob >= 0.6:
        st.error(f"⚠️ High Risk of Churn: {percentage}% probability")
        st.write("**Recommendation:** Offer a discounted long-term contract or loyalty reward immediately.")
    elif prediction == 1 and prob >= threshold:
        st.warning(f"⚠️ Medium Risk of Churn: {percentage}% probability")
        st.write("**Recommendation:** Monitor closely and reach out proactively with a retention offer.")
    else:
        st.success(f"✅ Low Risk of Churn: {percentage}% probability")
        st.write("**Recommendation:** Customer appears loyal. Maintain current service quality.")

    st.divider()
    st.subheader("Details")
    col3, col4, col5 = st.columns(3)
    col3.metric("Churn Probability", f"{percentage}%")
    col4.metric("Threshold Used", f"{int(threshold*100)}%")
    col5.metric("Prediction", "Will Churn" if prediction == 1 else "Will Stay")