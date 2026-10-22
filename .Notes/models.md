# Models

Man geht von unabhängig zu abhängig vor. Beim User beginnend, weil andere Daten auf den User verweisen.

Bei einer 1:n Beziehung liegt der Fremdschlüssel auf der n-Seite.
Bei einer 1:1 Beziehung lieft die Referenz üblicherweise bei dem ergänzenden Objekt.
Bei einer n:m Beziehung verbindet eine zuätzliche Tabelle beide Seiten.

Wichtig: Die Referenz wird nur auf einer Seite gespeichert. Django ermöglicht trotzdem den Zugriff in beide Richtungen; dafür ist unter anderem related_name da.

## Verknüpfung

Die Verknüpfung ist ein Feld in einem deiner Models, das auf einen Datensatz eines anderen Models zeigt.
Um herauszufinden, wo es hingehört, formulierst du die Beziehung in beide Richtungen.

Ein Benutzer kann mehrere Angebote erstellen.
Ein Angebot gehört genau zu einem Benutzer.

Das ist 1:n. Der Fremdschlüssel kommt auf die n-Seite, also ins Angebot.

Django ermöglicht trotzdem beide Zugriffsrichtungen:

offer.user                 | Benutzer dieses Angebots
user.offers.all()          | Alle Angebote dieses Benutzers

user ist das Feld, das du geschrieben hast. offers ist der Rückwärtsname aus related_name.

## User

Es wird das eingebaute Django-User Modell benutzt. In user_auth_app/models.py muss man dafür kein eigenes Model schreiben. Die App kümmert sich später um Registrierung und Login.

Felder, die Django bereits mit dem User-Model mitbringt:

- username | Charfield | Pflichtfeld
- email | EmailField | eindeutig, Pflichfeld
- password | von Django verwalteter Passwort-Hash, immer über create_user() oder set_password() setzen
- (repeated password)
- first_name | Charfield, optional
- last_name | Charfield, optional
- date_joined | DateTimeField, Zeitpunkt der Registrierung
  
Zusätzliche Felder:

- repeated_password | kein Model-Feld, wird nur bei der Registrierung im Serializer mit dem Passwort verglichen
- type (beschreibt die Benutzerrolle) | ChoiceField (customer, business) -> Im Profile gespeichert!

### Login & Registrierung

Erfolgt über den Username und das Password
Token Authentifizierung.

## Profile

GET /api/profile/{pk}
Ruft die detaillierten Informationen eines Benutzerprofils ab (sowohl für Kunden- als auch für Geschäftsnutzer). Ermöglicht auch das Bearbeiten der Profildaten (PATCH).

Beziehung 1:1 User:Profile. Die Referenz liegt im Profile.

- user | OneToOneField auf settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
- location | CharField, optional
- tel | CharField, optional, Telefonnummer können + und führende Nullen enthalten
- description | Textfeld, lang -> Profilbeschreibung
- working_hours | CharField, optional
- type | CharField mit choices für customer und business
- file  |  ImageField -> optionales Profilbild
- uploaded_at | DateTimeField, optional, beim Upload gezielt setzen

Diese Felder sollten nicht doppelt im Profil gesetzt werden:

- created_at | kann in der API aus user.date_joined kommen
- username, first_name, last_name, email | kommen über User

## Angebote (offers)

GET /api/offers/
Description: Dieser Endpunkt gibt eine Liste von Angeboten zurück. Jedes Angebot enthält eine Übersicht der Angebotsdetails, den minimalen Preis und die kürzeste Lieferzeit.

Hier kommen drei Dinge zusammen: gespeicherte Angebote, Suchoptionen und die Verpackung der Antwort.
Query Parameter bestimmen, welche Angebote man abruft.

count, next, previous und results gehören zur Seiteneinteilung, also zur Pagination.

### Query Parameters

Name Type Description
creator_id | integer | Filtert die Angebote nach dem Benutzer, der sie erstellt hat.
min_price | float | Filtert Angebote mit einem Mindestpreis.
max_delivery_time | integer | Filtert Angebote, deren Lieferzeit kürzer oder gleich dem angegebenen Wert ist.
ordering | string | Sortiert die Angebote nach den Feldern 'updated_at' oder 'min_price'.
search | string | Durchsucht die Felder 'title' und 'description' nach Übereinstimmungen.
page_size | integer | Gibt an, wie viele Ergebnisse pro Seite zurückgegeben werden sollen. Dies sollte mit dem Frontend abgestimmt sein.

- user | ForeignKey auf settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offers"
- title | CharField, Pflichtfeld
- image | ImageFIeld, optional
- description | TextField, Pflichtfeld
- details | Rückwärtsbeziehung zu mehreren Angebotsdetaisl, kein zusätzliches Feld in Offer nötig
- created_at | DateTimeField mit auto_now_add=True
- updated_at | DateTimeField mit auto_now=True
  
- offer_type ? gehört eventuell in ein eigenes Model

## OfferDetail

Beziehung: Offer 1:n OfferDetail

- offer |  ForeignKey auf Offer, on_delete=models.CASCADE, related_name='details'
- title | CharField, Pflichtfeld
- revisions | IntegerField; erlaubte Werte anhand der Vorgaben festlegen
- delivery_time_in_days | PositiveIntegerField, mindestens 1
- price | DecimalField, beispielsweise max_digits=10, decimal_places=2
- features | JSONField für eine Liste von Texten, default=list
- offer_type | CharField mit festen Auswahlwerten
Pro Angebot sollte jeder Pakettyp höchstens einmal vorkommen. Dafür verwenden wir später einen UniqueConstraint auf offer und offer_type.

min_price und die kürzeste Lieferzeit berechnen wir aus den Angebotsdetails. Sie müssen nicht zusätzlich im Offer gespeichert werden.

## Bestellungen (orders)

Hier bestehen zwei Beziehungen zum User:

- User 1:n Order als Kunde
- User 1:n Order als Geschäftsnutzer

Felder:

- customer_user  |  ForeignKey auf settings.AUTH_USER_MODEL, related_name='customer_orders'
- business_user  |  ForeignKey auf settings.AUTH_USER_MODEL, related_name='business_orders'
- Für beide würde ich zunächst on_delete=models.PROTECT wählen, damit das Löschen eines Benutzers nicht seine Bestellungen entfernt.
- title  |  CharField
- revisions  |  IntegerField
- delivery_time_in_days  |  PositiveIntegerField, mindestens 1
- price  |  DecimalField
- features | JSONField, default=list
- offer_type  |  CharField mit choices
- status | CharField mit choices; genaue Statuswerte aus der API-Vorgabe übernehmen
- created_at  |  DateTimeField mit auto_now_add=True
- updated_at |  DateTimeField mit auto_now=True

## Review

/api/base-info/: kein eigenes Model nötig, die vier Kennzahlen werden berechnet.

## UniqueConstraints

class Meta steht auf derselben Einrückungsebene wie das Model Feld
constraints ist eine Liste mit Regeln.
models.UniqueCosntraint() erstellt die Beschreibung einer Eindeutigkeitsregel
fields nennt die Felder, deren Kombination eindeutig sein muss
name gibt der Datenbankregel einen Name, damit sie bspw. in Migrationen identifiert werden kann

Die Regel erlaubt also mehrere basic Pakete insgesamt, aber nur eines pro Angebot.
