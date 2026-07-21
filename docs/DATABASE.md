# Modèle de données de MCP Secret Manager

Ce document définit le modèle de données officiel de MCP Secret Manager.

Il sert de référence avant l'écriture des premières tables PostgreSQL. Il décrit les entités métier, leurs responsabilités, leurs relations, leurs cycles de vie et leurs invariants.

Ce document ne contient pas de schéma SQL, pas de migration et pas de modèle ORM. Il est une spécification de domaine.

## 1. Objectifs

### Pourquoi ce modèle de données existe

MCP Secret Manager doit stocker des secrets de manière structurée, sécurisée, auditable et extensible.

Le modèle de données existe pour représenter clairement :

- les frontières de sécurité ;
- l'organisation des secrets ;
- les versions immuables ;
- les providers ;
- les acteurs ;
- les rôles ;
- les permissions ;
- les tokens ;
- les événements d'audit.

Le modèle doit permettre au MVP de rester simple tout en préparant les évolutions futures liées aux agents IA, aux serveurs MCP, aux providers avancés et aux orchestrateurs multi-agents.

### Problèmes résolus

Ce modèle résout les problèmes suivants :

- organiser les secrets par vault et projet ;
- séparer la valeur secrète de ses métadonnées ;
- conserver l'historique des versions ;
- empêcher les modifications silencieuses de valeurs ;
- associer les accès à des acteurs identifiables ;
- appliquer des permissions explicites ;
- permettre la révocation de tokens ;
- auditer les opérations sensibles ;
- préparer l'ajout de nouveaux Secret Providers ;
- éviter une structure trop générique ou trop implicite.

### Principes de conception

Le modèle est guidé par :

- PostgreSQL-first ;
- simplicité du MVP ;
- intégrité référentielle ;
- séparation des responsabilités ;
- auditabilité ;
- immutabilité des versions ;
- refus des états ambigus ;
- évolutivité sans complexité prématurée.

Le modèle doit être suffisamment strict pour empêcher les incohérences, mais suffisamment extensible pour accueillir les futures capacités du projet.

## 2. Principes

### Normalisation

Les concepts métier importants doivent être représentés par des entités distinctes.

Vault, Project, Secret, SecretVersion, Actor, Role, Permission, Token et AuditEvent ne doivent pas être mélangés dans une même structure opaque.

La normalisation permet :

- une meilleure intégrité ;
- des relations explicites ;
- une auditabilité plus claire ;
- des permissions plus précises ;
- une évolution progressive du modèle.

Le modèle peut utiliser des métadonnées flexibles lorsque cela est pertinent, mais les relations critiques doivent rester structurées.

### Intégrité référentielle

Les relations entre entités doivent être protégées par le modèle.

Un secret ne peut pas exister sans projet. Un projet ne peut pas exister sans vault. Une version ne peut pas exister sans secret. Un rôle attribué doit référencer un acteur et un rôle valides.

L'intégrité référentielle évite les états orphelins, ambigus ou dangereux.

### Immutabilité des versions

Une version de secret est immuable.

Lorsqu'une valeur change, une nouvelle version est créée. Une version existante ne doit jamais être modifiée pour représenter une nouvelle valeur.

Cette règle protège :

- l'audit ;
- la rotation future ;
- la révocation ;
- la compréhension historique ;
- la reproductibilité des investigations.

### Least Privilege

Le modèle doit permettre d'exprimer des accès minimaux.

Cela implique :

- séparation entre acteur et rôle ;
- séparation entre rôle et permission ;
- permissions distinctes pour metadata et value ;
- attribution explicite des rôles ;
- tokens liés à des acteurs.

Le modèle ne doit pas forcer des permissions larges pour simplifier les requêtes.

### Auditabilité

Les actions sensibles doivent pouvoir être rattachées à :

- un acteur ;
- une ressource ;
- une action ;
- une décision ;
- une interface ;
- un moment.

Le modèle doit permettre de reconstruire l'histoire des opérations sans stocker de valeurs secrètes dans l'audit.

### Séparation Metadata / Secret Value

Les métadonnées d'un secret et la valeur chiffrée du secret sont deux responsabilités différentes.

Un Secret représente l'identité logique du secret. Une SecretVersion représente une valeur chiffrée à un moment donné.

Cette séparation permet :

- permissions distinctes ;
- versionnement ;
- lecture de metadata sans exposition de valeur ;
- audit plus précis ;
- rotation future.

