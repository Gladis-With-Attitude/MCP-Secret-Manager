# Objectif du document

Ce document définit la spécification fonctionnelle complète des interfaces utilisateur du frontend de MCP Secret Manager.

Il décrit chaque écran du produit, son objectif, ses utilisateurs, les informations affichées, les composants attendus, les API consommées, les permissions nécessaires, les actions possibles, les états de chargement, les états vides, les états d'erreur, le comportement responsive et les remarques UX importantes.

Ce document sert de référence pendant toute l'implémentation React. Il doit permettre à l'équipe produit, UX, frontend, backend et QA de partager une compréhension commune de ce qui doit être construit.

Il ne définit pas de code, pas de pseudo-code, pas de classes CSS, pas de wireframes et pas de choix d'implémentation détaillés. Il décrit le comportement attendu de l'application et la structure fonctionnelle des écrans.

Le frontend de MCP Secret Manager est une console SaaS d'administration pour un produit de sécurité. Chaque écran doit donc respecter trois contraintes fondamentales :

- rendre l'information lisible et actionnable ;
- éviter toute exposition inutile de donnée sensible ;
- respecter les décisions du backend concernant l'authentification, les permissions, l'audit et les états métier.

Les permissions indiquées dans ce document expriment l'intention fonctionnelle. Le backend reste toujours l'autorité finale. Le frontend peut masquer, désactiver ou contextualiser des actions selon les informations reçues, mais il ne doit jamais considérer cette logique comme une protection suffisante.

# Login

## Objectif

L'écran Login permet à un utilisateur humain de s'authentifier pour accéder à la console d'administration de MCP Secret Manager.

Il doit être simple, rassurant et sécurisé. Il doit permettre de comprendre immédiatement que l'utilisateur entre dans une application sensible, sans ajouter de friction inutile.

Cet écran doit aussi gérer les situations courantes :

- première connexion ;
- erreur d'identifiants ;
- session expirée ;
- indisponibilité temporaire du backend ;
- compte non autorisé ;
- tentative d'accès à une route protégée sans session.

Le login ne doit jamais exposer d'information sur l'existence d'utilisateurs, de vaults, de secrets ou de configuration interne.

## Utilisateur

Utilisateurs concernés :

- administrateur ;
- développeur ;
- membre DevOps ;
- membre d'équipe IA ;
- membre d'une PME ou entreprise ;
- futur utilisateur invité ou membre d'organisation.

L'écran doit convenir à un utilisateur technique, mais ne doit pas supposer qu'il connaît la structure interne du produit.

## Informations affichées

Informations principales :

- nom du produit ;
- indication qu'il s'agit de la console d'administration ;
- formulaire d'authentification ;
- message de sécurité bref et non anxiogène ;
- état de session expirée si applicable ;
- erreurs de connexion ;
- lien ou information de support si prévu ;
- indication de chargement pendant la connexion.

Champs attendus selon le backend MVP :

- identifiant, email ou username selon le modèle d'authentification retenu ;
- mot de passe si authentification par credentials ;
- éventuel champ de code MFA futur si activé ;
- bouton de connexion.

Informations à ne pas afficher :

- détails internes de configuration ;
- liste d'utilisateurs ;
- état des vaults ;
- version détaillée du backend si non nécessaire ;
- secrets ;
- tokens ;
- stack traces.

## Composants utilisés

Composants attendus :

- layout public ;
- logo ou marque produit ;
- formulaire ;
- champ texte ;
- champ mot de passe ;
- bouton Primary ;
- alerte d'erreur ;
- alerte d'information pour session expirée ;
- message de chargement ;
- éventuellement lien d'aide ;
- gestion du focus ;
- zone de feedback accessible.

Le formulaire doit être accessible au clavier. Les erreurs doivent être associées aux champs concernés lorsque possible.

## API utilisées

API consommées conceptuellement :

- authentification utilisateur ;
- création ou validation de session ;
- récupération minimale du profil connecté après connexion ;
- refresh de session si le backend le permet ;
- logout implicite ou nettoyage si une session invalide est détectée.

Le frontend ne doit pas gérer directement de secret de session exposé à JavaScript si une stratégie par cookies sécurisés est disponible.

## Permissions nécessaires

Aucune permission métier n'est nécessaire pour afficher l'écran Login.

Après connexion, le backend détermine :

- si l'utilisateur est authentifié ;
- si la session est valide ;
- quelles ressources seront accessibles ;
- quelles actions seront autorisées.

Le frontend ne doit pas accorder d'accès à l'application sur la base d'une réponse ambiguë.

## Actions disponibles

Actions principales :

- saisir les identifiants ;
- soumettre le formulaire ;
- afficher ou masquer le mot de passe si cette option est retenue ;
- revenir à une page publique si elle existe ;
- réessayer après erreur.

Actions futures possibles :

- demander une récupération de compte ;
- utiliser SSO ;
- saisir un second facteur ;
- sélectionner une organisation après connexion.

Le bouton de connexion doit être désactivé pendant la soumission pour éviter les doubles tentatives.

## États de chargement

États attendus :

- chargement initial de la page ;
- soumission en cours ;
- validation de session en cours ;
- redirection après succès.

Pendant la soumission :

- le bouton principal indique l'action en cours ;
- les champs peuvent rester visibles ;
- l'utilisateur ne doit pas croire que la connexion est terminée ;
- les doubles soumissions doivent être empêchées.

## États vides

L'écran Login n'a pas d'état vide classique.

Cas spécifique :

- si l'application ne possède pas encore de configuration d'authentification, afficher un message générique et sûr ;
- si l'instance nécessite une initialisation administrateur future, afficher une indication sans exposer de détails sensibles.

Le MVP peut ne pas inclure d'écran d'initialisation. Dans ce cas, l'écran Login reste centré sur l'authentification.

## États d'erreur

Erreurs à gérer :

- identifiants invalides ;
- champ requis manquant ;
- session expirée ;
- compte non autorisé ;
- backend indisponible ;
- erreur réseau ;
- trop de tentatives futures ;
- erreur inattendue.

Principes :

- ne pas indiquer si l'email ou username existe ;
- ne pas afficher de stack trace ;
- ne pas afficher de token ;
- ne pas exposer la politique interne d'authentification ;
- proposer une action utile lorsque possible.

Pour une session expirée, le message doit être clair : l'utilisateur doit se reconnecter pour continuer. Il ne doit pas être présenté comme une erreur critique.

## Responsive

Desktop :

- formulaire centré ou aligné dans une composition sobre ;
- largeur confortable ;
- message de sécurité visible ;
- aucun élément décoratif envahissant.

Laptop :

- mêmes priorités que desktop ;
- attention à la hauteur disponible.

Tablet :

- formulaire lisible ;
- champs suffisamment grands ;
- focus et clavier virtuel bien gérés.

Mobile :

- formulaire plein largeur avec marges confortables ;
- boutons faciles à toucher ;
- messages d'erreur visibles sans scroll excessif ;
- pas de contenu secondaire au-dessus du formulaire qui retarde l'action.

## Notes UX

Le Login doit être calme et direct.

Le produit manipule des secrets, mais l'écran ne doit pas être anxiogène. La sécurité doit être suggérée par la sobriété, la précision des messages, la qualité du formulaire et l'absence de bruit visuel.

Les erreurs doivent être utiles mais prudentes. Un message comme "Identifiants invalides" est préférable à une explication détaillée qui pourrait aider un attaquant.

Si l'utilisateur arrive depuis une route protégée, après connexion réussie il peut être redirigé vers la destination initiale, à condition que cette destination soit sûre et toujours autorisée par le backend.

# Dashboard

## Objectif

Le Dashboard fournit une vue d'ensemble opérationnelle de MCP Secret Manager.

Il doit permettre à l'utilisateur de comprendre rapidement l'état de son instance :

- ressources principales ;
- activité récente ;
- actions sensibles récentes ;
- API keys actives ;
- vaults et projets ;
- indicateurs de sécurité ;
- raccourcis vers les tâches courantes.

Le Dashboard n'est pas une page marketing. C'est une surface de travail. Il doit aider l'utilisateur à décider quoi faire ensuite.

## Utilisateur

Utilisateurs concernés :

- administrateur ;
- DevOps ;
- développeur ;
- équipe IA ;
- responsable technique ;
- utilisateur Enterprise futur.

Le Dashboard doit rester utile à la fois pour une instance fraîche et pour une instance contenant de nombreuses ressources.

## Informations affichées

Widgets attendus :

- nombre total de vaults ;
- nombre total de projects ;
- nombre total de secrets ;
- nombre total d'API keys actives ;
- nombre d'API keys révoquées ou expirées si disponible ;
- nombre d'événements d'audit récents ;
- derniers accès sensibles ;
- derniers refus d'autorisation ;
- derniers secrets modifiés ;
- ressources nécessitant attention.

Statistiques :

- ressources actives ;
- ressources archivées ;
- vaults verrouillés si disponibles ;
- activité sur une période récente ;
- tendance simple si backend la fournit.

Activité récente :

- acteur ;
- action ;
- ressource ;
- date ;
- résultat ;
- lien vers le détail d'audit ;
- indication visuelle pour actions sensibles.

Actions rapides :

- créer un vault ;
- créer un project depuis un contexte si possible ;
- créer un secret ;
- créer une API key ;
- consulter les audit logs ;
- accéder aux settings.

Cartes :

- cartes de statistiques ;
- carte d'activité récente ;
- carte de raccourcis ;
- carte d'attention sécurité ;
- états vides guidés.

Indicateurs :

- succès ;
- warning ;
- danger ;
- locked ;
- revoked ;
- archived ;
- informations neutres.

## Composants utilisés

Composants attendus :

- layout authentifié ;
- topbar ;
- sidebar ;
- breadcrumb minimal ou titre de page ;
- cartes de statistiques ;
- table ou liste d'activité récente ;
- badges d'état ;
- boutons d'action rapide ;
- empty state ;
- skeletons ;
- alertes ;
- liens contextuels.

