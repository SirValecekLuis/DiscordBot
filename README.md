# Discord bot pro server VŠB - informatika :fire:

> Funckionalita? Žádná. :cry:

## Struktura projektu
### Soubory jsou strukturovány tímhle stylem
```
discordbot/
│
├── src/
│   │
│   ├── start.py
│   │
│   └── bot/
│       │   
│       ├── package/
│       │   │
│       │   ├── __init__.py
│       │   └── module.py
│       ├── __init__.py
│       ├── bot.py
│       └── token.py
└── data/
    │
    └── conf.json
```

## Důležité je nastavit discord token v  `Data/conf.json`
```json
{
    "Token": "your token goes here"
}
```
