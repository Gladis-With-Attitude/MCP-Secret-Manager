# Architecture de MCP Secret Manager

Ce document décrit l'architecture interne de MCP Secret Manager.

Il sert de référence pour le développement, les revues de Pull Requests et les futures décisions techniques. Il ne décrit pas une implémentation détaillée, mais les frontières, responsabilités, dépendances et invariants que l'implémentation devra respecter.

MCP Secret Manager est un gestionnaire de secrets AI-first, MCP-native et OpenClaw-first. Son architecture doit donc protéger des données sensibles tout en restant suffisamment simple pour être comprise, testée et maintenue sur plusieurs années.

## 1. Objectifs de l'architecture

### Pourquoi cette architecture

Cette architecture existe pour construire un système où les responsabilités sont clairement séparées.

MCP Secret Manager doit exposer plusieurs interfaces :

- API REST ;
- serveur MCP ;
- CLI ;
- futurs SDKs ;
- futures intégrations OpenClaw et agents.

Toutes ces interfaces doivent utiliser les mêmes règles métier, les mêmes permissions, le même audit et le même service cryptographique. L'architecture doit empêcher la duplication de logique de sécurité dans chaque interface.

L'objectif principal est donc de placer la logique critique dans un coeur applicatif unique, entouré d'adaptateurs.

### Problèmes que l'architecture cherche à résoudre

L'architecture cherche à résoudre les problèmes suivants :

- éviter que l'API REST, le serveur MCP ou la CLI implémentent chacun leur propre logique de sécurité ;
- séparer clairement l'authentification, les permissions, les secrets, la crypto et l'audit ;
- permettre de tester les cas d'usage sans démarrer toute l'infrastructure ;
- éviter que le domaine dépende de FastAPI, PostgreSQL, Docker ou MCP ;
- permettre l'ajout futur de Secret Providers ;
- permettre l'ajout futur d'ABAC sans réécrire tous les modules ;
- permettre l'ajout de nouveaux clients sans modifier le domaine ;
- rendre les frontières de sécurité visibles ;
- éviter les raccourcis qui contourneraient les permissions ou l'audit.

### Problèmes que l'architecture ne cherche pas à résoudre

Le MVP ne cherche pas à résoudre :

- haute disponibilité ;
- multi-tenant complexe ;
- moteur de policies avancé ;
- orchestration distribuée ;
- intégration HSM obligatoire ;
- plugins dynamiques ;
- stockage interchangeable dès le premier jour ;
- synchronisation multi-région ;
- interface web ;
- remplacement de tous les gestionnaires de secrets existants.

L'architecture doit rendre ces évolutions possibles, mais ne doit pas les implémenter prématurément.

## 2. Principes architecturaux

### Clean Architecture

Le coeur du système doit être indépendant des frameworks.

Les règles métier et les invariants de sécurité doivent vivre dans les couches internes. Les frameworks, bases de données, protocoles et outils externes doivent rester dans les couches externes.

Conséquences :

- le Domain ne connaît pas FastAPI ;
- le Domain ne connaît pas PostgreSQL ;
- le Domain ne connaît pas MCP ;
- les interfaces appellent les cas d'usage, pas l'inverse ;
- les détails techniques doivent être remplaçables sans réécrire les règles métier.

### Separation of Concerns

Chaque composant doit avoir une responsabilité claire.

Auth authentifie. Permissions autorise. Secret orchestre le cycle de vie des secrets. Crypto chiffre et déchiffre. Audit journalise. REST et MCP exposent des interfaces.

Conséquences :

- un module ne doit pas faire le travail d'un autre ;
- la lecture d'un secret ne doit pas mélanger parsing HTTP, décision de permission, requête SQL, déchiffrement et formatage MCP dans un même endroit ;
- les responsabilités doivent être visibles dans la structure du projet ;
- les tests doivent pouvoir cibler une responsabilité isolée.

### Dependency Inversion

