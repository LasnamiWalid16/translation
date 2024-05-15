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
    st.title("Todays stats")
    st.write(result_df)
    
    # Calculate monthly totals
    translations_df['month'] = translations_df['created_at'].dt.to_period('M')
    monthly_totals = translations_df.groupby('month')['total'].sum().reset_index()
    st.title("Monthly Totals")
    st.write(monthly_totals)
    


def daily_stats():
    # Load MongoDB connection details from Streamlit secrets
    MONGO_DETAILS = st.secrets["FASTAPI_URL"]["MONGO_DETAILS"]

    # Connect to MongoDB
    client = MongoClient(MONGO_DETAILS)
    db = client.translation
    #collection = db['translations']
    # Specify the fields you want to project
    projection = {
        "_id": 0,
        "payments": 1,
    }

    # Get translations with projection
    data = []
    for document in db.translations.find({}, projection):
        for payment in document['payments']:
            data.append({
                'created_at': payment['created_at'],
                'price': payment['price']
            })

    # Create DataFrame
    df = pd.DataFrame(data)

    # Convert 'created_at' to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Group by date and sum of price
    df['date'] = df['created_at'].dt.date
    result_df = df.groupby('date')['price'].sum().reset_index()
    
    # Sort the DataFrame by date in descending order
    result_df = result_df.sort_values(by='date', ascending=False)

    
    st.title("Daily Payments")
    st.write(result_df)

    # Group by month
    monthly_df = result_df.copy()
    monthly_df['month'] = monthly_df['date'].apply(lambda x: x.strftime('%Y-%m'))
    monthly_df = monthly_df.groupby('month')['price'].sum().reset_index()

    st.title("Monthly Payments")
    st.write(monthly_df)