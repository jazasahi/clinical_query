import streamlit as st
import openai
import requests

# Hide API key using Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Single input for drug name and clinical question
user_query = st.text_input("Enter your clinical question (include the drug name in the query):")

# Function to search for the drug name in the OpenFDA database
def search_drug_name_in_query(query):
    words = query.split()
    for word in words:
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{word}"
        response = requests.get(url)
        if response.status_code == 200 and 'results' in response.json():
            return word, response.json()
    return None, None

if user_query:
    # Try to find the drug name from the user's query
    drug_name, drug_json = search_drug_name_in_query(user_query)

    if drug_name and drug_json:
        # Extract relevant drug information
        def extract_drug_info(drug_json):
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

        # Get the drug information from OpenFDA
        drug_info = extract_drug_info(drug_json)

        # Prepare the prompt for the LLM
        prompt = f"""
        Your task is to help a clinician answer a clinical question based on the drug's information from FDA package inserts.
        The question is: "{user_query}"
        The relevant drug data is provided below:
        ```{drug_info}```

        Provide a professional and concise answer based on the question and drug data. Focus on the facts, and organize the answer for a clinician.
        """

        # Get a response from OpenAI using the new ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sarcastic assistant for clinicians."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )

        # Output the response
        st.write(response['choices'][0]['message']['content'])
    else:
        st.write("Could not retrieve data from OpenFDA. Make sure the drug name is included in your query.")
