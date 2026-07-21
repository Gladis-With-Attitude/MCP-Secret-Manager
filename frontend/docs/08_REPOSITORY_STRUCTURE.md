# Introduction

Ce document définit la structure officielle du dépôt frontend de MCP Secret Manager.

Dans le monorepo, tous les chemins décrits dans ce document sont relatifs au dossier `frontend/`, sauf mention contraire. Par exemple, `app/` signifie `frontend/app/`, `providers/` signifie `frontend/providers/` et `tests/` signifie `frontend/tests/`.

Il décrit l'organisation logique du projet, les responsabilités de chaque grand espace, les conventions de nommage, les règles de dépendances, les principes d'import et les anti-patterns à éviter.

Il ne décrit pas l'implémentation. Il ne fournit pas d'arborescence imposée, de code, de pseudo-code ou de détail technique spécifique à un fichier. Il définit uniquement les frontières et conventions qui guideront l'organisation du frontend pendant toute sa durée de vie.

Une structure cohérente est essentielle parce que MCP Secret Manager est une application SaaS de sécurité qui devra évoluer sur plusieurs années.

Le frontend commencera avec un MVP comprenant dashboard, vaults, projects, secrets, secret versions, API keys, audit logs, RBAC, profil et settings. Il devra ensuite pouvoir accueillir multi-tenant, notifications, monitoring, analytics, billing, WebSockets, intégrations cloud, approbations et identités d'agents IA.

Sans structure claire, le projet risque de devenir difficile à maintenir :

- composants dispersés ;
- logique API dupliquée ;
- hooks impossibles à localiser ;
- features couplées entre elles ;
- dossier shared utilisé comme poubelle ;
- utils génériques incontrôlés ;
- règles de sécurité réimplémentées dans l'UI ;
- imports circulaires ;
- tests difficiles à écrire ;
- onboarding lent.

L'organisation doit donc être pensée pour plusieurs années, pas seulement pour les premiers écrans.

Chaque dossier doit avoir une responsabilité unique. Cette règle rend le projet plus lisible, plus testable et plus sûr. Dans un produit qui manipule des secrets, la capacité à savoir où se trouve une responsabilité est une exigence de qualité et de sécurité.

# Principes d'organisation

## Feature First

Le projet est organisé en priorité autour des features produit.

Une feature représente un domaine fonctionnel cohérent :

- dashboard ;
- vault ;
- project ;
- secret ;
- API key ;
- audit ;
- RBAC ;
- profile ;
- settings.

La philosophie Feature First permet de regrouper les éléments qui changent ensemble :

- UI spécifique ;
- hooks de données ;
- queries ;
- mutations ;
- services ;
- mappers ;
- validation ;
- tests.

Ce principe évite de disperser une même fonctionnalité dans de nombreux dossiers techniques. Un développeur qui travaille sur les secrets doit pouvoir trouver rapidement tout ce qui concerne les secrets.

## Separation of Concerns

Chaque espace du projet possède une responsabilité claire.

Exemples :

- `app/` organise les routes ;
- `features/` contient les domaines fonctionnels ;
- `components/` contient les composants partagés ;
- `lib/` contient l'infrastructure frontend et les utilitaires génériques ;
- `providers/` contient les providers globaux ;
- `tests/` contient les tests transverses.

La séparation des responsabilités limite les effets de bord. Elle évite que les composants visuels connaissent les détails HTTP, que les routes contiennent la logique des features ou que les utilitaires deviennent un second domaine métier.

## High Cohesion

Chaque dossier doit regrouper des éléments fortement liés.

Une feature est cohésive lorsque ses composants, hooks, mappers et tests servent le même domaine.

Un composant partagé est cohésif lorsqu'il remplit une responsabilité UI réutilisable.

Un utilitaire est cohésif lorsqu'il répond à un besoin technique clairement identifiable.

La forte cohésion facilite :

- la compréhension ;
- la modification ;
- les tests ;
- la suppression ;
- la revue ;
- l'évolution.

## Low Coupling

Les dépendances entre dossiers doivent être limitées et explicites.

Une feature ne doit pas dépendre des détails internes d'une autre feature. Si deux features doivent collaborer, elles doivent le faire via :

- route ;
- API backend ;
- modèle partagé réellement commun ;
- composant générique ;
- contrat public clairement identifié.

Le faible couplage permet de modifier une feature sans casser tout le projet.

## Composition over Duplication

