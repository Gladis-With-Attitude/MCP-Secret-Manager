# Spécification MCP de MCP Secret Manager

Ce document définit la spécification officielle de l'interface MCP de MCP Secret Manager.

Il décrit comment MCP Secret Manager expose ses capacités aux agents IA, clients MCP et futurs orchestrateurs agentiques.

Ce document ne contient pas de code, pas de SDK MCP, pas d'implémentation Python et pas de schéma MCP. Il définit le comportement attendu du serveur MCP et les garanties qu'il doit respecter.

## 1. Objectifs

### Pourquoi MCP est une interface de première classe

MCP Secret Manager est conçu pour les systèmes agentiques.

Dans ce contexte, MCP n'est pas une intégration secondaire. C'est une interface centrale qui permet à des agents IA et orchestrateurs d'interagir avec des secrets de manière structurée, limitée, autorisée et auditée.

Un agent IA ne doit pas manipuler directement des fichiers `.env`, variables d'environnement ou tokens globaux. Il doit demander une capacité précise à travers un outil explicite, avec une identité claire et des permissions vérifiées.

L'interface MCP doit donc être pensée comme une surface de sécurité majeure.

### Pourquoi REST et MCP coexistent

REST et MCP répondent à des usages différents.

REST sert principalement :

- OpenClaw ;
- CLI ;
- scripts ;
- applications ;
- SDKs ;
- intégrations système.

MCP sert principalement :

- agents IA ;
- clients MCP ;
- orchestrateurs ;
- serveurs MCP composés ;
- futurs workflows multi-agents.

Les deux interfaces doivent partager le même coeur applicatif, le même modèle de permissions, le même audit et les mêmes règles de domaine.

### Pourquoi MCP n'est pas un wrapper REST

Le serveur MCP ne doit pas être un client REST interne.

Il est un adaptateur de Presentation Layer qui appelle directement l'Application Layer.

Raisons :

- éviter une dépendance artificielle entre interfaces ;
- éviter des comportements divergents ;
- éviter de dupliquer les erreurs de protocole ;
- préserver des réponses adaptées aux agents ;
- traiter MCP comme une surface de sécurité à part entière ;
- permettre une évolution MCP indépendante de REST.

REST et MCP ne doivent pas dépendre l'un de l'autre.

Ils doivent dépendre des mêmes cas d'usage applicatifs.

## 2. Principes

### AI First

L'interface MCP est conçue pour être utilisée par des agents IA.

Cela signifie qu'elle doit anticiper :

- demandes ambiguës ;
- prompt injection ;
- appels d'outils en chaîne ;
- délégation entre agents ;
- usage excessif ;
- exfiltration indirecte ;
- erreurs de raisonnement d'un LLM.

Conséquence :

Les outils MCP doivent être précis, limités et faciles à auditer.

### Least Privilege

Un outil MCP ne doit exposer que la capacité minimale nécessaire.

Conséquences :

- pas de bulk read de valeurs au MVP ;
- metadata et value séparées ;
- permissions explicites ;
- réponses courtes ;
- pas de privilège spécial accordé par MCP ;
- OpenClaw et les agents utilisent des rôles minimaux.

### Explicit Tooling

Chaque outil MCP doit représenter une action claire.

Un agent doit appeler un outil dont l'intention est explicite, par exemple lire les métadonnées d'un secret ou lire la valeur d'un secret précis.

Conséquences :

- pas d'outil ambigu comme `query_everything` ;
- pas d'outil qui combine metadata, value et audit sans nécessité ;
- les noms d'outils doivent être stables et compréhensibles ;
- chaque outil correspond à une permission claire.

### Minimal Responses

Les réponses MCP doivent contenir uniquement l'information nécessaire.

Conséquences :

- une liste de secrets ne contient jamais les valeurs ;
- une lecture de valeur retourne uniquement la valeur demandée et le minimum de contexte ;
- une erreur ne révèle pas de secret ;
- une réponse ne doit pas aider un agent à énumérer inutilement l'infrastructure.

### Predictable Behaviour

Les outils MCP doivent avoir un comportement stable.

Un agent ou orchestrateur doit pouvoir savoir :

