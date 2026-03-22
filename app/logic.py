from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,SystemMessage

from extract import extract_text_pdf,extract_text_pdf_ocr,extract_relevant_snippets
from schema import State,ContractOutput

from langgraph.graph import START,END,StateGraph

import os
# from dotenv import load_dotenv



#load_dotenv()
llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="qwen/qwen3-32b",
        temperature=0.1,
    ).with_structured_output(ContractOutput)




sys_mess = """
Tu reçois du texte extrait d'un contrat de travail.

Ta mission est d'extraire uniquement les informations utiles au calcul d'une estimation de salaire.

Tu dois remplir exactement le schéma demandé avec les champs suivants :

- periode (toujours au format dd/mm/yyyy):
    - debut : date de début du contrat ou de la mission 
    - fin : date de fin du contrat ou de la mission

- base_hours :
    - type parmi ["hebdomadaire", "mensuel", "mission", "inconnu"]
    - valeur : nombre d'heures de base prévu au contrat
    Exemples :
    - 35 heures par semaine -> type="hebdomadaire", valeur=35
    - 151,67 heures par mois -> type="mensuel", valeur=151.67
    - mission de quelques heures -> type="mission"

- base_hourly_rate :
    - taux horaire brut de base
    - si plusieurs taux existent, prends le taux horaire normal de référence, pas les taux majorés

- base_salary_reference :
    - salaire mensuel ou montant de référence si clairement indiqué
    - utile seulement comme information complémentaire ou de secours

- daily_hours :
    - nombre d'heures travaillées sur une journée si une plage horaire claire est indiquée, s'il y en a plusieurs, prend la plus petite
    - exemple : 10H00 à 16H30 = 6.5 

- mission_days :
    - nombre de jours couverts par la mission si la période est courte et clairement identifiable
    - exemple : du 11/04/2022 au 16/04/2022 = 5  

- special_rate_rules :
    - retourne uniquement les règles spéciales détectées dans le contrat parmi :
        - night
        - sunday
        - holiday
    - pour chaque règle :
        - label parmi ["night", "sunday", "holiday"]
        - type parmi ["percent", "hourly_rate", "hourly_bonus"]
        - value numérique
        - condition si utile

Interprétation des types :
- percent = pourcentage de majoration, exemple 50 pour +50%
- hourly_rate = taux horaire spécial complet, exemple 17.2 €/h
- hourly_bonus = supplément horaire ajouté au taux de base, exemple 1.231 €/h

Règles importantes :
- priviligie l'extraction des heures journalières ou hedomadaires par rapport aux heures mensuelles si le contrat contient les deux informations.
- N'extrais PAS les règles d'heures supplémentaires.
- N'extrais PAS les primes de repas, salissure, panier ou autres primes fixes dans special_rate_rules.
- Ne prends pas une date isolée non liée à la mission comme période.
- Si une information est absente, mets null.
- Si une information est ambiguë, mets null et explique brièvement dans commentaire.
- Ne devine pas.
"""


def extraction(state:State):
    pdf_path = state["messages"][-1].content
    text_raw = extract_text_pdf(pdf_path=pdf_path)
    

    if text_raw.strip() == "":
        text_raw = extract_text_pdf_ocr(pdf_path=pdf_path)
        if text_raw.strip() == "":
            return {"retrieved_text":"","trust":False}

      
    text = extract_relevant_snippets(text=text_raw)
    if text.strip() == "":
         return {"retrieved_text":"","trust":False}
        
    
    return {"retrieved_text":text,"trust":True}



def llm_response(state:State):
    text = state["retrieved_text"]
     
    if state["trust"]:

        final_output= llm.invoke([
                SystemMessage(content=sys_mess),
                HumanMessage(content= f"Voici le texte extrait du contrat: {text}")
            ])
        
        return {"final_output":final_output,"comment":None}
    
    return {"final_output":None,"comment":"Une erreur s'est produit, vérifiez que votre fichier (contrat) est bien un pdf (nom du fichier se terminant par .pdf) et qu'il est de bonne qualité."}


# def output_validation(state:State):
    
#     llm_text = state["messages"][-1].content

#     try:
#         final_output = ContratOutput.model_validate(llm_text).model_dump()
#         print("It's okay")
#     except ValidationError as ve:
#         print(f"Erreur lors de la validation pydantic: {ve}")
    
#     return {"final_output":final_output}



def make_agent():

    graph=StateGraph(State)

    graph.add_node("extractor",extraction)
    graph.add_node("llm",llm_response)
    #graph.add_node("validator",output_validation)

    graph.add_edge(START,"extractor")
    graph.add_edge("extractor","llm")
    #graph.add_edge("llm","validator")
    graph.add_edge("llm",END)

    return graph.compile()


""""""

agent = make_agent()
# # Use a HumanMessage to properly format the input
# from langchain_core.messages import HumanMessage

# path1=r"app\Contrat_04-06Juillet_short.pdf"
# path2=r"app\Contrat_Test_Dupont.pdf"
# path3=r"app\izi1.pdf"
# path4=r"app\izi2.pdf"
# path = r"app\pdf\scalaire_esther (3).pdf"
# path1 = r"app\pdf\grand perroquet.webp"


# events = agent.stream(
#    {"messages": [HumanMessage(content=path1)]},
#     stream_mode="values"
# )


# for event in events:
#     msg= event["messages"] if "messages" in event and event["messages"] else None
#     txt = event["retrieved_text"] if "retrieved_text" in  event and event["retrieved_text"] else None
#     final = event["final_output"] if "final_output" in event and event["final_output"] else None
#     comment = event["comment"] if "comment" in event and event["comment"] else None


# print("message : ",msg)
# print("********************************************")
# print("texte : ",txt)
# print("********************************************")
# print("final : ",final.model_dump() if hasattr(final,"model_dump") else final)
# print("********************************************")
# print("comment:",comment)
# for event in events:
#     msg = event["messages"] if "messages" in event and event["messages"] else None
#     tch = event["tech"] if "tech" in event and event["tech"] else None
#     nw = event["news"] if "news" in event and event["news"] else None
#     fl = event["final"] if "final" in event and event["final"] else None


