# Introduction

Ce document définit le guide officiel de développement frontend de MCP Secret Manager.

Il constitue l'Engineering Handbook que chaque développeur frontend doit suivre avant de soumettre une Pull Request. Il ne remplace pas les documents d'architecture, de Design System, de sécurité, de structure de dépôt, d'intégration API ou de spécification UI. Il les complète en définissant les règles de développement quotidiennes.

MCP Secret Manager est une application SaaS de sécurité. Son frontend doit rester lisible, cohérent, robuste, accessible, sécurisé et maintenable pendant plusieurs années. Les décisions prises dans une petite Pull Request peuvent devenir des conventions implicites utilisées par toute l'équipe. Ce guide existe pour éviter que ces conventions naissent au hasard.

Des conventions communes sont indispensables parce qu'un projet frontend grandit vite :

- nouveaux écrans ;
- nouveaux composants ;
- nouveaux formulaires ;
- nouvelles mutations ;
- nouvelles permissions ;
- nouveaux états d'erreur ;
- nouvelles intégrations ;
- nouvelles contraintes de sécurité ;
- nouveaux contributeurs.

Sans règles communes, chaque développeur introduit naturellement ses préférences personnelles. Ces préférences peuvent être bonnes isolément, mais leur accumulation produit un codebase incohérent : plusieurs façons d'écrire un formulaire, plusieurs façons de gérer les erreurs, plusieurs patterns d'appel API, plusieurs styles de composants, plusieurs conventions de nommage, plusieurs réponses aux mêmes problèmes.

La cohérence est plus importante que les préférences individuelles.

Une équipe senior ne cherche pas à maximiser l'expression personnelle dans le code. Elle cherche à construire un système que plusieurs personnes peuvent comprendre, modifier, tester et faire évoluer sans friction. La meilleure convention n'est pas toujours celle qu'un développeur préfère. C'est celle que l'équipe peut appliquer avec fiabilité.

Un code est lu bien plus souvent qu'il n'est écrit.

Chaque composant, hook, mapper, test ou formulaire sera relu :

- pendant une review ;
- pendant un debug ;
- pendant une évolution ;
- pendant une correction de sécurité ;
- pendant un refactoring ;
- pendant l'onboarding ;
- par une autre personne ;
- par le même développeur plusieurs mois plus tard.

Le code doit donc être écrit pour être compris. La lisibilité n'est pas un luxe. C'est une propriété opérationnelle.

Le projet doit rester maintenable pendant plusieurs années.

Cela implique :

- des composants de taille raisonnable ;
- des responsabilités claires ;
- des abstractions justifiées ;
- des tests utiles ;
- des erreurs gérées ;
- des règles de sécurité répétées sans exception ;
- une accessibilité intégrée ;
- des Pull Requests limitées ;
- des reviews exigeantes mais constructives.

Le bon code frontend de MCP Secret Manager n'est pas seulement celui qui fonctionne aujourd'hui. C'est celui qui restera compréhensible, testable, sécurisé et maintenable par une équipe entière.

# Principes de développement

## Simplicité

La simplicité est la première qualité recherchée.

Un code simple est un code dont l'intention est évidente. Il utilise les patterns existants, évite les abstractions prématurées et limite les surprises.

Dans MCP Secret Manager, la simplicité protège aussi la sécurité. Une logique trop complexe rend les actions sensibles difficiles à auditer, les erreurs difficiles à prévoir et les comportements difficiles à tester.

Bonnes pratiques :

- préférer un flux lisible à une abstraction astucieuse ;
- limiter le nombre de responsabilités par fichier ;
- utiliser les conventions existantes ;
- éviter les helpers génériques sans besoin clair ;
- rendre les cas d'erreur explicites.

Erreurs fréquentes :

- créer une abstraction pour un seul usage ;
- cacher une logique importante dans un helper vague ;
- combiner plusieurs workflows dans un composant ;
- rendre une action sensible difficile à suivre.

## Lisibilité

La lisibilité prime sur la concision excessive.

Un code lisible :

- utilise des noms précis ;
- expose clairement les états ;
- sépare les étapes importantes ;
- rend les dépendances visibles ;
- évite les raccourcis implicites ;
- présente les erreurs comme des cas normaux.

La lisibilité doit être évaluée du point de vue d'un futur lecteur qui ne connaît pas le contexte de la Pull Request.

## Cohérence

La cohérence rend le codebase prévisible.

Elle concerne :

- nommage ;
- découpage des composants ;
- gestion des formulaires ;
- utilisation de TanStack Query ;
- gestion d'erreur ;
- structure des features ;
- tests ;
- patterns UX ;
- sécurité.

Lorsqu'un pattern existe déjà dans le projet, il doit être réutilisé sauf raison claire de le faire évoluer.

## Responsabilité unique

Chaque élément doit avoir une responsabilité principale.

Un composant rend une interface. Un hook encapsule un comportement. Un service appelle l'API. Un mapper transforme des données. Un schéma valide une entrée. Un test vérifie un comportement.

Mélanger ces responsabilités rend le code fragile.

Signaux d'alerte :

- un composant connaît les endpoints ;
- un composant de présentation décide une permission ;
- un mapper déclenche une mutation ;
- un hook global contient une règle métier ;
- un test vérifie trop de comportements indépendants.

## Composition

La composition est préférée aux composants monolithiques.

Un écran complexe doit être construit à partir de blocs compréhensibles. Chaque bloc doit avoir un rôle clair.