### Évolutivité

Le modèle doit pouvoir évoluer vers :

- Organizations ;
- Agent Identity ;
- Mission ;
- Budget ;
- Quota ;
- ABAC ;
- Secret Providers avancés ;
- rotation automatique ;
- intégrations matérielles ;
- providers cloud.

Cette évolutivité ne doit pas complexifier inutilement le MVP.

### Performance raisonnable avant optimisation

Le modèle doit être efficace pour les accès attendus, mais ne doit pas sacrifier la clarté pour des optimisations prématurées.

Les lectures fréquentes doivent être anticipées :

- trouver un secret par vault, projet et chemin ;
- charger la version courante ;
- vérifier les rôles et permissions ;
- écrire des événements d'audit ;
- filtrer l'audit par acteur, action ou ressource.

Les optimisations avancées doivent être guidées par l'usage réel.

## 3. Vue d'ensemble

Vue logique des principales entités :

```text
                         +----------------+
                         |     Actor      |
                         +--------+-------+
                                  |
                                  | receives
                                  v
                         +----------------+
                         |   ActorRole    |
                         +--------+-------+
                                  |
                                  v
                         +----------------+
                         |      Role      |
                         +--------+-------+
                                  |
                                  | grants
                                  v
                         +----------------+
                         | RolePermission |
                         +--------+-------+
                                  |
                                  v
                         +----------------+
                         |   Permission   |
                         +----------------+


                         +----------------+
                         | ServiceAccount |
                         +--------+-------+
                                  |
                                  | is represented by
                                  v
                         +----------------+
                         |     Actor      |
                         +--------+-------+
                                  |
                                  | authenticates with
                                  v
                         +----------------+
                         |     Token      |
                         +----------------+


                         +----------------+
                         |     Vault      |
                         +--------+-------+
                                  |
                                  | contains
                                  v
                         +----------------+
                         |    Project     |
                         +--------+-------+
                                  |
                                  | contains
                                  v
                         +----------------+
                         |     Secret     |
                         +--------+-------+
                                  |
                                  | has many
                                  v
                         +----------------+
                         | SecretVersion  |
                         +----------------+
                                  ^
                                  |
                         encrypted value


                         +----------------+
                         | SecretProvider |
                         +--------+-------+
                                  |
                                  | classifies / powers
                                  v
                         +----------------+
                         |     Secret     |
                         +----------------+


                         +----------------+
                         |   AuditEvent   |
                         +----------------+
                           ^      ^     ^
                           |      |     |
                         Actor  Action Resource
```

Relations principales :

- un Vault contient plusieurs Projects ;
- un Project contient plusieurs Secrets ;
- un Secret possède plusieurs SecretVersions ;
- un Secret référence un SecretProvider ;
- un Actor peut recevoir plusieurs Roles ;
- un Role peut contenir plusieurs Permissions ;
- un ServiceAccount est représenté par un Actor ;
- un Token authentifie un Actor ;
- un AuditEvent référence un acteur, une action et une ressource.

## 4. Description des entités

### Vault

Rôle :

Le Vault est la principale frontière logique et cryptographique du système.

Responsabilité :

- regrouper des projets ;
- porter un état de sécurité ;
- délimiter un espace de secrets ;
- préparer la séparation des clés cryptographiques ;
- permettre des permissions par périmètre.

Cycle de vie :

- créé ;
- actif ;
- verrouillé ;
- archivé ;
- potentiellement détruit selon procédures futures.

Invariants :

- un vault possède un état explicite ;
- un vault verrouillé interdit la lecture des valeurs secrètes ;
- un vault archivé ne doit pas accepter d'opérations normales d'écriture ;
- un vault ne doit pas être supprimé si des dépendances actives existent, sauf procédure explicite.

### Project

Rôle :

Le Project organise les secrets à l'intérieur d'un vault.

Responsabilité :

- structurer les secrets par usage ;
- représenter des environnements ou domaines applicatifs ;
- permettre des permissions plus fines que le vault ;
- rendre les chemins de secrets compréhensibles.

Cycle de vie :

- créé dans un vault ;
- actif ;
- archivé ;
- supprimé logiquement ou physiquement selon règles futures.

Invariants :

- un project appartient toujours à un seul vault ;
- un project ne peut pas exister sans vault ;
- un project archivé ne doit pas recevoir de nouveaux secrets ;
- un project ne doit pas contenir deux secrets actifs avec le même chemin logique.

### Secret

