import streamlit as st
import pandas as pd
import requests

FASTAPI_URL = st.secrets.FASTAPI_URL.FASTAPI_URL 

# Function to add a new client
def add_new_client():
    st.title('Add new client')
    with st.form(key="vendor_form"):
        last_name = st.text_input(label="Last Name*")
        first_name = st.text_input(label="First Name")
        phone = st.text_input(label="phone number*")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit Client Details")

        if submit_button:
            if not phone or not last_name:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                client_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone,
                    "email": 'lasnami@gmail.com',
                }

                response = requests.post(FASTAPI_URL + "/client/", json=client_data)

                if response.status_code == 200:
                    st.success("Client added successfully.")
                else:
                    st.error(f"Error: Unable to add client. Status Code: {response.status_code}")
                    st.text(response.text)  # Print the response content for debugging
    
# Function to view all clients
def view_all_clients():
    st.title('All client')

    # Make a GET request to retrieve all clients
    response = requests.get(FASTAPI_URL + "/client/")

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json().get("data", [])

        # Extract relevant information from nested structure
        clients_data = []
        for sublist in data:
            for client_dict in sublist:
                clients_data.append({
                    "last_name": client_dict.get("last_name", ""),
                    "first_name": client_dict.get("first_name", ""),
                    "phone": client_dict.get("phone", ""),
                })

        # Display the clients in a DataFrame
        clients_df = pd.DataFrame(clients_data)
             
        # #Sidebar with select box for payment status
        # clients_df["full_name"] = clients_df["last_name"] + " " + clients_df["first_name"]
        # selected_client = st.sidebar.selectbox('Select Payment Status', clients_df["full_name"].unique())
        # filtered_df = clients_df[clients_df['full_name'] == selected_client ]
  
        st.dataframe(clients_df)

    else:
        st.error(f"Error: Unable to retrieve clients. Status Code: {response.status_code}")
        st.text(response.text)  # Print the response content for debugging