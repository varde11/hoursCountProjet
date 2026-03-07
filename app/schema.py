from pydantic import BaseModel, Field
from typing import Optional, Literal, Annotated, TypedDict, List
from langgraph.graph.message import add_messages

class Periode(BaseModel):
    debut: Optional[str] = Field(None, description="Date de début")
    fin: Optional[str] = Field(None, description="Date de fin")

class HeureItem(BaseModel):
    type: Optional[Literal["hebdomadaire", "mensuel", "quotidien", "plage_horaire", "total", "inconnu"]] = "inconnu"
    valeur: Optional[str] = None

class RemunerationItem(BaseModel):
    type: Optional[Literal["taux_horaire", "mensuel_brut", "mensuel_net", "prime", "majoration", "inconnu"]] = "inconnu"
    valeur: Optional[float] = None
    devise: Optional[str] = "EUR"
    label: Optional[str] = None

class ContratOutput(BaseModel):
    periode: Periode
    heures: List[HeureItem] = Field(default_factory=list)
    remuneration: List[RemunerationItem] = Field(default_factory=list)
    commentaire: Optional[str] = None

class State(TypedDict):
    messages: Annotated[list, add_messages]
    retrieved_text: str
    final_output: dict