import streamlit as st
import pandas as pd
import requests


FASTAPI_URL = st.secrets.FASTAPI_URL.FASTAPI_URL 

# Function to add a new translation
def add_new_translation():
    #get clients
    response_client = requests.get(f"{FASTAPI_URL}/client/")
    if response_client.status_code == 200:
        data_response_client = response_client.json()
        client_data = data_response_client.get("data", [])

        # Flatten the nested structure and extract the "_id" and "last_name" fields
        clients_list = [{"_id": doc.get("id", ""), "last_name": doc.get("last_name", ""), "first_name": doc.get("first_name", "")} for sublist in client_data for doc in sublist]

        # Create a pandas DataFrame
        clients_df = pd.DataFrame(clients_list, columns=["_id", "last_name","first_name"])
        clients_df["full_name"] = clients_df["last_name"] + " " + clients_df["first_name"]

        client_full_names = clients_df["full_name"].tolist()
        #client_ids = clients_df["_id"].tolist()
    
    else:
        st.error(f"Failed to fetch client data. Status code: {response_client.status_code}")

    #get documents
    response_document = requests.get(f"{FASTAPI_URL}/document/")
    if response_document.status_code == 200:
        data_response_document = response_document.json()
        document_data = data_response_document.get("data", [])

        # Flatten the nested structure and extract the "_id" and "name" fields
        documents_list = [{"_id": doc.get("id", ""), "name": doc.get("name", "")} for sublist in document_data for doc in sublist]

        # Create a pandas DataFrame
        documents_df = pd.DataFrame(documents_list, columns=["_id", "name"])

        document_names = documents_df["name"].tolist()
    
    else:
        st.error(f"Failed to fetch document data. Status code: {response_document.status_code}")

    st.title('New Translation')

    if 'stage' not in st.session_state:
        st.session_state.stage = 0

    def set_stage(stage):
        st.session_state.stage = stage

    selected_client = st.selectbox("Select a Client", options=client_full_names)
    n_lines = st.number_input('Number of documents to translate', 0, 10)
    discount = st.number_input('Discount %', 0, 50)
    
    
    with st.form(key="translation_form"):
        languages = ['ARB->FR','ARB->ANG','FR->ARB','FR->ANG','ANG->ARB','ANG->FR']
        forms_dict = {}
        for i in range(n_lines):
            st.markdown(f"## Document {i + 1}")
            document = st.selectbox(f'Document name {i + 1}', options=document_names)
            language = st.selectbox(f'Language {i + 1}', options=languages)
            price = st.number_input(f'Price {i + 1}', min_value=1000, max_value=10000)
            nb_copies = st.number_input(f'Number of Copies {i + 1}', min_value=1, max_value=100)

            # Use a unique key for each form
            key = f"form_{i}"

            # Store the values in the forms_dict with the unique key
            forms_dict[key] = {'Document': documents_df[documents_df['name']==document].iloc[0]['_id'],'language':language, 'Price': price, 'Number of Copies': nb_copies}

        # Use st.form_submit_button for final submission
        submit_button = st.form_submit_button('Submit All', on_click=set_stage, args=(1,))

        if st.session_state.stage > 0:
            # Handle the final submission
            if submit_button:
                # Prepare data for the translation
                id_selected_client = clients_df[clients_df['full_name']==selected_client].iloc[0]['_id']
                
                translation_data = {
                    "client_id": id_selected_client,
                    "work_status" : "not_yet",
                    "payment_status" : "not_yet",
                    "discount" : discount,
                    "total_without_discount" : 0,
                    "total": 0,
                    "rest":0,
                    "payment": 0,
                    "documents": [
                        {
                            "document_id": forms_dict[f"form_{i}"]["Document"],
                            "language": forms_dict[f"form_{i}"]["language"],
                            "price": forms_dict[f"form_{i}"]["Price"],
                            "nb_copies": forms_dict[f"form_{i}"]["Number of Copies"],
                        }
                        for i in range(n_lines)
                    ],
                }
                total_without_discount = sum(doc['price'] * doc['nb_copies'] for doc in translation_data['documents'])
                total = total_without_discount - (translation_data['discount'] * total_without_discount / 100)
                translation_data['total'] = total
                translation_data['total_without_discount'] = total_without_discount
                translation_data['rest'] = total
                
                
                
                # Make the API call for translation
                #response_translation = requests.post(f"{FASTAPI_URL}/translation", json=translation_data)
                response_translation = requests.post(FASTAPI_URL + "/translation/", json=translation_data)

                if response_translation.status_code == 200:
                    st.success("Translation added successfully!")
                else:
                    st.error(f"Failed to add translation. Status code: {response_translation.status_code}")


