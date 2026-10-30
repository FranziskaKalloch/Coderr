# Permissions

In Django wird getattr() häufig im Kontext von Berechtigungen (Permissions) verwendet,
um dynamisch zu prüfen, ob ein Benutzer bestimmte Rechte an einem Objekt besitzt, oder um Berechtigungsmethoden dynamisch aufzurufen.

## Dynamische Prüfung von Permission-Methoden

Wenn man Berechtigungen dynamisch basierend auf einem String (z. B. 'has_perm') prüfen möchte,
kann man getattr() auf dem User-Objekt aufrufen.

'getattr' bedeutet: "Lies ein Attribut von einem Objekt"

Die Funktion nimmt drei Angaben entgegen:

'getattr(object, name, default)'

object         -> request.user    -> Das Objekt, dessen Attribut man lesen möchte(z.B. eine Model-Instanz)
name           -> "profile"       -> Eine Zeichenkette, die den Namen des Attributs enthält
default.       -> None            -> optional: der Wert, der zurückgegeben wird, wenn das Attribut nicht existiet

Der Defaultwert ist ein Ersatzwert, den man selbst festlegt. None bedeutet hier: "Es wurde kein Profil gefunden"

Wenn man den Wert eines Feldes auslesen möchte:

Ein einfaches Django-Model            -> user = User.object.get(id=1)
Statischer Zugriff (normales Pythion) -> name = user.first.name
Dynamischer Zugriff mit getattr       -> feld_name = "first_name" | name = gettatr(user, feld_name)

## Das Benutzerobjekt holen

-> user = request.user

## Permission Class mit getattr

from rest_framework.permissions import BasePermission

class BusinessUser(BasePermission):
    """Allow public GET access and restrict creation to business users."""

    def has_permission(self, request, view):
        user = request.user

        if request.method == "GET":
            return True

        if not user.is_authenticated:
            return False

        profile = getattr(user, "profile", None)

        if profile is None:     # Deny access if the user has no profile.
            return False

        return profile.type == "business"

## Beispiel

Punktnotation       ->    user.email
getattr()           ->    getattr(user, "email")
