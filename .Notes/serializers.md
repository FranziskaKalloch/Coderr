# Umwandlung zwischen Model-Objekten und API Daten, Validierung sowie Erstellen und Aktualisieren

Was verlangt der Endpunkt?
Welche Aufgabe übernimmt der Serializer beziehungsweise die View?
Wie setzen wir es um?
Warum entscheiden wir uns dafür?
Wie prüfen wir das Verhalten?

## Was macht ein Serializer?

Er beschreibt, welche Daten deine API annimmt, wie sie geprüft werden und welche Daten sie ausgibt.
Dabei hat er zwei Richtungen:

- Eingehend -> Daten aus dem Request -> Eingaben prüfen und in verwendbare Python-Daten umwandeln.
- Ausgehend -> Bspw. User Objekt -> Ausgewählte Werte für die API Antwort aufbereiten

Der Parser verarbeitet das eingehende JSON. Der Serializer prüft die daraus entstandenen Daten. Am Ende macht der Renderer aus den Antwortdaten wieder JSON. DRF: Serializer

Was bedeutet „ausgehend“?
„Ausgehend“ bedeutet: Diese Daten verlassen dein Backend als Antwort an den Client.
Ja, bei deiner Registrierung ist damit die Success Response gemeint. Allgemein können auch Fehlerantworten ausgehen.

Warum werden diese Daten ausgegeben?
Damit das Frontend mit dem Ergebnis weiterarbeiten kann:

- Der token kann bei späteren Anfragen zur Authentifizierung mitgeschickt werden.
- Die user_id identifiziert das angelegte Konto.
- username und email informieren das Frontend darüber, welches Konto erstellt wurde.
Der Benutzer sieht dabei nicht unbedingt die komplette Antwort. Das Frontend verarbeitet sie und entscheidet, was es auf der Oberfläche anzeigt.

### ModelSerializer

Ein ModelSerializer nimmt dir Arbeit ab: Er kann aus einem Model Felder und bestimmte Validatoren ableiten und bringt einfache Speicheroperationen mit. Eure Registrierung braucht zusätzlich eigene Regeln für Passwortbestätigung, Passwortspeicherung und Profilanlage. DRF: ModelSerializer

### Queryset

Ein QuerySet kann beispielsweise einem Eindeutigkeitsvalidator sagen, in welchen Datensätzen er nach einem bereits vergebenen Wert suchen soll. Das bedeutet nicht, dass du erst sämtliche User laden und selbst durchlaufen musst. DRF: Validatoren

### „Passwort und Passwortbestätigung sind write_only und required?“

- required bedeutet: Das Feld muss in der Eingabe vorhanden sein.
- write_only bedeutet: Der Serializer nimmt das Feld entgegen, gibt es aber nicht aus.
- Ein leeres Passwort auszuschließen ist eine zusätzliche Feldregel.
write_only verschlüsselt oder hasht nichts. Es steuert ausschließlich die Ausgabe. DRF: Felder

### „Was überprüft validate(self, attrs)?“

attrs enthält die bereits auf Feldebene geprüften Eingaben. Die Methode eignet sich für Regeln, die mehrere Felder gemeinsam betreffen – etwa den Passwortvergleich.
Bei einem Fehler wird ein Validierungsfehler ausgelöst. Bei Erfolg werden die geprüften Daten zurückgegeben. Die Methode speichert dabei noch keinen User. DRF: Validierung

### „Warum validated_data beim Erstellen?“

Weil das die Daten sind, die die Serializer-Prüfungen erfolgreich durchlaufen haben.
Der Ablauf lautet:

Request-Daten → Validierung → validated_data → Speichern

Die View startet über is_valid() die Prüfung. Erst danach ruft sie save() auf. Wenn der Serializer dabei eine neue Instanz erstellen soll, führt save() dessen create()-Methode aus.
Vor dem Anlegen müssen die Daten ihrem Zweck zugeordnet werden: repeated_password wird nicht gespeichert, type gehört zum Profile und die User-Felder zum User.

### „User erstellen, danach set_password und speichern?“

Entscheidend ist, dass das Passwort als Hash gespeichert wird. Ein einfaches Anlegen eines Users mit einem gewöhnlich zugewiesenen Passwort erledigt das nicht automatisch.
Djangos create_user() übernimmt die Passwort-Hashbildung bereits.
set_password() ist eine weitere Möglichkeit; es verändert die Instanz, speichert sie aber nicht selbst. Passwortqualität und Hashbildung bleiben zwei getrennte Aufgaben.

### Was übernimmt anschließend die View?

Die View organisiert den HTTP-Ablauf:

1. Eine Registrierungsanfrage entgegennehmen.
2. Den Zugriff ohne vorhandenen Login erlauben.
3. Die Request-Daten an den Serializer übergeben.
4. Die Validierung starten.
5. Bei gültigen Daten das Speichern auslösen.
6. Den Token für den angelegten User bereitstellen.
7. Die vorgegebene Antwort mit Status 201 zurückgeben.
Ungültige Eingaben führen laut eurer API zu 400. Ein interner Fehler ist 500 und sollte nicht als gewöhnlicher Eingabefehler behandelt werden.
Der Serializer kennt die Datenregeln; die View steuert die Anfrage und die HTTP-Antwort. User und Profile sollten außerdem gemeinsam erfolgreich angelegt werden, damit bei einem Fehler kein halbfertiger Registrierungszustand entsteht.

## Registrierung (SERIALIZER)

