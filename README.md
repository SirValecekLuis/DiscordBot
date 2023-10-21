# Discord bot pro server VŠB - informatika :fire:

## Funkcionality:
Počítání slov "tobiáš" a "olivk*" či "poli" ve zprávě od uživatele a zapsání do DB na základě ID

## TODO: 
Přidat emote když někdo napíše zmíněné slovo z counteru

Přidat loggování na errors (.log/zasílání zpráv do PM či nějaké loggování do speciálního DC channelu?)

Upravit strukturu projektu v README na aktuální + upravit popis projektu a popsat co se používá a co k čemu slouží 

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
