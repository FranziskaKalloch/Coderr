from offers_app import Offer, OfferDetail


#### AUFGABEN: ZUGRIFF AUF DIE OBJEKTE #####
### 1. Instanz erstellen: Offer()  | erstellt ein Objekt im Arbeitsspeicher 
### 2. first_offer.save()          | speichert das Objekt in der Datenbank
### 1+2. Offer.objects.create()    | erstellt ein Objekt und speichert es sofort in der Datenbank

first_offer = Offer() 
# Python erstellt ein neues Objekt nach dem Bauplan der Klasse Offer. 
# Dieses Objekt besitzt die definierten Felder. Der Name first_offer verweist darauf
# Das Objekt existiert bisher nur im Arbeitsspeicher. 
# Es wurde nichts in der Datenbank gespeichert.


#  Weise der Instanz über das Feld title den Text "Website erstellen" zu & gebe den Titel aus
first_offer.title = "Website erstellen" 
print(first_offer.title)

# Erstelle eine ungespeicherte Instanz von OfferDetail mit dem Variablennamen first_detail. 
# Weise anschließend ihrem Feld offer deine vorhandene Instanz first_offer zu.

first_detail = OfferDetail()
OfferDetail(first_offer)