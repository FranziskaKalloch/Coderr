# Die `patch`-Methode erklärt

Die `patch`-Methode erlaubt einem angemeldeten Nutzer, **einzelne Felder seines eigenen Profils zu ändern**. Der Client muss nur die Felder senden, die geändert werden sollen.

## 1. Die Anfrage entgegennehmen

```python
def patch(self, request, pk):
```

Die Methode wird bei einer HTTP-PATCH-Anfrage aufgerufen.

- `request` enthält unter anderem den angemeldeten Nutzer (`request.user`) und die gesendeten Daten (`request.data`).
- `pk` kommt aus der URL und ist hier die **User-ID**, nach der gesucht wird.

## 2. Das Profil suchen

```python
profile = get_object_or_404(Profile, user_id=pk)
```

Django sucht das Profil, dessen `user_id` dem Wert aus der URL entspricht. Existiert es nicht, wird die Anfrage mit **404 Not Found** beendet.

## 3. Die Berechtigung prüfen

```python
self.permission_classes = [IsOwner]
self.check_object_permissions(request, profile)
```

Hier setzt du für die anschließende Berechtigungsprüfung die Klasse `IsOwner` ein.

`check_object_permissions()` ruft deren `has_object_permission()` auf und übergibt das gefundene Profil. Dort sollte geprüft werden, ob `request.user` der Besitzer dieses Profils ist. Falls die Prüfung scheitert, wird die Methode abgebrochen; ein angemeldeter Nutzer erhält dann normalerweise **403 Forbidden**.

Die auf Klassenebene gesetzte Berechtigung `IsAuthenticated` wurde bereits vor dem Aufruf von `patch()` geprüft.

## 4. Den Serializer mit den Änderungen vorbereiten

```python
serializer = ProfileUpdateSerializer(
    profile,
    data=request.data,
    partial=True
)
```

Der Serializer erhält drei wichtige Angaben:

| Angabe | Bedeutung |
|---|---|
| `profile` | Die bestehende Profilinstanz, die aktualisiert werden soll |
| `data=request.data` | Die vom Client gesendeten Änderungen |
| `partial=True` | Nicht alle normalerweise erforderlichen Felder müssen mitgesendet werden |

Sendet der Client beispielsweise:

```json
{
  "first_name": "Max"
}
```

wird dieses Feld aktualisiert, sofern der Serializer es unterstützt. **Nicht mitgesendete Felder behalten ihren bisherigen Wert.**

## 5. Die Daten prüfen

```python
if serializer.is_valid():
```

Der Serializer prüft, ob die gesendeten Daten seinen Regeln entsprechen, beispielsweise hinsichtlich Datentypen und Feldlängen. Die Prüfung allein speichert noch nichts.

## 6. Die Änderungen speichern

```python
serializer.save()
```

Sind die Daten gültig, speichert der Serializer die Änderungen am bestehenden Profil. Weil du ihm zuvor `profile` übergeben hast, führt er eine Aktualisierung aus.

## 7. Das aktualisierte Profil zurückgeben

```python
serializer = ProfileDetailSerializer(profile)
return Response(serializer.data, status=status.HTTP_200_OK)
```

Anschließend verwendest du den `ProfileDetailSerializer`, um das aktualisierte Profil für die Antwort aufzubereiten. So kann die Antwort mehr Felder enthalten, als über den `ProfileUpdateSerializer` bearbeitet werden dürfen.

Der Client erhält die Profildaten mit **200 OK**.

## 8. Ungültige Daten behandeln

```python
return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

Sind die Eingabedaten ungültig, werden keine Änderungen gespeichert. Stattdessen erhält der Client **400 Bad Request** und die Fehlerdetails.

## Ablauf im Überblick

**Profil suchen → Besitz prüfen → Änderungen validieren → speichern → aktualisiertes Profil zurückgeben.**
