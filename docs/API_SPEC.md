# Spécification fonctionnelle de l'API REST

Ce document définit le contrat fonctionnel officiel de l'API REST de MCP Secret Manager.

Il décrit les ressources exposées, les opérations autorisées, les permissions attendues, les garanties de sécurité, le modèle d'erreurs et les invariants.

Ce document ne contient pas de code, pas de route FastAPI, pas de modèle Pydantic et pas de schéma OpenAPI. Il décrit ce que l'API doit exposer, indépendamment de son implémentation.

## 1. Objectifs

### Pourquoi une API REST

L'API REST fournit une interface stable, explicite et interopérable pour interagir avec MCP Secret Manager.

Elle doit permettre à des clients humains et machines de :

- administrer des vaults ;
- organiser des projets ;
- créer et gérer des secrets ;
- lire des métadonnées ;
- lire une valeur secrète précise ;
- gérer les tokens ;
- consulter l'audit ;
- vérifier l'état de santé du service.

L'API REST est une interface de première classe, mais elle ne porte pas la logique métier. Elle appelle l'Application Layer, qui applique les règles de permission, d'audit, de crypto et de domaine.

### Clients attendus

Les clients attendus sont :

- OpenClaw ;
- CLI officielle ;
- scripts d'administration ;
- services internes ;
- applications web futures ;
- SDK Python futur ;
- SDK TypeScript futur ;
- outils de test et d'intégration ;
- orchestrateurs ou systèmes qui ne passent pas par MCP.

OpenClaw est le premier client prioritaire du MVP.

### Garanties de l'API

L'API REST garantit :

- versionnement explicite ;
- authentification des actions sensibles ;
- autorisation explicite ;
- séparation metadata/value ;
- erreurs prévisibles ;
- réponses stables ;
- audit des opérations sensibles ;
- absence de secret dans les erreurs ;
- absence de lecture bulk de valeurs au MVP ;
- refus par défaut.

## 2. Principes

### Resource-oriented

L'API est orientée ressources.

Les concepts principaux du domaine sont exposés comme ressources :

- vaults ;
- projects ;
- secrets ;
- versions ;
- tokens ;
- actors ;
- roles ;
- permissions ;
- audit events.

Les routes doivent représenter des ressources et actions explicites, pas des fonctions ambiguës.

### Stateless

Chaque requête doit contenir le contexte nécessaire à son authentification.

Le serveur ne doit pas dépendre d'une session HTTP implicite pour les clients machine du MVP.

Conséquences :

- les tokens portent l'authentification ;
- les permissions sont évaluées à chaque requête sensible ;
- une requête doit pouvoir être auditée indépendamment ;
- aucun état client implicite ne doit accorder de privilèges.

### Explicit Authorization

Chaque opération sensible correspond à une permission explicite.

Exemples :

- lire un vault nécessite `vault.read` ;
- créer un secret nécessite `secret.create` ;
- lire une valeur secrète nécessite `secret.value.read` ;
- lire l'audit nécessite `audit.read`.

La lecture de métadonnées et la lecture de valeur sont deux opérations différentes.

### Least Privilege

L'API ne doit pas forcer les clients à demander plus de permissions que nécessaire.

Conséquences :

- endpoints metadata séparés des endpoints value ;
- tokens de service limités ;
- pas d'export massif au MVP ;
- OpenClaw utilise uniquement les permissions nécessaires ;
- les réponses ne contiennent pas de données non demandées.

### Predictable Errors

Les erreurs doivent être stables, compréhensibles et sûres.

Un client doit pouvoir distinguer :

- erreur de validation ;
- erreur d'authentification ;
- refus d'autorisation ;
- ressource introuvable ;
- conflit métier ;
- erreur crypto ;
- erreur interne.

Les erreurs ne doivent jamais révéler de secret, token complet, clé ou détail interne dangereux.

### Stable Contracts

Le contrat public doit rester stable.

Les clients comme OpenClaw, la CLI et les futurs SDKs doivent pouvoir dépendre de l'API sans rupture imprévisible.

Toute rupture doit être :

