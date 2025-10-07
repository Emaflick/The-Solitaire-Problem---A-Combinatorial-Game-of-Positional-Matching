#Test Combinazioni V3 (Risolto per n=1-7)

# ================================================================
# Test Combinazioni V3
# Ricerca stocastica con parallelismo per il gioco delle sequenze
#
# Descrizione:
# Questo programma simula il gioco delle "combinazioni" su un mazzo
# formato da più copie dei numeri 1..N.
# Ad ogni step viene verificata la condizione di presa: se la carta
# in posizione i ha valore i+1, viene rimossa, assegnando punti pari
# al suo valore. Dopo ogni presa può avvenire una rotazione parziale
# del mazzo. La partita termina quando il contatore di mancate (miss)
# supera la soglia fissata.
#
# Obiettivo:
# Trovare, tramite esplorazione stocastica, una sequenza iniziale di
# carte che massimizzi il punteggio finale. Il punteggio ottimale è
# teoricamente noto, ma difficilmente raggiungibile senza una ricerca
# intensiva.
#
# Metodo:
# - Genera molte permutazioni casuali del mazzo (restart).
# - Per ogni sequenza iniziale, applica hill-climbing con mosse locali
#   (swap e spostamento di blocchi) per migliorarla.
# - Ogni processo mantiene il miglior punteggio locale trovato e lo
#   comunica al master tramite una coda asincrona.
# - Se un processo raggiunge il punteggio target, segnala lo stop agli
#   altri tramite un evento condiviso (early-stop cooperativo).
#
# Parallelismo:
# La ricerca è distribuita su più processi per sfruttare tutti i core
# disponibili. I processi lavorano in parallelo su sottoinsiemi di
# restart, aumentando la probabilità di trovare l’ottimo in tempi brevi.
# Parametri configurabili:
# - MISS_SET   : soglia massima di mancate consecutive
# - TARGET     : punteggio obiettivo da raggiungere
# - MAX_STARTS : numero totale di restart da provare
# - HC_ITERS   : passi di hill-climbing per restart
# - SEED       : seme per la riproducibilità (None per random puro)
# - N_PROCS    : numero di processi paralleli
#
# Output:
# - Stampa i progressi ogni volta che viene trovato un nuovo best.
# - Stampa un messaggio di successo se viene raggiunto il TARGET.
# - Alla fine riporta la sequenza vincente e il punteggio ottenuto.
# ================================================================

import random
import multiprocessing as mp
from math import ceil

#REGOLE DELLA PARTITA

MISS_SET= 4

def riordina(arr, i):
    #Ruota l'array spostando i primi i elementi in coda.
    if i <= 0:
        return arr
    return arr[i:] + arr[:i]

def gioca(p):
    # p è una tupla; la rendo mutabile (posso sempre modificare la tupla durante un processo)
    arr = list(p)
    punt = 0
    i = 0
    miss = 0  # fallimenti consecutivi

    #Il gioco termina quando miss > i-1 (cioè arrivo a contare un numero superiore delle mie carte a disposizione)
    while arr and miss <= MISS_SET:
        if i >= len(arr):
            i = 0

        if arr[i] == i + 1:
            punt += (i + 1)
            del arr[i]
            miss = 0
            if i > 0 and arr:
                arr = riordina(arr, i)
            i = 0
        else:
            # Avanza l'indice di 1 posizione; se supera la lunghezza della lista, torna a 0 (scansione circolare).
            # Se invece l'array è vuoto, resetta semplicemente l'indice a 0 per sicurezza.
            i = (i + 1) % len(arr) if arr else 0
            miss += 1

    return punt #Alla fine della giocatà ritorno il punteggio ottenuto

# --- mazzo base ---
base = [1]*4 + [2]*4 + [3]*4 + [4]*4 + [5]*4 #costruzione del mazzo


# --- PARAMETRI DI RICERCA
TARGET = 58         # fermati appena lo trovi
MAX_STARTS = 250000     # restart totali da suddividere fra i processi
HC_ITERS = 7500      # passi di miglioramento locale per restart
SEED = None         # Seed casuale (Tengo None se lo randomizzo ad ogni ciclo - consigliato)
N_PROCS = max(1, mp.cpu_count() - 1)  # usa quasi tutti i core

if SEED is not None:
    random.seed(SEED) #Randomizza la sequenza in base al SEED