Les couches internes ne doivent pas dépendre des détails externes.

L'Application Layer peut exprimer un besoin comme "charger un secret" ou "écrire un événement d'audit". L'Infrastructure Layer fournit l'implémentation concrète avec PostgreSQL ou un autre mécanisme.

Conséquences :

- les cas d'usage dépendent de contrats, pas de détails ;
- les détails de stockage restent à l'extérieur ;
- les tests peuvent remplacer PostgreSQL par des doubles de test ;
- les futures intégrations ne doivent pas contaminer le domaine.

### Composition over Coupling

Les cas d'usage doivent composer des services spécialisés plutôt que coupler fortement les modules.

Une lecture de secret compose Auth, Permissions, Secret Repository, Crypto et Audit. Aucun de ces modules ne doit devenir un "god service".

Conséquences :

- les modules restent petits ;
- les interactions sont explicites ;
- les dépendances circulaires sont interdites ;
- les fonctionnalités futures se branchent sur des frontières claires.

### Explicit Dependencies

Les dépendances doivent être visibles et injectées explicitement.

Un cas d'usage qui a besoin d'un repository, d'un service crypto ou d'un service d'audit doit le déclarer clairement. Les dépendances globales implicites rendent les tests difficiles et les chemins de sécurité opaques.

Conséquences :

- éviter l'état global mutable ;
- éviter les singletons implicites pour la logique métier ;
- rendre les dépendances faciles à identifier en revue ;
- permettre des tests ciblés et prévisibles.

### Testability

L'architecture doit rendre les tests naturels.

La logique critique doit être testable sans serveur HTTP, sans serveur MCP et sans effets de bord inutiles.

Conséquences :

- les cas d'usage doivent pouvoir être testés directement ;
- les permissions doivent pouvoir être testées isolément ;
- la crypto doit pouvoir être testée indépendamment des transports ;
- l'audit doit pouvoir être vérifié sans lire de logs système ;
- les scénarios de refus doivent être aussi testés que les scénarios de succès.

### Security Boundaries

Les frontières de sécurité doivent être explicites.

MCP Secret Manager manipule des secrets. Le système doit donc définir clairement où les secrets peuvent apparaître, où ils ne doivent jamais apparaître, et quelles couches sont autorisées à déclencher un déchiffrement.

Conséquences :

- les permissions sont vérifiées avant la crypto ;
- l'audit ne reçoit jamais la valeur d'un secret ;
- les interfaces ne contournent jamais l'Application Layer ;
- les secrets en clair ont une durée de vie minimale ;
- toute nouvelle interface est une surface de sécurité.

## 3. Vue d'ensemble

Vue logique des principaux composants :

```text
                         +-----------------------+
                         |        Clients        |
                         |-----------------------|
                         | OpenClaw              |
                         | MCP Agents            |
                         | REST Clients          |
                         | CLI Users             |
                         | Future SDKs           |
                         +-----------+-----------+
                                     |
                                     v
          +--------------------------+--------------------------+
          |                 Presentation Layer                  |
          |-----------------------------------------------------|
          | REST API             MCP Server              CLI    |
          +----------+---------------+-------------------+------+
                     |                                   |
                     v                                   v
          +-----------------------------------------------------+
          |                 Application Layer                   |
          |-----------------------------------------------------|
          | Use Cases                                           |
          | Auth Orchestration                                  |
          | Permission Checks                                   |
          | Secret Workflows                                    |
          | Audit Coordination                                  |
          +--------------------------+--------------------------+
                                     |
                                     v
          +-----------------------------------------------------+
          |                    Domain Layer                     |
          |-----------------------------------------------------|
          | Vaults      Projects      Secrets      Versions     |
          | Roles       Permissions   Providers    Audit Events |
          | Domain Rules and Invariants                         |
          +--------------------------+--------------------------+
                                     |
                                     v
          +-----------------------------------------------------+
          |                Infrastructure Layer                 |
          |-----------------------------------------------------|
          | PostgreSQL Repositories                             |
          | Crypto Implementation                               |
          | Token Storage                                       |
          | Configuration                                       |
          | Migrations                                          |
          | Health Checks                                       |
          +------------+----------------+-----------------------+
                       |                |
                       v                v
              +----------------+  +----------------+
              |   PostgreSQL   |  | Crypto Backend |
              +----------------+  +----------------+
                       |
                       v
              +----------------+
              |  Audit Tables  |
              +----------------+
```

