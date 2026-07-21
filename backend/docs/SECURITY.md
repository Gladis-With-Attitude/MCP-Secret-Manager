# Sécurité de MCP Secret Manager

Ce document définit la stratégie de sécurité officielle de MCP Secret Manager.

Il explique comment le projet protège les secrets, quels risques il prend en compte, quelles garanties il cherche à fournir et quelles limites il assume explicitement.

Ce document ne décrit pas une implémentation. Il définit les exigences et décisions de sécurité que l'implémentation devra respecter.

MCP Secret Manager est un composant d'infrastructure critique. Toute évolution du projet doit être compatible avec ce document, avec la Constitution du projet et avec l'architecture validée.

## 1. Objectifs

### Pourquoi la sécurité est la priorité absolue

MCP Secret Manager stocke et contrôle l'accès à des secrets capables de compromettre une infrastructure complète.

Ces secrets peuvent donner accès à :

- des services IA ;
- des comptes développeur ;
- des dépôts de code ;
- des serveurs ;
- des bases de données ;
- des fournisseurs cloud ;
- des APIs externes ;
- des containers ;
- des agents IA ;
- des serveurs MCP ;
- OpenClaw.

Une faille dans MCP Secret Manager peut provoquer une compromission en cascade. La sécurité n'est donc pas une fonctionnalité parmi d'autres. Elle est la condition d'existence du projet.

### Actifs protégés

Le projet protège principalement :

- valeurs secrètes ;
- clés API ;
- tokens OAuth ;
- clés SSH ;
- mots de passe ;
- certificats ;
- secrets applicatifs ;
- tokens de service ;
- clés cryptographiques internes ;
- métadonnées sensibles ;
- historique des versions ;
- événements d'audit ;
- configuration de sécurité ;
- permissions et rôles.

Les métadonnées ne sont pas toujours secrètes au sens cryptographique, mais elles sont sensibles. Un nom de secret, un chemin, un provider ou un projet peut révéler l'architecture interne d'une infrastructure.

### Objectifs de sécurité

MCP Secret Manager cherche à garantir :

- confidentialité des secrets au repos ;
- confidentialité des secrets en transit ;
- contrôle explicite des accès ;
- refus par défaut ;
- séparation entre métadonnées et valeurs secrètes ;
- audit des actions sensibles ;
- réduction du rayon d'impact d'un token volé ;
- résistance à l'exfiltration de base PostgreSQL seule ;
- protection contre les fuites accidentelles dans logs et erreurs ;
- comportement prévisible face aux agents IA ;
- intégration sûre avec OpenClaw et MCP ;
- simplicité suffisante pour être auditable.

### Non-objectifs de sécurité

Le projet ne prétend pas garantir :

- la sécurité d'une machine entièrement compromise ;
- la protection contre un administrateur root malveillant sur l'hôte ;
- l'impossibilité pour un client autorisé de divulguer un secret après l'avoir reçu ;
- la prévention complète de toute fuite mémoire ;
- la sécurité de fournisseurs externes comme GitHub, OpenAI ou Cloudflare ;
- la sécurité des applications qui consomment les secrets ;
- la détection parfaite de toutes les attaques ;
- l'anonymat des utilisateurs ;
- la conformité réglementaire automatique ;
- la haute disponibilité sécurisée au MVP.

Ces limites doivent rester explicites dans toute communication du projet.

## 2. Threat Model

Le modèle de menace de MCP Secret Manager considère que le système est exposé à des acteurs humains, services, agents IA, orchestrateurs, erreurs de configuration, dépendances compromises et attaques opportunistes.

Les niveaux de probabilité utilisés sont :

- faible ;
- moyenne ;
- élevée.

Les niveaux d'impact utilisés sont :

- faible ;
- moyen ;
- élevé ;
- critique.

### Menaces principales

