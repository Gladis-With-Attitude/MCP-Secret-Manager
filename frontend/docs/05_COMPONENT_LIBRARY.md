# Introduction

La Component Library de MCP Secret Manager définit l'ensemble des composants réutilisables du frontend.

Elle existe pour garantir que l'application reste cohérente, maintenable, accessible et sûre pendant toute son évolution. MCP Secret Manager est une console SaaS d'administration pour un produit de sécurité. Chaque composant influence donc la compréhension de l'utilisateur, la perception de confiance et la réduction des erreurs opérationnelles.

Une bibliothèque de composants n'est pas seulement un catalogue visuel. C'est un contrat d'usage entre design, produit et développement. Elle précise quels composants existent, à quoi ils servent, comment ils doivent être utilisés, quels états ils doivent gérer et quelles limites ils ne doivent pas dépasser.

La cohérence est particulièrement importante dans MCP Secret Manager pour plusieurs raisons :

- les utilisateurs manipulent des secrets, clés API, rôles, permissions et audit logs ;
- les actions sensibles doivent être identifiables partout de la même manière ;
- les états comme archived, locked, revoked ou current version ne doivent jamais être ambigus ;
- les formulaires doivent réduire les erreurs ;
- les dialogs doivent expliquer clairement les conséquences ;
- les tables doivent rester scannables ;
- les valeurs secrètes doivent être masquées par défaut ;
- l'accessibilité doit être garantie sur tous les composants interactifs.

Le projet privilégie la réutilisation plutôt que la recréation.

Réutiliser un composant validé permet :

- d'assurer une expérience homogène ;
- de réduire les bugs ;
- de faciliter les tests ;
- d'accélérer l'implémentation ;
- de rendre les revues plus simples ;
- de préserver l'accessibilité ;
- d'appliquer les règles de sécurité de manière constante.

Créer un nouveau composant est justifié lorsqu'un besoin réel n'est pas couvert, lorsqu'un composant existant serait détourné de son rôle ou lorsqu'un nouveau pattern devient suffisamment stable pour être formalisé.

La Component Library suit un principe central : les composants partagés doivent rester génériques et réutilisables, tandis que les composants métier doivent vivre dans les features concernées. Un composant partagé peut afficher un badge, une table ou un dialog. Il ne doit pas connaître les règles internes d'un vault, d'un secret, d'une permission ou d'un audit log sauf s'il s'agit explicitement d'un composant métier dédié documenté dans cette bibliothèque.

# Layout Components

Les Layout Components structurent l'application. Ils définissent les zones principales, la navigation, le contexte de page et les séparations visuelles.

Ils doivent rester stables, sobres et prévisibles. Un layout ne doit pas contenir de logique métier complexe.

## AppLayout

Rôle :

AppLayout est le layout principal de l'application authentifiée. Il fournit le cadre global de la console.

Responsabilités :

- afficher Sidebar ;
- afficher Topbar ;
- définir la zone de contenu principale ;
- gérer les contraintes de largeur et hauteur ;
- accueillir les providers visuels nécessaires ;
- préserver une structure stable entre les routes protégées ;
- permettre une navigation responsive.

Variantes :

- layout desktop avec Sidebar visible ;
- layout tablet avec Sidebar repliable ;
- layout mobile avec navigation en drawer ;
- layout futur multi-tenant avec sélecteur de contexte.

Bonnes pratiques :

- garder le shell stable pendant la navigation ;
- éviter les sauts visuels ;
- réserver la logique métier aux pages ou features ;
- préserver l'accessibilité des landmarks ;
- maintenir une séparation claire entre navigation et contenu.

Mauvaises pratiques :

- charger des données métier détaillées dans AppLayout ;
- intégrer des formulaires métier globaux ;
- afficher des secrets ou données sensibles dans le shell ;
- rendre tout l'arbre client sans nécessité ;
- dupliquer la navigation dans les pages.

## PublicLayout

Rôle :

PublicLayout structure les pages accessibles sans session.

Responsabilités :

- encadrer Login ;
- afficher une identité produit minimale ;
- proposer une expérience sobre ;
- éviter toute fuite d'information privée ;
- fournir des zones d'erreur publique.

Variantes :

- login ;
- page publique d'erreur ;
- page future de récupération de compte ;
- page future SSO.

Bonnes pratiques :

- rester minimal ;
- ne pas afficher d'informations sur l'instance ;
- préserver une hiérarchie claire ;
- fonctionner parfaitement sur mobile.

Mauvaises pratiques :

- afficher des liens vers ressources internes ;
- afficher des statistiques ;
- exposer une version détaillée du backend si non nécessaire ;
- utiliser un design marketing trop éloigné de l'application.

## AuthLayout

Rôle :

AuthLayout encadre spécifiquement les écrans d'authentification.

Responsabilités :

- centrer ou structurer le formulaire ;
- gérer les messages de session expirée ;
- afficher les erreurs globales ;
- préserver le focus ;
- offrir une expérience sécurisée.

Variantes :

- login classique ;
- MFA futur ;
- SSO futur ;
- reset password futur.

Bonnes pratiques :

- garder le formulaire lisible ;
- associer erreurs et champs ;
- éviter les distractions ;
- rendre la soumission claire.

Mauvaises pratiques :

- afficher trop de texte ;
- révéler si un utilisateur existe ;
- masquer les erreurs sous des messages vagues ;
- stocker des credentials localement.

## PageHeader

Rôle :

PageHeader présente le contexte principal d'une page.

Responsabilités :

- afficher le titre ;
- afficher une description courte si utile ;
- afficher les badges d'état majeurs ;
- afficher les actions principales ;
- accueillir un breadcrumb si nécessaire ;
- rendre le contexte immédiatement compréhensible.

Variantes :

- header de liste ;
- header de détail ;
- header avec actions ;
- header avec badges ;
- header compact mobile.

Bonnes pratiques :

- une action principale clairement identifiable ;
- badges d'état proches du titre ;
- description courte ;
- actions dangereuses séparées.

Mauvaises pratiques :

- plusieurs actions Primary concurrentes ;
- titres trop longs ;
- badges secondaires trop nombreux ;
- actions sensibles sans confirmation.

## Sidebar

Rôle :

Sidebar fournit la navigation principale des routes protégées.

Responsabilités :

- afficher les sections principales ;
- indiquer la section active ;
- organiser les groupes ;
- rester utilisable au clavier ;
- s'adapter aux permissions si le backend fournit les informations nécessaires ;
- se transformer sur mobile.

Variantes :

- expanded ;
- collapsed futur ;
- mobile drawer ;
- tenant-aware futur.

Bonnes pratiques :

- garder les labels stables ;
- utiliser des icônes cohérentes ;
- ne pas masquer une section de manière incohérente ;
- préserver l'ordre de navigation.

Mauvaises pratiques :