Rôle :

Le Secret représente l'identité logique d'un secret.

Responsabilité :

- définir le nom ou chemin du secret ;
- porter les métadonnées métier ;
- référencer le provider ;
- référencer la version courante ;
- séparer l'identité du secret de ses valeurs versionnées.

Cycle de vie :

- créé ;
- actif ;
- mis à jour au niveau metadata ;
- nouvelle version ajoutée ;
- archivé ;
- supprimé logiquement ;
- détruit selon procédure future.

Invariants :

- un secret appartient toujours à un seul project ;
- un secret possède un provider ;
- un secret possède zéro ou plusieurs versions selon son état ;
- un secret actif avec valeur lisible doit posséder une version courante ;
- modifier une valeur crée une nouvelle version ;
- modifier les métadonnées ne modifie pas les versions existantes.

### SecretVersion

Rôle :

SecretVersion représente une valeur chiffrée immuable d'un secret à un instant donné.

Responsabilité :

- stocker le ciphertext ;
- stocker les métadonnées cryptographiques nécessaires ;
- représenter une version historique ;
- permettre la rotation et la révocation futures.

Cycle de vie :

- créée ;
- active ;
- dépréciée ;
- révoquée ;
- détruite cryptographiquement ou physiquement selon règles futures.

Invariants :

- une SecretVersion appartient toujours à un seul Secret ;
- une SecretVersion est immuable ;
- une SecretVersion ne doit jamais contenir de valeur en clair ;
- une SecretVersion ne peut pas changer de Secret ;
- une SecretVersion révoquée ne doit plus être retournée comme valeur lisible ;
- une SecretVersion détruite ne doit pas être récupérable.

### SecretProvider

Rôle :

SecretProvider décrit l'origine, la nature ou les capacités associées à un secret.

Responsabilité :

- classifier un secret ;
- déclarer les capacités futures ;
- préparer validation, rotation, révocation ou synchronisation ;
- éviter que le coeur du modèle dépende d'un type de secret particulier.

Cycle de vie :

- défini par le système ;
- activé ;
- désactivé ou déprécié selon compatibilité future.

Invariants :

- un secret référence toujours un provider ;
- le provider local statique existe au MVP ;
- un provider ne contourne jamais permissions, crypto ou audit ;
- désactiver un provider ne doit pas rendre incohérents les secrets historiques.

### Actor

Rôle :

Actor représente une identité capable d'agir dans le système.

Responsabilité :

- unifier utilisateurs humains, comptes de service et futures identités agents ;
- servir de cible aux rôles ;
- être référencé dans l'audit ;
- permettre une autorisation cohérente.

Cycle de vie :

- créé ;
- actif ;
- désactivé ;
- supprimé logiquement selon règles futures.

Invariants :

- toute action sensible doit être associée à un Actor ;
- un Actor désactivé ne doit pas pouvoir s'authentifier ;
- un Actor peut posséder plusieurs rôles ;
- un Actor peut être référencé durablement par l'audit même après désactivation.

### ServiceAccount

Rôle :

ServiceAccount représente un service technique comme OpenClaw, un serveur MCP ou une application.

Responsabilité :

- identifier un service non humain ;
- permettre des tokens dédiés ;
- isoler les accès de service des accès humains ;
- faciliter la révocation et l'audit.

Cycle de vie :

- créé ;
- actif ;
- token renouvelé ou révoqué ;
- désactivé ;
- supprimé logiquement.

Invariants :

- un ServiceAccount est représenté par un Actor ;
- un ServiceAccount doit pouvoir être révoqué sans supprimer l'audit ;
- OpenClaw doit utiliser un ServiceAccount dédié ;
- un ServiceAccount ne doit pas partager son identité avec un utilisateur humain.

### Role

Rôle :

Role regroupe des permissions.

Responsabilité :

- simplifier l'attribution des droits ;
- permettre des profils comme admin, auditor, secret_reader ou service_openclaw ;
- éviter d'attribuer des permissions une par une à chaque acteur.

Cycle de vie :

- créé ;
- modifié ;
- désactivé ou supprimé si non utilisé ;
- versionnement futur possible si nécessaire.

Invariants :

- un Role doit avoir un nom explicite ;
- un Role ne doit pas contenir de permissions implicites non documentées ;
- modifier un Role peut affecter plusieurs Actors et doit être audité ;
- les rôles larges doivent être rares et justifiés.

### Permission

Rôle :

Permission représente une action autorisée.