Le Dashboard peut utiliser des cartes, car il présente des synthèses. Les listes d'activité doivent rester structurées et scannables.

## API utilisées

API consommées conceptuellement :

- résumé dashboard ou agrégations ;
- liste récente d'audit logs ;
- compte des vaults ;
- compte des projects ;
- compte des secrets ;
- compte des API keys ;
- informations de session ;
- informations de permissions disponibles pour actions rapides.

Si le backend ne fournit pas d'endpoint agrégé au MVP, le frontend peut consommer plusieurs endpoints de lecture, mais cette orchestration doit rester dans la feature dashboard et ne pas dupliquer la logique métier.

## Permissions nécessaires

Permissions typiques :

- lecture dashboard ou lecture des ressources agrégées ;
- lecture vault metadata ;
- lecture project metadata ;
- lecture secret metadata ;
- lecture API key metadata ;
- lecture audit logs pour l'activité récente ;
- permissions de création pour afficher certaines actions rapides.

Si l'utilisateur ne possède pas une permission, le widget correspondant peut être masqué, remplacé par un état limité ou afficher une information non sensible.

Le Dashboard ne doit jamais afficher une donnée que le backend ne permet pas de consulter.

## Actions disponibles

Actions principales :

- naviguer vers Vault List ;
- naviguer vers Project List ;
- naviguer vers Secret List ;
- naviguer vers API Keys ;
- naviguer vers Audit Logs ;
- créer un vault si autorisé ;
- créer une API key si autorisé ;
- ouvrir le détail d'un événement récent ;
- ouvrir une ressource depuis l'activité récente.

Actions secondaires :

- rafraîchir les données ;
- modifier la période d'activité si supportée ;
- ajuster un filtre simple ;
- accéder aux settings.

## États de chargement

États attendus :

- skeletons pour cartes de statistiques ;
- skeleton pour activité récente ;
- chargement progressif par widget ;
- état de refresh discret ;
- chargement des actions rapides si permissions en cours de résolution.

Le Dashboard ne doit pas attendre que toutes les données soient disponibles pour afficher ce qui peut déjà l'être, sauf si cela crée une incohérence.

## États vides

Cas d'instance fraîche :

- aucun vault ;
- aucun project ;
- aucun secret ;
- aucune API key ;
- aucun audit log significatif.

L'état vide doit :

- expliquer que l'instance est prête ;
- proposer de créer le premier vault ;
- guider ensuite vers la création d'un project et d'un secret ;
- rester rassurant.

Cas de permissions limitées :

- afficher une vue restreinte ;
- expliquer que certaines informations ne sont pas disponibles ;
- ne pas révéler l'existence de ressources non autorisées.

## États d'erreur

Erreurs à gérer :

- échec de chargement d'un widget ;
- échec de chargement global ;
- session expirée ;
- accès refusé à certaines agrégations ;
- backend indisponible ;
- erreur réseau.

Un widget en erreur ne doit pas nécessairement casser tout le Dashboard. Si possible, afficher les autres widgets et isoler l'erreur.

## Responsive

Desktop :

- grille de statistiques ;
- activité récente visible ;
- actions rapides latérales ou en haut ;
- navigation complète.

Laptop :

- grille adaptée ;
- priorité aux métriques et activité récente ;
- éviter les cartes trop hautes.

Tablet :

- cartes en deux colonnes ou pile ;
- activité récente simplifiée ;
- actions rapides groupées.

Mobile :

- cartes empilées ;
- priorité au statut global et actions critiques ;
- activité récente en liste compacte ;
- navigation mobile accessible.

## Notes UX

Le Dashboard doit être utile dès la première visite.

Il doit éviter les graphiques décoratifs sans valeur. Les statistiques doivent être directement liées aux décisions utilisateur.

Les actions rapides doivent tenir compte des permissions. Une action non autorisée ne doit pas apparaître comme disponible.

L'activité récente ne doit jamais inclure de valeur secrète. Elle doit afficher uniquement des métadonnées sûres.

# Vault List

## Objectif

Vault List permet de consulter, rechercher, filtrer, trier et administrer les vaults.

Un vault est une frontière logique et de sécurité. Cette liste doit aider l'utilisateur à comprendre l'organisation générale de l'instance et à accéder rapidement au bon vault.

## Utilisateur

Utilisateurs concernés :

- administrateur ;
- DevOps ;
- développeur ;
- équipe IA ;
- responsable sécurité ;
- utilisateur avec accès limité à certains vaults.

Chaque utilisateur ne voit que les vaults que le backend l'autorise à consulter.

## Informations affichées

Liste et colonnes attendues :

- nom du vault ;
- description courte si disponible ;
- statut ;
- nombre de projects ;
- nombre de secrets ou résumé si disponible ;
- date de création ;
- date de mise à jour ;
- propriétaire ou acteur créateur si disponible ;
- indicateur locked ;
- indicateur archived ;
- actions.

Recherche :

- recherche par nom ;
- recherche par description ou métadonnées si supportée ;
- état sans résultat.

Filtres :

- statut actif ;
- archived ;
- locked ;
- date de création ;
- propriétaire ou acteur si disponible.

Tri :

- nom ;
- date de création ;
- date de mise à jour ;
- nombre de projects ;
- statut.

Pagination :

- pagination standard si volume important ;
- conservation des filtres et recherche ;
- indication de la page ou du nombre de résultats si disponible.

Création :

- bouton créer un vault ;
- dialog ou page dédiée selon complexité ;
- champs minimum : nom, description optionnelle, métadonnées éventuelles.

Suppression et archivage :

- archivage privilégié au MVP si le backend le supporte ;
- suppression définitive hors périmètre ou fortement restreinte ;
- confirmation obligatoire ;
- distinction claire entre archiver et supprimer.

## Composants utilisés

Composants attendus :

- page header ;
- bouton Primary de création ;
- table ;
- recherche ;
- filtres ;
- tri ;
- pagination ;
- badges de statut ;
- menu d'actions ;
- dialog de création ;
- dialog de confirmation d'archivage ;
- alertes d'erreur ;
- skeleton de table ;
- empty state.

## API utilisées

API consommées conceptuellement :

- lister les vaults ;
- rechercher ou filtrer les vaults ;
- créer un vault ;
- lire les métadonnées d'un vault ;
- archiver un vault ;
- verrouiller un vault si disponible ;
- supprimer logiquement si supporté ;
- récupérer les permissions applicables.

## Permissions nécessaires

Permissions typiques :

- lecture vault metadata pour voir la liste ;
- création vault pour créer ;
- mise à jour vault pour modifier ;
- archivage vault pour archiver ;
- verrouillage vault pour verrouiller ;
- suppression vault si disponible ;
- lecture des compteurs associés si backend les autorise.

Le frontend doit désactiver ou masquer les actions non autorisées selon les informations disponibles, tout en gérant les refus backend.

## Actions disponibles

Actions principales :

- rechercher ;
- filtrer ;
- trier ;
- changer de page ;
- ouvrir un vault ;
- créer un vault.

Actions de ligne :

- ouvrir le détail ;
- modifier les métadonnées ;
- archiver ;
- verrouiller si disponible ;
- restaurer si futur ;
- consulter l'historique ou audit associé ;
- supprimer si supporté et autorisé.

Les actions sensibles doivent passer par confirmation.

## États de chargement

États attendus :

- skeleton de table au chargement initial ;
- indicateur discret lors de changement de filtre ;
- état de chargement sur création ;
- état de chargement sur archivage ;
- désactivation des actions pendant mutation.

Les lignes ne doivent pas disparaître brutalement pendant un refresh sauf changement confirmé.

## États vides

Cas possibles :

- aucun vault créé ;
- aucun vault accessible ;
- aucun résultat après recherche ;
- aucun résultat après filtre.

État vide sans vault :

- expliquer qu'un vault est le premier conteneur de sécurité ;
- proposer de créer un vault si autorisé ;
- indiquer que l'utilisateur doit contacter un administrateur si non autorisé.

État vide filtré :

- indiquer qu'aucun vault ne correspond ;
- proposer de retirer les filtres.

## États d'erreur

Erreurs à gérer :

- impossible de charger les vaults ;
- erreur de création ;
- nom invalide ;
- conflit de nom ;
- accès refusé ;
- erreur d'archivage ;
- erreur de verrouillage ;
- session expirée ;
- backend indisponible.

Les erreurs de mutation doivent rester proches de l'action concernée ou apparaître dans un feedback global clair.

## Responsive

Desktop :

- table complète ;
- filtres visibles ;
- actions de ligne dans menu ou colonne dédiée.

Laptop :

- table complète avec colonnes prioritaires ;
- colonnes secondaires masquables si nécessaire.

Tablet :

- table simplifiée ou liste structurée ;
- filtres dans un panneau ;
- actions dans menu.

Mobile :

- liste de vaults en lignes ou cards compactes ;
- statut visible ;
- recherche prioritaire ;
- filtres dans un drawer ;
- action créer accessible si autorisée.

## Notes UX

Le statut du vault doit être visible dans toutes les représentations.

Un vault locked ne doit pas ressembler à un vault archived. Le locked indique une restriction active. L'archived indique une ressource retirée de l'usage courant.

La suppression définitive, si elle existe un jour, doit être traitée comme une action exceptionnelle et non comme une action standard de liste.

# Vault Details

## Objectif

Vault Details permet de consulter et administrer un vault précis.

L'écran doit donner une vue claire du vault comme frontière de sécurité : informations générales, état, statistiques, projects associés, permissions, actions disponibles et historique pertinent.

## Utilisateur

Utilisateurs concernés :

- administrateur ;
- DevOps ;
- développeur ayant accès au vault ;
- équipe IA ;
- responsable sécurité.