La composition est préférée à la duplication.

Lorsqu'un pattern UI est répété, il doit être extrait en composant réutilisable si cela améliore la cohérence. Lorsqu'une logique technique est répétée, elle doit être centralisée si elle est vraiment générique.

Mais la composition ne doit pas devenir une abstraction prématurée.

Il vaut mieux accepter une duplication temporaire entre deux features qu'extraire trop tôt un composant générique mal conçu. Une abstraction partagée devient une responsabilité durable.

## Scalability

La structure doit pouvoir évoluer sans refonte majeure.

Elle doit permettre :

- ajout de nouvelles features ;
- ajout de nouveaux composants ;
- ajout de providers ;
- ajout de modules API ;
- ajout de tests ;
- ajout de fonctionnalités Enterprise ;
- séparation future par tenant ;
- intégration temps réel future.

L'évolutivité doit venir de frontières propres, pas d'une généralisation excessive dès le MVP.

## Discoverability

La structure doit rendre les choses faciles à trouver.

Un développeur doit pouvoir répondre rapidement à ces questions :

- où est la page ;
- où est la feature ;
- où sont les appels API ;
- où sont les hooks ;
- où est la validation ;
- où sont les composants partagés ;
- où sont les tests ;
- où sont les types ;
- où sont les providers.

La découvrabilité est particulièrement importante pour les revues, l'onboarding et les contributions assistées par IA.

# Vue d'ensemble

Le projet frontend est organisé autour de grands espaces fonctionnels.

Ce document ne fixe pas une arborescence exacte. Il définit les espaces attendus et leurs responsabilités.

## app/

`app/` contient la structure de routing Next.js App Router.

Rôle :

- routes ;
- pages ;
- layouts ;
- loading states ;
- error boundaries ;
- not-found ;
- route groups ;
- composition des features dans les routes.

`app/` est une couche d'assemblage et de navigation.

## features/

`features/` contient les domaines produit.

Rôle :

- UI métier ;
- hooks métier ;
- services de feature ;
- queries ;
- mutations ;
- mappers ;
- validation ;
- tests proches de la feature.

Chaque feature doit rester autonome autant que possible.

## components/

`components/` contient les composants partagés et réutilisables.

Rôle :

- composants de layout ;
- composants de navigation ;
- composants de formulaire ;
- boutons ;
- tables génériques ;
- badges ;
- dialogs ;
- feedback ;
- loading ;
- error states.

Les composants partagés ne portent pas de logique métier.

## lib/

`lib/` contient l'infrastructure frontend et les utilitaires génériques.

Rôle :

- client HTTP ;
- helpers ;
- fonctions pures ;
- normalisation technique ;
- gestion d'erreurs générique ;
- utilitaires transverses.

`lib/` ne doit pas devenir un dossier fourre-tout.

## hooks/

`hooks/` contient les hooks partagés non métier.

Rôle :

- hooks UI génériques ;
- hooks techniques ;
- comportements transverses ;
- hooks de préférences non sensibles.

Les hooks métier restent dans les features.

## providers/

`providers/` contient les providers globaux.

Rôle :

- Query Provider ;
- Theme Provider ;
- Auth Provider si nécessaire ;
- Toast Provider ;
- providers futurs comme WebSocket, Analytics ou Notifications.

Les providers doivent rester peu nombreux et explicites.

## styles/

`styles/` contient les fondations visuelles globales.

Rôle :

- styles globaux ;
- conventions visuelles ;
- fondations de thème ;
- support light/dark mode ;
- règles globales minimales.

La majorité du style doit rester portée par les composants.

## assets/

`assets/` contient les ressources visuelles du frontend.

Rôle :

- logos ;
- icônes spécifiques ;
- images ;
- illustrations ;
- assets de marque.

Aucun secret, token ou fichier de configuration sensible ne doit y être stocké.

## types/

`types/` contient les types partagés.

Rôle :

- types UI communs ;
- types techniques ;
- types transverses ;
- types de statut partagés ;
- types de pagination ;
- types d'erreur.

Les types spécifiques à une feature restent dans cette feature.

## config/

`config/` contient la configuration frontend non sensible.

Rôle :

- constantes ;
- configuration publique ;
- environnement ;
- feature flags futurs ;
- limites UI ;
- routes connues ;
- options non sensibles.

Toute valeur exposée au frontend doit être considérée comme publique.

## tests/

