import streamlit as st
import pandas as pd
import requests
from modules.client import add_new_client,view_all_clients
from modules.document import add_new_document,view_all_documents
from modules.translation import add_new_translation,view_all_trasnlations,update_trasnlation
from modules.stats import stats



# Sidebar with action selection
selected_action = st.sidebar.selectbox("Choose an Action", ["Add new Client", "View All Clients", "Add new Document","View All Documents", "Add new translation",
                                                            "View All Translations","Update translation","Stats"])

# Perform the action based on the selection
if selected_action == "Add new Client":
    add_new_client()
elif selected_action == "View All Clients":
    view_all_clients()
elif selected_action == "Add new Document":
    add_new_document()
elif selected_action == "View All Documents":
    view_all_documents()
elif selected_action == "Add new translation":
    add_new_translation()
elif selected_action == "View All Translations":
    view_all_trasnlations()
elif selected_action == "Update translation":
    update_trasnlation()
elif selected_action == "Stats":
    stats()

