import streamlit as st
import requests

# Define the function to query OpenFDA
def query_openfda(drug_name):
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}&limit=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            return data["results"][0]  # Return the first result
        else:
            st.warning(f"No data found for the drug: {drug_name}")
            return None
    else:
        st.error(f"Error {response.status_code}: Could not retrieve data from OpenFDA")
        return None

# Function to filter and organize the drug information
def organize_drug_info(drug_json):
    fields = {
        'Brand Name': ['openfda', 'brand_name'],
        'Generic Name': ['openfda', 'generic_name'],
        'Indications': ['indications_and_usage'],
        'Warnings': ['warnings'],
        'Dosage': ['dosage_and_administration'],
        'Forms and Strength': ['dosage_forms_and_strengths'],
        'Contraindications': ['contraindications'],
        'Precautions': ['warnings_and_cautions'],
        'Adverse Reactions': ['adverse_reactions'],
        'Drug Interactions': ['drug_interactions'],
        'Pregnancy': ['pregnancy'],
        'Pediatric Use': ['pediatric_use'],
        'Geriatric Use': ['geriatric_use'],
        'Overdose': ['overdosage'],
        'Mechanism of Action': ['mechanism_of_action'],
        'Pharmacodynamics': ['pharmacodynamics'],
        'Pharmacokinetics': ['pharmacokinetics'],
        'Clinical Studies': ['clinical_studies'],
        'How Supplied': ['how_supplied'],
        'Instructions for Use': ['instructions_for_use'],
        'NDC': ['package_ndc']
    }
    
    drug_info = {}
    
    for field, path in fields.items():
        try:
            # Traverse the JSON data based on the path in the fields dictionary
            data = drug_json
            for key in path:
                data = data[key]  # Drill down to the required data
            drug_info[field] = data[0] if isinstance(data, list) else data
        except (KeyError, IndexError):
            drug_info[field] = "Information not available"
    
    return drug_info

# Function to filter the relevant information based on user's question
def filter_drug_info_by_question(drug_info, user_question):
    # Define keywords for each category
    keyword_mapping = {
        'Brand Name': ['brand', 'name'],
        'Generic Name': ['generic', 'name'],
        'Indications': ['indication', 'use', 'treat'],
        'Warnings': ['warning', 'risk', 'caution'],
        'Dosage': ['dosage', 'dose', 'administer'],
        'Forms and Strength': ['form', 'strength'],
        'Contraindications': ['contraindication', 'not use', 'avoid'],
        'Precautions': ['precaution', 'caution', 'warning'],
        'Adverse Reactions': ['adverse', 'reaction', 'side effect'],
        'Drug Interactions': ['interaction', 'mix', 'drug interaction'],
        'Pregnancy': ['pregnancy', 'pregnant', 'breastfeeding'],
        'Pediatric Use': ['pediatric', 'child', 'children'],
        'Geriatric Use': ['geriatric', 'elderly'],
        'Overdose': ['overdose'],
        'Mechanism of Action': ['mechanism', 'action'],
        'Pharmacodynamics': ['pharmacodynamics', 'effect'],
        'Pharmacokinetics': ['pharmacokinetics', 'absorption'],
        'Clinical Studies': ['clinical study', 'research'],
        'How Supplied': ['supplied', 'package'],
        'Instructions for Use': ['instructions', 'how to use'],
        'NDC': ['ndc', 'code']
    }
    
    # Filter based on keywords in the user question
    relevant_info = {}
    for key, keywords in keyword_mapping.items():
        if any(keyword in user_question.lower() for keyword in keywords):
            relevant_info[key] = drug_info.get(key, "Information not available")
    
    return relevant_info

# Streamlit app code
st.title("Clinical Drug Information Query")

# Input fields for drug name and user's clinical question
drug_name = st.text_input("Enter the drug name:")
user_question = st.text_area("Enter your clinical question:")

if st.button("Get Drug Information"):
    if drug_name and user_question:
        # Query OpenFDA for the drug data
        drug_data = query_openfda(drug_name)
        
        if drug_data:
            # Organize the drug information
            drug_info = organize_drug_info(drug_data)
            
            # Filter the drug information based on the user's question
            filtered_info = filter_drug_info_by_question(drug_info, user_question)
            
            # Display the filtered information
            for key, value in filtered_info.items():
                st.write(f"**{key}:** {value}")