Responsabilité :

- exprimer les droits de manière atomique ;
- distinguer les actions sensibles ;
- permettre l'évaluation RBAC.

Cycle de vie :

- définie par le système ;
- utilisée par des roles ;
- dépréciée ou remplacée avec précaution si l'API évolue.

Invariants :

- une Permission doit représenter une action claire ;
- lire metadata et lire value sont des permissions distinctes ;
- une permission inconnue ne doit jamais être traitée comme autorisée ;
- les permissions publiques doivent être documentées.

### RolePermission

Rôle :

RolePermission associe un Role à une Permission.

Responsabilité :

- représenter les droits accordés par un rôle ;
- permettre l'évolution contrôlée des rôles ;
- rendre les permissions auditablement explicites.

Cycle de vie :

- créée lorsqu'une permission est ajoutée à un rôle ;
- supprimée ou désactivée lorsqu'elle est retirée ;
- auditée si le changement affecte la sécurité.

Invariants :

- une RolePermission référence toujours un Role valide ;
- une RolePermission référence toujours une Permission valide ;
- les doublons logiques sont interdits ;
- les changements doivent être auditables.

### ActorRole

Rôle :

ActorRole associe un Actor à un Role.

Responsabilité :

- attribuer des droits à un acteur ;
- permettre la révocation d'un rôle ;
- séparer identité et autorisation.

Cycle de vie :

- créée lors d'une attribution ;
- active ;
- révoquée ou supprimée selon politique ;
- conservée dans l'audit par événement.

Invariants :

- un ActorRole référence toujours un Actor valide ;
- un ActorRole référence toujours un Role valide ;
- un acteur ne doit pas recevoir de rôle implicite non visible ;
- la révocation doit prendre effet sur les nouvelles demandes.

### Token

Rôle :

Token permet à un Actor de s'authentifier.

Responsabilité :

- représenter un credential révocable ;
- permettre l'accès des services et clients ;
- lier une authentification à un acteur ;
- permettre l'audit et la révocation.

Cycle de vie :

- créé ;
- actif ;
- utilisé ;
- expiré si expiration définie ;
- révoqué ;
- supprimé physiquement selon politique future.

Invariants :

- un Token appartient toujours à un Actor ;
- un Token complet ne doit jamais être stocké en clair ;
- un Token révoqué ne redevient jamais valide ;
- un Token désactivé ne doit pas authentifier ;
- un Token doit être révocable indépendamment de l'Actor.

### AuditEvent

Rôle :

AuditEvent représente un événement de sécurité ou d'activité sensible.

Responsabilité :

- enregistrer les actions importantes ;
- conserver les refus et succès ;
- relier acteur, action, ressource, interface et décision ;
- fournir une base d'investigation.

Cycle de vie :

- créé ;
- conservé selon politique ;
- archivé ou purgé selon rétention future.

Invariants :

- un AuditEvent ne contient jamais de valeur secrète ;
- un AuditEvent ne contient jamais de token complet ;
- un AuditEvent doit rester compréhensible même si la ressource référencée est supprimée ;
- un AuditEvent doit distinguer allowed et denied ;
- l'audit ne doit pas être utilisé comme stockage métier.

## 5. Relations

### Vault et Project

Cardinalité :

- un Vault possède plusieurs Projects ;
- un Project appartient à un seul Vault.

Contraintes métier :

- un Project ne peut pas exister sans Vault ;
- un Vault verrouillé affecte les opérations sensibles de ses Projects ;
- archiver un Vault doit affecter l'usage normal de ses Projects.

### Project et Secret

Cardinalité :

- un Project possède plusieurs Secrets ;
- un Secret appartient à un seul Project.

Contraintes métier :

- un Secret sans Project est interdit ;
- un Project archivé ne doit pas recevoir de nouveau Secret actif ;
- deux Secrets actifs ne doivent pas partager le même chemin logique dans un même Project.

### Secret et SecretVersion

Cardinalité :

- un Secret possède plusieurs SecretVersions ;
- une SecretVersion appartient à un seul Secret.

Contraintes métier :

- une SecretVersion ne peut pas être orpheline ;
- une SecretVersion est immuable ;
- un Secret actif lisible doit référencer une version courante ;
- une seule version doit être courante pour un Secret donné.

### Secret et SecretProvider

Cardinalité :

- un Secret référence un SecretProvider ;
- un SecretProvider peut être utilisé par plusieurs Secrets.