- dupliquer les actions de page ;
- inclure des données sensibles ;
- changer l'ordre selon les écrans ;
- utiliser uniquement des icônes sans labels dans les modes principaux.

## Topbar

Rôle :

Topbar fournit les actions globales et le contexte utilisateur.

Responsabilités :

- afficher recherche globale si disponible ;
- afficher menu profil ;
- afficher notifications futures ;
- afficher command palette future ;
- afficher contexte tenant futur ;
- fournir accès logout via profil.

Variantes :

- topbar simple MVP ;
- topbar avec recherche ;
- topbar avec notifications ;
- topbar mobile.

Bonnes pratiques :

- rester sobre ;
- ne pas concurrencer PageHeader ;
- garder les actions globales uniquement ;
- éviter les informations sensibles.

Mauvaises pratiques :

- placer des actions métier spécifiques ;
- afficher des secrets ;
- surcharger avec des widgets ;
- cacher le profil ou logout.

## Breadcrumb

Rôle :

Breadcrumb rend visible la hiérarchie de navigation.

Responsabilités :

- afficher le chemin contextuel ;
- permettre le retour vers les parents ;
- clarifier vault, project, secret et version ;
- respecter les permissions de navigation.

Variantes :

- simple ;
- avec objets tronqués ;
- avec statuts ;
- mobile compact.

Bonnes pratiques :

- utiliser des labels lisibles ;
- tronquer proprement ;
- ne pas révéler de ressources non autorisées ;
- garder le dernier élément non ambigu.

Mauvaises pratiques :

- afficher des valeurs secrètes ;
- créer des chemins trop longs sans truncation ;
- utiliser le breadcrumb comme navigation principale ;
- l'omettre sur les pages de détail hiérarchiques.

## Section

Rôle :

Section regroupe un bloc logique de contenu dans une page.

Responsabilités :

- structurer le contenu ;
- afficher un titre local ;
- accueillir description, actions et contenu ;
- séparer visuellement sans lourdeur.

Variantes :

- section simple ;
- section avec action ;
- section dense ;
- section de formulaire ;
- section de détail.

Bonnes pratiques :

- un objectif par section ;
- titre clair ;
- action locale alignée avec le contenu ;
- espacement cohérent.

Mauvaises pratiques :

- utiliser Section comme Card décorative ;
- imbriquer trop profondément ;
- mélanger plusieurs sujets ;
- cacher les actions sensibles dans un coin peu visible.

## Card

Rôle :

Card regroupe une unité d'information autonome.

Responsabilités :

- présenter un résumé ;
- isoler un bloc de dashboard ;
- afficher un état vide ;
- regrouper des paramètres ;
- contenir une ressource lorsqu'une table n'est pas adaptée.

Variantes :

- stat card ;
- summary card ;
- settings card ;
- empty card ;
- security card.

Bonnes pratiques :

- utiliser pour une unité claire ;
- garder une hiérarchie interne ;
- limiter les actions ;
- préférer bordure ou surface à ombre forte.

Mauvaises pratiques :

- mettre des cartes dans des cartes ;
- remplacer toutes les tables par des cartes ;
- utiliser comme décoration ;
- créer des cartes trop grandes sans information utile.

## Divider

Rôle :

Divider sépare visuellement des groupes.

Responsabilités :

- clarifier les sections ;
- structurer les menus ;
- séparer les zones d'un dialog ;
- organiser les panneaux.

Variantes :

- horizontal ;
- vertical ;
- discret ;
- section divider.

Bonnes pratiques :

- utiliser avec parcimonie ;
- préférer l'espacement lorsque suffisant ;
- maintenir une couleur discrète ;
- éviter la surcharge visuelle.

Mauvaises pratiques :

- créer une grille trop marquée ;
- utiliser comme décoration ;
- remplacer une vraie hiérarchie ;
- multiplier les séparateurs dans une table déjà structurée.

# Navigation Components

Les Navigation Components permettent de se déplacer, filtrer, chercher et explorer l'application.

Ils doivent être prévisibles, accessibles et cohérents.

## NavItem

Rôle :

NavItem représente une entrée de navigation individuelle.

Responsabilités :

- afficher label ;
- afficher icône ;
- indiquer état actif ;
- gérer disabled si nécessaire ;
- supporter focus clavier ;
- éventuellement afficher un badge.

Bonnes pratiques :

- label explicite ;
- icône stable ;
- état actif visible ;
- tooltip en mode compact.

Mauvaises pratiques :

- icône seule sans aide ;
- état actif uniquement par couleur ;
- action dangereuse dans un item de navigation ;
- changement de destination selon contexte non visible.

## NavGroup

Rôle :

NavGroup regroupe plusieurs NavItems.

Responsabilités :

- organiser les sections ;
- améliorer la lecture ;
- permettre collapse futur ;
- fournir un label de groupe si utile.

Bonnes pratiques :

- groupes peu nombreux ;
- noms courts ;
- ordre stable ;
- séparation logique.

Mauvaises pratiques :

- trop de groupes ;
- groupes changeants par route ;
- mélange de navigation et actions ;
- labels marketing.

## Tabs

Rôle :

Tabs permet de naviguer entre sous-vues d'un même contexte.

Responsabilités :

- afficher l'onglet actif ;
- préserver le contexte ;
- supporter clavier ;
- éventuellement refléter l'état dans l'URL ;
- ne pas remplacer la navigation principale.

Bonnes pratiques :

- utiliser pour des vues de même niveau ;
- labels courts ;
- contenu chargé proprement ;
- état actif visible.

Mauvaises pratiques :

- tabs trop nombreuses ;
- actions dans tabs ;
- tabs imbriquées excessivement ;
- masquer des erreurs de chargement dans un onglet.

## Pagination

Rôle :

Pagination permet de naviguer dans des listes longues.

Responsabilités :

- afficher page ou curseur ;
- indiquer précédent/suivant ;
- préserver filtres ;
- gérer disabled ;
- rester accessible.

Bonnes pratiques :

- conserver recherche et filtres ;
- afficher une information de résultat si disponible ;
- éviter les sauts visuels ;
- rendre les contrôles tactiles suffisants.

Mauvaises pratiques :

- perdre les filtres au changement de page ;
- cacher l'état de chargement ;
- permettre une page invalide ;
- mélanger pagination et tri de manière confuse.

## SearchBar

Rôle :

SearchBar permet de rechercher dans une liste ou globalement.

Responsabilités :

- saisir une requête ;
- gérer clear ;
- indiquer loading ;
- être accessible ;
- éviter la recherche dans les valeurs secrètes.

Bonnes pratiques :

- placeholder précis ;
- debounce si pertinent ;
- état sans résultat clair ;
- portée de recherche compréhensible.

Mauvaises pratiques :

- rechercher dans des secrets values ;
- placeholder comme seule explication ;
- lancer trop de requêtes ;
- confondre recherche globale et filtre local.

## FilterBar

