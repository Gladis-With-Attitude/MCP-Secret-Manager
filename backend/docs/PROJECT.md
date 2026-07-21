# MCP Secret Manager

## Présentation

MCP Secret Manager est un gestionnaire de secrets open source, auto-hébergé, conçu pour les infrastructures IA modernes.

Son rôle est de stocker, protéger, organiser, contrôler et auditer l'accès aux secrets utilisés par des systèmes agentiques, des serveurs MCP, des orchestrateurs d'agents, des applications, des scripts, des containers Docker et des services d'infrastructure.

Le premier consommateur du projet est OpenClaw.

MCP Secret Manager doit devenir le composant de confiance chargé de fournir à OpenClaw et aux futurs agents IA les secrets dont ils ont besoin, au moment où ils en ont besoin, avec le minimum de privilèges possible, une traçabilité complète et une surface d'exposition réduite.

Les secrets concernés incluent notamment :

- clés API ;
- tokens OAuth ;
- clés SSH ;
- mots de passe ;
- certificats ;
- secrets applicatifs ;
- credentials de services ;
- secrets utilisés par des agents IA ou des serveurs MCP.

MCP Secret Manager n'est pas seulement une base chiffrée de secrets. C'est une couche de contrôle entre des acteurs logiciels potentiellement autonomes et des ressources sensibles.

### Pourquoi ce projet existe

Les infrastructures IA personnelles et professionnelles évoluent rapidement vers des architectures composées de multiples agents, outils, serveurs MCP, orchestrateurs, services Docker, scripts d'automatisation et applications web.

Dans ce type d'environnement, les secrets sont souvent dispersés dans :

- fichiers `.env` ;
- variables d'environnement ;
- volumes Docker ;
- fichiers de configuration ;
- scripts locaux ;
- dashboards d'API providers ;
- configurations MCP ;
- prompts ou contextes d'agents ;
- dépôts privés.

Cette dispersion rend difficile :

- l'audit des accès ;
- la rotation des secrets ;
- la révocation rapide ;
- la séparation des responsabilités ;
- la limitation des permissions ;
- la compréhension de quel service utilise quel secret ;
- la protection contre les comportements inattendus d'agents IA.

MCP Secret Manager existe pour centraliser cette responsabilité dans un composant dédié, explicite, auditable et pensé dès le départ pour les usages agentiques.

### Pourquoi ce n'est pas un clone de HashiCorp Vault

MCP Secret Manager s'inspire des bonnes pratiques de l'industrie en matière de gestion de secrets, mais il ne cherche pas à reproduire HashiCorp Vault.

HashiCorp Vault est un produit très puissant, généraliste, conçu pour un grand nombre de scénarios d'entreprise : secrets dynamiques, PKI, cloud, identité, politiques complexes, haute disponibilité, multi-backends et intégrations massives.

MCP Secret Manager poursuit un objectif différent :

- être simple à auto-héberger ;
- être compréhensible par un seul mainteneur ou une petite équipe ;
- être optimisé pour PostgreSQL dès le départ ;
- être utilisable rapidement avec OpenClaw ;
- être MCP-native ;
- fournir une surface claire aux agents IA ;
- privilégier des permissions simples au MVP ;
- évoluer progressivement vers des contrôles plus avancés ;
- éviter la complexité prématurée.

Le projet ne cherche pas à remplacer tous les gestionnaires de secrets existants. Il cherche à devenir le gestionnaire de secrets naturel d'une infrastructure IA personnelle ou semi-professionnelle centrée sur OpenClaw, MCP et les agents.

### Pourquoi il est pensé pour les agents IA

Un agent IA n'est pas un utilisateur classique.

Un agent peut :

- interpréter des instructions ambiguës ;
- appeler des outils ;
- enchaîner plusieurs actions ;
- déléguer à d'autres agents ;
- être influencé par du contenu externe ;
- subir une prompt injection ;
- demander plus d'informations que nécessaire ;
- exposer involontairement des résultats dans des logs, traces ou réponses.

Pour cette raison, un Secret Manager utilisé par des agents doit être conçu différemment.