- justifiée ;
- documentée ;
- versionnée si possible ;
- accompagnée d'un chemin de migration.

### Versioning Strategy

L'API utilise un préfixe de version.

Le MVP expose conceptuellement :

```text
/v1
```

Les changements compatibles peuvent rester dans la même version.

Les changements incompatibles doivent être introduits dans une nouvelle version majeure, par exemple :

```text
/v2
```

La sécurité prime sur la compatibilité lorsqu'une rupture corrige un comportement dangereux.

## 3. Authentification

L'authentification identifie l'acteur qui effectue la requête.

Le MVP repose sur des tokens associés à des acteurs.

Les détails internes de génération, stockage et validation des tokens appartiennent à l'implémentation et à la documentation sécurité. Ce document définit seulement le contrat fonctionnel.

### Admin

L'Admin est un utilisateur humain ayant des permissions d'administration.

Il peut typiquement :

- créer des vaults ;
- créer des projets ;
- gérer des secrets ;
- créer des comptes de service ;
- gérer les rôles ;
- consulter l'audit ;
- révoquer des tokens.

L'Admin n'est pas exempté d'audit.

### Service Account

Un Service Account représente un client technique.

Exemples :

- OpenClaw ;
- application interne ;
- script d'automatisation ;
- container Docker ;
- serveur MCP.

Un Service Account s'authentifie avec un token révocable et reçoit des rôles explicites.

### OpenClaw

OpenClaw utilise un Service Account dédié.

Garanties attendues :

- identité distincte ;
- rôle minimal ;
- token révocable ;
- audit filtrable ;
- accès limité aux vaults, projets et secrets nécessaires.

OpenClaw ne doit pas utiliser un token admin pour son fonctionnement normal.

## 4. Ressources exposées

### Vault

Rôle :

Frontière logique et cryptographique principale.

Opérations autorisées :

- lister ;
- créer ;
- consulter ;
- modifier les métadonnées ;
- verrouiller ;
- archiver.

Permissions typiques :

- `vault.read` ;
- `vault.create` ;
- `vault.update` ;
- `vault.lock` ;
- `vault.archive`.

### Project

Rôle :

Regroupement logique de secrets dans un vault.

Opérations autorisées :

- lister dans un vault ;
- créer ;
- consulter ;
- modifier les métadonnées ;
- archiver.

Permissions typiques :

- `project.read` ;
- `project.create` ;
- `project.update` ;
- `project.archive`.

### Secret

Rôle :

Identité logique d'un secret.

Opérations autorisées :

- créer ;
- lister les métadonnées ;
- consulter les métadonnées ;
- modifier les métadonnées ;
- lire la valeur courante ;
- archiver ;
- supprimer logiquement.

Permissions typiques :

- `secret.create` ;
- `secret.metadata.read` ;
- `secret.metadata.list` ;
- `secret.update` ;
- `secret.value.read` ;
- `secret.archive` ;
- `secret.delete`.

### SecretVersion

Rôle :

Version immuable chiffrée d'un secret.

Opérations autorisées :

- ajouter une nouvelle version ;
- lister les versions metadata-only ;
- consulter les métadonnées d'une version ;
- lire une version si autorisée et non révoquée ;
- révoquer une version future.

Permissions typiques :

- `secret.version.create` ;
- `secret.version.read` ;
- `secret.value.read` ;
- `secret.version.revoke`.

### Token

Rôle :

Credential révocable associé à un acteur.

Opérations autorisées :

- créer ;
- lister les métadonnées ;
- révoquer ;
- consulter l'état.

Permissions typiques :

- `token.create` ;
- `token.read` ;
- `token.revoke`.

Un token complet n'est jamais retourné après sa création initiale.

### Actor

Rôle :

Identité capable d'agir dans le système.

Opérations autorisées :

- lister ;
- consulter ;
- créer selon type ;
- désactiver ;
- associer des rôles.

Permissions typiques :

- `actor.read` ;
- `actor.create` ;
- `actor.disable` ;
- `actor.role.assign`.

### Role

Rôle :