La composition facilite :

- la lecture ;
- les tests ;
- la réutilisation ;
- l'accessibilité ;
- le responsive ;
- la maintenance.

La composition ne signifie pas découper chaque ligne en composant. Le découpage doit suivre les responsabilités.

## Séparation des responsabilités

La séparation des responsabilités protège les frontières du projet.

Règles :

- l'UI ne contient pas d'appels HTTP directs ;
- les composants partagés ne contiennent pas de logique métier ;
- les services ne contiennent pas de logique UI ;
- les mappers ne décident pas la sécurité ;
- les hooks métier restent dans les features ;
- les providers globaux ne deviennent pas des stores universels.

## Explicite plutôt qu'implicite

Les comportements importants doivent être visibles.

Cela vaut particulièrement pour :

- loading ;
- erreurs ;
- permissions ;
- reveal ;
- mutations ;
- invalidation ;
- nettoyage de données sensibles ;
- confirmations.

Un futur lecteur doit pouvoir comprendre pourquoi une action se produit et quelles données sont concernées.

## Optimisation seulement lorsqu'elle est justifiée

L'optimisation prématurée complique souvent le code sans bénéfice réel.

Avant d'optimiser, il faut :

- identifier le problème ;
- mesurer ou observer l'impact ;
- choisir l'optimisation la plus simple ;
- vérifier qu'elle n'affaiblit pas la sécurité ;
- préserver la lisibilité.

Memoization, virtualisation, lazy loading et suspense sont utiles lorsqu'ils répondent à un besoin réel. Ils ne doivent pas être appliqués par réflexe.

# Bonnes pratiques React

## Composants fonctionnels

Tous les composants React doivent être fonctionnels.

Un composant fonctionnel doit :

- avoir un rôle clair ;
- recevoir ses données via props ;
- limiter son état local ;
- composer d'autres composants ;
- rester lisible ;
- gérer ses états visuels.

Un composant ne doit pas devenir un conteneur de toutes les responsabilités d'un écran.

## Props

Les props doivent être explicites.

Bonnes pratiques :

- noms clairs ;
- types précis ;
- éviter les props trop génériques ;
- éviter les objets fourre-tout ;
- documenter les props publiques complexes ;
- garder les callbacks nommés selon l'intention utilisateur.

Erreurs fréquentes :

- passer tout un DTO brut à un composant de présentation ;
- multiplier les booléens qui créent des combinaisons impossibles ;
- utiliser des noms vagues ;
- passer des fonctions qui font plusieurs choses.

## Composition

La composition doit être le pattern principal.

Elle permet d'assembler :

- layouts ;
- sections ;
- cards ;
- tables ;
- formulaires ;
- dialogs ;
- actions.

La composition est préférable à un composant configurable par un grand nombre de props lorsque les variations deviennent trop nombreuses.

## Children

`children` est utile pour composer des surfaces flexibles.

Bon usage :

- layout ;
- card ;
- section ;
- dialog ;
- provider ;
- wrapper visuel.

Mauvais usage :

- cacher une logique métier ;
- rendre l'ordre du contenu ambigu ;
- remplacer des props explicites lorsque la structure est fixe ;
- rendre le composant difficile à tester.

## État local

L'état local doit rester local lorsque possible.

Approprié pour :

- ouverture de menu ;
- onglet actif local ;
- état de dialog ;
- valeur temporaire non persistée ;
- UI hover ou expanded ;
- étape d'un petit workflow.

À éviter :

- copier l'état serveur ;
- stocker des permissions comme vérité ;
- stocker des secrets durablement ;
- créer un état global pour une interaction locale.

## useMemo

`useMemo` doit être utilisé lorsque le calcul est réellement coûteux ou lorsque la stabilité de référence est nécessaire pour un composant spécifique.

Bon usage :

- colonnes de table complexes ;
- calculs coûteux ;
- données dérivées volumineuses ;
- dépendance à une optimisation mesurée.

Mauvais usage :

- entourer chaque calcul simple ;
- cacher une logique de transformation qui devrait être un mapper ;
- corriger un problème de rendu non compris ;
- complexifier le code sans mesure.

## useCallback

`useCallback` doit être utilisé lorsque la stabilité d'une fonction a une utilité réelle.

Bon usage :

- callbacks passés à des composants memoized ;
- gestionnaires utilisés dans des hooks dépendants ;
- interactions de tables complexes.

Mauvais usage :

- tous les handlers par défaut ;
- dépendances incorrectes ;
- usage pour masquer une architecture confuse ;
- optimisation sans impact observé.

## useEffect

`useEffect` doit être utilisé avec prudence.

Il sert à synchroniser React avec un système externe ou un effet de bord réel.

Bon usage :

- event listener ;
- synchronisation avec API navigateur ;
- nettoyage sur unmount ;
- intégration technique ;
- focus management spécifique.

Mauvais usage :

- dériver un état qui pourrait être calculé pendant le rendu ;
- déclencher des appels API au lieu d'utiliser TanStack Query ;
- corriger une mauvaise structure de données ;
- orchestrer toute la logique d'un écran ;
- oublier cleanup.

`useEffect` ne doit pas être le réflexe par défaut.

## Hooks personnalisés

Les hooks personnalisés doivent encapsuler un comportement réutilisable ou une logique de feature.

Bonnes pratiques :