MCP Secret Manager part du principe qu'un agent ne doit jamais recevoir un accès large à un coffre de secrets. Il doit demander un secret précis, dans un contexte précis, avec une identité précise, et recevoir uniquement ce qui est strictement autorisé.

A terme, le projet devra pouvoir prendre en charge :

- des identités d'agents ;
- des accès à durée de vie courte ;
- des quotas de lecture ;
- des budgets d'utilisation ;
- des justifications de demandes ;
- un audit spécialisé pour les agents ;
- des protections contre les comportements inattendus des LLM ;
- des contrôles adaptés aux orchestrateurs multi-agents.

Toutes ces fonctionnalités ne font pas partie du MVP, mais la conception du projet doit permettre de les accueillir sans refonte fondamentale.

## Vision

### Vision court terme

La vision court terme est de construire un MVP robuste, petit et réellement utilisable.

Le MVP doit permettre à OpenClaw de :

- s'authentifier auprès de MCP Secret Manager ;
- stocker des secrets dans PostgreSQL ;
- organiser ces secrets en vaults et projets ;
- lire un secret précis via API REST ;
- lire un secret précis via MCP ;
- bénéficier d'un chiffrement au repos ;
- bénéficier d'un audit minimal mais fiable ;
- utiliser des rôles et permissions simples.

Le court terme privilégie la clarté, la sécurité et la capacité à livrer rapidement.

Le projet doit éviter les fonctionnalités avancées tant que les fondations ne sont pas solides.

### Vision moyen terme

La vision moyen terme est d'étendre MCP Secret Manager au-delà d'OpenClaw, tout en conservant une architecture simple.

Les priorités moyen terme incluent :

- SDK Python ;
- SDK TypeScript ;
- CLI plus complète ;
- rotation manuelle des secrets ;
- tokens à durée de vie courte ;
- quotas simples ;
- audit enrichi pour agents ;
- sauvegarde et restauration chiffrées ;
- premiers Secret Providers externes ;
- intégration plus profonde avec les serveurs MCP ;
- documentation opérateur complète.

A ce stade, MCP Secret Manager doit pouvoir être utilisé par plusieurs services, plusieurs scripts, plusieurs agents et plusieurs serveurs MCP sans devenir difficile à administrer.

### Vision long terme

La vision long terme est de faire de MCP Secret Manager une couche de confiance pour systèmes agentiques distribués.

Dans cette vision, le projet pourrait fournir :

- des identités d'agents de première classe ;
- des permissions contextuelles avancées ;
- des accès temporaires ;
- des budgets par mission ;
- des approbations humaines ;
- des secrets dynamiques ;
- des intégrations TPM, YubiKey ou HSM ;
- des providers cloud ;
- des contrôles de délégation entre agents ;
- des politiques de sécurité déclaratives ;
- un audit chaîné et exportable ;
- une interface web ;
- des mécanismes de détection d'anomalies ;
- une compatibilité avec de futurs orchestrateurs multi-agents.

L'ambition finale est que les agents puissent travailler efficacement sans jamais disposer de privilèges excessifs.

## Philosophie

### Security First

La sécurité est la raison d'être du projet.

Chaque décision doit être évaluée selon son impact sur :

- la confidentialité des secrets ;
- l'intégrité des données ;
- l'authenticité des acteurs ;
- la traçabilité des accès ;
- la révocation ;
- la réduction de la surface d'attaque.

Une fonctionnalité pratique mais dangereuse doit être refusée, retardée ou redesignée.

Le comportement par défaut doit être restrictif. En cas d'erreur, d'ambiguïté ou de configuration incomplète, le système doit refuser l'accès.

### AI First

MCP Secret Manager est conçu pour des systèmes dans lesquels les agents IA sont des consommateurs importants de secrets.

Cela implique une attention particulière aux demandes indirectes, aux appels d'outils, aux contextes de mission, aux erreurs d'orchestration et aux prompt injections.

Le projet doit considérer les agents comme des acteurs techniques puissants mais potentiellement imprévisibles. Leur accès doit être précis, limité, révocable et audité.

