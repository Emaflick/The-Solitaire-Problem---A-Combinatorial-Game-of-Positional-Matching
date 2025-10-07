# Test Combinazioni V2 (Risolto per n=1-6)
#
# Ricerca stocastica con hill-climbing per trovare una sequenza (multiset 1..6 con 4 copie ciascuno)
# che massimizzi il punteggio del gioco. Struttura:
# - gioca(): valuta una sequenza (simulazione del gioco)
# - mosse locali (swap, block-move): piccole modifiche della sequenza
# - hill_climb(): prova molte mosse locali e tiene i miglioramenti
# - ciclo di restart: riparte da molte permutazioni casuali finché raggiunge TARGET

import random

def riordina(arr, i):
    """Ruota l'array spostando i primi i elementi in coda."""
    # Se i <= 0 non serve ruotare (già allineato)
    if i <= 0:
        return arr
    # Sposta il prefisso arr[:i] in fondo e porta in testa arr[i:]
    return arr[i:] + arr[:i]

def gioca(p):
    # Valutatore del punteggio: data una sequenza p (tupla), simula la partita.
    # Converte la tupla in lista (mutabile) perché usiamo 'del' e riordini.
    arr = list(p)
    punt = 0          # punteggio accumulato
    i = 0             # indice logico corrente
    miss = 0          # conteggio di fallimenti consecutivi (nessuna presa)

    # Continua finché ci sono carte e non superi 5 mancate di fila (miss <= 5)
    while arr and miss <= 5:
        # Wrap-around dell'indice se oltre la fine
        if i >= len(arr):
            i = 0

        # Condizione di presa: il valore della carta deve eguagliare i+1
        if arr[i] == i + 1:
            punt += (i + 1)   # aggiungi il valore (i+1) al punteggio
            del arr[i]        # rimuovi la carta
            miss = 0          # resetta i fallimenti
            # Se hai preso a indice > 0, applica la rotazione come da regola
            if i > 0 and arr:
                arr = riordina(arr, i)
            # Dopo una presa si riparte sempre dall'inizio (i=0)
            i = 0
        else:
            # Avanza di una posizione in modalità circolare
            i = (i + 1) % len(arr) if arr else 0
            miss += 1         # incrementa il contatore di mancate

    # Ritorna il punteggio totale conseguito con questa sequenza
    return punt

# --- mazzo base ---
# Multiset con 4 copie di ciascun numero da 1 a 6 (totale 24 carte)
base = [1]*4 + [2]*4 + [3]*4 + [4]*4 + [5]*4 + [6]*4

# --- PARAMETRI DELLA RICERCA (puoi regolarli) ---
TARGET = 82        # Punteggio obiettivo: se raggiunto, interrompi la ricerca
MAX_STARTS = 15000 # Numero di restart casuali (nuove permutazioni iniziali)
HC_ITERS = 800     # Numero di passi di miglioramento locale per ogni restart
SEED = 129546      # Seed per avere run ripetibili (metti None per casualità pura)

# Inizializzazione del generatore casuale (riproducibilità opzionale)
if SEED is not None:
    random.seed(SEED)

def random_perm(multiset):
    # Crea una permutazione casuale del multiset:
    # - copia per non alterare l'originale
    # - shuffle in place
    # - ritorna tupla (immutabile) comoda da passare a gioca()
    b = multiset[:]
    random.shuffle(b)
    return tuple(b)

def swap_local(t):
    # Mossa locale: scambia due posizioni scelte a caso
    lst = list(t)
    i, j = random.sample(range(len(lst)), 2)
    lst[i], lst[j] = lst[j], lst[i]
    return tuple(lst)

def block_move_local(t):
    # Mossa locale: sposta un piccolo blocco contiguo (lunghezza 2..4) in un'altra posizione
    lst = list(t)
    L = random.randint(2, 4)           # dimensione del blocco da muovere
    i = random.randint(0, len(lst) - L)
    block = lst[i:i+L]                  # estrai blocco
    del lst[i:i+L]                      # rimuovi blocco dalla posizione originale
    j = random.randint(0, len(lst))     # nuova posizione di inserimento
    lst[j:j] = block                    # inserisci il blocco
    return tuple(lst)

def hill_climb(start, iters=HC_ITERS, target=TARGET):
    # Algoritmo di miglioramento locale:
    # - parte da 'start'
    # - prova 'iters' mosse locali
    # - tiene solo le mosse che non peggiorano (>=) il punteggio
    best = start
    best_score = gioca(best)
    # Early-exit: se già al target non serve cercare oltre
    if best_score >= target:
        return best, best_score

    for _ in range(iters):
        # 50%: swap di due carte | 50%: sposta un blocco contiguo
        cand = swap_local(best) if random.random() < 0.5 else block_move_local(best)
        sc = gioca(cand)
        # Accetta la mossa se non peggiora il punteggio corrente
        if sc >= best_score:
            best, best_score = cand, sc
            # Early-stop: raggiunto il target, esci
            if best_score >= target:
                break
    # Restituisce la miglior sequenza trovata e il relativo punteggio
    return best, best_score

# --- Ricerca: multi-start + hill-climbing + early-stop ---
miglior_seq = None   # migliore sequenza trovata globalmente
punteggio = -1       # punteggio globale migliore (sentinella iniziale)

for start_idx in range(1, MAX_STARTS + 1):
    # Genera una permutazione iniziale del mazzo (restart)
    p0 = random_perm(base)
    # Migliora localmente la sequenza di partenza
    cand, sc = hill_climb(p0, iters=HC_ITERS, target=TARGET)

    # Aggiorna best globale se trovi un punteggio superiore
    if sc > punteggio:
        punteggio = sc
        miglior_seq = cand
        print(f"[{start_idx}] nuovo best: {punteggio}")

    # Early-stop globale: raggiunto TARGET, interrompi i restart
    if punteggio >= TARGET:
        print(f"Raggiunto target {TARGET} allo start #{start_idx}.")
        break

# Report finale: sequenza e punteggio migliori trovati
print("Sequenza vincente:", miglior_seq, "  Punteggio:", punteggio)