- nom clair ;
- responsabilité unique ;
- retour explicite ;
- gestion loading/error si données ;
- tests lorsque comportement critique ;
- emplacement correct selon hook global ou métier.

Erreurs fréquentes :

- hook trop large ;
- hook qui mélange UI, API et permission ;
- hook global contenant logique de feature ;
- hook difficile à tester.

## Rendu conditionnel

Le rendu conditionnel doit être lisible.

Bonnes pratiques :

- gérer loading, error, empty et success explicitement ;
- éviter les conditions imbriquées difficiles à lire ;
- extraire les blocs complexes ;
- préserver l'accessibilité.

Erreurs fréquentes :

- cacher silencieusement une erreur ;
- rendre null sans explication pour un état important ;
- mélanger permission, loading et empty dans une même condition opaque.

## Listes

Les listes doivent être stables, performantes et accessibles.

Bonnes pratiques :

- afficher loading ;
- afficher empty state ;
- afficher error state ;
- utiliser pagination ou virtualisation si volume important ;
- éviter les valeurs secrètes dans les listes.

## Clés

Les clés doivent être stables.

Bonnes pratiques :

- utiliser un identifiant stable ;
- éviter les index lorsque la liste change ;
- éviter les clés générées à chaque rendu.

Des clés instables peuvent provoquer des bugs visuels, pertes de focus et comportements inattendus.

## Fragments

Les fragments sont utiles pour grouper sans ajouter de DOM inutile.

Ils doivent rester lisibles. Si un fragment contient trop de logique ou trop d'éléments hétérogènes, un composant nommé peut être préférable.

## Gestion des erreurs UI

Les erreurs UI doivent être traitées comme des états normaux.

Bonnes pratiques :

- ErrorState pour erreurs globales ;
- messages proches des champs ;
- RetryBlock pour lectures ;
- ForbiddenState pour refus ;
- NotFoundState pour ressource absente ;
- nettoyage des données sensibles lors d'erreurs inattendues.

Erreurs fréquentes :

- ignorer catch ou error ;
- afficher une erreur brute ;
- transformer un refus en vide ;
- afficher une stack trace ;
- laisser une valeur secrète visible après erreur.

# Bonnes pratiques Next.js

## App Router

L'App Router structure les routes du frontend.

Il doit être utilisé pour :

- layouts ;
- pages ;
- route groups ;
- loading ;
- error ;
- not-found ;
- navigation entre ressources.

Les routes doivent rester une couche d'assemblage. Elles composent les features, mais ne contiennent pas toute la logique métier de l'écran.

## Server Components

Les Server Components sont le choix par défaut lorsqu'une interaction client n'est pas nécessaire.

À utiliser pour :

- layouts ;
- pages consultatives ;
- chargement initial ;
- structure ;
- données non interactives ;
- réduction du JavaScript client.

À éviter pour :

- formulaires interactifs ;
- états locaux ;
- TanStack Query côté client ;
- dialogs interactifs ;
- composants utilisant APIs navigateur.

Les Server Components ne doivent jamais précharger des valeurs secrètes destinées à un reveal volontaire.

## Client Components

Les Client Components sont utilisés lorsque l'interactivité est nécessaire.

À utiliser pour :

- formulaires ;
- menus ;
- dialogs ;
- tables interactives ;
- filtres ;
- recherche ;
- mutations ;
- hooks React client ;
- APIs navigateur ;
- reveal et copy.

Un Client Component doit être placé aussi bas que possible dans l'arbre.

## Layouts

Les layouts doivent définir les cadres persistants.

Bonnes pratiques :

- limiter la logique ;
- préserver stabilité visuelle ;
- gérer navigation ;
- accueillir providers si nécessaire ;
- éviter les données métier détaillées.

## loading

Les états loading de route doivent préserver la structure.

Bonnes pratiques :

- utiliser skeletons adaptés ;
- éviter une page blanche ;
- ne pas simuler de secret ;
- garder une transition stable.

## error

Les error boundaries doivent afficher des erreurs sûres.

Bonnes pratiques :

- message utile ;
- retry si possible ;
- aucune stack trace production ;
- nettoyage des états sensibles ;
- journalisation filtrée future.

## not-found

`not-found` doit gérer les ressources absentes sans fuite.

Bonnes pratiques :

- message sobre ;
- retour vers contexte parent ;
- éviter de révéler si une ressource existe mais est interdite ;
- cohérence avec ForbiddenState.

## Navigation

La navigation doit préserver le contexte.

Bonnes pratiques :

- breadcrumbs pour ressources hiérarchiques ;
- URLs sans données sensibles ;
- redirections sûres ;
- nettoyage des valeurs secrètes au changement de route ;
- conservation des filtres lorsque pertinent.

## Metadata

Les metadata de page doivent rester non sensibles.

Interdit :

- nom de secret sensible ;
- valeur ;
- token ;
- données d'audit sensibles ;
- informations privées.

Les titres peuvent indiquer une section ou ressource uniquement si cela ne crée pas de fuite selon le contexte produit.

# Gestion de l'état

## React State

React State sert à l'état local de l'interface.

Approprié pour :

- modales ;
- menus ;
- onglets locaux ;
- champs temporaires ;
- états visuels ;
- reveal temporaire ;
- sélection locale.

Non approprié pour :

- état serveur durable ;
- cache API ;
- permissions comme vérité ;
- session complète ;
- données sensibles persistantes.

## TanStack Query

TanStack Query gère l'état serveur côté client.