### MCP Native

MCP n'est pas une intégration secondaire.

Le serveur MCP est un composant de première classe du projet. Il doit être conçu avec le même sérieux que l'API REST.

Les outils MCP exposés par le projet doivent être :

- explicites ;
- limités ;
- auditables ;
- cohérents avec le modèle de permissions ;
- adaptés aux agents ;
- incapables de retourner des secrets en masse par défaut.

### OpenClaw First

OpenClaw est le premier consommateur officiel de MCP Secret Manager.

Le MVP doit être pensé pour servir ce cas d'usage avant tous les autres.

Cela signifie que les décisions initiales doivent privilégier :

- une intégration simple avec OpenClaw ;
- un vault dédié OpenClaw ;
- un rôle minimal pour OpenClaw ;
- une lecture fiable de secrets précis ;
- un audit clair des accès OpenClaw ;
- une configuration compatible avec un serveur Debian auto-hébergé.

### Least Privilege

Chaque acteur doit recevoir uniquement les permissions nécessaires à sa tâche.

Lire les métadonnées d'un secret ne doit pas autoriser la lecture de sa valeur.

Administrer un vault ne doit pas nécessairement impliquer l'accès à toutes les valeurs secrètes.

Un service comme OpenClaw ne doit pas recevoir de droits administratifs s'il n'en a pas besoin.

Un agent IA ne doit pas pouvoir lister ou lire des secrets sans demande explicite et permission associée.

### Audit Everything

Toute action sensible doit être auditée.

Le projet doit permettre de répondre à des questions simples :

- qui a demandé ce secret ?
- quand ?
- via quelle interface ?
- avec quel résultat ?
- depuis quel type de client ?
- quelle permission a été évaluée ?
- l'accès a-t-il été autorisé ou refusé ?

L'audit ne doit jamais contenir de valeur secrète.

L'audit est une fonctionnalité de sécurité, pas une fonctionnalité de debug.

### Documentation Before Code

Le projet doit être guidé par sa documentation.

Les décisions importantes doivent être documentées avant d'être implémentées.

La documentation doit expliquer :

- les objectifs ;
- les non-objectifs ;
- les compromis ;
- les limites ;
- les choix technologiques ;
- les invariants de sécurité ;
- les règles de contribution.

Une contribution qui modifie le comportement de sécurité du projet doit mettre à jour la documentation correspondante.

### Simple Before Complex

Le MVP doit rester volontairement petit.

MCP Secret Manager doit éviter la complexité prématurée :

- pas de moteur ABAC dans le MVP ;
- pas de multi-tenant dans le MVP ;
- pas de haute disponibilité dans le MVP ;
- pas d'interface web dans le MVP ;
- pas de plugins complexes dans le MVP ;
- pas de rotation automatique dans le MVP.

La simplicité initiale est une stratégie de sécurité.

Un système plus simple est plus facile à comprendre, tester, auditer et maintenir.

### Extensible By Design

Simple ne signifie pas fermé.

Le projet doit être conçu pour évoluer vers :

- de nouveaux Secret Providers ;
- de nouveaux clients ;
- de nouveaux types d'identités ;
- des permissions plus fines ;
- des politiques avancées ;
- des intégrations cloud ;
- des protections matérielles ;
- des mécanismes spécifiques aux agents.

Les points d'extension doivent être prévus, mais leur implémentation doit rester progressive.

## Objectifs

### Problèmes que le projet cherche à résoudre

MCP Secret Manager cherche à résoudre les problèmes suivants :

- centraliser les secrets d'une infrastructure IA personnelle ;
- éviter la dispersion des secrets dans des fichiers et scripts ;
- fournir un accès sécurisé à OpenClaw ;
- exposer une interface MCP sûre pour agents IA ;
- fournir une API REST claire ;
- stocker les secrets chiffrés dans PostgreSQL ;
- organiser les secrets par vault et projet ;
- séparer métadonnées et valeurs secrètes ;
- contrôler les accès via rôles et permissions ;
- auditer les lectures et modifications sensibles ;
- préparer l'arrivée de Secret Providers ;
- construire une base durable pour des usages agentiques avancés.