Les flèches indiquent la direction autorisée des dépendances.

Les couches externes dépendent des couches internes. Les couches internes ne dépendent jamais des couches externes.

## 4. Les couches

### Presentation Layer

La Presentation Layer expose le système aux clients.

Elle contient :

- API REST ;
- serveur MCP ;
- CLI ;
- futurs SDK adapters si nécessaire.

Responsabilités :

- recevoir les requêtes ;
- valider le format externe ;
- extraire les credentials ;
- convertir les entrées externes en commandes applicatives ;
- appeler l'Application Layer ;
- transformer les réponses applicatives en réponses REST, MCP ou CLI ;
- transformer les erreurs applicatives en erreurs de protocole.

Elle a le droit de connaître :

- le protocole exposé ;
- les schémas de requête/réponse externes ;
- les codes HTTP ;
- les formats MCP ;
- les arguments CLI ;
- les cas d'usage applicatifs qu'elle appelle.

Elle ne doit jamais connaître :

- les détails SQL ;
- les primitives crypto ;
- la structure physique des tables ;
- les règles de permission internes ;
- les secrets déchiffrés plus longtemps que nécessaire ;
- les chemins internes de stockage.

Règle importante :

La Presentation Layer ne décide pas si un acteur peut lire un secret. Elle demande à l'Application Layer d'exécuter un cas d'usage.

### Application Layer

L'Application Layer orchestre les cas d'usage.

Elle contient les workflows métier comme :

- créer un vault ;
- créer un projet ;
- créer un secret ;
- ajouter une version ;
- lire les métadonnées ;
- lire la valeur d'un secret ;
- vérifier une permission ;
- écrire un événement d'audit.

Responsabilités :

- coordonner les modules ;
- appliquer l'ordre correct des opérations ;
- vérifier les permissions ;
- demander le chiffrement ou déchiffrement ;
- déclencher l'audit ;
- gérer les transactions applicatives ;
- retourner des résultats adaptés aux interfaces.

Elle a le droit de connaître :

- les entités du Domain ;
- les contrats de repositories ;
- les contrats crypto ;
- les contrats audit ;
- les contrats de permissions ;
- les identités applicatives.

Elle ne doit jamais connaître :

- les détails HTTP ;
- les détails MCP bas niveau ;
- les arguments CLI bruts ;
- la syntaxe SQL concrète ;
- la configuration Docker ;
- la représentation exacte des tables.

Règle importante :

L'Application Layer est la seule couche autorisée à orchestrer une lecture complète de secret.

### Domain Layer

Le Domain Layer représente les concepts fondamentaux du projet.

Il contient :

- Vault ;
- Project ;
- Secret ;
- SecretVersion ;
- SecretProvider ;
- Role ;
- Permission ;
- Actor ;
- AuditEvent ;
- règles et invariants métier.

Responsabilités :

- définir les entités ;
- définir les états valides ;
- protéger les invariants ;
- exprimer les règles métier pures ;
- éviter les états incohérents.

Il a le droit de connaître :

- ses propres concepts ;
- les valeurs métier ;
- les règles de validation pures ;
- les transitions d'état autorisées.

Il ne doit jamais connaître :

- FastAPI ;
- MCP ;
- PostgreSQL ;
- SQL ;
- Docker ;
- fichiers de configuration ;
- bibliothèques crypto concrètes ;
- détails d'audit physique ;
- frameworks de test ou de transport.

Règle importante :

