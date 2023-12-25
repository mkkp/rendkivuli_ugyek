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
•	Probléma megnevezése (szabad szöveges mező)  
•	Típus (legördülő menü)  
Szemét  
Közmű  
Út és Járda  
Akadálymentesítés  
Növény  
Állat  
Épület  
Közlekedés  
Tájékoztatás  
Műemlék  
•	Részletes leírás (szabad szöveges mező)    
•	Képek feltöltése (file dialógus menü)    
Ha a felhasználó kiválasztja a képeket, megjelenik még egy opcionálisan használatba vehető  file feltöltési mező, ahol a felhasználó további képeket adhat a bejelentéshez.
•	Email cím (szabad szöveges mező)  
•	Adatkezelési szabályzat elfogadása (bepipálható mező)  
•	Cím (szabad szöveges mező)  
  
Opcionális mezők:  
•	Megoldási javaslat (szabad szöveges mező)  
•	Telefon (szabad szöveges mező)  
A bejelentés oldalon a felhasználó képeket is tud feltölteni. A képek összmérete nincsen maximálva.  
A helyszín megadásánál a felhasználó egy gomb segítségével le tudja ellenőrizni / kiegészíteni az általa begépelt helyszín címet.  
A cím megadását egy térkép segíti, amire ha a felhasználó rákattint, akkor a cím automatikusan kitöltődik.  

Mobilon a cím megadását a helyhozzáférés segíti.   
Ha a felhasználó készülékén a helymeghatározás be van kapcsolva, akkor helyszín adatok automatikusan kitöltésre kerülnek.  
Ha a felhasználó készülékén a helymeghatározás ki van kapcsolva, akkor a következő üzenetet kapja:  
“Ajjaj... A helyhozzáférés nincsen engedélyezve. Ha szeretnéd, hogy robokutyi töltse ki helyetted a címet, akkor kérlek engedélyezd.”  
Ha a felhasználó ekkor engedélyezi a helyhozzáférést és frissíti az oldalt, akkor helyszín adatok automatikusan kitöltésre kerülnek.  
A térképen található egy kereső mező, amit szintén lehet használni a cím megadásakor.  
A térképen szerepelnek navigációs ikonok.  
A térképet ki lehet nagyítani teljes méretűre.  
A Bejelent gombra kattintva, a kötelező mezőkre lefut egy űrlap ellenőrzés. 
Ha egy kötelező mező kitöltetlenül maradt, akkor a következő hibaüzenetek válnak láthatóvá az űrlapon, aszerint hogy melyik mezőt nem töltötték ki:  
•	Probléma megnevezése: Ha nem tudod megnevezni, akkor az nem probléma.  
•	Típus: Tök széles a választék, bökj rá egyre!  
•	Részletes leírás: Nem baj, ha nem töltöd ki. Tényleg. Csináld csak! Semmi baj. Nem haragszunk. Azt csinálsz, amit akarsz.  
•	Képek feltöltése: Ellopták a képfájlt. Próbáld újra!  
•	Email cím: A PIN-kódod jól jönne, de inkább írd be ide a mailed.  
•	Adatkezelési szabályzat elfogadása: Haladjunk, kérem, haladjunk.  
•	Cím: Sajnos pontosan meg kell mondanod, hogy hol van mi, merre, miként.  
A program a háttérben végez egy email ellenőrzést, és megszakítja a bejelentést ha:  
szintaktikailag hibás az email cím pl nincs benne @ karakter (Hibaüzenet: A Kutya mindenit de fura ez az email cím!)  
a cím mezőben “http” karakterláncot talál.  
nem engedélyezett file formátumokat talál (engedélyezett: png, jpeg)  
Ha az űrlap ellenőrzés nem talál kitöltetlen kötelező mezőt, akkor elkezdi az adatok és képek feltöltését az adatbázisba.   
Töltés közben egy gif és egy felirat (Türelem, már dolgozunk rajta!) tájékoztatja a felhasználót arról, hogy a rendszer munkát végez.  
Ha sikeres a bejelentés, rendszerüzenetet kap a felhasználó:   
Gratulálunk, sikeres bejelentés. Küldtünk levelet is.  
Ha sikeres a feltöltés, a felhasználó által megadott email címre level megy:   
Szia!  
Köszi, hogy jelezted nekünk az alábbi problémát: valami4642  
4000 mérnökünk és 3600 menyétünk elkezdett dolgozni rajta.    
Hamarosan megoldjuk, vagy nem.  
Keresünk majd, amint kitaláltuk, hogy mit csináljunk a dologgal.  
Addig is itt tudod nyomonkövetni, hogyan állunk vele: https://rendkivuliugyek.com/single_submission/1  
Rendkívüli Ügyek Minisztériuma  
Ha sikeres a feltöltés, a bejelentés oldal az ügy adatlapjára továbbítja a bejelentő böngészőjét.  

