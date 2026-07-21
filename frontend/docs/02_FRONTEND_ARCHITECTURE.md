# Objectifs d'architecture

Ce document définit l'architecture frontend officielle de MCP Secret Manager.

Dans le monorepo, tous les chemins frontend mentionnés dans ce document sont relatifs au dossier `frontend/`, sauf mention contraire. Par exemple, `app/` désigne `frontend/app/` et `tests/` désigne `frontend/tests/`.

Il doit être considéré comme une référence structurante avant toute première ligne de React. Son rôle est de fixer les choix techniques, les responsabilités des dossiers, les frontières entre UI, données, état et API, ainsi que les règles qui permettront au frontend de rester simple, maintenable, évolutif, performant, testable, cohérent et sécurisé.

Le frontend de MCP Secret Manager est une application SaaS d'administration pour un produit de sécurité. Il ne peut donc pas être traité comme une interface générique. Il manipule des ressources sensibles, rend visibles des permissions, déclenche des actions à impact sécurité, affiche des événements d'audit et peut révéler ponctuellement des valeurs secrètes. Son architecture doit réduire les erreurs humaines, limiter les fuites accidentelles et rester alignée avec les garanties du backend.

Le backend reste la source d'autorité métier et sécurité. Le frontend ne remplace pas la Clean Architecture backend. Il l'accompagne par une architecture applicative claire, orientée features, respectueuse de l'API et conçue pour évoluer vers une console SaaS moderne.

## Simplicité

La simplicité est le premier objectif d'architecture.

Une application d'administration de secrets peut rapidement devenir difficile à maintenir si elle mélange navigation, appels API, formulaires, règles d'affichage, mapping de données, permissions, composants génériques et logique métier dans les mêmes fichiers.

L'architecture frontend doit éviter cette confusion.

La simplicité recherchée se traduit par :

- des dossiers prévisibles ;
- des responsabilités explicites ;
- des conventions stables ;
- peu de patterns concurrents ;
- une séparation claire entre UI, données, formulaires et accès API ;
- une préférence pour les solutions standard de l'écosystème React et Next.js ;
- une absence d'abstractions prématurées.

Une architecture simple permet à un développeur, à une équipe DevOps ou à un assistant IA de localiser rapidement où une modification doit être faite. Elle réduit les risques de duplication et rend les revues plus sûres.

## Maintenabilité

La maintenabilité garantit que l'application pourra évoluer sans accumuler de dette structurelle.

MCP Secret Manager va commencer avec un MVP centré sur dashboard, vaults, projects, secrets, secret versions, API keys, audit logs, RBAC, profil et paramètres. Il devra ensuite accueillir des fonctionnalités plus avancées comme multi-tenant, monitoring, notifications, webhooks, analytics, billing, identités d'agents ou temps réel.

La maintenabilité impose :

- des features isolées ;
- des composants réutilisables ;
- une couche API stable ;
- des types partagés de manière contrôlée ;
- des conventions de nommage homogènes ;
- des formulaires standardisés ;
- des erreurs présentées selon une stratégie commune ;
- une logique de données testable.

Chaque évolution doit pouvoir être intégrée sans refonte globale. Les modifications locales doivent rester locales lorsque le domaine le permet.

## Évolutivité

L'évolutivité désigne la capacité de l'architecture à accueillir plus de ressources, plus de workflows, plus de volumes et plus de cas d'usage.

Le frontend doit pouvoir évoluer vers :

- plusieurs organisations ou tenants ;
- plusieurs plans SaaS ;
- des permissions plus fines ;
- des vues temps réel ;
- du monitoring ;
- des notifications ;
- des intégrations cloud ;
- des workflows Enterprise ;
- des identités d'agents IA ;
- des approbations humaines.

Cette évolutivité ne doit pas être obtenue en généralisant tout dès le MVP. Elle doit être obtenue par des frontières propres : features indépendantes, API layer séparée, composants partagés raisonnables, providers centralisés et routing organisé.

L'architecture doit rendre les futures extensions naturelles, sans imposer une complexité Enterprise à la première version.

## Performance

La performance est un objectif produit et un objectif de sécurité opérationnelle.

Une interface lente pousse les utilisateurs à contourner le système, à stocker des secrets ailleurs ou à utiliser directement des scripts non contrôlés. Une console de sécurité doit donc être rapide, réactive et stable.

La performance recherchée inclut :

- chargement initial maîtrisé ;
- navigation fluide ;
- rendu efficace des tableaux ;
- chargement progressif des données ;
- cache serveur adapté ;
- invalidation précise ;
- composants clients limités aux besoins réels ;
- découpage du bundle ;
- streaming et suspense lorsque pertinents.

La performance ne doit pas compromettre la sécurité. Une optimisation qui conserve inutilement une valeur secrète en mémoire, affiche une donnée sensible trop longtemps ou masque une erreur critique doit être refusée.

## Testabilité

La testabilité est indispensable pour un frontend qui administre des secrets.

Les erreurs frontend peuvent provoquer :

- mauvaise confirmation d'une action sensible ;
- affichage ambigu d'une permission ;
- mauvaise interprétation d'un état de révocation ;
- perte de contexte entre vault, projet et secret ;
- affichage accidentel d'une valeur ;
- mauvaise gestion d'une expiration de session ;
- action déclenchée sur la mauvaise ressource.

L'architecture doit rendre les tests naturels :

- composants isolés testables ;
- hooks séparés ;
- fonctions de mapping testables ;
- formulaires validés ;
- flows critiques couverts par des tests d'intégration ;
- parcours principaux vérifiés en end-to-end ;
- erreurs et états vides testés.

Les tests doivent cibler en priorité les workflows sensibles : création de secret, révélation de valeur, création ou révocation d'API key, modification de permissions, consultation d'audit logs et protection des routes.

## Cohérence

La cohérence est essentielle pour créer une expérience premium et réduire les erreurs.

Le frontend doit utiliser les mêmes patterns pour :

- listes ;
- pages de détail ;
- formulaires ;
- modales de confirmation ;
- badges d'état ;
- messages d'erreur ;
- chargements ;
- états vides ;
- pagination ;
- mutations ;
- permissions visibles ;
- actions dangereuses.

Une interface cohérente permet à l'utilisateur d'apprendre le produit progressivement. Elle permet aussi aux développeurs de livrer plus vite, car les décisions de conception et d'architecture ne sont pas réinventées à chaque écran.

## Sécurité

La sécurité du frontend a une limite claire : le client ne doit jamais être considéré comme une frontière de confiance.

Le backend reste responsable des permissions, de l'autorisation, de la validation métier, de l'audit, du chiffrement et des décisions critiques. Le frontend doit respecter ces décisions, les rendre compréhensibles et éviter les fuites accidentelles.

L'architecture doit imposer :

- aucune logique de permission métier définitive côté client ;
- aucun secret stocké inutilement ;
- aucune valeur sensible dans les logs ;
- aucune valeur secrète dans les URLs ;
- masquage par défaut ;
- affichage ponctuel et volontaire des valeurs ;
- gestion stricte des erreurs ;
- séparation des DTO API et modèles d'affichage ;
- confirmations pour actions sensibles ;
- suppression rapide des valeurs sensibles de l'état UI lorsque possible.

Le frontend doit être une surface d'administration sûre, pas une seconde implémentation du domaine backend.

# Stack technique

La stack retenue pour MCP Secret Manager frontend est :

- Next.js 15 ;
- React 19 ;
- TypeScript ;
- App Router ;
- Tailwind CSS ;
- shadcn/ui ;
- TanStack Query ;
- React Hook Form ;
- Zod.

Ces choix forment une stack moderne, largement adoptée, adaptée aux applications SaaS, compatible avec une architecture frontend feature-first et capable de produire une expérience rapide, maintenable et accessible.

## Next.js 15

Next.js 15 est le framework applicatif principal.

Son rôle est de fournir :

- routing applicatif ;
- layouts imbriqués ;
- server rendering ;
- streaming ;
- découpage automatique ;
- conventions de structure ;
- optimisation de performance ;
- support des Server Components ;
- intégration naturelle avec React moderne.

Next.js est adapté à MCP Secret Manager parce que le produit a besoin d'une application web riche, structurée, sécurisée et performante. Le framework permet de combiner des pages rendues côté serveur lorsque cela améliore la performance ou la sécurité, et des composants clients lorsque l'interactivité est nécessaire.

Next.js doit être utilisé comme cadre d'application, pas comme lieu de duplication de logique backend. Les routes frontend organisent l'expérience utilisateur. Elles ne portent pas les règles métier critiques.

## React 19

React 19 est la bibliothèque d'interface.

Son rôle est de fournir :

- composition de composants ;
- rendu déclaratif ;
- gestion d'interactions ;
- Server Components ;
- Client Components ;
- Suspense ;
- modèle mental stable pour construire l'UI.

React est adapté au produit parce que MCP Secret Manager aura de nombreux écrans composés : tableaux, filtres, formulaires, pages de détail, modales, panneaux latéraux, badges, menus et composants sensibles.

React doit être utilisé avec discipline. Les composants doivent rester petits, lisibles et composables. La logique de données, les appels API et les mappings ne doivent pas être dispersés dans les composants visuels.