| Menace | Description | Impact | Probabilité | Stratégie de mitigation |
| --- | --- | --- | --- | --- |
| Vol de base PostgreSQL | Un attaquant obtient un dump ou accès lecture à la base. | Critique | Moyenne | Chiffrement des valeurs, envelope encryption, séparation de la clé maître, pas de secrets en clair, permissions base limitées. |
| Fuite de logs | Une valeur secrète, un token ou un payload sensible apparaît dans les logs. | Critique | Moyenne | Interdiction de logger les secrets, audit sans valeurs, redaction, tests, revues de code. |
| Serveur compromis | L'hôte Debian ou le container applicatif est compromis. | Critique | Moyenne | Durcissement production, séparation des secrets, permissions Linux, rotation post-incident, audit, limitation des tokens. |
| Token volé | Un token API, CLI, MCP ou OpenClaw est exfiltré. | Élevé | Élevée | Tokens hashés au stockage, révocation, durée de vie limitée à terme, rôles minimaux, audit d'utilisation. |
| Prompt injection | Un contenu externe pousse un agent IA à demander ou révéler un secret. | Élevé | Élevée | MCP tools limités, permissions strictes, demandes précises, pas de bulk read, audit agentique futur, least privilege. |
| Agent malveillant | Un agent tente d'obtenir plus de secrets que nécessaire. | Élevé | Moyenne | Identité dédiée à terme, permissions minimales, quotas futurs, réponses limitées, audit des refus. |
| Développeur malveillant | Une contribution introduit une faille ou une exfiltration. | Critique | Faible à moyenne | Petites PR, revues, tests, CI, analyse de dépendances, documentation des changements sécurité. |
| Utilisateur légitime imprudent | Un admin expose un token, configure trop largement ou lit un secret dans un contexte non sûr. | Élevé | Élevée | Secure defaults, documentation, rôles minimaux, avertissements, audit, révocation. |
| Brute force | Tentatives répétées sur tokens, mots de passe ou endpoints. | Moyen à élevé | Moyenne | Hash des tokens, rate limiting futur, logs d'échec, refus génériques, durcissement reverse proxy. |
| Énumération | Un attaquant tente de découvrir vaults, projets, chemins ou IDs. | Moyen | Élevée | Permissions sur métadonnées, erreurs prudentes, pagination contrôlée, pas de recherche large non autorisée. |
| Replay | Réutilisation d'une requête ou d'un token capturé. | Élevé | Moyenne | HTTPS, tokens révocables, TTL futurs, idempotency contrôlée sur mutations, audit. |
| Fuite mémoire | Une valeur secrète reste en mémoire ou apparaît dans un dump. | Élevé | Moyenne | Durée de vie minimale des secrets en clair, pas de cache en clair au MVP, durcissement OS, limitation des dumps. |
| Supply chain | Dépendance compromise ou paquet malveillant. | Critique | Moyenne | Dépendances limitées, lockfiles, revue des dépendances, scan CI, mises à jour contrôlées. |
| Dépendance compromise | Une bibliothèque utilisée par le projet contient une vulnérabilité. | Élevé | Moyenne | Suivi CVE, mises à jour, tests de non-régression, dépendances éprouvées. |
| Mauvaise configuration | Secret Manager lancé avec permissions trop larges ou clé maître mal protégée. | Critique | Moyenne | Validation stricte de configuration, documentation production, refus au démarrage si configuration invalide. |
| Backup exposé | Un backup PostgreSQL ou archive est accessible à un attaquant. | Critique | Moyenne | Backups chiffrés à terme, séparation de la clé maître, stockage restreint, test de restauration. |
| Interface MCP trop large | Un tool MCP permet un accès excessif. | Critique | Moyenne | MCP comme surface sécurité, tools précis, pas de bulk values, mêmes permissions que REST. |
| Contournement par interface | REST, MCP ou CLI implémente une logique différente. | Critique | Moyenne | Application Layer unique, tests partagés, interdiction d'accès direct aux repositories. |
| Erreur crypto | Nonce réutilisé, mauvaise clé, mauvais AAD ou primitive faible. | Critique | Faible à moyenne | Bibliothèques éprouvées, AES-256-GCM, no home-made crypto, tests crypto, revue stricte. |
| Compromission OpenClaw | OpenClaw est compromis et utilise ses permissions. | Élevé | Moyenne | Rôle OpenClaw minimal, vault/projet dédié, révocation token, audit filtrable. |
| Provider externe compromis | Un provider futur expose ou modifie un secret. | Élevé | Moyenne | Abstraction provider contrôlée, permissions/audit obligatoires, pas de confiance implicite. |

### Hypothèses de confiance

Le modèle de sécurité suppose :

- l'hôte de production est administré avec sérieux ;
- PostgreSQL est accessible uniquement depuis des réseaux ou containers autorisés ;
- la clé maître n'est pas stockée en clair dans PostgreSQL ;
- les clients autorisés sont responsables de ce qu'ils font avec un secret reçu ;
- les administrateurs comprennent qu'un accès root à la machine peut compromettre le système.

Ces hypothèses doivent être réduites dans le temps, mais elles ne peuvent pas être éliminées totalement dans le MVP.

