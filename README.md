In occasione delle elezioni regionali in Emilia Romagna ed Umbria del 17 e 18 novembre 2024, ho utilizzato Claude.ai per realizzare uno script che permettesse di estrarre i dati relativi ai risultati elettorali.
In questo repository si trovano gli script realizzati dall'intelligenza artificiale (ScrapeUmbria.py, ScrapeER.py e Rimini.py).
Lo script dedicato alla provincia di Rimini è stato necessario perché in un primo momento avevamo indicato in maniera non corretta il codice elettorale dei comuni della provincia di Rimini.
Gli script funzionano infatti costruendo le url da interrogare a partire dai codici elettorali dei singoli comuni, che ho inserito in questo repositori (Codici ER.csv e Codici Umbria.csv).
I tre restanti .csv contengono i dati estratti dall'AI.
Per far funzionare gli script è necessario scaricare sul proprio computer anche i file contenenti i codici elettorali e correggere il percorso per raggiungere questo file nello script, indicando quello relativo al proprio computer.
Questi dati sono stati utilizzati per un articolo uscito su InfoData, il data blog del Sole24Ore, raggiungibile a questo link:
https://www.infodata.ilsole24ore.com/2024/11/19/elezioni-regionali-umbria-emilia-romagna-abbiamo-aggiustato-il-codice-ora-i-dati-si-estraggono-grazie-intelligenza-artificiale
