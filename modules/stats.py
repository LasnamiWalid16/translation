import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta


def stats():
    # Load MongoDB connection details from Streamlit secrets
    MONGO_DETAILS = st.secrets["FASTAPI_URL"]["MONGO_DETAILS"]

    # Connect to MongoDB
    client = MongoClient(MONGO_DETAILS)

    db = client.translation

    # Specify the fields you want to project
    projection = {
        "client_id": 1,
        "work_status": 1,
        "payment_status": 1,
        "total": 1,
        "rest": 1,
        "payment": 1,
        "created_at": 1,
        "updated_at": 1,
    }

    # Get translations with projection
    translations = db.translations.find({}, projection)
    translations_df = pd.DataFrame(translations)

    # Calculate and display total and rest
    total_sum = translations_df['total'].sum()
    rest_sum = translations_df['rest'].sum()
    st.write(f"Total: {total_sum}")
    st.write(f"Rest: {rest_sum}")

    # Calculate today's total and payment
    today = datetime.now().strftime('%Y-%m-%d')
    today_total = translations_df[translations_df['created_at'].dt.strftime('%Y-%m-%d') == today]['total'].sum()
    today_payment = translations_df[translations_df['created_at'].dt.strftime('%Y-%m-%d') == today]['payment'].sum()
    st.write(f"Today's Total: {today_total}")
    st.write(f"Today's Payment: {today_payment}")