### Problèmes que le projet ne cherche pas à résoudre au MVP

Le MVP ne cherche pas à résoudre :

- la haute disponibilité ;
- le multi-tenant d'entreprise ;
- la fédération d'identité complexe ;
- les secrets dynamiques ;
- la rotation automatique ;
- la gestion PKI complète ;
- l'interface web ;
- le remplacement de tous les gestionnaires de secrets existants ;
- le support de tous les clouds ;
- l'intégration HSM obligatoire ;
- l'exécution sécurisée de code agentique ;
- la prévention complète de toute fuite après remise d'un secret à un client autorisé.

MCP Secret Manager peut limiter, tracer et contrôler l'accès à un secret. Il ne peut pas garantir qu'un client autorisé ne divulguera jamais un secret après l'avoir reçu. Cette limite doit rester explicite dans toute la documentation.

## Architecture Générale

MCP Secret Manager est organisé autour de quelques grands composants.

### API REST

L'API REST sert les clients programmatiques, la CLI, OpenClaw et les futurs SDK.

Elle doit être stable, documentée par OpenAPI et conçue pour des appels explicites.

L'API REST ne doit jamais proposer de raccourcis dangereux, comme l'export massif de valeurs secrètes au MVP.

### Serveur MCP

Le serveur MCP expose MCP Secret Manager aux agents IA et orchestrateurs compatibles MCP.

Il fournit des outils limités permettant de consulter des métadonnées ou de demander un secret précis.

Le serveur MCP applique les mêmes règles de sécurité que l'API REST.

### Service d'identité

Le service d'identité représente les acteurs qui interagissent avec le système :

- utilisateurs humains ;
- comptes de service ;
- OpenClaw ;
- futurs agents IA.

Au MVP, l'identité reste simple et centrée sur les utilisateurs administrateurs et comptes de service.

### Service de permissions

Le service de permissions vérifie si un acteur possède la permission nécessaire pour effectuer une action.

Le MVP utilise uniquement des rôles et permissions.

Les politiques contextuelles avancées sont réservées à des versions ultérieures.

### Service de secrets

Le service de secrets gère :

- les vaults ;
- les projets ;
- les secrets ;
- les versions de secrets ;
- les métadonnées ;
- les lectures de valeurs.

Il ne doit jamais contourner le service de permissions ou le service d'audit.

### Service cryptographique

Le service cryptographique est responsable du chiffrement et du déchiffrement des valeurs secrètes.

Il doit être isolé conceptuellement du reste de l'application.

Le reste du système ne doit pas manipuler directement les primitives cryptographiques.

### Service d'audit

Le service d'audit enregistre les actions sensibles.

Il doit être appelé pour les succès comme pour les refus.

Il ne doit jamais recevoir de valeur secrète.

### Secret Providers

Les Secret Providers décrivent l'origine, le format et les capacités futures associées à un secret.

Au MVP, le seul provider requis est un provider local statique.

L'abstraction doit néanmoins préparer l'ajout futur de providers comme GitHub, OpenAI, Anthropic, Cloudflare, Docker, AWS, TPM, YubiKey ou fichiers locaux.

## Technologies Retenues

### PostgreSQL

PostgreSQL est le backend de stockage officiel dès le MVP.

Ce choix est motivé par :

- la fiabilité transactionnelle ;
- la maturité opérationnelle ;
- les contraintes relationnelles ;
- les index performants ;
- les migrations maîtrisées ;
- le support JSONB pour les métadonnées extensibles ;
- la robustesse des sauvegardes ;
- la possibilité future d'ajouter Row-Level Security comme défense supplémentaire.

Le projet ne prévoit pas SQLite pour le MVP.

PostgreSQL doit être considéré comme une dépendance centrale, pas comme un backend interchangeable initialement.

### FastAPI

FastAPI est retenu pour le MVP afin de construire rapidement une API claire, typée et documentée.

Ce choix permet :