Rôle :

FilterBar regroupe les filtres d'une liste.

Responsabilités :

- afficher filtres actifs ;
- permettre réinitialisation ;
- gérer filtres avancés ;
- rester responsive ;
- conserver l'état dans l'URL lorsque pertinent.

Bonnes pratiques :

- filtres les plus utiles visibles ;
- filtres actifs identifiables ;
- reset facile ;
- mobile en drawer ou panneau.

Mauvaises pratiques :

- trop de filtres visibles ;
- filtres sans label ;
- état impossible à comprendre ;
- filtres qui révèlent des ressources non autorisées.

## Command Palette (future)

Rôle :

Command Palette offrira une navigation et des actions rapides.

Responsabilités futures :

- rechercher des routes ;
- rechercher des ressources autorisées ;
- déclencher des actions non sensibles ;
- ouvrir des workflows avec confirmation ;
- respecter les permissions backend.

Bonnes pratiques :

- actions nommées ;
- contexte visible ;
- confirmations pour actions sensibles ;
- aucune révélation de secret.

Mauvaises pratiques :

- révéler une valeur directement ;
- exécuter une action dangereuse sans confirmation ;
- afficher des ressources non autorisées ;
- devenir une seconde UI incohérente.

# Form Components

Les Form Components doivent rendre les formulaires accessibles, cohérents et sûrs.

Ils s'appuient sur les principes de validation frontend, tout en respectant le fait que la validation backend reste définitive.

## TextInput

Rôle :

TextInput permet la saisie de texte simple.

Responsabilités :

- afficher label via FormField ;
- gérer état normal, focus, disabled, error ;
- supporter description ;
- transmettre les erreurs ;
- être accessible.

Accessibilité :

- label associé ;
- état erreur annoncé ;
- focus visible ;
- taille de cible correcte.

Validation :

- requis ;
- longueur ;
- format ;
- caractères autorisés selon contexte.

Erreurs :

- proches du champ ;
- claires ;
- non techniques.

## PasswordInput

Rôle :

PasswordInput permet la saisie d'un mot de passe.

Responsabilités :

- masquer par défaut ;
- permettre reveal si retenu ;
- éviter logs ;
- gérer autocomplete selon contexte ;
- afficher erreurs.

Accessibilité :

- bouton show/hide nommé ;
- indication d'état ;
- label visible ;
- focus clair.

Mauvaises pratiques :

- afficher le mot de passe par défaut ;
- conserver la valeur après logout ;
- afficher le mot de passe dans une erreur ;
- utiliser pour un secret applicatif hors contexte.

## SecretInput

Rôle :

SecretInput permet la saisie d'une valeur secrète.

Responsabilités :

- masquer la valeur par défaut ;
- éviter persistance ;
- permettre reveal volontaire ;
- permettre clear ;
- gérer copy seulement si nécessaire ;
- nettoyer après soumission ou fermeture ;
- ne jamais logger.

Accessibilité :

- label explicite ;
- aide claire ;
- bouton reveal nommé ;
- bouton clear nommé ;
- message d'erreur associé.

Validation :

- requis selon workflow ;
- longueur minimale ou maximale si applicable ;
- format si le secret a un type ;
- validation non intrusive.

Erreurs :

- jamais afficher la valeur ;
- message sûr ;
- correction claire.

## TextArea

Rôle :

TextArea permet la saisie de texte multi-ligne.

Responsabilités :

- descriptions ;
- notes non sensibles ;
- métadonnées longues ;
- commentaires de version si supportés.

Bonnes pratiques :

- limiter la hauteur ;
- indiquer longueur si nécessaire ;
- ne pas utiliser pour valeurs secrètes sauf composant spécialisé.

Mauvaises pratiques :

- utiliser pour stocker des secrets sans traitement sensible ;
- laisser redimensionnement casser le layout ;
- accepter de longues données sans validation.

## Select

Rôle :

Select permet de choisir une option unique.

Responsabilités :

- afficher options ;
- gérer valeur sélectionnée ;
- supporter disabled ;
- afficher erreurs ;
- fonctionner au clavier.

Usages :

- vault ;
- project ;
- rôle ;
- statut ;
- type ;
- période.

Mauvaises pratiques :

- options trop nombreuses sans recherche ;
- labels ambigus ;
- valeurs non autorisées ;
- absence d'état loading pour options distantes.

## MultiSelect

Rôle :

MultiSelect permet de choisir plusieurs options.

Responsabilités :

- afficher sélection ;
- permettre suppression ;
- gérer options nombreuses ;
- supporter recherche si nécessaire ;
- rester accessible.

Usages :

- permissions ;
- tags ;
- filtres ;
- acteurs futurs.

Mauvaises pratiques :

- utiliser pour permissions critiques sans confirmation ;
- afficher trop de badges sans regroupement ;
- ne pas expliquer les options sélectionnées.

## Checkbox

Rôle :

Checkbox représente un choix binaire ou une sélection multiple.

Responsabilités :

- état coché ;
- état indéterminé si nécessaire ;
- label ;
- focus ;
- disabled.

Usages :

- sélection de ligne ;
- option simple ;
- confirmation explicite.

Mauvaises pratiques :

- utiliser sans label ;
- utiliser pour une action immédiate dangereuse ;
- rendre disabled sans explication.

## Switch

Rôle :

Switch représente l'activation ou désactivation d'une option.

Responsabilités :

- état on/off ;
- label ;
- feedback ;
- confirmation si option sensible.

Usages :

- préférences ;
- paramètres non destructifs ;
- options futures.

Mauvaises pratiques :

- utiliser pour action destructive ;
- changer un paramètre critique sans confirmation ;
- état ambigu.

## RadioGroup

Rôle :

RadioGroup permet de choisir une option parmi plusieurs visibles.

Responsabilités :

- afficher options ;
- expliquer différences ;
- supporter clavier ;
- état sélectionné clair.

Usages :

- choix de mode ;
- type d'acteur ;
- niveau de scope ;
- options limitées.

Mauvaises pratiques :

- trop d'options ;
- labels trop longs ;
- options non comparables.

## DatePicker

Rôle :

DatePicker permet de choisir une date ou période.

Responsabilités :

- sélection accessible ;
- format lisible ;
- validation ;
- gestion timezone ;
- erreurs.

Usages :

- filtres audit ;
- expiration API key future ;
- périodes analytics futures.

Mauvaises pratiques :

- format ambigu ;
- timezone implicite pour audit ;
- date impossible non expliquée.

## FormField

Rôle :

FormField enveloppe label, contrôle, aide et erreur.

Responsabilités :

- associer label et champ ;
- afficher description ;
- afficher ValidationMessage ;
- gérer required ;
- standardiser l'espacement.

Bonnes pratiques :

- un champ par FormField ;
- label clair ;
- erreur proche ;
- aide concise.

Mauvaises pratiques :