## TypeScript

TypeScript est obligatoire pour tout le frontend.

Son rôle est de fournir :

- typage statique ;
- documentation implicite des contrats ;
- détection précoce d'erreurs ;
- robustesse des mappings API ;
- meilleures refactorisations ;
- sécurité accrue dans les workflows complexes.

MCP Secret Manager manipule des ressources dont les états sont importants : actif, archivé, verrouillé, révoqué, courant, expiré, refusé, autorisé. TypeScript permet de représenter ces états explicitement et de réduire les erreurs d'interprétation.

TypeScript ne remplace pas la validation runtime. Les données venant de l'API doivent rester considérées comme externes et peuvent être validées ou normalisées lorsque nécessaire.

## App Router

L'App Router de Next.js est le système de routing officiel du frontend.

Son rôle est de fournir :

- routing basé sur les dossiers ;
- layouts imbriqués ;
- loading states par route ;
- error boundaries par route ;
- route groups ;
- séparation claire entre routes publiques et protégées ;
- support naturel des Server Components.

L'App Router est adapté à une console SaaS parce qu'il permet de structurer l'application autour de zones fonctionnelles : authentification, application protégée, paramètres, ressources, erreurs et vues de détail.

Le routing doit représenter l'architecture d'information du produit, pas seulement les URLs. Les layouts doivent exprimer les contextes : application connectée, navigation principale, vault actif, projet actif, page de détail.

## Tailwind CSS

Tailwind CSS est l'outil principal de styling.

Son rôle est de fournir :

- styles utilitaires ;
- design system cohérent ;
- rapidité d'implémentation ;
- contraintes visuelles explicites ;
- support responsive ;
- support dark mode ;
- réduction des CSS globales non maîtrisées.

Tailwind est adapté à MCP Secret Manager parce qu'il permet de construire une UI premium avec cohérence et rapidité, tout en gardant le styling proche des composants.

Tailwind doit être utilisé avec discipline. Les classes ne doivent pas devenir un substitut à un système de composants. Les patterns visuels répétés doivent être encapsulés dans des composants partagés lorsque cela améliore la cohérence.

## shadcn/ui

shadcn/ui fournit une base de composants accessibles, composables et personnalisables.

Son rôle est de fournir :

- composants UI de base ;
- conventions de composition ;
- accessibilité de composants interactifs ;
- intégration naturelle avec Tailwind ;
- base esthétique moderne sans dépendance à un design fermé.

shadcn/ui est adapté au produit parce que MCP Secret Manager a besoin de composants fiables : dialogs, menus, tabs, inputs, forms, tables, badges, buttons, popovers, command menus et alerts.

Les composants shadcn/ui doivent être considérés comme une base, pas comme une identité produit finale. Ils devront être adaptés à la charte visuelle de MCP Secret Manager tout en conservant leur accessibilité.

## TanStack Query

TanStack Query est la solution principale de gestion d'état serveur côté client.

Son rôle est de fournir :

- cache de données API ;
- gestion des chargements ;
- gestion des erreurs ;
- invalidation ;
- mutations ;
- retries contrôlés ;
- refetch ;
- synchronisation entre vues ;
- expérience réactive sur les données serveur.

TanStack Query est adapté aux zones interactives du produit : listes filtrées, pages de détail, mutations, formulaires qui déclenchent des actions, pagination, audit logs et états qui doivent être rafraîchis après modification.

TanStack Query ne doit pas devenir un store global pour l'état UI. Il gère l'état serveur, pas l'ouverture d'une modale ou le contenu temporaire d'un champ.

## React Hook Form

React Hook Form est la solution principale pour les formulaires.

Son rôle est de fournir :

- gestion performante des champs ;
- validation intégrée ;
- état de formulaire ;
- erreurs par champ ;
- soumission contrôlée ;
- bonne intégration avec Zod ;
- support de formulaires complexes sans re-renders inutiles.

MCP Secret Manager aura de nombreux formulaires sensibles : création de vault, projet, secret, version, clé API, rôle, paramètres et confirmations. React Hook Form permet de standardiser ces parcours.

Les formulaires doivent rester proches des features qui les utilisent. Les composants de champ génériques peuvent être partagés, mais les règles de validation spécifiques doivent rester compréhensibles dans le contexte de la feature.

## Zod

Zod est la solution principale de validation runtime et de schémas côté frontend.

Son rôle est de fournir :

- validation de formulaires ;
- parsing de données ;
- messages d'erreur structurés ;
- cohérence entre types et validation ;
- protection contre les données inattendues ;
- normalisation des entrées utilisateur.

Zod est particulièrement utile dans un produit de sécurité, car les données saisies doivent être contrôlées avant d'être envoyées au backend. Cela améliore l'expérience utilisateur, réduit les requêtes invalides et clarifie les erreurs.

Zod ne remplace pas la validation backend. Toute validation frontend est une aide UX et une première ligne de qualité, jamais une garantie de sécurité définitive.

# Principes d'architecture

Les principes suivants guident toute décision frontend. Ils sont normatifs et doivent être utilisés pendant les revues, les arbitrages et les futures extensions.

## Feature-first

L'architecture est organisée en priorité par feature métier.

Les domaines principaux comme vaults, projects, secrets, audit, API keys, RBAC, settings et user profile doivent posséder leurs propres espaces de code.

Ce principe évite de disperser une même fonctionnalité entre des dossiers génériques trop larges. Une personne travaillant sur les secrets doit pouvoir trouver les composants, hooks, schémas, types, appels API et helpers liés aux secrets dans un emplacement prévisible.

Les dossiers globaux restent utiles pour les composants réellement transverses, les providers, les utilitaires génériques, les styles et les types partagés. Ils ne doivent pas absorber la logique spécifique des features.

## Composition over inheritance

Le frontend doit privilégier la composition.

React est naturellement orienté composition. Les pages doivent être construites à partir de composants simples assemblés entre eux, plutôt que de systèmes d'héritage ou de composants trop abstraits.

Ce principe favorise :

- composants plus petits ;
- responsabilités plus claires ;
- réutilisation plus flexible ;
- tests plus simples ;
- design system évolutif.

Un composant générique ne doit être créé que lorsqu'un pattern est réellement répété et stabilisé.

## Smart vs Dumb components

L'architecture doit distinguer les composants connectés aux données des composants purement visuels.

Les composants dits smart sont responsables de la coordination :

- chargement de données ;
- mutations ;
- état de formulaire ;
- orchestration d'une action ;
- adaptation des données à l'affichage.

Les composants dits dumb sont responsables du rendu :

- structure visuelle ;
- présentation ;
- labels ;
- états visuels ;
- interaction locale simple.

Cette séparation évite que les composants d'interface deviennent difficiles à lire. Elle facilite aussi les tests et la réutilisation.

La règle n'impose pas deux dossiers pour chaque composant. Elle impose surtout une discipline : un tableau visuel ne doit pas connaître les détails du client HTTP, et un hook de mutation ne doit pas décider de la structure visuelle d'une page.

## Server Components par défaut

Les Server Components doivent être le choix par défaut lorsque l'interactivité client n'est pas nécessaire.

Ce choix permet :

- de réduire le JavaScript envoyé au navigateur ;
- d'améliorer le chargement initial ;
- de garder certaines opérations côté serveur ;
- de tirer parti du modèle Next.js ;
- de réserver les Client Components aux besoins réels.

Les pages statiques, layouts, shells, vues de détail peu interactives et certaines lectures initiales peuvent s'appuyer sur des Server Components.

Ce principe doit toutefois rester pragmatique. Les écrans fortement interactifs, les tableaux filtrables côté client, les formulaires, les modales et les actions utilisateur nécessitent des Client Components.

## Client Components uniquement si nécessaire

Un composant doit devenir client lorsqu'il utilise :

- état React local ;
- effets navigateur ;
- événements interactifs ;
- formulaires ;
- TanStack Query ;
- APIs navigateur ;
- composants nécessitant une interaction côté client.

Ce principe protège la performance et la maintenabilité. Une application d'administration riche aura forcément des Client Components, mais ils doivent être choisis volontairement.

Chaque Client Component doit avoir une raison claire d'exister. Les composants clients trop hauts dans l'arbre augmentent le bundle et réduisent les bénéfices des Server Components.

## UI séparée de la logique métier

Le frontend ne doit pas porter la logique métier critique.

Il peut gérer :

- présentation ;
- validation UX ;
- états de formulaire ;
- mapping d'affichage ;
- permissions visibles retournées par l'API ;
- confirmations ;
- contraintes d'ergonomie.

Il ne doit pas décider de façon autonome :

- si un utilisateur a réellement le droit d'effectuer une action ;
- si une lecture de secret doit être autorisée ;
- si un rôle est valide ;
- si une ressource doit être visible pour des raisons de sécurité ;
- si une action sensible doit être auditée.

Ces décisions appartiennent au backend. Le frontend doit appeler l'API, afficher les résultats, gérer les refus et éviter les hypothèses dangereuses.

## API comme source de vérité

L'API REST du backend est la source de vérité du frontend.

Le frontend ne doit pas maintenir une copie durable de l'état métier. Le cache client est un outil de performance et d'expérience, pas une source d'autorité.