# Function to view all clients
def view_all_trasnlations():
    st.title('All Translations')
    
        #get clients
    response_client = requests.get(f"{FASTAPI_URL}/client/")
    if response_client.status_code == 200:
        data_response_client = response_client.json()
        client_data = data_response_client.get("data", [])

        # Flatten the nested structure and extract the "_id" and "last_name" fields
        clients_list = [{"_id": doc.get("id", ""), "last_name": doc.get("last_name", ""), "first_name": doc.get("first_name", ""),
                         "phone": doc.get("phone", "")} for sublist in client_data for doc in sublist]

        # Create a pandas DataFrame
        clients_df = pd.DataFrame(clients_list, columns=["_id", "last_name","first_name","phone"])
        clients_df["full_name"] = clients_df["last_name"] + " " + clients_df["first_name"]
        clients_df = clients_df[["_id","full_name","phone"]]
    else:
        st.error(f"Failed to fetch client data. Status code: {response_client.status_code}")

    # Make a GET request to retrieve all translations
    response = requests.get(FASTAPI_URL + "/translation/")

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json().get("data", [])

        # Extract relevant information from nested structure
        translations_data = []
        for sublist in data:
            for translation_dict in sublist:
                translations_data.append({
                    "id": translation_dict.get("id", ""),
                    "client_id": translation_dict.get("client_id", ""),
                    "work_status": translation_dict.get("work_status", ""),
                    "payment_status": translation_dict.get("payment_status", ""),
                    "discount": translation_dict.get("discount", ""),
                    "total_without_discount": translation_dict.get("total_without_discount", ""),
                    "total": translation_dict.get("total", ""),
                    "rest": translation_dict.get("rest", ""),
                    "payment": translation_dict.get("payment", ""),
                    "created_at": translation_dict.get("created_at", ""),
                })

        # Display the translations in a DataFrame
        translations_df = pd.DataFrame(translations_data)
        
        #join translations_df with clients_df
        result_inner = pd.merge(translations_df, clients_df, left_on='client_id', right_on='_id', how='inner')
        result_inner = result_inner[['full_name','phone','work_status','payment_status','discount','total_without_discount'
                                     ,'total','rest','payment','created_at']]
        result_inner['created_at'] = pd.to_datetime(result_inner['created_at'])
        result_inner['created_at'] = result_inner['created_at'].dt.date
        
        # Sidebar with select box for payment status
        selected_work_status = st.sidebar.selectbox('Select work_status', result_inner['work_status'].unique())
        selected_payment_status = st.sidebar.selectbox('Select Payment Status', result_inner['payment_status'].unique())
        # Filter the DataFrame based on the selected payment status
        filtered_df = result_inner[(result_inner['work_status'] == selected_work_status) & (result_inner['payment_status'] == selected_payment_status) ]
        #filtered_df = result_inner[result_inner['payment_status'] == selected_payment_status]
        # Display the filtered DataFrame
        st.write('Filtered DataFrame:', filtered_df)
        

    else:
        st.error(f"Error: Unable to retrieve translations. Status Code: {response.status_code}")
        st.text(response.text)  # Print the response content for debugging
        