## 3. Security Model

### Zero Trust

Le système ne fait pas confiance implicitement à un client, une interface, un réseau local ou un agent.

Chaque demande doit être authentifiée, autorisée et auditée selon son niveau de sensibilité.

Conséquences :

- REST, MCP et CLI suivent les mêmes règles ;
- un client local n'est pas automatiquement privilégié ;
- OpenClaw reçoit une identité et des permissions explicites ;
- les futurs agents IA auront leurs propres identités et limites.

### Least Privilege

Chaque acteur reçoit uniquement les permissions nécessaires.

Au MVP, cela se traduit par un modèle RBAC simple. A terme, le projet pourra ajouter des mécanismes plus contextuels, mais le principe reste identique : réduire le rayon d'impact.

Conséquences :

- séparation metadata/value ;
- rôles dédiés ;
- pas de wildcard dangereux au MVP ;
- tokens de service limités ;
- permissions explicites par action sensible.

### Fail Closed

Le système refuse l'accès en cas d'incertitude.

Conséquences :

- absence de permission = refus ;
- erreur de vérification = refus ;
- vault verrouillé = refus de lecture ;
- configuration invalide = démarrage refusé ou fonctionnalité désactivée explicitement ;
- erreur crypto = aucune valeur retournée.

### Defense in Depth

La sécurité ne repose pas sur une seule barrière.

MCP Secret Manager combine :

- authentification ;
- autorisation ;
- chiffrement ;
- audit ;
- séparation des couches ;
- restrictions PostgreSQL ;
- durcissement Docker/Linux ;
- documentation opérateur ;
- tests.

Si une barrière échoue, les autres doivent limiter l'impact.

### Explicit Authorization

Chaque action sensible doit correspondre à une permission explicite.

Conséquences :

- `secret.metadata.read` est distinct de `secret.value.read` ;
- `audit.read` est distinct de l'administration ;
- les tools MCP déclarent clairement l'action applicative appelée ;
- aucun accès secret ne doit dépendre d'une convention implicite.

### Secure Defaults

La configuration par défaut doit être sûre.

Conséquences :

- refus par défaut ;
- pas de secret en clair au repos ;
- pas de logs contenant les payloads sensibles ;
- pas de lecture bulk de valeurs au MVP ;
- services exposés minimalement ;
- configuration production explicitement validée.

## 4. Authentification

L'authentification répond à la question : "Qui fait la demande ?"

Elle ne répond pas à la question : "Cette identité a-t-elle le droit de faire cette action ?" Cette seconde question appartient à l'autorisation.

### Admin

L'admin est un utilisateur humain chargé d'administrer une instance personnelle auto-hébergée.

Responsabilités typiques :

- initialiser le système ;
- créer des vaults ;
- créer des projets ;
- gérer les rôles ;
- créer des comptes de service ;
- révoquer des tokens ;
- consulter l'audit ;
- réaliser des opérations de récupération.

L'admin est puissant, mais ses actions doivent rester auditables. Même un admin ne doit pas bénéficier de comportements implicites invisibles.

### Service Account

Un Service Account représente un service technique.

Exemples :

- OpenClaw ;
- un serveur MCP ;
- une application interne ;
- un script d'automatisation ;
- un container Docker.

Un Service Account doit :

- posséder une identité stable ;
- utiliser un token révocable ;
- recevoir un rôle minimal ;
- être auditée séparément d'un utilisateur humain.

### OpenClaw

OpenClaw est le premier Service Account officiel du projet.

OpenClaw doit avoir :

- une identité dédiée ;
- un vault ou projet dédié ;
- un rôle minimal ;
- un token révocable ;
- des accès auditables ;
- aucune permission administrative inutile.

La compromission d'OpenClaw ne doit pas donner accès à tous les secrets de l'instance.

### Future Agent Identity

Les agents IA seront représentés à terme comme des identités de première classe.

Une future Agent Identity pourra inclure :

- agent_id ;
- parent_agent_id ;
- orchestrateur ;
- mission ;
- durée de vie ;
- budget ;
- quota ;
- justification ;
- tool MCP utilisé.

Ces éléments ne font pas partie du MVP complet, mais l'architecture doit les anticiper.

## 5. Autorisation

L'autorisation répond à la question : "Cette identité peut-elle effectuer cette action sur cette ressource ?"

### RBAC du MVP

Le MVP utilise un modèle RBAC simple basé sur :

- acteurs ;
- rôles ;
- permissions ;
- ressources.

Exemples de permissions :

