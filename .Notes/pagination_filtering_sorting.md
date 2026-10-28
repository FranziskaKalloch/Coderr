# Pagination

In deutsch würde man Seitenunterteilung oder Ähnliches sagen.
Die Daten werden in einzelne Teilabschnitte unterteilt. Somit kann man den Benutzer unterstützen, einen guten Überblick über die Daten zu haben.
Zum anderen geht eine Leistungsoptimierung einher, weil Daten schneller abgefragt werden können, wenn diese aufgeteilt werden.
Dadurch kann der Benutzer besser durch die Daten navigieren.
Au0erdem ist es eine Reduzierung der Serverlast, da immer nur Teile bereitgestellt werden.

## Einrichtung für PageNumberPagination (global einstellen)

In der 'settings.py' wird die Pagination installiert und definiert.
Im Teil vom 'REST_FRAMEWORK' wird folgendes geschrieben:

' 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10, '

Jetzt werden 10 Einträge, Daten oder Produkte pro Seite angezeigt.
Wenn man jetzt eine Abfrage macht, dann sieht die Response etwas anders aus.
Man bekommt ein Dictionary zurück und in diesem Dictonary sind erstmal weitere Felder, die von der Pagination kommen:

- count
- next
- previous
- results

Im 'results' Feld ist jetzt quasi das Ergebnis der API Anfrage enthalten und zwar 10 Einträge pro Seite.

'count' ist die Anzahl der Einträge.
Das 'next' Feld ist der Verweis auf die nächste Seite.
Und das 'previous' Feld ist quasi der Gegensatz, die vorherige Seite.

## Einrichtung für LimitOffsetPagination (global einstellen)

' 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10, '

Im 'next' Feld werden jetzt andere Parameter benutzt: Limit und Offset.

Offset ist der Abstand von Beginn an.

## Eigene Pagination in pagination.py erstellen (lokal einstellen)

## Querysets

Ein QuerySet beschreibt eine Datenbankabfrage.
Django führt sie normalerweise erst aus, wenn die Ergebnisse tatsächlich benötigt werden.

## Was bedeutet annotate?

Die API-Beschreibung will pro Angebot einen Wert (Ein Offer kann aber drei Werte haben, 100€ Basic, 200€ Standard, 300€ Premium). Es gibt also pro Angebot mehrere Preise.
In dem Punkt wollen wir aber den günstigsten Preis und die kürzeste Lieferzeit. Da diese Werte in keiner Spalte stehen, müssen sie berechnet werden.

annotate() macht genau das. Es hängt jedem Offer im Queryset ein zusätzliches, berechnetes Feld an. Dazu gehört auch Min.
'Min' ist eine Datenbankfunktion aus django.db.models. Sie ermittelt den kleinsten Wert eines Feldes.

Für jedes Offer schaut die Datenbank in die zugehörigen Details und nimmt den kleinsten Wert.
Deshalb heißen die Felder in deinem Serializer 'min_price' und 'min_delivery_time' und sind read_only. Sie kommen nicht aus dem Model, sondern aus der Annotation. Der Name, den du in annotate(...) vergibst, muss exakt zu diesen Serializer-Feldern passen.

annotate ergänzt jedes Objekt einer Abfrage um einen zusätzlichen Wert. Die eigentliche Berechnung übernimmt hier Min.

### ListAPIView (annotate, queryset, search, ordering) - GET /api/offers/

Zwei Werte annotieren                   | annotate(Min(...))
Parameter prüfen + filtern              | get_queryset() mit ValidationError -> 400
'search'                                | SearchFilter
'ordering'                              | OrderingFilter
Paginierte Antwort                      | Pagination-Klasse
Serialisieren + zurückgeben             | macht ListAPIView automatisch

### Zwei Werte annotieren

Ohne die beiden Felder wäre der QuerySet einfach Offer.objects.all(). Dein Serializer erwartet aber min_price und min_delivery_time, und die gibt es nicht in Offer. Genau hier kommt annotate ins Spiel. Der Aufbau ist:

'''
Offer.objects.annotate(
    NAME_1=Min("beziehung__field"),
    NAME_2=Min("beziehung__field"),
)
'''

Alle vier Stellen müssen ausgefüllt werden:

- NAME_1 / NAME_2: Die Namen, die dein Serializer erwartet -> also: min_price & min_delivery_time
- Die Strings in Min(...): Beziehung zu den Details, dann __, dann das Feld.

Den Namen der Beziehung findest man im Model bei OfferDetail.offer im related_name. Die Feldnamen für Preis und Lieferzeit stehen direkt darunter in OfferDetail. Das sind die einzigen Informationen, die du aus deinem Model abliest.

### Wieso

Vorwärts (von OfferDetail nach Offer): Das Feld heißt offer. So kommt man von einem Detail zu seinem Angebot.
Rückwärts (von Offer nach OfferDetail): Diese Richtung hat kein eigenes Feld in Offer. Django legt sie automatisch an, und der Name dafür ist der related_name.

## Was bedeutete param.get()

Angenommen jemand ruft diese URL auf:

'''
/api/offers/?min_price=150&max_delivery_time=5
'''

In der View -> params = self.request.query_params

params.get("min_price")          # ergibt "150"
params.get("max_delivery_time")  # ergibt "5"
params.get("creator_id")         # ergibt None, weil nicht angegeben

.get("min_price") bedeutet: „Lies den Wert mit diesem Namen aus.“ Es filtert noch nichts und fragt keine Angebote aus der Datenbank ab. Die Werte kommen zunächst als Text an. DRF-Dokumentation
