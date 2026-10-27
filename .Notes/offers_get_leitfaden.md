# Vom API-Endpunkt zur Umsetzung: GET /api/offers/

Wir gehen die Vorgabe aus `Endpoint Dokumentation.html` in der Reihenfolge durch, in der du daraus deine Umsetzung ableiten kannst. Bei jedem Schritt unterscheiden wir: **Was steht in der Dokumentation? Was bedeutet das? Was musst du dafür anlegen?**

Die kurzen Codeausschnitte zur Pagination zeigen ihre Zusammensetzung. Sie bilden noch keinen fertigen Offers-Endpunkt.

## Vorgehensweise

1. Serializer: Zuerst legst du fest, wie ein einzelnes Angebot in der Antwort aussehen soll. Die Felder leitest du aus dem Objekt innerhalb von results in deiner API-Dokumentation ab.
2. Pagination: Danach konfigurierst du, wie viele dieser Angebote pro Seite zurückkommen.
3. View: Hier verbindest du die Datenbankabfrage, Pagination und Serializer.
4. URLs: Zum Schluss machst du die View unter /api/offers/ erreichbar.

## 1. Welche Angaben der Dokumentation schaust du dir zuerst an?

Suche den ersten Eintrag unter „Angebote (offers)“. Lies dort zunächst nur diese fünf Angaben:

| Angabe aus der Dokumentation | Was du daraus ableitest |

|---|---|
| Methode: `GET` | Die Anfrage liest Daten. Du brauchst für diese Anfrage keine Erstellung oder Änderung von Angeboten. |
| Route: `/api/offers/` | Eine Listen-URL ohne einzelne Angebots-ID muss zur View führen. |
| „No Permissions required“ | Die Liste darf ohne Anmeldung aufgerufen werden. |
| „Die Antwort verwendet PageNumberPagination“ | Du verwendest die DRF-Klasse `PageNumberPagination` als Grundlage. |
| „Success Response“ | Dieses Beispiel bestimmt die Form deiner Antwort und die benötigten Serializer-Felder. |

Danach liest du die „Query Parameters“. Sie beschreiben zusätzliche Möglichkeiten, die Liste einzuschränken oder anders anzuzeigen. Zu ihnen kommen wir in Schritt 8.

**Warum nicht direkt beim Modell anfangen?** Das Modell beschreibt, was gespeichert wird. Die API-Dokumentation beschreibt, was dieser bestimmte Endpunkt ausgeben soll. Das ist nicht immer dasselbe.

## 2. Das Antwortbeispiel in zwei Teile zerlegen

Die Antwort in deiner Dokumentation hat diese äußere Form. Zur Übersicht sind hier nur zwei Felder eines Angebots gezeigt:

```json
{
  "count": 23,
  "next": "http://127.0.0.1:8000/api/offers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Website Design"
    }
  ]
}
```

Es gibt also **eine Hülle um die Liste** und **die Angebote innerhalb der Liste**.

### Teil A: Die Hülle kommt von der Pagination

- `count`: Wie viele Angebote passen insgesamt zur Anfrage?
- `next`: Wo kann der Client die nächste Seite abrufen?
- `previous`: Wo kann er die vorherige Seite abrufen?
- `results`: Hier stehen die Angebote der angefragten Seite.

Diese vier Feldnamen musst du nicht selbst in einem Offer-Serializer definieren. `PageNumberPagination` bringt die Antwortform bereits mit.

### Teil B: Ein Angebot kommt vom Serializer

Nimm jetzt **ein einzelnes Objekt innerhalb von `results`** aus deiner Dokumentation. Es enthält:

```text
id
user
title
image
description
created_at
updated_at
details
min_price
min_delivery_time
user_details
```

**Genau daraus entsteht die Feldliste deines Offer-Serializers.** Du übernimmst die Namen aus der Antwortvorgabe. Anschließend klärst du für jeden Namen die Datenquelle.

## 3. Für jedes Antwortfeld die Datenquelle finden

Öffne neben der Dokumentation deine `offers_app/models.py`.

### 3.1 Diese Felder findest du direkt bei Offer

