# URL Shortener (Скорочувач URL-адрес) #

* Author: Noelia Ruiz Martínez

This add-on is used to shorten URLs from NVDA through [is.gd][1].

## Діалог скорочення URL ##

Перейдіть до меню NVDA, підменю «Інструменти» і активуйте пункт «Скоротити
URL-адресу».

Крім того, ви можете призначити жест у діалозі «Жести вводу» NVDA.

Діалог скорочення URL містить такі елементи керування:

* Список для вибору однієї зі збережених URL-адрес. У цьому списку натисніть
  клавіші shift+tab для пошуку, і tab для натискання однієї з наведених
  нижче кнопок.
* Скопіювати скорочену URL-адресу. Цей пункт також можна активувати,
  натиснувши клавішу Enter у списку URL-адрес.
* A readonly box showing details about the selected URL.
* Set of controls to shorten a new URL: Provide the new URL; optionally, you
  can set a display name and a custom subfix for the shortened URL. Finally,
  press the Shorten URL button.
* Перейменувати: відкриває діалог для надання нового імені для відображення
  вибраної URL-адреси у списку.
* Видалити: відкриває  діалог для видалення вибраної URL-адреси.
* Видалити збережені URL-адреси: відкриває  діалог для видалення збережених
  URL-адрес із папки конфігурації.
* Закрити.

## Changes for 8.0.0 ##

* Added a readonly box with details about the selected URL.

## Changes for 5.0.0 ##

* The new URL dialog has been replaced with a set of controls in the main
  dialog, so that the focus can be placed in the relevant field to fix
  possible errors.

## Зміни у версії 2.0.0 ##

* Опція Скоротити URL-адресу не з'являтиметься кілька разів у підменю
  Інструменти під час перезавантаження плагінів.
* Діалог «Нова URL-адреса» містить поле для редагування, у якому можна
  вказати власний суфікс для скороченої URL-адреси.

## Зміни у версії 1.0.0 ##

* Перша версія.


[[!tag dev stable]]

[1]: https://is.gd
