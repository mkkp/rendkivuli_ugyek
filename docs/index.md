# Rendkívüli Ügyek Minisztériuma

## Specifikáció

A Rendkívüli Ügyek Minisztériuma webes alkalmazás a következő funkciókat teszi lehetővé:  

* Közterületen található elhanyagolt állapotú tárgyakról szóló bejelentés felvétele és gyűjtése az adatbázisba.  
* Bejelentések adminisztrációja. (státuszok közti váltás, szervező hozzáadása, képek hozzáadása utólagosan)  
* Bejelentések körüli kommunikáció lehetővé tétele.(levelek, kommentek, elérhetőségek)  
* Bejelentések megjelenítése (kártyaként és térképen)  

## Az applikáció általános magas szintű leírása  

A Rendkívüli Ügyek Minisztériuma tartalmazza a következő oldalakat:  
1. Kezdőlap  
2. Bejelentés  
3. Ügy adatlap  
4. Összes bejelentés  
5. Térkép  
6. Statisztikák  
7. Regisztráció  
8. Bejelentkezés / Kijelentkezés  
  
### 1. Kezdőlap  
  
A kezdőlapot minden felhasználói jogosultság eléri.  
A kezdőlapon a következő leírás szerepel:  
> Üdv az MKKP városmódosító oldalán!  
> Benőtte a gaz a szétrúgott elektromos szekrényt?  
> Kátyúba dőlt az összegrefitizett villanyoszlop?  
> Nem látszik a szeméttől a lekopott zebra, amin amúgy se lehetne átkelni kerekesszékkel?  
> Jelentsd be a térképen a problémákat, amiket a városodban látsz és mi megoldjuk!  
> Vagy legalább viccessé tesszük.  
> Vagy legalább széppé.  
> A bejelentések alatt kommentben várjuk az ötleteket, hogy mit kezdjünk az adott problémával.  
> Ha bármi kérdésed van az oldallal kapcsolatban, esetleg kezdtél valamit az egyik bejelentéssel,  
> írj nekünk a ketfarkukutya@gmail.com-ra!  

### 2. Bejelentés  

A bejelentés oldalt minden felhasználói jogosultság eléri.  
A bejelentés oldalon a felhasználó városfelújítós probléma bejelentést tud tenni.  
A felület célja az ügy adatainak és az ügyhöz csatolt képek felvétele az adatbázisba.  
Kötelezően kitöltendő mezők:  
- Probléma megnevezése (szabad szöveges mező)
- Típus (legördülő menü)
  - Szemét
  - Közmű
  - Út és Járda
  - Akadálymentesítés
  - Növény
  - Állat
  - Épület
  - Közlekedés
  - Tájékoztatás
  - Műemlék

-	Részletes leírás (szabad szöveges mező)    
-	Képek feltöltése (file dialógus menü)    
Ha a felhasználó kiválasztja a képeket, megjelenik még egy opcionálisan használatba vehető  
file feltöltési mező, ahol a felhasználó további képeket adhat a bejelentéshez.
-	Email cím (szabad szöveges mező)  
-	Adatkezelési szabályzat elfogadása (bepipálható mező)  
-	Cím (szabad szöveges mező)  
  
**Opcionális mezők:**  
-	Megoldási javaslat (szabad szöveges mező)  
-	Telefon (szabad szöveges mező)  
A bejelentés oldalon a felhasználó képeket is tud feltölteni.    
A helyszín megadásánál a felhasználó egy gomb segítségével le tudja ellenőrizni / kiegészíteni az általa begépelt helyszín címet.  
A cím megadását egy térkép segíti, amire ha a felhasználó rákattint, akkor a cím automatikusan kitöltődik.  
  
Mobilon a cím megadását a helyhozzáférés segíti.   
Ha a felhasználó készülékén a helymeghatározás be van kapcsolva, akkor helyszín adatok automatikusan kitöltésre kerülnek.  
Ha a felhasználó készülékén a helymeghatározás ki van kapcsolva, akkor a következő üzenetet kapja:  
*“Ajjaj... A helyhozzáférés nincsen engedélyezve. Ha szeretnéd, hogy robokutyi töltse ki helyetted a címet, akkor kérlek engedélyezd.”  
Ha a felhasználó ekkor engedélyezi a helyhozzáférést és frissíti az oldalt, akkor helyszín adatok automatikusan kitöltésre kerülnek.*