`id`, `user`, `title`, `image`, `description`, `created_at` und `updated_at` gehören zum Modell `Offer`. `id` legt Django automatisch an.

Deshalb verwendest du für den Hauptserializer einen `ModelSerializer` mit dem Modell `Offer`. Direkte Modellfelder kann dieser anhand des Modells beschreiben. Du musst beispielsweise `title` nicht noch einmal als neues Textfeld anlegen.

`user` ist im Antwortbeispiel eine Zahl. Hier soll also die Benutzer-ID ausgegeben werden. Der `ModelSerializer` stellt einen normalen Fremdschlüssel standardmäßig über seinen Primärschlüssel dar.

Bei `image` erwartet die Dokumentation ohne vorhandenes Bild `null`. Achte bei der späteren Ausgabe darauf, dass dieser Fall stimmt.

### 3.2 details ist eine Liste von Paket-Verweisen

In der Dokumentation steht bei `details` beispielsweise:

```json
"details": [
  {"id": 1, "url": "/offerdetails/1/"},
  {"id": 2, "url": "/offerdetails/2/"},
  {"id": 3, "url": "/offerdetails/3/"}
]
```

So liest du das:

1. Die eckigen Klammern zeigen: Hier kommen mehrere Einträge zurück.
2. Jeder Eintrag enthält nur `id` und `url`.
3. Es werden hier keine Paketpreise oder Paketbeschreibungen ausgegeben.

**Daraus leitest du einen kleinen zusätzlichen Serializer ab**, der ein `OfferDetail` mit genau diesen zwei Feldern darstellt.

Woher kommen dessen Objekte? In deinem Modell besitzt `OfferDetail.offer` den Eintrag `related_name="details"`. Damit kannst du von einem Angebot aus seine Pakete unter `offer.details` erreichen.

Im Hauptserializer wird dieser kleine Serializer beim Feld `details` verwendet. Weil dort mehrere Pakete stehen, bekommt er `many=True`.

Für `url` gibt es kein Modellfeld. Diese Adresse wird aus der Detail-ID und der benannten Route zum Detail-Endpunkt erzeugt. Ein geeignetes DRF-Feld dafür ist `HyperlinkedIdentityField`. Es braucht den passenden Routenname und für absolute URLs den Request im Serializer-Kontext.

**Hinweis zur Vorgabe:** Im Listenbeispiel fehlt bei den Detail-URLs `/api/`; im Beispiel für das einzelne Angebot ist es enthalten. Die erzeugte URL muss zur tatsächlich erreichbaren Detail-Route passen. Diesen Unterschied solltest du beim Frontend-Abgleich klären.

### 3.3 user_details ist ein Objekt mit Benutzerinformationen

In der Dokumentation steht:

```json
"user_details": {
  "first_name": "John",
  "last_name": "Doe",
  "username": "jdoe"
}
```

So leitest du die Umsetzung ab:

1. Es ist ein einzelnes Objekt, keine Liste. Hier brauchst du kein `many=True`.
2. Die drei Felder gehören zum Django-Modell `User`.
3. Das Angebot kennt diesen Benutzer bereits über `Offer.user`.
4. Ein kleiner User-Serializer gibt die drei verlangten Felder aus.
5. Im Offer-Serializer heißt die Ausgabe `user_details`, ihre Datenquelle ist aber `user`. Diese Zuordnung gibst du mit `source="user"` an.

Damit kann dieselbe Beziehung zweimal unterschiedlich dargestellt werden: unter `user` als ID und unter `user_details` mit den drei Benutzerfeldern.

### 3.4 min_price und min_delivery_time musst du berechnen

Diese Namen findest du nicht im Modell `Offer`. Lies dafür die Beschreibung des Endpunkts: Er verlangt den minimalen Preis und die kürzeste Lieferzeit.

Angenommen, die Pakete eines Angebots sehen so aus:

| Paket | Preis | Lieferzeit in Tagen |

|---|---:|---:|
| Basic | 100 | 7 |
| Standard | 200 | 5 |
| Premium | 300 | 3 |

