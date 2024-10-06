from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()
client = InferenceClient(api_key=os.getenv('HUGGINGFACE_KEY'))

def summarize(info, agent_prompt=True, model='meta-llama/Llama-3.2-3B-Instruct', max_tokens=2000):
	if agent_prompt:
		agent_prompt = """
						You are an expert medical data analyst. You are given structured patient data, with the first code being the patient's ID. Your task is to directly output a detailed yet concise summary of all relevant information about the patient, excluding their ID, in under 1500 words. The summary should cover the patient's conditions, medications, immunizations, procedures, care plans, observations, encounters, allergies, and any other critical health information. Important dates (such as for medications, procedures, and immunizations) must be included in the summary.

						The response must not include any code or instructions on how to read the JSON. Simply return a structured JSON object in this format:
						{
						"p_id": "<patient's ID>",
						"summary": "<all about the patient in a single string (can be formatted in Markdown), excluding new lines, but including important dates, remove any repeated phrases/words>"
						}
						Make sure the summary is clear, comprehensive, and includes relevant dates alongside medications, procedures, and immunizations. Do not write any code or provide any implementation details—just the JSON object as specified. 
						"""
	else:
		agent_prompt = ''
	response = client.chat_completion(
        model=model,
        messages=[{"role": "user", "content": f"{agent_prompt} : {info}"}],
		max_tokens=max_tokens,
        temperature=0.2,
        stream=False
    )
	# print(response.choices[0].message.content)
	return response.choices[0].message.content

def main():
	summarize("""
{'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85': {'age': 5, 'gender': 'M', 'profile': defaultdict(None, {'allergies': [('Animal dander (substance)', 'allergy'), ('Aspirin', 'allergy'), ("Cow's milk (substance)", 'allergy'), ('Grass pollen (substance)', 'allergy'), ('House dust mite (organism)', 'allergy'), ('Latex (substance)', 'allergy'), ('Mold (organism)', 'allergy'), ('Shellfish (substance)', 'allergy'), ('Soya bean (substance)', 'allergy')], 'conditions': [(None, None, None)], 'immunizations': [('DTaP',), ('DTaP',), ('DTaP',), ('DTaP',), ('Hep A  ped/adol  2 dose',), ('Hep A  ped/adol  2 dose',), ('Hep B  adolescent or pediatric',), ('Hep B  adolescent or pediatric',), ('Hep B  adolescent or pediatric',), ('Hib (PRP-OMP)',), ('Hib (PRP-OMP)',), ('Hib (PRP-OMP)',), ('IPV',), ('IPV',),ep B  adolescent or pediatric',), ('Hib (PRP-OMP)',), ('Hib (PRP-OMP)',), ('Hib (PRP-OMP)',), ('IPV',), ('IPV',), ('IPV',), ('Influenza  seasonal  injectable  preservative free',), ('Influenza  seasonal  injectable  preservative free',), ('MMR',), ('Pneumococcal conjugate PCV 13',), ('Pneumococcal conjugate PCV 13',), ('Pneumococcal conjugate PCV 13',), ('Pneumococcal conjugate PCV 13',), ('rotavirus  monovalent',), ('rotavirus  monovalent',), ('varicella',)], 'medications': [('2020-02-17T10:40:32Z', None, 'NDA020800 0.3 ML Epinephrine 1 MG/ML Auto-Injector'), ('2020-02-17T10:40:32Z', None, 'cetirizine hydrochloride 5 MG Oral Tablet')], 'observations': [('survey', 'Tobacco smoking status NHIS', 'Never smoker', None, 'text'), ('vital-signs', 'Body Height', '88.8', 'cm', 'numeric'), ('vital-signs', 'Body Mass Index', '16.3', 'kg/m2', 'numeric'), ('vital-signs', 'Body Weight', '12.9', 'kg', 'numeric'), ('vital-signs', 'Body mass index (BMI) [Percentile] Per age and gender', '51.1', '%', 'numeric'), ('vital-signs', 'Diastolic Blood Pressure', '72.0', 'mm[Hg]', 'numeric'), ('vital-signs', 'Head Occipital-frontal circumference', '48.5', 'cm', 'numeric'), ('vital-signs', 'Heart rate', '62.0', '/min', 'numeric'), ('vital-signs', 'Pain severity - 0-10 verbal numeric rating [Score] - Reported', '2.0', '{score}', 'numeric'), ('vital-signs', 'Respiratory rate', '13.0', '/min', 'numeric'), ('vital-signs', 'Systolic Blood Pressure', '118.0', 'mm[Hg]', 'numeric'), ('vital-signs', 'Weight-for-length Per age and sex', '49.0', '%', 'numeric')], 'procedures': [('2019-02-17T05:07:38Z', '2019-02-17T05:22:38Z', 'Medication Reconciliation (procedure)'), ('2019-05-26T05:07:38Z', '2019-05-26T05:22:38Z', 'Medication Reconciliation (procedure)'), ('2019-07-28T05:07:38Z', '2019-07-28T05:22:38Z', 'Medication Reconciliation (procedure)'), ('2020-02-17T10:07:38Z', '2020-02-17T10:40:32Z', 'Allergy screening test'), ('2020-04-26T05:07:38Z', '2020-04-26T05:22:38Z', 'Medication Reconciliation (procedure)'), ('2021-01-24T05:07:38Z', '2021-01-24T05:22:38Z', 'Medication Reconciliation (procedure)')]})}}""")

if __name__ == "__main__":
	main()