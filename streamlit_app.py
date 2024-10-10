import streamlit as st
import openai
import requests

# Hide API key using Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Single input for drug name and clinical question
user_query = st.text_input("Enter the drug name and your clinical question:")

if user_query:
    # Process the query (extracting drug info and passing to LLM)
    
    # Query OpenFDA API
    def query_openfda(drug_name):
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    # Extract relevant information from OpenFDA response
    def extract_drug_info(drug_json):
        if 'results' in drug_json:
            drug_info = {}
            fields = {
                'Brand Name': 'openfda.brand_name',
                'Generic Name': 'openfda.generic_name',
                'Indications': 'indications_and_usage',
                'Warnings': 'warnings',
                'Dosage': 'dosage_and_administration',
                'Forms and strength': 'dosage_forms_and_strengths',
                'Contraindications': 'contraindications',
                'Precautions': 'warnings_and_cautions',
                'Adverse Reactions': 'adverse_reactions',
                'Drug Interactions': 'drug_interactions',
                'Pregnancy': 'Pregnancy',
                'Pediatric use': 'pediatric_use',
                'Geriatric use': 'geriatric_use',
                'Overdose': 'overdosage',
                'Mechanism of action': 'mechanism_of_action',
                'Pharmacodynamics': 'pharmacodynamics',
                'Pharmacokinetics': 'pharmacokinetics',
                'Clinical Studies': 'clinical_studies',
                'How supplied': 'how_supplied',
                'Instructions for use': 'instructions_for_use',
                'NDC': 'package_ndc'
            }
            
            # Extract fields using loop
            for key, value in fields.items():
                try:
                    field_path = value.split('.')
                    field_data = drug_json['results'][0]
                    for path in field_path:
                        field_data = field_data[path]
                    drug_info[key] = field_data[0] if isinstance(field_data, list) else field_data
                except (KeyError, IndexError):
                    drug_info[key] = "Unknown"

            return drug_info
        else:
            return {}

    # Query OpenFDA for the drug
    drug_json = query_openfda(user_query.split()[0])  # Extract drug name from first word

    if drug_json:
        drug_info = extract_drug_info(drug_json)

        # Now, pass the combined user input and drug information to the LLM
        prompt = f"""
        Your task is to help a clinician answer a clinical question based on the drug's information from FDA package inserts.
        The question is: "{user_query}"
        The relevant drug data is provided below:
        ```{drug_info}```

        Provide a professional and concise answer based on the question and drug data. Focus on the facts, and organize the answer for a clinician.
        """

        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=500,
            temperature=0.2
        )

        st.write(response['choices'][0]['text'])
    else:
        st.write("Could not retrieve data from OpenFDA.")
