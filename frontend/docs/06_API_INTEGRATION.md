# Introduction

Ce document définit la stratégie officielle d'intégration entre le frontend de MCP Secret Manager et le backend.

Il ne décrit pas l'API backend elle-même. Les ressources, permissions, invariants, erreurs métier et contrats fonctionnels backend sont documentés séparément. Le présent document décrit uniquement les responsabilités du frontend lorsqu'il consomme cette API.

La couche API frontend a un rôle précis : fournir une frontière stable, typée et testable entre l'interface React et les endpoints backend. Elle transforme des intentions UI en requêtes HTTP, reçoit des réponses, normalise les erreurs, expose les données au Query Layer et prépare les modèles nécessaires à l'affichage.

La couche API est isolée de l'UI pour éviter que les composants ne connaissent les détails techniques de communication :

- construction d'URL ;
- headers ;
- credentials ;
- cookies ;
- pagination ;
- parsing ;
- retries ;
- erreurs HTTP ;
- mapping DTO ;
- invalidation de cache.

Cette isolation rend le frontend plus maintenable. Un changement de contrat API, de format d'erreur, de pagination ou de stratégie d'authentification doit avoir un impact localisé. Les composants doivent rester concentrés sur l'expérience utilisateur, pas sur la mécanique réseau.

La couche API ne contient aucune logique métier.

Elle ne décide pas si un utilisateur peut lire un secret, créer une API key, modifier un rôle, archiver un vault ou révéler une valeur. Ces décisions appartiennent au backend. Le frontend ne fait que transmettre la requête, afficher la réponse, gérer les refus et adapter l'expérience utilisateur.

Le backend est l'autorité. Le frontend est un consommateur sécurisé et discipliné.

# Principes généraux

Les principes suivants sont obligatoires pour toute intégration API côté frontend.

## Backend = source de vérité

Le backend est la source de vérité pour :

- données métier ;
- permissions ;
- authentification ;
- session ;
- audit ;
- validation ;
- chiffrement ;
- états des ressources ;
- refus d'accès ;
- règles de sécurité.

Le frontend ne doit jamais considérer son état local comme une vérité définitive. Le cache client est un outil d'expérience, pas une autorité.

Après une mutation sensible, l'UI doit s'aligner sur l'état confirmé par le backend.

## Frontend = consommateur

Le frontend consomme les endpoints exposés par le backend.

Son rôle est de :

- demander des données ;
- soumettre des intentions utilisateur ;
- afficher les réponses ;
- présenter les erreurs ;
- mettre à jour ou invalider le cache ;
- guider l'utilisateur ;
- éviter les fuites accidentelles.

Le frontend ne doit pas contourner l'API en simulant des décisions ou en reconstruisant des états métier non confirmés.

## Aucune logique métier

La couche API frontend ne contient pas de logique métier.

Elle ne doit pas :

- calculer une autorisation ;
- déduire un droit à partir d'un rôle supposé ;
- décider qu'une action sensible doit être autorisée ;
- simuler un état backend ;
- valider une règle de sécurité comme vérité finale ;
- déclencher un audit local autonome.

Elle peut :

- valider des entrées pour améliorer l'UX ;
- adapter une réponse à un format UI ;
- afficher une permission fournie par le backend ;
- gérer un refus ;
- normaliser des erreurs.

La différence est fondamentale : améliorer l'expérience n'est pas remplacer le domaine backend.

## DTO uniquement

La communication avec le backend passe par des DTO.

Les DTO représentent les formes de requêtes et réponses API. Ils ne sont pas les entités backend internes. Ils ne doivent pas être confondus avec :

- modèles de domaine backend ;
- modèles UI ;
- état de formulaire ;
- entités persistées ;
- objets métier internes.

Le frontend doit manipuler des Request DTO et Response DTO au niveau de la couche API, puis les transformer en modèles adaptés à l'interface lorsque nécessaire.

## Séparation stricte UI/API

L'UI ne construit pas directement les requêtes HTTP.

Les composants de présentation ne doivent jamais :

- appeler fetch ou un client HTTP ;
- connaître les endpoints ;
- construire des headers ;
- interpréter des codes HTTP ;
- gérer des retries ;
- mapper des DTO complexes ;
- contenir une logique de refresh de session.

Les composants connectés aux données passent par le Query Layer, les hooks de feature ou les services adaptés.

## Architecture orientée contrats

Le frontend doit être construit autour de contrats explicites.

Les contrats incluent :

- DTO de requête ;
- DTO de réponse ;
- types d'erreur ;
- paramètres de pagination ;
- paramètres de recherche ;
- statuts ;
- modèles UI ;
- query keys ;
- règles d'invalidation.

Une architecture orientée contrats facilite :

- les tests ;
- la revue ;
- les refactorisations ;
- la compatibilité ;
- l'intégration avec le backend ;
- la détection des ruptures.

# Architecture de la couche API

La couche API est composée de plusieurs responsabilités distinctes :

- API Client ;
- Services ;
- DTO ;
- Mappers ;
- Query Layer ;
- Mutation Layer ;
- Error Layer.

Ces responsabilités peuvent être réparties dans différents fichiers ou modules selon l'organisation finale, mais leurs frontières doivent rester claires.

## API Client

L'API Client est le point d'accès HTTP central.

Responsabilités :

- appliquer la base URL ;
- ajouter les headers communs ;
- gérer les credentials ;
- parser les réponses ;
- normaliser les erreurs techniques ;
- appliquer les timeouts ;
- appliquer une politique de retry contrôlée ;
- gérer les comportements transverses.

L'API Client ne connaît pas les features métier. Il fournit une capacité technique de communication.

Il ne doit pas :

- décider des permissions ;
- transformer une réponse en composant UI ;
- afficher une notification ;
- contenir des règles de vault, project, secret ou RBAC ;
- stocker des valeurs secrètes.

## Services

