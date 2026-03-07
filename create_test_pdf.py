import fitz  # PyMuPDF

# Créer un document PDF vierge
doc = fitz.open()

# Ajouter une page
page = doc.new_page()

# Contenu du contrat avec les keywords
contrat_text = """
CONTRAT DE TRAVAIL

Entreprise: Acme Corporation
Employé: Jean Dupont
Date: 5 Mars 2026

=====================================

PÉRIODE D'EMPLOI:
Date de début: 1er janvier 2026
Date de fin: 31 décembre 2026
Durée du travail: À définir selon horaire

=====================================

HORAIRE DE TRAVAIL:

L'horaire de travail est fixé comme suit:

Horaire hebdomadaire: 35 heures par semaine
Horaire mensuel: Environ 152 heures par mois

La durée du travail est à temps plein, conformément 
à la législation en vigueur.

Heures de travail quotidiennes: 7 heures
Jours de travail: Lundi au vendredi

=====================================

RÉMUNÉRATION:

Type de rémunération: Salaire mensuel brut
Taux horaire: 15,50 EUR par heure
Salaire mensuel brut: 2 350 EUR
Salaire mensuel net: 1 820 EUR

La rémunération est versée le dernier jour 
ouvrable de chaque mois.

=====================================

OBSERVATIONS ET CONDITIONS:

Le présent contrat de travail entre en vigueur à 
la date indiquée ci-dessus. L'employé s'engage à 
respecter les conditions de travail, notamment 
concernant les heures de travail et l'horaire convenu.

Tout changement de conditions sera notifié par écrit.

Signature de l'employeur: _______________
Signature de l'employé: _______________
"""

# Insérer le texte dans la page
page.insert_text((50, 50), contrat_text, fontsize=11, fontname="helv")

# Sauvegarder le PDF
pdf_path = "app/Contrat_Test_Dupont.pdf"
doc.save(pdf_path)
doc.close()

print(f"✅ PDF créé avec succès: {pdf_path}")
