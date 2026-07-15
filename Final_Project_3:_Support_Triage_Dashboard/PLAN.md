# PLAN : Support Triage Dashboard

## 1. Architecture Globale
Le projet s'appuie sur une API REST asynchrone (FastAPI) couplée au SDK Google GenAI moderne (`google-genai`). Le frontend est un tableau de bord en Single Page Application (HTML/Tailwind/VanillaJS) utilisant un polling à 1 seconde pour mettre à jour l'état du traitement en temps réel.

## 2. Modèle de Concurrence & Résilience
* **Sémaphore (`asyncio.Semaphore`) :** Fixé par la variable d'environnement `CONCURRENCY_LIMIT` (8 par défaut). Garantit que le backend ne lance pas plus de 8 requêtes IA en parallèle pour protéger les quotas de l'API.
* **Retries (`tenacity`) :** Utilisation d'un backoff exponentiel (jusqu'à 3 tentatives) pour absorber les micro-coupures réseau ou erreurs de surcharge (HTTP 429/503).
* **Isolation des pannes :** Si un ticket échoue définitivement après les 3 retries (ex: texte illisible, blocage de sécurité IA), l'erreur est interceptée et logguée dans un champ `error` dédié au sein du modèle `TicketResult`. Le traitement globale (`asyncio.as_completed`) n'est jamais interrompu : le lot se terminera toujours à 100%.

## 3. Sécurité (Prompt Injection)
Les corps de texte des tickets sont encapsulés au sein de balises de délimitation `<ticket_body>...</ticket_body>`. L'instruction système force le modèle LLM à ne traiter cette zone *que* comme de la donnée brute à analyser, l'empêchant de se faire hijacker par des commandes malveillantes dissimulées dans un ticket client.