- `vault.read` ;
- `project.read` ;
- `secret.create` ;
- `secret.metadata.read` ;
- `secret.value.read` ;
- `secret.update` ;
- `audit.read` ;
- `token.create` ;
- `token.revoke`.

Ce modèle est volontairement simple pour être :

- compréhensible ;
- testable ;
- auditable ;
- adapté au MVP ;
- suffisant pour OpenClaw.

### Pourquoi ABAC est exclu du MVP

ABAC permet des règles contextuelles plus fines, mais introduit une complexité importante.

Le MVP exclut ABAC pour éviter :

- un moteur de policy prématuré ;
- des règles difficiles à auditer ;
- des comportements implicites ;
- des erreurs de priorité entre règles ;
- une surface de test trop large.

ABAC pourra être ajouté plus tard dans le module Permissions, sans déplacer l'autorisation dans REST, MCP ou les repositories.

### Évaluation des permissions

Une permission doit être évaluée :

1. après authentification ;
2. avant toute action sensible ;
3. avant tout déchiffrement ;
4. avant toute modification ;
5. avec une action et une ressource explicites ;
6. avec un refus par défaut.

Une évaluation doit produire une décision claire :

- autorisé ;
- refusé.

Le refus doit être auditable.

### Éviter les contournements

Les contournements sont évités par les règles suivantes :

- REST ne parle pas directement aux repositories ;
- MCP ne parle pas directement aux repositories ;
- CLI ne contourne pas l'Application Layer ;
- Crypto ne décide pas des permissions ;
- Infrastructure ne décide pas des droits métier ;
- tous les flux de lecture de valeur passent par le même cas d'usage applicatif ;
- les tests couvrent succès et refus.

## 6. Protection des secrets

### Secrets au repos

Les secrets stockés dans PostgreSQL doivent être chiffrés.

La base de données peut contenir :

- ciphertext ;
- nonce ;
- métadonnées crypto ;
- métadonnées métier ;
- informations de version.

La base ne doit jamais contenir :

- valeur secrète en clair ;
- clé maître ;
- token complet en clair.

L'exfiltration de PostgreSQL seule ne doit pas suffire à révéler les valeurs secrètes.

### Secrets en mémoire

Les secrets peuvent exister temporairement en mémoire lorsqu'un client autorisé les lit.

Exigences :

- durée de vie minimale ;
- pas de cache en clair au MVP ;
- pas de stockage global de valeurs déchiffrées ;
- pas de logs de valeurs ;
- prudence avec exceptions et traces.

Le projet reconnaît que Python ne permet pas de garantir un effacement mémoire parfait. Cette limite doit être compensée par la réduction de la durée d'exposition et le durcissement de l'environnement.

### Secrets en transit

Les secrets transmis à un client autorisé doivent circuler sur un canal protégé.

Exigences :

- HTTPS en production ;
- reverse proxy correctement configuré ;
- pas de secret dans URL ou query string ;
- pas de secret dans headers non nécessaires ;
- réponses minimales ;
- clients responsables de leur propre stockage après réception.

### Secrets dans les logs

Les secrets ne doivent jamais apparaître dans :

- logs applicatifs ;
- logs HTTP ;
- logs MCP ;
- logs CLI ;
- traces ;
- messages d'erreur ;
- événements d'audit ;
- sorties de debug.

Les logs doivent privilégier :

- identifiants de ressources ;
- actions ;
- décisions ;
- erreurs génériques ;
- request_id ;
- actor_id.

### Secrets dans les erreurs

Les erreurs ne doivent jamais inclure :

- valeur secrète ;
- token complet ;
- payload brut sensible ;
- clé ;
- ciphertext inutilement exposé ;
- stacktrace en production.

Les erreurs client doivent être sûres, compréhensibles et non révélatrices.

### Secrets dans les backups

Les backups contiendront des ciphertexts et métadonnées.

Ils doivent être protégés comme des actifs sensibles.

Exigences :

- accès restreint ;
- séparation de la clé maître ;
- chiffrement des backups à terme ;
- test de restauration ;
- rotation après suspicion de fuite ;
- documentation claire.

Un backup PostgreSQL plus la clé maître peut compromettre tous les secrets. Ces éléments doivent être séparés opérationnellement.

## 7. Cryptographie

### Pourquoi AES-256-GCM

AES-256-GCM est retenu pour le MVP comme mécanisme principal de chiffrement authentifié.

Il fournit :

- confidentialité ;
- intégrité ;
- authentification des données associées ;
- maturité ;
- compatibilité large ;
- compréhension par les auditeurs sécurité.