A térképen található egy kereső mező, amit szintén lehet használni a cím megadásakor.  
A térképen szerepelnek navigációs ikonok.  
A térképet ki lehet nagyítani teljes méretűre. 

A Bejelent gombra kattintva, a kötelező mezőkre lefut egy űrlap ellenőrzés. 
Ha egy kötelező mező kitöltetlenül maradt, akkor a következő hibaüzenetek válnak láthatóvá az űrlapon, 
aszerint hogy melyik mezőt nem töltötték ki:  
-	Probléma megnevezése: Ha nem tudod megnevezni, akkor az nem probléma.  
-	Típus: Tök széles a választék, bökj rá egyre!  
-	Részletes leírás: Nem baj, ha nem töltöd ki. Tényleg. Csináld csak! Semmi baj. Nem haragszunk. Azt csinálsz, amit akarsz.  
-	Képek feltöltése: Ellopták a képfájlt. Próbáld újra!  
-	Email cím: A PIN-kódod jól jönne, de inkább írd be ide a mailed.  
-	Adatkezelési szabályzat elfogadása: Haladjunk, kérem, haladjunk.  
-	Cím: Sajnos pontosan meg kell mondanod, hogy hol van mi, merre, miként.
 
A program a háttérben végez egy email ellenőrzést, és megszakítja a bejelentést ha:  
- szintaktikailag hibás az email cím pl nincs benne @ karakter (Hibaüzenet: A Kutya mindenit de fura ez az email cím!)  
- a cím mezőben “http” karakterláncot talál.  
- nem engedélyezett file formátumokat talál (engedélyezett: png, jpeg)

Ha az űrlap ellenőrzés nem talál kitöltetlen kötelező mezőt, akkor elkezdi az adatok és képek feltöltését az adatbázisba.   
Töltés közben egy gif és egy felirat (Türelem, már dolgozunk rajta!) tájékoztatja a felhasználót arról, hogy a rendszer munkát végez.  
Ha sikeres a bejelentés, rendszerüzenetet kap a felhasználó:   
*Gratulálunk, sikeres bejelentés. Küldtünk levelet is.*  

Ha sikeres a feltöltés, a felhasználó által megadott email címre level megy:   

*Szia!  
Köszi, hogy jelezted nekünk az alábbi problémát: valami4642  
4000 mérnökünk és 3600 menyétünk elkezdett dolgozni rajta.    
Hamarosan megoldjuk, vagy nem.  
Keresünk majd, amint kitaláltuk, hogy mit csináljunk a dologgal.  
Addig is itt tudod nyomonkövetni, hogyan állunk vele: https://rendkivuliugyek.com/single_submission/1  
Rendkívüli Ügyek Minisztériuma*  

Ha sikeres a feltöltés, a bejelentés oldal az ügy adatlapjára továbbítja a bejelentő böngészőjét.  

### 3. Ügy adatlap
Az ügy adatlapja minden jogosultsági szintnek elérhető, viszont a felhasználók a különböző jogosultsági szintektől függően más-más honlap elemeket látnak.  
A **regisztrálatlan felhasználó** jogosultági szint a következő elemeket látja az adatlapon:  
- Borítókép  
- A borítóképre rá lehet kattintani, ekkor megjelenik a bejelentés összes képét (borítókép-előtte-utána) tartalmazó galéria.  
- A borítókép teljes felbontásban jelenik meg.  


Ügy Adatlap:  
- Ha az ügy kiemelt ügy, akkor ez az információ megjelenik az adatlap első sorában  
- Leírás  
- Státusz  
- Ebben a státuszban  
- Típus  
- Bejelentve  
- Megye  
- Cím  
- Zárószöveg (csak akkor ha megoldott sátuszú az ügy és kitöltötték ezt a mezőt)


Ha az ügy nem megoldott, akkor megjelenik a következő kapcsolat információ:  
Ha szeretnél részt venni a felújításban, írj nekünk a rendkivuliugyek@mkkp.hu-ra!  
Facebook Share gomb amely megjeleníti az eddigi megosztások számát.  
A facebook megosztásra kattintva a megosztás képe a mindenkori borítókép lesz.  
Ha az ügy nem befejezett, akkor a facebook megosztás szövege a részletes leírás szövege.  
Ha az ügy befejezett, és ki van töltve a zárószöveg mező, akkor a facebook megosztás szövege a zárószöveg szövegével egyezik meg.