Le Domain Layer doit rester portable et testable sans infrastructure.

### Infrastructure Layer

L'Infrastructure Layer implémente les détails techniques.

Elle contient :

- repositories PostgreSQL ;
- migrations ;
- implémentation crypto ;
- stockage de tokens ;
- chargement de configuration ;
- health checks ;
- intégrations système ;
- éventuels adapters externes.

Responsabilités :

- persister les données ;
- charger et sauvegarder les entités ;
- appliquer les migrations ;
- effectuer le chiffrement concret ;
- gérer les connexions PostgreSQL ;
- exposer l'état de santé technique ;
- fournir les implémentations des contrats requis par l'Application Layer.

Elle a le droit de connaître :

- PostgreSQL ;
- SQL ;
- bibliothèques crypto ;
- variables de configuration ;
- détails système ;
- schémas physiques.

Elle ne doit jamais :

- décider seule d'autoriser un accès secret ;
- contourner l'Application Layer ;
- exposer des secrets en clair dans les logs ;
- écrire de l'audit contenant une valeur secrète ;
- imposer des règles métier non exprimées par les couches internes.

Règle importante :

L'Infrastructure Layer fournit des capacités. Elle ne possède pas la politique de sécurité du système.

## 5. Dépendances

Table des dépendances autorisées :

| Depuis | Vers | Autorisé | Raison |
| --- | --- | --- | --- |
| Presentation | Application | Oui | Les interfaces déclenchent les cas d'usage. |
| Presentation | Domain | Limité | Autorisé pour types simples de lecture, mais la logique passe par Application. |
| Presentation | Infrastructure | Non | Les interfaces ne doivent pas accéder directement au stockage, à la crypto ou à l'audit. |
| Application | Domain | Oui | Les cas d'usage manipulent les concepts métier. |
| Application | Infrastructure | Non direct | L'Application dépend de contrats, pas d'implémentations concrètes. |
| Application | Presentation | Non | Les cas d'usage ne connaissent pas REST, MCP ou CLI. |
| Domain | Application | Non | Le domaine ne connaît pas les workflows. |
| Domain | Infrastructure | Non | Le domaine ne connaît pas PostgreSQL, crypto concrète ou configuration. |
| Domain | Presentation | Non | Le domaine ne connaît aucun protocole externe. |
| Infrastructure | Domain | Oui | L'infrastructure reconstruit et persiste les entités du domaine. |
| Infrastructure | Application | Limité | Autorisé pour implémenter des contrats définis côté application. |
| Infrastructure | Presentation | Non | L'infrastructure ne dépend pas des interfaces. |
| REST | MCP | Non | Les interfaces ne doivent pas dépendre les unes des autres. |
| MCP | REST | Non | MCP n'est pas un wrapper REST interne. |
| CLI | REST | Non au coeur | La CLI peut appeler l'API en mode client externe, mais pas dans l'architecture interne du serveur. |
| Crypto | Audit | Non | La crypto ne journalise pas les événements métier. |
| Audit | Crypto | Non | L'audit ne chiffre/déchiffre pas les secrets. |
| Permissions | Crypto | Non | Les permissions ne dépendent pas des valeurs secrètes. |
| Crypto | Permissions | Non | La crypto ne décide pas de l'autorisation. |

Règle générale :

Les dépendances doivent pointer vers l'intérieur. Les détails techniques peuvent dépendre des abstractions métier. Les abstractions métier ne dépendent jamais des détails techniques.

## 6. Découpage en modules

### Auth

Le module Auth gère l'authentification.

Responsabilités :

- identifier l'acteur ;
- valider les tokens ;
- distinguer utilisateur, compte de service et futur agent ;
- fournir une identité applicative aux cas d'usage.

Il ne décide pas seul des permissions.

### Vault

Le module Vault gère les frontières principales de sécurité.

Responsabilités :

- créer un vault ;
- lire ses métadonnées ;
- verrouiller ou archiver un vault ;
- garantir que l'état du vault est respecté.