`tests/` contient les tests transverses et scénarios globaux.

Rôle :

- tests d'intégration ;
- tests end-to-end ;
- fixtures ;
- mocks ;
- helpers de test ;
- scénarios critiques.

Les tests unitaires proches d'une feature peuvent vivre avec la feature lorsque cela améliore la lisibilité.

# app/

`app/` porte l'App Router.

Il définit comment l'utilisateur navigue dans l'application. Il ne doit pas devenir l'endroit où toute la logique frontend est implémentée.

## Layouts

Les layouts définissent les cadres persistants.

Responsabilités :

- layout public ;
- layout authentifié ;
- layout de console ;
- layout par route group ;
- layout de contexte futur ;
- structure navigationnelle.

Un layout peut composer des providers ou shells, mais il ne doit pas contenir de logique métier détaillée.

## Routes

Les routes représentent les chemins utilisateur.

Elles doivent être nommées selon les concepts produit :

- dashboard ;
- vaults ;
- projects ;
- secrets ;
- api keys ;
- audit logs ;
- RBAC ;
- settings ;
- profile.

Les routes doivent rester compréhensibles et alignées avec l'architecture d'information.

## Pages

Les pages composent les features.

Responsabilités :

- recevoir les paramètres de route ;
- charger les données initiales si pertinent ;
- composer les composants de feature ;
- afficher le layout de page ;
- connecter route et domaine.

Une page ne doit pas contenir une implémentation complète de feature si celle-ci mérite un espace dédié.

## Loading

Les fichiers ou mécanismes de loading de route gèrent les états de chargement.

Responsabilités :

- préserver la structure ;
- fournir skeletons ;
- éviter les pages blanches ;
- rester spécifiques au segment de route.

Ils ne doivent pas simuler de données sensibles.

## Error

Les erreurs de route doivent être gérées par des boundaries.

Responsabilités :

- afficher une erreur sûre ;
- permettre retry ;
- éviter fuite d'information ;
- nettoyer états sensibles si nécessaire.

Les erreurs métier spécifiques peuvent être gérées dans les features lorsque cela offre une meilleure UX.

## not-found

`not-found` gère les ressources absentes ou non résolues.

Responsabilités :

- afficher un état sûr ;
- proposer une navigation ;
- éviter d'exposer des détails non autorisés ;
- rester cohérent avec ForbiddenState.

## Ce qui appartient à app/

Appartient à `app/` :

- fichiers de route ;
- pages ;
- layouts ;
- loading ;
- error ;
- not-found ;
- route groups ;
- composition route-feature ;
- métadonnées de page si nécessaire.

## Ce qui n'appartient pas à app/

N'appartient pas à `app/` :

- composants métier volumineux ;
- services API de feature ;
- mappers ;
- validation Zod métier ;
- logique de mutation complexe ;
- composants partagés ;
- utilitaires génériques ;
- types globaux ;
- logique de permission locale.

# features/

`features/` est le coeur fonctionnel du frontend.

Chaque feature regroupe ce qui appartient à un domaine produit donné.

## Philosophie Feature First

La structure Feature First évite que le projet soit organisé uniquement par types techniques.

Au lieu de chercher les secrets dans :

- components ;
- hooks ;
- services ;
- types ;
- tests ;
- forms ;
- utils.

Le développeur doit pouvoir ouvrir la feature `secret` et y trouver l'essentiel de ce domaine.

## Contenu d'une feature

Une feature peut regrouper :

- UI spécifique ;
- composants connectés ;
- composants métier ;
- hooks métier ;
- services propres au domaine ;
- queries ;
- mutations ;
- mappers ;
- validation ;
- types locaux ;
- tests ;
- fixtures locales ;
- constantes locales.

Tous ces éléments ne sont pas obligatoires dans chaque feature. Une feature simple doit rester simple.

## UI

L'UI de feature contient les composants spécifiques au domaine.

Exemples :

- SecretMetadataCard ;
- VersionTimeline ;
- AuditDetails ;
- RoleCard ;
- SecuritySummary.

Ces composants peuvent connaître les concepts métier de leur feature.

## Hooks

Les hooks de feature encapsulent la logique propre au domaine.

Exemples :

- lecture d'une liste ;
- mutation de création ;
- état d'un workflow de reveal ;
- filtre spécifique.

Ils ne doivent pas être déplacés dans `hooks/` s'ils ne sont pas réellement transverses.

## Services