- plusieurs contrôles non liés dans un seul FormField ;
- placeholder comme label ;
- messages longs.

## FormSection

Rôle :

FormSection regroupe des champs liés.

Responsabilités :

- structurer un formulaire ;
- afficher titre ;
- afficher description ;
- séparer les zones sensibles.

Usages :

- metadata ;
- permissions ;
- sécurité ;
- préférences.

Mauvaises pratiques :

- trop de sections ;
- sections sans cohérence ;
- mélanger actions dangereuses et champs ordinaires.

## ValidationMessage

Rôle :

ValidationMessage affiche une erreur ou information de validation.

Responsabilités :

- être lisible ;
- être associé au champ ;
- être accessible ;
- rester sûr.

Bonnes pratiques :

- message court ;
- correction possible ;
- ton calme ;
- aucune donnée sensible.

Mauvaises pratiques :

- afficher payload brut ;
- afficher stack trace ;
- blâmer l'utilisateur ;
- masquer les erreurs backend.

# Buttons

Les boutons expriment l'action. Leur variant doit refléter l'importance, le contexte et le risque.

Chaque bouton doit gérer les états hover, focus, active, disabled et loading.

## PrimaryButton

Usage :

PrimaryButton représente l'action principale d'un écran, formulaire ou dialog.

Variantes :

- standard ;
- loading ;
- full width mobile ;
- avec icône.

États :

- default ;
- hover ;
- focus ;
- active ;
- disabled ;
- loading.

Accessibilité :

- label explicite ;
- focus visible ;
- état loading annoncé si nécessaire ;
- pas d'icône seule.

Bon usage :

- créer vault ;
- sauvegarder ;
- confirmer une action positive.

Mauvais usage :

- action dangereuse ;
- plusieurs PrimaryButton concurrents ;
- action secondaire.

## SecondaryButton

Usage :

SecondaryButton représente une action importante mais non principale.

Variantes :

- standard ;
- avec icône ;
- compact.

États :

- default ;
- hover ;
- focus ;
- active ;
- disabled ;
- loading.

Accessibilité :

- label clair ;
- focus visible.

Bon usage :

- annuler ;
- ouvrir une vue secondaire ;
- accéder à un détail.

Mauvais usage :

- remplacer Primary par préférence esthétique ;
- action dangereuse sans traitement Danger.

## OutlineButton

Usage :

OutlineButton représente une action secondaire visible.

Variantes :

- standard ;
- compact ;
- avec icône.

Bon usage :

- ouvrir filtres ;
- changer période ;
- exporter metadata future ;
- action alternative.

Mauvais usage :

- action principale d'un formulaire ;
- action critique.

## GhostButton

Usage :

GhostButton représente une action discrète.

Variantes :

- text ;
- icon with label ;
- compact ;
- table action.

Bon usage :

- action de ligne ;
- menu ;
- close ;
- navigation secondaire.

Mauvais usage :

- action principale ;
- action dangereuse sans signal supplémentaire ;
- bouton invisible hors hover.

## DangerButton

Usage :

DangerButton représente une action à risque.

Variantes :

- standard ;
- loading ;
- destructive confirmation ;
- compact pour menu avec traitement visuel.

États :

- default ;
- hover ;
- focus ;
- active ;
- disabled ;
- loading.

Accessibilité :

- label explicite ;
- focus visible ;
- ne pas dépendre uniquement de la couleur ;
- confirmation associée lorsque nécessaire.

Bon usage :

- révoquer API key ;
- archiver ;
- supprimer logiquement ;
- retirer assignment ;
- verrouiller si impact critique.

Mauvais usage :

- action non dangereuse ;
- simple annulation ;
- feedback d'erreur.

## IconButton

Usage :

IconButton représente une action compacte avec icône.

Variantes :

- default ;
- ghost ;
- outline ;
- danger ;
- table ;
- toolbar.

États :

- default ;
- hover ;
- focus ;
- active ;
- disabled ;
- loading.

Accessibilité :

- nom accessible obligatoire ;
- tooltip recommandé ;
- taille de cible suffisante ;
- focus visible.

Bon usage :

- copier ;
- révéler ;
- masquer ;
- filtrer ;
- rafraîchir ;
- ouvrir menu.

Mauvais usage :

- action ambiguë sans tooltip ;
- action dangereuse sans label dans un contexte critique ;
- icône non standard.

# Tables

Les composants de table sont centraux dans MCP Secret Manager.

Ils doivent favoriser la scannabilité, les actions contextuelles, la pagination, le tri, les filtres et l'accessibilité.

## DataTable

Rôle :

DataTable affiche une collection structurée de ressources.

Responsabilités :

- rendre colonnes ;
- rendre lignes ;
- gérer loading ;
- gérer empty ;
- gérer error local si prévu ;
- supporter tri ;
- supporter actions ;
- rester accessible.

Bonnes pratiques :

- colonnes choisies selon décision utilisateur ;
- valeurs longues tronquées ;
- statuts visibles ;
- actions cohérentes ;
- aucune valeur secrète.

Mauvaises pratiques :

- table trop dense sans hiérarchie ;
- actions cachées sans raison ;
- colonnes décoratives ;
- données sensibles dans cellules.

## TableToolbar

Rôle :

TableToolbar regroupe recherche, filtres et actions de table.

Responsabilités :

- afficher SearchBar ;
- afficher FilterBar ;
- afficher action principale ;
- afficher actions secondaires ;
- gérer responsive.

Bonnes pratiques :

- action principale à droite ou zone stable ;
- recherche visible ;
- filtres actifs clairs.

Mauvaises pratiques :

- trop de contrôles ;
- action dangereuse dans toolbar sans confirmation ;
- mélange de filtres globaux et locaux.

## TableRow

Rôle :

TableRow représente une ressource.

Responsabilités :

- afficher informations clés ;
- gérer hover ;
- supporter clic vers détail si prévu ;
- contenir actions ;
- préserver accessibilité.

Bonnes pratiques :

- zone principale clairement navigable ;
- actions séparées ;
- statut visible ;
- pas de données sensibles.

Mauvaises pratiques :

- ligne entière cliquable avec boutons conflictuels ;
- hover qui déplace le contenu ;
- action dangereuse au clic direct accidentel.

## TableActions

Rôle :

TableActions regroupe les actions d'une ligne.

Responsabilités :

- afficher action principale ;
- afficher menu secondaire ;
- identifier danger ;
- gérer disabled ;
- déclencher confirmations.

Bonnes pratiques :

- limiter le nombre d'actions visibles ;
- libellés explicites ;
- confirmation sensible ;
- ordre cohérent.

Mauvaises pratiques :

- actions différentes selon lignes sans explication ;
- suppression directe ;
- icônes ambiguës.

## EmptyTable

Rôle :

EmptyTable affiche un état vide dans une table.

Responsabilités :

