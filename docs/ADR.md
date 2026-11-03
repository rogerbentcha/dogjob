# Décisions d'architecture (ADR)

## ADR-001 : REST comme cœur, MCP en façade, un seul processus
**Statut** : accepté · **Date** : 2026-11-02

**Contexte** : Dogjob doit être utilisable par une API REST et par un assistant IA via MCP, sans que les deux divergent.

**Options**
1. Deux services indépendants (API et serveur MCP), chacun avec sa logique.
2. Un serveur MCP seul, sans REST.
3. Une couche de services partagée, avec deux façades minces (REST et MCP) dans un même processus FastAPI.

**Décision** : option 3. Routes et outils MCP ne contiennent que validation d'entrée et formatage de sortie. Le MCP est exposé en *streamable HTTP* sur `/mcp`.

**Conséquences**
- (+) Une règle métier existe à un seul endroit ; une seule authentification et un seul déploiement.
- (+) L'API REST sert aussi aux tests, aux scripts et à une future interface web.
- (−) Le montage du MCP dans FastAPI (cycle de vie) est à valider par un prototype.
- (−) Un bug du processus affecte les deux interfaces.

---

## ADR-002 : l'extraction des offres se fait côté assistant, pas côté serveur
**Statut** : accepté

**Contexte** : tu captures une offre à partir d'un lien ou d'une capture d'écran.

**Options**
1. Le serveur télécharge la page (scraping) ou lit l'image (OCR).
2. L'assistant IA lit le lien ou l'image et appelle `capturer_offre` avec des champs structurés.

**Décision** : option 2.

**Conséquences**
- (+) Aucun scraping ni OCR à maintenir. Les sites d'offres bloquent souvent les robots et changent de structure.
- (+) Le serveur reste simple, déterministe et testable.
- (−) La qualité de l'extraction dépend de l'assistant. Le serveur doit donc valider ses entrées et renvoyer des erreurs claires.
- (−) L'outil ne marche pas sans client IA ; l'API REST reste la solution de repli manuelle.

---

## ADR-003 : une seule entité `Candidature` (offre = candidature)
**Statut** : accepté

**Contexte** : on pourrait modéliser séparément « offre repérée » et « candidature déposée ».

**Options**
1. Deux entités `Offre` et `Candidature`.
2. Une seule entité `Candidature`, avec le statut `À postuler` pour une offre repérée.

**Décision** : option 2.

**Conséquences**
- (+) Modèle plus simple, un seul cycle de vie et une seule table d'historique.
- (−) Impossible de postuler deux fois à la même offre (cas jugé peu probable).
- (−) Si le modèle doit évoluer (ex. plusieurs candidatures par offre), il faudra une migration.

---

## ADR-004 : l'entreprise est retrouvée par son nom ou créée dans le service
**Statut** : accepté

**Contexte** : pour tenir « capturer une offre en moins de 10 s », l'assistant ne doit pas enchaîner « chercher l'entreprise » puis « la créer » puis « créer la candidature ».

**Options**
1. L'assistant gère lui-même la recherche et la création de l'entreprise.
2. Le service `capturer_offre` fait *find-or-create* par nom.

**Décision** : option 2, avec une comparaison insensible à la casse et aux espaces superflus.

**Conséquences**
- (+) Un seul appel, moins d'erreurs possibles côté assistant.
- (−) Risque de doublons (« Doctolib » / « Doctolib SAS »). Accepté pour le MVP ; une fusion manuelle pourra être ajoutée plus tard.
- (−) Une faute de frappe crée une entreprise parasite, que l'on corrige avec `modifier_entreprise`.

---

## ADR-005 : le rappel est une commande lancée par cron, pas un endpoint HTTP
**Statut** : accepté

**Contexte** : Ferry sait lancer des cron jobs. Le déclencheur peut appeler une URL ou exécuter une commande.

**Options**
1. Le cron appelle un endpoint protégé (`POST /internal/reminders`).
2. Le cron exécute `python -m dogjob.send_reminders` dans la même image Docker.
3. Un planificateur intégré à l'application (APScheduler).

**Décision** : option 2, une exécution quotidienne à heure fixe (Europe/Paris).

**Conséquences**
- (+) Aucune route supplémentaire à protéger ; même code et même base que l'API.
- (+) Plus fiable que l'option 3 : pas de rappel perdu ou doublé si l'application redémarre ou est répliquée.
- (−) Le job dépend de la configuration de Ferry ; son échec doit être visible (logs, voire alerte).

---

## ADR-006 : relances idempotentes pilotées par un compteur
**Statut** : accepté

**Contexte** : un cron peut tourner deux fois ou être manqué ; on ne veut ni rafale de mails ni doublons.

**Options**
1. Calculer l'échéance uniquement à partir de dates.
2. Stocker `nb_relances` et `dernière_relance_le`, et ne l'incrémenter qu'après un envoi réussi.

**Décision** : option 2 : échéance = `postulé_le + 7 × (nb_relances + 1) jours`, un seul rappel par candidature et par exécution. À la 3ᵉ relance, passage automatique en `Sans suite` (source `auto` dans l'historique). Une clé d'idempotence `candidature_id + n° de relance` est transmise à Resend, si l'API la supporte (à vérifier).

**Conséquences**
- (+) Rattrapage sain après une panne : un rappel par jour d'exécution, pas une rafale.
- (+) Un échec d'envoi est simplement réessayé au passage suivant.
- (−) Un crash entre l'envoi et la mise à jour peut provoquer un doublon ; la clé d'idempotence réduit ce risque sans le garantir à 100 %.

---

## ADR-007 : authentification par clé d'API unique
**Statut** : accepté, **avec risque ouvert**

**Contexte** : mono-utilisateur, service exposé sur Internet.

**Options**
1. Clé d'API statique dans l'en-tête `Authorization: Bearer`.
2. OAuth 2.1 (requis par certains clients MCP distants).
3. Aucune authentification, réseau privé seulement.

**Décision** : option 1 : clé en variable d'environnement, comparée à temps constant, jamais journalisée. Toutes les routes l'exigent, sauf `/health`.

**Conséquences**
- (+) Simple à implémenter et à comprendre.
- (−) Une clé unique non rotative est un point de défaillance : prévoir une procédure de changement de clé.
- (−) **Risque** : si ton client MCP n'accepte pas d'en-tête personnalisé, il faudra OAuth. À vérifier sur le client choisi avant de commencer le développement.