Approprié pour :

- listes ;
- détails ;
- pagination ;
- filtres serveur ;
- mutations ;
- invalidation ;
- refetch.

Règles :

- query keys stables ;
- cache invalidé après mutation ;
- pas de cache durable de secret value ;
- erreurs gérées explicitement ;
- logout nettoie le cache.

## Context

Context sert aux états réellement transverses.

Approprié pour :

- thème ;
- session minimale ;
- providers ;
- configuration UI globale ;
- command palette future.

Non approprié pour :

- remplacer TanStack Query ;
- stocker toutes les données métier ;
- contourner le props design ;
- créer un store global non maîtrisé.

## Providers

Les providers initialisent et exposent des contextes globaux.

Ils doivent être :

- rares ;
- justifiés ;
- testables ;
- sans logique métier excessive ;
- nettoyés au logout si nécessaire.

## URL

L'URL doit porter l'état partageable et navigationnel.

Approprié pour :

- route ;
- identifiants de ressource ;
- filtres ;
- recherche ;
- pagination ;
- tabs significatifs.

Interdit :

- secret ;
- token ;
- API key ;
- valeur de formulaire sensible ;
- donnée privée inutile.

## Form State

L'état de formulaire est géré par la solution de formulaire retenue.

Il doit rester :

- local au formulaire ;
- validé ;
- nettoyé après succès ;
- prudent avec les champs sensibles ;
- synchronisé avec erreurs backend.

# Gestion des formulaires

## Validation

La validation frontend améliore l'expérience.

Elle doit :

- détecter les erreurs évidentes ;
- être cohérente avec le backend ;
- rester compréhensible ;
- ne pas remplacer la validation backend ;
- gérer les champs sensibles prudemment.

## Erreurs

Les erreurs doivent être visibles et proches du champ.

Règles :

- message clair ;
- aucun payload brut ;
- aucune donnée sensible ;
- erreur globale si nécessaire ;
- focus vers erreur critique lorsque pertinent.

## Accessibilité

Tout formulaire doit être accessible.

Règles :

- labels visibles ;
- erreurs reliées aux champs ;
- focus visible ;
- navigation clavier ;
- bouton submit identifiable ;
- champs requis indiqués ;
- descriptions utiles.

## UX

Un formulaire doit guider sans surcharger.

Bonnes pratiques :

- champs groupés ;
- aide courte ;
- action principale claire ;
- annulation disponible ;
- états loading et success ;
- confirmations pour actions sensibles.

## Soumission

La soumission doit être explicite.

Règles :

- empêcher double soumission ;
- afficher loading ;
- gérer erreur ;
- invalider cache après succès ;
- nettoyer données sensibles ;
- ne pas utiliser optimistic update sur actions sensibles.

## Reset

Le reset doit être volontaire.

Règles :

- nettoyer champs après succès lorsque approprié ;
- préserver données non sensibles après erreur ;
- nettoyer champs sensibles lors d'annulation ;
- ne pas surprendre l'utilisateur.

## Prévention des doubles soumissions

Les actions de création, révocation, modification RBAC, reveal ou API key doivent empêcher les doubles soumissions.

Le bouton doit indiquer loading et l'action ne doit pas être relancée sans réponse claire.

## Champs sensibles

Les champs sensibles doivent :

- masquer par défaut ;
- éviter persistence ;
- éviter autocomplete non maîtrisée ;
- nettoyer au reset ;
- ne jamais apparaître dans logs ;
- ne jamais être dans URL.

## Confirmation

Les confirmations sont requises pour :

- reveal ;
- révocation ;
- suppression logique ;
- archivage ;
- modification RBAC sensible ;
- création API key selon contexte ;
- paramètres de sécurité.

La confirmation doit nommer la ressource et la conséquence.

# Couche API

La couche API est la seule voie de communication avec le backend.

Règles obligatoires :

- jamais d'appel HTTP dans un composant de présentation ;
- jamais de construction d'URL backend dans l'UI ;
- jamais de gestion de headers dans l'UI ;
- jamais de logique métier dans les services ;
- jamais de secret dans logs ;
- erreurs toujours normalisées.

## Services

Les services regroupent les appels par domaine.

Ils :

- appellent l'API ;
- reçoivent ou retournent des DTO ;
- restent sans UI ;
- restent sans décision métier.

## DTO

Les DTO représentent les contrats de transport.

Ils ne sont pas :

- des entités backend ;
- des modèles UI ;
- des états de formulaire ;
- des permissions calculées.

## Queries

Les queries gèrent les lectures.

Elles doivent :

- avoir des clés stables ;
- inclure les paramètres ;
- gérer loading/error ;
- ne pas précharger de secret value ;
- respecter le cache.

## Mutations

Les mutations gèrent les actions.

Elles doivent :

- appeler un service ;
- gérer loading ;
- gérer erreurs ;
- invalider le cache ;
- éviter optimistic update pour sécurité ;
- nettoyer données sensibles.

## Mapping

Le mapping transforme :

- DTO vers modèle UI ;
- formulaire vers Request DTO.

Il ne doit pas inventer une permission, un statut ou un comportement métier.

## Gestion des erreurs

Chaque appel API doit gérer :

- réseau ;
- validation ;
- authentification ;
- autorisation ;
- not found ;
- conflit ;
- serveur ;
- réponse inattendue.

Une erreur non gérée est une régression.

# Composants

## Taille idéale

Un composant doit rester lisible en une lecture raisonnable.

