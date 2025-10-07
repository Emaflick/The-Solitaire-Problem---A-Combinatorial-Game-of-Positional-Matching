#Test Combinazioni V1 (Risolto per n=1-4)

from more_itertools import distinct_permutations

def riordina(arr, i):
    """Ruota l'array spostando i primi i elementi in coda."""
    # i è l'indice appena 'usato'; dopo la delete, ruotiamo per riportare
    # l'inizio dell'array subito dopo la posizione i
    if i <= 0:
        return arr
    return arr[i:] + arr[:i]

def gioca(p):
    # p è una tupla (da distinct_permutations); la rendo mutabile
    arr = list(p)
    punt = 0
    i = 0
    miss = 0  # fallimenti consecutivi (il tuo "limit")

    while arr and miss <= 4:
        # se l'indice supera la lunghezza, fai wrap
        if i >= len(arr):
            i = 0

        if arr[i] == i + 1:
            punt += (i + 1)
            del arr[i]
            miss = 0
            # ruota l'array come da tua idea originale (solo se i>0)
            if i > 0 and arr:
                arr = riordina(arr, i)
            # dopo la rotazione, riparti dall'inizio
            i = 0
        else:
            # nessun match: vai avanti e conta il fallimento
            i = (i + 1) % len(arr) if arr else 0
            miss += 1

    return punt

# --- ricerca della sequenza migliore ---
base = [1]*4 + [2]*4 + [3]*4 + [4]*4 + [5]*4
miglior_seq = None
punteggio = -1

for p in distinct_permutations(base):
    try_punt = gioca(p)
    if try_punt > punteggio:
        punteggio = try_punt
        miglior_seq = p  # salvo la tupla 'p' (immutabile, comoda da stampare)
    if try_punt==58:
        punteggio=try_punt
        miglior_seq=p
        break

print("Sequenza vincente:", miglior_seq, "  Punteggio:", punteggio)