Un vault verrouillé ne permet pas la lecture de valeurs secrètes.

### Project

Le module Project organise les secrets dans un vault.

Responsabilités :

- créer un projet ;
- associer un projet à un vault ;
- permettre des regroupements comme `dev`, `staging`, `prod` ou `openclaw`.

Le projet n'est pas une frontière cryptographique aussi forte que le vault, mais il est une frontière d'organisation et de permissions.

### Secret

Le module Secret gère le cycle de vie logique des secrets.

Responsabilités :

- créer un secret ;
- lire les métadonnées ;
- ajouter une version ;
- déterminer la version courante ;
- refuser les états invalides.

Le module Secret ne doit pas exposer de valeur sans passage par les permissions et la crypto.

### Provider

Le module Provider représente l'abstraction Secret Provider.

Responsabilités :

- décrire l'origine ou la nature d'un secret ;
- associer un secret à un provider ;
- préparer les capacités futures comme validation, rotation ou révocation.

Au MVP, seul le provider local statique est requis.

### Permissions

Le module Permissions décide si un acteur possède une permission donnée.

Responsabilités :

- charger les rôles ;
- résoudre les permissions ;
- refuser par défaut ;
- fournir une décision explicite à l'Application Layer.

Le MVP utilise roles et permissions uniquement. ABAC est exclu du MVP.

### Audit

Le module Audit enregistre les événements sensibles.

Responsabilités :

- écrire les événements ;
- distinguer succès et refus ;
- capturer acteur, action, ressource, décision et contexte ;
- garantir que les valeurs secrètes ne sont jamais enregistrées.

L'audit observe les actions. Il ne décide pas de l'autorisation.

### Crypto

Le module Crypto chiffre et déchiffre les valeurs secrètes.

Responsabilités :

- chiffrer une nouvelle version ;
- déchiffrer une version autorisée ;
- gérer les métadonnées cryptographiques ;
- utiliser des primitives éprouvées ;
- éviter toute cryptographie maison.

Le module Crypto ne décide jamais si un acteur a le droit de lire un secret.

### MCP

Le module MCP expose les outils MCP.

Responsabilités :

- recevoir les appels tools MCP ;
- convertir ces appels en cas d'usage applicatifs ;
- limiter les réponses ;
- préserver la séparation metadata/value ;
- fournir une surface sûre aux agents.

Le module MCP ne doit pas contourner REST, mais il ne doit pas non plus dépendre de REST. MCP et REST sont deux adaptateurs vers la même Application Layer.

### REST

Le module REST expose l'API HTTP.

Responsabilités :

- recevoir les requêtes HTTP ;
- valider les payloads ;
- gérer les codes d'erreur HTTP ;
- publier le contrat OpenAPI ;
- appeler les cas d'usage applicatifs.

REST ne doit pas contenir de logique métier critique.

### CLI

Le module CLI fournit une interface opérateur.

Responsabilités :

- opérations administratives locales ;
- création de vaults, projets et secrets ;
- lecture contrôlée ;
- intégration au workflow de développement.

La CLI doit utiliser les mêmes cas d'usage et garanties de sécurité que les autres interfaces.

### Configuration

Le module Configuration charge et valide la configuration.

Responsabilités :

- configuration PostgreSQL ;
- configuration crypto ;
- configuration des tokens ;
- configuration des interfaces ;
- validation stricte au démarrage.

Une configuration invalide doit empêcher le démarrage ou désactiver explicitement la fonctionnalité concernée.

### Health

Le module Health expose l'état technique du système.

Responsabilités :

- vérifier l'accès PostgreSQL ;
- vérifier l'état minimal de configuration ;
- exposer des checks utilisables par Docker ou orchestrateurs ;
- ne jamais exposer de secret ou information sensible.

### Migration

Le module Migration gère l'évolution du schéma PostgreSQL.