Les Services regroupent les appels API par domaine fonctionnel.

Exemples conceptuels :

- service vault ;
- service project ;
- service secret ;
- service API key ;
- service audit ;
- service RBAC ;
- service session ;
- service settings.

Responsabilités :

- exposer des fonctions d'appel API par ressource ;
- recevoir des Request DTO ;
- retourner des Response DTO ;
- centraliser les chemins d'endpoint ;
- rester indépendants de l'UI.

Les Services ne contiennent pas de logique métier. Ils ne font pas d'autorisation. Ils ne décident pas qu'une ressource est modifiable. Ils envoient une requête et retournent une réponse ou une erreur.

## DTO

Les DTO définissent la forme des données échangées avec le backend.

Responsabilités :

- représenter les payloads d'entrée ;
- représenter les payloads de sortie ;
- typer les paramètres ;
- documenter les champs optionnels ;
- isoler l'UI du format backend brut.

Les DTO vivent à la frontière API. Ils ne doivent pas envahir toute l'UI lorsque des modèles d'affichage plus adaptés sont nécessaires.

## Mappers

Les Mappers transforment les DTO en modèles UI et les modèles de formulaire en DTO.

Responsabilités :

- normaliser les dates ;
- fournir des valeurs par défaut d'affichage ;
- adapter les noms de champs ;
- convertir les statuts en modèles d'affichage ;
- traiter les champs optionnels ;
- préserver la distinction metadata/value ;
- éviter que les composants ne connaissent les détails DTO.

Les Mappers ne doivent pas inventer de données métier. Ils ne doivent pas accorder une permission, changer un statut ou masquer un refus backend.

## Query Layer

Le Query Layer coordonne les lectures de données côté client, principalement avec TanStack Query.

Responsabilités :

- définir les query keys ;
- appeler les Services ;
- gérer cache ;
- gérer loading ;
- gérer erreurs ;
- gérer refetch ;
- gérer prefetch ;
- exposer des hooks de lecture aux features ;
- appliquer les paramètres de recherche, filtres et pagination.

Le Query Layer doit rester proche des features lorsque les données sont spécifiques à une feature.

## Mutation Layer

Le Mutation Layer coordonne les écritures et actions côté client.

Responsabilités :

- appeler les Services de mutation ;
- gérer loading ;
- gérer erreurs ;
- invalider les caches appropriés ;
- déclencher feedback UI via la feature ;
- éviter les doubles soumissions ;
- encadrer les actions sensibles.

Les mutations sensibles ne doivent pas utiliser des optimistic updates sauf justification explicite et validation produit/sécurité.

## Error Layer

L'Error Layer normalise les erreurs provenant du backend ou du réseau.

Responsabilités :

- distinguer erreurs réseau ;
- distinguer erreurs HTTP ;
- distinguer validation ;
- distinguer authentification ;
- distinguer autorisation ;
- distinguer ressource introuvable ;
- distinguer conflit ;
- distinguer indisponibilité ;
- fournir des messages UI sûrs ;
- préserver des informations techniques non sensibles pour monitoring futur.

L'Error Layer ne doit jamais exposer de secret, token, payload sensible, stack trace brute ou détail interne dangereux.

# HTTP Client

Le HTTP Client est unique et centralisé.

Il constitue la base technique de toutes les communications avec le backend.

## Client HTTP unique

Un seul client HTTP doit porter les comportements transverses.

Objectifs :

- cohérence ;
- gestion commune des erreurs ;
- politique de retry maîtrisée ;
- configuration unique ;
- meilleure testabilité ;
- réduction des duplications.

Créer plusieurs clients concurrents introduit des risques :

- headers incohérents ;
- credentials oubliés ;
- erreurs mal normalisées ;
- retries dangereux ;
- logique dupliquée ;
- comportement différent selon les features.

Des clients spécialisés peuvent exister uniquement s'ils partagent une base commune et répondent à un besoin clairement identifié, par exemple uploads futurs ou streaming futur.

## Configuration

La configuration du client doit être explicite et centralisée.

Elle inclut :

- base URL ;
- environnement ;
- timeouts ;
- credentials ;
- headers communs ;
- politique de retry ;
- stratégie de parsing ;
- stratégie d'erreur.

La configuration ne doit jamais inclure de secret côté client.

Les variables exposées au navigateur doivent être considérées comme publiques.

## Base URL

La base URL définit l'origine de l'API backend.

Règles :

- être configurable par environnement ;
- ne pas être codée en dur dans les composants ;
- ne pas contenir de token ;
- être validée lors de l'initialisation ;
- rester compatible avec déploiement SaaS, auto-hébergé ou reverse proxy.

Le frontend ne doit pas construire des URLs sensibles à la main dans les composants.

## Timeout

Les timeouts évitent les requêtes bloquées indéfiniment.

Principes :

- timeout raisonnable pour lectures ordinaires ;
- timeout adapté pour opérations longues futures ;
- feedback utilisateur clair ;
- possibilité de retry pour lectures non sensibles ;
- prudence sur mutations.

Un timeout ne signifie pas forcément que l'action backend n'a pas été exécutée. Pour une mutation sensible, l'UI doit éviter d'affirmer un échec définitif si l'état serveur est incertain. Elle doit proposer un rafraîchissement ou vérifier l'état.

## Headers

Les headers communs peuvent inclure :

- type de contenu ;
- accept ;
- informations de corrélation futures ;
- version client future ;
- protection CSRF selon stratégie backend.

Ils ne doivent pas inclure :

- secret ;
- token exposé inutilement ;
- valeur de secret ;
- donnée utilisateur sensible non nécessaire.

## Cookies

Les cookies sécurisés sont la stratégie privilégiée pour la session web.

Le frontend doit :

- envoyer les credentials lorsque nécessaire ;
- s'appuyer sur les cookies HttpOnly si disponibles ;
- ne pas lire les tokens de session en JavaScript ;
- gérer les expirations ;
- déclencher logout propre.