L'utilisateur doit posséder une permission de lecture sur le vault pour accéder à cette vue.

## Informations affichées

Informations principales :

- nom du vault ;
- description ;
- statut ;
- état locked ;
- état archived ;
- date de création ;
- date de mise à jour ;
- propriétaire ou acteur créateur si disponible ;
- identifiant technique si utile ;
- métadonnées non sensibles.

Statistiques :

- nombre de projects ;
- nombre de secrets ;
- nombre d'API keys liées si disponible ;
- activité récente ;
- nombre d'événements d'audit récents ;
- indicateurs de risque ou attention si disponibles.

Projects :

- liste des projects du vault ;
- statut de chaque project ;
- nombre de secrets par project si disponible ;
- date de mise à jour ;
- accès au détail.

Permissions :

- permissions effectives de l'utilisateur sur ce vault si l'API les fournit ;
- rôles associés si disponibles ;
- acteurs ou comptes de service liés si disponible au MVP.

Historique :

- événements récents liés au vault ;
- création ;
- modification ;
- verrouillage ;
- archivage ;
- accès refusés ;
- actions sensibles.

## Composants utilisés

Composants attendus :

- page header avec statut ;
- breadcrumb ;
- badges ;
- panneau d'informations ;
- cartes de statistiques ;
- table ou liste de projects ;
- section permissions ;
- section activité récente ;
- menus d'actions ;
- dialogs de modification ;
- dialogs de confirmation ;
- empty states ;
- skeletons.

## API utilisées

API consommées conceptuellement :

- lire un vault ;
- lister les projects du vault ;
- récupérer les statistiques du vault ;
- récupérer les permissions effectives ;
- récupérer l'activité ou audit lié ;
- modifier les métadonnées ;
- archiver ;
- verrouiller ;
- restaurer futur si disponible.

## Permissions nécessaires

Permissions typiques :

- lecture vault metadata ;
- lecture project metadata pour voir les projects ;
- mise à jour vault pour modifier ;
- archivage vault ;
- verrouillage vault ;
- lecture audit pour historique ;
- lecture RBAC ou permission summary si disponible.

Une absence de permission sur les projects doit être gérée sans révéler d'information non autorisée.

## Actions disponibles

Actions principales :

- modifier le vault ;
- créer un project dans ce vault ;
- consulter les projects ;
- consulter l'audit lié ;
- archiver le vault ;
- verrouiller le vault si disponible.

Actions secondaires :

- copier l'identifiant technique si non sensible ;
- ouvrir les paramètres de permissions ;
- rafraîchir ;
- retourner à la liste.

Actions sensibles :

- archiver ;
- verrouiller ;
- modifier des permissions ;
- supprimer si supporté.

## États de chargement

États attendus :

- skeleton du header ;
- skeleton des statistiques ;
- skeleton de la liste de projects ;
- chargement séparé de l'historique ;
- état de mutation sur actions sensibles.

Si les statistiques échouent mais que le vault charge, la page peut rester visible avec une erreur locale.

## États vides

Cas possibles :

- vault sans project ;
- aucun événement d'audit visible ;
- aucune permission détaillée disponible ;
- aucune statistique disponible.

Vault sans project :

- expliquer qu'un project organise les secrets dans un vault ;
- proposer de créer un project si autorisé ;
- sinon indiquer que l'utilisateur n'a pas l'autorisation de création.

## États d'erreur

Erreurs à gérer :

- vault introuvable ;
- accès refusé ;
- vault archivé ou locked avec actions limitées ;
- chargement des projects échoué ;
- chargement audit échoué ;
- modification échouée ;
- archivage échoué ;
- session expirée.

Une ressource introuvable et un accès refusé doivent être présentés selon les informations sûres fournies par le backend.

## Responsive

Desktop :

- header complet ;
- statistiques en grille ;
- projects en table ;
- panneau d'activité ou permissions visible.

Laptop :

- mêmes sections avec densité ajustée ;
- colonnes secondaires réduites.

Tablet :

- sections empilées ;
- projects en liste structurée si nécessaire ;
- actions dans menu.

Mobile :

- header compact ;
- statut très visible ;
- actions principales accessibles ;
- projects en liste ;
- historique en liste compacte.

## Notes UX

Le contexte vault doit rester visible lorsqu'on navigue vers ses projects ou secrets.

Les actions sur un vault ont un impact large. Les confirmations doivent rappeler que les projects et secrets associés peuvent être affectés selon les règles backend.

# Project List

## Objectif

Project List permet de consulter et administrer les projects accessibles à l'utilisateur.

La vue peut exister globalement ou dans le contexte d'un vault. Elle doit aider à organiser les secrets par application, service, environnement, équipe ou usage.

## Utilisateur

Utilisateurs concernés :

- développeur ;
- DevOps ;
- équipe IA ;
- administrateur ;
- responsable technique.

L'utilisateur peut voir uniquement les projects autorisés par le backend.

## Informations affichées

Colonnes attendues :

- nom du project ;
- vault parent ;
- description ;
- statut ;
- nombre de secrets ;
- date de création ;
- date de mise à jour ;
- propriétaire ou acteur si disponible ;
- actions.

Recherche :

- nom ;
- description ;
- vault parent si vue globale ;
- métadonnées si supportées.

Filtres :

- vault ;
- statut ;
- archived ;
- date ;
- propriétaire si disponible.

Tri :

- nom ;
- vault ;
- date de création ;
- date de mise à jour ;
- nombre de secrets ;
- statut.

Pagination :

- standard si volume élevé ;
- filtres conservés.

Création :

- création depuis liste globale avec choix du vault ;
- création depuis Vault Details avec vault prérempli ;
- description optionnelle ;
- validation de nom.

Suppression et archivage :

- archivage privilégié ;
- suppression définitive hors MVP sauf décision backend contraire ;
- confirmation obligatoire.

## Composants utilisés

Composants attendus :

- page header ;
- table ;
- recherche ;
- filtres ;
- tri ;
- pagination ;
- badge de statut ;
- badge de vault ;
- bouton créer ;
- dialog ou page de création ;
- dialog d'archivage ;
- empty state ;
- skeleton.

## API utilisées

API consommées conceptuellement :

- lister les projects ;
- lister les projects d'un vault ;
- créer un project ;
- lire un project ;
- modifier les métadonnées ;
- archiver un project ;
- récupérer les vaults accessibles pour création ;
- récupérer les permissions applicables.

## Permissions nécessaires

Permissions typiques :

- lecture project metadata ;
- lecture vault metadata pour afficher le vault parent ;
- création project ;
- mise à jour project ;
- archivage project ;
- lecture compteur secrets si autorisée.

La création d'un project nécessite aussi une permission valide dans le vault cible.

## Actions disponibles

Actions principales :

- rechercher ;
- filtrer ;
- trier ;
- ouvrir un project ;
- créer un project.

Actions de ligne :

- ouvrir ;
- modifier ;
- archiver ;
- consulter les secrets ;
- consulter l'audit lié ;
- supprimer si supporté.

Les actions sensibles doivent être confirmées.

## États de chargement

États attendus :

- skeleton de table ;
- chargement de filtres vault ;
- chargement de création ;
- chargement d'archivage ;
- refresh après mutation.

## États vides

Cas possibles :

- aucun project ;
- aucun project dans un vault ;
- aucun résultat filtré ;
- aucun project accessible.

État vide :

- expliquer qu'un project organise les secrets ;
- proposer de créer un project si autorisé ;
- proposer de changer de vault ou filtre si pertinent.

## États d'erreur

Erreurs à gérer :

- impossible de charger les projects ;
- vault parent inaccessible ;
- création refusée ;
- nom invalide ;
- conflit ;
- archivage refusé ;
- session expirée ;
- backend indisponible.

## Responsive

Desktop :

- table globale avec colonnes principales ;
- filtres visibles ;
- actions de ligne.

Laptop :

- colonnes secondaires réduites si besoin.

Tablet :

- vue liste structurée possible ;
- filtres dans panneau.

Mobile :

- liste compacte ;
- vault parent visible ;
- statut visible ;
- action créer accessible.

## Notes UX

La relation project-vault doit être toujours claire, surtout dans la liste globale.

Créer un project sans comprendre son vault parent peut entraîner une mauvaise organisation des secrets. Le formulaire doit rendre ce choix explicite.

# Project Details

## Objectif

Project Details permet de consulter et administrer un project précis.

L'écran doit mettre en avant le contexte du project, ses secrets, ses statistiques, ses permissions et son activité récente.

## Utilisateur

Utilisateurs concernés :

- développeur ;
- DevOps ;
- équipe IA ;
- administrateur ;
- responsable sécurité.

## Informations affichées

Informations principales :

- nom du project ;
- vault parent ;
- description ;
- statut ;
- date de création ;
- date de mise à jour ;
- identifiant technique si utile ;
- métadonnées non sensibles.

Statistiques :

- nombre de secrets ;
- nombre de versions si disponible ;
- activité récente ;
- API keys liées si disponible ;
- derniers changements.

Secrets :

- liste des secrets du project ;
- nom ;
- description ;
- statut ;
- version courante ;
- date de dernière modification ;
- badges ;
- actions.

Permissions :

- permissions effectives sur le project si fournies ;
- rôles ou acteurs associés si disponibles ;
- indication des actions autorisées.

Historique :

- événements liés au project ;
- créations ;
- modifications ;
- archivages ;
- accès à des secrets du project si disponible ;
- refus d'autorisation.

## Composants utilisés

Composants attendus :

- page header ;
- breadcrumb avec vault ;
- badges ;
- cartes de statistiques ;
- table de secrets ;
- actions rapides ;
- section permissions ;
- section activité ;
- dialog de modification ;
- dialog d'archivage ;
- empty state ;
- skeletons.

## API utilisées

API consommées conceptuellement :