Après une mutation sensible, les données concernées doivent être invalidées ou rechargées afin de refléter l'état confirmé par le backend.

Les états optimistes doivent être réservés aux actions sûres et réversibles. Ils doivent être évités pour les actions de sécurité comme révocation, modification de permissions, verrouillage, suppression logique ou révélation de valeur.

## Backend responsable de la sécurité

Le backend reste responsable de la sécurité.

Le frontend améliore la sécurité d'usage, mais il ne peut pas garantir la sécurité métier. Un utilisateur peut modifier le client, appeler directement l'API ou contourner l'interface. Toutes les décisions critiques doivent donc être validées côté backend.

Le frontend doit :

- respecter les statuts et permissions retournés ;
- présenter les refus clairement ;
- ne pas masquer les erreurs critiques ;
- éviter d'envoyer des données inutiles ;
- ne pas stocker de secrets ;
- ne pas exposer de détails sensibles ;
- déclencher les confirmations UX nécessaires.

## Contrats explicites

Les contrats entre API layer, features et composants doivent être explicites.

Les données reçues de l'API doivent être représentées par des DTO ou types de réponse. Les données utilisées par l'UI peuvent être adaptées dans des modèles d'affichage lorsque cela améliore la clarté.

Cette séparation permet d'éviter que l'UI dépende directement de chaque détail du backend. Elle rend les migrations API plus sûres et localise les transformations.

## États sensibles traités explicitement

Les ressources sensibles doivent avoir des états explicites dans l'UI.

Exemples :

- vault actif ;
- vault verrouillé ;
- vault archivé ;
- projet archivé ;
- secret actif ;
- secret supprimé logiquement ;
- version courante ;
- clé API active ;
- clé API révoquée ;
- session expirée ;
- permission refusée.

Un état sensible ne doit pas être seulement une couleur ou un texte secondaire. Il doit être représenté de manière cohérente, accessible et non ambiguë.

# Organisation des dossiers

L'organisation des dossiers doit rendre les responsabilités visibles. Elle doit rester stable et compréhensible tout au long du développement.

La structure cible comprend les dossiers suivants :

- `app/` ;
- `features/` ;
- `components/` ;
- `hooks/` ;
- `providers/` ;
- `lib/` ;
- `types/` ;
- `styles/` ;
- `public/` ;
- `tests/`.

Cette organisation est feature-first, avec des dossiers globaux réservés aux éléments transverses.

## app/

Le dossier `app/` contient le routing Next.js App Router.

Rôle :

- définir les routes ;
- définir les layouts ;
- définir les pages ;
- définir les loading states ;
- définir les error boundaries ;
- organiser les route groups ;
- séparer routes publiques et protégées ;
- porter la structure de navigation principale.

Contenu attendu :

- pages de connexion et autres routes publiques ;
- routes protégées de l'application ;
- layouts globaux ;
- layouts d'espace authentifié ;
- layouts imbriqués par contexte ;
- pages d'erreur ;
- fichiers de chargement par route ;
- métadonnées de pages lorsque nécessaire.

Responsabilités :

- composer les features ;
- fournir le contexte de route ;
- déclencher les chargements serveur lorsque pertinent ;
- organiser l'expérience de navigation ;
- ne pas contenir de logique métier complexe ;
- ne pas contenir de client HTTP dispersé.

Le dossier `app/` doit rester une couche d'assemblage. Les fonctionnalités concrètes vivent dans `features/`.

## features/

Le dossier `features/` contient les fonctionnalités métier.

Rôle :

- regrouper le code lié à un domaine produit ;
- isoler les composants spécifiques ;
- isoler les hooks de données ;
- isoler les formulaires ;
- isoler les schémas de validation ;
- isoler les mappings ;
- rendre chaque feature compréhensible séparément.

Contenu attendu :

- dashboard ;
- vault ;
- project ;
- secret ;
- secret version ;
- API keys ;
- audit ;
- RBAC ;
- user profile ;
- settings ;
- futures features comme monitoring, notifications, billing ou tenants.

Responsabilités :

- exposer des composants ou containers utilisés par les routes ;
- encapsuler les appels API propres à la feature via la couche API prévue ;
- définir les schémas de formulaire propres à la feature ;
- mapper les données métier vers des modèles d'affichage ;
- contenir les tests spécifiques lorsque ce choix est retenu.

Une feature ne doit pas importer directement des détails internes d'une autre feature sauf via une interface explicitement partagée. Les dépendances transverses doivent passer par `components/`, `lib/`, `types/` ou des APIs publiques clairement définies.

## components/

Le dossier `components/` contient les composants UI transverses.

Rôle :

- fournir le design system applicatif ;
- centraliser les composants génériques ;
- garantir la cohérence visuelle ;
- réduire la duplication ;
- encapsuler les composants shadcn/ui adaptés au produit.

Contenu attendu :

- boutons ;
- champs ;
- dialogs ;
- tables génériques ;
- badges ;
- tooltips ;
- menus ;
- layouts UI génériques ;
- composants de chargement ;
- états vides ;
- alertes ;
- composants de confirmation ;
- composants sensibles génériques comme affichage masqué ou champ secret.

Responsabilités :

- rester indépendants du domaine métier lorsque possible ;
- accepter des données via props ;
- ne pas appeler directement l'API ;
- ne pas connaître les routes métier sauf exceptions justifiées ;
- être accessibles ;
- être compatibles light mode et dark mode.

Les composants partagés ne doivent pas devenir des composants géants capables de tout faire. Ils doivent rester composables.

## hooks/

Le dossier `hooks/` contient les hooks transverses.

Rôle :

- regrouper la logique React réutilisable entre features ;
- fournir des comportements UI génériques ;
- éviter la duplication.

Contenu attendu :

- hooks de media query ;
- hooks de thème ;
- hooks de raccourcis clavier ;
- hooks de debounce ;
- hooks de confirmation générique ;
- hooks liés à des préférences locales ;
- hooks d'interface non spécifiques à une feature.

Responsabilités :

- ne pas contenir de logique métier spécifique ;
- ne pas devenir un espace fourre-tout ;
- rester testables ;
- documenter les comportements non évidents.

Les hooks de données propres à une feature doivent rester dans la feature concernée.

## providers/

Le dossier `providers/` contient les providers React globaux.

Rôle :

- centraliser les contextes applicatifs ;
- configurer les bibliothèques globales ;
- rendre l'ordre des providers explicite.

Contenu attendu :

- provider TanStack Query ;
- provider de thème ;
- provider de session ou auth context si nécessaire ;
- provider de toasts ;
- provider de modales globales si retenu ;
- providers futurs comme analytics, monitoring ou temps réel.

Responsabilités :

- initialiser les contextes ;
- limiter les effets globaux ;
- ne pas porter de logique métier ;
- rester compatibles avec le modèle Next.js.

Les providers doivent être peu nombreux. Chaque provider global augmente la complexité mentale de l'application.

## lib/

Le dossier `lib/` contient les utilitaires techniques et l'infrastructure frontend.

Rôle :

- centraliser les helpers non liés à une feature ;
- fournir le client HTTP ;
- gérer les erreurs techniques ;
- fournir les helpers de formatage ;
- héberger les fonctions de mapping transverses ;
- contenir les constantes globales.

Contenu attendu :

- client API ;
- gestion d'erreurs API ;
- helpers de dates ;
- helpers de formatage ;
- helpers de pagination ;
- helpers de validation générique ;
- configuration frontend ;
- fonctions utilitaires pures.

Responsabilités :

- rester indépendant de l'UI ;
- éviter les dépendances vers `app/` ;
- éviter les dépendances vers des composants ;
- fournir des fonctions testables ;
- ne pas contenir de logique spécifique aux features lorsque celle-ci appartient clairement à `features/`.

`lib/` doit rester un socle technique, pas un domaine parallèle.

## types/

Le dossier `types/` contient les types TypeScript transverses.

Rôle :

- centraliser les types partagés par plusieurs features ;
- définir les formes communes ;
- éviter les duplications incompatibles.

Contenu attendu :

- types de pagination ;
- types d'erreur ;
- types de session ;
- types de thème ;
- types de permissions affichables ;
- types de statut commun ;
- types API transverses si nécessaire.

Responsabilités :

- ne pas absorber tous les types de features ;
- éviter les types trop génériques ;
- exprimer les concepts communs ;
- rester lisible.

Les types spécifiques à une feature doivent vivre dans la feature. Les types partagés ne doivent être extraits que lorsqu'ils sont réellement transverses.

## styles/

Le dossier `styles/` contient les styles globaux et les définitions de thème.

Rôle :

- centraliser les styles globaux indispensables ;
- définir les variables de thème ;
- configurer les fondations visuelles ;
- garantir la cohérence light et dark mode.

Contenu attendu :

- styles globaux ;
- tokens CSS ;
- variables de thème ;
- styles de base ;
- ajustements globaux strictement nécessaires.

Responsabilités :

- rester limité ;
- éviter les styles globaux qui modifient des composants de manière implicite ;
- soutenir Tailwind et shadcn/ui ;
- garantir l'accessibilité visuelle.

La majorité du styling doit rester dans les composants via Tailwind et le système de composants.

## public/