Contraintes métier :

- un Secret doit toujours avoir un provider ;
- le provider local statique existe dès le MVP ;
- un provider désactivé ne doit pas rendre illisible l'historique sans décision explicite.

### Actor et ServiceAccount

Cardinalité :

- un ServiceAccount est représenté par un Actor ;
- un Actor peut représenter un ServiceAccount, un utilisateur humain ou une future identité agent.

Contraintes métier :

- un ServiceAccount ne partage pas son identité avec un utilisateur humain ;
- un ServiceAccount désactivé ne doit plus s'authentifier ;
- OpenClaw possède son ServiceAccount dédié.

### Actor et Token

Cardinalité :

- un Actor peut posséder plusieurs Tokens ;
- un Token appartient à un seul Actor.

Contraintes métier :

- un Token ne peut pas exister sans Actor ;
- un Token révoqué ne redevient jamais valide ;
- un Token complet n'est jamais stocké en clair ;
- révoquer un Token ne supprime pas l'Actor.

### Actor, Role et Permission

Cardinalité :

- un Actor peut avoir plusieurs Roles ;
- un Role peut être attribué à plusieurs Actors ;
- un Role peut contenir plusieurs Permissions ;
- une Permission peut appartenir à plusieurs Roles.

Associations :

- ActorRole relie Actor et Role ;
- RolePermission relie Role et Permission.

Contraintes métier :

- l'absence de rôle ou permission équivaut à un refus ;
- une permission inconnue n'autorise rien ;
- les changements de rôles et permissions doivent être auditables.

### AuditEvent et ressources

Cardinalité :

- un Actor peut générer plusieurs AuditEvents ;
- une ressource peut être référencée par plusieurs AuditEvents ;
- un AuditEvent concerne une action et une décision.

Contraintes métier :

- l'audit doit rester lisible même après suppression logique d'une ressource ;
- l'audit ne doit pas dépendre de la présence permanente de toutes les ressources référencées ;
- l'audit ne contient jamais de valeur secrète.

## 6. Cycle de vie

### Création

La création d'une entité doit :

- être demandée par un Actor authentifié lorsque l'action est sensible ;
- vérifier les permissions nécessaires ;
- produire un état initial valide ;
- respecter les contraintes de parenté ;
- générer un AuditEvent si l'entité est sensible.

Exemples :

- créer un Vault ;
- créer un Project dans un Vault ;
- créer un Secret dans un Project ;
- créer une SecretVersion initiale ;
- créer un Token pour un Actor.

### Modification

La modification doit distinguer :

- modifications de métadonnées ;
- modifications de permissions ;
- changement d'état ;
- nouvelle version de secret.

Une modification de valeur secrète ne modifie jamais une SecretVersion existante. Elle crée une nouvelle SecretVersion.

Les modifications sensibles doivent être auditables.

### Versionnement

Le versionnement concerne principalement SecretVersion.

Chaque nouvelle valeur d'un Secret devient une nouvelle SecretVersion.

Le Secret logique garde la référence de la version courante.

### Archivage

L'archivage marque une entité comme non active sans la supprimer.

Exemples :

- Vault archivé ;
- Project archivé ;
- Secret archivé ;
- Provider déprécié.

L'archivage est utile pour préserver l'historique, l'audit et la compréhension opérationnelle.

### Suppression logique

La suppression logique rend une entité indisponible dans les opérations normales tout en conservant son existence pour audit, restauration ou investigation.

Elle est préférable à la suppression physique pour les entités sensibles au MVP.

### Suppression physique

La suppression physique retire réellement les données.

Elle doit être utilisée avec prudence, car elle peut casser l'audit, l'investigation ou la restauration.

Elle doit respecter les contraintes référentielles et les politiques de rétention.

### Destruction cryptographique

La destruction cryptographique rend une valeur irrécupérable en supprimant ou invalidant les clés nécessaires à son déchiffrement.

Elle peut être plus sûre qu'une simple suppression physique lorsque les backups conservent encore des ciphertexts.

Cette capacité est prévue pour une version future et doit être conçue avec un haut niveau de prudence.

## 7. Versionnement

### Pourquoi les versions sont immuables

Les versions sont immuables pour garantir que l'histoire d'un secret ne soit pas réécrite.

Cette règle permet :

- audit fiable ;
- rotation propre ;
- investigations compréhensibles ;
- rollback contrôlé futur ;
- révocation ciblée ;
- absence d'écrasement silencieux.