- ce que l'outil fait ;
- quelle permission est nécessaire ;
- quelle ressource est concernée ;
- quel type de réponse attendre ;
- quels refus sont possibles.

La prévisibilité réduit les erreurs agentiques et facilite l'audit.

### Auditability

Les appels MCP sont des événements de sécurité.

Les actions sensibles doivent générer un AuditEvent indiquant clairement que l'interface utilisée était MCP.

Conséquences :

- les lectures de valeurs sont auditées ;
- les refus sensibles sont audités ;
- le nom du tool doit être conservé ;
- l'acteur MCP doit être identifiable ;
- les valeurs secrètes ne sont jamais auditées.

### Tool Isolation

Chaque tool doit être isolé fonctionnellement.

Un tool ne doit pas obtenir implicitement les capacités d'un autre.

Conséquences :

- `list_secrets` ne lit pas les valeurs ;
- `get_secret_metadata` ne lit pas les valeurs ;
- `read_secret_value` ne liste pas tous les secrets ;
- `list_audit_events` ne donne pas accès aux secrets ;
- `health` ne révèle pas de configuration sensible.

## 3. Architecture MCP

Vue conceptuelle :

```text
          +----------------+
          |     Agent      |
          +--------+-------+
                   |
                   v
          +----------------+
          |   MCP Client   |
          +--------+-------+
                   |
                   v
          +----------------+
          |   MCP Server   |
          +--------+-------+
                   |
                   v
          +----------------+
          | Application    |
          | Layer          |
          +--------+-------+
                   |
                   v
          +----------------+
          | Domain Layer   |
          +--------+-------+
                   |
                   v
          +----------------+
          | Infrastructure |
          +----------------+
```

### Agent

L'Agent est le système IA ou sous-agent qui demande une action.

Responsabilités :

- décider qu'un outil est nécessaire ;
- fournir les arguments demandés ;
- utiliser la réponse de manière appropriée.

Limites :

- l'agent n'est pas considéré comme intrinsèquement fiable ;
- l'agent ne décide pas de ses propres permissions ;
- l'agent ne reçoit pas de privilège implicite.

### MCP Client

Le MCP Client transporte les appels de l'agent vers le serveur MCP.

Responsabilités :

- établir la communication ;
- transmettre l'identité ou le contexte d'authentification selon configuration ;
- présenter les tools disponibles à l'agent ;
- transmettre les résultats.

Limites :

- le client MCP ne décide pas de l'autorisation ;
- le client MCP ne doit pas modifier les réponses pour contourner les restrictions ;
- le client MCP doit être traité comme une partie de la surface d'attaque.

### MCP Server

Le MCP Server expose les tools officiels de MCP Secret Manager.

Responsabilités :

- déclarer les tools ;
- valider les arguments ;
- résoudre l'acteur ;
- appeler l'Application Layer ;
- limiter les réponses ;
- transformer les erreurs en erreurs MCP sûres ;
- déclencher ou transmettre le contexte d'audit.

Limites :

- le MCP Server ne lit pas directement PostgreSQL ;
- le MCP Server ne déchiffre pas directement ;
- le MCP Server ne décide pas seul de l'autorisation ;
- le MCP Server ne dépend pas de REST.

### Application Layer

L'Application Layer porte les cas d'usage.

Responsabilités :

- vérifier les permissions ;
- orchestrer les opérations ;
- appeler Domain, Crypto, Audit et repositories ;
- appliquer les invariants métier.

Le MCP Server doit passer par cette couche pour toute action métier.

### Domain Layer

Le Domain Layer définit les concepts :

- Vault ;
- Project ;
- Secret ;
- SecretVersion ;
- Actor ;
- Role ;
- Permission ;
- Provider ;
- AuditEvent.

Il ne connaît pas MCP.

## 4. Outils (Tools)

Les tools du MVP doivent rester limités.

Ils exposent les capacités nécessaires à OpenClaw, aux premiers agents et aux intégrations MCP sans introduire de surface dangereuse.

### health

Objectif :

Vérifier que le serveur MCP répond.

Permissions nécessaires :

- aucune ou permission minimale selon configuration.

Type de réponse :

- statut minimal.

Contraintes :

