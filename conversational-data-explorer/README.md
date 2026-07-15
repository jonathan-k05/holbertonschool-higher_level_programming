# Conversational Data Explorer

Chat avec votre base de données en langage naturel. L'app génère du SQL
via un LLM, mais **ne l'exécute jamais aveuglément** : chaque requête
proposée passe par `guardrails.py` avant de toucher la base.

## Modèle de sécurité (le cœur du projet)

Une question ne peut jamais entraîner qu'**une seule requête SELECT en
lecture seule**. Concrètement, `backend/guardrails.py` :

1. retire les commentaires SQL (`--`, `/* */`) avant toute analyse, pour
   qu'une écriture cachée dans un commentaire soit neutralisée et non
   exécutée ;
2. refuse tout ce qui contient plus d'une instruction (`;` au milieu) ;
3. exige que la requête commence par `SELECT` (bloque aussi
   `WITH ... AS (...)`, volontairement, pour éliminer les CTE qui
   cachent une écriture) ;
4. refuse toute requête contenant `INSERT`, `UPDATE`, `DELETE`, `DROP`,
   `ALTER`, `TRUNCATE`, `PRAGMA`, etc., même en sous-clause ;
5. ajoute automatiquement un `LIMIT` (200 par défaut, 1000 maximum).

Ces règles s'appliquent **quoi que dise la question ou le modèle** — la
question de l'utilisateur est traitée comme une donnée, jamais comme une
instruction système. Voir `backend/tests/test_guardrails.py` pour les cas
adversariaux couverts (`delete all users`, `DROP TABLE`, requêtes
empilées, écriture cachée dans un commentaire ou un CTE, etc.) — tous
bloqués.

## Structure

```
conversational-data-explorer/
├── backend/
│   ├── main.py           # API FastAPI
│   ├── db.py              # modèles, seed, introspection du schéma
│   ├── nl2sql.py           # question -> SQL, résultats -> réponse
│   ├── guardrails.py       # les vérifications de sécurité
│   ├── ai.py               # appel au modèle Gemini
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│       └── test_guardrails.py
├── frontend/
│   └── index.html
├── .gitignore
├── PLAN.md
└── README.md
```

## Lancer le projet

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # puis renseigner GEMINI_API_KEY
uvicorn main:app --reload
```

Le backend écoute sur `http://localhost:8000`. La base SQLite
(`data.db`) est créée et peuplée automatiquement au premier démarrage.

Ouvrez ensuite `frontend/index.html` dans un navigateur (double-clic
suffit, ou servez-le avec `python -m http.server` depuis `frontend/`
pour éviter certaines restrictions de navigateur).

## Obtenir une clé Gemini

Une clé gratuite est disponible sur
[Google AI Studio](https://aistudio.google.com/). Collez-la dans
`backend/.env` sous `GEMINI_API_KEY`.

## Tests

```bash
cd backend
pytest tests/ -v
```

Les 16 tests couvrent à la fois les cas qui doivent être bloqués
(injections, requêtes empilées, écritures) et les cas qui doivent
passer (SELECT simples, LIMIT ajouté/plafonné automatiquement).

## Endpoints

| Méthode | Route      | Description                                  |
|---------|------------|-----------------------------------------------|
| GET     | `/health`  | vérifie que l'API répond                      |
| GET     | `/schema`  | schéma introspecté en direct                  |
| POST    | `/ask`     | question → SQL sécurisé → réponse             |
| GET     | `/history` | historique de la session                      |
| POST    | `/seed`    | réinitialise la base avec des données d'exemple |

### Exemple `POST /ask`

```json
// requête
{ "question": "Combien de commandes par région ?" }

// réponse
{
  "question": "Combien de commandes par région ?",
  "answer": "La région Nord compte le plus de commandes, suivie de l'Est.",
  "sql": "SELECT region, COUNT(*) as n FROM customers GROUP BY region LIMIT 200",
  "columns": ["region", "n"],
  "rows": [{"region": "North", "n": 11}, ...],
  "row_count": 4,
  "is_read_only": true,
  "timestamp": "2026-07-15T20:53:43.445062"
}
```

## Base de données d'exemple

Trois tables liées, peuplées automatiquement au démarrage si vides :

- `customers` (id, name, region, signup_date)
- `orders` (id, customer_id, order_date, status, amount)
- `payments` (id, order_id, due_date, payment_date, amount, paid)

Questions d'exemple à essayer :

- "Combien de commandes par région ?"
- "Quels clients ont des paiements en retard ?"
- "Quel est le montant total des commandes fermées ?"
- "Top 5 des clients par montant total dépensé"

## Sécurité — checklist

- `.env` est ignoré par git (`.gitignore`), `.env.example` est commité.
- Accès à la base uniquement via SQLAlchemy (ORM / requêtes
  paramétrées) — jamais de concaténation de chaînes SQL.
- Guardrails en lecture seule prouvés par tests automatisés.
- La question de l'utilisateur est toujours traitée comme une donnée,
  jamais comme une instruction (protection contre le prompt injection).
