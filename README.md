# Discord bot pro server VŠB - informatika :fire:

> Funckionalita? Žádná. :cry:

## Struktura projektu
### Soubory jsou strukturovány tímhle stylem
```
discordbot/
│
├── main.py
│
├── bot.py
│
├── module1/
│   │
│   ├── __init__.py
│   └── module_file.py
│   
├── module2/
│   │
│   ├── __init__.py
│   └── module_file.py
│
└── data/
    │
    └── conf.json
```
### Poté v main.py bude vždy následujicí pořadí importů
```python
# prvně bude importnut client z bot.py
from bot import client

# a po té ostatní moduly
import module1
import module2
```
### V jednotlivých modulech pak v `__init__.py`  budete nastavovat callback funkce na eventy

```python
from bot import client


# you can set whichever event you want
@client.event
async def on_message(message):
    # your desired functionality
```

### Dále je nutný mít nastavený token v `Data/conf.json`
```json
{
    "Token": "your token goes here"
}
```