- expliquer l'absence de données ;
- distinguer vide réel et filtre sans résultat ;
- proposer action si autorisée ;
- rester aligné avec la table.

Bonnes pratiques :

- message court ;
- action claire ;
- reset filtres si pertinent.

Mauvaises pratiques :

- afficher juste "No data" ;
- suggérer une action non autorisée ;
- révéler que des ressources existent mais sont interdites.

## ColumnVisibility

Rôle :

ColumnVisibility permet de gérer les colonnes visibles dans les tables futures.

Responsabilités :

- afficher colonnes disponibles ;
- préserver colonnes obligatoires ;
- sauvegarder préférence si prévu ;
- rester non sensible.

Bonnes pratiques :

- ne pas permettre de masquer les informations critiques ;
- préférences non sensibles ;
- reset possible.

Mauvaises pratiques :

- masquer statut ;
- stocker données sensibles en préférence ;
- rendre une table incompréhensible.

## SortHeader

Rôle :

SortHeader rend une colonne triable.

Responsabilités :

- afficher état de tri ;
- supporter clavier ;
- annoncer tri ;
- déclencher changement.

Bonnes pratiques :

- indicateur visible ;
- tri stable ;
- labels accessibles.

Mauvaises pratiques :

- tri caché ;
- tri non annoncé ;
- colonne affichée triable mais non fonctionnelle.

## PaginationFooter

Rôle :

PaginationFooter affiche les contrôles de pagination.

Responsabilités :

- précédent ;
- suivant ;
- page ou curseur ;
- nombre d'éléments si disponible ;
- état disabled ;
- loading discret.

Bonnes pratiques :

- préserver filtres ;
- taille tactile suffisante ;
- feedback sur chargement.

Mauvaises pratiques :

- perdre recherche ;
- afficher une page invalide ;
- masquer erreurs de pagination.

# Status Components

Les Status Components rendent les états, rôles et permissions immédiatement lisibles.

Ils ne doivent jamais dépendre uniquement de la couleur. Le libellé porte toujours le sens.

## Badge

Rôle :

Badge est le composant générique de label compact.

Responsabilités :

- afficher un libellé court ;
- représenter une catégorie ;
- servir de base aux badges spécialisés ;
- rester accessible.

Bonnes pratiques :

- libellés courts ;
- couleur cohérente ;
- taille stable.

Mauvaises pratiques :

- longs paragraphes ;
- badges trop nombreux ;
- couleur seule.

## StatusBadge

Rôle :

StatusBadge affiche un état général.

États :

- active ;
- inactive ;
- pending ;
- failed ;
- disabled ;
- expired.

Responsabilités :

- rendre l'état clair ;
- être cohérent dans les tables et détails ;
- éviter l'ambiguïté.

## RoleBadge

Rôle :

RoleBadge affiche un rôle.

Responsabilités :

- distinguer admin, viewer, maintainer, service account ou rôles futurs ;
- rester lisible ;
- ne pas suggérer une permission non confirmée.

## PermissionBadge

Rôle :

PermissionBadge affiche une permission.

Responsabilités :

- nommer l'action ;
- indiquer le type de ressource si nécessaire ;
- signaler les permissions sensibles ;
- rester compact.

Les permissions de lecture de valeur secrète doivent être plus reconnaissables qu'une permission de lecture metadata.

## ArchivedBadge

Rôle :

ArchivedBadge indique qu'une ressource est archivée.

Responsabilités :

- distinguer archived de deleted ;
- expliquer si nécessaire ;
- atténuer sans masquer.

## LockedBadge

Rôle :

LockedBadge indique qu'une ressource ou contexte est verrouillé.

Responsabilités :

- signaler une restriction forte ;
- rester visible ;
- ne pas être confondu avec archived.

## RevokedBadge

Rôle :

RevokedBadge indique qu'une clé ou token est révoqué.

Responsabilités :

- rendre l'invalidité claire ;
- apparaître dans API Keys et audit ;
- ne pas être confondu avec expired.

## CurrentVersionBadge

Rôle :

CurrentVersionBadge identifie la version courante d'un secret.

Responsabilités :

- distinguer version active et versions historiques ;
- apparaître dans Secret Details et Version History ;
- rester non ambigu.

# Secret Components

Les Secret Components sont des composants sensibles.

Ils doivent appliquer strictement les règles de sécurité UI : valeur masquée par défaut, reveal volontaire, nettoyage, audit visible lorsque pertinent et absence de stockage inutile.

## SecretValue

Rôle :

SecretValue affiche une valeur secrète ou son état masqué.

Responsabilités :

- masquer la valeur par défaut ;
- afficher un placeholder sûr ;
- afficher la valeur uniquement après autorisation et action explicite ;
- gérer expiration d'affichage si retenue ;
- nettoyer la valeur à la fermeture ou changement de contexte ;
- éviter toute persistance.

Bonnes pratiques :

- indiquer que la valeur est masquée ;
- utiliser monospace pour valeur révélée ;
- limiter la largeur ;
- éviter retour à la ligne dangereux pour longues valeurs ;
- ne jamais utiliser dans une table.

Mauvaises pratiques :

- afficher par défaut ;
- stocker dans cache durable ;
- afficher dans toast ;
- passer la valeur à des composants non nécessaires ;
- logger la valeur.

## RevealButton

Rôle :

RevealButton déclenche volontairement la lecture d'une valeur secrète.

Responsabilités :

- indiquer clairement l'action ;
- gérer loading ;
- gérer disabled ;
- déclencher confirmation si nécessaire ;
- appeler le workflow autorisé ;
- afficher erreur de permission.

Bonnes pratiques :

- label explicite ;
- icône cohérente ;
- indiquer audit possible ;
- éviter usage dans listes.

Mauvaises pratiques :

- révélation au hover ;
- révélation automatique au chargement ;
- révélation bulk ;
- action sans feedback.

## CopyButton

Rôle :

CopyButton copie une valeur ou un identifiant.

Responsabilités :

- copier uniquement sur action explicite ;
- afficher feedback bref ;
- ne pas afficher la valeur dans le feedback ;
- gérer erreurs du presse-papiers ;
- distinguer copie de secret et copie d'identifiant.

Bonnes pratiques :

- label ou tooltip clair ;
- feedback "copié" sans valeur ;
- disabled si aucune valeur disponible ;
- nettoyage après copie si nécessaire.

Mauvaises pratiques :

- copie automatique ;
- afficher la valeur copiée ;
- copier une valeur non révélée sans contexte ;
- utiliser la même présentation pour secret et ID non sensible.

## SecretMetadataCard

Rôle :

SecretMetadataCard présente les métadonnées d'un secret.

Responsabilités :

- afficher nom ;
- description ;
- vault ;
- project ;
- statut ;
- version courante ;
- dates ;
- provider ;
- tags non sensibles.

Bonnes pratiques :