- Előtte képek (ha vannak)  
- Ha csak egy kép van, akkor az borítóképként jelenik meg, tehát az előtte képek szekcióban nem jelenik meg.
- Utána képek (ha vannak)
- Térkép

A **regisztrált felhasználó** jogosultsági szint a következő elemeket látja az adatlapon:
- Örökli a regisztrálatlan felhasználó elemeit
- Komment szekció, ahol kommenteket adhat az adatlapphoz, módosíthatja és törölheti azokat. 
  A kommenteknél a felhasználó neve és a komment hozzáadásának dátuma szerepel.
  
A **szervező felhasználó** jogosultsági szint a következő elemeket látja az adatlapon:  
- Örökli a regisztrált felhasználó elemeit
- Adatlap módosítása gomb
- Előtte képek feltöltése
- Utána képek feltöltése
Fontos, hogy az ügyhöz adott szervező, csak az adott ügynél rendelkezik a fentebbi jogokkal. 
	Más ügyeknél a jogosultsági szintje a rendes jogosultsági szintjével egyezik meg.
	
A **regisztrált felhasználó, aki ha bejelentő is** egyben
- Örökli a szervező felhasználó elemeit
Fontos, hogy a regisztrált bejelentő, **csak az adott ügynél** rendelkezik a fentebb jogokkal. 
	Más ügyeknél a jogosultsági szintje a rendes jogosultsági szintjével egyezik meg.
	
A **koordinátor felhasználó** jogosultsági szint a következő elemeket látja az adatlapon:
- Örökli a szervező felhasználó elemeit
	Fontos, hogy a koordinátor felhasználó nem csak egy adott ügynél rendelkezik a 
	fentebb leírt jogosultságokkal, hanem az **összes ügynél**.
	
Az **admin** felhasználó jogosultsági szint a következő elemeket látja az adatlapon:
- Örökli a koordinátor felhasználó elemeit
- Ügy törlése gomb
- Mások kommentjeinek szerkesztése és törlése

### 4. Összes bejelentés
Az összes bejelentés minden jogosultsági szintnek elérhető.   
A különböző jogosultsági szintek között nincsen eltérés; mindenki ugyanazt látja.  
Oldalelemek:  
- Részletes keresés gomb. A gombra kattintva lenyílik egy menü, ahol különböző szűkítéseket lehet megadni:
  - Státusz
  - Típus
  - Megye
  Amennyiben a Megye részbe Budapest-et ad meg a felhasználó, akkor megjelenik egy további legördülő menü, 
  ami a Budapesten belüli kerület választást teszi lehetővé.
- Szöveges keresés 
A szöveges keresés minden státuszban típusban és megyében keres és független az összes többi szűkítési beállítástól.  

A részletes keresés alatt az egyes ügyek kártyái látszódnak. Egy kártya felépítése a következő:  
- Fejléc: Típus piktogram, Típus megnevezés
- Borítókép 
- Bejelentés megnevezése
- Város
- Bejelentés leírása (csak az első mondat)  
	Az összes bejelentés közül egyszerre csak N darab jelenik meg. 
	A honlap alján paginációs menü található.
	
### 5. Térkép
A térkép minden jogosultsági szintnek elérhető.  
A különböző jogosultsági szintek között nincsen eltérés; mindenki ugyanazt látja.  
Oldalelemek:  
- Részletes keresés gomb. A gombra kattintva lenyílik egy menü, ahol különböző szűkítéseket lehet megadni:	
- Típus
- Státusz
- Térkép 
A térképen az egyes ügyek típus ikonokként jelennek meg. 
Az ikonra kattintva egy új ablak ugrik fel, a következő felépítéssel:
- Ügy neve
- Ügy típusa 
- Ügy státusza
- Ügy borító képe. A képre kattintva átkerülünk az ügy adatlapjára.
- Jelmagyarázat
  A jelmagyarázat mobilon más arányt vesz fel, hogy olvasható maradjon, 
  tehát két külön kép van beállítva.
  
### 6. Statisztika
A statisztika oldal minden jogosultsági szintnek elérhető.  
A különböző jogosultsági szintek között nincsen eltérés. Mindenki ugyanazt látja.
Az adminisztrátori statisztikához lásd: 6. Monitoring fejezet.  

