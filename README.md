# Rendkívüli Ügyek Minisztériuma
MKKP Rendkívüli Ügyek Minisztériuma python implementáció

Honlap: https://rendkivuliugyek.com/  
Dokumentáció: https://mkkp.github.io/rendkivuli_ugyek/  

### A Rendkívüli Ügyek Minisztériuma webes alkalmazás a következő funkciókat teszi lehetővé:  
* Közterületen található elhanyagolt állapotú tárgyakról szóló bejelentés felvétele az adatbázisba.  
* Bejelentések adminisztrációja. 
(státuszok közti váltás, szervező hozzáadása, képek hozzáadása utólagosan)  
* Bejelentések körüli kommunikáció
(levelek, kommentek, elérhetőségek)  
* Bejelentések megjelenítése 
(kártyaként és térképen) 
* **Kapcsolattartás biztosítása a Ganümédeszen állomásozó űrhajókkal**

### Tesztkörnyezet felállítása

Egy localhost-on kiszolgált tesztkörnyezetet a következő módon lehet létrehozni:

```
git clone git@github.com:mkkp/rendkivuli_ugyek.git
cd rendkivuli_ugyek
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp test.env .env
python3 app.py
```

Ez az env config mockolni fogja az e-mail küldést és az OAuth-ot, így lehet
az éles rendszerhez való hozzáférés nélkül tesztelni.

A test user jogosultsági szintjét az első bejelentkezés után a következőképp lehet
változtatni:
```
echo "update user set role='registered' where email='ketfarku@kutyi.kuty';" | sqlite3 db/app.db
```

---