Il devient probablement trop gros lorsqu'il :

- mélange data fetching, formulaire, table et dialog ;
- contient plusieurs workflows indépendants ;
- gère trop d'états ;
- possède trop de props ;
- contient de longues conditions imbriquées ;
- devient difficile à tester.

## Responsabilité

Chaque composant doit avoir une responsabilité principale.

Exemples :

- afficher un badge ;
- afficher un header ;
- afficher une table ;
- gérer un formulaire ;
- coordonner une section de feature.

## Découpage

Découper un composant lorsque :

- une partie a une responsabilité autonome ;
- une partie est réutilisée ;
- une condition complexe devient illisible ;
- un sous-ensemble mérite un test ;
- une partie mélange logique et présentation ;
- le composant devient difficile à nommer.

Ne pas découper lorsque :

- le nouveau composant n'a pas de rôle clair ;
- il n'est utilisé qu'une fois et rend la lecture plus difficile ;
- il existe seulement pour réduire artificiellement la taille.

## Composition

Les composants doivent être composés plutôt que configurés à l'excès.

Trop de variantes, booléens et branches internes indiquent souvent qu'une composition plus claire est nécessaire.

## Réutilisation

Réutiliser les composants existants lorsque le besoin correspond.

Créer un nouveau composant lorsque :

- le composant existant serait détourné ;
- une nouvelle responsabilité apparaît ;
- un pattern se répète ;
- l'accessibilité ou la sécurité exige un composant dédié.

## Props

Les props doivent être :

- typées ;
- compréhensibles ;
- minimales ;
- stables ;
- orientées intention.

Éviter les props qui exposent les détails internes d'une feature à un composant partagé.

## Variantes

Les variantes doivent être limitées.

Une variante est justifiée lorsqu'elle représente un usage stable du Design System.

Éviter les variantes ad hoc pour un seul écran.

## Séparation présentation / logique

Les composants de présentation :

- reçoivent des données ;
- affichent l'UI ;
- déclenchent des callbacks ;
- ne connaissent pas l'API.

Les composants connectés :

- coordonnent queries ;
- coordonnent mutations ;
- gèrent les erreurs ;
- transmettent les données aux composants de présentation.

# Performance

## Rendering

Le rendu doit rester prévisible.

Bonnes pratiques :

- état local limité ;
- composants clients placés bas ;
- listes paginées ;
- données dérivées calculées proprement ;
- éviter re-renders massifs inutiles.

## Lazy loading

Lazy loading est utile pour :

- dialogs lourds ;
- vues rarement utilisées ;
- composants futurs de monitoring ;
- modules Enterprise ;
- visualisations coûteuses.

Il ne doit pas ralentir les actions fréquentes.

## Memoization

Memoization doit être justifiée.

Avant de l'utiliser :

- vérifier le problème ;
- identifier le calcul ou rendu coûteux ;
- mesurer si possible ;
- garder le code compréhensible.

## Pagination

La pagination est obligatoire pour les listes pouvant grandir.

Elle protège :

- performance ;
- lisibilité ;
- réseau ;
- accessibilité.

## Virtualisation future

La virtualisation sera utile pour :

- audit logs volumineux ;
- grandes listes ;
- monitoring futur ;
- analytics futur.

Elle doit préserver l'accessibilité.

## Suspense futur

Suspense doit être utilisé pour améliorer le chargement progressif.

Il ne doit pas masquer des erreurs importantes ou créer des zones instables.

## Optimisation prématurée

À éviter :

- useMemo partout ;
- useCallback partout ;
- découpage excessif ;
- cache manuel ;
- complexité sans mesure ;
- virtualisation avant volume réel.

Mesurer avant d'optimiser.

Moyens possibles :

- profiler React ;
- mesurer bundle ;
- observer temps de chargement ;
- analyser re-renders ;
- mesurer latence API ;
- surveiller performance utilisateur.

# Accessibilité

L'accessibilité est une exigence de qualité, pas une option.

## Navigation clavier

Chaque action doit être accessible au clavier.

Cela inclut :

- menus ;
- dialogs ;
- tabs ;
- tables ;
- boutons ;
- formulaires ;
- filtres ;
- pagination.

## Focus

Le focus doit être visible et logique.

Règles :

- ne jamais supprimer le focus ;
- restaurer focus après dialog ;
- déplacer focus vers erreurs si pertinent ;
- distinguer focus et hover ;
- tester au clavier.

## ARIA

ARIA complète la sémantique native.

Règles :

- utiliser HTML sémantique d'abord ;
- nom accessible pour IconButton ;
- erreurs associées aux champs ;
- dialogs nommés ;
- états importants annoncés si nécessaire.

## Lecteurs d'écran

Les composants doivent être compréhensibles avec lecteur d'écran.

Règles :

- labels explicites ;
- titres structurés ;
- tables avec en-têtes ;
- badges avec texte ;
- actions dangereuses nommées ;
- valeurs secrètes non révélées involontairement.

## Contrastes

Les contrastes doivent être suffisants en light mode et dark mode.

La couleur ne doit jamais être la seule information.

## Formulaires

Les formulaires doivent :

- avoir des labels ;
- afficher erreurs ;
- indiquer champs requis ;
- être navigables au clavier ;
- gérer focus ;
- expliquer les champs sensibles.

## Dialogs

Les dialogs doivent :

