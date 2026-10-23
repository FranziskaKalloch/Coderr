# Was passiert, wenn ein User seine Daten im Formular eingibt und abschickt

Wenn ein User das Registrierungsformular abschickt, schickt das Frontend eine HTTP-POST-Anfrage an dein Backend. Die Anfrage enthält zum Beispiel Benutzername, E-Mail, beide Passwörter und den Profiltyp.
Die View steuert den Ablauf. Der Serializer prüft die Daten und legt User und Profil an.

## Die Anfrage erreicht die View

Django ordnet die angefragte URL der RegisterView zu. Weil es eine POST-Anfrage ist, ruft APIView deine post()-Methode auf.
'request' ist das Anfrageobjekt.
'request.data' enthält die abgeschickten Eingaben, beispielsweise Benutzername, E-Mail, Passwort, Passwortwiederholung und Profiltyp.

## Die View erstellt den Serializer

Die View übergibt request.data an eine neue Instanz von RegisterSerializer.
Der Serializer hat damit die Eingaben erhalten. Zu diesem Zeitpunkt wurde noch nichts validiert oder gespeichert.

## Die View ruft is_valid() auf

Damit startet die Prüfung im Serializer:

- Sind die erforderlichen Felder vorhanden?
- Haben sie ein gültiges Format?
- Sind Benutzername und E-Mail noch verfügbar?
- Ist der Profiltyp erlaubt?
- Stimmen die Passwörter überein und erfüllen sie die Passwortregeln?

Die feldübergreifenden Prüfungen hast du in deiner validate()-Methode festgelegt. Diese wird während der Validierung automatisch aufgerufen.
Bei Erfolg stehen die geprüften Daten als 'validated_data' bereit. Bei einem Fehler darf der Ablauf nicht zum Speichern weitergehen.

Bei deinem aktuellen Stand: is_valid() allein gibt bei Fehlern False zurück. Es stoppt deine post()-Methode nicht automatisch. Diese Fehlerbehandlung fehlt noch.

## Die View ruft save() auf

Nach erfolgreicher Validierung löst die View das Speichern aus.
Weil du dem Serializer keinen bestehenden User zum Bearbeiten übergeben hast, ruft save() automatisch deine create() Methode auf und übergibt ihr die geprüften Daten.
Deine create()-Methode erledigt dann:

- Über create_user() den User mit gehashtem Passwort anlegen.
- Das Profil erstellen und mit diesem User verknüpfen.
- Den erstellten User zurückgeben.
  
Dieser User gelangt über save() zurück zur View.
Deshalb braucht die View dessen Rückgabewert für den nächsten Schritt.

## Die View erstellt den Token

Jetzt existiert der User in der Datenbank. Die View kann für genau diesen User einen Token erstellen lassen.
Der Token dient dem Frontend später als Nachweis bei Anfragen, die eine Anmeldung erfordern.

## Die View sendet die Antwort

Zum Schluss gibt die View eine Response zurück: mit dem Token, den vorgesehenen Userdaten und dem Status 201 Created.

request.data        |           Ungeprüfte Eingaben aus der Anfrage
Serializer-Instanz  |           Verarbeitet diese konkrete Registrierung
is_valid()          |           Startet die Validierung
validate()          |           Deine zusätzlichen Prüfregeln im Serializer
validated_data      |           Erfolgreich geprüfte Daten
save()              |           Löst nach der Validierung das Erstellen aus
create()            |           Deine Umsetzung zum Anlegen von User und Profil
Response            |           Antwort der View an das Frontend

## Reihenfolge

Für den Token brauchst du einen User.
Damit der User existiert, musst du ihn speichern.
Bevor du speicherst, müssen die Daten geprüft sein.
Damit der Serializer sie prüfen kann, musst du ihm die Eingaben übergeben.