# Function to view all clients
def update_trasnlation():
    st.title('All Translations')
    
        #get clients
    response_client = requests.get(f"{FASTAPI_URL}/client/")
    if response_client.status_code == 200:
        data_response_client = response_client.json()
        client_data = data_response_client.get("data", [])

        # Flatten the nested structure and extract the "_id" and "last_name" fields
        clients_list = [{"_id": doc.get("id", ""), "last_name": doc.get("last_name", ""), "first_name": doc.get("first_name", ""),
                         "phone": doc.get("phone", "")} for sublist in client_data for doc in sublist]

        # Create a pandas DataFrame
        clients_df = pd.DataFrame(clients_list, columns=["_id", "last_name","first_name","phone"])
        clients_df["full_name"] = clients_df["last_name"] + " " + clients_df["first_name"]
        clients_df = clients_df[["_id","full_name","phone"]]
    else:
        st.error(f"Failed to fetch client data. Status code: {response_client.status_code}")

    # Make a GET request to retrieve all translations
    response = requests.get(FASTAPI_URL + "/translation/")

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json().get("data", [])

        # Extract relevant information from nested structure
        translations_data = []
        for sublist in data:
            for translation_dict in sublist:
                translations_data.append({
                    "id": translation_dict.get("id", ""),
                    "client_id": translation_dict.get("client_id", ""),
                    "work_status": translation_dict.get("work_status", ""),
                    "payment_status": translation_dict.get("payment_status", ""),
                    "discount": translation_dict.get("discount", ""),
                    "total_without_discount": translation_dict.get("total_without_discount", ""),
                    "total": translation_dict.get("total", ""),
                    "rest": translation_dict.get("rest", ""),
                    "payment": translation_dict.get("payment", ""),
                    "created_at": translation_dict.get("created_at", ""),
                })

        # Display the translations in a DataFrame
        translations_df = pd.DataFrame(translations_data)
        
        #join translations_df with clients_df
        result_inner = pd.merge(translations_df, clients_df, left_on='client_id', right_on='_id', how='inner')
        result_inner = result_inner[['id','full_name','phone','work_status','payment_status','discount','total_without_discount'
                                     ,'total','rest','payment','created_at']]
        result_inner['created_at'] = pd.to_datetime(result_inner['created_at'])
        result_inner['created_at'] = result_inner['created_at'].dt.date
        
        selected_client = st.sidebar.selectbox('Select Client', result_inner['full_name'].unique())
        selected_client_data = result_inner[result_inner['full_name'] == selected_client].iloc[0]

        with st.form(key="vendor_form"):
            st.write("Update Selected Client Data:")
            
            st.write("Total:", selected_client_data['total'])
            st.write("Payment:", selected_client_data['payment'])
            st.write("Rest:", selected_client_data['rest'])
            new_payment = st.number_input(label="New Payment*", value=selected_client_data['total'] - selected_client_data['payment'],
    min_value=0.0)
            work_status_options = ['not_yet', 'Done']
            new_work_status = st.selectbox(label="Work Status*", options=work_status_options, index=work_status_options.index(selected_client_data['work_status']))

            submit_button = st.form_submit_button(label="Update translation details")
            if submit_button:
                
                new_translation_data = {
                    "work_status" : new_work_status,
                    "payment_status" : 'Done' if selected_client_data['payment'] + new_payment == selected_client_data['total'] else selected_client_data['payment_status'] ,
                    "rest": selected_client_data['total'] - (selected_client_data['payment'] + new_payment),
                    "payment": selected_client_data['payment'] + new_payment,
                }
                id_translation = selected_client_data['id']
                response_translation = requests.put(FASTAPI_URL + f"/translation/{id_translation}", json=new_translation_data)
                if response_translation.status_code == 200:
                    st.success("Translation updated successfully!")
                else:
                    st.error(f"Failed to update translation. Status code: {response_translation.status_code}")
        

    else:
        st.error(f"Error: Unable to retrieve translations. Status Code: {response.status_code}")
        st.text(response.text) 