Le dossier `public/` contient les assets statiques.

Rôle :

- fournir les images publiques ;
- fournir les icônes statiques ;
- fournir les favicons ;
- fournir les fichiers publics non sensibles.

Contenu attendu :

- logo ;
- favicon ;
- illustrations éventuelles ;
- assets de marque ;
- fichiers publics strictement nécessaires.

Responsabilités :

- ne jamais contenir de secrets ;
- ne jamais contenir de configuration sensible ;
- rester organisé ;
- optimiser les assets visibles.

Tout fichier placé dans `public/` doit être considéré comme accessible publiquement.

## tests/

Le dossier `tests/` contient les tests transverses et scénarios d'application.

Rôle :

- organiser les tests d'intégration ;
- organiser les tests end-to-end ;
- fournir les fixtures ;
- fournir les helpers de test ;
- documenter les scénarios critiques.

Contenu attendu :

- tests end-to-end ;
- tests d'intégration applicative ;
- fixtures ;
- helpers ;
- mocks API ;
- scénarios de sécurité UX.

Responsabilités :

- couvrir les parcours critiques ;
- éviter la duplication excessive ;
- fournir des tests lisibles ;
- rester aligné avec les workflows produit.

Les tests unitaires proches d'une feature peuvent être placés à proximité du code de la feature si ce choix améliore la lisibilité. Les tests transverses et end-to-end vivent dans `tests/`.

# Organisation des Features

Les features représentent les domaines fonctionnels principaux du frontend.

Chaque feature doit regrouper ce qui est nécessaire pour livrer un domaine utilisateur cohérent. Elle ne doit pas être un simple dossier de composants visuels. Elle contient l'interface, les hooks de données, les formulaires, les schémas, les types locaux et les helpers propres au domaine.

La structure fonctionnelle initiale comprend :

- `features/dashboard/` ;
- `features/vault/` ;
- `features/project/` ;
- `features/secret/` ;
- `features/audit/` ;
- `features/api-key/` ;
- `features/rbac/` ;
- `features/user-profile/` ;
- `features/settings/`.

Les noms doivent rester cohérents, explicites et alignés avec les concepts produit.

## Contenu d'une feature

Une feature peut contenir :

- composants spécifiques ;
- containers connectés aux données ;
- hooks TanStack Query propres à la feature ;
- fonctions de mutation ;
- schémas Zod ;
- types locaux ;
- mappings DTO vers UI ;
- helpers spécifiques ;
- textes d'état vide ;
- tests spécifiques ;
- constantes locales.

Tous ces éléments ne sont pas obligatoires dans chaque feature. La structure doit rester proportionnée. Une feature simple ne doit pas créer des fichiers vides pour suivre une structure artificielle.

## Dashboard

La feature dashboard coordonne la vue synthétique de l'application.

Responsabilités :

- afficher les indicateurs globaux ;
- afficher l'activité récente ;
- fournir des raccourcis ;
- présenter les états importants ;
- gérer les états vides d'une instance fraîche.

Elle consomme probablement plusieurs endpoints ou agrégations, mais elle ne doit pas réimplémenter la logique des features sous-jacentes. Elle affiche une synthèse.

## Vault

La feature vault gère les écrans liés aux vaults.

Responsabilités :

- liste des vaults ;
- création ;
- détail ;
- modification de métadonnées ;
- états verrouillé ou archivé ;
- actions sensibles ;
- navigation vers les projets associés.

La feature vault représente une frontière de sécurité majeure. Les composants doivent rendre les états et actions sensibles sans ambiguïté.

## Project

La feature project gère les projets contenus dans les vaults.

Responsabilités :

- liste des projets ;
- création ;
- détail ;
- modification ;
- archivage ;
- accès aux secrets d'un projet ;
- maintien du contexte vault.

La feature project doit toujours préserver la lisibilité de la relation entre vault et projet.

## Secret

La feature secret gère les secrets et leurs versions.

Responsabilités :

- liste des secrets ;
- création ;
- détail de métadonnées ;
- modification de métadonnées ;
- archivage ou suppression logique ;
- affichage de la version courante ;
- accès à l'historique des versions ;
- création de nouvelle version ;
- révélation ponctuelle de valeur lorsque autorisée.

Cette feature est la plus sensible. Elle doit appliquer les conventions de masquage, confirmation, audit visible et absence de stockage inutile.

## Audit

La feature audit gère les audit logs.

Responsabilités :

- liste des événements ;
- filtres ;
- recherche ;
- pagination ;
- détail d'événement ;
- liens contextuels ;
- représentation claire des actions sensibles ;
- représentation claire des refus.

La feature audit doit rendre l'enquête rapide sans exposer de valeur secrète.

## API Key

La feature API key gère les clés d'accès et tokens techniques.

Responsabilités :

- liste des clés ;
- création ;
- affichage ponctuel de valeur lors de création si applicable ;
- détail ;
- révocation ;
- statut ;
- dernière utilisation ;
- permissions ou rôles associés.

Cette feature doit traiter la création et la révocation comme des actions de sécurité majeures.

## RBAC

La feature RBAC gère la représentation des rôles et permissions.

Responsabilités :

- afficher les rôles ;
- afficher les permissions ;
- gérer les affectations lorsque disponible ;
- présenter les permissions effectives ;
- confirmer les changements sensibles.

Le frontend ne décide pas de l'autorisation. Il rend le modèle backend compréhensible et affiche les décisions retournées.

## User Profile

La feature user profile gère l'utilisateur connecté.

Responsabilités :

- informations du compte ;
- préférences personnelles ;
- contexte d'identité ;
- déconnexion ;
- paramètres personnels non globaux.

Cette feature doit aider l'utilisateur à savoir avec quel compte il agit.

## Settings

La feature settings gère les paramètres de l'instance ou de l'application.

Responsabilités :

- configuration générale ;
- préférences globales disponibles ;
- informations système non sensibles ;
- accès aux futures options Enterprise ;
- actions administratives sensibles si exposées.

Les paramètres doivent rester prudents : aucune donnée sensible ne doit être affichée par commodité.

# Routing

Le routing doit refléter l'architecture d'information du produit.

MCP Secret Manager est une application d'administration structurée autour de ressources hiérarchiques et de contextes de sécurité. L'utilisateur doit toujours comprendre s'il se trouve dans une route publique, une route protégée, un vault, un projet, un secret, une section de paramètres ou une page d'audit.

## App Router

L'App Router est utilisé pour toutes les routes.

Il permet :

- d'organiser les pages par dossiers ;
- de définir des layouts imbriqués ;
- de gérer les chargements par segment ;
- de gérer les erreurs par segment ;
- de séparer les zones publiques et protégées ;
- d'exploiter les Server Components ;
- de structurer les pages de détail.

Le routing doit rester lisible. Les noms de segments doivent correspondre aux concepts utilisateur, pas à des détails techniques internes.

## Layouts imbriqués

Les layouts imbriqués doivent exprimer les contextes applicatifs.

Exemples de contextes :

- application globale ;
- session authentifiée ;
- navigation principale ;
- espace de ressources ;
- contexte vault ;
- contexte projet ;
- section paramètres.

Les layouts doivent éviter la duplication de navigation, de shell applicatif et de providers locaux. Ils doivent aussi permettre des chargements progressifs cohérents.

Un layout ne doit pas contenir de logique métier complexe. Il compose l'environnement de page.

## Route groups

Les route groups doivent organiser les routes sans imposer une structure d'URL inutile.

Ils peuvent servir à séparer :

- routes publiques ;
- routes authentifiées ;
- routes d'administration ;
- routes d'erreur ;
- routes expérimentales futures ;
- zones de layout distinctes.

Les route groups doivent être utilisés pour clarifier l'architecture, pas pour masquer une navigation confuse.

## Protected routes

Les routes protégées sont toutes les routes qui nécessitent une session authentifiée.

Elles incluent :

- dashboard ;
- vaults ;
- projects ;
- secrets ;
- API keys ;
- audit logs ;
- RBAC ;
- profil ;
- paramètres.

La protection des routes repose sur la session, pas sur une logique RBAC métier côté frontend. Le frontend peut masquer ou désactiver certaines actions selon les informations retournées par l'API, mais le backend reste l'autorité.

Si la session est absente, invalide ou expirée, l'utilisateur doit être redirigé ou invité à se reconnecter selon le contexte.

## Public routes

Les routes publiques sont accessibles sans session.

Elles incluent principalement :

- connexion ;
- éventuelle récupération de compte si prévue ;
- page d'erreur publique ;
- informations minimales non sensibles.

Les routes publiques ne doivent pas exposer d'informations sur les vaults, projets, secrets, clés API, audit logs, rôles, utilisateurs internes ou configuration sensible.

## Error routes

Les routes d'erreur doivent fournir une expérience claire et sûre.

Elles couvrent :

- ressource introuvable ;
- accès refusé ;
- erreur serveur ;
- erreur de chargement ;
- session expirée ;
- erreur inattendue.

Les erreurs doivent éviter de révéler des détails internes. Elles doivent proposer une action utile : revenir en arrière, retourner au dashboard, recharger, se reconnecter ou contacter un administrateur.

## Loading routes

Les loading routes doivent rendre les transitions prévisibles.