Les cookies ne doivent pas conduire le frontend à considérer une session comme valide sans confirmation backend.

## Credentials

Les credentials doivent être gérés de manière uniforme.

Règles :

- inclure credentials selon configuration ;
- ne pas exposer tokens dans localStorage ;
- ne pas mettre de tokens dans les URLs ;
- ne pas dupliquer les secrets de session ;
- nettoyer le cache à logout.

## Interceptors

Les interceptors ou mécanismes équivalents peuvent servir à :

- ajouter headers communs ;
- normaliser réponses ;
- normaliser erreurs ;
- gérer expiration ;
- déclencher refresh contrôlé ;
- ajouter corrélation future.

Ils ne doivent pas :

- masquer toutes les erreurs ;
- relancer des mutations dangereuses ;
- afficher des toasts depuis la couche HTTP globale ;
- contenir des règles métier ;
- logger des payloads sensibles.

## Retry policy

La politique de retry doit être restrictive.

Retries possibles :

- lectures idempotentes ;
- erreurs réseau temporaires ;
- indisponibilité courte ;
- endpoints de statut.

Retries à éviter :

- création de secret ;
- création de version ;
- création d'API key ;
- révocation ;
- modification RBAC ;
- révélation de secret ;
- mutation non idempotente.

Le retry ne doit jamais déclencher deux fois une action sensible.

# Authentication

L'authentification frontend gère l'état de session de l'utilisateur et l'accès aux routes protégées.

Elle ne gère pas les permissions métier.

## Cookies sécurisés

La stratégie privilégiée repose sur des cookies sécurisés.

Le frontend doit :

- s'appuyer sur les cookies émis par le backend ou la couche serveur ;
- inclure les credentials dans les requêtes nécessaires ;
- ne pas stocker de token de session dans localStorage ;
- ne pas exposer le refresh token à JavaScript ;
- gérer les erreurs d'authentification.

Le détail de configuration des cookies appartient au backend et à la configuration de déploiement. Le frontend doit respecter cette stratégie.

## Session

La session côté frontend représente un état utilisateur minimal.

Elle peut contenir :

- identifiant utilisateur ;
- nom ou email ;
- état authentifié ;
- informations de profil non sensibles ;
- expiration approximative si disponible ;
- contexte tenant futur.

Elle ne doit pas contenir :

- refresh token ;
- access token lisible si évitable ;
- API key ;
- secret ;
- permissions interprétées comme vérité finale non confirmée.

La session doit être vérifiée par le backend.

## Refresh

Le refresh de session doit être centralisé.

Responsabilités frontend :

- détecter expiration ou réponse d'authentification invalide ;
- appeler le mécanisme de refresh si prévu ;
- éviter les boucles ;
- éviter les refresh concurrents incontrôlés ;
- réessayer une lecture sûre si le refresh réussit ;
- rediriger vers Login si le refresh échoue ;
- nettoyer les caches sensibles si la session est terminée.

Le refresh ne doit pas être utilisé pour masquer indéfiniment une session invalide.

## Expiration

En cas d'expiration :

- l'utilisateur doit être informé ;
- les requêtes sensibles doivent être stoppées ;
- les caches doivent être nettoyés selon le niveau de risque ;
- les valeurs révélées doivent être supprimées ;
- la redirection vers Login doit préserver la destination seulement si c'est sûr.

Une mutation échouée par expiration ne doit pas être présentée comme réussie.

## Logout

Le logout doit :

- appeler l'endpoint backend si nécessaire ;
- invalider la session ;
- nettoyer TanStack Query ;
- nettoyer états UI sensibles ;
- fermer dialogs contenant des valeurs ;
- rediriger vers Login ;
- empêcher le retour visuel vers données sensibles via cache.

Le logout est une action de sécurité et doit être fiable.

## Récupération du profil

La récupération du profil sert à afficher l'utilisateur connecté et initialiser l'expérience.

Le profil doit rester minimal :

- nom ;
- email ;
- rôle résumé si backend le fournit ;
- préférences ;
- informations non sensibles.

Le frontend ne doit pas déduire toutes les permissions à partir du profil. Les permissions effectives doivent être fournies par les endpoints appropriés ou validées action par action par le backend.

# DTO

Les DTO sont les contrats de transport entre frontend et backend.

Ils doivent rester distincts des entités backend et des modèles UI.

## Philosophie

Un DTO décrit une forme de données échangée.

Il répond à la question :

- qu'est-ce que le frontend envoie ;
- qu'est-ce que le frontend reçoit.

Il ne répond pas à la question :

- quelle est l'entité interne backend ;
- comment l'UI doit afficher la donnée ;
- quelles règles métier doivent être appliquées.

Cette séparation protège le frontend contre une dépendance excessive aux détails internes backend.

## Request DTO

Les Request DTO représentent les données envoyées au backend.

Exemples conceptuels :

- création de vault ;
- modification de project ;
- création de secret ;
- création de version ;
- création d'API key ;
- filtre d'audit ;
- assignment RBAC.

Responsabilités :

- contenir uniquement les champs attendus ;
- exclure les données UI inutiles ;
- respecter les noms et formats du contrat API ;
- ne pas inclure d'information sensible non nécessaire ;
- être construits par mappers ou services adaptés.

## Response DTO

Les Response DTO représentent les données reçues.

Responsabilités :

- refléter le contrat API ;
- porter les champs optionnels explicitement ;
- distinguer metadata et value ;
- représenter les statuts ;
- permettre au mapper de produire un modèle UI.

Le frontend doit être robuste face aux champs optionnels et aux évolutions compatibles.

## Validation

La validation des DTO côté frontend peut servir à :

- sécuriser les formulaires ;
- détecter une réponse inattendue ;
- améliorer les messages utilisateur ;
- éviter des requêtes invalides ;
- protéger les composants contre des données manquantes.