def random_perm(multiset):
    b = multiset[:]    # Copia il multiset originale (per non modificarlo).
    random.shuffle(b)  # Mescola l'ordine degli elementi con random.shuffle.
    return tuple(b)    # Restituisce il risultato come tupla (immutabile), utile da passare a gioca().


def swap_local(t):
    lst = list(t)                            # copia mutabile della tupla
    i, j = random.sample(range(len(lst)),2) #scegli due posizioni casuali diverse
    lst[i], lst[j] = lst[j], lst[i]          # scambia gli elementi
    return tuple(lst)                        # torna a tupla (immutabile)

def block_move_local(t):
    lst = list(t)                            # copia mutabile della tupla
    L = random.randint(2, 5)                 # lunghezza del blocco da spostare
    i = random.randint(0, len(lst) - L)      # posizione di inizio del blocco
    block = lst[i:i+L]                       # blocco estratto
    del lst[i:i+L]                           # rimuove il blocco dalla lista
    j = random.randint(0, len(lst))          # nuova posizione di inserimento
    lst[j:j] = block                         # reinserisce il blocco
    return tuple(lst)                        # torna a tupla (immutabile)

def hill_climb(start, iters=HC_ITERS, target=TARGET):
    best = start                    # sequenza corrente migliore
    best_score = gioca(best)        # punteggio della sequenza iniziale
    if best_score >= target:        # se già ottimale, esci subito
        return best, best_score

    # Ciclo principale: prova per 'iters' volte a migliorare la sequenza
    for _ in range(iters):
        # Genera una nuova sequenza candidata a partire dalla migliore attuale:
        # - con probabilità 50% fa uno swap di due carte,
        # - con probabilità 50% sposta un piccolo blocco di carte.
        cand = swap_local(best) if random.random() < 0.7 else block_move_local(best)
        # Calcola il punteggio della sequenza candidata
        sc = gioca(cand)
        # Se il punteggio è migliore o uguale a quello corrente, aggiorna la soluzione
        if sc >= best_score:
            best, best_score = cand, sc
            # Se abbiamo già raggiunto il punteggio target, interrompi subito la ricerca
            if best_score >= target:
                break
    # Al termine restituisci la miglior sequenza trovata e il suo punteggio
    return best, best_score


# ==========================
# PARALLELISMO
# ==========================

def worker_search(per_proc_starts, target, seed, ret_queue, stop_event):
    # Inizializza il generatore casuale del *processo*:
    # - se 'seed' è fornito, rende la run ripetibile (deterministica per quel processo)
    # - se 'seed' è None, usa entropia di sistema (run non deterministica)
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()
    # Miglior risultato trovato da *questo* processo (score e sequenza corrispondente).
    # Partiamo da per indicare che non abbiamo un risultato
    local_best_sc = -1
    local_best_seq = None

    # La funzione worker_search rappresenta l’unità operativa eseguita in parallelo dai diversi processi.
    # Ciascun processo esegue un certo numero di restart (per_proc_starts), cercando di migliorare le sequenze
    # e comunicando i risultati al processo principale tramite una coda condivisa (ret_queue).
    # Se uno dei processi raggiunge il punteggio obiettivo (target), invia un segnale agli altri attraverso
    # l’evento condiviso (stop_event), permettendo così di interrompere il lavoro rimanente ed evitare calcoli inutili.
    # Per massimizzare l’efficacia della ricerca, ogni processo può ricevere un seme casuale differente,
    # in modo da esplorare traiettorie diverse e non ripetere le stesse sequenze.
    # Quando un processo individua un punteggio migliore rispetto a quelli trovati finora,
    # invia il risultato al processo principale usando ret_queue.put(("best", score, seq)),
    # consentendo al master di monitorare i progressi della ricerca in tempo reale.
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

    for _ in range(per_proc_starts):
        # Se un altro processo ha già segnalato il successo (TARGET trovato),
        # interrompi subito questo worker per non sprecare tempo.
        if stop_event.is_set():
            break

        # Genera una permutazione casuale del mazzo di base (restart)
        p0 = random_perm(base)

        # Prova a migliorare localmente la sequenza (hill climbing) e valuta il punteggio
        cand, sc = hill_climb(p0, iters=HC_ITERS, target=target)

        # Se questo worker ha trovato un risultato migliore del suo best locale,
        # aggiornalo e notifica il processo principale (per logging/progressi)
        if sc > local_best_sc:
            local_best_sc, local_best_seq = sc, cand
            # Messaggio asíncrono: informa il master di un nuovo "best" locale
            ret_queue.put(("best", sc, cand))

        # Early-stop globale: se abbiamo raggiunto il TARGET,
        # invia messaggio di successo, attiva lo stop-event e termina
        if sc >= target:
            ret_queue.put(("done", sc, cand))
            stop_event.set()
            break