- lire un project ;
- lire le vault parent ;
- lister les secrets du project ;
- créer un secret ;
- modifier project ;
- archiver project ;
- récupérer statistiques ;
- récupérer audit lié ;
- récupérer permissions effectives.

## Permissions nécessaires

Permissions typiques :

- lecture project metadata ;
- lecture vault metadata ;
- lecture secret metadata pour afficher les secrets ;
- création secret ;
- mise à jour project ;
- archivage project ;
- lecture audit ;
- lecture permissions effectives.

L'accès aux valeurs secrètes n'est pas nécessaire pour afficher Project Details.

## Actions disponibles

Actions principales :

- créer un secret ;
- ouvrir un secret ;
- modifier le project ;
- archiver le project ;
- consulter audit lié.

Actions secondaires :

- retourner au vault ;
- filtrer les secrets ;
- rechercher dans les secrets ;
- copier l'identifiant technique si non sensible ;
- accéder aux permissions.

## États de chargement

États attendus :

- skeleton header ;
- skeleton stats ;
- skeleton table secrets ;
- chargement action créer ;
- refresh après mutation.

## États vides

Cas possibles :

- project sans secret ;
- aucun secret accessible ;
- aucun résultat de recherche ;
- aucun événement visible.

Project sans secret :

- expliquer qu'un secret peut maintenant être créé dans ce project ;
- proposer "Créer un secret" si autorisé ;
- rappeler que les valeurs restent masquées par défaut.

## États d'erreur

Erreurs à gérer :

- project introuvable ;
- accès refusé ;
- vault parent inaccessible ;
- secrets impossibles à charger ;
- modification refusée ;
- archivage refusé ;
- session expirée ;
- erreur réseau.

## Responsive

Desktop :

- header avec actions ;
- stats en grille ;
- secrets en table ;
- activité en section secondaire.

Laptop :

- table avec colonnes essentielles.

Tablet :

- sections empilées ;
- secrets en liste ou table simplifiée.

Mobile :

- contexte vault-project très visible ;
- liste de secrets compacte ;
- action créer accessible ;
- actions secondaires dans menu.

## Notes UX

Le project est le contexte principal de gestion des secrets. L'utilisateur doit toujours savoir dans quel vault et project il agit avant de créer ou modifier un secret.

La liste des secrets ne doit jamais afficher les valeurs. Même les fragments doivent être limités et justifiés.

# Secret List

## Objectif

Secret List permet de consulter, rechercher, filtrer et administrer les secrets accessibles dans un project ou globalement selon les permissions.

Cette vue est critique. Elle doit insister sur un principe central : la valeur d'un secret n'est jamais affichée dans la liste.

La liste affiche les métadonnées, statuts et informations opérationnelles, mais jamais les valeurs secrètes complètes.

## Utilisateur

Utilisateurs concernés :

- développeur ;
- DevOps ;
- équipe IA ;
- administrateur ;
- responsable sécurité ;
- compte humain avec accès limité.

L'utilisateur peut consulter les métadonnées des secrets selon ses permissions. La lecture de valeur est une permission distincte et ne doit pas être confondue avec l'accès à la liste.

## Informations affichées

Colonnes attendues :

- nom du secret ;
- project ;
- vault ;
- description courte ;
- statut ;
- provider ou type si disponible ;
- version courante ;
- date de dernière version ;
- date de création ;
- date de mise à jour ;
- tags ou métadonnées non sensibles si disponibles ;
- actions.

Informations explicitement interdites dans la liste :

- valeur secrète complète ;
- token complet ;
- mot de passe ;
- clé privée ;
- credential brut ;
- ancienne valeur ;
- contenu de version ;
- donnée qui permettrait une exfiltration.

Badges :

- active ;
- archived ;
- deleted logically si supporté ;
- current version ;
- provider ;
- permission limitée ;
- valeur lisible si l'API expose une indication sûre ;
- rotation future si disponible plus tard.

Statuts :

- actif ;
- archivé ;
- supprimé logiquement ;
- version manquante ;
- lecture valeur autorisée ou non si fourni sans risque ;
- project archivé ;
- vault locked.

Recherche :

- nom ;
- description ;
- tags ;
- provider ;
- métadonnées autorisées ;
- jamais dans les valeurs secrètes au MVP.

Filtres :

- vault ;
- project ;
- statut ;
- provider ;
- date de mise à jour ;
- version courante ;
- archived ;
- locked context si disponible.

Tri :

- nom ;
- date de création ;
- date de mise à jour ;
- project ;
- statut ;
- version courante.

Pagination :

- standard pour grands volumes ;
- conservation recherche et filtres.

## Composants utilisés

Composants attendus :

- page header ;
- table de secrets ;
- recherche ;
- filtres ;
- tri ;
- pagination ;
- badges ;
- menu d'actions ;
- bouton créer ;
- dialog de création ;
- dialog d'archivage ;
- empty state ;
- skeleton ;
- alertes sécurité contextuelles.

La table doit être conçue pour une forte scannabilité.

## API utilisées

API consommées conceptuellement :

- lister les secrets ;
- lister les secrets d'un project ;
- rechercher les secrets par métadonnées ;
- créer un secret ;
- lire metadata d'un secret ;
- archiver ou supprimer logiquement un secret ;
- récupérer permissions effectives ;
- récupérer vaults/projects accessibles pour filtres.

La lecture de valeur secrète ne doit pas être consommée par la liste.

## Permissions nécessaires

Permissions typiques :

- lecture secret metadata ;
- lecture project metadata ;
- lecture vault metadata ;
- création secret ;
- mise à jour secret metadata ;
- archivage secret ;
- suppression logique secret si disponible ;
- lecture secret value uniquement pour actions dédiées hors affichage liste.

La liste doit fonctionner pour des utilisateurs qui peuvent lire les métadonnées sans pouvoir révéler les valeurs.

## Actions disponibles

Actions principales :

- rechercher ;
- filtrer ;
- trier ;
- ouvrir un secret ;
- créer un secret.

Actions de ligne :

- ouvrir détails ;
- modifier metadata ;
- créer une nouvelle version ;
- archiver ;
- supprimer logiquement si supporté ;
- consulter audit lié ;
- révéler la valeur uniquement via action explicite et si autorisé.

L'action "Reveal" ne doit pas être l'action principale de la liste. Elle doit rester volontaire, contextualisée et idéalement effectuée depuis Secret Details.

## États de chargement

États attendus :

- skeleton de table ;
- chargement de recherche ;
- chargement de filtres ;
- chargement de création ;
- refresh après mutation ;
- indicateur discret pour pagination.

Les skeletons ne doivent jamais simuler des valeurs secrètes.

## États vides

Cas possibles :

- aucun secret dans le project ;
- aucun secret accessible ;
- aucun résultat de recherche ;
- aucun résultat pour filtres.

État vide sans secret :

- expliquer qu'un secret stocke une valeur sensible versionnée ;
- proposer de créer un secret si autorisé ;
- rappeler que les valeurs seront masquées par défaut.

État vide filtré :

- proposer de retirer les filtres ;
- ne pas suggérer que des secrets existent si l'utilisateur n'est pas autorisé à les voir.

## États d'erreur

Erreurs à gérer :

- impossible de charger les secrets ;
- project inaccessible ;
- vault locked ;
- accès refusé ;
- création refusée ;
- conflit de nom ;
- archivage refusé ;
- session expirée ;
- erreur réseau.

Une erreur de permission sur la lecture de valeur ne doit pas empêcher l'affichage des métadonnées si celles-ci sont autorisées.

## Responsive

Desktop :

- table complète ;
- filtres visibles ;
- badges visibles ;
- actions contextuelles.

Laptop :

- colonnes essentielles ;
- description ou métadonnées secondaires tronquées.

Tablet :

- table simplifiée ou liste structurée ;
- project et statut visibles ;
- filtres en panneau.

Mobile :

- liste compacte ;
- nom, project, statut et version courante visibles ;
- aucune valeur ;
- actions dans menu ;
- création accessible si autorisée.

## Notes UX

La Secret List doit éduquer l'utilisateur par sa structure : les secrets ont des métadonnées visibles, mais leur valeur est protégée.

Aucune valeur ne doit être visible dans les colonnes, prévisualisations, tooltips, exports, attributs de recherche ou états de chargement.

Les badges doivent aider à distinguer rapidement les statuts. Archived, locked et revoked doivent être visuellement différents.

# Secret Details

## Objectif

Secret Details permet de consulter et administrer un secret précis.

Cette vue est la surface principale pour comprendre un secret : metadata, version courante, historique, permissions, actions de révélation, copie, audit et préparation à la rotation future.

Elle doit respecter un principe absolu : la valeur n'est jamais affichée par défaut.

## Utilisateur

Utilisateurs concernés :

- développeur ;
- DevOps ;
- équipe IA ;
- administrateur ;
- responsable sécurité ;
- utilisateur avec permission de lecture metadata ;
- utilisateur avec permission distincte de lecture value si autorisé.

## Informations affichées

Metadata :

- nom du secret ;
- description ;
- vault parent ;
- project parent ;
- statut ;
- provider ou type ;
- tags ou métadonnées ;
- date de création ;
- date de mise à jour ;
- identifiant technique si utile ;
- version courante ;
- créateur si disponible.

Versions :

- version courante ;
- nombre de versions ;
- dernières versions ;
- date de création des versions ;
- statut de version ;
- accès vers l'historique complet.

Permissions :

- permissions effectives de l'utilisateur si disponibles ;
- indication de capacité à lire metadata ;
- indication de capacité à lire value si fournie de manière sûre ;
- rôles ou acteurs associés si disponibles.

Reveal :

- valeur masquée par défaut ;
- action explicite pour révéler ;
- indication que la lecture peut être auditée ;
- durée ou contexte d'affichage si prévu ;
- état de permission insuffisante si refusée.

Copy :