Les services de feature consomment l'API pour le domaine concerné.

Ils ne contiennent pas de logique métier backend. Ils regroupent les appels API liés à la feature.

## Queries

Les queries de feature gèrent les lectures.

Elles définissent :

- clés de cache ;
- paramètres ;
- appels services ;
- états ;
- invalidation liée.

## Mutations

Les mutations de feature gèrent les actions.

Elles doivent :

- appeler les services ;
- gérer loading ;
- gérer erreurs ;
- invalider les caches appropriés ;
- éviter optimistic updates pour actions sensibles.

## Mappers

Les mappers de feature transforment les DTO en modèles UI ou les formulaires en DTO.

Ils doivent rester explicites et testables.

## Validation

La validation de feature gère les formulaires du domaine.

Elle améliore l'UX mais ne remplace jamais la validation backend.

## Tests

Les tests proches de la feature couvrent :

- composants ;
- mappers ;
- hooks ;
- validation ;
- flows locaux.

Les scénarios end-to-end restent plutôt dans `tests/`.

## Frontières entre features

Une feature ne doit pas importer les détails internes d'une autre feature.

Autorisé :

- utiliser une route vers une autre feature ;
- utiliser un composant partagé ;
- utiliser un type partagé réel ;
- utiliser une API publique de feature explicitement exposée ;
- passer par le backend.

Interdit :

- importer un hook interne d'une autre feature sans contrat ;
- réutiliser un composant métier hors contexte ;
- modifier un mapper d'une autre feature pour un besoin local ;
- créer une dépendance circulaire ;
- mélanger deux domaines dans un même dossier.

# components/

`components/` contient les composants partagés.

Ces composants sont utilisés par plusieurs features ou routes.

## Composants purement réutilisables

Les composants partagés doivent être génériques.

Exemples :

- Button ;
- Dialog ;
- DataTable ;
- Badge ;
- FormField ;
- EmptyState ;
- Spinner ;
- Skeleton ;
- PageHeader ;
- Breadcrumb ;
- Tabs.

Ils peuvent être spécialisés par variante, mais pas par logique métier.

## Aucune logique métier

Un composant partagé ne doit pas :

- appeler une API métier ;
- décider une permission ;
- connaître un endpoint ;
- contenir une règle vault ;
- contenir une règle secret ;
- contenir une règle RBAC ;
- manipuler une valeur secrète sans composant dédié documenté ;
- importer une feature.

Il reçoit ses données et callbacks par composition.

## Composition

Les composants partagés doivent encourager la composition.

Un composant doit :

- exposer un rôle clair ;
- accepter du contenu ou des props adaptées ;
- rester testable ;
- gérer ses états UI ;
- laisser le domaine aux features.

La composition permet de construire des écrans riches sans créer des composants trop abstraits ou trop couplés.

# lib/

`lib/` contient l'infrastructure frontend et les utilitaires techniques.

## Client HTTP

Le client HTTP central appartient à `lib/`.

Responsabilités :

- base URL ;
- credentials ;
- headers ;
- parsing ;
- erreurs ;
- retry policy ;
- timeouts ;
- configuration technique.

Il ne connaît pas les composants React.

## Utilitaires

Les utilitaires doivent être génériques.

Exemples :

- formatage de date ;
- formatage de nombre ;
- helpers de pagination ;
- helpers d'erreur ;
- normalisation technique ;
- fonctions pures.

Un utilitaire spécifique à une feature doit rester dans la feature.

## Helpers

Les helpers doivent avoir une responsabilité précise.

Bon helper :

- petit ;
- pur si possible ;
- nommé clairement ;
- testé si critique ;
- réutilisé par plusieurs espaces.

Mauvais helper :

- dépend d'une feature ;
- modifie un état global ;
- mélange UI, API et métier ;
- contient des branches métier cachées.

## Fonctions génériques

Les fonctions génériques doivent être réellement génériques.

Le fait qu'une fonction soit utilisée une seule fois ne justifie pas toujours sa présence dans `lib/`.

## Infrastructure

`lib/` peut contenir :

- API client ;
- error normalization ;
- configuration runtime non sensible ;
- helpers d'environnement ;
- intégration monitoring future ;
- utilities de sécurité frontend.

## Ce qui ne doit jamais s'y trouver

Ne doit pas se trouver dans `lib/` :