- une forte productivité initiale ;
- une intégration naturelle avec Python ;
- une génération OpenAPI native ;
- une bonne ergonomie de développement ;
- une compatibilité avec l'écosystème IA ;
- une vitesse suffisante pour le périmètre MVP.

FastAPI est un choix pragmatique pour démarrer. Il ne doit pas empêcher une évolution future si le projet exige un autre runtime pour certains composants.

### Python

Python est retenu comme langage principal du MVP.

Ce choix correspond au contexte du projet :

- proximité avec l'écosystème IA ;
- intégration naturelle avec OpenClaw ;
- vitesse de développement ;
- simplicité pour les contributeurs ;
- richesse de l'écosystème web, crypto, testing et tooling ;
- facilité à produire ensuite un SDK Python officiel.

Ce choix impose une discipline forte :

- dépendances limitées ;
- typage strict autant que possible ;
- tests systématiques ;
- primitives crypto éprouvées ;
- séparation claire des responsabilités ;
- pas de logique de sécurité implicite.

### Docker

Docker est retenu comme moyen de déploiement et de développement local.

Le projet doit pouvoir être lancé facilement sur une machine Debian auto-hébergée.

Docker doit servir :

- à fournir PostgreSQL en local ;
- à lancer le backend FastAPI en local ;
- à lancer le frontend Next.js en local ;
- à isoler l'environnement de développement ;
- à documenter le déploiement ;
- à faciliter les tests d'intégration ;
- à préparer l'intégration avec d'autres services.

Le workflow local recommandé est le stack Docker Compose racine, composé des services `postgres`, `backend` et `frontend`.

Docker ne remplace pas le durcissement de production. Les configurations de production devront être documentées séparément.

### OpenAPI

OpenAPI est obligatoire pour l'API REST.

Il sert à :

- documenter le contrat public ;
- faciliter les tests ;
- préparer les SDKs ;
- aider les intégrations externes ;
- éviter les comportements implicites.

Toute évolution significative de l'API devra respecter la compatibilité ou être explicitement versionnée.

### AES-256-GCM

AES-256-GCM est retenu comme algorithme de chiffrement authentifié principal pour le MVP.

Ce choix apporte :

- confidentialité ;
- intégrité ;
- authentification des données associées ;
- maturité ;
- support large ;
- compréhension claire par les auditeurs sécurité.

Le projet doit utiliser une bibliothèque éprouvée.

Le projet ne doit jamais implémenter lui-même AES, GCM ou une primitive cryptographique bas niveau.

### MCP

MCP est une interface fondamentale du projet.

Le protocole permet à MCP Secret Manager d'être utilisé par des agents IA et orchestrateurs d'outils de manière standardisée.

Le serveur MCP doit être pensé comme une surface de sécurité majeure :

- outils limités ;
- permissions vérifiées ;
- réponses minimales ;
- audit systématique ;
- compatibilité avec les futures identités d'agents.

## MVP

Le MVP doit être volontairement limité.

Son objectif n'est pas d'être complet. Son objectif est d'être sûr, compréhensible, testable et utile à OpenClaw.

### Inclus dans le MVP

Le MVP inclut :

- PostgreSQL comme stockage unique ;
- FastAPI comme API REST ;
- Python comme langage principal ;
- Docker pour le développement et le déploiement local ;
- vaults ;
- projets ;
- secrets ;
- versions immuables de secrets ;
- provider local statique ;
- chiffrement AES-256-GCM ;
- rôles ;
- permissions ;
- comptes de service ;
- token d'accès pour OpenClaw ;
- audit des actions sensibles ;
- serveur MCP minimal ;
- CLI administrative minimale ;
- documentation de référence ;
- documentation d'installation locale ;
- tests unitaires et d'intégration essentiels.

### Exclu du MVP

Le MVP exclut volontairement :

- multi-tenant Organization ;
- ABAC ;
- moteur de policies avancé ;
- interface web ;
- rotation automatique ;
- secrets dynamiques ;
- haute disponibilité ;
- HSM ;
- TPM ;
- YubiKey ;
- intégrations cloud ;
- approbation humaine ;
- budgets agents ;
- quotas agents ;
- analyse comportementale ;
- export SIEM ;
- SDK TypeScript ;
- SDK Python complet ;
- providers externes complets.

