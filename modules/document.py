import streamlit as st
import pandas as pd
import requests
from os import environ as env



FASTAPI_URL = st.secrets.FASTAPI_URL.FASTAPI_URL 

# Function to add a new document
def add_new_document():
    st.title('Add New Docuemnt')
    with st.form(key="vendor_form"):
        name = st.text_input(label="Document Name*")
        description = st.text_input(label="Decription")

        st.markdown("**required*")

        submit_button = st.form_submit_button(label="Submit document Details")

        if submit_button:
            if not name:
                st.warning("Ensure all mandatory fields are filled.")
                st.stop()
            else:
                document_data = {
                    "description": description,
                    "name": name,
                }

                response = requests.post(FASTAPI_URL + "/document/", json=document_data)

                if response.status_code == 200:
                    st.success("document added successfully.")
                else:
                    st.error(f"Error: Unable to add document. Status Code: {response.status_code}")
                    st.text(response.text)  # Print the response content for debugging
                    


# Function to view all documents
def view_all_documents():
    st.title('All document')
    # Make a GET request to retrieve all documents
    response = requests.get(FASTAPI_URL + "/document/")

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json().get("data", [])

        # Extract relevant information from nested structure
        documents_data = []
        for sublist in data:
            for document_dict in sublist:
                documents_data.append({
                    "name": document_dict.get("name", ""),
                    "description": document_dict.get("description", ""),
                })

        # Display the documents in a DataFrame
        documents_df = pd.DataFrame(documents_data)
        st.dataframe(documents_df)

    else:
        st.error(f"Error: Unable to retrieve documents. Status Code: {response.status_code}")
        st.text(response.text)  # Print the response content for debugging