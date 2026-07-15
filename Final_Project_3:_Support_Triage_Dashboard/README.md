# Support Triage Dashboard

Un tableau de bord de triage automatisé pour les tickets de support, utilisant FastAPI (asynchrone) et le SDK Google GenAI (Gemini) avec des sorties JSON structurées.

## Concurrence et Résilience
- **Sémaphore (`asyncio.Semaphore`) :** Limite les appels parallèles à l'API Gemini (8 par défaut) pour éviter de surcharger le service et d'obtenir des erreurs HTTP 429 (Rate Limit).
- **Retries (`tenacity`) :** Gère les échecs temporaires avec un backoff exponentiel (jusqu'à 3 tentatives).
- **Isolation des erreurs :** Si un ticket échoue définitivement, l'erreur est capturée dans l'objet `TicketResult`. Le traitement du lot continue sans être interrompu.

---

## Étapes pour lancer le projet

### 1. Préparer l'environnement
Créez et activez votre environnement virtuel Python :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate