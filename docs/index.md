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