Elle ne remplace jamais la validation backend.

Pour les réponses API, la validation runtime peut être utilisée sur les frontières critiques ou lorsque la robustesse est nécessaire.

## Évolution

Les DTO doivent pouvoir évoluer.

Évolutions compatibles :

- ajout de champ optionnel ;
- ajout de statut reconnu mais non utilisé ;
- ajout de metadata ;
- ajout de pagination enrichie.

Évolutions potentiellement incompatibles :

- suppression de champ requis ;
- changement de type ;
- changement de sémantique ;
- renommage ;
- changement de pagination ;
- modification du format d'erreur.

Le frontend doit localiser l'impact des évolutions dans les DTO, mappers et services.

## Compatibilité

Le frontend doit viser une compatibilité stricte avec la version d'API supportée.

Règles :

- ne pas consommer des champs non documentés ;
- ne pas dépendre d'un détail accidentel ;
- gérer les champs optionnels ;
- afficher une erreur sûre si le contrat attendu n'est pas respecté ;
- coordonner les changements avec l'équipe backend.

## Pourquoi ne jamais manipuler directement les entités backend

Les entités backend appartiennent au domaine serveur.

Le frontend ne doit pas les manipuler directement parce que :

- il ne connaît pas les invariants internes ;
- il ne porte pas la logique métier ;
- il ne doit pas dépendre de la structure de persistance ;
- il affiche souvent une version adaptée à l'UX ;
- il doit rester découplé de l'architecture interne backend ;
- il doit pouvoir évoluer avec les contrats API.

Le frontend manipule des DTO et des modèles UI, pas des entités de domaine backend.

# Mapping

Le mapping relie la couche API à l'interface.

Il transforme des données de transport en données affichables, et des intentions UI en payloads acceptés par l'API.

## DTO → UI Model

Le mapping DTO vers UI Model prépare les données pour l'affichage.

Responsabilités :

- formater les dates ;
- convertir les statuts en labels ;
- préparer les badges ;
- calculer les champs d'affichage ;
- gérer les champs manquants ;
- normaliser les valeurs optionnelles ;
- préserver les identifiants nécessaires ;
- séparer valeurs sensibles et metadata.

Le UI Model doit faciliter le rendu sans cacher la vérité serveur.

## UI Model → DTO

Le mapping UI Model ou Form Model vers DTO prépare les requêtes.

Responsabilités :

- retirer les champs purement UI ;
- convertir formats de dates ;
- convertir sélections en identifiants ;
- construire les scopes ;
- préparer les filtres ;
- inclure uniquement les champs requis ;
- éviter l'envoi de données sensibles inutiles.

Le mapper doit être explicite. Un formulaire ne doit pas envoyer tout son état local par facilité.

## Normalisation

La normalisation rend les données prévisibles.

Exemples :

- date convertie dans un format attendu ;
- statut inconnu traité comme état fallback ;
- champ optionnel remplacé par valeur d'affichage neutre ;
- tableau absent converti en liste vide pour l'UI ;
- libellé technique adapté à un label utilisateur.

La normalisation ne doit pas modifier le sens métier.

## Valeurs par défaut

Les valeurs par défaut doivent être uniquement des valeurs d'affichage ou de formulaire.

Exemples acceptables :

- description absente affichée comme non renseignée ;
- liste vide ;
- badge unknown ;
- compteur non disponible ;
- filtre initial.

Exemples interdits :

- supposer qu'une ressource est active si le statut manque ;
- supposer qu'une permission est accordée ;
- supposer qu'une API key est valide ;
- supposer qu'un secret possède une version courante ;
- remplacer une valeur secrète absente par un placeholder trompeur.

## Gestion des champs optionnels

Les champs optionnels doivent être traités avec prudence.

Règles :

- distinguer absent, null, vide et non autorisé si le contrat le permet ;
- ne pas afficher une absence comme une erreur si elle est normale ;
- ne pas inventer une information ;
- utiliser un fallback visuel neutre ;
- conserver la possibilité d'évolution API.

# TanStack Query

TanStack Query gère l'état serveur côté client.

Il ne remplace pas l'API layer. Il orchestre lectures, mutations, cache, invalidation et refetch autour des services.

## Queries

Les queries sont utilisées pour les lectures.

Cas d'usage :

- lister vaults ;
- lire vault details ;
- lister projects ;
- lire secret metadata ;
- lister versions ;
- lister API keys ;
- lister audit logs ;
- lire profil ;
- lire settings.

Règles :

- query keys stables ;
- paramètres inclus dans la clé ;
- erreurs gérées ;
- données sensibles exclues du cache durable ;
- séparation par utilisateur et tenant futur.

## Mutations

Les mutations sont utilisées pour les écritures ou actions.

Cas d'usage :

- créer ;
- modifier ;
- archiver ;
- supprimer logiquement ;
- révoquer ;
- créer version ;
- créer API key ;
- reveal ;
- logout.

Règles :

- loading explicite ;
- erreurs explicites ;
- invalidation ciblée ;
- absence d'optimistic update pour actions sensibles ;
- prévention des doubles soumissions.

## Cache

Le cache améliore la performance et l'expérience.

Règles :

- cacher metadata autorisées ;
- ne pas cacher durablement les valeurs secrètes ;
- invalider après mutation ;
- nettoyer à logout ;
- isoler par session ;
- préparer isolation multi-tenant future.

Le cache est temporaire et subordonné à l'API.

## Invalidation

Une mutation doit invalider les données affectées.

Exemples :

- création vault invalide liste vaults et dashboard ;
- création project invalide projects du vault, project list et dashboard ;
- création secret invalide secret list, project details et dashboard ;
- création version invalide secret details et version history ;
- révocation API key invalide API keys et audit récent ;
- modification RBAC invalide RBAC views et permissions effectives ;
- changement settings invalide settings et éventuellement session.

