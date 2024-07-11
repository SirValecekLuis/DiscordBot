# Discord bot for VŠB - informatika 🔥

## Moduly:

`auto_pin.py` - Slouží k automatickému pinnování zpráv v channelu.

`auto_voice.py` - Slouží k automatickému vytváření voice channelu pro discord uživatele.

`countdown.py` - Odpočet kolik zbývá do zkoušky s pravidelným zasíláním do channelu.

`counter.py` - Počítá kolikrát někdo napsal nějaké slovo.

`database_communication.py` - Slouží k vkládání proměnných do DB skrz discord, pouze pro administrátory.

`help.py` - Obyčejné informativní příkazy.

`leaderboard.py` - Vypisuje uživatele s nejvíce slovy a dalšími věcmi (z `counter.py`).

`login_info.py` - Čistě informativní modul pro vypsání toho, že bot byl spojen s API discordu.

`semester_switching.py` - Slouží k prohození semestrů pro zjednodušení práce po konci semestru.

`welcome_message.py` - Pošle novému připojenému uživateli uvítací zprávu.

## Codebase

```
discordbot/
│
│── start.py
│── settings.py
│── error_handling.py
│── database.py
│
│── bot/
    │
    │── __init__.py
    │── auto_pin.py
    │── auto_voice.py
    │── countdown.py
    │── counter.py
    │── database_communication.py
    │── help.py
    │── leaderboard.py
    │── login_info.py
    │── semester_switching.py
    │── welcome_message.py
    │

```

# Pravidla pro přispívání do projektu

## 📚 Pravidla pro moduly (soubory ve složce `bot`)

### 🔧 Struktura modulů

- Každý modul **musí** obsahovat funkci `setup` (stačí zkopírovat z ostatních modulů).
- V každém Cogu **musí** být implementována funkce `cog_command_error` (stačí zkopírovat z ostatních modulů).

### 🧹 Kvalita kódu

- **Vždy používejte Pylint.**
- Pište **komentáře ke kódu**, aby se zpětně dalo snadno pochopit, co se kde děje.
- Používejte verze dané `requirements.txt` a `requirements_dev.txt` s Pythonem 3.11.

## 🤝 Pravidla pro přispívání do repozitáře

### 🔄 Pull Requesty (PR)

- Pokud nejsou změny triviální (např. změna 1 řádku, přepis proměnné), **měly by vždy procházet přes Pull Request**.
- Triviální změny mohou být commitovány přímo do main branch, ale pouze pro contributors a s rozvahou.

### ✅ Kontrola kvality

- **Celý PR musí projít Pylint checkem**.
- Schválení alespoň 2 contributory.

Hodně štěstí s PR! 🎉