- copie de la valeur uniquement après action autorisée ;
- feedback de copie ;
- pas de persistance ;
- pas de copie invisible automatique.

Audit :

- derniers événements liés au secret ;
- lectures de valeur ;
- créations de version ;
- modifications metadata ;
- refus d'accès ;
- acteur ;
- date ;
- résultat.

Rotation future :

- emplacement prévu pour information de rotation ;
- statut de rotation future ;
- dernière rotation future ;
- prochaine rotation future ;
- action future de rotation manuelle.

Au MVP, la rotation future peut être indiquée comme non disponible seulement si cela apporte une valeur UX. Il ne faut pas encombrer la vue avec des fonctionnalités absentes.

## Composants utilisés

Composants attendus :

- page header ;
- breadcrumb vault/project ;
- badges de statut ;
- panneau metadata ;
- composant de valeur masquée ;
- bouton Reveal ;
- bouton Copy ;
- section versions ;
- table courte des versions ;
- section permissions ;
- section audit ;
- dialogs de révélation ;
- dialogs de confirmation ;
- actions contextuelles ;
- skeletons ;
- empty states.

Les composants de valeur secrète doivent être traités comme des composants de sécurité.

## API utilisées

API consommées conceptuellement :

- lire metadata du secret ;
- lire versions du secret ;
- lire version courante ;
- créer une nouvelle version ;
- révéler la valeur du secret ou d'une version autorisée ;
- copier côté client après réception autorisée ;
- lire audit lié ;
- récupérer permissions effectives ;
- modifier metadata ;
- archiver ou supprimer logiquement.

L'API de lecture de valeur doit être appelée uniquement après action utilisateur explicite.

## Permissions nécessaires

Permissions typiques :

- lecture secret metadata ;
- lecture project metadata ;
- lecture vault metadata ;
- lecture secret version metadata ;
- création secret version ;
- lecture secret value pour Reveal et Copy ;
- mise à jour secret metadata ;
- archivage secret ;
- suppression logique secret ;
- lecture audit logs.

La permission de lire metadata ne donne jamais implicitement la permission de lire value.

## Actions disponibles

Actions principales :

- modifier metadata ;
- créer une nouvelle version ;
- révéler la valeur si autorisé ;
- copier la valeur si autorisé ;
- consulter l'historique complet ;
- consulter audit lié.

Actions secondaires :

- archiver ;
- supprimer logiquement si disponible ;
- copier identifiant non sensible ;
- retourner au project ;
- accéder aux permissions.

Actions futures :

- déclencher rotation ;
- configurer rotation ;
- ajouter webhook lié ;
- surveiller usage.

## États de chargement

États attendus :

- skeleton metadata ;
- skeleton versions ;
- skeleton audit ;
- chargement Reveal isolé ;
- chargement Copy si lecture nécessaire ;
- chargement mutation metadata ;
- chargement création version.

Le chargement Reveal doit être explicitement lié à la lecture de valeur. Il ne doit pas bloquer toute la page.

## États vides

Cas possibles :

- aucune version ;
- aucun audit visible ;
- aucune permission détaillée disponible ;
- rotation non configurée future.

Un secret sans version doit être traité comme un état nécessitant attention. L'interface doit proposer de créer une version si autorisé.

## États d'erreur

Erreurs à gérer :

- secret introuvable ;
- accès refusé ;
- metadata chargée mais value refusée ;
- versions impossibles à charger ;
- audit impossible à charger ;
- reveal refusé ;
- reveal échoué ;
- copy impossible ;
- création de version refusée ;
- vault locked ;
- project archived ;
- session expirée.

Un refus de lecture value doit être clair et non dramatique. Il signifie que l'utilisateur n'a pas cette permission.

## Responsive

Desktop :

- metadata et actions visibles ;
- versions et audit en sections ;
- panneaux secondaires possibles.

Laptop :

- sections compactes ;
- actions principales dans header.

Tablet :

- sections empilées ;
- Reveal dans zone dédiée ;
- audit en liste compacte.

Mobile :

- contexte très visible ;
- valeur masquée ;
- action Reveal séparée ;
- actions dangereuses dans menu ;
- versions en liste.

## Notes UX

La vue Secret Details doit constamment distinguer :

- nom du secret ;
- metadata ;
- valeur ;
- version ;
- audit.

L'action Reveal doit être volontaire. L'utilisateur doit comprendre qu'elle peut être auditée et qu'elle expose temporairement une donnée sensible.

La copie doit donner un feedback bref, sans afficher la valeur dans un toast.

# Secret Version History

## Objectif

Secret Version History permet de consulter l'historique complet des versions d'un secret.

Il doit rendre visible l'évolution du secret dans le temps, identifier la version courante et permettre la création d'une nouvelle version si autorisée.

## Utilisateur

Utilisateurs concernés :

- développeur ;
- DevOps ;
- administrateur ;
- équipe sécurité ;
- équipe IA.

## Informations affichées

Historique :

- liste des versions ;
- numéro ou identifiant de version ;
- badge Current Version ;
- statut ;
- date de création ;
- créateur si disponible ;
- metadata crypto non sensible si affichable ;
- commentaire ou note si disponible ;
- actions.

Version courante :

- clairement identifiée ;
- positionnée dans la liste ;
- accessible depuis Secret Details ;
- badge distinct.

Création :

- action créer une nouvelle version ;
- formulaire de nouvelle valeur ;
- validation ;
- confirmation si nécessaire.

Navigation :

- breadcrumb vault/project/secret ;
- retour Secret Details ;
- lien vers audit associé ;
- accès aux détails d'une version si disponible.

Valeurs :

- jamais affichées dans l'historique ;
- reveal possible uniquement par action explicite et permission adaptée ;
- aucune prévisualisation.

## Composants utilisés

Composants attendus :

- page header ;
- breadcrumb ;
- table de versions ;
- badges ;
- bouton créer version ;
- dialog ou page de création ;
- composant champ sensible ;
- confirmation ;
- empty state ;
- skeleton ;
- pagination si nécessaire.

## API utilisées

API consommées conceptuellement :

- lister les versions d'un secret ;
- lire metadata d'une version ;
- créer une nouvelle version ;
- révéler une version si autorisé ;
- définir version courante si supporté ;
- lire audit lié.

## Permissions nécessaires

Permissions typiques :

- lecture secret metadata ;
- lecture secret version metadata ;
- création secret version ;
- lecture secret value pour révéler une version ;
- mise à jour version courante si supportée ;
- lecture audit.

## Actions disponibles

Actions principales :

- consulter versions ;
- créer nouvelle version ;
- ouvrir metadata d'une version ;
- retourner au secret.

Actions sensibles :

- révéler valeur d'une version ;
- définir une version comme courante si disponible ;
- détruire ou révoquer une version future si supporté.

## États de chargement

États attendus :

- skeleton de table ;
- chargement création version ;
- chargement reveal isolé ;
- refresh après création ;
- chargement pagination.

## États vides

Cas possibles :

- aucune version ;
- aucune version accessible ;
- aucun résultat filtré futur.

État sans version :

- expliquer qu'une version contient la valeur effective du secret ;
- proposer de créer la première version si autorisé ;
- signaler que sans version courante le secret ne peut pas fournir de valeur.

## États d'erreur

Erreurs à gérer :

- versions impossibles à charger ;
- secret introuvable ;
- accès refusé ;
- création refusée ;
- valeur invalide ;
- reveal refusé ;
- conflit de version ;
- session expirée.

## Responsive

Desktop :

- table complète ;
- badges visibles ;
- actions de ligne.

Laptop :

- table avec colonnes essentielles.

Tablet :

- liste structurée possible ;
- action créer visible.

Mobile :

- versions en liste ;
- current version très visible ;
- reveal protégé ;
- actions dans menu.

## Notes UX

L'historique doit renforcer l'idée d'immutabilité. Une version existante ne doit pas être présentée comme modifiable si le backend garantit son immutabilité.

Créer une version doit être perçu comme remplacer la valeur courante selon les règles backend, pas comme modifier silencieusement l'ancienne valeur.

# API Keys

## Objectif

API Keys permet de gérer les clés d'accès utilisées par les clients techniques.

Cette vue doit rendre explicites les accès machines : création, statut, permissions, dernière utilisation, révocation et valeur affichée une seule fois.

## Utilisateur

Utilisateurs concernés :

- administrateur ;
- DevOps ;
- développeur ;
- équipe IA ;
- responsable sécurité.

## Informations affichées

Liste :

- nom de la clé ;
- acteur ou service account associé ;
- statut ;
- rôles ou permissions ;
- date de création ;
- date d'expiration si disponible ;
- dernière utilisation ;
- créateur ;
- scope ou contexte ;
- actions.

Création :

- nom ;
- description ;
- acteur ou service account ;
- permissions ou rôle ;
- expiration si disponible ;
- contexte vault/project si applicable ;
- confirmation ;
- valeur générée affichée une seule fois.

Révocation :

- clé concernée ;
- conséquence ;
- confirmation ;
- feedback ;
- statut revoked après confirmation backend.

Permissions :

- rôles associés ;
- permissions visibles ;
- périmètre ;
- indication de moindre privilège si disponible.

Dernière utilisation :

- date ;
- acteur technique ;
- ressource ou endpoint si disponible ;
- état jamais utilisée ;
- lien vers audit si disponible.

Valeur affichée une seule fois :

- affichage après création uniquement si backend le prévoit ;
- message indiquant qu'elle ne sera plus récupérable ;
- action de copie ;
- nettoyage après fermeture ;
- aucun affichage dans la liste.

## Composants utilisés

Composants attendus :

- page header ;
- table API keys ;
- badges de statut ;
- badges role/permission ;
- bouton créer ;
- dialog de création ;
- écran ou dialog de valeur générée ;
- bouton copy ;
- dialog de révocation ;
- filtres ;
- recherche ;
- pagination ;
- empty state ;
- skeleton.