# Ogni iterazione esegue un restart indipendente:
# - Se un altro processo ha già trovato il target, interrompi subito.
# - Genera una sequenza casuale e migliorarla con hill_climb.
# - Se ottieni un punteggio migliore del best locale, aggiorna e notifica al master ("best").
# - Se raggiungi il target, invia messaggio "done", attiva lo stop_event e termina
#   così tutti i processi si fermano (stop cooperativo).
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

def parallel_search():
    # Crea oggetti condivisi fra processi:
    # - Manager: gestisce risorse condivise
    # - ret_queue: coda per messaggi asincroni dai worker ("best", "done")
    # - stop_event: evento per fermare cooperativamente tutti i worker
    manager = mp.Manager()
    ret_queue = manager.Queue()
    stop_event = manager.Event()

    # Quanti restart assegnare a ciascun processo (ripartizione quasi uniforme)
    per_proc = ceil(MAX_STARTS / N_PROCS)

    # Avvio dei processi worker
    procs = []
    for r in range(N_PROCS):
        # Seed per-processo:
        # - se SEED è fisso, sfaso i semi per avere run ripetibili ma diverse tra processi
        # - se SEED è None, ogni processo usa entropia di sistema
        seed_r = None if SEED is None else (SEED + r + 1)
        p = mp.Process(
            target=worker_search,
            args=(per_proc, TARGET, seed_r, ret_queue, stop_event)
        )
        p.start()
        procs.append(p)

    # Best globale accumulato dal master (solo per reporting/ritorno finale)
    best_sc = -1
    best_seq = None

    # Loop di ascolto: finché almeno un processo è vivo, leggi aggiornamenti dalla coda
    while any(p.is_alive() for p in procs):
        try:
            # Timeout breve per restare reattivi anche se non arrivano messaggi
            msg, sc, seq = ret_queue.get(timeout=0.5)

            if msg == "best" and sc > best_sc:
                # Nuovo best globale segnalato da un worker
                best_sc, best_seq = sc, seq
                print(f"[Aggiornamento:] nuovo best globale: {best_sc}/{TARGET}")

            elif msg == "done":
                # Un worker ha raggiunto il TARGET: registra risultato, segnala stop e esci
                best_sc, best_seq = sc, seq
                print(f"[SUCCESSO!] raggiunto target {TARGET}")
                stop_event.set()
                break

        except Exception:
            # Timeout della queue: nessun messaggio, continua a monitorare i processi
            pass

    # Assicurati che tutti i processi terminino correttamente
    for p in procs:
        p.join(timeout=1.0)

    # Ritorna la miglior sequenza e il relativo punteggio (TARGET o best parziale)
    return best_seq, best_sc

# La funzione parallel_search gestisce la ricerca in parallelo coordinando più processi indipendenti.
# Funziona così:
# 1. Inizializza tre primitive di sincronizzazione:
#    - Manager: permette di creare strutture condivise tra processi.
#    - Queue (ret_queue): coda per ricevere dai worker messaggi asincroni ("best" per progressi, "done" per successo).
#    - Event (stop_event): flag condiviso che, quando impostato, segnala a tutti i worker di fermarsi.
# 2. Divide il numero totale di restart (MAX_STARTS) in blocchi quasi uguali (per_proc) per ogni processo.
# 3. Avvia i processi worker, ciascuno con il proprio seme (seed) per esplorazioni diverse ma ripetibili.
# 4. Il processo principale ascolta la coda:
#    - Se riceve un messaggio "best", aggiorna il best globale e stampa i progressi.
#    - Se riceve "done", significa che un worker ha trovato il TARGET: registra il risultato,
#      attiva lo stop_event per fermare gli altri e interrompe il ciclo.
# 5. Attende la terminazione di tutti i processi (join) per garantire che non restino risorse aperte.
# 6. Infine restituisce la miglior sequenza trovata (best_seq) e il relativo punteggio (best_score).
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    seq, sc = parallel_search()

    print("\n== RISULTATO ==")
    print("Sequenza Vincente:", seq)
    print("Punteggio:", sc)