- piéger le focus ;
- restaurer le focus ;
- avoir un titre ;
- avoir des actions claires ;
- permettre annulation ;
- nommer la ressource pour actions sensibles.

## Tables

Les tables doivent :

- avoir des en-têtes ;
- supporter navigation logique ;
- afficher tri accessible ;
- garder actions de ligne nommées ;
- éviter contenu secret.

## Messages d'erreur

Les messages d'erreur doivent être :

- visibles ;
- lisibles ;
- associés au contexte ;
- non dépendants uniquement de la couleur ;
- sûrs.

# Sécurité

Les règles de sécurité frontend sont obligatoires.

## Jamais de secret dans localStorage

localStorage ne doit jamais contenir :

- secret ;
- API key complète ;
- token ;
- refresh token ;
- password ;
- payload sensible.

## Jamais de secret dans les logs

Interdit dans :

- console ;
- monitoring ;
- analytics ;
- error reporting ;
- tests non contrôlés ;
- messages d'erreur.

## Reveal volontaire

Une valeur secrète est révélée uniquement :

- après action utilisateur ;
- après autorisation backend ;
- dans un composant prévu ;
- temporairement.

Jamais au chargement, jamais au hover, jamais en bulk.

## Nettoyage mémoire

Les valeurs sensibles doivent être nettoyées :

- fermeture de dialog ;
- changement de route ;
- logout ;
- expiration ;
- erreur inattendue ;
- annulation.

## Backend = autorité

Le backend décide :

- permissions ;
- validation ;
- secret access ;
- audit ;
- états ;
- révocations.

Le frontend affiche et gère les réponses.

## Aucune logique de permission locale

Le frontend peut améliorer l'UX avec affichage conditionnel.

Il ne doit jamais considérer cet affichage comme une protection réelle.

## Respect du RBAC backend

Le frontend doit :

- respecter les refus ;
- afficher permissions fournies ;
- distinguer metadata et value ;
- invalider après changements RBAC ;
- éviter toute déduction dangereuse.

# Tests

Les tests protègent les comportements importants.

Ils doivent être utiles, lisibles et proportionnés au risque.

## Tests unitaires

À écrire pour :

- mappers ;
- validation ;
- helpers ;
- formatage ;
- normalisation d'erreurs ;
- fonctions pures ;
- logique de sécurité locale testable.

Pas forcément nécessaire pour :

- composants purement visuels très simples ;
- wrappers sans logique ;
- code déjà couvert par un test plus pertinent.

## Tests d'intégration

À écrire pour :

- formulaire avec validation et mutation ;
- query avec affichage ;
- gestion d'erreur API ;
- invalidation ;
- session expirée ;
- refus de permission ;
- interaction entre composants d'une feature.

## Tests E2E

À écrire pour les parcours critiques :

- login ;
- création vault ;
- création project ;
- création secret ;
- création version ;
- reveal ;
- création API key ;
- révocation API key ;
- audit logs ;
- RBAC.

Les tests E2E doivent rester stables et centrés sur le comportement utilisateur.

## Tests de régression

À écrire après correction d'un bug significatif.

Indispensables pour :

- bugs sécurité ;
- erreurs de permission ;
- fuites de secret ;
- mauvais nettoyage ;
- invalidation cache ;
- formulaires critiques ;
- navigation protégée.

# Documentation

La documentation doit soutenir le code, pas le remplacer.

## Quand écrire de la documentation

Écrire de la documentation lorsque :

- une décision est structurante ;
- un comportement n'est pas évident ;
- un composant public a des règles d'usage ;
- une contrainte sécurité est importante ;
- un workflow est complexe ;
- une convention est nouvelle.

## ADR

Une ADR est appropriée pour :

- choix technique majeur ;
- changement d'architecture ;
- changement de stratégie de sécurité ;
- adoption d'une dépendance importante ;
- convention qui impacte tout le projet.

## README

Un README local peut être utile pour :

- expliquer une feature complexe ;
- documenter un module ;
- guider les tests ;
- expliquer des fixtures.

Il doit rester court et maintenu.

## Commentaires

Les commentaires doivent expliquer le pourquoi, pas le quoi.

Bon commentaire :

- clarifie une contrainte ;
- explique une décision ;
- signale un invariant ;
- documente un compromis.

Mauvais commentaire :

- répète le code ;
- masque un nom peu clair ;
- justifie un hack permanent ;
- devient obsolète.

## Décisions d'architecture

Les décisions d'architecture appartiennent aux documents dédiés ou ADR.

Elles ne doivent pas être cachées dans une Pull Request ou un commentaire isolé.

## Documentation des composants publics

Un composant partagé important doit documenter :

- rôle ;
- variantes ;
- états ;
- accessibilité ;
- règles de sécurité si sensible ;
- exemples d'usage dans la documentation dédiée si nécessaire.

## Le code comme documentation principale

Le code doit rester la première documentation.

Cela signifie :

- noms explicites ;
- structure claire ;
- types précis ;
- responsabilités visibles ;
- tests lisibles ;
- pas de comportement magique.

Une documentation longue ne compense pas un code confus.

# Pull Requests

Une Pull Request doit être facile à reviewer.

## Taille raisonnable

Une PR doit être aussi petite que possible tout en livrant une unité cohérente.

Éviter :

- refactoring massif mélangé à feature ;
- changements UI et API non liés ;
- modifications de style global opportunistes ;
- corrections diverses sans lien.

## Objectif unique

Une PR doit avoir un objectif principal.

