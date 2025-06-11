**⚠️ TENTO DOCKER SLOUŽÍ POUZE PRO LOKÁLNÍ VÝVOJ ⚠️**

**Pro rozjetí docker-compose.yml je zapotřebí nainstalovat minimálně docker engine nebo docker desktop**

Potom stačí rozjet soubor docker-compose.yml, který se nachází v ../DiscordBot/docker_local_dev/mongoDB/ ať už pomocí terminálu, nebo jako službu např. v Pycharm a počkat na úvodní instalaci mongoDB a Atlas GUI. 

Jakmile se nainstaluje celej container tak stačí znovu spustit celej container/zapnout znova službu v Pycharm a mongoDB běží na adresách, které jsou níže.

Po spuštění je k dispozici:

🗄️ MongoDB databázi na localhost:27017

🌐 Atlas UI na http://localhost:8081

Ve svém .env souboru nastav connection string:

DATABASE_LOGIN="mongodb://admin:admin@localhost:27017/"

**Po spuštění skriptu start.py se automaticky:**

✅ Vytvoří nová databáze DiscordBot

✅ Vytvoří všechny potřebné (prázdné) kolekce po prvním spuštění bota