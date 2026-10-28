# UNIT TESTS

Mit Unit Tests prüft man die kleinsten Einheiten der Logik.

Unit Tests können Automatisiert gestartet werde, z.B. jedes Mal, wenn man Änderungen pusht läuft der Test durch.

Die Unit Tests werden in der dazugehörigen App in der test.py definiert.
Man kann auch einen Ordner anlegen und dort die einzelnen Tests Datei anlegen.

## Tests definieren

In einer Klasse (class Tests(TestCase)) werden Methoden definiert, die die eigentlichen Tests sind.
Diese Methoden müssen immer mit 'test_example' anfangen, damit Django sie als Tests ansieht. Danach schreibt man einfach was man testen möchte.