L'utilisation doit reposer sur une bibliothèque éprouvée. Le projet ne doit pas implémenter lui-même AES, GCM ou une primitive cryptographique.

### Pourquoi envelope encryption

Envelope encryption permet de séparer les clés qui chiffrent les données des clés qui protègent ces clés.

Cette approche facilite :

- rotation de clés ;
- séparation par vault ;
- limitation du rayon d'impact ;
- migration future vers TPM, YubiKey ou HSM ;
- re-chiffrement de clés sans forcément re-chiffrer toutes les données.

### Pourquoi une clé maître

La clé maître est la racine de confiance de l'instance.

Elle permet de protéger les clés de niveau inférieur.

Elle ne doit pas être stockée dans PostgreSQL.

Sa protection est une responsabilité opérationnelle majeure.

Au MVP, la clé maître peut être gérée localement de manière simple mais stricte. A terme, le projet pourra évoluer vers des mécanismes matériels ou distribués.

### Pourquoi un DEK par version

Un Data Encryption Key par version de secret réduit le couplage cryptographique entre secrets.

Cette approche permet :

- versions immuables ;
- rotation plus propre ;
- révocation future ;
- rewrap de clés ;
- isolation des erreurs ;
- audit plus clair.

Une version de secret chiffrée avec son propre DEK est plus facile à raisonner qu'un grand ensemble de secrets partageant une même clé de données.

### Interdictions cryptographiques

Le projet interdit :

- cryptographie maison ;
- chiffrement sans authentification ;
- stockage de clé maître en base ;
- réutilisation dangereuse de nonce ;
- génération aléatoire non sécurisée ;
- algorithmes obsolètes ;
- protocoles improvisés ;
- downgrade silencieux d'algorithme.

## 8. Audit

### Objectifs de l'audit

L'audit doit permettre de comprendre les actions sensibles.

Il doit aider à :

- enquêter sur un incident ;
- détecter des accès inhabituels ;
- prouver qu'une action a eu lieu ;
- identifier un acteur ;
- distinguer succès et refus ;
- comprendre quelle interface a été utilisée ;
- suivre l'activité OpenClaw, MCP et future agentique.

### Quoi auditer

Doivent être audités :

- authentification réussie ou refusée selon sensibilité ;
- création de token ;
- révocation de token ;
- création de vault ;
- verrouillage ou archivage de vault ;
- création de projet ;
- création de secret ;
- ajout de version ;
- lecture de métadonnées sensible ;
- lecture de valeur secrète ;
- refus de permission ;
- erreur crypto ;
- opération de backup ou restauration ;
- changement de rôle ou permission.

### Quoi ne jamais auditer

L'audit ne doit jamais contenir :

- valeur secrète ;
- token complet ;
- clé maître ;
- DEK ;
- mot de passe ;
- payload brut sensible ;
- stacktrace contenant des données sensibles.

### Durée de conservation

La durée de conservation dépendra de l'exploitation de l'instance.

Principes :

- conserver assez longtemps pour enquêter ;
- éviter une croissance non maîtrisée ;
- protéger les événements d'audit comme des données sensibles ;
- documenter les politiques de purge ;
- préserver les événements liés aux incidents.

Au MVP, la priorité est la fiabilité de l'écriture d'audit. Les politiques avancées de rétention peuvent venir ensuite.

## 9. Surface d'attaque

### REST

Risques :

- injection de payload ;
- endpoints trop permissifs ;
- erreurs trop détaillées ;
- brute force ;
- énumération ;
- mauvaise authentification.

Protections :

- validation stricte ;
- OpenAPI ;
- authentification obligatoire ;
- permissions explicites ;
- erreurs sûres ;
- pas de bulk read de valeurs au MVP ;
- audit.

### MCP

Risques :

- tool trop puissant ;
- prompt injection ;
- agent qui demande trop ;
- confusion entre metadata et value ;
- réponse contenant plus que nécessaire ;
- contournement des permissions REST.

Protections :

- MCP comme composant de première classe ;
- tools limités ;
- mêmes cas d'usage que REST ;
- permissions identiques ;
- réponses minimales ;
- pas d'accès direct aux repositories ;
- audit avec client_type MCP.

### CLI

Risques :

- exposition dans shell history ;
- affichage accidentel ;
- mauvais contexte utilisateur ;
- usage sur machine non sécurisée.

Protections :