Elles doivent :

- préserver la structure de page ;
- éviter les sauts visuels ;
- signaler le chargement ;
- différencier chargement initial et rechargement partiel lorsque pertinent ;
- rester sobres.

Un état de chargement ne doit pas afficher de fausses données sensibles. Les skeletons doivent être neutres.

# Data Fetching

La stratégie de data fetching combine Server Components, Client Components et TanStack Query.

Le choix dépend de la nature de la donnée, du besoin d'interactivité, du niveau de fraîcheur attendu, du risque sécurité et de l'expérience utilisateur.

## Server Components

Les Server Components sont privilégiés pour :

- chargements initiaux de pages peu interactives ;
- données nécessaires au layout ;
- informations de session ;
- données stables ou peu modifiées ;
- pages de détail principalement consultatives ;
- réduction du JavaScript client.

Ils permettent d'améliorer la performance initiale et de limiter le travail côté navigateur.

Ils ne doivent pas être utilisés pour conserver ou exposer inutilement des valeurs secrètes. Toute lecture de valeur secrète doit rester une action volontaire et sensible.

## Client Components

Les Client Components sont utilisés pour :

- formulaires ;
- tableaux interactifs ;
- filtres dynamiques ;
- mutations ;
- modales ;
- menus ;
- toasts ;
- interactions utilisateur ;
- composants utilisant TanStack Query ;
- affichage temporaire de valeur secrète.

Ils doivent rester aussi bas que possible dans l'arbre de rendu pour préserver les bénéfices des Server Components.

## TanStack Query

TanStack Query est utilisé pour l'état serveur côté client.

Cas d'usage :

- listes filtrées ;
- pagination ;
- recherche ;
- détails rechargés après mutation ;
- audit logs ;
- actions déclenchant invalidation ;
- données fréquemment consultées ;
- états de chargement et d'erreur côté client.

Chaque query doit avoir une clé stable, structurée et représentative des paramètres utilisés. Les mutations doivent invalider précisément les queries concernées.

## Cache

Le cache doit améliorer l'expérience sans compromettre l'exactitude.

Règles :

- cache court ou prudent pour ressources sensibles ;
- invalidation après mutation ;
- absence de cache durable pour valeurs secrètes ;
- différenciation entre métadonnées et valeurs ;
- attention particulière aux changements de session ;
- séparation des caches par contexte utilisateur.

Les valeurs secrètes révélées ne doivent pas être stockées dans le cache TanStack Query de manière durable. Elles doivent être traitées comme données temporaires.

## Invalidation

L'invalidation est obligatoire après les mutations qui changent l'état serveur.

Exemples :

- création d'un vault ;
- modification d'un projet ;
- création d'un secret ;
- création d'une version ;
- révocation d'une clé API ;
- changement RBAC ;
- archivage d'une ressource ;
- modification de paramètres.

L'invalidation doit être ciblée. Invalider toute l'application après chaque mutation est simple mais peut devenir coûteux et imprécis.

## Optimistic Updates

Les optimistic updates doivent être utilisées avec prudence.

Elles peuvent être envisagées pour des interactions non sensibles, facilement réversibles et sans impact sécurité fort.

Elles doivent être évitées pour :

- révocation d'API key ;
- modification RBAC ;
- lecture ou révélation de secret ;
- verrouillage de vault ;
- suppression logique ;
- archivage ;
- opérations d'audit ;
- paramètres de sécurité.

Pour les actions sensibles, l'UI doit attendre la confirmation backend avant d'afficher l'état final.

## Revalidation

La revalidation doit garantir que les données critiques restent à jour.

Elle peut être déclenchée :

- après mutation ;
- au retour de focus ;
- après expiration d'un délai ;
- lors d'un changement de route ;
- lors d'un changement de contexte ;
- après reconnexion.

La fréquence doit être adaptée au type de donnée. Les audit logs ou statuts de clés peuvent demander une fraîcheur supérieure à des métadonnées de profil.

# Gestion d'état

La gestion d'état doit être explicitement segmentée selon la nature de l'état.

Il ne doit pas exister un store global unique contenant tout. Chaque type d'état a une solution adaptée.

## État serveur

L'état serveur représente les données dont la source de vérité est le backend.

Exemples :

- vaults ;
- projects ;
- secrets ;
- secret versions ;
- API keys ;
- audit logs ;
- rôles ;
- permissions ;
- paramètres serveur ;
- session confirmée.

Solution :

- Server Components lorsque la donnée est nécessaire au rendu initial ou peu interactive ;
- TanStack Query lorsque la donnée est utilisée dans des vues interactives ou doit être invalidée/rechargée côté client.

Règle :

L'état serveur ne doit pas être copié dans un store global UI sauf justification forte. Le cache de données doit rester géré par les mécanismes prévus.

## État UI

L'état UI représente l'état temporaire de l'interface.

Exemples :

- modale ouverte ;
- onglet actif ;
- menu ouvert ;
- panneau latéral visible ;
- filtre local ;
- tri sélectionné ;
- ligne sélectionnée ;
- état d'un toast ;
- confirmation en cours.

Solution :

- état React local ;
- hooks locaux ;
- contexte React limité lorsque l'état doit être partagé dans une sous-arborescence ;
- paramètres d'URL lorsque l'état doit être partageable ou persistant dans la navigation.

Règle :

L'état UI doit rester proche du composant ou de la feature qui l'utilise.

## État local

L'état local représente les données temporaires propres à un composant ou une interaction.

Exemples :

- valeur d'un champ temporaire ;
- visibilité d'une valeur masquée ;
- étape courante d'un petit workflow ;
- sélection dans un menu ;
- état d'un composant contrôlé.

Solution :

- état React local ;
- React Hook Form pour les formulaires ;
- hooks spécialisés pour comportements réutilisables.

Règle :

Les valeurs secrètes révélées doivent rester locales, temporaires et supprimées dès qu'elles ne sont plus nécessaires.

## Formulaires

Les formulaires sont gérés par React Hook Form et validés avec Zod.

Exemples :

- création de vault ;
- création de projet ;
- création de secret ;
- création de version ;
- création d'API key ;
- modification de métadonnées ;
- filtres avancés ;
- paramètres ;
- confirmations sensibles.

Solution :

- React Hook Form pour l'état de formulaire ;
- Zod pour validation et messages ;
- mutations TanStack Query ou actions adaptées pour la soumission ;
- composants de champs partagés.

Règle :

La validation frontend améliore l'UX, mais le backend reste la validation définitive. Les erreurs backend doivent être affichées correctement même si la validation frontend a réussi.

## Préférences utilisateur

Les préférences utilisateur représentent les choix non critiques de l'utilisateur.

Exemples :

- thème light ou dark ;
- densité d'affichage ;
- colonnes visibles si prévu ;
- préférence de pagination ;
- dernier filtre utilisé si non sensible.

Solution :

- stockage côté serveur si la préférence doit suivre l'utilisateur ;
- stockage local navigateur pour les préférences purement ergonomiques et non sensibles ;
- contexte React ou provider de thème pour l'application.

Règle :

Aucune préférence ne doit contenir de secret, token, valeur sensible ou information confidentielle. Les préférences locales doivent être considérées comme lisibles par l'utilisateur et son environnement navigateur.

# API Layer

L'API layer est la frontière entre le frontend et le backend.

Elle doit être centralisée, typée, testable et séparée de l'UI. Les composants ne doivent pas construire manuellement les requêtes HTTP dans les pages. Les features consomment des fonctions ou hooks dédiés qui s'appuient sur l'API layer.

## Client HTTP

Le client HTTP centralise :

- base URL ;
- headers communs ;
- credentials ;
- parsing des réponses ;
- normalisation des erreurs ;
- timeouts si retenus ;
- comportement de retry ;
- gestion de session lorsque nécessaire.

Le client HTTP doit être un outil technique, pas un service métier.

Il doit éviter :

- logs de payloads sensibles ;
- duplication des URLs ;
- gestion d'erreurs incohérente ;
- stockage de secrets ;
- logique RBAC.

## Séparation API/UI

Les composants UI ne doivent pas dépendre directement du format brut des réponses API lorsque ce format est complexe ou instable.

La séparation doit permettre :

- de changer un endpoint avec impact localisé ;
- de mapper les DTO vers des modèles d'affichage ;
- de tester les transformations ;
- de garder les composants lisibles ;
- de gérer les états d'erreur uniformément.

Les features peuvent exposer des hooks comme points d'entrée de données, mais ces hooks doivent rester alignés avec l'API layer.

## Mapping DTO

Les DTO représentent les données telles que retournées par le backend.

Les modèles UI représentent les données telles qu'utilisées par l'interface.

Le mapping est utile lorsque :

- les noms API ne sont pas idéaux pour l'affichage ;
- les dates doivent être normalisées ;
- les statuts doivent être transformés en labels ;
- des champs optionnels doivent recevoir des valeurs par défaut ;
- une structure imbriquée doit être simplifiée ;
- l'UI doit combiner plusieurs informations.

Le mapping ne doit jamais inventer une autorisation ou masquer un refus. Il doit rester une transformation de présentation.

## Gestion des erreurs

L'API layer doit normaliser les erreurs.

Types d'erreurs attendus :

