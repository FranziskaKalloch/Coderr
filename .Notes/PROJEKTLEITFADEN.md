# Coderr – gemeinsamer Leitfaden

## Verbindliche Arbeitsweise

- Der Nutzer richtet das Projekt selbst ein und schreibt den Code.
- Codex erklärt Zusammenhänge und gibt schrittweise einen Leitfaden mit überschaubaren Aufgaben.
- Niemals eigenständig Code schreiben, Dateien verändern oder Befehle ausführen. Dafür ist jeweils eine ausdrückliche Anweisung erforderlich.
- Codebeispiele nur auf ausdrücklichen Wunsch.
- Zuerst ausschließlich das Backend entwickeln. Frontend und Backend erst ganz zum Schluss verbinden.

## Roter Faden

1. Anforderungen und lokale API-Dokumentation gemeinsam verstehen.
2. Django-Projekt und Apps selbst einrichten; Einstellungen und Datenbank verstehen.
3. Datenmodelle und Beziehungen planen: Benutzerprofile, Angebote, Angebotspakete, Bestellungen, Bewertungen.
4. Registrierung und Login mit Token-Authentifizierung sowie Customer- und Business-Rollen entwickeln.
5. REST-API schrittweise umsetzen: Profile, Angebote und Angebotsdetails, Bestellungen, Bewertungen, Plattformstatistiken.
6. Filter, Suche, Sortierung, Pagination, Validierung und Berechtigungen passend zur Dokumentation ergänzen.
7. Backend und API-Verhalten testen.
8. Erst zum Schluss Frontend und Backend verbinden und gemeinsam prüfen.

Bei jedem Schritt zuerst erklären, was gebaut wird und warum; anschließend eine überschaubare Aufgabe geben.

## API-Vertrag

Quelle: `Endpoint Dokumentation.html` im Projektordner. Diese wurde vollständig gelesen; bei Implementierungsfragen erneut die genaue Vorgabe prüfen.

- POST /api/registration/
- POST /api/login/
- GET, PATCH /api/profile/{pk}/
- GET /api/profiles/business/
- GET /api/profiles/customer/
- GET, POST /api/offers/
- GET, PATCH, DELETE /api/offers/{id}/
- GET /api/offerdetails/{id}/
- GET, POST /api/orders/
- PATCH, DELETE /api/orders/{id}/
- GET /api/order-count/{business_user_id}/
- GET /api/completed-order-count/{business_user_id}/
- GET, POST /api/reviews/
- PATCH, DELETE /api/reviews/{id}/
- GET /api/base-info/