- composants React métier ;
- logique de permission métier ;
- logique de secret ;
- logique RBAC réelle ;
- services propres à une seule feature si non partagés ;
- validations de formulaire très spécifiques ;
- hacks temporaires ;
- dossier utils vague ;
- valeurs sensibles ;
- tokens ;
- secrets.

# hooks/

`hooks/` contient les hooks globaux partagés.

## Hooks métier

Les hooks métier appartiennent aux features.

Exemples :

- hook de liste des secrets ;
- hook de création d'API key ;
- hook de reveal secret ;
- hook de assignments RBAC.

Ils ne doivent pas être placés dans `hooks/` car ils ne sont pas génériques.

## Hooks partagés

Les hooks partagés appartiennent à `hooks/`.

Exemples :

- media query ;
- debounce ;
- clipboard générique non secret ;
- previous value ;
- keyboard shortcut générique ;
- local preference non sensible.

Ils doivent être indépendants des domaines métier.

## Hooks techniques

Les hooks techniques peuvent encapsuler un comportement de plateforme.

Exemples :

- détection de viewport ;
- gestion focus ;
- état mounted ;
- event listener ;
- reduced motion.

Ils doivent rester petits, testables et sans logique métier.

# providers/

`providers/` contient les providers globaux de l'application.

Les providers doivent être explicites, peu nombreux et justifiés.

## Query Provider

Le Query Provider configure TanStack Query.

Responsabilités :

- client query ;
- options globales ;
- cache ;
- retry defaults ;
- comportement d'erreur ;
- nettoyage au logout via coordination.

Il ne doit pas contenir de logique métier de feature.

## Theme Provider

Le Theme Provider gère light mode, dark mode et préférences visuelles.

Responsabilités :

- thème actuel ;
- préférence utilisateur ;
- synchronisation non sensible ;
- compatibilité système ;
- hydratation visuelle correcte.

Il ne doit pas stocker d'information sensible.

## Auth Provider

Un Auth Provider peut exister si l'architecture finale le justifie.

Responsabilités :

- état session minimal ;
- profil courant ;
- logout ;
- session expiration ;
- coordination UI.

Il ne doit pas :

- stocker refresh token ;
- décider des permissions métier ;
- exposer des secrets ;
- remplacer les vérifications backend.

## Futurs providers

Providers futurs possibles :

- Notifications Provider ;
- WebSocket Provider ;
- Analytics Provider ;
- Monitoring Provider ;
- Tenant Provider ;
- Command Palette Provider.

Chaque nouveau provider doit être justifié. Un provider global ajoute une dépendance mentale à toute l'application.

# styles/

`styles/` contient les fondations visuelles globales.

## Global styles

Les styles globaux doivent rester limités.

Ils définissent :

- base visuelle ;
- comportement global ;
- reset ou normalisation ;
- fondations light/dark ;
- typographie de base.

Ils ne doivent pas cibler des composants spécifiques de manière implicite.

## Design tokens

Les design tokens peuvent être définis dans les fondations visuelles.

Ils représentent :

- couleurs ;
- espacements ;
- radius ;
- typographie ;
- z-index ;
- transitions ;
- ombres.

Ce document ne définit pas les tokens eux-mêmes. Il définit uniquement leur emplacement conceptuel.

## Conventions

Les conventions de style doivent suivre le Design System.

Règles :

- cohérence light/dark ;
- accessibilité ;
- pas de styles globaux imprévisibles ;
- composants responsables de leur présentation ;
- pas de duplication de règles visuelles critiques.

# assets/

`assets/` contient les ressources visuelles.

## Icônes

Les icônes doivent être cohérentes.

Règles :

- privilégier la bibliothèque d'icônes choisie ;
- stocker uniquement les icônes spécifiques au produit ;
- éviter les doublons ;
- nommer clairement ;
- ne pas utiliser d'icônes comme seule information.

## Images

Les images doivent être optimisées et justifiées.

Usages :

- illustration d'état vide ;
- marque ;
- documentation future ;
- visuels non sensibles.

Interdit :

- capture contenant secret ;
- image contenant token ;
- image contenant configuration sensible.

## Logos

Les logos doivent être centralisés.

Règles :

- versions light/dark si nécessaire ;
- formats adaptés ;
- cohérence ;
- pas de duplication.

## Illustrations

Les illustrations doivent rester sobres.

Elles peuvent aider les empty states, mais ne doivent pas transformer l'application en landing page.

## Règles

Tout asset doit être considéré comme public s'il est servi au navigateur.