Dann muss dieses Angebot `min_price = 100` und `min_delivery_time = 3` erhalten. Die beiden Werte dürfen aus unterschiedlichen Paketen stammen.

Eine passende Umsetzung ist die Berechnung in der Datenbankabfrage mit `Min` und `annotate`:

- `details__price` bedeutet: Gehe über die Beziehung `details` zum Feld `price`.
- `Min` ermittelt den kleinsten Wert pro Angebot.
- `annotate` macht das Ergebnis unter einem gewählten Namen am abgefragten Offer-Objekt verfügbar.

Du wählst die Namen `min_price` und `min_delivery_time`, damit sie zur API-Antwort passen. Das ergänzt die abgefragten Objekte; es legt keine neuen Datenbankspalten an.

Im Serializer deklarierst du diese berechneten Felder ausdrücklich: Preis als Dezimalfeld, Lieferzeit als Integerfeld, jeweils nur zum Lesen. Sie lassen sich nicht automatisch aus dem Modell ableiten, weil sie dort keine Felder sind.

## 4. Was weißt du damit über deine Serializer?

Du hast aus dem Antwortbeispiel drei Bausteine abgeleitet:

| Baustein | Modell/Datenquelle | Ausgabefelder |

|---|---|---|
| Detail-Verweis-Serializer | `OfferDetail` | `id`, `url` |
| Benutzerübersicht-Serializer | `User` | `first_name`, `last_name`, `username` |
| Offer-Listen-Serializer | `Offer` mit berechneten Werten | Die elf Felder aus Schritt 2, einschließlich der beiden eingebauten Serializer |

Der Serializer **bestimmt die Darstellung der ausgewählten Angebote**. Er entscheidet hier nicht über die Seite und speichert bei dieser GET-Anfrage nichts.

Du übergibst ihm die gelesenen Objekte. `is_valid()` und `save()` brauchst du für diesen GET-Ablauf nicht.

## 5. Pagination Schritt für Schritt zusammensetzen

Jetzt kümmern wir uns um die Hülle aus Schritt 2.

### 5.1 Was gibt die Dokumentation vor?

Zwei Stellen gehören zusammen:

- Unter „Extra Information“ steht `PageNumberPagination`.
- Unter „Query Parameters“ steht `page_size`: Der Client soll die Anzahl der Ergebnisse pro Seite angeben können.

Daraus folgt: Du brauchst eine Pagination auf Basis von Seitennummern, die zusätzlich den Parameter `page_size` akzeptiert.

### 5.2 Datei und Klasse anlegen

Lege `offers_app/api/pagination.py` an. Darin kannst du diese kleine Konfigurationsklasse aufbauen:

```python
from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100
```

Die Klasse muss nicht zwingend `OfferPagination` heißen. Diesen Namen wählst du selbst und verwendest ihn später beim Import in der View.

### 5.3 Jede Zeile verstehen

**`from rest_framework.pagination import PageNumberPagination`**

Du importierst die vorhandene DRF-Klasse. Sie kann bereits Seiten auswählen, Treffer zählen und die Antwortfelder `count`, `next`, `previous` und `results` erzeugen.

**`class OfferPagination(PageNumberPagination):`**

Du erstellst deine eigene Klasse auf dieser Grundlage. Die vorhandenen Funktionen werden geerbt. Du musst die Seitenberechnung nicht selbst programmieren.

**`page_size = 6`**

Wenn der Client keine Größe angibt, enthält eine Seite bis zu sechs Angebote. Eine letzte Seite kann weniger enthalten.

Die Zahl 6 ist hier ein Beispiel. Deine Dokumentation nennt keinen Standardwert. Dieser muss mit dem Frontend abgestimmt werden. Die Einstellung ist hier wichtig, weil dein Projekt bisher auch keine globale `PAGE_SIZE` festlegt.

**`page_size_query_param = "page_size"`**

Damit erlaubst du dem Client, die Standardgröße über einen URL-Parameter zu ändern. Der Name stammt aus deiner API-Dokumentation.

Beispiel: `/api/offers/?page_size=10` fordert bis zu zehn Angebote an.

Ohne diese Einstellung würde deine Klasse den Parameter nicht für die Seitengröße verwenden.