- validation ;
- authentification ;
- autorisation ;
- ressource introuvable ;
- conflit ;
- rate limit futur ;
- erreur serveur ;
- erreur réseau ;
- erreur inattendue.

Chaque erreur doit pouvoir être affichée de manière appropriée. Une erreur d'autorisation ne se présente pas comme une erreur réseau. Une erreur de validation ne se présente pas comme une erreur serveur.

Les erreurs ne doivent pas afficher de détails sensibles, de stack trace, de token, de payload secret ou d'information interne dangereuse.

## Authentification

L'API layer doit inclure les credentials selon la stratégie d'authentification retenue.

La stratégie privilégiée repose sur des cookies sécurisés gérés côté serveur et envoyés automatiquement lorsque le contexte l'autorise.

Le frontend ne doit pas manipuler ou stocker de tokens sensibles dans un état global accessible inutilement.

## Refresh

Le refresh de session doit être géré de manière centralisée.

Objectifs :

- éviter les boucles infinies ;
- éviter les refresh concurrents non contrôlés ;
- gérer l'expiration proprement ;
- préserver l'expérience utilisateur lorsque la session peut être renouvelée ;
- déconnecter clairement lorsque le refresh échoue.

Le refresh ne doit pas masquer indéfiniment un problème d'authentification. Une session invalide doit conduire à une reconnexion.

## Retries

Les retries doivent être prudents.

Ils peuvent être utiles pour :

- erreurs réseau temporaires ;
- endpoints de lecture non sensibles ;
- indisponibilité courte.

Ils doivent être évités ou fortement contrôlés pour :

- mutations ;
- création de clé API ;
- révélation de secret ;
- révocation ;
- changement RBAC ;
- actions non idempotentes.

Un retry automatique ne doit jamais déclencher deux fois une action sensible non idempotente.

## Pagination

La pagination doit être standardisée.

Elle concerne :

- vaults si volume élevé ;
- projects ;
- secrets ;
- versions ;
- API keys ;
- audit logs ;
- utilisateurs ou acteurs futurs ;
- notifications futures.

L'API layer doit exposer une représentation cohérente de la pagination à l'UI. Les paramètres de page, limite, curseur, tri et filtres doivent être traités de manière prévisible.

Les audit logs peuvent nécessiter une pagination plus robuste, potentiellement par curseur, afin de préserver l'ordre chronologique et la performance.

# Authentification

L'authentification frontend doit identifier l'utilisateur connecté, gérer sa session et protéger l'accès aux routes privées.

Elle ne doit jamais contenir de logique de permission métier définitive.

## Session

La session représente l'état authentifié de l'utilisateur.

Elle peut inclure :

- identifiant utilisateur ;
- nom ou email ;
- état de connexion ;
- informations minimales de profil ;
- informations non sensibles utiles à l'UI ;
- expiration approximative si disponible.

Elle ne doit pas inclure :

- secret ;
- token API complet ;
- refresh token lisible par JavaScript ;
- permissions interprétées comme vérité définitive si le backend ne les retourne pas explicitement ;
- données sensibles inutiles.

La session doit être chargée au niveau approprié pour protéger les routes et afficher le shell authentifié.

## Cookies

Les cookies sécurisés sont privilégiés pour la session web.

Objectifs :

- réduire l'exposition des tokens à JavaScript ;
- faciliter l'envoi des credentials ;
- s'intégrer proprement avec Next.js ;
- améliorer la posture contre certaines fuites côté client.

Les cookies doivent être configurés côté backend ou couche serveur selon les exigences de sécurité :

- HttpOnly lorsque possible ;
- Secure en production ;
- SameSite adapté ;
- durée de vie maîtrisée ;
- révocation côté serveur.

Le frontend doit s'appuyer sur cette stratégie sans dupliquer les secrets de session dans localStorage.

## Refresh token

Le refresh token, s'il existe, doit être protégé.

Règles :

- ne pas l'exposer au JavaScript applicatif ;
- ne pas le stocker dans localStorage ;
- ne pas l'afficher ;
- ne pas le logger ;
- gérer son expiration ;
- prévoir un logout clair si le refresh échoue.

Le mécanisme de refresh doit être invisible lorsque tout fonctionne, mais explicite lorsque la session ne peut plus être renouvelée.

## Expiration

L'expiration de session doit être gérée avec clarté.

Comportements attendus :

- éviter les erreurs silencieuses ;
- informer l'utilisateur lorsqu'une action échoue à cause de la session ;
- rediriger vers la connexion lorsque nécessaire ;
- préserver l'URL de destination si cela est sûr ;
- nettoyer les caches sensibles ;
- fermer ou réinitialiser les états contenant des valeurs sensibles.

Une expiration pendant une action sensible doit être traitée prudemment. L'utilisateur ne doit pas croire qu'une action a réussi si elle n'a pas été confirmée par le backend.

## Logout

Le logout doit être fiable.

Il doit :

- appeler le backend lorsque nécessaire ;
- invalider la session ;
- nettoyer les caches client ;
- supprimer les données temporaires ;
- revenir à une route publique ;
- empêcher le retour vers des données sensibles via un état client.

Le logout est une action de sécurité. Il doit être simple, visible et robuste.

## Protection des routes

Les routes protégées doivent vérifier l'existence d'une session valide.

Cette vérification peut se faire au niveau serveur, middleware ou layout selon le choix d'implémentation final, mais elle doit être centralisée et cohérente.

La protection des routes ne remplace pas l'autorisation backend. Elle empêche simplement l'accès à l'application sans session.

Les erreurs d'autorisation sur une ressource doivent être affichées comme des refus d'accès, pas comme des absences de route génériques lorsque le backend fournit cette information de manière sûre.

# Gestion des erreurs

La gestion des erreurs doit être cohérente, sûre et actionnable.

Une erreur est une partie normale de l'expérience d'administration. Elle peut venir d'une validation, d'une permission insuffisante, d'une session expirée, d'une ressource absente, d'un conflit ou d'une indisponibilité réseau.

L'objectif n'est pas de cacher les erreurs. L'objectif est de les présenter sans fuite d'information sensible et avec une action utile.

## Erreurs API

Les erreurs API doivent être normalisées par l'API layer.

Elles doivent ensuite être affichées selon leur nature :

- validation : message proche du champ concerné ;
- authentification : invitation à se reconnecter ;
- autorisation : message clair de refus ;
- ressource introuvable : page ou état dédié ;
- conflit : explication de l'état concurrent ;
- serveur : message générique et possibilité de réessayer ;
- rate limit futur : indication de délai ou limitation.

Le frontend doit éviter d'afficher les messages backend bruts s'ils peuvent contenir des informations internes. Les messages doivent être mappés vers des formulations sûres.

## Erreurs réseau

Les erreurs réseau doivent être distinguées des erreurs métier.

Elles peuvent signifier :

- backend indisponible ;
- perte de connexion ;
- timeout ;
- CORS ou configuration ;
- proxy en erreur ;
- navigateur hors ligne.

L'interface doit proposer de réessayer lorsque cela a du sens. Elle doit éviter de présenter une erreur réseau comme un refus d'autorisation.

## Erreurs utilisateur

Les erreurs utilisateur sont souvent liées aux formulaires ou à une action impossible.

Exemples :

- champ requis manquant ;
- nom invalide ;
- confirmation incorrecte ;
- tentative d'action sur ressource archivée ;
- filtre invalide ;
- sélection manquante.

Ces erreurs doivent être précises, locales et faciles à corriger.

## Erreurs inattendues

Les erreurs inattendues doivent être capturées par des error boundaries.

Elles doivent :

- préserver l'application lorsque possible ;
- proposer une récupération ;
- éviter d'afficher des détails internes ;
- ne pas révéler de données sensibles ;
- pouvoir être observées par un système de monitoring futur.

Une erreur inattendue dans une zone sensible doit nettoyer les états temporaires contenant des valeurs confidentielles.

# Performance

La performance doit être traitée comme une qualité de base.

L'application doit donner une impression de rapidité et de précision, y compris sur des vues riches comme audit logs, secrets ou API keys.

## Lazy loading

Le lazy loading doit être utilisé pour charger les parties non nécessaires au rendu initial.

Exemples :

- modales avancées ;
- panneaux secondaires ;
- composants de visualisation lourds futurs ;
- sections Enterprise non fréquentes ;
- éditeurs ou composants spécialisés futurs.

Le lazy loading ne doit pas créer de latence visible sur les actions fréquentes critiques.

## Code splitting

Le code splitting doit s'appuyer sur Next.js et les frontières de routes.

Objectifs :

- réduire le bundle initial ;
- charger uniquement les features nécessaires ;
- isoler les sections futures ;
- améliorer la navigation.

Les dépendances lourdes doivent être introduites avec prudence et chargées uniquement où elles sont nécessaires.

## Streaming

Le streaming doit être utilisé lorsque des parties de page peuvent être rendues progressivement.

Cas pertinents :

- dashboard avec plusieurs blocs de données ;
- pages qui combinent résumé et listes ;
- zones dont les chargements ont des vitesses différentes ;
- vues futures de monitoring ou analytics.

Le streaming doit améliorer la perception de performance sans produire une interface instable.