- commandes prudentes ;
- documentation ;
- pas de sortie verbeuse contenant des secrets par défaut ;
- mêmes permissions que les autres interfaces ;
- audit des actions sensibles.

### PostgreSQL

Risques :

- dump exfiltré ;
- compte base trop privilégié ;
- accès réseau non restreint ;
- logs SQL sensibles ;
- backup exposé.

Protections :

- chiffrement applicatif des valeurs ;
- utilisateur PostgreSQL à privilèges limités ;
- réseau restreint ;
- migrations contrôlées ;
- backups protégés ;
- pas de secret en clair.

### Docker

Risques :

- variables d'environnement exposées ;
- volumes trop larges ;
- container privilégié ;
- réseau trop ouvert ;
- logs container contenant des secrets.

Le développement local utilise le Docker Compose racine avec les services `postgres`, `backend` et `frontend`. Cette orchestration sert à rendre l'environnement reproductible ; elle ne constitue pas une configuration de production durcie.

Protections :

- configuration minimale ;
- volumes restreints ;
- pas de container privilégié par défaut ;
- réseau limité ;
- logs redacted ;
- documentation production.

### Configuration

Risques :

- clé maître mal protégée ;
- mode debug en production ;
- CORS trop permissif ;
- secrets dans fichiers versionnés ;
- permissions fichiers incorrectes.

Protections :

- validation au démarrage ;
- documentation ;
- modes explicites ;
- permissions Linux strictes ;
- interdiction des secrets dans Git ;
- erreurs de configuration fail closed.

### Providers

Risques :

- provider externe compromis ;
- permissions provider trop larges ;
- rotation incorrecte ;
- fuite via metadata ;
- provider qui contourne l'audit.

Protections :

- abstraction contrôlée ;
- permissions et audit obligatoires ;
- capacités explicites ;
- provider local simple au MVP ;
- intégrations externes ajoutées progressivement.

### OpenClaw

Risques :

- token OpenClaw volé ;
- OpenClaw compromis ;
- accès trop large ;
- logs OpenClaw contenant des secrets ;
- appel MCP ou REST non prévu.

Protections :

- identité dédiée ;
- rôle minimal ;
- vault/projet dédié ;
- token révocable ;
- audit filtrable ;
- documentation d'intégration.

## 10. Gestion des secrets

### Création

La création d'un secret doit :

- authentifier l'acteur ;
- vérifier la permission ;
- valider le vault et le projet ;
- associer un provider ;
- chiffrer la valeur ;
- créer une première version ;
- auditer l'action sans valeur secrète.

### Stockage

Le stockage doit :

- conserver uniquement des valeurs chiffrées ;
- séparer métadonnées et ciphertext ;
- préserver les versions ;
- éviter toute valeur en clair ;
- associer les métadonnées crypto nécessaires.

### Lecture

La lecture doit :

- identifier l'acteur ;
- vérifier l'état du vault ;
- vérifier la permission ;
- charger la version courante ;
- déchiffrer uniquement après autorisation ;
- auditer l'accès ;
- retourner une réponse minimale.

### Rotation

La rotation est partiellement future.

Elle devra :

- créer une nouvelle version ;
- préserver l'audit ;
- éviter la modification en place ;
- permettre une transition contrôlée ;
- révoquer ou déprécier les anciennes versions selon politique.

### Révocation

La révocation doit rendre une version ou un token inutilisable.

Elle devra être :

- explicite ;
- auditée ;
- irréversible sauf mécanisme documenté ;
- claire pour les clients.

### Suppression

La suppression doit distinguer :

- suppression logique ;
- suppression physique ;
- destruction cryptographique.

Au MVP, la suppression doit être prudente et documentée.

### Archivage

L'archivage permet de conserver des métadonnées et événements sans autoriser l'usage normal.

Un vault ou secret archivé ne doit pas être traité comme actif.

### Destruction

La destruction est l'étape où les données deviennent définitivement irrécupérables.

Elle peut être :

- physique, par suppression des ciphertexts ;
- cryptographique, par destruction des clés nécessaires.

Cette capacité doit être conçue avec prudence, car elle peut empêcher toute récupération.

## 11. Sécurité du développement

### Tests

Les tests de sécurité sont obligatoires.

Ils doivent couvrir :

- autorisations accordées ;
- autorisations refusées ;
- absence de permission ;
- séparation metadata/value ;
- lecture avec vault verrouillé ;
- audit des succès ;
- audit des refus ;
- erreurs crypto ;
- validation des entrées ;
- outils MCP critiques ;
- endpoints REST critiques.