Ces exclusions sont des décisions de design, pas des oublis.

Le MVP doit rester assez petit pour être construit correctement.

## Roadmap

### Phase 1 - Documentation et fondations

Objectif : établir la source de vérité du projet.

Livrables :

- document projet ;
- architecture technique ;
- threat model ;
- conventions de contribution ;
- périmètre MVP ;
- décisions technologiques.

### Phase 2 - MVP OpenClaw

Objectif : permettre à OpenClaw d'utiliser MCP Secret Manager en local.

Livrables :

- API REST minimale ;
- PostgreSQL ;
- chiffrement au repos ;
- rôles et permissions ;
- audit ;
- CLI minimale ;
- serveur MCP minimal ;
- scénario OpenClaw documenté et testé.

### Phase 3 - Expérience développeur

Objectif : rendre le projet agréable à utiliser et contribuer.

Livrables :

- documentation d'installation ;
- documentation API ;
- exemples ;
- tests plus complets ;
- packaging Docker ;
- premiers guides d'intégration.

### Phase 4 - Capacités agents

Objectif : enrichir les contrôles adaptés aux agents IA.

Livrables possibles :

- identités d'agents ;
- justifications de demandes ;
- quotas de lecture ;
- tokens courts ;
- audit agentique ;
- limitations par outil MCP ;
- premiers budgets d'utilisation.

### Phase 5 - Secret Providers

Objectif : connecter MCP Secret Manager à des écosystèmes externes.

Livrables possibles :

- provider GitHub ;
- provider OpenAI ;
- provider Anthropic ;
- provider Cloudflare ;
- provider Docker ;
- provider fichiers locaux ;
- validation et rotation assistée.

### Phase 6 - Durcissement long terme

Objectif : faire évoluer le projet vers une infrastructure de confiance durable.

Livrables possibles :

- sauvegardes chiffrées avancées ;
- restauration testée ;
- rotation des clés ;
- policies avancées ;
- intégration TPM/YubiKey/HSM ;
- audit chaîné ;
- interface web ;
- intégration multi-agents.

## Qualité

### Tests

Le projet doit être testé dès le début.

Les tests doivent couvrir au minimum :

- permissions autorisées ;
- permissions refusées ;
- séparation metadata/value ;
- chiffrement et déchiffrement ;
- erreurs de déchiffrement ;
- audit des succès ;
- audit des refus ;
- endpoints critiques ;
- outils MCP critiques ;
- migrations PostgreSQL.

Les tests de sécurité ne doivent pas être reportés à la fin.

Toute correction de bug de sécurité doit ajouter un test de non-régression.

### Documentation

La documentation est une partie du produit.

Elle doit rester :

- claire ;
- à jour ;
- versionnée ;
- lisible par un nouveau contributeur ;
- explicite sur les compromis ;
- honnête sur les limites.

Toute fonctionnalité publique doit être documentée.

Toute décision de sécurité importante doit être documentée.

### Sécurité

Les exigences minimales de sécurité sont :

- aucun secret en clair au repos ;
- aucune valeur secrète dans les logs ;
- refus par défaut ;
- permissions explicites ;
- audit des accès sensibles ;
- dépendances surveillées ;
- primitives crypto éprouvées ;
- séparation des responsabilités ;
- erreurs sûres ;
- configuration de production documentée.

Les raccourcis de développement ne doivent pas devenir des comportements de production.

### Revues de code

Toute contribution significative doit être revue.

Les revues doivent vérifier :

- la cohérence avec ce document ;
- l'impact sécurité ;
- les tests ;
- la documentation ;
- la lisibilité ;
- la compatibilité avec le MVP ou la roadmap ;
- l'absence de complexité inutile.

Les changements liés à l'authentification, aux permissions, à la crypto ou à l'audit doivent recevoir une attention particulière.

### Rétrocompatibilité