Oldalelemek:
- Bejelentések megoszlása státusz szerint oszlopdiagram
- Bejelentések megoszlása megye szerint oszlopdiagram
- További hasznos statisztikák lista
- Kényelmetlen fehérneműk száma a Parlamentben: 199
- Összes statisztika az oldalon: 11.5
- Főispánok száma Magyarországon: 19
- Összes bejelentés a honlapon: *A*
- Összes bolygó száma a Naprendszerben: 8
- Összes regisztrált felhasználó: *B*
- Magyarországon található települések száma: 3155
- Ételautomaták által évente megölt emberek száma átlagosan a világon: 10  
  Az A és B jelű elemek valós dinamikus változók, az összes többi pont statikus érték.


### 7. Regisztráció
# TODO


### 8. Bejelentkezés  
# TODO

### 9. Fiókbeállítások
A fiókbeállítás menüpontot csak a regisztrált felhasználó látja.  
Oldalelemek:  
- Felhasználónév  
- Email cím  
- Telefon szám  
- Létrehozva  
- Felhasználói szint  
- Adatok módosítása gomb  
A gombra kattintva megjelenik az adatmódosító felület.  
Az adatmódosító felületen a következő módosítások végezhetőek:  
  - Felhasználónév módosítása  
  - Email módosítása  
  - Telefonszám módosítása  

- Ügyeim listája gomb
A gombra kattintva két lista jelenik meg.
  - Általam bejelentve lista.  
  Ez minden olyan ügy, amit a felhasználó jelentett be.

  - Szervező vagyok lista.  
  Ez minden olyan ügy, ahol a felhasználó szervezőként lett hozzáadva az ügyhöz.


- Dokumentáció és egyéb anyagok link
- Github oldal link
- Monitorozó oldal link
- Adatkezelési szabályzat link

Admin  jogosultsági szint elér egy további oldal elemet:
- Összes ügy letöltése egy csv-ben. 
A gombra kattintva elkezdődik az összes ügy exportálása és letöltése CSV (“,”) formátumban. Windows alatt lehet hogy beolvasásakor be kell állítani, hogy UTF-8 karakterkészlettel értelmezze a szöveget. 
Windows alatt lehet hogy nem elég simán dupla klikkel megnyitni, hanem 
Adatok > Szövegből > UTF-8
A néni 1:12-től nagyon szépen elmagyarázza: https://www.youtube.com/watch?v=ZbljSnxoNLo
A csv a következő mezőket tartalmazza:
- ID
- Bejelentő email	
- Bejelentő telefon	
- Cím	
- Elnevezés	
- Hosszúsági fok	
- Kiemelt	Leírás	
- Létrehozva	
- Megoldás	
- Megoldási javaslat	
- Megye	
- Státusz	
- Státusz változás dátuma
- Státuszt változtató felhasználó	
- Szervező email	Szervező felhasználó	
- Szélességi fok	
- Típus	
- Város
Figyelem, ez a táblázat tartalmazza a bejelentő email címét és esetlegesen a telefonszámát is,
	vagyis a GDPR szerinti személyes adatokat! Regisztrálatlan és regisztrált (nem szervező, 
	nem koordinátor és nem admin) felhasználók számára ezek az adatok  a honlapon belül sehol nem
	jelennek meg.
	
### 10. Felhasználói adatok módosítása
A Felhasználói adatok módosítása oldalt a regisztrált felhasználó látja.  
A következő adatokat tudja módosítani a felhasználó:  
- Felhasználónév
- Email
- Telefonszám

### 11. Felhasználók
A Felhasználók oldalt az csak admin jogosultsági szint éri el.  
Oldalelemek:
- Email alapú keresési mező. A keresés nem közöl adatokat az adatbázis felé, végig a frontenden marad.
- Táblázat a következő adatokkal:
- Felhasználó
- Email
- Telefon
- Felhasználói szint
- Létrehozva
- Utoljára itt

A felhasználó nevére kattintva megjelenik a Felhasználó kezelése nevű oldal.  
A Felhasználó kezelése oldalt az csak admin jogosultsági szint éri el.  

Oldalelemek:
- Felhasználó név
- Jogosultsági szint legördülő menü. A kiválasztott jogosultsági szintet (registered / coordinator / admin)a Ment gombra kattintva lehet érvényesíteni.  
A jogosultsági szintnek nem kell átfutási idő, viszont egy kijelentkezés-bejelentkezés javasolt az új jogosultsági szinttel rendelkező felhasználó részéről.
- Email
- Telefon
- Felhasználó létrehozva
- Utolsó bejelentkezés
- Ment gomb

