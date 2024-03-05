import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

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

    # Calculate today's total and payment
    today = datetime.now().strftime('%Y-%m-%d')
    today_transactions = translations_df[translations_df['created_at'].dt.strftime('%Y-%m-%d') == today]
    today_total = today_transactions['total'].sum()
    today_payment = today_transactions['payment'].sum()

    # Create a pandas DataFrame for display
    data = {
        'Total': [total_sum],
        'Rest': [rest_sum],
        'TodayTotal': [today_total],
        'TodayPayment': [today_payment]
    }
    result_df = pd.DataFrame(data)

    # Display the DataFrame
    st.write(result_df)
    
    # Calculate monthly totals
    translations_df['month'] = translations_df['created_at'].dt.to_period('M')
    monthly_totals = translations_df.groupby('month')['total'].sum().reset_index()
    st.write("Monthly Totals")
    st.write(monthly_totals)

# Run the stats function
stats()