L'invalidation doit être précise sans devenir fragile.

## Refetch

Le refetch est utilisé pour actualiser une donnée.

Cas d'usage :

- retour de focus ;
- action utilisateur "refresh" ;
- après expiration courte ;
- après mutation ;
- après reconnect réseau ;
- données d'audit ou monitoring futures.

Le refetch ne doit pas être agressif sur des données coûteuses ou sensibles.

## Prefetch

Le prefetch peut améliorer la navigation.

Cas d'usage :

- précharger détails au hover ou focus d'une ligne ;
- précharger page suivante ;
- précharger ressources liées ;
- précharger settings ou profil.

Règles :

- prefetch uniquement metadata ou données non sensibles ;
- jamais de prefetch de secret value ;
- respecter permissions ;
- éviter surcharge réseau.

## Background Refresh

Le background refresh maintient certaines vues à jour.

Cas d'usage :

- dashboard ;
- audit logs récents ;
- API keys status ;
- notifications futures ;
- monitoring futur.

Règles :

- fréquence raisonnable ;
- pause si onglet inactif selon comportement choisi ;
- pas de refresh de secret value ;
- feedback discret.

## Optimistic Updates

Les optimistic updates affichent un résultat avant confirmation backend.

Utilisation possible :

- préférence UI non critique ;
- filtre local ;
- changement visuel réversible ;
- action faible impact si validée par produit.

À éviter pour :

- création de secret ;
- création de version ;
- reveal ;
- copy liée à secret value ;
- révocation API key ;
- modification RBAC ;
- archivage ;
- suppression logique ;
- verrouillage ;
- settings sécurité.

Pour les actions sensibles, attendre le backend est obligatoire.

# Gestion des erreurs

La gestion des erreurs doit être explicite, sûre et cohérente.

Chaque type d'erreur doit produire un comportement UI adapté.

## Erreurs réseau

Description :

- backend inaccessible ;
- timeout ;
- perte de connexion ;
- proxy indisponible ;
- navigateur offline.

Comportement UI attendu :

- afficher une erreur réseau claire ;
- proposer retry pour lectures ;
- éviter retry automatique sur mutations sensibles ;
- conserver le contexte ;
- ne pas afficher de détails techniques bruts.

## Erreurs HTTP

Description :

- code HTTP indiquant validation, authentification, autorisation, not found, conflit ou serveur.

Comportement UI attendu :

- mapper vers une erreur typée ;
- afficher un message adapté ;
- déclencher redirection si session invalide ;
- afficher ForbiddenState ou NotFoundState si nécessaire ;
- préserver les données existantes si pertinent.

## Erreurs métier

Description :

- conflit de nom ;
- ressource archivée ;
- vault locked ;
- action impossible ;
- version invalide ;
- clé déjà révoquée.

Comportement UI attendu :

- message contextualisé ;
- action de correction ;
- état visuel cohérent ;
- pas de détail interne.

Le frontend affiche ces erreurs. Il ne les résout pas en contournant le backend.

## Validation

Description :

- champs invalides ;
- champ requis ;
- format incorrect ;
- longueur incorrecte ;
- payload refusé.

Comportement UI attendu :

- erreurs proches des champs ;
- erreurs globales si nécessaire ;
- conservation des saisies non sensibles ;
- nettoyage des valeurs sensibles selon risque ;
- messages utiles.

Les erreurs backend de validation doivent être affichées même si la validation frontend avait réussi.

## Authentification

Description :

- session absente ;
- session expirée ;
- refresh échoué ;
- login invalide.

Comportement UI attendu :

- redirection Login ;
- message session expirée ;
- nettoyage cache ;
- fermeture dialogs sensibles ;
- aucune donnée protégée visible après logout.

## Permissions

Description :

- action refusée ;
- ressource non accessible ;
- permission insuffisante ;
- RBAC modifié pendant la session.

Comportement UI attendu :

- afficher ForbiddenState ou message local ;
- ne pas masquer silencieusement ;
- ne pas révéler d'information interdite ;
- invalider permissions si nécessaire ;
- proposer retour ou contact admin.

## Indisponibilité

Description :

- backend down ;
- maintenance ;
- dépendance indisponible ;
- service health dégradé.

Comportement UI attendu :

- message global ou local ;
- retry si pertinent ;
- désactivation d'actions impossibles ;
- conservation de la lisibilité ;
- aucun affichage de données sensibles obsolètes si risque.

# Pagination

La pagination doit être standardisée et compatible avec l'évolution backend.

## Offset

La pagination offset peut être utilisée pour des listes simples.

Cas d'usage :

- vaults ;
- projects ;
- secrets ;
- API keys ;
- rôles ;
- assignments.

Avantages :

- simple ;
- facile à comprendre ;
- compatible avec pages numérotées.

Limites :

- moins performante sur grands volumes ;
- moins stable si les données changent rapidement.

## Cursor

La pagination cursor est préférable pour les flux volumineux ou chronologiques.

Cas d'usage :

- audit logs ;
- monitoring futur ;
- notifications futures ;
- événements temps réel historiques.

Avantages :

- stabilité ;
- performance ;
- meilleure continuité sur flux changeants.

Limites :

- moins intuitive pour pages numérotées ;
- nécessite une UI adaptée.

## Évolution future

Le frontend doit rester capable de supporter les deux modèles.

Règles :

- isoler les détails de pagination dans l'API layer ;
- exposer un modèle UI cohérent ;
- éviter que les composants dépendent directement du format brut ;
- permettre migration offset vers cursor.

## Conservation des filtres

Les filtres doivent être conservés pendant la pagination.

Règles :

- query key inclut filtres ;
- URL peut refléter filtres importants ;
- changement de filtre réinitialise la pagination si nécessaire ;
- retour navigateur préserve le contexte lorsque pertinent.

## Conservation de la recherche

La recherche doit être conservée pendant la pagination.

Règles :