Exemples :

- ajouter un écran ;
- corriger un bug ;
- refactorer un composant ;
- ajouter une mutation ;
- améliorer l'accessibilité d'un dialog.

## Description claire

La description doit expliquer :

- ce qui change ;
- pourquoi ;
- impact utilisateur ;
- zones touchées ;
- risques ;
- décisions notables.

## Captures d'écran pour changements UI

Toute PR UI doit inclure des captures ou enregistrements pertinents lorsque possible.

Inclure :

- desktop ;
- mobile si impact responsive ;
- light/dark si changement visuel ;
- états loading/error/empty si pertinents.

## Tests exécutés

La PR doit indiquer les tests exécutés.

Exemples :

- unitaires ;
- intégration ;
- E2E ;
- vérification manuelle ;
- accessibilité manuelle ;
- responsive.

Si un test n'a pas été exécuté, l'expliquer.

## Checklist complétée

La checklist de développement doit être parcourue avant demande de review.

Elle ne doit pas être traitée comme une formalité.

## Lien avec les issues

La PR doit référencer les issues, tickets ou décisions liées lorsque disponibles.

Cela facilite le contexte et l'historique.

## Absence de code mort

La PR ne doit pas introduire :

- composants inutilisés ;
- helpers inutilisés ;
- feature flags oubliés ;
- TODO permanents ;
- imports morts ;
- styles non utilisés ;
- branches impossibles.

## Critères d'acceptation

Une PR est acceptable si :

- l'objectif est clair ;
- le code respecte l'architecture ;
- les conventions sont suivies ;
- la sécurité est respectée ;
- l'accessibilité est prise en compte ;
- les erreurs sont gérées ;
- les tests sont adaptés ;
- la documentation est suffisante ;
- aucun code mort n'est introduit ;
- la review peut être faite efficacement.

# Code Review

La revue de code sert à améliorer le produit, pas à juger le développeur.

Une bonne review est exigeante, précise et respectueuse. Elle protège la qualité collective.

## Checklist de revue

Architecture :

- la modification est au bon endroit ;
- les frontières sont respectées ;
- aucune dépendance circulaire ;
- aucune logique API dans l'UI ;
- aucune logique métier dans shared.

Lisibilité :

- noms clairs ;
- responsabilités visibles ;
- conditions compréhensibles ;
- fichiers de taille raisonnable ;
- comportement explicite.

Cohérence :

- patterns existants réutilisés ;
- composants partagés utilisés correctement ;
- conventions de nommage respectées ;
- états UI cohérents.

Sécurité :

- aucun secret stocké ;
- aucun secret loggé ;
- reveal volontaire ;
- cleanup présent ;
- backend autorité ;
- refus gérés ;
- RBAC respecté.

Accessibilité :

- clavier ;
- focus ;
- labels ;
- aria si nécessaire ;
- dialogs accessibles ;
- contrastes ;
- erreurs associées.

Performance :

- pas de rendu inutile évident ;
- listes paginées si nécessaire ;
- pas d'optimisation prématurée complexe ;
- pas de bundle lourd injustifié.

Duplication :

- duplication acceptable ou à extraire ;
- pas de copie de logique sensible ;
- composants réutilisés.

Tests :

- niveau de test adapté ;
- cas erreur couverts ;
- refus couverts si pertinent ;
- régression couverte ;
- tests lisibles.

UX :

- états loading, empty, error ;
- feedback ;
- confirmations ;
- responsive ;
- cohérence Design System.

Documentation :

- décision importante documentée ;
- commentaires utiles ;
- README ou ADR si nécessaire ;
- pas de documentation obsolète.

# Refactoring

Le refactoring améliore la structure sans changer le comportement attendu.

## Quand refactorer

Refactorer lorsque :

- un composant devient difficile à lire ;
- une duplication se stabilise ;
- une responsabilité est au mauvais endroit ;
- un bug révèle une mauvaise frontière ;
- un test devient difficile à écrire ;
- une future feature serait bloquée par la structure actuelle.

## Quand attendre

Attendre lorsque :

- le besoin est hypothétique ;
- le refactor n'est pas lié à l'objectif de PR ;
- le risque dépasse le bénéfice immédiat ;
- les tests sont insuffisants ;
- la zone est en évolution rapide.

## Limiter les risques

Pour limiter les risques :

- refactorer par petites étapes ;
- garder les comportements visibles identiques ;
- ajouter tests avant si nécessaire ;
- éviter de mélanger feature et refactor ;
- valider avec captures si UI.

## Découper un gros refactoring

Un gros refactoring doit être découpé :

- préparation ;
- extraction ;
- migration ;
- nettoyage ;
- suppression de l'ancien chemin.

Chaque étape doit rester reviewable.

## Préserver les comportements existants

Le refactoring ne doit pas modifier silencieusement :

- permissions ;
- reveal ;
- cache ;
- erreurs ;
- navigation ;
- états visuels ;
- accessibilité.

## Éviter les gros refactorings opportunistes

Les gros refactorings opportunistes sont dangereux.

Ils :

- ralentissent les reviews ;
- augmentent le risque de régression ;
- mélangent les objectifs ;
- rendent les bugs difficiles à attribuer ;
- créent des conflits.

Ils doivent être planifiés, justifiés et testés.

# Anti-patterns

Les erreurs suivantes doivent être évitées.