Dans le monorepo, les migrations versionnées vivent sous `db/migrations/` et la configuration Alembic sous `db/alembic.ini`. Le code backend qui dépend des modèles ou repositories reste sous `backend/src/`.

Responsabilités :

- migrations versionnées ;
- compatibilité des schémas ;
- changements reproductibles ;
- documentation des ruptures éventuelles.

Les migrations ne doivent jamais écrire de secrets en clair.

## 7. Flux principaux

### Authentification

1. Un client appelle REST, MCP ou CLI.
2. La Presentation Layer extrait les credentials.
3. Le module Auth valide les credentials.
4. Auth produit une identité applicative.
5. L'Application Layer reçoit cette identité.
6. Les permissions sont évaluées dans les cas d'usage concernés.
7. L'audit enregistre les succès ou refus pertinents.

Auth identifie l'acteur. Permissions décide ce que l'acteur peut faire.

### Lecture d'un secret

1. Le client demande la valeur d'un secret précis.
2. La Presentation Layer valide le format de la demande.
3. L'Application Layer reçoit l'identité, l'action et la ressource.
4. Le secret et ses métadonnées sont chargés.
5. Le vault est vérifié.
6. Le module Permissions vérifie `secret.value.read`.
7. En cas de refus, aucun déchiffrement n'a lieu.
8. En cas d'autorisation, la version courante est chargée.
9. Le module Crypto déchiffre la valeur.
10. Le module Audit enregistre l'accès sans la valeur.
11. La Presentation Layer retourne une réponse minimale.

Invariant :

Les permissions sont toujours vérifiées avant le déchiffrement.

### Permission refusée

1. Un acteur demande une action.
2. L'Application Layer demande une décision au module Permissions.
3. Permissions retourne un refus explicite.
4. L'Application Layer déclenche un événement d'audit `denied`.
5. La Presentation Layer transforme l'erreur en réponse adaptée au protocole.
6. Aucun secret n'est déchiffré.

Le refus est un comportement normal et sécurisé.

### Création d'un secret

1. Un acteur authentifié demande la création d'un secret.
2. La Presentation Layer valide le payload externe.
3. L'Application Layer vérifie la permission `secret.create`.
4. Le module Secret valide le vault, le projet, le path et le provider.
5. Le module Crypto chiffre la valeur initiale.
6. L'Infrastructure Layer persiste le secret et sa première version.
7. Le module Audit enregistre la création sans valeur secrète.
8. La Presentation Layer retourne les métadonnées créées.

La réponse ne doit pas réexposer la valeur secrète par défaut.

### Ajout d'une version

1. Un acteur demande l'ajout d'une nouvelle version.
2. L'Application Layer vérifie la permission appropriée.
3. Le module Secret valide que le secret existe et accepte une nouvelle version.
4. Le module Crypto chiffre la nouvelle valeur.
5. L'Infrastructure Layer persiste une version immuable.
6. Le pointeur de version courante est mis à jour selon les règles applicatives.
7. L'audit enregistre l'opération.

Une version existante ne doit jamais être modifiée en place.

### Lecture via MCP

1. Un agent ou client MCP appelle un tool.
2. Le module MCP valide le nom du tool et ses arguments.
3. MCP transforme l'appel en commande applicative.
4. L'Application Layer exécute le même cas d'usage que REST ou CLI.
5. Les permissions sont évaluées.
6. Si le tool lit une valeur, la crypto intervient uniquement après autorisation.
7. L'audit indique que le client était MCP.
8. MCP retourne une réponse minimale et structurée.

MCP ne doit jamais exposer un accès plus large que REST.

### Lecture via REST

1. Un client REST appelle l'endpoint de lecture.
2. REST valide la requête et l'authentification.
3. REST appelle le cas d'usage applicatif.
4. Application vérifie permissions, vault et secret.
5. Crypto déchiffre si autorisé.
6. Audit enregistre l'accès.
7. REST transforme le résultat en réponse HTTP.

