# Self-Counting Solitaire 🔢🃏  
*A combinatorial exploration of deterministic elimination dynamics*

### Author  
**Emanuele Renzoni**  
Politecnico di Milano — Mathematical Engineering  
October 2025  

---

## 🧩 Overview  

The **Self-Counting Solitaire** is a combinatorial and algorithmic study inspired by a simple card game played with repeated values.  
At each round, the player counts cards from the top of the deck and removes the first one whose **value equals its position index**.  
After each removal, the preceding block is cyclically moved to the bottom, and the process continues until no valid match is found.

This project investigates the mathematical structure behind this rule, defines a formal model, and implements several algorithmic strategies to approximate or achieve the optimal sequence of eliminations.

The central question:  
> *Given a deck of N distinct values (each repeated four times), what is the maximum total score achievable under this deterministic rule?*

---

## 🧮 Mathematical Definition  

For an integer \( N \geq 1 \), define the multiset  

\[
M = \{ 1^4, 2^4, \dots, N^4 \}
\]

Each initial configuration \( A \in \Omega \) is a permutation of \( M \).  
During the game, the player removes the first card \( q_j \) such that \( q_j = j \).  
Each successful elimination awards a score equal to \( j \), and the sequence continues with the deck cyclically rotated.

The total score for a configuration \( A \) is

\[
F(A) = \sum_{i=1}^{T(A)} k_i,
\]

where \( k_i \) is the position of the match at round \( i \).

The optimization problem is

\[
\max_{A \in \Omega} F(A)
\]

with theoretical upper bound  

\[
B(N) = 4 \sum_{i=1}^N i = 2N(N + 1)
\]

---

## 🚫 The Five-Card Impossibility  

A fundamental result of the study is the **Five-Card Barrier Theorem**:

> It is impossible to completely resolve any configuration containing exactly five cards.

Since each value appears at most four times, no configuration of length five can reach a terminal state with all cards removed.  
This establishes an intrinsic limit in the dynamics of the game and explains why the process can never fully “win” the deck.

---

## 🧠 Algorithmic Development  

The project evolved through **three main algorithmic versions**, each improving scalability and performance.

### 🔹 Version 1 – Exhaustive Enumeration  
- Explores all distinct permutations up to \( N = 4 \).  
- Uses deterministic simulation of the counting rule.  
- Confirms the **two-point gap**: \( F_{\max}(N) = B(N) - 2 \).

### 🔹 Version 2 – Stochastic Hill Climbing  
- Introduces random restarts and local swaps (2–4 elements).  
- Explores the configuration space probabilistically.  
- Reproduces the two-point gap for \( N = 5, 6 \).  

### 🔹 Version 3 – Parallelized Search (Multiprocessing)  
- Fully distributed implementation using Python’s `multiprocessing`.  
- Each CPU core performs an independent stochastic search.  
- Cooperative early-stop and asynchronous queues.  
- Successfully optimizes up to \( N = 7 \) with near-linear scaling.

---

## 📊 Empirical Observation  

All tested cases (up to \( N = 7 \)) exhibit a **consistent structural deficit**:

\[
F_{\max}(N) = B(N) - 2
\]

This two-point gap appears invariant with respect to deck size — suggesting an inherent property of the counting process rather than a computational artifact.

---

## 🧩 Current Conjecture  

> **Conjecture (Global Existence):**  
> For every integer \( N \geq 2 \), there exists at least one initial configuration  
> \( A(N) \) such that the process terminates with the single-card state  
> \( Q_{\text{final}} = (2) \).

A constructive *backward synthesis algorithm* is provided, based on safe inverse steps ensuring non-coincidence in suffixes.  
While the method is conditionally correct, a general *availability lemma* guaranteeing global existence remains open.

---

## ⚙️ Implementation  

All Python implementations — from **V1 (deterministic enumeration)** to **V3 (parallel stochastic optimization)** — are included in the repository:

- `test_combinazioni_v1.py`  
- `test_combinazioni_v2.py`  
- `test_combinazioni_v3.py`  
- `inverse_method_sequence_builder.py`

Each file includes clear logging, parameter tuning, and early-stop heuristics for reproducibility.

---

## 🧭 Future Work  

- Formal proof of the *global existence conjecture* for all \( N \).  
- Analytical derivation of the two-point deficit.  
- Extension to larger decks (e.g., \( N = 10 \), the Italian 40-card deck).  
- Development of heuristic sequence generators and visual analyzers.

---

## 🧠 Broader Relevance  

Though born as a mathematical curiosity, the *Self-Counting Solitaire* connects to topics in:
- **Combinatorics & Discrete Dynamics**
- **Permutation Structures and Derangements**
- **Optimization and Heuristic Search**
- **Parallel Computation**
- **Algorithmic Proof Construction**

Its backward-synthesis logic mirrors real-world processes such as cyclic scheduling, cache rotation, and pipeline optimization — demonstrating how playful problems can yield rigorous mathematical and computational insights.

---

## 📎 Reference  

Full formal write-up (PDF):  
**[Solitaire_Problem.pdf](./Solitaire_Problem.pdf)**

---

> *“A problem posed in jest became a serious object of inquiry.”*  
> — *Emanuele Renzoni, 2025*
