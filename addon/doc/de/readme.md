# URL verkürzen #

* Author: Noelia Ruiz Martínez

This add-on is used to shorten URLs from NVDA through [is.gd][1].

## Dialogfeld zum URL verkürzen ##

Gehen Sie in das NVDA-Menü, Untermenü Extras und wählen Sie den Eintrag "URL
verkürzen" aus.

Alternativ können Sie einen Tastenbefehl über das Dialogfeld für die
Tastenbefehle in NVDA zuweisen.

Das Dialogfeld zum URL verkürzen enthält die folgenden Steuerelemente:

* Eine Liste, um eine der gespeicherten URLs auszuwählen. Drücken Sie in
  dieser Liste Umschalt+Tab, um nach einer zu suchen und Tab, um eine der
  folgenden Tasten zu betätigen.
* Verkürzte URL kopieren. Dies kann auch durch Drücken der Eingabetaste in
  der Liste der URLs getätigt werden.
* A readonly box showing details about the selected URL.
* Set of controls to shorten a new URL: Provide the new URL; optionally, you
  can set a display name and a custom subfix for the shortened URL. Finally,
  press the Shorten URL button.
* Umbenennen: Öffnet ein Dialogfeld, in dem Sie einen neuen Namen für die
  Anzeige der ausgewählten URL in der Liste eingeben können.
* Löschen: Öffnet einen Dialogfeld zum Löschen einer ausgewählten URL.
* Gespeicherte URLs entfernen: Öffnet einen Dialogfeld zum Entfernen
  gespeicherter URLs aus dem Konfigurationsordner.
* Schließen.

## Changes for 8.0.0 ##

* Added a readonly box with details about the selected URL.

## Changes for 5.0.0 ##

* The new URL dialog has been replaced with a set of controls in the main
  dialog, so that the focus can be placed in the relevant field to fix
  possible errors.

## Änderungen in 2.0.0 ##

* Die Option "URL verkürzen" wird im Untermenü "Extras" nicht mehr mehrfach
  angezeigt, sobald Plugins neu geladen werden.
* Das Dialogfeld für Neue URL enthält ein Bearbeitungsfeld, in dem Sie ein
  benutzerdefiniertes Subfix für die verkürzte URL angeben können.

## Änderungen in 1.0.0 ##

* Erstveröffentlichung.


[[!tag dev stable]]

[1]: https://is.gd