**`max_page_size = 100`**

Damit legst du eine selbst gewählte Obergrenze fest. Fordert der Client 500 Angebote pro Seite an, begrenzt DRF die Größe auf 100. Auch 100 ist ein Beispielwert, keine Vorgabe der Endpoint-Dokumentation.

### 5.4 Wo wird die Seitennummer eingestellt?

`PageNumberPagination` versteht den Parameter `page` bereits. Du musst ihn für diesen Fall nicht zusätzlich konfigurieren.

Bei `/api/offers/?page=2&page_size=6` bedeutet:

- `page=2`: zweite Seite auswählen.
- `page_size=6`: bis zu sechs Angebote pro Seite ausgeben.

Wenn es 14 Treffer gibt, enthält die zweite Seite die Positionen 7 bis 12 der sortierten Liste. `count` bleibt 14. Die Positionsnummern sind nicht zwingend die Datenbank-IDs.

**Bis hier ist nur die Klasse angelegt. Damit der Endpunkt sie verwendet, musst du sie noch in der View aufrufen.**

## 6. Die Pagination mit deiner APIView verbinden

Wir bleiben hier bei `APIView`, weil du diese bereits von deinen Profil-Endpunkten kennst. Bei dieser View schreibst du die Pagination-Aufrufe selbst in die GET-Methode.

Nehmen wir für die folgenden Ausschnitte an:

- `offers` ist dein bereits gefiltertes und sortiertes Offer-Queryset.
- `OfferListSerializer` ist der Name, den du deinem Hauptserializer gegeben hast.
- `OfferPagination` wurde aus deiner neuen Datei importiert.

Die Namen `offers`, `paginator` und `page` sind selbst gewählte Variablennamen. Die Methodennamen stammen von DRF.

### 6.1 Eine Pagination-Instanz erzeugen

```python
paginator = OfferPagination()
```

Du erzeugst ein Objekt deiner Konfigurationsklasse. Dieses Objekt verarbeitet anschließend die aktuelle Anfrage und merkt sich die ausgewählte Seite.

### 6.2 Die aktuelle Seite auswählen

```python
page = paginator.paginate_queryset(offers, request)
```

Hier gibst du zwei Dinge hinein:

- `offers`: die gesamte passende und sortierte Auswahl an Angeboten.
- `request`: die aktuelle Anfrage mit Parametern wie `page` und `page_size`.

Die Methode ermittelt daraus die Seite. In `page` liegen die Angebote, die in dieser Antwort erscheinen sollen. Der Paginator kennt jetzt außerdem die Gesamtzahl und die benachbarten Seiten.

### 6.3 Die Angebote dieser Seite serialisieren

```python
serializer = OfferListSerializer(
    page,
    many=True,
    context={"request": request},
)
```

- `page`: Du gibst nur die ausgewählten Angebote hinein.
- `many=True`: Es sind mehrere Angebote, die alle gleich dargestellt werden sollen.
- `context`: Du reichst den Request weiter, damit beispielsweise URL-Felder absolute Adressen erzeugen können.

Nach diesem Schritt enthält `serializer.data` die darstellbaren Angebotsdaten der Seite. Die äußere Hülle fehlt noch.

### 6.4 Die vollständige Antwort zurückgeben

```python
return paginator.get_paginated_response(serializer.data)
```

Du gibst die serialisierten Angebote an denselben Paginator zurück. Er setzt sie unter `results` ein und ergänzt `count`, `next` und `previous`.

Diese Methode liefert bereits eine `Response`. Du musst die vier äußeren Felder nicht selbst zusammensetzen.

### 6.5 Warum genau diese Reihenfolge?

```text
Alle passenden Angebote
        ↓ paginate_queryset
Angebote der aktuellen Seite
        ↓ OfferListSerializer
Darstellbare Daten dieser Angebote
        ↓ get_paginated_response
Antwort mit count, next, previous und results
```

Die erste Pagination-Methode wählt aus. Die zweite verpackt die Ausgabe. Dazwischen stellt der Serializer die ausgewählten Angebote dar.