Groupe de permissions.

Opérations autorisées :

- lister ;
- consulter ;
- créer ;
- modifier ;
- associer à un acteur.

Permissions typiques :

- `role.read` ;
- `role.create` ;
- `role.update` ;
- `actor.role.assign`.

### Permission

Rôle :

Action atomique autorisable.

Opérations autorisées :

- lister ;
- consulter.

Permissions typiques :

- `permission.read`.

Au MVP, les permissions sont principalement définies par le système.

### AuditEvent

Rôle :

Trace d'une opération sensible.

Opérations autorisées :

- lister ;
- filtrer ;
- consulter.

Permissions typiques :

- `audit.read`.

AuditEvent ne contient jamais de valeur secrète.

### Health

Rôle :

État de santé technique du service.

Opérations autorisées :

- vérifier que le service répond ;
- vérifier que les dépendances critiques sont disponibles selon niveau d'exposition.

Permissions typiques :

- health public minimal possible ;
- health détaillé réservé à une permission administrative future.

Health ne doit jamais exposer de secret, token ou configuration sensible.

## 5. Endpoints conceptuels

Les endpoints ci-dessous décrivent le contrat conceptuel de l'API.

Les noms exacts, payloads et réponses détaillées seront formalisés dans OpenAPI au moment de l'implémentation, en respectant cette spécification.

### Health

#### GET /v1/health

Objectif :

Indiquer que le service est vivant.

Permission :

Peut être public si la réponse reste minimale.

Résultat attendu :

Statut de disponibilité minimal.

#### GET /v1/health/ready

Objectif :

Indiquer que le service est prêt à traiter des requêtes.

Permission :

Accès restreint ou réponse minimale selon configuration.

Résultat attendu :

Statut de disponibilité des dépendances critiques sans détail sensible.

### Auth et tokens

#### POST /v1/tokens

Objectif :

Créer un token pour un acteur autorisé.

Permission :

`token.create`.

Résultat attendu :

Token complet retourné uniquement au moment de la création, avec ses métadonnées.

#### GET /v1/tokens

Objectif :

Lister les métadonnées des tokens accessibles.

Permission :

`token.read`.

Résultat attendu :

Liste paginée sans token complet.

#### GET /v1/tokens/{id}

Objectif :

Consulter les métadonnées d'un token.

Permission :

`token.read`.

Résultat attendu :

Métadonnées du token, jamais sa valeur complète.

#### POST /v1/tokens/{id}/revoke

Objectif :

Révoquer un token.

Permission :

`token.revoke`.

Résultat attendu :

Token marqué comme révoqué. L'opération doit être idempotente.

### Vaults

#### GET /v1/vaults

Objectif :

Lister les vaults visibles par l'acteur.

Permission :

`vault.read`.

Résultat attendu :

Liste paginée de métadonnées de vaults.

#### POST /v1/vaults

Objectif :

Créer un vault.

Permission :

`vault.create`.

Résultat attendu :

Vault créé avec état initial valide.

#### GET /v1/vaults/{id}

Objectif :

Consulter les métadonnées d'un vault.

Permission :

`vault.read`.

Résultat attendu :

Métadonnées du vault.

#### PATCH /v1/vaults/{id}

Objectif :

Modifier les métadonnées non sensibles d'un vault.

Permission :

`vault.update`.

Résultat attendu :

Vault mis à jour.

#### POST /v1/vaults/{id}/lock

Objectif :

Verrouiller un vault.

Permission :

`vault.lock`.

Résultat attendu :

Le vault refuse les lectures de valeurs secrètes.

#### POST /v1/vaults/{id}/archive

Objectif :

Archiver un vault.

Permission :

`vault.archive`.

Résultat attendu :

Le vault quitte l'usage normal.

### Projects

#### GET /v1/vaults/{vault_id}/projects

Objectif :

Lister les projets d'un vault.

Permission :

`project.read`.

Résultat attendu :

Liste paginée de projets.

#### POST /v1/vaults/{vault_id}/projects

Objectif :

Créer un projet dans un vault.

Permission :