- ne révèle pas de configuration sensible ;
- ne révèle pas de secrets ;
- ne révèle pas la topologie interne.

### list_vaults

Objectif :

Lister les vaults visibles par l'acteur.

Permissions nécessaires :

- `vault.read`.

Type de réponse :

- liste paginée ou bornée de métadonnées de vaults.

Contraintes :

- aucune valeur secrète ;
- ne liste que les vaults autorisés ;
- réponse limitée.

### list_projects

Objectif :

Lister les projets visibles dans un vault donné.

Permissions nécessaires :

- `project.read`.

Type de réponse :

- liste paginée ou bornée de métadonnées de projets.

Contraintes :

- nécessite un vault explicite ;
- ne révèle pas les secrets ;
- respecte l'état du vault.

### list_secrets

Objectif :

Lister les métadonnées des secrets accessibles dans un projet.

Permissions nécessaires :

- `secret.metadata.list` ou `secret.metadata.read`.

Type de réponse :

- liste paginée ou bornée de métadonnées de secrets.

Contraintes :

- ne retourne jamais les valeurs ;
- nécessite un projet explicite ;
- limite l'information retournée ;
- ne sert pas à énumérer toute l'instance.

### get_secret_metadata

Objectif :

Consulter les métadonnées d'un secret précis.

Permissions nécessaires :

- `secret.metadata.read`.

Type de réponse :

- métadonnées du secret.

Contraintes :

- ne retourne jamais la valeur ;
- ne retourne pas les données cryptographiques sensibles inutiles ;
- respecte les permissions.

### read_secret_value

Objectif :

Lire la valeur courante d'un secret précis.

Permissions nécessaires :

- `secret.value.read`.

Type de réponse :

- valeur secrète minimale et contexte minimal.

Contraintes :

- nécessite un identifiant ou chemin exact ;
- ne liste pas les secrets ;
- ne retourne qu'une seule valeur ;
- vérifie l'état du vault ;
- vérifie les permissions avant crypto ;
- génère un AuditEvent ;
- ne retourne pas de données supplémentaires inutiles.

### create_secret

Objectif :

Créer un secret et sa première version.

Permissions nécessaires :

- `secret.create`.

Type de réponse :

- métadonnées du secret créé.

Contraintes :

- la valeur initiale est chiffrée au stockage ;
- la réponse ne réexpose pas la valeur par défaut ;
- l'action est auditée ;
- le provider est explicite.

### create_secret_version

Objectif :

Ajouter une nouvelle version à un secret existant.

Permissions nécessaires :

- `secret.version.create`.

Type de réponse :

- métadonnées de la version créée.

Contraintes :

- ne modifie jamais une version existante ;
- crée une version immuable ;
- peut devenir la version courante selon cas d'usage ;
- action auditée ;
- réponse sans valeur secrète par défaut.

### list_versions

Objectif :

Lister les versions d'un secret.

Permissions nécessaires :

- `secret.version.read`.

Type de réponse :

- liste de métadonnées de versions.

Contraintes :

- ne retourne jamais les valeurs ;
- nécessite un secret explicite ;
- réponse bornée.

### read_version

Objectif :

Lire une version précise d'un secret si elle est autorisée et lisible.

Permissions nécessaires :

- `secret.value.read`.

Type de réponse :

- valeur secrète de la version demandée avec contexte minimal.

Contraintes :

- nécessite secret et version explicites ;
- ne lit pas les versions révoquées ou détruites ;
- génère un AuditEvent ;
- vérifie permissions avant crypto.

### list_audit_events

Objectif :

Lister les événements d'audit accessibles.

Permissions nécessaires :

- `audit.read`.

Type de réponse :

- liste paginée ou bornée d'événements d'audit.

Contraintes :

- ne contient jamais de valeurs secrètes ;
- peut être filtré ;
- doit éviter l'exposition excessive ;
- accès réservé.

## 5. Permissions

L'interface MCP réutilise le même modèle de permissions que REST.

Un tool MCP correspond à une action applicative et donc à une permission.

Exemples :