Wenn du dem Serializer versehentlich `offers` statt `page` übergibst, verarbeitest du wieder die gesamte Treffermenge. Deshalb ist diese Übergabe entscheidend.

## 7. Was geschieht insgesamt in der View?

Die View verbindet die bisher erklärten Bausteine. Für diesen GET-Endpunkt gehören diese Aufgaben in den Ablauf:

1. **Zugriff erlauben:** Laut Dokumentation ist die Liste öffentlich. Das kannst du mit `AllowAny` ausdrücken.
2. **Angebote abfragen:** Die Ausgangsmenge kommt aus `Offer`.
3. **Berechnete Werte ergänzen:** Mindestpreis und kürzeste Lieferzeit aus den zugehörigen Paketen bestimmen.
4. **Anfrageparameter berücksichtigen:** Auswahl filtern, durchsuchen und sortieren.
5. **Seite auswählen:** Mit deiner Pagination-Klasse und dem aktuellen Request.
6. **Angebote darstellen:** Die ausgewählte Seite an den Serializer geben.
7. **Antwort liefern:** Die Daten in der Pagination-Hülle mit Status 200 zurückgeben.

Ein Queryset ist die Django-Beschreibung einer Datenbankabfrage. Beim Aufbauen werden noch nicht sofort alle Datensätze als Python-Objekte geladen. Die Abfrage kann deshalb erst um Filter, Sortierung und Berechnungen erweitert werden, bevor die Seite gelesen wird.

Eine definierte Sortierung ist wichtig: Ohne festgelegte Reihenfolge ist nicht verlässlich, welche Angebote zu welcher Seite gehören. Bei gleichen Sortierwerten kann eine zusätzliche ID-Sortierung die Reihenfolge eindeutig machen.

## 8. Wie leitest du die Query-Parameter ab?

Die Tabelle „Query Parameters“ sagt dir, welche URL-Eingaben der Endpunkt verstehen muss. In der View liest du sie über `request.query_params` oder verwendest dafür geeignete Filter-Backends. Die Pagination verarbeitet ihre Parameter selbst.

| Vorgabe | Beispielanfrage | Daraus folgende Aufgabe |

|---|---|---|
| `creator_id` | `?creator_id=7` | Nur Angebote mit Benutzer-ID 7 auswählen. |
| `min_price` | `?min_price=100` | Angebote auswählen, deren berechneter Mindestpreis mindestens 100 beträgt. |
| `max_delivery_time` | `?max_delivery_time=5` | Angebote nach der maximal erlaubten Lieferzeit filtern. |
| `ordering` | `?ordering=min_price` | Nach dem berechneten Mindestpreis sortieren; außerdem soll `updated_at` möglich sein. |
| `search` | `?search=Website` | Titel und Beschreibung nach dem Begriff durchsuchen. |
| `page_size` | `?page_size=6` | Durch deine Pagination-Klasse bis zu sechs Angebote pro Seite liefern. |

Beim Lieferzeitfilter ist die Dokumentation nicht ganz eindeutig: Muss mindestens ein Paket oder müssen alle Pakete innerhalb der Grenze liegen? Ein Vergleich mit `min_delivery_time` bedeutet, dass mindestens ein Paket die Grenze erfüllt. Diese Auslegung muss beim Umsetzen bewusst gewählt und bei Bedarf mit dem Frontend geklärt werden.

Filterung und Suche müssen **vor** der Seitenaufteilung erfolgen. Beispiel: Von 30 Angeboten passen 8 zum Suchwort. Die Pagination soll diese 8 Treffer aufteilen, und `count` soll 8 sein.

Würdest du zuerst die ersten 6 Angebote auswählen und erst darin suchen, könnten passende Angebote auf anderen Seiten übersehen werden.

Die Dokumentation verlangt für ungültige Anfrageparameter Status 400. Fachliche Eingaben wie ein nicht numerischer Mindestpreis müssen dafür geprüft werden. Beachte beim späteren Fehlerverhalten: Die eingebaute Pagination liefert für nicht vorhandene Seiten standardmäßig 404 und behandelt ungültige Seitengrößen teilweise durch Rückfall auf den Standard. Falls die Vorgabe auch dort 400 meint, brauchst du eine Anpassung.