### Revues

Les revues doivent évaluer :

- conformité avec la Constitution ;
- respect de l'Architecture ;
- impact sécurité ;
- couverture de tests ;
- documentation ;
- dépendances ajoutées ;
- comportement en cas d'erreur ;
- absence de fuite de secrets.

Les changements d'auth, permission, crypto, audit et MCP doivent être traités comme sensibles.

### Dépendances

Les dépendances doivent être :

- nécessaires ;
- maintenues ;
- réputées ;
- verrouillées ;
- scannées ;
- mises à jour avec prudence.

Toute dépendance crypto doit être particulièrement justifiée.

### CI

La CI doit progressivement inclure :

- tests unitaires ;
- tests d'intégration ;
- lint ;
- type checking ;
- analyse statique ;
- scan de dépendances ;
- détection de secrets ;
- vérification documentation.

### Secrets Git

Le dépôt ne doit jamais contenir :

- clés API ;
- tokens ;
- clés privées ;
- mots de passe ;
- certificats privés ;
- clés maître ;
- dumps contenant des secrets.

Toute fuite dans Git doit être traitée comme un incident de sécurité.

### Lint et analyse statique

Les outils de lint et analyse statique doivent aider à maintenir :

- lisibilité ;
- cohérence ;
- absence d'erreurs simples ;
- détection de patterns dangereux ;
- robustesse des types.

Ils ne remplacent pas les revues humaines.

## 12. Sécurité de production

### Permissions Linux

L'hôte doit appliquer le principe du moindre privilège.

Bonnes pratiques :

- utilisateur système dédié ;
- fichiers de configuration protégés ;
- clé maître non lisible par d'autres utilisateurs ;
- permissions strictes sur volumes ;
- limitation des dumps mémoire si possible.

### Sauvegardes

Les sauvegardes doivent être :

- régulières ;
- protégées ;
- testées ;
- séparées de la clé maître ;
- documentées ;
- restaurables.

Un backup non testé n'est pas une stratégie de récupération.

### Firewall

L'exposition réseau doit être minimale.

Bonnes pratiques :

- PostgreSQL non exposé publiquement ;
- API exposée uniquement si nécessaire ;
- accès administratifs restreints ;
- ports documentés ;
- filtrage réseau.

### HTTPS

En production, les communications externes doivent utiliser HTTPS.

Le projet doit fonctionner derrière un reverse proxy sûr et correctement configuré.

Les secrets ne doivent jamais transiter en clair sur un réseau non fiable.

### Reverse proxy

Le reverse proxy doit gérer :

- TLS ;
- limites de taille ;
- timeouts ;
- headers sûrs ;
- journalisation prudente ;
- éventuellement rate limiting.

Il ne doit pas logger les payloads contenant des secrets.

### Docker

Docker doit être utilisé avec prudence.

Le stack local de développement est orchestré par le `docker-compose.yml` racine. Les Dockerfiles de service vivent dans `backend/Dockerfile` et `frontend/Dockerfile`.

Bonnes pratiques :

- pas de container privilégié ;
- volumes minimaux ;
- réseau restreint ;
- secrets hors image ;
- logs contrôlés ;
- images à jour.

### Monitoring

Le monitoring doit observer :

- disponibilité ;
- erreurs ;
- refus inhabituels ;
- lectures de secrets ;
- usage par acteur ;
- santé PostgreSQL ;
- échecs de déchiffrement.

Le monitoring ne doit pas collecter de valeurs secrètes.

### Rotation

La production doit prévoir :

- rotation des tokens ;
- rotation des clés applicatives ;
- rotation après incident ;
- rotation des credentials PostgreSQL ;
- rotation future des clés cryptographiques.

La rotation doit être documentée avant d'être automatisée.

## 13. Incidents de sécurité

### Détecter

Un incident peut être détecté par :

- audit inhabituel ;
- lecture excessive de secrets ;
- refus répétés ;
- token utilisé depuis un contexte inattendu ;
- échec crypto ;
- fuite détectée dans Git ;
- alerte de dépendance ;
- comportement anormal d'OpenClaw ou d'un agent.

### Contenir

La containment doit viser à limiter immédiatement l'impact.

Actions possibles :

- révoquer un token ;
- verrouiller un vault ;
- couper une interface ;
- isoler le container ;
- restreindre le réseau ;
- stopper OpenClaw ou le client compromis ;
- préserver les logs et événements d'audit.

### Récupérer

La récupération peut impliquer :