- query key inclut le terme ;
- pagination réagit au terme actif ;
- clear search réinitialise proprement ;
- mobile conserve aussi l'état.

# Recherche

La recherche peut être locale ou serveur selon le volume, la sensibilité et les capacités backend.

La recherche ne doit jamais s'effectuer dans les valeurs secrètes au MVP.

## Recherche locale

La recherche locale est adaptée aux petits volumes déjà chargés.

Cas d'usage :

- options de Select ;
- petites listes de rôles ;
- préférences locales ;
- données non sensibles déjà autorisées.

Règles :

- ne pas chercher dans des champs non affichables ;
- ne pas conserver de données sensibles ;
- rester rapide ;
- indiquer absence de résultat.

## Recherche serveur

La recherche serveur est adaptée aux ressources métier.

Cas d'usage :

- vaults ;
- projects ;
- secrets metadata ;
- API keys metadata ;
- audit logs ;
- actors futurs.

Responsabilités frontend :

- envoyer query ;
- inclure filtres ;
- gérer pagination ;
- afficher loading ;
- afficher empty state ;
- ne pas chercher dans secret values ;
- respecter les résultats autorisés par backend.

## Debounce

Le debounce évite d'envoyer une requête à chaque frappe.

Règles :

- délai court et confortable ;
- feedback visuel si nécessaire ;
- annulation ou ignore des réponses obsolètes ;
- pas de debounce sur soumission explicite si l'utilisateur déclenche une recherche.

## Filtres

Les filtres structurent les recherches.

Responsabilités frontend :

- afficher options autorisées ;
- envoyer paramètres ;
- conserver état ;
- permettre reset ;
- distinguer filtres actifs.

Les filtres ne doivent pas révéler l'existence de ressources non autorisées.

## Tri

Le tri permet de comparer et organiser les résultats.

Responsabilités frontend :

- afficher tri actif ;
- envoyer champ et direction ;
- préserver recherche et filtres ;
- gérer colonnes non triables ;
- afficher fallback si backend refuse.

# Mutations

Les mutations modifient l'état serveur ou déclenchent une action sensible.

Elles doivent être conçues avec prudence.

## Bonnes pratiques générales

Règles :

- une mutation correspond à une intention claire ;
- état loading visible ;
- double soumission empêchée ;
- erreurs affichées explicitement ;
- cache invalidé après succès ;
- action sensible confirmée ;
- pas de payload inutile ;
- pas de logs sensibles.

Une mutation ne doit pas faire plusieurs actions métier indépendantes sauf si le backend expose un workflow atomique.

## Création

Exemples :

- créer vault ;
- créer project ;
- créer secret ;
- créer version ;
- créer API key.

Comportement :

- validation frontend ;
- soumission ;
- attente confirmation backend ;
- invalidation des listes et détails concernés ;
- feedback succès ;
- nettoyage des valeurs sensibles.

Pas d'optimistic update pour création de secret, version ou API key.

## Modification

Exemples :

- modifier metadata ;
- modifier settings ;
- modifier assignment futur.

Comportement :

- conserver contexte ;
- validation ;
- mutation ;
- invalidation ciblée ;
- feedback ;
- gestion conflit.

Optimistic update possible uniquement pour préférences non sensibles.

## Archivage

L'archivage retire une ressource de l'usage courant sans forcément la supprimer.

Comportement :

- confirmation ;
- bouton danger ou warning selon impact ;
- pas d'optimistic update ;
- invalidation liste et détail ;
- badge Archived après confirmation.

## Suppression logique

La suppression logique est plus sensible que l'archivage.

Comportement :

- confirmation forte ;
- rappel de conséquence ;
- pas d'optimistic update ;
- invalidation ;
- état supprimé ou navigation retour selon backend.

## Révocation

La révocation concerne notamment les API keys.

Comportement :

- confirmation forte ;
- indication d'impact sur services ;
- pas d'optimistic update ;
- invalidation API keys ;
- invalidation audit récent ;
- badge Revoked après confirmation.

## Reveal

Reveal est une mutation ou action sensible de lecture selon le contrat backend.

Comportement :

- action explicite ;
- confirmation ou indication audit ;
- appel dédié ;
- pas de prefetch ;
- pas de cache durable ;
- affichage temporaire ;
- nettoyage ;
- gestion permission refusée.

Reveal ne doit jamais être automatique.

## Copy

Copy peut copier une valeur déjà révélée ou déclencher un workflow si la valeur doit être lue.

Comportement :

- action explicite ;
- aucun affichage dans toast ;
- feedback bref ;
- gestion erreur presse-papiers ;
- distinction secret value vs identifiant non sensible.

Copy ne doit pas stocker la valeur.

## Optimistic updates

À utiliser :

- préférence UI ;
- filtre local ;
- action réversible non sensible.

À éviter :

- toute action de sécurité ;
- toute action irréversible ;
- toute action auditée critique ;
- toute action sur secret value ;
- toute révocation ;
- tout RBAC.

# Uploads futurs

Les uploads ne font pas partie du MVP, mais l'architecture doit pouvoir les accueillir.

## Import

Imports possibles futurs :

- import de metadata ;
- import de secrets depuis fichier ;
- import de configuration ;
- migration depuis autre outil.

Responsabilités frontend :

- validation locale de format non sensible ;
- avertissements ;
- aperçu sans exposer inutilement ;
- progression ;
- annulation si possible ;
- erreurs ligne par ligne si applicable ;
- nettoyage du fichier après usage.

Les imports contenant des secrets sont hautement sensibles. Ils ne doivent pas être stockés localement au-delà du strict nécessaire.

## Export

Exports possibles futurs :

- export de metadata ;
- export audit ;
- export configuration non sensible ;
- rapports.

Règles :

- aucun export bulk de valeurs secrètes au MVP ;
- confirmation pour exports sensibles ;
- respect permissions backend ;
- logs sans contenu sensible ;
- nom de fichier non révélateur si contexte sensible.