`project.create`.

Résultat attendu :

Projet créé dans le vault.

#### GET /v1/projects/{id}

Objectif :

Consulter les métadonnées d'un projet.

Permission :

`project.read`.

Résultat attendu :

Métadonnées du projet.

#### PATCH /v1/projects/{id}

Objectif :

Modifier les métadonnées d'un projet.

Permission :

`project.update`.

Résultat attendu :

Projet mis à jour.

#### POST /v1/projects/{id}/archive

Objectif :

Archiver un projet.

Permission :

`project.archive`.

Résultat attendu :

Projet retiré de l'usage normal.

### Secrets

#### GET /v1/projects/{project_id}/secrets

Objectif :

Lister les métadonnées des secrets d'un projet.

Permission :

`secret.metadata.list` ou `secret.metadata.read`.

Résultat attendu :

Liste paginée de métadonnées, sans valeur secrète.

#### POST /v1/projects/{project_id}/secrets

Objectif :

Créer un secret et sa première version.

Permission :

`secret.create`.

Résultat attendu :

Secret créé avec version initiale chiffrée. La valeur n'est pas retournée par défaut.

#### GET /v1/secrets/{id}

Objectif :

Consulter les métadonnées d'un secret.

Permission :

`secret.metadata.read`.

Résultat attendu :

Métadonnées du secret, sans valeur.

#### PATCH /v1/secrets/{id}

Objectif :

Modifier les métadonnées du secret.

Permission :

`secret.update`.

Résultat attendu :

Métadonnées mises à jour. Aucune version n'est modifiée.

#### GET /v1/secrets/{id}/value

Objectif :

Lire la valeur courante d'un secret précis.

Permission :

`secret.value.read`.

Résultat attendu :

Valeur secrète minimale retournée uniquement si autorisée.

#### POST /v1/secrets/{id}/archive

Objectif :

Archiver un secret.

Permission :

`secret.archive`.

Résultat attendu :

Secret retiré de l'usage normal.

#### DELETE /v1/secrets/{id}

Objectif :

Effectuer une suppression logique du secret.

Permission :

`secret.delete`.

Résultat attendu :

Secret marqué comme supprimé selon politique MVP.

### Secret versions

#### GET /v1/secrets/{secret_id}/versions

Objectif :

Lister les versions d'un secret en metadata-only.

Permission :

`secret.version.read`.

Résultat attendu :

Liste paginée des versions sans valeur secrète.

#### POST /v1/secrets/{secret_id}/versions

Objectif :

Ajouter une nouvelle version de valeur secrète.

Permission :

`secret.version.create`.

Résultat attendu :

Nouvelle version immuable créée et potentiellement définie comme courante.

#### GET /v1/secrets/{secret_id}/versions/{version_id}

Objectif :

Consulter les métadonnées d'une version.

Permission :

`secret.version.read`.

Résultat attendu :

Métadonnées de version, sans valeur.

#### GET /v1/secrets/{secret_id}/versions/{version_id}/value

Objectif :

Lire une version précise si autorisée.

Permission :

`secret.value.read`.

Résultat attendu :

Valeur de la version demandée si elle est lisible et autorisée.

### Actors

#### GET /v1/actors

Objectif :

Lister les acteurs visibles.

Permission :

`actor.read`.

Résultat attendu :

Liste paginée d'acteurs.

#### POST /v1/actors

Objectif :

Créer un acteur humain ou technique selon périmètre MVP.

Permission :

`actor.create`.

Résultat attendu :

Acteur créé.

#### GET /v1/actors/{id}

Objectif :

Consulter un acteur.

Permission :

`actor.read`.

Résultat attendu :

Métadonnées de l'acteur.

#### POST /v1/actors/{id}/disable

Objectif :

Désactiver un acteur.

Permission :

`actor.disable`.

Résultat attendu :

Acteur désactivé et incapable de nouvelles authentifications.

### Roles et permissions

#### GET /v1/roles

Objectif :

Lister les rôles.

Permission :

`role.read`.

Résultat attendu :

Liste paginée des rôles.