- `list_vaults` utilise `vault.read` ;
- `list_projects` utilise `project.read` ;
- `list_secrets` utilise `secret.metadata.read` ou `secret.metadata.list` ;
- `get_secret_metadata` utilise `secret.metadata.read` ;
- `read_secret_value` utilise `secret.value.read` ;
- `create_secret` utilise `secret.create` ;
- `create_secret_version` utilise `secret.version.create` ;
- `list_audit_events` utilise `audit.read`.

Règles :

- un tool n'accorde jamais de privilège supplémentaire ;
- MCP ne contourne jamais RBAC ;
- MCP ne possède pas de permissions spéciales ;
- l'absence de permission équivaut à un refus ;
- les refus sensibles sont auditables ;
- permissions avant crypto ;
- metadata et value restent séparées.

MCP peut adapter la forme de la réponse à un agent, mais il ne change pas la décision d'autorisation.

## 6. Gestion des erreurs

Les erreurs MCP doivent être prévisibles, sûres et adaptées aux agents.

### Erreurs de validation

Description :

Arguments manquants, invalides ou incohérents.

Garanties :

- aucune action sensible n'est exécutée ;
- aucun secret n'est retourné ;
- message suffisamment clair pour corriger l'appel ;
- pas de détail interne dangereux.

### Erreurs de permissions

Description :

L'acteur est identifié mais ne possède pas la permission.

Garanties :

- aucun déchiffrement ;
- refus potentiellement audité ;
- pas de valeur secrète ;
- pas de révélation excessive sur la ressource.

### Erreurs crypto

Description :

Déchiffrement impossible, intégrité invalide, clé absente ou algorithme non disponible.

Garanties :

- aucune valeur partielle ;
- erreur sûre ;
- événement de sécurité selon sensibilité ;
- pas de détail cryptographique exploitable dans la réponse agent.

### Outils inconnus

Description :

Le client MCP demande un tool non exposé ou non supporté.

Garanties :

- aucun fallback vers un comportement générique ;
- aucun accès implicite ;
- erreur stable ;
- possibilité d'audit si répétée ou suspecte.

### Erreurs internes

Description :

Erreur inattendue du serveur ou de l'infrastructure.

Garanties :

- message générique ;
- pas de stacktrace ;
- pas de secret ;
- logs internes prudents ;
- audit si l'action était sensible.

## 7. Réponses

### Réponses minimales

Les réponses MCP doivent être minimales par défaut.

Un tool retourne seulement ce qui est nécessaire pour l'action demandée.

Exemples :

- `list_secrets` retourne des métadonnées utiles, pas les valeurs ;
- `read_secret_value` retourne une seule valeur, pas tout le secret ;
- `health` retourne un statut, pas la configuration.

### Séparation metadata/value

La séparation metadata/value est obligatoire.

Un tool metadata ne doit jamais retourner une valeur.

Un tool de lecture de valeur ne doit pas se transformer en endpoint d'exploration.

### Limitation des informations

Les réponses doivent limiter :

- volume ;
- détails internes ;
- métadonnées sensibles ;
- informations cryptographiques ;
- structure complète de l'instance.

Le but est d'aider l'agent à accomplir sa tâche, pas de lui donner une carte complète du système.

### Absence de secrets inutiles

Un secret n'est retourné que si :

- le tool est explicitement destiné à lire une valeur ;
- la ressource est précise ;
- l'acteur possède la permission ;
- le vault et la version sont dans un état compatible ;
- le cas d'usage applicatif autorise l'opération.

## 8. Audit

### Tools générant un AuditEvent

Doivent générer un AuditEvent :

- `read_secret_value` ;
- `read_version` ;
- `create_secret` ;
- `create_secret_version` ;
- `list_audit_events` ;
- refus de permission sur action sensible ;
- erreur crypto significative.

Peuvent générer un AuditEvent selon configuration :

- `list_vaults` ;
- `list_projects` ;
- `list_secrets` ;
- `get_secret_metadata` ;
- `health` en cas d'abus ou diagnostic.

### Distinguer REST et MCP

Chaque AuditEvent issu de MCP doit indiquer que l'interface utilisée était MCP.

Il doit également conserver conceptuellement :

- actor_id ;
- actor_type ;
- tool_name ;
- action ;
- resource_type ;
- resource_id ;
- decision ;
- timestamp ;
- request_id ou équivalent ;
- client_type = MCP.