- rotation des secrets exposés ;
- restauration depuis backup ;
- génération de nouveaux tokens ;
- correction de configuration ;
- mise à jour de dépendance ;
- déploiement d'un correctif ;
- revue complète des accès.

### Documenter

Tout incident doit être documenté.

La documentation doit inclure :

- date et heure ;
- méthode de détection ;
- systèmes affectés ;
- secrets potentiellement exposés ;
- actions de containment ;
- actions de récupération ;
- cause racine ;
- tests ajoutés ;
- mesures préventives.

Un incident non documenté est une opportunité d'apprentissage perdue.

## 14. Checklist sécurité avant release

Avant chaque release, vérifier :

- [ ] Aucun secret n'est présent dans le dépôt.
- [ ] Aucun secret n'apparaît dans les logs de test.
- [ ] Les tests critiques passent.
- [ ] Les tests de permissions couvrent succès et refus.
- [ ] Les tests MCP critiques passent.
- [ ] Les tests REST critiques passent.
- [ ] Les migrations PostgreSQL sont testées.
- [ ] Les dépendances nouvelles sont justifiées.
- [ ] Les dépendances connues vulnérables sont traitées ou documentées.
- [ ] Les changements d'API sont documentés.
- [ ] Les changements MCP sont documentés.
- [ ] Les changements de permissions sont documentés.
- [ ] Les changements crypto sont revus avec attention.
- [ ] Les erreurs client ne révèlent pas de détails sensibles.
- [ ] L'audit ne contient aucune valeur secrète.
- [ ] Les tokens complets ne sont jamais stockés en clair.
- [ ] Les secrets au repos sont chiffrés.
- [ ] Les permissions sont vérifiées avant déchiffrement.
- [ ] Les refus sont audités lorsque nécessaire.
- [ ] La documentation de sécurité est à jour.

## 15. Ce que MCP Secret Manager ne garantit PAS

MCP Secret Manager fournit une couche de contrôle forte, mais il ne peut pas éliminer tous les risques.

### Client autorisé

Un client autorisé qui reçoit un secret peut le divulguer volontairement ou accidentellement.

MCP Secret Manager peut :

- limiter l'accès ;
- auditer la lecture ;
- réduire la portée ;
- révoquer les accès futurs.

Il ne peut pas contrôler parfaitement ce que le client fait après réception.

### Administrateur root

Un administrateur root sur l'hôte peut compromettre la machine, lire la mémoire du processus, modifier le système ou intercepter des données.

MCP Secret Manager ne prétend pas protéger totalement contre un root malveillant sur le serveur.

### Machine entièrement compromise

Si l'hôte, le runtime, le réseau local, PostgreSQL et la clé maître sont tous compromis, les secrets doivent être considérés comme compromis.

La stratégie correcte est alors :

- containment ;
- rotation ;
- restauration ;
- enquête ;
- durcissement.

### Agents IA après réception du secret

Un agent IA autorisé peut mal utiliser un secret après l'avoir reçu.

Le projet peut réduire ce risque par :

- permissions minimales ;
- réponses limitées ;
- audit ;
- futurs quotas ;
- futures justifications ;
- futurs budgets.

Il ne peut pas garantir qu'un modèle ou orchestrateur externe ne divulguera jamais une valeur qu'il a reçue.

### Sécurité des providers externes

Les futurs providers comme GitHub, OpenAI, Anthropic, Cloudflare, Docker ou AWS auront leurs propres modèles de sécurité.

MCP Secret Manager ne peut pas garantir la sécurité interne de ces fournisseurs.

### Conformité réglementaire automatique

Le projet peut aider à construire une infrastructure plus sûre et plus auditable.

Il ne garantit pas automatiquement une conformité réglementaire spécifique.

### Absence totale de bugs

Aucun logiciel non trivial ne peut garantir l'absence totale de bugs.

La stratégie du projet est de réduire les risques par :

- simplicité ;
- tests ;
- revues ;
- documentation ;
- audit ;
- dépendances prudentes ;
- conception sécurisée.

## Conclusion

MCP Secret Manager doit être construit comme un produit de sécurité sérieux.

Sa promesse n'est pas de rendre les secrets magiquement invulnérables. Sa promesse est de fournir une couche de contrôle claire, stricte, auditable et adaptée aux infrastructures IA modernes.

Le projet doit protéger les secrets au repos, contrôler les accès, limiter les interfaces, auditer les actions sensibles et assumer honnêtement ses limites.

Cette stratégie de sécurité doit guider toutes les futures Pull Requests.