REST ne doit pas contenir de logique alternative à MCP pour le même comportement métier.

### Audit

1. Un cas d'usage démarre une action sensible.
2. L'Application Layer conserve le contexte utile : acteur, action, ressource, interface, request id.
3. Après décision, l'Application Layer demande l'écriture d'un événement.
4. Le module Audit construit un événement sans valeur secrète.
5. L'Infrastructure Layer persiste l'événement.

Les événements d'audit doivent être utiles pour enquêter sans devenir une source de fuite.

## 8. Gestion des erreurs

### Où les erreurs sont levées

Les erreurs doivent être levées au plus près de leur cause.

Exemples :

- Auth lève une erreur d'identité invalide ;
- Permissions lève ou retourne un refus d'autorisation ;
- Domain lève une erreur d'état invalide ;
- Crypto lève une erreur de déchiffrement ou de configuration crypto ;
- Infrastructure lève une erreur de stockage ou de migration ;
- Configuration lève une erreur de configuration invalide.

### Où les erreurs sont transformées

Les erreurs sont transformées aux frontières.

La Presentation Layer transforme les erreurs applicatives en :

- réponses HTTP ;
- erreurs MCP ;
- messages CLI.

L'Application Layer peut transformer des erreurs techniques en erreurs métier lorsque cela protège les détails internes.

Exemple :

Une erreur SQL brute ne doit pas être exposée à un client REST ou MCP.

### Où les erreurs sont journalisées

Les erreurs sensibles doivent être auditées au niveau applicatif.

Les erreurs techniques peuvent être journalisées par l'infrastructure, mais sans secret, token ou payload sensible.

Règles :

- un refus de permission est un événement d'audit ;
- un échec de déchiffrement est un événement de sécurité ;
- une erreur de validation peut être journalisée de manière minimale ;
- une erreur interne ne doit pas exposer de détails sensibles au client ;
- aucun log ne doit contenir de valeur secrète.

## 9. Frontières de sécurité

### Frontière client / serveur

Tout ce qui entre depuis REST, MCP ou CLI est non fiable.

Conséquences :

- validation stricte ;
- authentification obligatoire pour les actions sensibles ;
- erreurs sûres ;
- pas de confiance implicite dans les clients.

### Frontière Presentation / Application

La Presentation Layer traduit le protocole. L'Application Layer applique les cas d'usage.

Conséquences :

- pas de logique de permission dans REST ou MCP ;
- pas d'accès direct au stockage depuis REST ou MCP ;
- pas de déchiffrement dans les handlers de protocole.

### Frontière Application / Crypto

La crypto ne doit être appelée qu'après les vérifications nécessaires.

Conséquences :

- Permissions avant Crypto ;
- vault actif avant Crypto ;
- secret version valide avant Crypto ;
- audit de l'action même en cas de refus.

### Frontière Audit / Secrets

L'audit doit recevoir le contexte de l'action, jamais la valeur secrète.

Conséquences :

- pas de secret en clair dans audit ;
- pas de token complet dans audit ;
- pas de payload brut contenant une valeur ;
- pas d'erreur contenant la valeur.

### Frontière Domain / Infrastructure

Le Domain exprime les règles. L'Infrastructure fournit les détails techniques.

Conséquences :

- pas de SQL dans le domaine ;
- pas de FastAPI dans le domaine ;
- pas de dépendance PostgreSQL dans les entités ;
- pas de règles métier cachées dans les repositories.

## 10. Évolutivité

### Nouveaux Secret Providers

Les providers doivent s'ajouter derrière l'abstraction Provider.

Le provider local statique reste le cas simple du MVP. Les futurs providers GitHub, OpenAI, Anthropic, Cloudflare, Docker, AWS, TPM, YubiKey ou fichiers locaux devront s'intégrer sans modifier les règles fondamentales de Secret, Permissions, Audit ou MCP.

Un provider peut ajouter des capacités, mais ne doit pas contourner :