## API utilisées

API consommées conceptuellement :

- lister API keys ;
- créer API key ;
- lire metadata API key ;
- révoquer API key ;
- lister rôles ou permissions disponibles ;
- lire dernière utilisation si disponible ;
- lire audit lié.

La valeur complète d'une API key ne doit jamais être récupérée après création si le backend applique cette règle.

## Permissions nécessaires

Permissions typiques :

- lecture API key metadata ;
- création API key ;
- révocation API key ;
- lecture roles ;
- lecture permissions ;
- lecture audit ;
- gestion service accounts si disponible.

## Actions disponibles

Actions principales :

- créer API key ;
- consulter liste ;
- filtrer ;
- rechercher ;
- révoquer ;
- consulter audit lié.

Actions secondaires :

- copier valeur lors de création ;
- consulter détail metadata ;
- modifier description si supporté ;
- filtrer par statut ;
- filtrer par acteur.

## États de chargement

États attendus :

- skeleton de table ;
- chargement création ;
- chargement valeur générée ;
- chargement révocation ;
- refresh après révocation ;
- chargement rôles/permissions disponibles.

Pendant la création, l'utilisateur ne doit pas fermer accidentellement le dialog sans comprendre que la valeur pourrait être perdue.

## États vides

Cas possibles :

- aucune API key ;
- aucune API key active ;
- aucun résultat filtré ;
- aucune permission pour créer.

État vide :

- expliquer qu'une API key donne accès à un client technique ;
- proposer d'en créer une si autorisé ;
- rappeler qu'elle doit être limitée au nécessaire.

## États d'erreur

Erreurs à gérer :

- liste impossible à charger ;
- création refusée ;
- permissions invalides ;
- révocation refusée ;
- clé déjà révoquée ;
- valeur non récupérable ;
- session expirée ;
- erreur réseau.

Une erreur après création doit être traitée avec prudence si la valeur a été générée. L'interface doit suivre strictement la réponse backend.

## Responsive

Desktop :

- table complète ;
- permissions visibles ;
- dernière utilisation visible ;
- actions de ligne.

Laptop :

- colonnes essentielles ;
- permissions résumées.

Tablet :

- liste structurée ;
- filtres dans panneau ;
- création en dialog adapté.

Mobile :

- liste compacte ;
- statut et dernière utilisation visibles ;
- révocation protégée ;
- valeur créée affichée dans une vue très claire et lisible.

## Notes UX

La création d'une API key est un moment de sécurité majeur.

L'interface doit rappeler que la valeur doit être copiée et stockée dans un endroit sûr. Elle ne doit jamais afficher la valeur dans un toast, une table, un log ou une URL.

La révocation doit être claire : elle invalide l'accès technique concerné et peut impacter des services.

# Audit Logs

## Objectif

Audit Logs permet de consulter, filtrer et analyser les événements d'audit.

Cette vue est essentielle pour la traçabilité. Elle doit aider à répondre rapidement à la question : qui a fait quoi, quand, sur quelle ressource, avec quel résultat.

## Utilisateur

Utilisateurs concernés :

- administrateur ;
- DevOps ;
- responsable sécurité ;
- équipe IA ;
- auditeur interne futur ;
- responsable technique.

## Informations affichées

Table :

- date et heure ;
- acteur ;
- type d'acteur ;
- action ;
- ressource ;
- type de ressource ;
- résultat ;
- adresse ou contexte si disponible et sûr ;
- niveau de sensibilité ;
- actions.

Filtres :

- période ;
- acteur ;
- type d'action ;
- type de ressource ;
- résultat ;
- vault ;
- project ;
- secret ;
- API key ;
- lecture valeur ;
- refus d'autorisation.

Recherche :

- identifiant d'événement ;
- acteur ;
- ressource ;
- action ;
- metadata autorisées.

Pagination :

- pagination robuste ;
- ordre chronologique stable ;
- conservation filtres ;
- accès page suivante/précédente ;
- éventuellement curseur futur.

Détail :

- événement complet ;
- date ;
- acteur ;
- action ;
- ressource ;
- résultat ;
- contexte ;
- message sûr ;
- liens vers ressources ;
- informations techniques non sensibles ;
- corrélation future si disponible.

Navigation vers ressources :

- vault ;
- project ;
- secret metadata ;
- API key metadata ;
- acteur ;
- role ;
- event related details.

## Composants utilisés

Composants attendus :

- page header ;
- table dense ;
- filtres avancés ;
- recherche ;
- badges de résultat ;
- badges de type d'action ;
- pagination ;
- drawer ou page de détail ;
- liens contextuels ;
- empty state ;
- skeleton table ;
- alertes d'erreur.

## API utilisées

API consommées conceptuellement :

- lister audit logs ;
- filtrer audit logs ;
- rechercher audit logs ;
- lire détail d'un événement ;
- récupérer listes de filtres si disponibles ;
- récupérer ressources liées selon permissions.

Les audit logs ne doivent jamais contenir de valeurs secrètes. Le frontend doit aussi éviter de les afficher s'ils apparaissaient par erreur.

## Permissions nécessaires

Permissions typiques :

- lecture audit logs ;
- lecture ressource liée pour navigation ;
- lecture actor metadata si disponible ;
- lecture vault/project/secret metadata selon liens.

Un utilisateur sans permission audit ne doit pas accéder à cette vue.

## Actions disponibles

Actions principales :

- filtrer ;
- rechercher ;
- changer de période ;
- ouvrir détail ;
- naviguer vers ressource liée ;
- réinitialiser filtres ;
- changer de page.

Actions futures :

- exporter metadata d'audit ;
- sauvegarder une recherche ;
- créer alerte ;
- envoyer vers SIEM.

Aucun export de valeurs secrètes ne doit exister.

## États de chargement

États attendus :

- skeleton de table ;
- chargement de filtres ;
- chargement de page suivante ;
- chargement du détail ;
- refresh discret.

La table doit préserver la structure pendant le chargement.

## États vides

Cas possibles :

- aucun audit log ;
- aucun résultat sur période ;
- aucun résultat après filtres ;
- audit non disponible.

État vide :

- expliquer la situation ;
- proposer de modifier filtres ;
- pour instance fraîche, indiquer que les événements apparaîtront après actions.

## États d'erreur

Erreurs à gérer :

- accès refusé ;
- logs impossibles à charger ;
- détail introuvable ;
- filtre invalide ;
- backend indisponible ;
- session expirée.

Les erreurs ne doivent jamais afficher de payload brut sensible.

## Responsive

Desktop :

- table dense complète ;
- filtres visibles ;
- détail en drawer ou page.

Laptop :

- colonnes essentielles ;
- filtres repliables si nécessaire.

Tablet :

- table simplifiée ;
- filtres en panneau ;
- détail en page ou drawer plein écran.

Mobile :

- liste chronologique ;
- filtres accessibles ;
- détail plein écran ;
- navigation vers ressources claire.

## Notes UX

Audit Logs doit être conçu pour l'enquête.

Les actions sensibles comme lecture de valeur, révocation, refus d'autorisation et modification RBAC doivent être rapidement identifiables.

La date et l'acteur sont prioritaires. Le détail doit fournir le contexte sans exposer de secret.

# RBAC

## Objectif

RBAC permet de consulter et administrer les rôles, permissions et assignments.

Cette vue traduit le modèle d'autorisation backend en interface compréhensible. Elle ne doit jamais devenir une implémentation frontend autonome de la permission métier.

## Utilisateur

Utilisateurs concernés :

- administrateur ;
- responsable sécurité ;
- DevOps senior ;
- responsable technique ;
- utilisateur Enterprise futur.

## Informations affichées

Roles :

- liste des rôles ;
- nom ;
- description ;
- type système ou custom futur ;
- nombre de permissions ;
- nombre d'assignments ;
- date de création si disponible ;
- statut.

Permissions :

- action autorisée ;
- ressource concernée ;
- niveau de sensibilité ;
- description ;
- groupe fonctionnel ;
- indication des permissions critiques.

Assignments :

- acteur ;
- type d'acteur ;
- rôle ;
- scope ;
- vault ou project concerné ;
- date d'attribution ;
- attribué par ;
- statut.

Vue détaillée :

- détail d'un rôle ;
- permissions incluses ;
- acteurs assignés ;
- historique ;
- actions de modification.

Modification :

- créer ou modifier rôle futur si supporté ;
- ajouter assignment ;
- retirer assignment ;
- changer scope ;
- confirmation.

Restrictions :

- rôles système non modifiables si backend les définit ;
- permissions critiques confirmées ;
- impossibilité de retirer son propre accès admin sans protection si backend impose une règle ;
- backend autorité finale.

## Composants utilisés

Composants attendus :

- tabs Roles, Permissions, Assignments ;
- tables ;
- badges role ;
- badges permission ;
- filtres ;
- recherche ;
- dialogs de modification ;
- dialogs de confirmation ;
- page ou drawer de détail ;
- empty states ;
- skeletons ;
- alertes de restriction.

## API utilisées

API consommées conceptuellement :

- lister rôles ;
- lire rôle ;
- lister permissions ;
- lister assignments ;
- créer assignment ;
- retirer assignment ;
- modifier rôle si supporté ;
- récupérer acteurs ;
- récupérer scopes disponibles ;
- lire audit lié RBAC.

## Permissions nécessaires

Permissions typiques :

- lecture RBAC ;
- lecture roles ;
- lecture permissions ;
- lecture assignments ;
- modification RBAC ;
- création assignment ;
- suppression assignment ;
- lecture actors ;
- lecture audit.

La modification RBAC doit être strictement contrôlée par le backend.

## Actions disponibles

Actions principales :

- consulter rôles ;
- consulter permissions ;
- consulter assignments ;
- ouvrir détail ;
- ajouter assignment si autorisé ;
- retirer assignment si autorisé ;
- modifier rôle si supporté.