#### POST /v1/roles

Objectif :

Créer un rôle.

Permission :

`role.create`.

Résultat attendu :

Rôle créé.

#### GET /v1/roles/{id}

Objectif :

Consulter un rôle.

Permission :

`role.read`.

Résultat attendu :

Rôle et permissions associées.

#### PATCH /v1/roles/{id}

Objectif :

Modifier un rôle.

Permission :

`role.update`.

Résultat attendu :

Rôle mis à jour.

#### POST /v1/actors/{actor_id}/roles/{role_id}

Objectif :

Attribuer un rôle à un acteur.

Permission :

`actor.role.assign`.

Résultat attendu :

Association acteur/rôle créée. L'opération doit être idempotente.

#### DELETE /v1/actors/{actor_id}/roles/{role_id}

Objectif :

Retirer un rôle d'un acteur.

Permission :

`actor.role.revoke`.

Résultat attendu :

Association acteur/rôle retirée ou révoquée.

#### GET /v1/permissions

Objectif :

Lister les permissions connues du système.

Permission :

`permission.read`.

Résultat attendu :

Liste des permissions documentées.

### Audit

#### GET /v1/audit/events

Objectif :

Lister les événements d'audit filtrables.

Permission :

`audit.read`.

Résultat attendu :

Liste paginée d'événements d'audit sans valeur secrète.

#### GET /v1/audit/events/{id}

Objectif :

Consulter un événement d'audit.

Permission :

`audit.read`.

Résultat attendu :

Détail de l'événement sans valeur secrète.

## 6. Modèle d'erreurs

### Validation

Une erreur de validation indique que la requête est mal formée ou viole le contrat attendu.

Garanties :

- aucune action sensible n'est exécutée ;
- aucun secret n'est retourné ;
- l'erreur est compréhensible ;
- les détails restent sûrs.

### Authentication

Une erreur d'authentification indique que l'identité n'a pas pu être établie.

Garanties :

- aucune ressource sensible n'est révélée ;
- le token complet n'est jamais retourné ;
- la réponse ne permet pas de distinguer inutilement des états internes.

### Authorization

Une erreur d'autorisation indique que l'identité est connue mais n'a pas la permission.

Garanties :

- aucun déchiffrement n'a lieu ;
- le refus est auditable lorsque pertinent ;
- la réponse ne révèle pas de valeur secrète ;
- les détails de permission restent sûrs.

### Not Found

Une erreur Not Found indique qu'une ressource n'est pas accessible ou n'existe pas.

Garanties :

- l'API peut masquer l'existence d'une ressource si nécessaire pour éviter l'énumération ;
- aucune valeur secrète n'est révélée ;
- la réponse reste stable.

### Conflict

Une erreur Conflict indique un conflit métier.

Exemples :

- nom déjà utilisé ;
- état de vault incompatible ;
- tentative de modifier une version immuable ;
- token déjà révoqué selon sémantique non-idempotente.

Garanties :

- l'état reste cohérent ;
- aucune valeur secrète n'est révélée.

### Crypto

Une erreur Crypto indique un échec cryptographique.

Exemples :

- échec de déchiffrement ;
- intégrité invalide ;
- clé indisponible ;
- algorithme non supporté.

Garanties :

- aucune valeur partielle n'est retournée ;
- l'événement est traité comme sensible ;
- les détails exposés au client sont minimaux ;
- l'audit ou les logs de sécurité ne contiennent pas de secret.

### Internal

Une erreur Internal indique un échec inattendu.

Garanties :

- réponse générique ;
- pas de stacktrace en production ;
- pas de secret dans l'erreur ;
- journalisation interne prudente ;
- audit si l'action était sensible.

## 7. Pagination

Toutes les routes de liste doivent être paginées.

Ressources concernées :

- vaults ;
- projects ;
- secrets ;
- versions ;
- actors ;
- roles ;
- tokens ;
- audit events.

Principes :

- taille par défaut raisonnable ;
- taille maximale imposée ;
- ordre stable ;
- pagination compatible avec filtrage ;
- pas de liste non bornée ;
- pas de bulk values.