## Fichiers

Gestion fichiers :

- taille maximale ;
- type autorisé ;
- validation ;
- feedback ;
- erreurs ;
- nettoyage ;
- aucun fichier sensible dans stockage local permanent.

## Streaming

Le streaming futur peut servir à :

- gros exports ;
- imports longs ;
- monitoring ;
- logs ;
- progression.

Responsabilités frontend :

- afficher progression ;
- gérer annulation ;
- gérer erreurs partielles ;
- éviter rétention de données sensibles ;
- conserver l'accessibilité.

# WebSockets futurs

Les WebSockets ne font pas partie du MVP, mais l'architecture prévoit leur ajout.

Ils doivent être utilisés de manière ciblée, pas comme remplacement global de TanStack Query.

## Stratégie prévue

Les WebSockets pourront fournir des événements temps réel.

Responsabilités frontend :

- connecter après authentification ;
- gérer reconnexion ;
- gérer expiration session ;
- écouter événements autorisés ;
- invalider caches concernés ;
- afficher notifications ;
- éviter données sensibles dans payloads.

Le backend reste responsable de l'autorisation des événements.

## Audit temps réel

Cas d'usage :

- activité récente ;
- audit logs live ;
- alertes de refus ;
- actions sensibles.

Règles :

- payloads sans secret ;
- mise à jour contrôlée ;
- possibilité de pause ;
- historique confirmé par API.

## Notifications

Cas d'usage :

- expiration API key ;
- rotation future ;
- webhook en échec ;
- demande d'approbation future ;
- alerte sécurité.

Règles :

- aucune valeur secrète ;
- lien vers ressource ;
- niveau de criticité ;
- respect préférences utilisateur.

## Monitoring

Cas d'usage :

- statut système ;
- jobs ;
- health ;
- métriques futures.

Règles :

- données agrégées ;
- pas de secret ;
- fallback polling si WebSocket indisponible.

## Présence

La présence utilisateur est future et non prioritaire.

Cas possible :

- indiquer qu'un autre administrateur consulte ou modifie une ressource.

Règles :

- minimisation des données ;
- aucune valeur secrète ;
- ne pas bloquer les workflows sans backend conflict handling.

# API Security

Le frontend a des responsabilités de sécurité fortes, même s'il n'est pas une frontière de confiance.

## Aucune confiance dans le client

Le client peut être modifié.

Conséquences :

- toute permission est validée backend ;
- toute mutation est validée backend ;
- toute lecture de secret value est validée backend ;
- les contrôles UI ne sont que des aides ;
- les refus backend sont normaux.

## Jamais de secret dans localStorage

Règles :

- aucune valeur secrète ;
- aucun token sensible ;
- aucune API key complète ;
- aucun refresh token ;
- aucune donnée confidentielle.

localStorage est considéré comme non sûr pour des secrets.

## Jamais de token dans l'URL

Interdictions :

- token dans query params ;
- token dans hash ;
- secret dans route ;
- API key dans lien ;
- valeur secrète dans redirect URL.

Les URLs peuvent être historisées, loggées ou partagées.

## Jamais de secret dans les logs

Interdictions :

- console logs de valeur ;
- logs de payload création secret ;
- logs headers ;
- logs tokens ;
- logs API key complète ;
- logs erreurs brutes contenant secret.

Cette règle vaut aussi en développement.

## Nettoyage mémoire

Les valeurs sensibles doivent être nettoyées dès que possible.

Situations :

- fermeture RevealDialog ;
- changement de route ;
- logout ;
- expiration session ;
- erreur inattendue ;
- fin de création API key ;
- annulation formulaire secret.

Le nettoyage mémoire côté JS n'est pas une garantie absolue, mais il réduit l'exposition accidentelle.

## Protection XSS

Le frontend doit réduire les risques XSS.

Règles :

- ne pas injecter HTML non sûr ;
- échapper les contenus affichés ;
- éviter dangerously set inner HTML sauf justification exceptionnelle ;
- traiter les metadata utilisateur comme non fiables ;
- ne pas afficher de secret dans DOM plus longtemps que nécessaire ;
- appliquer Content Security Policy future selon architecture.

Une faille XSS dans un Secret Manager est critique.

## Protection CSRF selon stratégie backend

Si l'authentification utilise des cookies, CSRF doit être considéré.

Responsabilités frontend :

- envoyer token CSRF si backend le requiert ;
- respecter SameSite et stratégie backend ;
- ne pas contourner les protections ;
- gérer erreurs CSRF clairement ;
- ne pas dupliquer une sécurité incohérente.

La stratégie exacte est définie avec le backend.

## Respect strict du RBAC backend

Le frontend doit respecter les informations RBAC retournées.

Règles :

- ne pas inventer permissions ;
- ne pas déduire des droits critiques ;
- gérer refus ;
- invalider après changements RBAC ;
- afficher les permissions de manière lisible ;
- distinguer metadata read et secret value read.

# Observabilité

L'observabilité frontend doit aider à diagnostiquer les problèmes sans compromettre la confidentialité.

## Logs frontend

Les logs frontend doivent être limités.

Informations acceptables :

- type d'erreur ;
- route ;
- composant ou feature ;
- code d'erreur normalisé ;
- statut HTTP ;
- request id futur ;
- timestamp ;
- environnement.

Informations interdites :

- secret value ;
- API key complète ;
- token ;
- refresh token ;
- password ;
- payload de création secret ;
- headers sensibles ;
- cookies ;
- stack trace contenant données sensibles ;
- identifiants trop détaillés si non nécessaires.

## Erreurs

Les erreurs capturées doivent être normalisées.

Objectifs :

- diagnostiquer ;
- regrouper ;
- prioriser ;
- corréler avec backend futur ;
- détecter régressions.

Les erreurs utilisateur attendues ne doivent pas être traitées comme incidents critiques.

