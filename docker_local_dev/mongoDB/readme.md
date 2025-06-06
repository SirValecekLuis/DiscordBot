**Docker Desktop musí být nainstalovaný a spuštěný**

Potom stačí rozjet soubor Dockerfile, který se nachází v ../DiscordBot/docker_files/mongoDB/ ať už pomocí terminálu, nebo jako službu např. v Pycharm a počkat na úvodní instalaci mongoDB a Atlas GUI. 

Jakmile se nainstaluje celej container tak stačí znovu spustit celej container/zapnout znova službu v Pycharm a mongoDB běží na adresách, které jsou níže.

Po spuštění je k dispozici:

🗄️ MongoDB databázi na localhost:27017

🌐 Atlas UI na http://localhost:27080

Ve svém .env souboru nastav connection string:

DATABASE_LOGIN="mongodb://admin:admin@localhost:27017/"

**Po spuštění skriptu start.py se automaticky:**

✅ Vytvoří nová databáze discord_bot

✅ Vytvoří všechny potřebné (prázdné) kolekce

✅ Kolekce se postupně naplní během používání bota