Actions sensibles :

- accorder permission critique ;
- retirer rôle ;
- modifier rôle admin ;
- changer scope ;
- supprimer assignment.

Chaque action sensible nécessite confirmation.

## États de chargement

États attendus :

- skeleton tables ;
- chargement tabs ;
- chargement détail ;
- chargement modification ;
- refresh après changement.

## États vides

Cas possibles :

- aucun assignment ;
- aucun rôle custom ;
- aucune permission visible ;
- aucun résultat filtré.

État vide :

- expliquer le rôle de RBAC ;
- proposer une action si autorisée ;
- sinon indiquer que les droits sont gérés par un administrateur.

## États d'erreur

Erreurs à gérer :

- accès refusé ;
- rôles impossibles à charger ;
- assignments impossibles à charger ;
- modification refusée ;
- conflit ;
- tentative de retrait non autorisée ;
- session expirée.

Les erreurs doivent expliquer l'échec sans divulguer de structure interne inutile.

## Responsive

Desktop :

- tabs et tables complètes ;
- détail en panneau ;
- filtres visibles.

Laptop :

- tables avec colonnes essentielles ;
- détail en drawer.

Tablet :

- tabs empilées ;
- assignments en liste structurée.

Mobile :

- navigation par sections ;
- rôles en liste ;
- permissions regroupées ;
- modification sensible en écran dédié ou dialog plein écran.

## Notes UX

RBAC doit être très lisible.

Les libellés doivent expliquer clairement ce qu'une permission permet. Les permissions liées à secret value read doivent être visuellement plus sensibles qu'une permission de lecture metadata.

Le frontend doit toujours gérer le cas où une action visible est refusée par le backend, car les permissions peuvent changer.

# User Profile

## Objectif

User Profile permet à l'utilisateur connecté de consulter ses informations personnelles, préférences, éléments de sécurité de session et actions liées à son compte.

## Utilisateur

Tous les utilisateurs humains authentifiés.

## Informations affichées

Informations :

- nom ;
- email ou identifiant ;
- rôle principal si disponible ;
- type de compte ;
- date de création si disponible ;
- organisation ou tenant futur ;
- informations non sensibles de profil.

Préférences :

- thème ;
- densité d'affichage future ;
- préférences de table futures ;
- langue future si supportée ;
- format de date futur.

Sécurité :

- état de session ;
- dernière connexion si disponible ;
- sessions actives futures ;
- MFA futur ;
- changement de mot de passe futur si applicable.

Session :

- bouton logout ;
- indication session expirant bientôt si disponible ;
- action de refresh implicite si supportée.

## Composants utilisés

Composants attendus :

- page header ;
- sections de profil ;
- formulaire de préférences ;
- badges role ;
- boutons ;
- dialog logout si nécessaire ;
- alertes ;
- skeletons.

## API utilisées

API consommées conceptuellement :

- lire profil courant ;
- modifier préférences ;
- lire état session ;
- logout ;
- lire informations de sécurité du compte si disponible.

## Permissions nécessaires

Permission typique :

- utilisateur authentifié.

Certaines informations avancées peuvent nécessiter des permissions spécifiques, mais le profil de base doit appartenir à l'utilisateur connecté.

## Actions disponibles

Actions principales :

- modifier préférences ;
- changer thème ;
- logout ;
- rafraîchir profil.

Actions futures :

- configurer MFA ;
- gérer sessions ;
- changer mot de passe ;
- connecter SSO.

## États de chargement

États attendus :

- skeleton profil ;
- chargement préférences ;
- chargement sauvegarde ;
- chargement logout.

## États vides

Cas possibles :

- certaines préférences non disponibles ;
- informations de sécurité non disponibles ;
- rôle non affichable.

L'UI doit rester simple et ne pas présenter cela comme une erreur.

## États d'erreur

Erreurs à gérer :

- profil impossible à charger ;
- sauvegarde préférences échouée ;
- logout échoué ;
- session expirée ;
- accès refusé inattendu.

## Responsive

Desktop :

- sections en colonnes ou blocs ;
- sécurité et préférences séparées.

Laptop :

- blocs compacts.

Tablet :

- sections empilées.

Mobile :

- sections simples ;
- bouton logout visible ;
- formulaires adaptés.

## Notes UX

Le profil doit aider l'utilisateur à comprendre avec quel compte il agit.

Il ne doit pas devenir une page de paramètres globaux. Les paramètres de l'instance appartiennent à Settings.

# Settings

## Objectif

Settings permet de consulter et modifier les paramètres disponibles de l'application ou de l'instance.

Cette vue doit rester prudente : elle ne doit jamais exposer de secrets de configuration, tokens internes, clés maîtres ou détails dangereux.

## Utilisateur

Utilisateurs concernés :

- administrateur ;
- DevOps ;
- responsable technique ;
- responsable sécurité.

## Informations affichées

Configuration :

- nom de l'instance si disponible ;
- URL publique si disponible ;
- environnement non sensible ;
- statut des fonctionnalités ;
- paramètres frontend ;
- options de sécurité exposées au MVP.

Informations système :

- version frontend ;
- version backend si considérée sûre ;
- état API ;
- état santé simplifié ;
- mode déploiement non sensible ;
- informations de configuration publiques.

Préférences :

- thème global futur ;
- options d'affichage ;
- préférences d'organisation future ;
- defaults non sensibles.

Paramètres disponibles :

- paramètres de session si exposés ;
- paramètres d'audit si exposés ;
- paramètres UI ;
- futurs paramètres notifications ;
- futurs paramètres integrations ;
- futurs paramètres billing.

Informations interdites :

- clé maître ;
- tokens ;
- secrets ;
- mots de passe ;
- variables d'environnement sensibles ;
- chaînes de connexion ;
- détails internes exploitables.

## Composants utilisés

Composants attendus :

- page header ;
- sections de paramètres ;
- formulaires ;
- toggles ;
- selects ;
- badges de statut ;
- alertes ;
- dialogs de confirmation ;
- empty states ;
- skeletons.

## API utilisées

API consommées conceptuellement :

- lire paramètres disponibles ;
- modifier paramètres autorisés ;
- lire health/status simplifié ;
- lire configuration publique ;
- lire permissions administratives ;
- audit des changements sensibles.

## Permissions nécessaires

Permissions typiques :

- lecture settings ;
- modification settings ;
- lecture health ;
- lecture configuration publique ;
- administration instance pour paramètres sensibles.

Les paramètres non autorisés doivent être masqués ou affichés en lecture seule selon les règles backend.

## Actions disponibles

Actions principales :

- consulter configuration ;
- modifier paramètres disponibles ;
- sauvegarder ;
- réinitialiser un champ ;
- consulter statut système.

Actions sensibles :

- modifier une option de sécurité ;
- désactiver une fonctionnalité ;
- changer un comportement d'audit ;
- modifier une stratégie de session.

Ces actions doivent être confirmées.

## États de chargement

États attendus :

- skeleton sections ;
- chargement sauvegarde ;
- refresh statut ;
- chargement permissions.

## États vides

Cas possibles :

- aucun paramètre modifiable ;
- statut système non disponible ;
- fonctionnalité future non activée.

L'empty state doit expliquer que certains paramètres sont configurés côté serveur ou hors UI.

## États d'erreur

Erreurs à gérer :

- accès refusé ;
- paramètres impossibles à charger ;
- sauvegarde refusée ;
- validation échouée ;
- conflit de configuration ;
- session expirée ;
- backend indisponible.

## Responsive

Desktop :

- sections organisées ;
- navigation interne si beaucoup de paramètres ;
- formulaires lisibles.

Laptop :

- sections compactes.

Tablet :

- sections empilées ;
- navigation interne repliée.

Mobile :

- paramètres en liste ;
- actions sensibles confirmées ;
- formulaires adaptés.

## Notes UX

Settings doit être sobre et rassurant.

Une option non disponible ne doit pas être présentée comme cassée. Les fonctionnalités futures peuvent être absentes sans polluer le MVP.

Les informations système doivent aider au diagnostic sans révéler de détails sensibles.

# Navigation globale

La navigation globale structure l'expérience de MCP Secret Manager.

Elle doit permettre à l'utilisateur de comprendre rapidement :

- où il se trouve ;
- quelles sections existent ;
- quelle ressource est active ;
- quelles actions globales sont disponibles ;
- comment revenir à un contexte parent.

## Sidebar

La Sidebar est la navigation principale de l'application authentifiée.

Sections attendues :

- Dashboard ;
- Vaults ;
- Projects ;
- Secrets ;
- API Keys ;
- Audit Logs ;
- RBAC ;
- Settings.

Principes :

- élément actif clairement visible ;
- icônes cohérentes ;
- labels explicites ;
- organisation stable ;
- sections futures ajoutées sans casser la structure ;
- version mobile via drawer ou navigation adaptée.

La Sidebar ne doit pas afficher des sections que l'utilisateur ne peut jamais consulter, sauf si une stratégie produit choisit explicitement de montrer des entrées désactivées avec explication.

## Topbar

La Topbar fournit les informations et actions globales.

Contenu possible :

- recherche globale ;
- état de session ;
- profil utilisateur ;
- accès notifications futures ;
- raccourci command palette future ;
- contexte tenant futur ;
- action de logout via menu profil.

La Topbar doit rester sobre. Elle ne doit pas dupliquer la Sidebar.

## Breadcrumb

Le Breadcrumb est essentiel pour les ressources hiérarchiques.

Il doit apparaître sur :

- Vault Details ;
- Project Details ;
- Secret Details ;
- Secret Version History ;
- pages contextuelles d'audit.

Il doit rendre claire la relation :

- Vault ;
- Project ;
- Secret ;
- Version.

Chaque élément navigable doit respecter les permissions. Un lien vers une ressource non autorisée ne doit pas exposer d'information.