Ne jamais stocker dans `assets/` :

- secret ;
- fichier `.env` ;
- token ;
- clé privée ;
- credentials ;
- export d'audit sensible ;
- capture avec données réelles.

# types/

`types/` contient les types partagés.

## Types partagés

Les types partagés doivent être utilisés par plusieurs espaces.

Exemples :

- pagination ;
- erreur normalisée ;
- statut commun ;
- thème ;
- option de select ;
- type de route ;
- session minimale.

Un type utilisé par une seule feature doit rester dans cette feature.

## Types UI

Les types UI décrivent des formes d'affichage partagées.

Exemples :

- option de filtre ;
- badge variant ;
- table column metadata ;
- empty state action ;
- navigation item.

Ils ne doivent pas être confondus avec les DTO API.

## Types techniques

Les types techniques décrivent l'infrastructure frontend.

Exemples :

- error kind ;
- environment kind ;
- provider props ;
- query status abstraction si nécessaire.

## Ce qui ne doit pas être partagé

Ne pas partager prématurément :

- types propres à une feature ;
- DTO spécifiques si non utilisés ailleurs ;
- types de formulaire locaux ;
- types temporaires ;
- types qui forcent le couplage entre features ;
- types backend internes.

Partager un type crée une dépendance. Cette décision doit être volontaire.

# config/

`config/` contient les constantes et paramètres frontend non sensibles.

## Constantes

Constantes possibles :

- limites UI ;
- routes connues ;
- labels de navigation ;
- valeurs de pagination par défaut ;
- options de thème ;
- délais UI non sensibles.

Une constante spécifique à une feature doit rester dans la feature.

## Configuration

La configuration peut inclure :

- base URL publique ;
- environnement ;
- mode de build ;
- comportement d'interface ;
- configuration de monitoring future non sensible.

Toute configuration exposée au frontend est publique.

## Feature flags futurs

Les feature flags pourront gérer :

- notifications ;
- monitoring ;
- analytics ;
- billing ;
- multi-tenant ;
- WebSockets ;
- command palette.

Les feature flags frontend ne sont pas une sécurité. Une fonctionnalité désactivée pour sécurité doit aussi être bloquée backend.

## Environnement

Les variables d'environnement frontend doivent être minimales.

Interdit :

- secret ;
- token ;
- mot de passe ;
- clé privée ;
- chaîne de connexion ;
- credential fournisseur.

Autorisé :

- URL publique ;
- mode ;
- flag non sensible ;
- configuration d'affichage.

# tests/

`tests/` organise les tests transverses.

## Unitaires

Les tests unitaires peuvent vivre :

- près du code testé ;
- dans une structure dédiée si transversal.

Ils couvrent :

- helpers ;
- mappers ;
- validation ;
- formatage ;
- fonctions pures ;
- comportements isolés.

## Intégration

Les tests d'intégration vérifient la collaboration entre plusieurs modules frontend.

Ils couvrent :

- feature avec API mockée ;
- query + UI ;
- mutation + invalidation ;
- formulaire + validation ;
- erreur API + affichage ;
- session expirée.

## E2E

Les tests end-to-end couvrent les parcours utilisateur.

Parcours prioritaires :

- login ;
- création vault ;
- création project ;
- création secret ;
- création version ;
- reveal secret ;
- création API key ;
- révocation API key ;
- audit logs ;
- modification RBAC.

## Fixtures

Les fixtures représentent des données de test.

Règles :

- données réalistes ;
- aucun vrai secret ;
- aucun vrai token ;
- cas succès ;
- cas erreur ;
- cas permission refusée ;
- cas empty.

## Mocks

Les mocks simulent les réponses API.

Règles :

- alignement avec DTO ;
- erreurs typées ;
- pagination ;
- refus ;
- session expirée ;
- absence de valeurs sensibles réelles.

Les mocks ne doivent pas devenir une API parallèle non maintenue.

# Nommage

Le nommage doit être cohérent et lisible.

## Dossiers

Les dossiers doivent porter des noms :

- courts ;
- explicites ;
- en anglais ;
- alignés avec le domaine ;
- stables.

Éviter :

- noms vagues ;
- abréviations ;
- noms temporaires ;
- catégories fourre-tout.

## Composants

Les composants utilisent des noms descriptifs.

Règles :

- nom en PascalCase ;
- suffixe explicite si utile ;
- nom orienté rôle ;
- pas de nom trop générique pour un composant métier.