- distinguer metadata et value ;
- aucun secret value ;
- badges clairs ;
- actions limitées.

Mauvaises pratiques :

- inclure valeur ;
- masquer le statut ;
- confondre version et secret.

## VersionTimeline

Rôle :

VersionTimeline affiche l'évolution des versions d'un secret.

Responsabilités :

- lister versions ;
- identifier current version ;
- afficher dates ;
- afficher créateur si disponible ;
- permettre navigation ;
- supporter pagination ou compactage si nombreuses versions.

Bonnes pratiques :

- current version visible ;
- aucune valeur affichée ;
- actions sensibles séparées ;
- historique lisible.

Mauvaises pratiques :

- afficher values ;
- rendre les versions modifiables si immutables ;
- masquer la version courante.

# Feedback Components

Les Feedback Components informent l'utilisateur sur les états, erreurs, succès et chargements.

Ils doivent être clairs, courts, accessibles et sûrs.

## Alert

Rôle :

Alert affiche un message important dans le contexte de la page ou section.

Variantes :

- info ;
- success ;
- warning ;
- danger.

Bonnes pratiques :

- message actionnable ;
- pas de données sensibles ;
- icône et texte ;
- lien utile si pertinent.

Mauvaises pratiques :

- stack trace ;
- payload API ;
- message trop long ;
- alerte permanente non pertinente.

## Toast

Rôle :

Toast affiche un feedback temporaire.

Usages :

- sauvegarde réussie ;
- copie réussie ;
- action terminée ;
- erreur courte.

Bonnes pratiques :

- bref ;
- non bloquant ;
- aucune valeur secrète ;
- durée raisonnable.

Mauvaises pratiques :

- afficher secret copié ;
- remplacer une erreur de formulaire ;
- contenir une action critique obligatoire ;
- empiler trop de toasts.

## Banner

Rôle :

Banner affiche une information globale ou persistante.

Usages :

- session bientôt expirée ;
- mode maintenance ;
- warning système ;
- fonctionnalité dégradée.

Bonnes pratiques :

- message global réel ;
- action claire ;
- dismiss si approprié.

Mauvaises pratiques :

- message marketing ;
- alerte locale dans banner global ;
- informations sensibles.

## Progress

Rôle :

Progress affiche l'avancement d'une opération.

Usages :

- import futur ;
- rotation future ;
- synchronisation future ;
- traitement long.

Bonnes pratiques :

- progression honnête ;
- label clair ;
- état terminé ou échoué.

Mauvaises pratiques :

- fausse précision ;
- cacher l'échec ;
- utiliser pour actions instantanées.

## Spinner

Rôle :

Spinner indique une attente courte.

Bonnes pratiques :

- bouton en loading ;
- zone compacte ;
- court délai.

Mauvaises pratiques :

- page entière sans contexte ;
- spinner permanent ;
- remplacer skeleton lorsque structure connue.

## Skeleton

Rôle :

Skeleton préserve la structure pendant le chargement.

Usages :

- tables ;
- cards ;
- détails ;
- dashboard ;
- audit.

Bonnes pratiques :

- dimensions proches du contenu ;
- pas de fausses données ;
- pas de secret simulé.

Mauvaises pratiques :

- skeleton trop animé ;
- layout différent du contenu final ;
- shimmer agressif.

## EmptyState

Rôle :

EmptyState explique une absence de contenu.

Responsabilités :

- expliquer ;
- rassurer ;
- guider ;
- proposer une action si autorisée.

Bonnes pratiques :

- message précis ;
- action claire ;
- distinction vide réel et filtre ;
- aucune fuite sur ressources non autorisées.

Mauvaises pratiques :

- "No data" seul ;
- action non autorisée ;
- ton alarmiste.

# Dialog Components

Les dialogs interrompent l'utilisateur pour une décision ou un formulaire important.

Ils doivent être accessibles, focalisés et proportionnés au risque.

## Dialog

Objectif :

Dialog est le composant de base.

Contenu :

- titre ;
- description optionnelle ;
- contenu principal ;
- actions ;
- bouton fermer si approprié.

Boutons :

- action principale ;
- annulation ;
- action secondaire si nécessaire.

Règles UX :

- focus piégé ;
- fermeture claire ;
- retour focus ;
- pas de contenu trop long ;
- pas d'action sensible implicite.

## ConfirmDialog

Objectif :

ConfirmDialog confirme une action importante.

Contenu :

- ressource concernée ;
- action ;
- conséquence ;
- niveau de risque ;
- message court.

Boutons :

- confirmer ;
- annuler.

Règles UX :

- confirmation explicite ;
- action principale adaptée au risque ;
- aucune ambiguïté.

## DeleteDialog

Objectif :

DeleteDialog confirme une suppression ou suppression logique.

Contenu :

- nom de la ressource ;
- type de suppression ;
- réversibilité ;
- impact ;
- avertissement.

Boutons :

- DangerButton ;
- annuler.

Règles UX :

- distinguer delete, archive et revoke ;
- demander confirmation forte si impact élevé ;
- ne pas utiliser pour archiver si ArchiveDialog existe.

## ArchiveDialog

Objectif :

ArchiveDialog confirme l'archivage d'une ressource.

Contenu :

- ressource ;
- conséquence ;
- effet sur actions futures ;
- indication de réversibilité si disponible.

Boutons :

- confirmer archive ;
- annuler.

Règles UX :

- Archived n'est pas Deleted ;
- expliquer les restrictions ;
- feedback après succès.

## RevealDialog

Objectif :

RevealDialog encadre la révélation d'une valeur secrète.

Contenu :

- secret concerné ;
- contexte vault/project ;
- indication que l'action peut être auditée ;
- valeur masquée puis révélée après succès ;
- action copy.

Boutons :

- reveal ;
- copy après reveal ;
- fermer.

Règles UX :

- valeur masquée par défaut ;
- reveal volontaire ;
- nettoyage à la fermeture ;
- pas de valeur dans toast ;
- gestion permission refusée.

## ApiKeyDialog

Objectif :

ApiKeyDialog gère création et affichage initial d'une API key.

Contenu :

- formulaire de création ;
- rôle ou permissions ;
- scope ;
- expiration si disponible ;
- valeur générée après succès ;
- avertissement d'affichage unique.

Boutons :

- créer ;
- copier ;
- fermer ;
- annuler.

Règles UX :

- afficher la valeur une seule fois ;
- empêcher fermeture accidentelle sans avertissement si valeur non copiée ;
- nettoyer la valeur après fermeture ;
- aucun stockage.

# RBAC Components

Les RBAC Components rendent les rôles, permissions et assignments compréhensibles.

Ils ne prennent jamais de décision d'autorisation définitive. Ils affichent les informations et déclenchent des actions que le backend valide.

## RoleCard

Rôle :

RoleCard résume un rôle.

Responsabilités :

- afficher nom ;
- description ;
- type ;
- nombre de permissions ;
- nombre d'assignments ;
- badges ;
- actions.

