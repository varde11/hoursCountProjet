# import fitz  # PyMuPDF

# # Créer un document PDF vierge
# doc = fitz.open()

# # Ajouter une page
# page = doc.new_page()

# # Contenu du contrat avec les keywords
# contrat_text = """
# CONTRAT DE TRAVAIL

# Entreprise: Acme Corporation
# Employé: Jean Dupont
# Date: 5 Mars 2026

# =====================================

# PÉRIODE D'EMPLOI:
# Date de début: 1er janvier 2026
# Date de fin: 31 décembre 2026
# Durée du travail: À définir selon horaire

# =====================================

# HORAIRE DE TRAVAIL:

# L'horaire de travail est fixé comme suit:

# Horaire hebdomadaire: 35 heures par semaine
# Horaire mensuel: Environ 152 heures par mois

# La durée du travail est à temps plein, conformément 
# à la législation en vigueur.

# Heures de travail quotidiennes: 7 heures
# Jours de travail: Lundi au vendredi

# =====================================

# RÉMUNÉRATION:

# Type de rémunération: Salaire mensuel brut
# Taux horaire: 15,50 EUR par heure
# Salaire mensuel brut: 2 350 EUR
# Salaire mensuel net: 1 820 EUR

# La rémunération est versée le dernier jour 
# ouvrable de chaque mois.

# =====================================

# OBSERVATIONS ET CONDITIONS:

# Le présent contrat de travail entre en vigueur à 
# la date indiquée ci-dessus. L'employé s'engage à 
# respecter les conditions de travail, notamment 
# concernant les heures de travail et l'horaire convenu.

# Tout changement de conditions sera notifié par écrit.

# Signature de l'employeur: _______________
# Signature de l'employé: _______________
# """

# # Insérer le texte dans la page
# page.insert_text((50, 50), contrat_text, fontsize=11, fontname="helv")

# # Sauvegarder le PDF
# pdf_path = "app/Contrat_Test_Dupont.pdf"
# doc.save(pdf_path)
# doc.close()

# print(f"✅ PDF créé avec succès: {pdf_path}")



# 1) Est ce que les heures sup sont des heures de dimanche ou jour férier ou de nuit ? 

"""
okay, j'ai appliqué les modif mais un petit soucis niveau logic , je t'affiche pour un autre cas de contrat d'intérim le final du llm, le text extrait ainsi que les estimation en fonction de 2 situation horaire.
Donc pour ce contrat, oui date de début était bien le 28/02 ( un samedi) et la date de fin le 07/03 ( un autre samedi) et par samedi il fallait faire 7h de temps ( oui sur le contrat y a une erreur 



periode=Periode(debut='28/02/2026', fin='07/03/2026') base_hours=BaseHours(type='hebdomadaire', valeur=14.0) base_hourly_rate=12.02 base_salary_reference=None daily_hours=8.5 mission_days=9 special_rate_rules=[SpecialRateRule(label='night', type='hourly_rate', value=15.03, condition=None)] commentaire=None
*********************
DATES ET HORAIRES                    REMUNERATION DE REFERENCE
Mission prévue du :       28/02/2026      au    07/03/2026      TAUX HORAIRE BRUT :                  
         12,02 €
TERME PRECIS     DUREE MINIMALE
Aménagement possible entre le     05/03/26        et le   10/03/26
Durée hebdo (h) : 14,00             Période d'essai (JT) :    2
Horaires : Horaires variables
(Lundi-Mardi-Mercredi-Jeudi-Vendredi-Samedi-Dimanche: 7:00-15:30)   HEURES FORMATION                 
           12,02 €
HEURES SUPP FORMATION                      15,03 €  /35>43H
HEURES SUPP FORMATION                      18,03 €  />43H
HEURES NUIT FORMATION                       15,03 €  /H. Nuit
REMUNERATION                                LEGISLATION
HEURES FORMATION                            12,02 €              les documents personnels nécessaires à l'exécution de votre mission  (
HEURES SUPP FORMATION                      15,03 €  /35>43H   ex : CNI, titre de séjour, carte BTP, permis de conduire, ....).
HEURES SUPP FORMATION                      18,03 €  />43H
HEURES NUIT FORMATION                       15,03 €  /H. Nuit                                        
                       Dans  le  cas  où  le  pass  sanitaire  ou  l'obligation  vaccinale  est      
nécessaire  à  l'exécution de votre  mission,  vous  vous  engagez à
fournir un justificatif conforme, conformément aux dispositions en
vigueur. A défaut votre contrat sera suspendu, sans rémunération.
Virement des paies le 12 du mois suivant.
work0:  missing_hours=0.0 extra_hours=0.0 night_hours=0.0 sunday_hours=0.0 holiday_hours=0.0 comment=None


estimation0:  planned_hours=76.5 actual_hours=76.5 normal_hours=35.0 overtime_25_hours=8.0 overtime_50_hours=33.5 base_amount=420.7 overtime_25_amount=120.19999999999999 overtime_50_amount=604.005 special_amount=0.0 total_estimated_salary=1144.905 details=[SalaryLine(label='Heures normales', hours=35.0, rate=12.02, amount=420.7), SalaryLine(label='Heures supplémentaires +25%', hours=8.0, rate=15.024999999999999, amount=120.19999999999999), SalaryLine(label='Heures supplémentaires +50%', hours=33.5, rate=18.03, amount=604.005)] warnings=[]
----------------------------------------
work1:  missing_hours=0.0 extra_hours=1.0 night_hours=0.0 sunday_hours=1.0 holiday_hours=0.0 comment=None


estimation1:  planned_hours=76.5 actual_hours=77.5 normal_hours=35.0 overtime_25_hours=8.0 overtime_50_hours=34.5 base_amount=420.7 overtime_25_amount=120.19999999999999 overtime_50_amount=622.0350000000001 special_amount=0.0 total_estimated_salary=1162.935 details=[SalaryLine(label='Heures normales', hours=35.0, rate=12.02, amount=420.7), SalaryLine(label='Heures supplémentaires +25%', hours=8.0, rate=15.024999999999999, amount=120.19999999999999), SalaryLine(label='Heures supplémentaires +50%', hours=34.5, rate=18.03, amount=622.0350000000001)] warnings=[]


"""

from datetime import datetime

srt='06/07/2025'


d= datetime.strptime(srt,"%d/%m/%Y").date()

print(d)
print(type(d))

print( datetime.now().replace(microsecond=0))