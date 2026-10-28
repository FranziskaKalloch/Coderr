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