Exemples de logique de nommage :

- composant partagé : Button, Dialog, DataTable ;
- composant métier : SecretMetadataCard, ApiKeyDialog, AuditTimeline.

## Hooks

Les hooks doivent exprimer leur usage.

Règles :

- préfixe use ;
- nom précis ;
- différencier lecture, mutation et comportement UI ;
- hooks métier dans feature ;
- hooks partagés dans `hooks/`.

## Types

Les types doivent indiquer leur nature.

Règles :

- distinguer DTO ;
- distinguer UI Model ;
- distinguer Form Model ;
- distinguer Error Type ;
- éviter les noms trop larges comme Data ou Item sans contexte.

## Providers

Les providers doivent être nommés selon leur responsabilité.

Règles :

- suffixe Provider ;
- nom clair ;
- pas de provider global vague ;
- scope explicite si provider local.

## Utilitaires

Les utilitaires doivent être nommés selon l'action.

Règles :

- nom verbal ou descriptif ;
- pas de helpers anonymes ;
- pas de fichier utils trop large ;
- domaine clair.

## Tests

Les tests doivent indiquer le comportement testé.

Règles :

- noms compréhensibles ;
- scénario utilisateur lorsque pertinent ;
- distinction unit, integration, e2e ;
- fixtures nommées par cas.

# Dépendances

Les dépendances doivent suivre une direction claire.

## Dépendances autorisées

Règles générales :

- `app/` peut composer `features/`, `components/`, `providers/`, `lib/` et `types/` ;
- `features/` peuvent utiliser `components/`, `hooks/`, `lib/`, `types/` et `config/` ;
- `components/` peuvent utiliser `lib/`, `hooks/`, `types/` et `styles/` ;
- `hooks/` peuvent utiliser `lib/` et `types/` ;
- `providers/` peuvent utiliser `lib/`, `types/`, `config/` et certains hooks partagés ;
- `lib/` peut utiliser `types/` et `config/` ;
- `tests/` peuvent importer les modules nécessaires selon le niveau de test.

## Dépendances interdites

Interdictions :

- `components/` importe `features/` ;
- `lib/` importe `components/` ;
- `lib/` importe `features/` ;
- une feature importe des détails internes d'une autre feature ;
- imports circulaires ;
- services API appelés depuis composants de présentation ;
- logique métier dans composants partagés ;
- providers globaux dépendant de features spécifiques ;
- styles globaux ciblant des composants métier sans contrat.

## Dépendances entre features

Les dépendances directes entre features doivent être évitées.

Si une feature a besoin d'une autre :

- utiliser navigation ;
- passer par une API backend ;
- extraire un composant réellement partagé ;
- extraire un type commun si justifié ;
- définir une API publique de feature avec prudence.

# Imports

Les imports doivent rester lisibles et respecter les frontières.

## Imports absolus

Les imports absolus peuvent être utilisés pour les grands espaces du projet.

Objectifs :

- éviter les chemins relatifs profonds ;
- clarifier la provenance ;
- faciliter les refactorisations ;
- rendre les dépendances visibles.

Les aliases doivent être peu nombreux et stables.

## Imports relatifs

Les imports relatifs sont adaptés aux fichiers proches.

Bon usage :

- composants d'une même feature ;
- fichiers voisins ;
- tests proches ;
- sous-modules locaux.

Mauvais usage :

- longs chemins fragiles ;
- remontées nombreuses ;
- accès profond à une autre feature.

## Aliases

Les aliases doivent refléter les espaces principaux.

Ils ne doivent pas masquer des dépendances interdites.

Un alias ne rend pas acceptable un import cross-feature non prévu.

## Imports croisés

Les imports croisés entre features sont dangereux.

Règles :

- éviter par défaut ;
- utiliser uniquement un point d'entrée public si nécessaire ;
- documenter les exceptions importantes ;
- refactoriser vers shared ou backend si la dépendance devient forte.

# Évolutivité

La structure doit évoluer sans se dégrader.

## Nouvelles features

Une nouvelle feature doit :

- avoir un domaine clair ;
- regrouper ses éléments ;
- éviter de modifier des dossiers partagés sans nécessité ;
- exposer seulement ce qui doit être consommé ;
- inclure tests adaptés ;
- respecter API integration et security.

Si une feature devient trop large, elle peut être subdivisée en sous-domaines internes.

## Nouveaux composants