## 9. Wie kommt die Anfrage überhaupt zu dieser View?

Aus der Route `/api/offers/` leitest du zwei Verbindungen ab:

1. In `offers_app/api/urls.py` verbindet der Teil `offers/` die URL mit deiner View.
2. In `core/urls.py` bindest du die Offers-URL-Datei unter `api/` ein.

Zusammen ergibt das `/api/offers/`. Der Endpunkt hat keine ID in der URL, weil er eine Liste liefert.

Achte darauf, `/api/` nicht in beiden Dateien einzutragen. Sonst würde versehentlich `/api/api/offers/` entstehen.

## 10. Ein vollständiges Beispiel im Kopf durchgehen

Die Anfrage lautet:

```text
GET /api/offers/?creator_id=7&page=2&page_size=3
```

Angenommen, Benutzer 7 besitzt insgesamt 8 Angebote.

1. Django findet die Offers-View über die URL-Konfiguration.
2. Die GET-Methode darf öffentlich ausgeführt werden.
3. Die View bereitet die Angebotsabfrage einschließlich der berechneten Werte vor.
4. Der Filter begrenzt die Auswahl auf die 8 Angebote von Benutzer 7.
5. Die Auswahl wird sortiert.
6. Die Pagination liest Seite 2 und Seitengröße 3.
7. Sie wählt die Positionen 4, 5 und 6 aus.
8. Der Serializer stellt diese drei Angebote mit allen verlangten Angebotsfeldern dar.
9. Der Paginator erstellt die Antwort: `count` ist 8, `results` enthält drei Angebote, und beide Nachbarseiten sind verlinkt.

Der Serializer muss dabei nicht wissen, dass es Seite 2 ist. Er bekommt einfach drei Offer-Objekte und stellt diese dar.

## 11. Deine nächsten konkreten Arbeitsschritte

1. In `serializers.py` den kleinen Serializer für die Detail-Verweise anlegen: Modell `OfferDetail`, Felder `id` und `url`.
2. Den User-Serializer für die drei Benutzerfelder ergänzen.
3. Den Hauptserializer für die elf Offer-Antwortfelder zusammensetzen.
4. In `pagination.py` die Pagination-Klasse wie in Schritt 5 konfigurieren.
5. In der GET-View die Angebotsabfrage vorbereiten und die vier Pagination-/Serializer-Aufrufe aus Schritt 6 verbinden.
6. Die Query-Parameter vor dem Pagination-Aufruf einarbeiten.
7. Die URL-Dateien verbinden.

Die anderen Offers-Endpunkte folgen später. Sie haben zum Teil andere Berechtigungen und Antwortfelder. Beispielsweise verlangt GET `/api/offers/{id}/` eine Anmeldung und liefert nur ein Angebot; dort brauchst du keine Listen-Pagination.

## Dokumentation zum Nachschlagen

Die fachlichen Anforderungen und Feldnamen stammen aus deiner lokalen Datei [Endpoint Dokumentation.html](Endpoint%20Dokumentation.html). Die Klassen- und Variablennamen in diesem Leitfaden sind Vorschläge.

- [DRF: PageNumberPagination](https://www.django-rest-framework.org/api-guide/pagination/#pagenumberpagination) – Basis der Pagination-Klasse und ihrer Einstellungen.
- [DRF: Verschachtelte Serializer](https://www.django-rest-framework.org/api-guide/relations/#nested-relationships) – Grundlage für `details` und `user_details`.
- [DRF: HyperlinkedIdentityField](https://www.django-rest-framework.org/api-guide/relations/#hyperlinkedidentityfield) – URLs zu den Detailobjekten erzeugen.
- [Django: Aggregation](https://docs.djangoproject.com/en/6.0/topics/db/aggregation/) – `Min` und `annotate` für berechnete Werte.

Später kannst du denselben Listenablauf auch mit `ListAPIView` umsetzen. Diese Anleitung bleibt zunächst bei deiner bekannten `APIView`, damit jeder Aufruf sichtbar bleibt.