La pagination doit éviter qu'un client puisse provoquer une charge excessive ou extraire trop d'informations en une seule requête.

## 8. Filtrage

Le filtrage doit être explicite et sûr.

Filtres MVP possibles :

- par vault ;
- par project ;
- par path de secret ;
- par provider ;
- par acteur ;
- par action ;
- par décision ;
- par période ;
- par état.

Le filtrage ne doit jamais contourner les permissions.

Un client ne doit voir que les ressources pour lesquelles il possède la permission applicable.

Pour l'audit, les filtres doivent aider l'investigation sans exposer de valeurs secrètes.

## 9. Idempotence

L'idempotence réduit les effets indésirables lors de retries réseau.

### Opérations qui doivent être idempotentes

Doivent être idempotentes :

- révocation de token ;
- verrouillage de vault ;
- archivage de vault ;
- archivage de project ;
- archivage de secret ;
- attribution d'un rôle déjà présent ;
- retrait d'un rôle déjà absent selon politique ;
- suppression logique déjà appliquée.

### Opérations qui peuvent utiliser une clé d'idempotence

Devraient pouvoir utiliser une stratégie d'idempotence :

- création de vault ;
- création de project ;
- création de secret ;
- ajout de version ;
- création de token.

L'idempotence ne doit pas masquer une incohérence métier.

### Opérations non idempotentes par nature

Certaines opérations créent volontairement un nouvel état :

- ajout d'une nouvelle SecretVersion ;
- création d'un nouveau token ;
- rotation de valeur.

Ces opérations doivent être protégées contre les retries accidentels par une stratégie explicite.

## 10. Audit

### Routes générant un AuditEvent

Doivent générer un AuditEvent :

- création de token ;
- révocation de token ;
- création de vault ;
- modification de vault ;
- verrouillage de vault ;
- archivage de vault ;
- création de project ;
- modification de project ;
- archivage de project ;
- création de secret ;
- modification de metadata secret ;
- lecture de valeur secrète ;
- ajout de SecretVersion ;
- lecture de version value ;
- archivage ou suppression logique de secret ;
- création ou modification de rôle ;
- attribution ou révocation de rôle ;
- désactivation d'acteur ;
- refus de permission sur action sensible ;
- erreur crypto significative.

### Routes pouvant générer un AuditEvent selon configuration

Peuvent générer un AuditEvent :

- lecture de métadonnées de vault ;
- lecture de métadonnées project ;
- lecture de métadonnées secret ;
- liste de secrets ;
- consultation d'audit.

### Routes ne devant jamais auditer de secret

Aucune route ne doit écrire dans AuditEvent :

- valeur secrète ;
- token complet ;
- clé ;
- payload brut sensible ;
- ciphertext inutilement exposé.

## 11. Invariants

Les garanties suivantes doivent toujours rester vraies :

- l'API REST ne contourne jamais l'Application Layer ;
- l'API REST ne parle jamais directement à PostgreSQL pour une opération métier ;
- l'API REST ne déclenche jamais directement le déchiffrement ;
- une lecture de valeur vérifie toujours les permissions ;
- une lecture de valeur vérifie toujours l'état du vault ;
- une lecture de valeur est auditée ;
- une lecture de métadonnées ne révèle jamais la valeur ;
- une liste de secrets ne retourne jamais les valeurs ;
- un endpoint de token ne retourne jamais un token complet sauf lors de sa création ;
- un token révoqué ne permet plus l'authentification ;
- OpenClaw n'utilise pas de token admin pour le fonctionnement normal ;
- une permission absente équivaut à un refus ;
- une erreur d'autorisation ne déclenche jamais de déchiffrement ;
- une erreur crypto ne retourne jamais de valeur partielle ;
- les erreurs ne révèlent jamais de secret ;
- les erreurs ne révèlent jamais de token complet ;
- les erreurs ne révèlent jamais de clé ;
- les erreurs internes ne retournent pas de stacktrace en production ;
- les routes de liste sont paginées ;
- aucune route MVP ne propose de bulk read de valeurs secrètes ;
- les filtres ne contournent jamais les permissions ;
- les réponses sont minimales par défaut ;
- les actions sensibles produisent un audit ;
- AuditEvent ne contient jamais de valeur secrète ;
- AuditEvent ne contient jamais de token complet ;
- les endpoints REST et MCP partagent les mêmes cas d'usage ;
- REST ne dépend pas de MCP ;
- MCP ne dépend pas de REST ;
- les mutations sensibles vérifient les permissions avant modification ;
- la création de secret ne retourne pas la valeur par défaut ;
- la modification des métadonnées d'un secret ne modifie pas ses versions ;
- l'ajout d'une version ne modifie pas une version existante ;
- une SecretVersion existante reste immuable ;
- verrouiller un vault empêche les lectures de valeur ;
- archiver une ressource la retire de l'usage normal ;
- les routes health ne révèlent pas de configuration sensible ;
- les contrats publics sont versionnés ;
- les ruptures de contrat sont documentées ;
- la sécurité prime sur la rétrocompatibilité en cas de conflit.