- permissions ;
- audit ;
- crypto ;
- séparation metadata/value.

### ABAC

ABAC est exclu du MVP mais doit pouvoir être ajouté plus tard.

L'architecture le permet en remplaçant ou enrichissant le module Permissions, sans déplacer la logique d'autorisation dans REST, MCP ou les repositories.

Le futur ABAC devra rester une décision applicative explicite.

### Nouveaux clients

Les nouveaux clients doivent être ajoutés comme adaptateurs de Presentation Layer.

Exemples :

- SDK Python ;
- SDK TypeScript ;
- web UI ;
- integrations Docker ;
- nouveaux outils CLI.

Ils doivent appeler les mêmes cas d'usage applicatifs.

### Nouveaux protocoles

Un nouveau protocole ne doit pas introduire une nouvelle logique métier.

Il doit :

- authentifier ou transmettre une identité ;
- valider ses entrées ;
- appeler l'Application Layer ;
- transformer les réponses ;
- respecter les mêmes permissions et audits.

### Nouveaux stockages

PostgreSQL est le stockage officiel du MVP.

Un futur stockage ne pourra être envisagé qu'en implémentant les contrats d'infrastructure existants. Il ne devra pas modifier le domaine ou les cas d'usage.

Le projet ne doit pas complexifier le MVP pour supporter prématurément plusieurs stockages.

### Nouveaux orchestrateurs

Les futurs orchestrateurs multi-agents doivent être modélisés comme des clients ou acteurs, pas comme des exceptions privilégiées.

Ils devront respecter :

- identités explicites ;
- permissions ;
- audit ;
- réponses limitées ;
- séparation des responsabilités.

## 11. Invariants

Les invariants suivants doivent toujours rester vrais :

- le Domain ne dépend jamais de FastAPI ;
- le Domain ne dépend jamais de MCP ;
- le Domain ne dépend jamais de PostgreSQL ;
- le Domain ne dépend jamais d'une bibliothèque crypto concrète ;
- l'Application Layer ne dépend jamais des handlers REST ;
- l'Application Layer ne dépend jamais des handlers MCP ;
- REST ne dépend jamais de MCP ;
- MCP ne dépend jamais de REST ;
- la CLI ne contourne jamais l'Application Layer ;
- les interfaces ne parlent jamais directement aux repositories ;
- les secrets ne sont jamais loggés ;
- l'audit ne voit jamais les valeurs des secrets ;
- les tokens complets ne sont jamais stockés en clair ;
- les permissions sont toujours vérifiées avant la crypto ;
- un refus de permission ne déclenche jamais de déchiffrement ;
- une version de secret est immuable ;
- une lecture de métadonnées ne donne pas accès à la valeur ;
- un vault verrouillé empêche la lecture de valeurs ;
- la crypto ne décide jamais des permissions ;
- les permissions ne dépendent jamais de la valeur déchiffrée d'un secret ;
- les erreurs exposées aux clients ne révèlent pas de détails sensibles ;
- les erreurs internes sensibles sont journalisées sans données secrètes ;
- les migrations ne stockent jamais de secret en clair ;
- les Secret Providers ne contournent jamais Permissions, Crypto ou Audit ;
- toute nouvelle interface est considérée comme une surface de sécurité ;
- toute logique de sécurité doit être testable sans protocole externe ;
- une couche ne contourne jamais la couche qui porte la responsabilité concernée.

## Conclusion

Cette architecture vise un équilibre précis : rester simple au MVP, tout en protégeant les frontières qui permettront au projet de grandir.

MCP Secret Manager ne doit pas devenir un ensemble de handlers REST, tools MCP et scripts partageant une base de données. Il doit rester un système structuré autour d'un coeur applicatif clair, de règles métier testables, d'une infrastructure interchangeable avec prudence et de frontières de sécurité explicites.

Cette discipline architecturale est ce qui permettra au projet de devenir durable, auditable et digne de confiance.
