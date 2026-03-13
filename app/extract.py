import fitz
import re
import unicodedata
import os



def extract_text_pdf(pdf_path: str) -> str:
    if not os.path.isfile(pdf_path) or not pdf_path.lower().endswith(".pdf"):
        return ""
    try:
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text("text",sort=True) for page in doc)
    
    except Exception :
        return ""


def normalize_text(s: str) -> str:
    s = s.replace("\u00a0", " ")              # nbsp
    s = re.sub(r"-\s*\n\s*", "", s)           # césure: "hebdo-\n madaire" -> "hebdomadaire"
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")  # remove accents
    s = re.sub(r"\s+", " ", s).strip()
    return s

KEYWORDS = [
    "heure", "heures", "duree du travail", "horaire", "hebdomadaire", "mensuel",
    "remuneration", "salaire", "taux horaire", "brut", "net", "Mission prévue"
    "periode", "temps partiel", "temps plein","dimanche","majoration","majo"
]


EXCLUDED_PATTERNS = [
    "nationalite",
    "ape",
    "qualification",
    "contact",
    "statut",
    "non cadre",
    "signature",
    "entreprise utilisatrice",
    "l'interimaire",
    "Justification",
    "Titre de séjour",
    "Motif"
]

def extract_relevant_snippets(text: str, window: int = 2, max_lines: int = 120) -> str:
    if text == "":
        return ""
    
    raw_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    norm_lines = [normalize_text(ln) for ln in raw_lines]

    include_pattern = re.compile("|".join(re.escape(k) for k in KEYWORDS), re.IGNORECASE)
    exclude_pattern = re.compile("|".join(re.escape(k) for k in EXCLUDED_PATTERNS), re.IGNORECASE)

    keep = set()
    for i, ln in enumerate(norm_lines):
        if exclude_pattern.search(ln):
            continue
        if include_pattern.search(ln):
            for j in range(max(0, i-window), min(len(raw_lines), i+window+1)):
                if not exclude_pattern.search(norm_lines[j]):
                    keep.add(j)

    selected = [raw_lines[i] for i in sorted(keep)]
    return "\n".join(selected[:max_lines])


#text2 = extract_text_pdf(r"app\qapa1.pdf")
# # text1 = extract_text_pdf(r"app\Contrat_04-06Juillet_short.pdf")
# #text3= extract_text_pdf(r"app\izi2.pdf")
#print(text2.strip() == "")

# print(extract_relevant_snippets(text=text2))




















# import os
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings



# # loader = PyPDFLoader(r"app\Contrat_Test_Dupont.pdf")
# # docs = loader.load()

# # for i in docs:

# #     i.metadata = {
# #         'auteur':"varde11",
# #         'page label' : '1'
# #      }

# embedding_model = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
# # splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
# # docs_chunk = splitter.split_documents(docs)
    
# # vectorstore = Chroma.from_documents(
# # documents=docs_chunk,
# # embedding=embedding_model,
# # persist_directory=  "app/vectorDB/"
    
# #  )
# # print("Données misent à jour dans la vectorDB")#pip install pypdf ; pip install chromadb pip install sentence-transformers


# vectorstore_persist = Chroma (
#     persist_directory="app/vectorDB",
#     embedding_function= embedding_model
# )


# r= vectorstore_persist.similarity_search("hebdomadaire",k=3)

# print(r)