Modifier une version existante détruirait la confiance dans l'historique.

### Comment une nouvelle version devient courante

Lorsqu'une nouvelle valeur est fournie pour un Secret :

1. une nouvelle SecretVersion est créée ;
2. elle reçoit son propre matériel cryptographique de données ;
3. elle est associée au Secret ;
4. le Secret logique met à jour sa référence de version courante ;
5. l'opération est auditée.

Le passage à la version courante doit être explicite et transactionnel.

### Pourquoi une version existante ne doit jamais être modifiée

Une version existante représente une valeur historique précise.

La modifier poserait plusieurs problèmes :

- audit trompeur ;
- impossibilité de savoir quelle valeur a été lue ;
- rotation ambiguë ;
- risque de corruption silencieuse ;
- difficulté de restauration ;
- perte de confiance dans les événements passés.

Une version peut changer d'état selon les règles futures, par exemple devenir révoquée ou détruite, mais sa valeur chiffrée ne doit pas être remplacée par une autre valeur.

## 8. Audit

### Entités générant des événements d'audit

Les entités suivantes peuvent générer des AuditEvents :

- Vault ;
- Project ;
- Secret ;
- SecretVersion ;
- SecretProvider ;
- Actor ;
- ServiceAccount ;
- Role ;
- Permission ;
- RolePermission ;
- ActorRole ;
- Token.

Les actions sensibles associées doivent être auditées.

Exemples :

- création de Vault ;
- verrouillage de Vault ;
- création de Secret ;
- lecture de valeur ;
- ajout de version ;
- révocation de Token ;
- attribution de Role ;
- refus de permission.

### Relation entre AuditEvent et les entités

Un AuditEvent doit pouvoir indiquer :

- l'Actor responsable ;
- l'action ;
- le type de ressource ;
- l'identifiant de ressource ;
- la décision ;
- l'interface utilisée ;
- le moment.

L'audit doit rester compréhensible même si la ressource est supprimée logiquement ou physiquement plus tard.

### Pourquoi AuditEvent ne contient jamais de secret

L'audit est une aide à l'investigation, pas un stockage de secrets.

Inclure une valeur secrète dans un AuditEvent créerait une seconde base de secrets, moins contrôlée et plus difficile à protéger.

AuditEvent ne doit jamais contenir :

- valeur secrète ;
- token complet ;
- clé privée ;
- clé maître ;
- DEK ;
- mot de passe ;
- payload brut sensible.

## 9. Contraintes métier

Les invariants suivants doivent toujours rester vrais :

- un Vault possède toujours un état explicite ;
- un Vault verrouillé interdit la lecture de valeurs secrètes ;
- un Vault archivé n'accepte pas d'écriture normale ;
- un Project appartient toujours à un seul Vault ;
- un Project ne peut pas exister sans Vault ;
- un Project archivé ne reçoit pas de nouveaux Secrets actifs ;
- un Secret appartient toujours à un seul Project ;
- un Secret sans Project est interdit ;
- un Secret référence toujours un SecretProvider ;
- un Secret actif lisible possède une version courante ;
- deux Secrets actifs d'un même Project ne partagent pas le même chemin logique ;
- une SecretVersion appartient toujours à un Secret ;
- une SecretVersion ne peut jamais être orpheline ;
- une SecretVersion est immuable ;
- une SecretVersion ne contient jamais de valeur en clair ;
- une SecretVersion ne change jamais de Secret ;
- une SecretVersion révoquée ne doit pas être retournée comme valeur courante ;
- une SecretVersion détruite ne doit pas être récupérable ;
- une seule SecretVersion est courante pour un Secret donné ;
- modifier une valeur crée toujours une nouvelle SecretVersion ;
- modifier les métadonnées d'un Secret ne modifie pas ses versions ;
- un SecretProvider peut être utilisé par plusieurs Secrets ;
- le provider local statique existe au MVP ;
- un provider ne contourne jamais permissions, crypto ou audit ;
- désactiver un provider ne casse pas l'historique existant sans décision explicite ;
- un Actor représente une identité capable d'agir ;
- toute action sensible est associée à un Actor ;
- un Actor désactivé ne peut pas s'authentifier ;
- un Actor peut posséder plusieurs Roles ;
- un Actor peut posséder plusieurs Tokens ;
- un ServiceAccount est représenté par un Actor ;
- OpenClaw utilise un ServiceAccount dédié ;
- un ServiceAccount ne partage pas son identité avec un utilisateur humain ;
- un Role regroupe des Permissions explicites ;
- un Role ne contient pas de permission implicite ;
- une Permission représente une action claire ;
- une Permission inconnue n'autorise rien ;
- lire metadata et lire value sont des Permissions distinctes ;
- un RolePermission référence un Role valide ;
- un RolePermission référence une Permission valide ;
- un ActorRole référence un Actor valide ;
- un ActorRole référence un Role valide ;
- l'absence d'ActorRole applicable équivaut à un refus ;
- l'absence de Permission applicable équivaut à un refus ;
- un Token appartient toujours à un Actor ;
- un Token complet n'est jamais stocké en clair ;
- un Token révoqué ne redevient jamais valide ;
- un Token expiré ne redevient pas valide sans nouveau token ;
- révoquer un Token ne supprime pas l'Actor ;
- supprimer un Actor ne doit pas rendre l'audit incompréhensible ;
- un AuditEvent ne contient jamais de valeur secrète ;
- un AuditEvent distingue succès et refus ;
- un AuditEvent reste compréhensible même après suppression d'une ressource ;
- un AuditEvent n'est pas utilisé comme stockage métier ;
- une lecture de valeur doit être précédée d'une vérification de permission ;
- un refus de permission ne déclenche jamais de déchiffrement ;
- une lecture de metadata ne donne jamais accès à la valeur ;
- les relations critiques ne sont pas stockées uniquement comme métadonnées flexibles ;
- la suppression physique ne doit pas casser les invariants d'audit sans procédure explicite ;
- les opérations sensibles doivent être auditables.