Bonnes pratiques :

- indiquer rôle système ;
- signaler permissions critiques ;
- actions claires.

Mauvaises pratiques :

- masquer les permissions sensibles ;
- suggérer une autorisation non confirmée ;
- modifier rôle sans confirmation.

## PermissionMatrix

Rôle :

PermissionMatrix présente des permissions par ressource ou groupe.

Responsabilités :

- organiser permissions ;
- distinguer metadata et value ;
- signaler actions sensibles ;
- supporter lecture et modification si autorisée.

Bonnes pratiques :

- groupement clair ;
- labels compréhensibles ;
- indication des permissions critiques ;
- accessibilité clavier.

Mauvaises pratiques :

- matrice trop dense ;
- cases ambiguës ;
- couleur seule ;
- modification directe sans confirmation.

## AssignmentList

Rôle :

AssignmentList affiche les affectations de rôles.

Responsabilités :

- acteur ;
- rôle ;
- scope ;
- date ;
- attribué par ;
- actions.

Bonnes pratiques :

- scope explicite ;
- rôle visible ;
- retrait confirmé ;
- filtres si nombreux.

Mauvaises pratiques :

- cacher le scope ;
- retirer sans confirmation ;
- mélanger utilisateurs et service accounts sans distinction.

# Audit Components

Les Audit Components servent à analyser les événements.

Ils doivent être denses, sûrs et orientés enquête.

## AuditTable

Rôle :

AuditTable affiche les événements sous forme tabulaire.

Responsabilités :

- date ;
- acteur ;
- action ;
- ressource ;
- résultat ;
- sensibilité ;
- actions ;
- pagination.

Bonnes pratiques :

- ordre chronologique clair ;
- refus visibles ;
- actions sensibles identifiées ;
- aucun secret.

Mauvaises pratiques :

- payload brut ;
- valeurs secrètes ;
- dates ambiguës ;
- colonnes inutiles.

## AuditTimeline

Rôle :

AuditTimeline affiche une séquence d'événements dans un contexte donné.

Usages :

- Secret Details ;
- Vault Details ;
- Project Details ;
- API Key future.

Bonnes pratiques :

- événements récents ;
- lien vers détail ;
- libellés humains ;
- statuts visibles.

Mauvaises pratiques :

- timeline trop longue ;
- masquer les refus ;
- utiliser comme remplacement de AuditTable pour enquête complète.

## AuditDetails

Rôle :

AuditDetails affiche le détail d'un événement.

Responsabilités :

- acteur ;
- action ;
- ressource ;
- résultat ;
- date ;
- contexte ;
- metadata sûre ;
- liens vers ressources.

Bonnes pratiques :

- structurer clairement ;
- aucun secret ;
- messages sûrs ;
- liens soumis aux permissions.

Mauvaises pratiques :

- afficher payload complet ;
- stack trace ;
- token ;
- donnée interne dangereuse.

# Dashboard Components

Les Dashboard Components synthétisent l'état de l'instance.

Ils doivent être utiles, pas décoratifs.

## StatCard

Rôle :

StatCard affiche une statistique clé.

Responsabilités :

- label ;
- valeur ;
- tendance si disponible ;
- statut ;
- lien vers détail.

Bonnes pratiques :

- valeur lisible ;
- label court ;
- contexte clair ;
- pas de métrique vanity.

Mauvaises pratiques :

- valeur sans signification ;
- couleur seule ;
- trop de StatCards.

## RecentActivity

Rôle :

RecentActivity affiche les événements récents.

Responsabilités :

- action ;
- acteur ;
- ressource ;
- date ;
- résultat ;
- lien audit.

Bonnes pratiques :

- événements sensibles visibles ;
- ordre récent ;
- aucune valeur secrète.

Mauvaises pratiques :

- masquer les refus ;
- afficher trop d'événements ;
- confondre activité et audit complet.

## QuickActions

Rôle :

QuickActions affiche des raccourcis vers les actions fréquentes.

Responsabilités :

- créer vault ;
- créer secret ;
- créer API key ;
- consulter audit ;
- accéder settings.

Bonnes pratiques :

- respecter permissions ;
- actions limitées ;
- labels clairs.

Mauvaises pratiques :

- action non autorisée sans explication ;
- actions dangereuses rapides sans confirmation ;
- trop d'actions.

## SecuritySummary

Rôle :

SecuritySummary présente les signaux de sécurité importants.

Responsabilités :

- API keys révoquées ou expirées ;
- vaults locked ;
- refus récents ;
- secrets sans version ;
- attention future.

Bonnes pratiques :

- prioriser les signaux ;
- lien vers résolution ;
- ton calme.

Mauvaises pratiques :

- alarmer sans action ;
- afficher informations non autorisées ;
- mélanger sécurité et promotion produit.

# Loading Components

Les Loading Components indiquent une attente sans casser la structure.

## Skeleton variants

Rôle :

Les variantes de Skeleton correspondent aux structures principales.

Variantes :

- table skeleton ;
- card skeleton ;
- detail skeleton ;
- form skeleton ;
- dashboard skeleton ;
- timeline skeleton.

Bonnes pratiques :

- imiter la structure réelle ;
- rester sobre ;
- éviter les animations agressives.

Mauvaises pratiques :

- skeleton générique partout ;
- tailles instables ;
- simuler des données sensibles.

## LoadingOverlay

Rôle :

LoadingOverlay bloque temporairement une zone pendant une action.

Usages :

- mutation de formulaire ;
- chargement de dialog ;
- opération non annulable courte.

Bonnes pratiques :

- utiliser avec parcimonie ;
- message clair ;
- ne pas bloquer toute application sans nécessité.

Mauvaises pratiques :

- masquer une erreur ;
- empêcher lecture de contexte ;
- overlay permanent.

## InlineLoading

Rôle :

InlineLoading indique un chargement local.

Usages :

- bouton ;
- ligne ;
- petite zone ;
- filtre.

Bonnes pratiques :

- proche de l'action ;
- discret ;
- accessible.

Mauvaises pratiques :

- spinner sans contexte ;
- trop d'indicateurs simultanés.

# Error Components

Les Error Components doivent être sûrs, utiles et cohérents.

Ils ne doivent jamais afficher d'information sensible.

## ErrorState

Rôle :

ErrorState affiche une erreur générale.

Responsabilités :

- expliquer ;
- proposer retry ;
- fournir action de retour ;
- rester sûr.

Bonnes pratiques :

- message clair ;
- action utile ;
- ton calme.

Mauvaises pratiques :

- stack trace ;
- payload brut ;
- message technique incompréhensible.

## ForbiddenState

Rôle :

ForbiddenState affiche un refus d'accès.

Responsabilités :

- indiquer permission insuffisante ;
- éviter fuite de ressource ;
- proposer retour ;
- suggérer contact admin si pertinent.