- Composants trop gros.
- Composants qui mélangent UI, API, état, formulaires et permissions.
- Logique métier dans les composants partagés.
- Appels HTTP dans un composant de présentation.
- `useEffect` utilisé par défaut.
- `useEffect` utilisé pour dériver un état simple.
- `useMemo` utilisé partout sans mesure.
- `useCallback` utilisé partout sans mesure.
- Optimisation prématurée.
- Duplication de logique de mapping.
- Duplication de composants avec petites variations.
- Props drilling excessif.
- Context utilisé comme store global.
- Provider global créé pour un état local.
- Dépendances circulaires.
- Imports profonds entre features.
- Barrel exports trop larges.
- Dossier utils fourre-tout.
- Dossier shared utilisé comme poubelle.
- Commentaires qui expliquent le quoi au lieu du pourquoi.
- Variables ambiguës.
- Types trop génériques.
- DTO utilisés directement dans toute l'UI.
- Gestion d'erreur oubliée.
- Loading state absent.
- Empty state absent.
- Refus de permission masqué.
- TODO permanents.
- Code mort.
- Feature flags oubliés.
- Secrets dans logs.
- Secrets dans localStorage.
- Token dans URL.
- Reveal automatique.
- Optimistic update sur action sensible.
- Tests E2E fragiles basés sur détails visuels.
- Documentation obsolète.
- Pull Request trop large.

# Development Checklist

Chaque développeur doit parcourir cette checklist avant de demander une review.

## Architecture

- Le changement est placé dans le bon espace du projet.
- La feature reste autonome.
- Les composants partagés restent génériques.
- La couche API reste séparée de l'UI.
- Aucune dépendance circulaire n'est introduite.
- Aucun import interdit entre features n'est introduit.
- Aucun provider global inutile n'est ajouté.

## Qualité du code

- Les noms sont explicites.
- Les responsabilités sont claires.
- Les composants restent de taille raisonnable.
- Les hooks ont un rôle précis.
- Les conditions complexes sont lisibles.
- Le code mort est supprimé.
- Aucun TODO permanent n'est introduit.
- La duplication est acceptable ou justifiée.

## UI / UX

- Les états loading sont présents.
- Les états empty sont présents.
- Les états error sont présents.
- Les actions sensibles sont confirmées.
- Les feedbacks utilisateur sont clairs.
- Le responsive est vérifié.
- Le light mode et dark mode restent cohérents si impactés.
- Les libellés sont compréhensibles.

## Accessibilité

- La navigation clavier fonctionne.
- Le focus est visible.
- Les dialogs gèrent le focus.
- Les champs ont des labels.
- Les erreurs sont associées aux champs.
- Les IconButtons ont un nom accessible.
- La couleur n'est pas la seule information.
- Les contrastes restent suffisants.

## Sécurité

- Aucun secret n'est affiché par défaut.
- Aucun secret n'est stocké localement.
- Aucun secret n'est loggé.
- Aucun token n'est placé dans l'URL.
- Reveal est volontaire.
- Copy est volontaire.
- Les valeurs sensibles sont nettoyées.
- Le backend reste l'autorité.
- Les refus backend sont gérés.
- Aucune logique de permission métier locale n'est ajoutée.

## Performance

- Les listes importantes sont paginées ou prêtes à l'être.
- Aucun rendu coûteux évident n'est introduit.
- Aucune dépendance lourde injustifiée n'est ajoutée.
- Les optimisations sont justifiées.
- Les Client Components sont limités au nécessaire.
- Les données sensibles ne sont pas préchargées.

## Tests

- Les helpers ou mappers critiques sont testés.
- Les formulaires critiques sont testés.
- Les erreurs importantes sont testées.
- Les refus sont testés si la fonctionnalité touche aux permissions.
- Les workflows sensibles sont couverts.
- Une régression corrigée ajoute un test.
- Les tests exécutés sont mentionnés dans la PR.

## Documentation

- Les décisions importantes sont documentées.
- Les commentaires expliquent le pourquoi.
- La documentation existante reste à jour.
- Un composant public complexe est documenté si nécessaire.
- Une ADR est proposée pour une décision structurante.

## Pull Request

- La PR a un objectif unique.
- La description est claire.
- Les captures sont fournies pour les changements UI.
- Les tests exécutés sont listés.
- Les issues liées sont référencées.
- Le code mort est absent.
- Les risques sont mentionnés.
- La PR est suffisamment petite pour être reviewée correctement.

# Conclusion

Le développement frontend de MCP Secret Manager doit être guidé par la simplicité, la lisibilité, la cohérence et la sécurité.

Le bon code n'est pas seulement celui qui fonctionne aujourd'hui. C'est celui qui reste compréhensible, testable, sécurisé et maintenable pendant plusieurs années par une équipe entière.

Chaque développeur doit écrire du code pour les futurs lecteurs : collègues, reviewers, mainteneurs, nouveaux arrivants et soi-même dans quelques mois. Chaque composant doit avoir une responsabilité claire. Chaque appel API doit passer par la couche prévue. Chaque formulaire doit gérer ses erreurs. Chaque action sensible doit être explicite. Chaque secret doit rester masqué par défaut. Chaque Pull Request doit améliorer le produit sans affaiblir sa cohérence.

MCP Secret Manager est un produit de sécurité. Son frontend doit refléter cette exigence dans chaque détail : architecture respectée, UI accessible, erreurs sûres, performances mesurées, tests utiles, reviews constructives et maintenance pensée sur le long terme.