## 12. Évolutions futures

### API v2

Une API v2 pourra être introduite pour des changements incompatibles.

Exemples :

- nouveau modèle de permissions ;
- ABAC ;
- nouveau modèle agentique ;
- changements structurants des réponses ;
- nouveaux mécanismes de tokens ;
- refonte des endpoints providers.

Une API v2 ne doit pas être créée pour de simples ajouts compatibles.

### Batch Operations

Les opérations batch pourront être utiles pour l'administration.

Exemples :

- créer plusieurs secrets ;
- archiver plusieurs ressources ;
- attribuer plusieurs rôles ;
- importer des métadonnées.

Contraintes futures :

- pas de bulk read de valeurs par défaut ;
- permissions évaluées par élément ;
- audit adapté ;
- limites de taille strictes ;
- erreurs partielles documentées.

### Long-running Operations

Certaines opérations futures pourront être longues.

Exemples :

- rotation massive ;
- rewrap de clés ;
- backup ;
- restauration ;
- import ;
- provider sync.

Elles pourront nécessiter :

- ressource Operation ;
- statut ;
- progression ;
- audit ;
- annulation contrôlée ;
- reprise.

### Streaming

Le streaming n'est pas prévu pour le MVP.

Usages futurs possibles :

- export d'audit ;
- suivi d'opération longue ;
- logs de rotation sans secret ;
- événements de monitoring.

Le streaming ne doit jamais devenir un canal d'exfiltration de valeurs secrètes.

### Webhooks

Les webhooks pourront notifier des systèmes externes.

Exemples :

- secret rotaté ;
- token révoqué ;
- vault verrouillé ;
- anomalie détectée ;
- backup terminé.

Contraintes :

- jamais de valeur secrète dans webhook ;
- signature des événements future ;
- retries contrôlés ;
- audit ;
- configuration sécurisée.

### Admin API

Une Admin API plus spécialisée pourra apparaître.

Elle devra rester :

- explicitement séparée ;
- fortement protégée ;
- auditée ;
- documentée ;
- compatible avec least privilege.

Elle ne devra pas devenir un canal de contournement.

### SDK

Les SDKs Python et TypeScript devront respecter le contrat REST.

Ils ne doivent pas :

- masquer des erreurs de permission ;
- logger des secrets ;
- introduire de retry dangereux ;
- contourner l'API ;
- exposer des helpers qui encouragent le bulk read de valeurs.

Ils doivent aider les clients à utiliser l'API correctement.

## Conclusion

L'API REST de MCP Secret Manager doit rester claire, stable et sûre.

Elle expose des ressources compréhensibles, applique des permissions explicites, sépare métadonnées et valeurs secrètes, audite les opérations sensibles et refuse les comportements ambigus.

Elle est l'une des interfaces principales du projet, mais elle n'est pas le coeur métier. Toute sa logique critique doit passer par l'Application Layer afin que REST, MCP, CLI et futurs SDKs partagent les mêmes garanties de sécurité.