Bonnes pratiques :

- message neutre ;
- aucune donnée interdite ;
- action de navigation.

Mauvaises pratiques :

- révéler détails de permission internes non autorisés ;
- accuser l'utilisateur ;
- proposer une action impossible.

## NotFoundState

Rôle :

NotFoundState affiche une ressource introuvable.

Responsabilités :

- indiquer absence ou indisponibilité ;
- proposer retour ;
- rester prudent sur les causes.

Bonnes pratiques :

- message simple ;
- lien vers liste parent ;
- pas de détails internes.

Mauvaises pratiques :

- révéler qu'une ressource existe mais est cachée ;
- afficher identifiants sensibles.

## RetryBlock

Rôle :

RetryBlock permet de relancer un chargement échoué.

Responsabilités :

- afficher erreur courte ;
- bouton retry ;
- état loading ;
- accessibilité.

Bonnes pratiques :

- utiliser pour erreurs réseau ;
- garder contexte ;
- éviter retry infini automatique.

Mauvaises pratiques :

- retry sur mutation sensible non idempotente ;
- masquer l'échec ;
- relancer sans feedback.

# Responsive Behavior

Tous les composants doivent être conçus pour s'adapter aux tailles d'écran principales.

La priorité est l'utilisabilité et la sécurité, pas la reproduction identique du desktop.

## Desktop

Comportement attendu :

- Sidebar visible ;
- Topbar complète ;
- tables complètes ;
- filtres visibles ;
- dialogs centrés ;
- cards en grille ;
- sections côte à côte lorsque utile ;
- actions principales visibles.

Les composants doivent utiliser l'espace pour améliorer la lecture et la comparaison.

## Laptop

Comportement attendu :

- même structure que desktop ;
- colonnes secondaires potentiellement masquées ;
- grilles plus compactes ;
- actions conservées ;
- hauteur disponible optimisée.

Les composants doivent éviter les zones trop hautes qui repoussent le contenu important.

## Tablet

Comportement attendu :

- Sidebar repliable ;
- filtres en panneau ;
- tables simplifiées ;
- cards empilées ou en deux colonnes ;
- dialogs adaptés ;
- actions regroupées.

Les composants doivent rester confortables au tactile.

## Mobile

Comportement attendu :

- navigation en drawer ;
- listes structurées au lieu de tables complexes ;
- actions dans menus ;
- boutons suffisamment grands ;
- dialogs plein écran si nécessaire ;
- contexte visible ;
- aucun affichage de valeur secrète par défaut.

Les actions sensibles doivent rester plus difficiles à déclencher par erreur, même sur petit écran.

# Accessibility Rules

Tous les composants doivent respecter des règles communes d'accessibilité.

## Clavier

Règles :

- chaque composant interactif est accessible au clavier ;
- ordre de tabulation logique ;
- menus, tabs, dialogs et tables interactives supportent les interactions clavier attendues ;
- aucun piège clavier ;
- raccourcis futurs documentés et non obligatoires.

## Focus

Règles :

- focus visible ;
- focus restauré après fermeture de dialog ;
- focus déplacé vers contenu important lorsque nécessaire ;
- focus non supprimé pour raison esthétique ;
- état focus différencié de hover.

## ARIA

Règles :

- utiliser ARIA lorsque la sémantique native ne suffit pas ;
- nom accessible obligatoire pour IconButton ;
- dialogs nommés ;
- erreurs reliées aux champs ;
- loading annoncé lorsque pertinent ;
- statuts importants compréhensibles.

## Lecteurs d'écran

Règles :

- labels explicites ;
- titres structurés ;
- tables avec en-têtes ;
- badges compréhensibles par texte ;
- actions dangereuses nommées ;
- valeurs secrètes masquées non révélées involontairement.

## Contrastes

Règles :

- texte lisible ;
- focus visible ;
- badges contrastés ;
- erreurs et warnings accessibles ;
- dark mode de première classe ;
- couleur jamais seule information.

# Component Principles

Les règles suivantes guident toute création ou modification de composant.

- Un composant a une responsabilité principale.
- La composition est préférée à la spécialisation prématurée.
- Les composants partagés restent génériques.
- Aucun composant métier ne doit vivre dans un espace shared générique sans justification.
- Aucun composant ne contient de logique de permission métier définitive.
- Les composants peuvent afficher un état autorisé ou refusé retourné par le backend.
- Les composants sensibles ne révèlent jamais une valeur par défaut.
- Les composants sensibles ne stockent jamais inutilement une valeur.
- Les composants de table n'affichent jamais de valeur secrète.
- Les dialogs sensibles nomment toujours la ressource concernée.
- Les boutons dangereux sont visuellement identifiables.
- Les composants doivent gérer loading, disabled, error et empty lorsque leur rôle l'exige.
- Les composants interactifs doivent être accessibles au clavier.
- Les IconButtons ont toujours un nom accessible.
- Les badges ne reposent jamais uniquement sur la couleur.
- Les composants doivent fonctionner en light mode et dark mode.
- Les composants doivent être testables.
- Les composants ne doivent pas importer directement des détails internes de features sans contrat clair.
- Les composants ne doivent pas appeler l'API s'ils sont purement présentationnels.
- Les composants connectés aux données doivent rester dans les features ou containers dédiés.
- Les composants doivent éviter les abstractions trop larges.
- Les variantes doivent être limitées et documentées.
- Une incohérence visuelle doit être corrigée dans le composant partagé, pas contournée écran par écran.
- La réutilisation ne doit pas forcer un mauvais usage. Si un composant ne convient pas, il faut le faire évoluer ou créer un composant adapté.

# Conclusion

La Component Library de MCP Secret Manager est un socle de cohérence, de sécurité et de maintenabilité.

Elle permet de construire une application SaaS premium sans réinventer les mêmes patterns à chaque écran. Elle garantit que les layouts, navigations, formulaires, boutons, tables, badges, dialogs, états de chargement, erreurs, composants secrets, composants RBAC, composants audit et composants dashboard partagent les mêmes règles.

Dans un Secret Manager, un composant n'est jamais neutre. Un mauvais badge peut rendre un statut ambigu. Un mauvais bouton peut banaliser une action dangereuse. Un mauvais champ peut exposer une valeur. Un mauvais dialog peut laisser croire qu'une révocation est réversible. La bibliothèque de composants existe pour éviter ces dérives.

La philosophie est simple : composants sobres, accessibles, composables, testables et sûrs. Réutiliser lorsque le pattern existe. Créer seulement lorsque le besoin est réel. Garder les composants partagés génériques. Garder les composants métier dans leur domaine. Ne jamais faire porter au frontend une décision de sécurité qui appartient au backend.

Cette bibliothèque doit accompagner toute l'implémentation React de MCP Secret Manager et rester alignée avec la vision produit, l'architecture frontend, le Design System et la spécification UI.