Le projet doit préserver autant que possible :

- les schémas de données ;
- les contrats API ;
- les formats d'audit ;
- les configurations ;
- les comportements de sécurité documentés.

Quand une rupture est nécessaire, elle doit être :

- justifiée ;
- documentée ;
- versionnée ;
- accompagnée d'un chemin de migration.

La sécurité prime sur la rétrocompatibilité lorsqu'un comportement existant est dangereux.

## Contribution

MCP Secret Manager est un projet open source professionnel.

Les contributeurs doivent respecter les règles suivantes.

### Respecter la vision

Toute contribution doit rester alignée avec :

- Security First ;
- AI First ;
- MCP Native ;
- OpenClaw First ;
- Least Privilege ;
- Audit Everything ;
- Documentation Before Code ;
- Simple Before Complex ;
- Extensible By Design.

Une contribution techniquement correcte peut être refusée si elle pousse le projet dans une direction contraire à sa philosophie.

### Commencer par le problème

Avant d'ajouter une fonctionnalité, il faut expliquer le problème résolu.

Le projet doit éviter les fonctionnalités ajoutées parce qu'elles sont possibles, mais pas nécessaires.

### Garder les changements petits

Les contributions doivent être petites, testables et faciles à relire.

Une pull request doit idéalement :

- résoudre un seul problème ;
- contenir ses tests ;
- mettre à jour la documentation ;
- éviter les refactorings non liés ;
- être fusionnable indépendamment.

### Ne pas affaiblir les garanties de sécurité

Une contribution ne doit pas :

- logger des secrets ;
- contourner les permissions ;
- mélanger metadata et valeur secrète ;
- introduire un accès large non justifié ;
- désactiver l'audit ;
- ajouter une dépendance crypto non éprouvée ;
- rendre un refus silencieusement permissif.

### Documenter les décisions

Les décisions structurantes doivent être documentées.

Cela inclut :

- nouveaux composants ;
- nouveaux providers ;
- nouveaux modèles de permissions ;
- nouvelles surfaces publiques ;
- changements de chiffrement ;
- changements de stockage ;
- changements MCP.

### Penser aux agents IA

Toute nouvelle surface d'accès doit être évaluée selon son usage possible par un agent IA.

Questions à poser :

- un agent peut-il obtenir plus que nécessaire ?
- la réponse est-elle trop large ?
- l'action est-elle auditée ?
- la permission est-elle explicite ?
- l'outil peut-il être abusé par prompt injection ?
- peut-on limiter la portée de la demande ?

## Vision Finale

Dans plusieurs années, MCP Secret Manager pourrait devenir une couche de confiance spécialisée pour les infrastructures agentiques.

Il pourrait permettre à des utilisateurs de définir des missions, des agents, des budgets, des permissions et des secrets de manière cohérente.

Un orchestrateur multi-agent pourrait demander :

- quel agent peut utiliser quel secret ;
- pour quelle mission ;
- pendant combien de temps ;
- avec quel budget ;
- avec quelle justification ;
- sous quelle supervision ;
- avec quel niveau d'audit.

MCP Secret Manager pourrait également fournir des mécanismes avancés comme :

- secrets utilisables sans révélation directe ;
- signatures via clés protégées ;
- chiffrement via TPM ou YubiKey ;
- rotation assistée par provider ;
- approbations humaines ;
- révocation coordonnée ;
- détection de comportements anormaux ;
- politique de moindre privilège adaptée aux agents ;
- audit cryptographiquement vérifiable.

La vision finale n'est pas de construire le plus gros gestionnaire de secrets possible.

La vision finale est de construire le gestionnaire de secrets le plus approprié pour une infrastructure IA personnelle, modulaire, auditable et durable.

MCP Secret Manager doit rester compréhensible, sûr et extensible.

Il doit aider les agents à travailler sans leur donner les clés de toute l'infrastructure.

Il doit permettre à OpenClaw, aux serveurs MCP, aux scripts, aux applications et aux futurs orchestrateurs d'accéder aux secrets avec précision, responsabilité et confiance.