## 10. Performance

### Accès les plus fréquents

Les accès les plus fréquents attendus sont :

- authentifier un Token ;
- résoudre les Roles d'un Actor ;
- vérifier une Permission ;
- trouver un Vault par identifiant ou nom ;
- trouver un Project dans un Vault ;
- trouver un Secret par Project et chemin ;
- charger la version courante d'un Secret ;
- écrire un AuditEvent ;
- lister les métadonnées autorisées ;
- filtrer l'audit par acteur, ressource, action ou période.

### Index probablement nécessaires

Sans définir de SQL, le modèle devra probablement optimiser :

- lookup de Token par empreinte ;
- lookup d'Actor actif ;
- lookup des ActorRoles par Actor ;
- lookup des RolePermissions par Role ;
- lookup de Vault par identifiant stable ;
- lookup de Project par Vault ;
- lookup de Secret par Project et chemin ;
- lookup de SecretVersion courante ;
- recherche d'AuditEvents par date ;
- recherche d'AuditEvents par Actor ;
- recherche d'AuditEvents par ressource ;
- recherche d'AuditEvents par décision.

### Compromis acceptés

Le MVP accepte :

- un modèle relationnel clair plutôt qu'une dénormalisation agressive ;
- une écriture d'audit systématique même si elle ajoute du coût ;
- une séparation Secret / SecretVersion même si une jointure est nécessaire ;
- des permissions lisibles plutôt qu'un moteur de policy optimisé ;
- des requêtes simples avant cache ;
- aucune mise en cache de secrets en clair.

La performance ne doit jamais justifier :

- le contournement des permissions ;
- la désactivation de l'audit ;
- le logging de valeurs ;
- la fusion dangereuse metadata/value ;
- la modification en place de versions.

## 11. Évolutions futures

### Organizations

Organizations est volontairement absent du MVP.

Le modèle pourra évoluer en ajoutant une entité Organization au-dessus de Vault.

L'objectif sera de permettre un multi-tenant futur sans modifier les concepts fondamentaux :

- Vault ;
- Project ;
- Secret ;
- SecretVersion ;
- Actor ;
- Role ;
- Permission.

### ABAC

ABAC pourra enrichir le modèle de permissions.

Entités futures possibles :

- Policy ;
- PolicyRule ;
- Condition ;
- Attribute ;
- Context.

ABAC devra s'ajouter au module Permissions sans déplacer l'autorisation dans les interfaces ou repositories.

### Agent Identity

Agent Identity représentera les agents IA comme acteurs de première classe.

Elle pourra étendre ou spécialiser Actor avec :

- agent_id ;
- parent agent ;
- orchestrateur ;
- niveau de confiance ;
- modèle ;
- contexte d'exécution ;
- durée de vie.

Le modèle actuel prépare cela grâce à Actor.

### Mission