## Suspense

Suspense doit servir à encadrer les chargements de composants ou données.

Il permet :

- fallback cohérent ;
- chargement progressif ;
- séparation des zones ;
- réduction des états manuels dispersés.

Les fallbacks doivent être sobres, accessibles et adaptés au contenu attendu.

## Memoization

La memoization doit être utilisée lorsque le besoin est mesuré ou évident.

Cas pertinents :

- calculs de présentation coûteux ;
- grandes listes ;
- colonnes de tables ;
- callbacks passés à de nombreux composants ;
- composants fréquemment rendus.

La memoization ne doit pas devenir un réflexe automatique. Une memoization excessive complique le code sans bénéfice réel.

## Virtualisation des listes

La virtualisation doit être envisagée pour les listes volumineuses.

Cas prioritaires :

- audit logs ;
- secrets très nombreux ;
- versions nombreuses ;
- API keys nombreuses ;
- événements de monitoring futurs.

La virtualisation doit préserver :

- accessibilité ;
- navigation clavier ;
- hauteur stable ;
- lisibilité ;
- comportement de recherche et filtre.

## Optimisation des images

Les images doivent être optimisées.

Même si MCP Secret Manager est une application d'administration et non une landing page, elle peut contenir :

- logo ;
- icônes ;
- illustrations d'états vides ;
- assets de marque.

Objectifs :

- formats adaptés ;
- tailles maîtrisées ;
- chargement paresseux lorsque pertinent ;
- absence d'assets inutiles ;
- cohérence visuelle.

Les images ne doivent jamais contenir d'informations sensibles.

# Accessibilité

L'accessibilité est obligatoire dès le MVP.

Une application de sécurité doit être utilisable par des personnes, équipements et contextes variés. L'accessibilité réduit les erreurs, améliore la qualité et renforce la confiance.

## Navigation clavier

Toutes les actions principales doivent être accessibles au clavier.

Cela inclut :

- navigation ;
- menus ;
- modales ;
- formulaires ;
- tables interactives ;
- filtres ;
- tabs ;
- boutons d'action ;
- confirmations ;
- fermeture de panneaux.

L'ordre de tabulation doit suivre la structure visuelle et logique de la page.

## Focus

Le focus doit être visible et cohérent.

Règles :

- ne jamais supprimer le focus sans alternative ;
- déplacer le focus dans les modales ;
- restaurer le focus après fermeture ;
- mettre le focus sur les erreurs de formulaire lorsque pertinent ;
- rendre les états focus visibles en light et dark mode.

Le focus est particulièrement important pour les actions sensibles. L'utilisateur doit savoir exactement quelle action il déclenche.

## ARIA

ARIA doit être utilisé lorsque les éléments natifs ne suffisent pas.

Objectifs :

- nommer les composants interactifs ;
- relier messages d'erreur et champs ;
- décrire les dialogs ;
- rendre les menus et tabs accessibles ;
- informer sur les états de chargement ou succès lorsque nécessaire.

ARIA ne doit pas compenser une mauvaise sémantique HTML. Les éléments natifs doivent être privilégiés.

## Lecteurs d'écran

L'application doit fournir une expérience compréhensible avec lecteurs d'écran.

Cela implique :

- landmarks cohérents ;
- titres structurés ;
- boutons nommés ;
- champs labellisés ;
- états annoncés lorsque pertinent ;
- tables avec en-têtes ;
- messages d'erreur associés ;
- actions sensibles clairement décrites.

Les valeurs secrètes masquées doivent être annoncées de manière sûre, sans révélation involontaire.

## Contrastes

Les contrastes doivent respecter les standards d'accessibilité.

Attention particulière :

- textes secondaires ;
- badges ;
- statuts ;
- erreurs ;
- avertissements ;
- focus rings ;
- dark mode ;
- disabled states ;
- tableaux denses.

La couleur seule ne doit jamais être l'unique moyen de comprendre un état.

## Formulaires accessibles

Les formulaires doivent être conçus pour l'accessibilité.

Règles :

- labels visibles ou accessibles ;
- descriptions lorsque nécessaire ;
- erreurs par champ ;
- messages de validation clairs ;
- groupement des champs liés ;
- indication des champs requis ;
- soumission clavier ;
- focus sur erreur critique ;
- absence de placeholder comme unique label.

Les formulaires sensibles doivent aussi expliquer les conséquences des actions lorsque cela est nécessaire.

# Tests

La stratégie de tests doit couvrir plusieurs niveaux.

Le but n'est pas d'obtenir une couverture artificielle, mais de protéger les workflows critiques, les composants partagés et les frontières de données.

## Unit tests

Les unit tests vérifient des unités isolées.

Ils couvrent :

- helpers de formatage ;
- mappings DTO vers UI ;
- validation Zod ;
- logique de construction de query params ;
- normalisation d'erreurs ;
- fonctions utilitaires ;
- hooks simples lorsque pertinent.

Rôle :

- détecter rapidement les régressions ;
- documenter les règles locales ;
- faciliter les refactorisations.

Les unit tests doivent rester rapides et ciblés.

## Component tests

Les component tests vérifient le rendu et les interactions de composants isolés ou semi-isolés.

Ils couvrent :

- formulaires ;
- dialogs ;
- tables ;
- badges d'état ;
- composants de champ secret ;
- états vides ;
- composants d'erreur ;
- composants de confirmation.

Rôle :

- garantir l'accessibilité de base ;
- vérifier les interactions utilisateur ;
- éviter les régressions visuelles fonctionnelles ;
- valider les états sensibles.

Les component tests doivent privilégier le comportement observable par l'utilisateur.

## Integration tests

Les integration tests vérifient la collaboration entre plusieurs éléments frontend.

Ils couvrent :

- page avec chargement de données ;
- formulaire avec mutation ;
- invalidation après mutation ;
- gestion d'erreur API ;
- changement de filtre ;
- pagination ;
- affichage conditionnel selon réponse backend ;
- session expirée dans un workflow.

Rôle :

- valider que les features fonctionnent comme un ensemble ;
- couvrir les frontières API/UI ;
- vérifier les scénarios critiques sans navigateur complet lorsque possible.

## End-to-end tests

Les end-to-end tests vérifient les parcours utilisateur complets.

Parcours prioritaires :

- login ;
- accès route protégée ;
- création d'un vault ;
- création d'un projet ;
- création d'un secret ;
- création d'une version ;
- révélation ponctuelle d'une valeur si autorisée ;
- création d'une API key ;
- révocation d'une API key ;
- consultation et filtrage des audit logs ;
- refus d'accès ;
- logout.

Rôle :

- garantir que les workflows critiques fonctionnent de bout en bout ;
- détecter les ruptures d'intégration ;
- vérifier l'expérience réelle ;
- protéger les scénarios sensibles.

Les tests end-to-end doivent rester stables. Ils doivent éviter les assertions trop fragiles liées à des détails visuels non essentiels.

# Conventions

Les conventions suivantes doivent être appliquées dans tout le projet.

Elles servent à réduire les débats récurrents, faciliter les revues et maintenir une cohérence forte.

## Nommage

Les noms doivent être explicites, lisibles et alignés avec le domaine.

Règles :

- utiliser les termes produit officiels ;
- éviter les abréviations ambiguës ;
- distinguer metadata et value ;
- distinguer API key, token et session ;
- distinguer vault, project, secret et version ;
- nommer les statuts de manière cohérente.

Un nom doit aider à comprendre le rôle sans ouvrir le fichier.

## Composants

Les composants doivent suivre des responsabilités claires.

Règles :

- composants de présentation séparés des appels API ;
- composants courts lorsque possible ;
- props explicites ;
- pas de composant générique avant répétition réelle ;
- actions sensibles représentées avec des composants cohérents ;
- composants accessibles par défaut.

Les composants partagés vivent dans `components/`. Les composants propres à une feature vivent dans la feature.

## Hooks

Les hooks doivent encapsuler une logique réutilisable.

Règles :

- hooks de données dans la feature concernée ;
- hooks UI transverses dans `hooks/` ;
- noms explicites ;
- pas de hook fourre-tout ;
- pas de logique métier sécurité côté client ;
- gestion claire des erreurs et états de chargement.

Un hook doit avoir un rôle précis : charger, muter, gérer une interaction ou encapsuler un comportement.

## Types

Les types doivent exprimer les contrats.

Règles :

- DTO proches de l'API ;
- modèles UI séparés lorsque nécessaire ;
- types spécifiques dans les features ;
- types transverses dans `types/` ;
- statuts représentés explicitement ;
- éviter les types trop larges ;
- éviter les données optionnelles partout par confort.

TypeScript doit aider à prévenir les erreurs de domaine, pas seulement satisfaire le compilateur.

## Fichiers

Les fichiers doivent être nommés selon leur rôle.

Règles :

- noms clairs ;
- pas de fichiers géants ;
- pas de regroupement artificiel sans cohésion ;
- tests proches du code lorsque utile ;
- fichiers de feature organisés par responsabilité ;
- index publics utilisés avec prudence.

Un fichier doit avoir une responsabilité compréhensible.

## Imports

Les imports doivent respecter les frontières.

Règles :