### Pourquoi un Tool est une surface de sécurité

Un tool MCP peut être appelé par un agent IA.

Cela signifie qu'il peut être invoqué :

- à la suite d'une mauvaise instruction ;
- sous influence d'une prompt injection ;
- de manière répétée ;
- dans un contexte de délégation ;
- avec une compréhension incomplète de l'agent.

Chaque tool doit donc être traité comme une interface publique sensible.

## 9. Sécurité spécifique aux agents

### Prompt injection

Un agent peut être influencé par du contenu externe qui lui demande d'exfiltrer un secret.

Mitigations :

- tools explicites ;
- permissions strictes ;
- pas de bulk values ;
- réponses minimales ;
- audit ;
- futures justifications et mission context.

### Tool abuse

Un agent peut appeler un tool plus souvent ou plus largement que nécessaire.

Mitigations :

- ressources explicites ;
- pagination ;
- permissions ;
- audit des refus ;
- quotas futurs ;
- budgets futurs.

### Secret exfiltration

Un agent autorisé peut recevoir un secret puis le divulguer.

Mitigations :

- least privilege ;
- une seule valeur à la fois ;
- audit ;
- tokens limités ;
- futures politiques "use without reveal" si possible ;
- human-in-the-loop futur.

Limite :

MCP Secret Manager ne peut pas garantir ce qu'un agent fait après réception d'une valeur autorisée.

### Excessive access

Un agent peut essayer d'obtenir plus de métadonnées ou secrets que nécessaire.

Mitigations :

- séparation list/read ;
- permissions metadata distinctes ;
- refus par défaut ;
- filtrage par ressource ;
- quotas futurs ;
- détection future d'anomalies.

### Future quotas

Les quotas pourront limiter :

- nombre de lectures ;
- nombre de refus ;
- nombre d'appels par mission ;
- volume de métadonnées ;
- accès par période.

Les quotas devront être évalués avant l'action sensible.

### Future budgets

Les budgets pourront limiter l'usage d'un agent selon :

- mission ;
- coût ;
- nombre de secrets ;
- niveau de sensibilité ;
- durée.

Un budget dépassé devra produire un refus auditable.

### Future mission context

Mission Context permettra de lier une demande de secret à :

- une mission ;
- un agent ;
- un orchestrateur ;
- une justification ;
- une durée ;
- un scope.

Ce contexte améliorera l'audit et les futures permissions contextuelles.

## 10. Invariants

Les invariants suivants doivent toujours rester vrais :

- un Tool ne contourne jamais l'Application Layer ;
- un Tool ne lit jamais directement PostgreSQL ;
- un Tool ne déchiffre jamais directement une valeur ;
- un Tool ne contourne jamais RBAC ;
- un Tool n'accorde jamais de privilège supplémentaire ;
- un Tool inconnu ne déclenche jamais de fallback générique ;
- MCP ne dépend pas de REST ;
- REST ne dépend pas de MCP ;
- MCP et REST partagent les mêmes cas d'usage applicatifs ;
- metadata et value restent séparées ;
- un Tool metadata ne retourne jamais de valeur secrète ;
- un Tool de liste ne retourne jamais de valeur secrète ;
- `read_secret_value` retourne au maximum une valeur précise ;
- `read_version` retourne au maximum une version précise ;
- une lecture de valeur vérifie toujours les permissions ;
- une lecture de valeur vérifie toujours l'état du vault ;
- les permissions sont vérifiées avant la crypto ;
- un refus de permission ne déclenche jamais de déchiffrement ;
- un secret n'est jamais retourné sans permission ;
- un secret n'est jamais retourné depuis une erreur ;
- une erreur ne révèle jamais de valeur secrète ;
- une erreur ne révèle jamais de token complet ;
- une erreur ne révèle jamais de clé ;
- une erreur crypto ne retourne jamais de valeur partielle ;
- une réponse MCP est minimale par défaut ;
- un AuditEvent MCP ne contient jamais de secret ;
- un AuditEvent MCP inclut le fait que l'interface était MCP ;
- les lectures de valeur via MCP sont auditées ;
- les créations de secrets via MCP sont auditées ;
- les créations de versions via MCP sont auditées ;
- les refus sensibles via MCP sont auditables ;
- `health` ne révèle jamais de configuration sensible ;
- `list_audit_events` ne révèle jamais de valeur secrète ;
- les outils MCP sont nommés explicitement ;
- chaque tool sensible correspond à une permission documentée ;
- les réponses ne contiennent pas de métadonnées cryptographiques inutiles ;
- les réponses ne fournissent pas une carte complète de l'instance sans permission ;
- les agents ne reçoivent pas de privilège implicite ;
- OpenClaw n'obtient pas de permissions spéciales via MCP ;
- les futurs quotas ou budgets ne doivent pas affaiblir RBAC ;
- toute nouvelle surface MCP est considérée comme une surface de sécurité ;
- toute modification de tool sensible doit mettre à jour cette spécification.