## Recherche globale

La recherche globale permet de retrouver rapidement des ressources.

Périmètre MVP possible :

- vaults ;
- projects ;
- secrets par metadata ;
- API keys par metadata ;
- audit logs si supporté.

Règles :

- jamais de recherche dans les valeurs secrètes ;
- résultats limités aux permissions backend ;
- distinction claire des types de ressource ;
- navigation directe vers le détail ;
- gestion d'absence de résultat.

## Command Palette future

La Command Palette est une fonctionnalité future.

Elle pourra permettre :

- navigation rapide ;
- actions courantes ;
- création de ressources ;
- recherche ;
- accès aux paramètres.

Règles futures :

- ne pas permettre d'action dangereuse sans confirmation ;
- ne jamais révéler un secret directement ;
- respecter les permissions backend ;
- afficher le contexte de l'action.

## Notifications future

Les notifications sont futures.

Elles pourront afficher :

- alertes de sécurité ;
- expiration de clé ;
- rotation échouée ;
- webhooks en erreur ;
- monitoring ;
- demandes d'approbation.

Règles futures :

- aucune valeur secrète ;
- liens contextuels ;
- niveau de criticité ;
- état lu/non lu ;
- préférences utilisateur.

# Flux utilisateur

Cette section décrit les principaux parcours fonctionnels. Ces flux doivent guider l'implémentation des écrans, dialogs, confirmations, états et tests.

## Créer un Vault

Point de départ :

- Dashboard ;
- Vault List ;
- action rapide globale future.

Étapes :

- l'utilisateur clique sur créer un vault ;
- l'interface affiche un formulaire ;
- l'utilisateur renseigne nom et description ;
- la validation frontend vérifie les erreurs évidentes ;
- la soumission appelle le backend ;
- le backend confirme ou refuse ;
- l'UI affiche un feedback ;
- la liste est invalidée ou rafraîchie ;
- l'utilisateur est redirigé vers Vault Details ou reste sur la liste selon la décision UX.

Permissions :

- création vault.

États :

- loading de soumission ;
- erreur de validation ;
- conflit de nom ;
- accès refusé ;
- succès.

Notes UX :

- expliquer qu'un vault est une frontière de sécurité ;
- éviter trop de champs au MVP ;
- proposer ensuite de créer un project.

## Créer un Project

Point de départ :

- Vault Details ;
- Project List ;
- Dashboard.

Étapes :

- l'utilisateur choisit ou confirme le vault parent ;
- il renseigne le nom du project ;
- il ajoute une description optionnelle ;
- il soumet ;
- le backend valide la permission dans le vault ;
- l'UI affiche le succès ;
- le project apparaît dans la liste ;
- l'utilisateur peut accéder à Project Details.

Permissions :

- création project dans le vault cible ;
- lecture vault metadata.

Notes UX :

- le vault parent doit être explicite ;
- depuis Vault Details, il doit être prérempli ;
- proposer ensuite de créer un secret.

## Créer un Secret

Point de départ :

- Project Details ;
- Secret List ;
- action rapide future.

Étapes :

- l'utilisateur choisit le project si nécessaire ;
- il renseigne metadata du secret ;
- il saisit la première valeur si le workflow backend le prévoit ;
- les champs sensibles sont masqués ;
- la validation frontend contrôle les champs ;
- la soumission appelle le backend ;
- le backend crée metadata et version selon le contrat ;
- l'UI nettoie toute valeur locale ;
- l'utilisateur accède à Secret Details ou reste dans la liste.

Permissions :

- création secret ;
- création secret version si valeur initiale ;
- lecture project metadata.

Notes UX :

- distinguer nom du secret et valeur ;
- rappeler que la valeur ne sera pas affichée par défaut ;
- ne jamais placer la valeur dans l'URL, logs ou état persistant.

## Créer une Version

Point de départ :

- Secret Details ;
- Secret Version History.

Étapes :

- l'utilisateur clique sur créer une version ;
- il saisit la nouvelle valeur ;
- le champ est sensible et masqué ;
- il confirme la création ;
- le backend crée une version immutable ;
- l'UI nettoie la valeur locale ;
- l'historique est rafraîchi ;
- la version courante est mise à jour selon règles backend.

Permissions :

- création secret version ;
- lecture secret metadata.

Notes UX :

- expliquer qu'une nouvelle version ne modifie pas l'ancienne ;
- afficher clairement la version courante après succès ;
- éviter optimistic update pour cette action.

## Révéler un Secret

Point de départ :

- Secret Details ;
- éventuellement Secret Version History.

Étapes :

- l'utilisateur clique sur Reveal ;
- l'UI affiche une confirmation ou indication selon niveau de risque ;
- l'utilisateur confirme ;
- le frontend appelle l'API de lecture de valeur ;
- le backend autorise, audite et retourne la valeur ;
- l'UI affiche la valeur temporairement ;
- l'utilisateur peut copier ;
- fermeture ou expiration nettoie la valeur.

Permissions :

- lecture secret value ;
- lecture metadata associée.

États :

- permission insuffisante ;
- chargement reveal ;
- erreur ;
- succès ;
- expiration affichage.

Notes UX :

- ne jamais révéler par défaut ;
- ne jamais révéler dans une table ;
- ne jamais afficher dans un toast ;
- expliquer que l'action peut être auditée ;
- nettoyer la valeur dès que possible.

## Créer une API Key

Point de départ :

- API Keys ;
- Dashboard action rapide ;
- Settings futur.

Étapes :

- l'utilisateur ouvre le formulaire ;
- il choisit nom, acteur, rôle ou permissions ;
- il définit un scope si disponible ;
- il confirme la création ;
- le backend génère la clé ;
- l'UI affiche la valeur complète une seule fois ;
- l'utilisateur copie la valeur ;
- fermeture nettoie la valeur ;
- la liste est rafraîchie.

Permissions :

- création API key ;
- lecture roles/permissions ;
- lecture actors si disponible.

Notes UX :

- insister sur le fait que la valeur ne sera plus récupérable si applicable ;
- ne pas autoriser fermeture accidentelle sans message ;
- ne jamais stocker la valeur.

## Révoquer une API Key

Point de départ :

- API Keys list ;
- API Key details future ;
- Audit context future.

Étapes :

- l'utilisateur sélectionne révoquer ;
- l'UI affiche une confirmation ;
- la confirmation nomme la clé et l'impact possible ;
- l'utilisateur confirme ;
- le backend révoque ;
- la table est rafraîchie ;
- le badge Revoked apparaît.

Permissions :

- révocation API key.

Notes UX :

- action Danger ;
- pas d'optimistic update ;
- indiquer que les services utilisant cette clé peuvent échouer.

## Consulter un Audit Log

Point de départ :

- Audit Logs ;
- Dashboard activité récente ;
- Secret Details ;
- Vault Details ;
- Project Details ;
- API Keys.

Étapes :

- l'utilisateur ouvre une liste d'événements ;
- il filtre ou recherche ;
- il sélectionne un événement ;
- le détail s'affiche ;
- il navigue vers la ressource liée si autorisé.

Permissions :

- lecture audit logs ;
- lecture ressource liée si navigation.

Notes UX :

- priorité à date, acteur, action, ressource, résultat ;
- aucun secret ;
- refus d'accès visible ;
- liens contextuels sûrs.

## Modifier un rôle

Point de départ :

- RBAC ;
- détail role ;
- assignment.

Étapes :

- l'utilisateur consulte un rôle ;
- il choisit une modification autorisée ;
- l'UI affiche les permissions concernées ;
- une confirmation apparaît si impact sensible ;
- le backend valide ;
- l'UI rafraîchit roles et assignments ;
- l'audit reflète l'action.

Permissions :

- modification RBAC ;
- lecture roles ;
- lecture permissions ;
- lecture assignments.

Notes UX :

- les rôles système peuvent être non modifiables ;
- les permissions critiques doivent être clairement identifiées ;
- ne pas permettre d'action ambiguë sur un scope.

# Principes UI

Tous les écrans de MCP Secret Manager doivent respecter les principes suivants.

- Le backend est la source de vérité.
- Le frontend ne contient jamais de logique de permission métier définitive.
- Une valeur secrète n'est jamais affichée par défaut.
- Une valeur secrète n'est jamais affichée dans une liste, une table, un toast, une URL ou un log.
- La lecture de valeur est toujours une action explicite.
- La copie d'une valeur est une action explicite.
- Les actions sensibles sont confirmées.
- Les actions dangereuses utilisent un traitement visuel cohérent.
- La couleur n'est jamais la seule information.
- Les états archived, locked et revoked sont distincts.
- Les tables privilégient la scannabilité.
- Les formulaires préviennent les erreurs avant soumission.
- Les erreurs sont actionnables et sûres.
- Les états vides expliquent, rassurent, guident et proposent une action.
- Les loading states préservent la structure.
- Les actions non autorisées sont masquées, désactivées ou expliquées selon le contexte.
- Tout refus backend est géré comme un cas normal.
- Les breadcrumbs sont utilisés pour les ressources hiérarchiques.
- Les données sensibles ne sont jamais stockées inutilement.
- Les caches sont invalidés après mutation.
- Les optimistic updates sont évités pour les actions de sécurité.
- Les composants doivent être accessibles au clavier.
- Le focus doit être visible.
- Le dark mode et le light mode sont traités comme des expériences complètes.
- Les écrans mobile doivent préserver la sécurité des actions.
- Le produit doit rester sobre, premium, précis et professionnel.
- Chaque écran doit aider l'utilisateur à savoir où il est, ce qu'il voit, ce qu'il peut faire et ce qui est risqué.

Cette spécification UI doit guider l'implémentation React écran par écran. Toute évolution future doit conserver la même exigence : rendre MCP Secret Manager administrable, clair, sécurisé et agréable à utiliser sans jamais compromettre les garanties fondamentales du produit.
