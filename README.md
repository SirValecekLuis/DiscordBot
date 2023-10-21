# Discord bot for VŠB - informatika :fire:

## Functionality:
Counting "tobiáš" || "olivk*" || "poli*" from the DC messages and based on the user ID then recorded in DB

/counters @user(optional) -> Bot sends a message only shown to you with all counters available for your record in DB. When used with a parameter it's going to print the user's statistics instead.

## Structure
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
