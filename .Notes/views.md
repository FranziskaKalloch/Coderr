# Verarbeitung von Anfragen, Berechtigungen, Filter und Pagination

Was verlangt der Endpunkt?
Welche Aufgabe übernimmt der Serializer beziehungsweise die View?
Wie setzen wir es um?
Warum entscheiden wir uns dafür?
Wie prüfen wir das Verhalten?

Der View macht nur drei Dinge:

- Daten entgegennehmen,
- an den Serializer übergeben,
- Antwort zurückschicken.

Die eigentliche Arbeit steckt im Serializer.

## RegisterView()

Die vier Zeilen in post() entsprechen genau dem Ablauf:

RegisterSerializer(data=request.data): Daten vom Frontend in den Serializer geben.
is_valid(raise_exception=True): prüfen lassen. Bei Fehlern wird automatisch eine 400er-Antwort geschickt.
serializer.save(): User und Profil anlegen lassen (ruft dein create() auf).
Response(...): Erfolg zurückmelden.

## Permission Class

Eine Permission Class legt fest, wer einen View aufrufen darf. In Django REST Framework gilt:

Ohne Einstellung darf jeder jeden View aufrufen (Standard ist AllowAny).
Mit globaler Einstellung in der settings.py gilt diese für alle Views:

REST_FRAMEWOR = {"DEFAULT_PERMISSION_CLASSES"; ["rest_framework.permissions.IsAuthenticated"]}

Sobald du das so gesetzt hast, braucht jeder View einen eingeloggten User. Bei der Registrierung ist das ein Problem: Der User hat noch keinen Account und kann sich nicht eingeloggt haben, also bekäme er ein 401 Unauthorized. Deshalb überschreibst du im Register-View mit permission_classes = [AllowAny], dass hier jeder zugreifen darf.

Wenn du in deinen Settings nichts dergleichen stehen hast, kannst du die Zeile weglassen. Sie schadet aber nicht, weil sie auch zeigt, dass der View absichtlich öffentlich ist.

## Warum user = serializer.save()?

save() ruft deine create()-Methode auf, und alles, was create() mit return user zurückgibt, ist der Rückgabewert von save(). Die Variable fängt dieses frisch angelegte User-Objekt auf.

Du brauchst sie nur, wenn du mit dem User danach noch etwas machst, zum Beispiel:

Daten für die Response auslesen (user.id, user.email)
einen Token für genau diesen User erzeugen (Token.objects.get_or_create(user=user))