- `app/` peut composer les features ;
- les features peuvent utiliser `components/`, `hooks/`, `lib/` et `types/` ;
- les composants partagés ne doivent pas dépendre des features ;
- `lib/` ne doit pas dépendre de l'UI ;
- éviter les imports profonds entre features ;
- éviter les cycles ;
- préférer les alias configurés lorsqu'ils améliorent la lisibilité.

Les dépendances doivent aller des couches spécifiques vers les couches partagées, pas l'inverse.

## Exports

Les exports doivent rester maîtrisés.

Règles :

- exposer uniquement ce qui est nécessaire ;
- éviter les barrels trop larges qui masquent les dépendances ;
- créer des points d'entrée publics de feature lorsque cela clarifie l'usage ;
- ne pas exporter des détails internes par confort ;
- éviter les collisions de noms.

Un export public devient une surface de dépendance. Il doit être choisi volontairement.

# Principes de sécurité

Le frontend a des responsabilités de sécurité importantes, même s'il n'est pas la source d'autorité.

Il doit protéger l'utilisateur contre les erreurs, limiter l'exposition des données sensibles et respecter strictement les décisions du backend.

## Ne jamais stocker un secret inutilement

Une valeur secrète ne doit jamais être stockée sans nécessité.

Règles :

- pas de valeur secrète dans localStorage ;
- pas de valeur secrète dans sessionStorage ;
- pas de valeur secrète dans les URLs ;
- pas de valeur secrète dans les query params ;
- pas de valeur secrète dans un cache durable ;
- pas de valeur secrète dans les logs ;
- pas de valeur secrète dans les analytics ;
- pas de valeur secrète dans les messages d'erreur.

Si une valeur est révélée, elle doit rester temporaire, locale et disparaître dès que l'action est terminée ou que la vue change.

## Ne jamais faire confiance au client

Le client est modifiable par définition.

Le frontend ne doit donc jamais supposer qu'une restriction visuelle suffit. Masquer un bouton ne protège rien si l'API autorise l'action.

Toutes les opérations sensibles doivent être validées par le backend.

Le frontend peut améliorer l'expérience en désactivant ou masquant des actions selon les informations reçues, mais il doit toujours gérer le refus backend comme cas normal.

## Masquer les valeurs par défaut

Les valeurs secrètes doivent être masquées par défaut.

La révélation doit être :

- volontaire ;
- ponctuelle ;
- visuellement claire ;
- idéalement confirmée selon le niveau de risque ;
- auditée côté backend ;
- limitée dans le temps lorsque possible.

La copie d'une valeur doit aussi être traitée comme une action sensible.

## Toujours respecter le RBAC backend

Le frontend doit afficher et respecter le modèle RBAC retourné par le backend.

Il ne doit pas :

- inventer des permissions ;
- recalculer des autorisations complexes ;
- accorder une action sur la base d'un rôle supposé ;
- contourner un refus ;
- cacher une erreur d'autorisation comme une erreur générique.

Lorsque le backend refuse une action, l'interface doit expliquer le refus de manière sûre.

## Ne jamais exposer d'informations sensibles dans les logs

Les logs frontend doivent être minimaux et prudents.

Interdictions :

- logger une valeur secrète ;
- logger un token ;
- logger un refresh token ;
- logger un payload complet de création de secret ;
- logger des headers sensibles ;
- logger des erreurs brutes contenant des détails internes ;
- envoyer des données sensibles à un outil de monitoring ou analytics.

Les logs de développement doivent aussi respecter cette règle. Une fuite en développement peut devenir une habitude dangereuse.

## Protéger les actions sensibles

Les actions sensibles doivent être clairement identifiées et confirmées.

Exemples :

- révéler une valeur ;
- copier une valeur ;
- créer une API key ;
- révoquer une API key ;
- modifier un rôle ;
- retirer une permission ;
- archiver une ressource ;
- verrouiller un vault ;
- supprimer logiquement un secret ;
- modifier des paramètres de sécurité.

La confirmation doit indiquer la ressource et la conséquence principale.

## Nettoyer les états sensibles

Les états contenant des informations sensibles doivent être nettoyés.

Situations :

- fermeture d'une modale ;
- changement de route ;
- logout ;
- expiration de session ;
- erreur inattendue ;
- fin d'une action de copie ;
- changement de contexte vault ou projet.

Le nettoyage doit être une règle d'architecture, pas une correction ponctuelle.

# Évolutivité

Cette architecture est conçue pour accompagner la croissance du produit sans refonte majeure.

L'objectif n'est pas de construire toutes les fonctionnalités futures dès maintenant, mais de préparer les frontières nécessaires.

## Multi-tenant

Le multi-tenant pourra être ajouté en introduisant un contexte tenant dans :

- routing ;
- session ;
- API layer ;
- providers ;
- query keys ;
- navigation ;
- paramètres.

L'architecture feature-first permet de rendre les features conscientes du tenant via des contrats explicites, sans dupliquer toute l'application.

Les caches devront être isolés par tenant afin d'éviter les mélanges de données.

## SDK Web

Un SDK Web futur pourra s'appuyer sur l'API layer et certains types partagés.

La séparation entre API, features et UI permettra d'extraire ou réutiliser une partie des appels backend sans embarquer l'interface complète.

Cela exige dès le départ de ne pas mélanger client HTTP, composants React et logique d'affichage.

## Monitoring

Le monitoring pourra être ajouté comme feature dédiée.

Il pourra utiliser :

- routes protégées ;
- dashboards spécialisés ;
- TanStack Query ;
- streaming ou revalidation ;
- composants de visualisation chargés paresseusement ;
- API layer standard.

L'architecture actuelle permet de l'ajouter sans modifier vault, secret ou audit au-delà des liens contextuels nécessaires.

## Notifications

Les notifications pourront être ajoutées via :

- provider global léger ;
- feature dédiée ;
- API layer ;
- composants partagés ;
- éventuel canal temps réel futur.

Les notifications devront respecter les règles de sécurité : aucun secret dans les messages, aucun payload sensible dans les outils tiers et préférences utilisateur séparées.

## WebSockets

Les WebSockets pourront être ajoutés pour certaines données temps réel.

Cas possibles :

- notifications ;
- monitoring ;
- événements d'audit récents ;
- état de jobs ;
- rotations futures.

L'ajout devra passer par un provider ou service spécialisé, sans remplacer TanStack Query pour tout l'état serveur.

Les événements temps réel devront invalider ou mettre à jour les caches de manière contrôlée.

## Temps réel

Le temps réel doit rester ciblé.

Il ne doit pas transformer toute l'application en flux permanent. Les ressources de sécurité doivent rester stables, auditables et compréhensibles.

Le temps réel est pertinent pour :

- alertes ;
- activité récente ;
- monitoring ;
- notifications ;
- logs récents ;
- jobs asynchrones.

Il est moins pertinent pour des formulaires ou pages de détail où la stabilité est plus importante.

## Analytics

Les analytics pourront être ajoutés comme feature et comme couche d'observation produit.

Deux formes doivent être distinguées :

- analytics produit internes à l'interface ;
- analytics métier sur l'usage des secrets.

Dans les deux cas, aucune valeur secrète ne doit être collectée. Les données doivent être minimisées, agrégées lorsque possible et contrôlées.

L'architecture séparant API, UI et features permet d'intégrer des graphiques ou vues analytiques sans contaminer les features existantes.

## Billing

Le billing pourra être ajouté comme feature SaaS dédiée.

Il nécessitera :

- routes protégées ;
- paramètres d'organisation ou tenant ;
- API layer spécifique ;
- composants de plan et usage ;
- états de limitation ;
- intégration future avec provider de paiement.

La structure `features/` permet d'ajouter billing sans modifier les features de sécurité, sauf pour afficher certains états de limites si nécessaire.

# Conclusion

L'architecture frontend de MCP Secret Manager doit produire une application SaaS moderne, fiable et maintenable, capable d'administrer un produit de sécurité sans diluer les garanties du backend.

Le choix de Next.js 15, React 19, TypeScript, App Router, Tailwind CSS, shadcn/ui, TanStack Query, React Hook Form et Zod fournit un socle cohérent pour construire une interface rapide, accessible, typée, composable et évolutive.

L'organisation feature-first permet de garder les domaines compréhensibles : dashboard, vaults, projects, secrets, versions, API keys, audit, RBAC, profil et paramètres. Les dossiers transverses fournissent le design system, les providers, les hooks communs, l'API layer, les types et les utilitaires sans absorber la logique métier.

Les principes d'architecture fixent une règle centrale : le frontend rend la sécurité administrable, mais le backend reste l'autorité. L'API est la source de vérité. Le client ne porte pas de logique de permission métier définitive. Les valeurs secrètes sont masquées, temporaires et jamais stockées inutilement.

Cette architecture est adaptée au MVP parce qu'elle reste simple et pragmatique. Elle est adaptée au long terme parce qu'elle prépare l'ajout de multi-tenant, monitoring, notifications, WebSockets, temps réel, analytics, billing, SDK Web et fonctionnalités Enterprise sans refonte majeure.

Le frontend doit être construit avec la même rigueur que le backend : frontières claires, responsabilités explicites, sécurité visible, expérience premium et capacité à évoluer sans perdre sa lisibilité.