Mission représentera un contexte de travail agentique.

Elle pourra relier :

- agents ;
- demandes de secrets ;
- justifications ;
- budgets ;
- quotas ;
- audit.

Mission ne fait pas partie du MVP afin d'éviter une complexité prématurée.

### Budget

Budget pourra limiter l'usage d'un agent ou d'une mission.

Exemples :

- nombre de lectures ;
- durée ;
- coût externe ;
- nombre de providers ;
- niveau de secret autorisé.

Budget devra s'ajouter sans modifier le cycle de vie de base d'un Secret.

### Quota

Quota pourra limiter les actions sur période.

Exemples :

- lectures par minute ;
- lectures par mission ;
- erreurs de permission ;
- accès provider externe.

Quota devra être évalué avant l'action sensible et audité.

### Secret Providers avancés

Les providers avancés pourront ajouter :

- validation ;
- rotation ;
- révocation ;
- génération ;
- synchronisation metadata ;
- interaction avec API externe ;
- opération cryptographique externe.

Ils devront toujours respecter :

- permissions ;
- audit ;
- séparation metadata/value ;
- invariants SecretVersion.

### Rotation automatique

La rotation automatique pourra ajouter :

- RotationPolicy ;
- RotationJob ;
- RotationAttempt ;
- RotationSchedule ;
- RotationResult.

Elle devra créer de nouvelles versions plutôt que modifier les anciennes.

### Cloud Providers

Les providers cloud pourront introduire :

- comptes externes ;
- credentials provider ;
- scopes ;
- metadata remote ;
- statuts de synchronisation.

Ces entités devront rester derrière l'abstraction Provider.

### TPM

TPM pourra être utilisé pour protéger des clés.

Le modèle actuel pourra évoluer en ajoutant des informations de key material externe sans modifier Secret ou SecretVersion.

### YubiKey

YubiKey pourra servir à protéger des clés, signer des opérations ou exiger une présence physique.

Cette évolution devra enrichir la gestion des clés et des opérations sensibles, sans transformer YubiKey en dépendance obligatoire du modèle MVP.

## 12. Ce qui est volontairement absent du MVP

Les entités suivantes sont absentes du MVP :

- Organization ;
- AgentIdentity spécialisée ;
- Mission ;
- Budget ;
- Quota ;
- Policy ;
- PolicyRule ;
- ABAC Attribute ;
- AccessRequest ;
- Lease ;
- RotationPolicy ;
- RotationJob ;
- RotationAttempt ;
- BackupManifest ;
- KeyRing détaillé ;
- KeyEncryptionKey ;
- DataEncryptionKey comme entité métier complète ;
- HSMDevice ;
- TPMDevice ;
- YubiKeyDevice ;
- CloudProviderAccount ;
- ProviderCredential ;
- HumanApproval ;
- AnomalySignal ;
- Notification ;
- WebSession ;
- API Client Application ;
- OAuth Client ;
- SecretLease ;
- DynamicSecret.

### Pourquoi ces entités sont absentes

Elles sont absentes pour préserver :

- simplicité du MVP ;
- lisibilité du modèle ;
- rapidité de développement ;
- testabilité ;
- sécurité ;
- compréhension par les contributeurs ;
- cohérence avec OpenClaw First.

Leur absence ne signifie pas qu'elles sont rejetées.

Le modèle actuel prépare leur arrivée grâce à :

- Actor ;
- Vault ;
- Project ;
- Secret ;
- SecretVersion ;
- SecretProvider ;
- Role ;
- Permission ;
- AuditEvent.

### Règle d'ajout futur

Une nouvelle entité ne doit être ajoutée que si :

- elle résout un problème réel ;
- elle ne duplique pas une entité existante ;
- elle respecte les invariants ;
- elle est documentée ;
- elle est testable ;
- elle n'introduit pas de complexité prématurée ;
- elle ne contourne pas les frontières de sécurité.

## Conclusion

Le modèle de données de MCP Secret Manager doit rester simple, relationnel, auditable et extensible.

Le MVP repose sur une hiérarchie claire :

```text
Vault -> Project -> Secret -> SecretVersion
```

Et sur un modèle d'accès clair :

```text
Actor -> Role -> Permission
```

Cette combinaison fournit les fondations nécessaires pour protéger les secrets d'OpenClaw aujourd'hui, puis accueillir progressivement les agents IA, les providers avancés, les quotas, les budgets, ABAC et les orchestrateurs multi-agents demain.