### 12. Ügy adatainak módosítása
Az ügy adatainak módosítását a szervező, a koordinátor és az admin jogosultsági szint éri el.

Oldalelemek:
- Státusz lenyíló menü  
  Ha a státuszt Megoldottra állítjuk, akkor megjelenik a Megoldás szabadszöveges mező. 
- Bejelentő email címe szabadszöveges mező
- Ügy megnevezése szabadszöveges mező
- Bejelentő telefonszáma szabadszöveges mező
- Ügy megnevezése szabadszöveges mező
- Ügy típusa lenyíló menü
- Ügy leírása szabadszöveges mező 
- Megoldási javaslat szabadszöveges mező
- Cím szabadszöveges mező
- Cím módosítása szabadszöveges mező
- Cím ellenőrzése gomb
- Csak az admin jogosoltságú felhasználónak elérhető oldalelem:
Kiemelt bejegyzés

### 13. Szervező hozzáadása
A rendező hozzáadása felület a koordinátor és az admin jogosultsági szinteknek elérhető.
Oldalelemek:
- Email alapú kereső
- Táblázat a következő elemekkel:
  - kijelöl (kipipálható doboz)
  - email 
  - felhasználó
  - telefon
  - Hozzáadom gomb
Egyszerre csak egy rendező adható hozzá egy bejelentéshez!

### 14. Easter Egg

01001110 11101001 01111010 01100100 00100000 01101101 01100101 01100111 00100000 01100001 01111010 00100000 01101111 01101100 01100100 01100001 01101100 01101111 01101110 00100000 00101111 01101011 01110101 01110100 01111001 01101001 00100000 01010101 01010010 01001100 00101101 01110100 00100001 
01000001 00100000 01101011 11101001 01110000 01100101 01101011 00100000 01100001 00100000 01101000 01110100 01110100 01110000 01110011 00111010 00101111 00101111 01100100 01101111 01100111 00101110 01100011 01100101 01101111 00101111 01100100 01101111 01100111 00101101 01100001 01110000 01101001 00101111 00100000 00101101 01110010 11110011 01101100 00100000 01101010 11110110 01101110 01101110 01100101 01101011 00101110 
<<<<<<< HEAD

=======
>>>>>>> 2ab5b14226d2f6f095e957ceef08293f14725419

### Szoftver architektúra
Az alábbi fejezetek tartalmazzák az alkalmazás techinkai leírását.  
A Rendkívüli Ügyek Minisztériuma specifikáció python Flask keretrendszerben lett implementálva.  
A flask adja a backend részt, míg a frontend HTML CSS és Javascript nyelven írt elemekből épül fel.  
A felhasznált python modulokat a requirements.txt tartalmazza.  
A Flask alkalmazások az MVT (Model View Template) architektúrát követik.  
![Flask MVT](flask_arch-640x296.png)
Ez egy kicsit más, mint az MVC (Model View Controller) architektúra. Mivel a Flask egy mikorkeretrendszer, ezért nem támogatja teljes egészében az MVC architektúra megvalósítását. Az MVT esetében a Controll részről a keretrendszer gondoskodik, amely HTTP requestre válaszként sablont (Template) küld.
A templatek a .\templates mappában találhatóak. 
A model, vagyis az adatbázis sémák definíciója a .\models.py fileban található. 
Az adatbázis a .\app.db nevű sqlite fileban található és az alkalmazás (app.py) első indításakor keletkezik a models.py definíciói alapján. 
A View részt az .\app.py kezeli 
A lekéréseket WSGI (PEP333) specifikáció szerint kezeli a middleware.
![Flask Nginx](flask_nginx.png)
A RÜM applikáció Gunicorn alkalmazás szervert használ, amely a következő feladatokért felel:
- Több alkalmazás instanciát futtat. (A RÜM esetében a Gunicorn 4 instanciát futtat)
Lásd Dockerfile: CMD ["-w=4", "-b", "0.0.0.0:5000", "app:app"]
- Ha leáll az alkalmazás, akkor automatikusan újraindítja az insanciát
- HTTP requesteket közvetít a webszerver és az alkalmazás között
- Terheléselosztást (load balancing) végez.
Dokumentáció: https://docs.gunicorn.org/en/stable/