## Monitoring

Monitoring futur :

- taux d'erreur ;
- erreurs API ;
- performance de chargement ;
- timeouts ;
- erreurs de rendering ;
- actions échouées ;
- session expirée ;
- disponibilité perçue.

Le monitoring ne doit jamais recevoir de données sensibles.

## Métriques

Métriques utiles :

- temps de chargement ;
- latence API côté client ;
- taux de retry ;
- taux d'erreur par endpoint ;
- usage des vues ;
- erreurs de formulaire agrégées ;
- échecs de mutation.

Métriques interdites :

- contenu des secrets ;
- noms sensibles si politique les considère confidentiels ;
- tokens ;
- payloads complets ;
- requêtes de recherche pouvant contenir donnée sensible sans minimisation.

## Corrélation future

La corrélation frontend/backend pourra utiliser un request id.

Objectifs :

- relier erreur UI et logs backend ;
- diagnostiquer incidents ;
- améliorer support ;
- suivre workflows.

Le request id ne doit pas contenir d'information sensible.

# Tests

La couche API doit être testée comme une frontière critique.

Les tests doivent couvrir les succès, les erreurs, les contrats, les régressions et les comportements de sécurité.

## Mocks

Les mocks permettent de tester le frontend sans backend réel.

Règles :

- mocks alignés avec DTO documentés ;
- scénarios succès et erreurs ;
- cas permission refusée ;
- session expirée ;
- validation ;
- pagination ;
- empty states ;
- données sensibles absentes des mocks sauf scénarios contrôlés de masquage.

Les mocks ne doivent pas devenir une API parallèle déconnectée du backend.

## Intégration

Les tests d'intégration vérifient :

- service API ;
- query layer ;
- mutation layer ;
- mapping ;
- gestion erreurs ;
- invalidation cache ;
- comportement session.

Ils doivent couvrir les flows critiques :

- créer vault ;
- créer project ;
- créer secret ;
- créer version ;
- reveal ;
- créer API key ;
- révoquer API key ;
- modifier RBAC ;
- consulter audit.

## Erreurs

Les tests doivent couvrir :

- réseau indisponible ;
- timeout ;
- 400 validation ;
- 401 authentification ;
- 403 autorisation ;
- 404 ;
- 409 conflit ;
- 500 ;
- réponse mal formée ;
- refresh échoué.

Chaque erreur doit produire le comportement UI attendu.

## Contrats

Les tests de contrat vérifient l'alignement avec l'API documentée.

Objectifs :

- détecter ruptures ;
- vérifier DTO ;
- vérifier erreurs ;
- vérifier pagination ;
- vérifier champs optionnels ;
- garantir compatibilité.

Ces tests peuvent s'appuyer sur fixtures, schémas ou serveur de test selon la stratégie retenue.

## Régressions

Les tests de régression doivent protéger les règles critiques :

- pas de secret en localStorage ;
- pas de secret dans toast ;
- pas de secret dans URL ;
- reveal uniquement sur action ;
- cache invalidé après mutation ;
- logout nettoie cache ;
- refus backend affiché ;
- optimistic update absent pour actions sensibles.

# Principes d'intégration

Les règles suivantes doivent être respectées pendant tout le développement.

- Une requête a une responsabilité claire.
- Un service API expose un contrat, pas une règle métier.
- Aucun appel API ne part d'un composant de présentation.
- Aucun composant UI ne construit une URL backend.
- Aucun composant UI ne gère directement des headers.
- Le backend valide toujours.
- Le backend autorise toujours.
- Le backend audite les actions sensibles.
- Le frontend gère explicitement les refus.
- Les DTO restent à la frontière API.
- Les modèles UI sont produits par mapping lorsque nécessaire.
- Une mutation invalide le cache approprié.
- Les optimistic updates sont interdits pour les actions sensibles.
- Les valeurs secrètes ne sont jamais préchargées.
- Les valeurs secrètes ne sont jamais mises en cache durable.
- Les valeurs secrètes ne sont jamais stockées dans localStorage ou sessionStorage.
- Les tokens ne sont jamais placés dans l'URL.
- Les erreurs sont toujours normalisées.
- Les erreurs sont toujours affichées de manière sûre.
- Les retries sont interdits sur mutations non idempotentes sensibles.
- Le refresh de session est centralisé.
- Le logout nettoie les caches et états sensibles.
- Les query keys incluent les paramètres pertinents.
- Les filtres et recherches sont conservés pendant pagination.
- Les recherches ne portent jamais sur les valeurs secrètes au MVP.
- Les logs frontend ne contiennent jamais de secret, token ou payload sensible.
- Les tests couvrent succès, erreurs, permissions et régressions de sécurité.

# Conclusion

L'intégration frontend/backend de MCP Secret Manager doit être stricte, explicite et sûre.

Le frontend n'est pas une seconde implémentation du domaine. Il est un consommateur discipliné de l'API backend. Il affiche les données autorisées, soumet les intentions utilisateur, gère les erreurs, organise le cache, nettoie les états sensibles et rend les décisions backend compréhensibles.

La couche API existe pour protéger l'UI des détails HTTP et protéger le produit contre la duplication de logique. Les Services parlent en DTO. Les Mappers préparent les modèles UI. TanStack Query orchestre lectures, mutations, cache et invalidation. L'Error Layer garantit des erreurs sûres et cohérentes. L'Authentication Layer gère session, refresh et logout sans exposer de tokens.

Cette stratégie permet au frontend de rester maintenable, testable, évolutif et aligné avec la posture de sécurité de MCP Secret Manager. Elle prépare aussi les évolutions futures : uploads, exports, WebSockets, notifications, monitoring, analytics, multi-tenant et corrélation d'observabilité.

Le principe final est simple : l'API backend décide, le frontend représente fidèlement, et l'utilisateur agit dans une interface claire, fiable et sécurisée.