## 11. Évolutions futures

### Agent Identity

Les Agent Identities permettront de distinguer les agents des services classiques.

Elles pourront inclure :

- agent_id ;
- modèle ;
- orchestrateur ;
- parent agent ;
- niveau de confiance ;
- durée de vie ;
- contexte d'exécution.

Elles devront s'intégrer au modèle Actor existant.

### Mission Context

Mission Context permettra de lier une demande MCP à une mission.

Objectifs :

- comprendre pourquoi un secret a été demandé ;
- limiter les accès par mission ;
- auditer les décisions ;
- préparer budgets et quotas ;
- faciliter l'investigation.

### Quotas

Les quotas limiteront l'usage des tools.

Exemples :

- lectures par période ;
- lectures par agent ;
- lectures par mission ;
- refus par période ;
- appels à des tools sensibles.

### Budgets

Les budgets permettront de limiter une mission ou un agent selon un coût ou un niveau d'accès.

Exemples :

- nombre maximal de secrets ;
- accès à certaines classifications ;
- durée d'une mission ;
- nombre de providers externes ;
- coût monétaire associé aux providers.

### Streaming

Le streaming pourra être utile pour :

- opérations longues ;
- export d'audit ;
- suivi de rotation ;
- événements administratifs.

Il ne doit jamais devenir un canal de streaming de valeurs secrètes.

### Approval Workflow

Certaines demandes pourront exiger une approbation.

Exemples :

- secret de haute sensibilité ;
- agent inconnu ;
- lecture hors mission ;
- rotation critique ;
- accès break-glass.

L'approbation devra être auditée.

### Human in the Loop

Human in the Loop permettra d'exiger une validation humaine avant une action sensible.

Cette capacité est particulièrement importante pour les agents IA.

Elle devra être conçue sans bloquer les usages simples du MVP.

### Multi-agent orchestration

Les orchestrateurs multi-agents pourront introduire :

- parent agent ;
- child agent ;
- délégation ;
- mission partagée ;
- propagation limitée de permissions ;
- audit hiérarchique.

La délégation ne devra jamais impliquer un héritage implicite de tous les secrets.

### Context-aware permissions

Les permissions contextuelles pourront enrichir RBAC.

Exemples :

- mission ;
- heure ;
- source ;
- agent ;
- outil ;
- justification ;
- classification.

Cette évolution correspondra à ABAC ou un modèle proche, mais elle est exclue du MVP.

### Dynamic Secrets

Les secrets dynamiques pourront être générés à la demande avec TTL.

Exemples :

- credentials temporaires ;
- tokens courts ;
- accès provider limité ;
- clés éphémères.

Ils devront respecter :

- permissions ;
- audit ;
- TTL ;
- révocation ;
- limites agents.

## Conclusion

L'interface MCP de MCP Secret Manager est conçue pour permettre aux agents IA d'utiliser des secrets sans recevoir un accès large à l'infrastructure.

Elle repose sur des tools explicites, des permissions strictes, des réponses minimales, une séparation metadata/value et un audit systématique des actions sensibles.

MCP n'est pas un wrapper REST. C'est une interface agentique de première classe vers les mêmes cas d'usage applicatifs que REST, avec les mêmes garanties de sécurité et une attention particulière aux risques propres aux agents IA.