Un nouveau composant partagé doit être créé lorsque :

- le besoin existe dans plusieurs endroits ;
- le pattern est stable ;
- la responsabilité est générique ;
- l'accessibilité peut être garantie ;
- il améliore la cohérence.

Sinon, le composant doit rester dans la feature.

## Nouveaux providers

Un nouveau provider doit être justifié.

Questions à poser :

- l'état est-il vraiment global ;
- peut-il rester local à une feature ;
- crée-t-il un couplage ;
- contient-il des données sensibles ;
- comment est-il testé ;
- comment est-il nettoyé au logout.

## Nouveaux modules

Un nouveau module dans `lib/`, `config/`, `types/` ou `hooks/` doit avoir une responsabilité claire.

Il ne doit pas être créé pour éviter de choisir un domaine.

## Évolution sans casser

Pour faire évoluer la structure :

- déplacer progressivement ;
- préserver les contrats publics ;
- éviter les refactors massifs inutiles ;
- supprimer les anciennes abstractions ;
- documenter les changements majeurs ;
- garder les tests verts.

# Anti-patterns

Les anti-patterns suivants doivent être évités.

- Composants géants qui mélangent UI, API, état, validation et permissions.
- Dossier `utils` fourre-tout.
- Dossier `shared` utilisé comme poubelle.
- Logique métier dans `components/`.
- Appels API dans composants de présentation.
- Services API qui décident des permissions.
- Features qui importent les détails internes d'autres features.
- Imports circulaires.
- Duplications de logique de mapping.
- Duplications de composants avec variations mineures.
- Providers globaux inutiles.
- Types partagés prématurément.
- Config contenant des secrets.
- Assets contenant des captures réelles sensibles.
- Tests basés sur des données secrètes réelles.
- Styles globaux qui modifient implicitement des composants.
- Pages `app/` contenant toute l'implémentation d'une feature.
- Mappers qui inventent des états métier.
- Feature flags frontend utilisés comme sécurité.
- Hooks globaux contenant du domaine.
- Couche API mélangée à l'UI.
- Barrel exports trop larges qui masquent les dépendances.
- Aliases utilisés pour contourner les frontières.
- Dossiers nommés `misc`, `common`, `helpers` sans responsabilité précise.

# Repository Principles

Les règles suivantes guident toute évolution du dépôt frontend.

- Une responsabilité par dossier.
- Une feature reste autonome.
- La composition est privilégiée.
- La duplication temporaire est acceptable avant une abstraction prématurée.
- Shared reste générique.
- Les composants partagés ne contiennent pas de logique métier.
- Les hooks métier restent dans les features.
- Les hooks partagés restent techniques ou UI.
- L'infrastructure reste isolée.
- Le client HTTP reste centralisé.
- Les DTO restent à la frontière API.
- Les modèles UI ne sont pas des entités backend.
- Aucune dépendance circulaire.
- Les dépendances entre features sont évitées.
- Les imports respectent les frontières.
- Les providers globaux sont rares et justifiés.
- Les types ne sont partagés que lorsqu'ils sont réellement transverses.
- Les assets ne contiennent jamais de données sensibles.
- La config frontend ne contient jamais de secret.
- Les tests utilisent des fixtures sûres.
- Les dossiers doivent être faciles à découvrir.
- Toute nouvelle abstraction doit réduire une complexité réelle.
- Toute exception structurelle doit être justifiée.

# Conclusion

La structure du dépôt frontend de MCP Secret Manager doit servir la clarté, la sécurité et l'évolution du produit.

Elle repose sur une organisation Feature First, complétée par des espaces transverses strictement définis : routing dans `app/`, domaines dans `features/`, composants réutilisables dans `components/`, infrastructure dans `lib/`, hooks globaux dans `hooks/`, providers dans `providers/`, fondations visuelles dans `styles/`, assets publics dans `assets/`, types partagés dans `types/`, configuration non sensible dans `config/` et tests transverses dans `tests/`.

Cette structure évite les responsabilités floues. Elle aide les développeurs à trouver rapidement le bon endroit, limite les dépendances croisées, protège les composants partagés contre la logique métier et prépare les évolutions futures sans refonte majeure.

Le principe directeur est simple : chaque dossier doit avoir une raison d'exister, chaque feature doit rester cohérente, chaque dépendance doit être explicite et aucune facilité locale ne doit affaiblir l'architecture globale du frontend.
