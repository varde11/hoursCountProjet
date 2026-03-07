from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,SystemMessage

from extract import extract_text_pdf,extract_relevant_snippets
from schema import ContratOutput,State
from pydantic import ValidationError

from langgraph.graph import START,END,StateGraph

import os
from dotenv import load_dotenv



load_dotenv()
llm = ChatGroq(
        api_key=os.getenv("myfirstApiKey"),
        model="qwen/qwen3-32b",
        temperature=0.1,
    ).with_structured_output(ContratOutput)



sys_mess = """
Tu reçois du texte extrait d'un contrat de travail.

Ta mission est d'extraire les informations suivantes dans le schéma demandé :

- periode :
    - debut
    - fin

- heures :
    - retourne une LISTE
    - chaque élément doit contenir :
        - type parmi ["hebdomadaire", "mensuel", "quotidien", "plage_horaire", "total", "inconnu"]
        - valeur (texte exact ou presque exact extrait du document)

- remuneration :
    - retourne une LISTE
    - chaque élément doit contenir :
        - type parmi ["taux_horaire", "mensuel_brut", "mensuel_net", "prime", "majoration", "inconnu"]
        - valeur numérique si identifiable
        - devise = "EUR" si non précisé autrement
        - label si utile (ex: "prime casse-croûte", "majoration dimanche", "majoration nuit")

Règles importantes :
- S'il y a plusieurs horaires, plusieurs durées ou plusieurs rémunérations, retourne-les toutes
- Ne retourne jamais un tableau à la place d'un objet simple pour `periode`
- Convertie toujours les date en format jour/mois/année
- Ne devine pas.
- Si une information n'est pas certaine, mets-la dans `commentaire`.
- Pour `valeur`, garde un nombre simple quand c'est possible.
- Pour la période, n'extrais une date de début ou de fin que si elle est clairement liée à la mission ou au contrat de travail.
- N'utilise pas une date isolée (exemple : date de naissance, date administrative) comme période de mission.
- Si aucune période de mission claire n'est trouvée, mets debut=None et fin=None.
- N'extrais pas une valeur numérique seule si son contexte n'est pas clair, sans libellé clair ne doit pas être classée
"""


def extraction(state:State):
    pdf_path = state["messages"][-1].content
    text_raw = extract_text_pdf(pdf_path=pdf_path)
    text = extract_relevant_snippets(text=text_raw)

    return {"retrieved_text":text}



def llm_response(state:State):
    text = state["retrieved_text"]

    final_output= llm.invoke([
            SystemMessage(content=sys_mess),
            HumanMessage(content= f"Voici le texte extrait du contrat: {text}")
        ])
    
    return {"final_output":final_output}


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


agent = make_agent()
# # Use a HumanMessage to properly format the input
# from langchain_core.messages import HumanMessage

path1=r"app\Contrat_04-06Juillet_short.pdf"
path2=r"app\Contrat_Test_Dupont.pdf"
path3=r"app\izi1.pdf"
path4=r"app\izi2.pdf"


events = agent.stream(
   {"messages": [HumanMessage(content=path3)]},
    stream_mode="values"
)


for event in events:
    msg= event["messages"] if "messages" in event and event["messages"] else None
    txt = event["retrieved_text"] if "retrieved_text" in  event and event["retrieved_text"] else None
    final = event["final_output"] if "final_output" in event and event["final_output"] else None


print("message : ",msg)
print("********************************************")
print("texte : ",txt)
print("********************************************")
print("final : ",final.model_dump())
# for event in events:
#     msg = event["messages"] if "messages" in event and event["messages"] else None
#     tch = event["tech"] if "tech" in event and event["tech"] else None
#     nw = event["news"] if "news" in event and event["news"] else None
#     fl = event["final"] if "final" in event and event["final"] else None