1. Was bekommt unser Registrierungsendpunkt, und was gibt er zurück?
2. Welche Eingaben werden gespeichert, welche nur geprüft?
3. Warum prüfen wir die Daten, bevor wir einen User anlegen?

Request Body besteht aus: username, email, password, repeated_password, type
Sucess Response besteht aus: token, username, email, user_id

Das ist der Ausgangspunkt für den Serializer!

Der RegisterSerializer nimmt die fünf Eingabefelder entgegen, prüft sie und übernimmt das Anlegen von User und Profile.

Die View stellt anschließend den Token bereit und setzt die vorgegebene Antwort aus token, username, email und user_id zusammen

write_only=True für password und repeated_password, da das Feld nur als Eingabe dient und diese verarbeitet.

### Passwörter miteinander vergleichen - validate(self, data)

Diese Methode ist eine Prüfung, die mehrere Felder gemeinsam betreffen.
Die Methode bekommt ein Dictonary mit den bereits auf Feldebene geprüften werden.
Wenn die gemeinsame Prüfung fehlschlägt, löst sie einen ValidationError aus

Bei data['password'] ist data das Dictonary und password der Schlüssel. Das eingegebene Passwort is der dazugehörige Wert

Warum ist data ein Dictonary?
DRF sammelt die geprüften Eingaben als Zuordnung von Feldnamen zu deren Werten.
So weiß eine Methode, welcher Wert zu welchem Serializer-Feld gehört.
DRF übergibt dieses Dictonary automatisch an die validate() Methode, nachdem die einzelnen Feldprüfungen erfolgreich waren.

### Wichtig

data enthält die bereits ausgelesenen und auf Feldebene geprüften Eingaben als Python-Dictionary.

Bis dahin ist Folgendes passiert:

1. Der Client schickt die Registrierungsdaten als JSON.
2. DRF wandelt das JSON in Python-Daten um.
3. Die Serializer-Felder prüfen die einzelnen Werte, etwa das E-Mail-Format und die erlaubten Kontotypen.
4. Deine validate()-Methode bekommt diese Werte als data und prüft jetzt den Zusammenhang zwischen den beiden Passwörtern.
Geprüft bedeutet hier noch nicht gespeichert. Erst wenn auch deine gemeinsame Validierung erfolgreich ist, stehen die Daten als validated_data zum anschließenden Speichern bereit.

Die View stößt das Speichern an; die create()-Methode des Serializers führt es aus.
Für eure Registrierung ist die Aufteilung so:

1. View: Übergibt die Request-Daten an den Serializer.
2. View: Ruft is_valid() auf. Dabei laufen die Feldprüfungen und deine validate()-Methode.
3. View: Ruft bei gültigen Daten serializer.save() auf.
4. Serializer: save() ruft für die Neuanlage die Methode create(validated_data) auf. Dort werden User und Profile in der Datenbank angelegt.
Dein bisheriges return data gibt also nur die geprüften Daten zurück. Es speichert noch nichts.

### create() im Serializer

In create() wird aus den geprüften Eingaben ein neuer User angelegt.

In der create()-Methode passiert gedanklich Folgendes:

1. Die geprüften Daten entgegennehmen.
   validated_data enthält Username, E-Mail, die beiden Passwörter und den Kontotyp.
2. Die Daten zuordnen.
   Die Passwortbestätigung wird nicht mehr benötigt. Den Kontotyp behalten wir für das Profile. Username, E-Mail und Passwort werden für den User verwendet.
3. Den User anlegen.
   Django erstellt den Datenbankeintrag und vergibt eine ID. Dabei muss das Passwort gehasht werden. Danach hast du in der Methode ein User-Objekt, mit dem du weiterarbeiten kannst.
4. Das Profile anlegen.
   Dein Profile-Model hat ein Feld namens user. Diesem Feld ordnest du den gerade erstellten User zu. Zusätzlich bekommt das Profile den geprüften type.
5. Den User zurückgeben.
   Dadurch erhält die View beim Aufruf von serializer.save() den angelegten User zurück.

Beim Erstellen übergibt man die Werte, die im neuen User gespeichert werden sollen. Hier für die Registrierung wird username, email und password benötigt.
Diese Werte werden aus validated_data gelesen, weil sie bereits die Serializer Prüfung durchlaufen haben.

also -> user = User.objects.create_user(()
create_user(). Diese Methode kümmert sich auch darum, das Passwort zu hashen.

Die beiden Seiten haben unterschiedliche Aufgaben:

Eine Methode wie create_user() benötigt Informationen, um einen User anzulegen: Wie soll er heißen? Welche E-Mail-Adresse hat er?

username=validated_data['username'] bedeutet also: „Gib der Methode als Benutzernamen den Wert, den der Benutzer eingegeben hat.“

### Passwort auf Stärke testen

validate_password(). Sie prüft das Passwort anhand der Regeln aus deinen AUTH_PASSWORD_VALIDATORS in den Settings.

### Token erstellen im Serializer

mit:

token = Token.objects.create(user=user)

erstellen wir einen Token für den entsprechenden User.
Links user: das Feld im Token-Modell, das auf einen User verweist.
Rechts user: deine Variable, die das erstellte User-Objekt enthält.
Wenn du den Token bereits im Serializer erstellst, muss die View ihn nicht erneut erstellen.

Allerdings muss die View den Token kennen, um ihn in der Antwort zurückzusenden. Im Serializer erstellt zu sein bedeutet nicht automatisch, dass die View ihn erhält. Entscheidend ist, was deine create()-Methode zurückgibt: Dieser Rückgabewert kommt bei der View über serializer.save() an.
