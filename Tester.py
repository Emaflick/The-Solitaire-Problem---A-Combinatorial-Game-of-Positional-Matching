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
base = [8, 6, 4, 10, 5, 9, 4, 6, 10, 4, 3, 7, 3, 8, 3, 4, 1, 1, 1, 2, 7, 10, 7, 9, 9, 7, 10, 6, 5, 3, 5, 6, 8, 5, 2, 9, 2, 1, 2, 8]
punteggio = -1
punteggio=gioca(base)


print("Sequenza:", base, "  Punteggio:", punteggio)
