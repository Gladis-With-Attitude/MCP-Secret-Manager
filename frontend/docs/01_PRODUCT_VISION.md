# Vision

MCP Secret Manager doit devenir l'interface d'administration moderne, claire et sécurisée permettant de piloter un gestionnaire de secrets conçu pour les environnements IA, DevOps, SaaS et MCP.

Le frontend n'est pas une simple couche visuelle posée sur une API. Il représente la surface de confiance humaine du produit : l'endroit où un administrateur comprend l'état de ses secrets, contrôle les accès, détecte les comportements sensibles, configure les permissions, révise l'historique et prend des décisions de sécurité avec le moins d'ambiguïté possible.

La mission du produit est de rendre la gestion des secrets à la fois robuste, compréhensible et opérationnelle pour des équipes qui manipulent des infrastructures de plus en plus distribuées. Les secrets ne sont plus seulement consommés par des applications traditionnelles. Ils sont utilisés par des scripts, des containers, des serveurs MCP, des agents IA, des orchestrateurs, des outils CLI, des services internes, des pipelines CI/CD et des produits SaaS connectés à de multiples fournisseurs externes.

Dans ce contexte, un Secret Manager moderne doit résoudre un problème central : permettre à des acteurs humains et machines d'accéder aux secrets dont ils ont besoin, au bon moment, avec le minimum de privilèges, tout en gardant une traçabilité fiable et une gouvernance lisible.

Le backend de MCP Secret Manager porte la logique métier, la sécurité, l'architecture Clean Architecture, l'API REST, le serveur MCP, le chiffrement, l'audit et les règles d'autorisation. Le frontend doit, lui, rendre cette puissance administrable. Il doit transformer des concepts sensibles comme vault, projet, secret, version, acteur, rôle, permission, token et événement d'audit en une expérience cohérente, rapide et rassurante.

L'ambition est de créer une application SaaS premium, même dans un contexte auto-hébergé ou open source. L'utilisateur doit ressentir que le produit est sérieux, précis, fiable et agréable à utiliser. L'interface doit être assez simple pour un développeur indépendant, assez claire pour une startup, assez structurée pour une PME, assez rigoureuse pour une équipe DevOps et assez extensible pour préparer des usages Enterprise.

MCP Secret Manager existe parce que les environnements modernes déplacent la frontière de sécurité. Dans une architecture IA et MCP, un agent peut appeler des outils, lire du contexte, déclencher des workflows, manipuler des credentials ou agir pour le compte d'un utilisateur. Un secret exposé trop largement peut compromettre un fournisseur cloud, un dépôt de code, une base de données, une infrastructure SaaS ou une chaîne d'automatisation complète.

La valeur du frontend est donc de rendre cette frontière visible. L'interface doit aider à répondre rapidement à des questions critiques :

- quels secrets existent ;
- dans quels vaults et projets ils sont organisés ;
- quels acteurs peuvent y accéder ;
- quelles permissions sont accordées ;
- quelles clés API sont actives ;
- quels secrets ont été lus, modifiés ou versionnés ;
- quelles actions sensibles ont eu lieu ;
- quels éléments nécessitent une revue ou une correction ;
- quelles configurations augmentent ou réduisent le risque.

Un Secret Manager moderne est utile dans un contexte IA parce qu'il évite de donner aux agents un accès implicite, global ou permanent à des credentials sensibles. Il permet de structurer les accès, de limiter les permissions, de tracer les demandes et de préparer des contrôles plus avancés comme les identités d'agents, les accès temporaires, les budgets de lecture, les approbations humaines ou les politiques contextuelles.

Il est utile dans un contexte DevOps parce qu'il centralise la gestion des secrets utilisés par les environnements, les services, les pipelines, les scripts et les containers. Il réduit la dépendance aux fichiers dispersés, aux variables d'environnement difficiles à auditer et aux secrets stockés dans des lieux non prévus pour cela.

Il est utile dans un contexte SaaS parce qu'il apporte une interface de gouvernance : administration multi-utilisateur, séparation des responsabilités, audit, gestion des clés, préparation au billing, organisation par projets, expérience de support et évolutivité vers des plans Enterprise.

Il est utile dans un contexte MCP parce qu'il fournit une couche dédiée entre les serveurs MCP, les agents et les secrets. MCP Secret Manager doit être perçu comme le composant naturel pour administrer les credentials utilisés par des outils MCP sans exposer inutilement les valeurs sensibles.

La vision produit du frontend est donc la suivante : offrir une application d'administration élégante, rapide, lisible et sécurisée, permettant de gérer les secrets d'infrastructures IA et DevOps avec la confiance d'un produit Enterprise et la simplicité d'un outil pensé pour des équipes modernes.

# Objectifs

Le frontend doit poursuivre des objectifs produit, UX, sécurité et techniques cohérents. Ces objectifs serviront de critères d'arbitrage pendant tout le développement.

## Simplicité

L'interface doit rendre des concepts de sécurité complexes compréhensibles sans les simplifier au point de devenir dangereux.

La simplicité recherchée n'est pas une absence de profondeur. Elle consiste à présenter les bonnes informations au bon moment, à organiser les workflows de manière naturelle et à éviter les écrans surchargés. Un utilisateur doit pouvoir créer un vault, organiser un projet, ajouter un secret, générer une clé API, vérifier les permissions et consulter l'audit sans lire la documentation complète du backend.

La navigation doit être prévisible. Les objets principaux doivent être faciles à retrouver. Les actions principales doivent être évidentes. Les détails avancés doivent rester accessibles sans envahir l'expérience quotidienne.

## Rapidité

L'application doit donner une impression immédiate de réactivité.

La gestion de secrets est souvent liée à des situations opérationnelles : mise en production, incident, révocation, configuration d'un service, onboarding d'un nouvel outil, audit de sécurité ou intégration d'un agent. Dans ces moments, l'utilisateur ne doit pas subir une interface lente ou confuse.

Les vues principales doivent se charger rapidement. Les transitions doivent être fluides. Les listes doivent rester utilisables avec un volume raisonnable de vaults, projets, secrets, versions, clés API et événements d'audit. Les filtres, recherches et changements d'état doivent produire un feedback immédiat.

## Sécurité

Le frontend doit renforcer le modèle de sécurité du backend au lieu de le diluer.

L'interface doit être conçue avec une posture de refus par défaut, de moindre privilège et de protection contre les fuites accidentelles. Elle ne doit jamais banaliser l'affichage d'une valeur secrète. Elle doit distinguer clairement les métadonnées d'un secret et sa valeur. Elle doit confirmer les actions sensibles et rendre les conséquences compréhensibles.

La sécurité doit aussi être visible. L'utilisateur doit comprendre quelles ressources sont actives, verrouillées, archivées, révoquées, limitées ou exposées à des permissions particulières. Les états critiques doivent être lisibles sans dramatisation inutile.

## Expérience premium

MCP Secret Manager doit donner l'impression d'un produit mature.

Une expérience premium se caractérise par de la précision, de la cohérence, une densité d'information maîtrisée, des micro-interactions utiles, une hiérarchie visuelle claire, une typographie soignée, des états vides bien pensés, des messages d'erreur actionnables et une absence de friction inutile.

Le produit doit être agréable à utiliser au quotidien. L'utilisateur doit sentir que l'interface respecte son temps, son attention et la criticité de ses données.

## Accessibilité

L'application doit être accessible dès le MVP.

L'accessibilité ne doit pas être traitée comme une amélioration tardive. Les contrastes, la navigation clavier, les états de focus, les libellés explicites, les messages d'erreur, les composants interactifs, les tableaux et les formulaires doivent être pensés pour une utilisation robuste par un large public.

Un produit de sécurité doit être particulièrement attentif à l'accessibilité : une action mal comprise, un bouton ambigu, un contraste insuffisant ou une erreur peu visible peut avoir des conséquences opérationnelles réelles.

## Confiance

L'objectif le plus important du frontend est d'inspirer confiance.

Cette confiance vient de plusieurs dimensions :

- exactitude des informations affichées ;
- cohérence entre l'interface et les règles backend ;
- absence d'ambiguïté sur les permissions ;
- clarté des actions sensibles ;
- traçabilité visible ;
- messages d'erreur sûrs et utiles ;
- expérience stable ;
- design sobre et professionnel.

L'utilisateur doit avoir le sentiment que le produit protège activement son infrastructure, sans le ralentir.

# Public cible

MCP Secret Manager doit pouvoir servir plusieurs types d'utilisateurs. Le frontend doit être conçu pour couvrir leurs besoins sans fragmenter l'expérience.

## Développeur indépendant

Le développeur indépendant utilise MCP Secret Manager pour sécuriser ses propres projets, agents, scripts, environnements locaux ou serveurs personnels.

Ses besoins principaux sont :

- centraliser les secrets dispersés dans plusieurs projets ;
- remplacer progressivement les fichiers de configuration sensibles ;
- connecter des outils personnels ou des agents IA ;
- comprendre rapidement ce qui est stocké ;
- générer une clé API pour un script ou un service ;
- révoquer un accès sans complexité ;
- auto-héberger facilement ;
- garder une interface légère et rapide.

Ce persona recherche une expérience simple, directe et peu intimidante. Il n'a pas forcément besoin de processus Enterprise, mais il veut éviter les erreurs dangereuses. Il apprécie les états vides guidés, les workflows courts, les labels clairs et une interface qui ne suppose pas l'existence d'une grande équipe.

## Startup

Une startup utilise MCP Secret Manager pour organiser les secrets de ses premiers produits, environnements et services internes.

Ses besoins principaux sont :

- séparer les secrets par projet, produit ou environnement ;
- gérer les accès entre développeurs, services et outils ;
- auditer les actions sensibles ;
- faciliter l'onboarding de nouveaux membres ;
- limiter les risques liés à une croissance rapide ;
- conserver une expérience suffisamment simple pour éviter les contournements ;
- préparer une montée en maturité sécurité.

Ce persona a besoin d'un équilibre entre simplicité et gouvernance. L'interface doit permettre d'aller vite, mais aussi d'établir de bonnes pratiques avant que l'organisation ne devienne trop complexe.

## PME

Une PME utilise MCP Secret Manager comme composant d'administration pour plusieurs applications, équipes ou clients internes.

Ses besoins principaux sont :

- structurer les secrets par domaines métier ;
- contrôler les rôles et permissions ;
- disposer d'un audit exploitable ;
- réduire la dépendance aux connaissances individuelles ;
- standardiser la gestion des clés API ;
- documenter les accès ;
- préparer des exigences de conformité ou de sécurité interne.

Ce persona recherche une interface fiable, compréhensible par plusieurs profils et capable de réduire les risques opérationnels. La lisibilité des statuts, des permissions et des logs est particulièrement importante.

## Équipe DevOps

Une équipe DevOps utilise MCP Secret Manager pour administrer les secrets nécessaires aux environnements, pipelines, déploiements, containers, services internes et outils d'infrastructure.

Ses besoins principaux sont :

- consulter rapidement l'état global du système ;
- organiser les secrets par vault, projet, environnement ou service ;
- gérer les clés API de comptes de service ;
- vérifier qui accède à quoi ;
- révoquer rapidement un token ;
- analyser les événements d'audit ;
- détecter les accès inhabituels ;
- préparer la rotation et les intégrations futures.

Ce persona attend une interface dense, efficace et orientée opération. Les tableaux, filtres, recherches, états, raccourcis de navigation et actions rapides sont essentiels. L'interface ne doit pas ressembler à une page marketing, mais à un outil de travail précis.

## Équipe IA

Une équipe IA utilise MCP Secret Manager pour contrôler les secrets consommés par des agents, serveurs MCP, orchestrateurs, outils d'évaluation, environnements de test et applications agentiques.

Ses besoins principaux sont :

- limiter les secrets accessibles aux agents ;
- comprendre quelles identités techniques sont utilisées ;
- isoler les accès par agent, outil ou projet ;
- auditer les lectures de secrets ;
- éviter les accès bulk ;
- préparer des politiques plus contextuelles ;
- réduire les risques liés aux prompt injections ;
- connecter MCP Secret Manager à des workflows MCP.

Ce persona a besoin que l'interface rende visibles les risques propres aux agents : identité, contexte, permission, fréquence d'accès, refus, historique et révocation. Même si toutes les protections avancées ne sont pas dans le MVP, le frontend doit préparer mentalement cette évolution.

## Entreprise

Une entreprise utilise MCP Secret Manager dans un contexte de gouvernance, conformité, séparation des responsabilités, intégrations cloud, monitoring, audit et gestion multi-équipes.

Ses besoins principaux sont :

- gérer plusieurs équipes ou unités organisationnelles ;
- appliquer des politiques strictes ;
- intégrer le produit avec des systèmes existants ;
- exporter ou connecter les logs d'audit ;
- gérer le cycle de vie des accès ;
- utiliser SSO, annuaires, rôles avancés et approbations ;
- disposer d'une traçabilité complète ;
- bénéficier de garanties de support, monitoring et reporting.

Ce persona dépasse largement le MVP, mais il influence la vision produit. Le frontend doit être conçu avec une architecture d'information capable d'accueillir des vues Enterprise futures sans refonte majeure.

# Proposition de valeur

MCP Secret Manager expose une API, mais le frontend apporte une valeur distincte. Une API permet l'intégration. Une interface graphique permet la compréhension, la gouvernance, la décision et l'administration humaine.

Utiliser uniquement une API oblige l'utilisateur à connaître les endpoints, les permissions, les identifiants, les structures de données, les états possibles et les workflows. Cela convient aux machines, aux scripts et aux intégrations, mais cela ne suffit pas pour administrer durablement un système sensible.

Le frontend apporte une couche de lisibilité au-dessus du domaine métier. Il permet de voir l'organisation des secrets, les relations entre vaults, projets, secrets, versions, clés API, rôles et audit logs. Il réduit la charge cognitive en transformant des opérations techniques en parcours cohérents.

La proposition de valeur principale est la suivante : offrir une console d'administration sécurisée qui rend la gestion des secrets compréhensible, rapide et fiable pour les humains, tout en respectant strictement les garanties du backend.

## Bénéfices d'une interface graphique

L'interface graphique apporte plusieurs bénéfices clés.

Elle améliore la découverte. Un utilisateur peut comprendre les concepts du produit en explorant l'application, sans devoir lire immédiatement toute la documentation API.

Elle améliore la supervision. Le dashboard, les listes, les statuts, les compteurs et les logs rendent l'état du système visible.

Elle améliore la sécurité opérationnelle. Les confirmations, avertissements, états verrouillés, badges de risque, distinctions metadata/value et historiques réduisent les erreurs humaines.

Elle améliore la collaboration. Plusieurs profils peuvent partager une compréhension commune des vaults, projets, secrets, permissions et événements.

Elle accélère les actions courantes. Créer un secret, consulter une version, révoquer une clé API, vérifier un rôle ou filtrer l'audit doit être plus rapide que composer manuellement des appels API.

Elle rend l'audit exploitable. Une liste brute d'événements n'est pas suffisante. L'interface doit permettre de filtrer, comprendre, contextualiser et enquêter.

Elle prépare la montée en gamme. Les fonctionnalités futures comme le multi-tenant, les intégrations cloud, le monitoring, l'analytics, le billing, le KMS ou le HSM nécessitent une console d'administration claire.

## Différenciation produit

MCP Secret Manager ne doit pas être perçu comme une simple base de secrets chiffrés. Il doit être perçu comme une couche de contrôle pour infrastructures modernes.

Sa différenciation repose sur :

- une orientation IA-first ;
- une compatibilité MCP-native ;
- une expérience frontend pensée pour l'administration ;
- une séparation claire entre métadonnées et valeurs secrètes ;
- une gouvernance adaptée aux acteurs humains et machines ;
- un modèle de moindre privilège ;
- une traçabilité visible ;
- une approche progressive entre MVP simple et ambition Enterprise.

Le frontend doit exprimer cette différenciation sans discours marketing envahissant. Le produit doit prouver sa valeur par sa clarté, sa précision et sa capacité à rendre les workflows sensibles plus sûrs.

# Fonctionnalités MVP

Le MVP doit fournir une console d'administration complète pour les ressources déjà structurantes du backend. Il ne doit pas chercher à couvrir toutes les ambitions Enterprise, mais il doit être réellement utilisable pour administrer un Secret Manager en production limitée ou en environnement de développement sérieux.

Les fonctionnalités MVP doivent respecter plusieurs règles générales :

- aucune lecture massive de valeurs secrètes ;
- distinction permanente entre métadonnées et valeur ;
- actions sensibles confirmées ;
- erreurs affichées sans fuite d'information sensible ;
- permissions visibles lorsque cela aide la décision ;
- audit des opérations sensibles mis en avant ;
- workflows courts pour les tâches fréquentes ;
- expérience responsive dès la première version.

## Dashboard

Objectif :

Le dashboard fournit une vue synthétique de l'état du Secret Manager. Il doit permettre à l'utilisateur de comprendre rapidement l'activité récente, les ressources principales, les accès sensibles et les éléments demandant attention.

Utilisateur concerné :

Le dashboard concerne principalement les administrateurs, les équipes DevOps, les responsables techniques, les équipes IA et les utilisateurs avancés. Il doit aussi rester compréhensible pour un développeur indépendant.

Bénéfice :

Le dashboard réduit le temps nécessaire pour évaluer l'état du système. Il donne une vision immédiate des vaults actifs, projets, secrets, clés API, événements récents, actions sensibles et éventuels signaux de risque.

Contenu attendu au MVP :

- résumé du nombre de vaults ;
- résumé du nombre de projets ;
- résumé du nombre de secrets ;
- résumé du nombre de clés API ou tokens actifs ;
- activité récente ;
- derniers événements d'audit sensibles ;
- accès rapides vers vaults, secrets, API keys et audit logs ;
- indicateurs d'état simples ;
- états vides utiles lorsque l'instance vient d'être installée.

Le dashboard ne doit pas devenir une page décorative. Il doit être une surface opérationnelle, conçue pour scanner rapidement l'information.

## Vaults

Objectif :

La section Vaults permet de gérer les grands conteneurs logiques et de sécurité du produit. Un vault représente une frontière importante pour l'organisation, la séparation et potentiellement la politique de protection des secrets.

Utilisateur concerné :

Administrateurs, DevOps, équipes IA, startups, PME et entreprises.

Bénéfice :

Les vaults permettent de structurer les secrets par domaine, environnement, client, équipe, produit ou niveau de sensibilité. Ils rendent l'organisation plus lisible et préparent des politiques de sécurité plus strictes.

Fonctionnalités attendues au MVP :

- lister les vaults ;
- créer un vault ;
- consulter les métadonnées d'un vault ;
- modifier les métadonnées autorisées ;
- afficher l'état du vault ;
- verrouiller un vault si le backend expose cet état ;
- archiver un vault si le workflow est disponible ;
- afficher les projets associés ;
- accéder rapidement aux secrets contenus via les projets ;
- indiquer les restrictions ou permissions pertinentes.

L'interface doit éviter de présenter un vault comme un simple dossier. Il s'agit d'une ressource de sécurité. Les actions comme verrouiller, archiver ou modifier doivent être traitées comme sensibles.

## Projects

Objectif :

La section Projects permet d'organiser les secrets à l'intérieur d'un vault. Un projet représente un regroupement logique lié à une application, un service, un environnement, une équipe ou un usage.

Utilisateur concerné :

Développeurs, équipes produit, DevOps, équipes IA, PME et startups.

Bénéfice :

Les projets évitent l'accumulation de secrets dans un espace plat. Ils facilitent la recherche, la gestion des permissions, l'audit contextuel et l'intégration avec des services consommateurs.

Fonctionnalités attendues au MVP :

- lister les projets d'un vault ;
- créer un projet ;
- consulter les métadonnées d'un projet ;
- modifier les informations autorisées ;
- archiver un projet ;
- afficher les secrets associés ;
- afficher les informations de contexte utiles ;
- fournir des raccourcis vers les clés API ou audit logs liés au projet lorsque disponible.

L'expérience doit rendre claire la relation entre vault et projet. L'utilisateur doit toujours savoir où il se trouve dans la hiérarchie.

## Secrets

Objectif :

La section Secrets permet de gérer l'identité logique et les métadonnées des secrets, sans confondre cette gestion avec la consultation de la valeur secrète.

Utilisateur concerné :

Développeurs, DevOps, équipes IA, administrateurs et utilisateurs techniques.

Bénéfice :

La gestion des secrets devient structurée, traçable et moins risquée que des fichiers dispersés. L'utilisateur peut créer, nommer, classer, retrouver, mettre à jour et archiver des secrets sans exposer inutilement leurs valeurs.

Fonctionnalités attendues au MVP :

- lister les secrets d'un projet ;
- rechercher un secret par nom ou métadonnées disponibles ;
- créer un secret ;
- consulter les métadonnées ;
- modifier les métadonnées autorisées ;
- archiver ou supprimer logiquement un secret selon le modèle backend ;
- identifier la version courante ;
- accéder à l'historique des versions ;
- afficher les informations de sécurité pertinentes ;
- déclencher une consultation ponctuelle de la valeur si l'utilisateur possède la permission requise.

La valeur du secret ne doit jamais être affichée par défaut. Une action volontaire, explicite et auditée doit être nécessaire pour révéler ou copier une valeur. L'interface doit limiter les risques d'exposition visuelle accidentelle.

## Secret Versions

Objectif :

La section Secret Versions permet de consulter et gérer l'historique des versions d'un secret. Elle matérialise l'idée qu'une valeur secrète évolue dans le temps sans écraser son historique métier.

Utilisateur concerné :

DevOps, développeurs, administrateurs, équipes sécurité, équipes IA.

Bénéfice :

Les versions permettent de comprendre l'évolution d'un secret, d'identifier la version courante, de préparer des rotations manuelles et de tracer les changements. Elles réduisent l'opacité autour des modifications sensibles.

Fonctionnalités attendues au MVP :

- afficher la liste des versions d'un secret ;
- distinguer clairement la version courante ;
- consulter les métadonnées d'une version ;
- créer une nouvelle version ;
- voir les informations de création et d'état ;
- accéder à la valeur d'une version uniquement si autorisé ;
- éviter toute modification directe d'une version existante si le modèle backend impose l'immutabilité ;
- afficher les événements d'audit associés lorsque disponible.

L'interface doit expliquer par sa structure qu'une version est un artefact sensible et immuable. Modifier un secret signifie créer une nouvelle version, pas altérer silencieusement l'existant.

## API Keys

Objectif :

La section API Keys permet de gérer les tokens ou clés d'accès utilisés par les clients techniques, scripts, services, CLI, OpenClaw, serveurs MCP ou applications internes.

Utilisateur concerné :

Administrateurs, DevOps, développeurs, équipes IA et responsables sécurité.

Bénéfice :

Les API Keys rendent les accès machines explicites, révocables et auditables. Elles évitent l'utilisation de credentials admin pour des services automatisés.

Fonctionnalités attendues au MVP :

- lister les clés API ou tokens disponibles ;
- créer une clé API ;
- associer une clé à un acteur ou compte de service ;
- afficher l'état actif ou révoqué ;
- afficher la date de création ;
- afficher la dernière utilisation si disponible ;
- révoquer une clé ;
- afficher les permissions ou rôles associés ;
- présenter la valeur de la clé uniquement au moment de sa création si le modèle backend le prévoit ;
- avertir clairement que la valeur complète ne sera pas récupérable ensuite si cette règle est appliquée.

La création et la révocation d'une clé API sont des moments de sécurité importants. L'interface doit être claire, sobre et explicite sur les conséquences.

## Audit Logs

Objectif :

La section Audit Logs permet de consulter l'historique des actions sensibles. Elle doit rendre les événements exploitables pour l'enquête, la supervision et la conformité interne.

Utilisateur concerné :

Administrateurs, équipes DevOps, équipes sécurité, responsables techniques, équipes IA.

Bénéfice :

Les audit logs permettent de répondre aux questions critiques : qui a fait quoi, quand, sur quelle ressource, avec quel résultat et depuis quel type d'acteur. Ils renforcent la confiance dans le système et facilitent la réaction en cas d'incident.

Fonctionnalités attendues au MVP :

- lister les événements d'audit ;
- filtrer par période ;
- filtrer par acteur ;
- filtrer par ressource ;
- filtrer par type d'action ;
- filtrer par résultat lorsque disponible ;
- consulter le détail d'un événement ;
- distinguer les lectures de métadonnées des lectures de valeurs ;
- mettre en évidence les refus d'autorisation ;
- fournir des liens contextuels vers vault, projet, secret ou clé concernée lorsque possible.

Les logs ne doivent jamais afficher de valeur secrète. L'interface doit rester utile sans exposer de données sensibles.

## RBAC

Objectif :

La section RBAC permet de comprendre et gérer les rôles, permissions et affectations d'accès. Elle traduit le modèle d'autorisation du backend en expérience administrable.

Utilisateur concerné :

Administrateurs, équipes DevOps, PME, entreprises, responsables sécurité.

Bénéfice :

RBAC réduit le risque d'accès excessif. Il permet de définir qui peut lire, créer, modifier, administrer ou auditer les ressources.

Fonctionnalités attendues au MVP :

- afficher les rôles disponibles ;
- afficher les permissions associées ;
- affecter un rôle à un acteur si le backend le permet ;
- retirer un rôle ;
- distinguer utilisateurs humains et comptes de service lorsque disponible ;
- afficher les permissions effectives dans les contextes critiques ;
- éviter les modifications ambiguës ;
- confirmer les changements d'autorisation sensibles.

L'interface RBAC doit être particulièrement lisible. Une permission mal comprise est un risque de sécurité. Les libellés doivent exprimer clairement l'action autorisée et son périmètre.

## Profil utilisateur

Objectif :

La section Profil utilisateur permet à l'utilisateur connecté de consulter ses informations, son identité applicative et certains paramètres personnels.

Utilisateur concerné :

Tous les utilisateurs humains.

Bénéfice :

Le profil renforce la clarté sur l'identité active. Il permet d'éviter les erreurs liées à une confusion de compte, d'organisation ou de rôle.

Fonctionnalités attendues au MVP :

- afficher les informations du compte ;
- afficher le rôle ou les permissions principales lorsque pertinent ;
- afficher les préférences personnelles disponibles ;
- permettre la gestion de paramètres d'affichage comme le thème si pris en charge ;
- fournir un accès aux informations de sécurité du compte lorsque disponible ;
- permettre la déconnexion.

Le profil ne doit pas devenir une zone de configuration générale. Il doit rester centré sur l'utilisateur courant.

## Paramètres

Objectif :

La section Paramètres permet d'administrer la configuration globale accessible depuis le frontend.

Utilisateur concerné :

Administrateurs, DevOps, responsables techniques.

Bénéfice :

Les paramètres centralisent les options structurantes et évitent que l'utilisateur ne cherche des configurations critiques dans plusieurs endroits.

Fonctionnalités attendues au MVP :

- afficher les informations générales de l'instance ;
- afficher les paramètres de sécurité disponibles ;
- afficher les informations d'environnement utiles sans exposer de secrets ;
- configurer les options frontend autorisées ;
- préparer l'accueil de futures sections Enterprise ;
- fournir des accès vers la documentation ou les informations système si pertinent.

Les paramètres doivent être sobres et prudents. Toute modification sensible doit être confirmée. Les valeurs confidentielles ne doivent jamais être exposées.

# Fonctionnalités futures

Les fonctionnalités futures correspondent aux ambitions moyen terme et Enterprise. Elles ne doivent pas surcharger le MVP, mais elles doivent être anticipées dans l'architecture d'information et les principes d'interface.

## Rotation automatique

La rotation automatique permettra de renouveler des secrets selon une fréquence, un événement ou une politique.

Valeur attendue :

- réduire la durée de vie des credentials ;
- limiter l'impact d'une fuite ;
- standardiser les pratiques de sécurité ;
- automatiser les opérations répétitives ;
- fournir un historique clair des rotations.

Le frontend devra permettre de configurer des règles, visualiser les prochaines rotations, consulter les échecs, déclencher une rotation manuelle et comprendre les dépendances.

## Webhooks

Les webhooks permettront de notifier des systèmes externes lorsqu'un événement se produit.

Valeur attendue :

- connecter MCP Secret Manager à des workflows existants ;
- déclencher des automatisations ;
- informer des outils CI/CD, monitoring ou incident management ;
- synchroniser certains états.

Le frontend devra gérer les endpoints, secrets de signature, événements abonnés, tentatives, erreurs et statuts.

## Notifications

Les notifications permettront d'alerter les utilisateurs sur des actions, risques ou échéances.

Valeur attendue :

- prévenir d'une clé bientôt expirée ;
- signaler une révocation ;
- alerter sur des refus répétés ;
- informer d'une rotation échouée ;
- améliorer la surveillance proactive.

Le frontend devra proposer des préférences, canaux, niveaux de criticité et historiques.

## Multi-tenant

Le multi-tenant permettra de gérer plusieurs organisations, espaces clients, équipes ou environnements isolés.

Valeur attendue :

- adapter le produit à des usages SaaS ;
- isoler les ressources ;
- gérer plusieurs clients ou business units ;
- préparer le billing et les plans ;
- renforcer la gouvernance.

Le frontend devra rendre le changement de tenant explicite, éviter les confusions de contexte et afficher clairement l'organisation active.

## Intégrations Cloud

Les intégrations cloud permettront de connecter MCP Secret Manager à des fournisseurs comme AWS, Google Cloud, Azure, Cloudflare ou d'autres services.

Valeur attendue :

- importer ou synchroniser certains secrets ;
- utiliser des identités cloud ;
- préparer des secrets dynamiques ;
- rapprocher le produit des workflows d'infrastructure.

Le frontend devra présenter les intégrations de manière sûre, avec états de connexion, permissions demandées, erreurs, dernière synchronisation et actions de révocation.

## Monitoring

Le monitoring permettra de suivre la santé opérationnelle du système.

Valeur attendue :

- détecter les anomalies ;
- suivre les erreurs ;
- visualiser les performances ;
- surveiller les accès ;
- faciliter l'exploitation en production.

Le frontend devra fournir des vues utiles sans devenir un outil d'observabilité complet. Il pourra mettre en avant les métriques critiques liées à la sécurité, à la disponibilité et aux opérations.

## KMS

L'intégration KMS permettra d'utiliser des services de gestion de clés externes.

Valeur attendue :

- renforcer la séparation des responsabilités cryptographiques ;
- répondre à des exigences Enterprise ;
- s'intégrer à des politiques de sécurité existantes ;
- améliorer le contrôle sur les clés de chiffrement.

Le frontend devra afficher le provider KMS, l'état de connexion, les erreurs, les politiques associées et les impacts sur les vaults.

## HSM

L'intégration HSM permettra de s'appuyer sur du matériel ou des services spécialisés pour protéger les clés.

Valeur attendue :

- renforcer le niveau de sécurité ;
- répondre à des contraintes réglementaires ;
- limiter l'exposition des clés maîtres ;
- préparer des déploiements critiques.

Le frontend devra rester très clair sur les états, contraintes et limites, car une mauvaise configuration HSM peut bloquer des opérations sensibles.

## Analytics

Les analytics permettront de comprendre l'usage du Secret Manager.

Valeur attendue :

- identifier les secrets les plus consultés ;
- repérer les ressources inutilisées ;
- visualiser les tendances d'accès ;
- aider à réduire les permissions excessives ;
- améliorer la gouvernance.

Les analytics ne doivent jamais exposer de valeurs secrètes. Ils doivent se concentrer sur les métadonnées, volumes, tendances et événements.

## Billing

Le billing permettra de gérer les plans, quotas, usage facturable et informations de paiement dans un contexte SaaS.

Valeur attendue :

- soutenir un modèle commercial ;
- gérer les limites de plan ;
- suivre l'utilisation ;
- permettre des offres team, pro ou enterprise ;
- connecter le produit à une expérience SaaS complète.

Le frontend devra intégrer le billing sans polluer les workflows de sécurité. Les limites commerciales doivent être expliquées clairement, sans empêcher la compréhension des risques.

## SSO et annuaires

Les intégrations SSO et annuaires permettront de connecter le produit à des fournisseurs d'identité d'entreprise.

Valeur attendue :

- centraliser l'identité ;
- simplifier l'onboarding et l'offboarding ;
- appliquer des politiques d'organisation ;
- améliorer la sécurité des comptes humains.

Le frontend devra gérer les providers, domaines autorisés, statuts de connexion et erreurs de configuration.

## Approbations humaines

Les approbations permettront d'exiger une validation avant certaines actions sensibles.

Valeur attendue :

- contrôler les lectures de secrets critiques ;
- limiter les actions d'agents ;
- ajouter un mécanisme humain dans les workflows à risque ;
- répondre à des besoins Enterprise.

Le frontend devra proposer des files d'attente, historiques, justifications, statuts et délais.

## Identités d'agents IA

Les identités d'agents permettront de représenter les agents comme des acteurs de première classe.

Valeur attendue :

- limiter les permissions par agent ;
- auditer les comportements agentiques ;
- associer des accès à des missions ou contextes ;
- réduire l'impact des prompt injections ;
- préparer des politiques adaptées aux orchestrateurs.

Le frontend devra aider les utilisateurs à comprendre qu'un agent n'est pas un simple token technique. Il s'agit d'un acteur autonome ou semi-autonome qui mérite une gouvernance spécifique.

# Principes UX

Le frontend doit être conçu comme un outil d'administration quotidien. L'expérience doit être efficace, sûre et agréable, sans surcharge décorative.

## Peu de clics

Les actions fréquentes doivent être accessibles rapidement.

Créer un secret, trouver une clé, révoquer un token, consulter l'audit d'une ressource ou accéder aux versions ne doit pas nécessiter une navigation profonde. Les parcours doivent respecter la hiérarchie du domaine, mais éviter les détours inutiles.

Les raccourcis contextuels sont importants. Depuis un secret, l'utilisateur doit pouvoir accéder à ses versions et événements. Depuis une clé API, il doit pouvoir consulter ses permissions ou événements associés. Depuis un audit log, il doit pouvoir revenir à la ressource concernée.

## Interface claire

La clarté prime sur la densité brute.

Les écrans doivent présenter une hiérarchie visuelle nette :

- titre de la vue ;
- contexte actif ;
- actions principales ;
- filtres ou recherche ;
- contenu principal ;
- états et informations secondaires ;
- actions sensibles séparées.

Les labels doivent être explicites. Les termes métier doivent être cohérents dans toute l'application. Une même action ne doit pas changer de nom selon les écrans.

## Responsive

L'application doit être utilisable sur desktop, laptop, tablette et mobile.

Le desktop reste le contexte principal pour un outil d'administration, mais le mobile peut être nécessaire pour consulter un état, révoquer rapidement un accès, vérifier un audit log ou intervenir pendant un incident.

Le responsive ne doit pas simplement empiler les éléments. Il doit préserver les priorités d'action et la lisibilité des ressources sensibles.

## Dark mode

Le dark mode doit être prévu comme une expérience de première classe.

Un produit utilisé par des développeurs, DevOps et équipes techniques sera souvent attendu en dark mode. Celui-ci doit être lisible, contrasté et professionnel. Il ne doit pas réduire la lisibilité des statuts, erreurs, avertissements ou informations de sécurité.

Le light mode doit également rester soigné. Le produit ne doit pas être conçu uniquement pour un thème.

## Cohérence

La cohérence doit couvrir la navigation, les composants, les libellés, les statuts, les confirmations, les messages d'erreur et la structure des pages.

Un utilisateur doit pouvoir apprendre un pattern une fois et le retrouver ailleurs. Par exemple, les listes de vaults, projets, secrets et API keys doivent partager des conventions communes : recherche, filtres, actions, états vides, pagination et accès aux détails.

## Feedback immédiat

Chaque action doit produire un retour clair.

Créer, modifier, archiver, révoquer, copier, révéler, filtrer ou sauvegarder doit déclencher un feedback visible. Ce feedback doit indiquer si l'action est terminée, en cours, échouée ou refusée.

Les erreurs doivent être actionnables. Elles doivent expliquer ce que l'utilisateur peut faire sans révéler d'information dangereuse.

## Confirmation des actions sensibles

Les actions sensibles doivent être confirmées.

Cela inclut notamment :

- révéler une valeur secrète ;
- copier une valeur secrète ;
- créer une clé API ;
- révoquer une clé API ;
- modifier des permissions ;
- archiver une ressource ;
- supprimer logiquement un secret ;
- verrouiller un vault ;
- modifier une configuration de sécurité.

Les confirmations doivent être proportionnées. Une action fréquente mais sensible doit rester fluide. Une action destructive ou difficilement réversible doit exiger une confirmation plus explicite.

## Prévention des erreurs

L'interface doit empêcher les erreurs plutôt que seulement les signaler après coup.

Cela passe par :

- validations en temps réel ;
- désactivation des actions impossibles ;
- messages de permission clairs ;
- états explicites ;
- séparation visuelle des actions dangereuses ;
- avertissements avant les conséquences irréversibles ;
- absence de valeurs secrètes dans les aperçus.

## Orientation contexte

L'utilisateur doit toujours comprendre le contexte actif.

Dans un produit organisé en vaults, projets, secrets et versions, la perte de contexte est dangereuse. Les breadcrumbs, titres, badges d'état et zones de contexte doivent aider l'utilisateur à savoir où il agit.

## Respect du secret

L'expérience doit constamment rappeler que les valeurs secrètes sont spéciales.

Le frontend ne doit pas traiter une valeur secrète comme un simple champ texte. Il doit limiter l'affichage, masquer par défaut, tracer les révélations, éviter les prévisualisations inutiles et réduire les risques de capture visuelle.

# Principes UI

Le style recherché est celui d'un SaaS premium, sobre, précis et technique.

Les inspirations mentionnées sont Linear, GitHub, Vercel, Infisical, Doppler et HashiCorp Vault. Le frontend ne doit jamais copier leur design, leurs composants, leurs écrans ou leur identité visuelle. Ces références servent uniquement à exprimer une philosophie : clarté, vitesse, confiance, densité maîtrisée, qualité typographique, cohérence et professionnalisme.

## Direction visuelle

L'interface doit être moderne sans être spectaculaire.

Le produit manipule des secrets. Il doit donc éviter une esthétique trop ludique, trop marketing ou trop décorative. La crédibilité vient de la sobriété, de la précision et de l'attention portée aux détails.

La direction visuelle doit évoquer :

- sécurité ;
- maîtrise ;
- clarté ;
- modernité ;
- rapidité ;
- confiance ;
- infrastructure ;
- qualité premium.

## Hiérarchie

La hiérarchie visuelle doit aider l'utilisateur à scanner rapidement l'information.

Les titres doivent être nets. Les actions principales doivent être visibles mais pas agressives. Les actions dangereuses doivent être reconnaissables. Les informations secondaires doivent être présentes sans concurrencer les informations critiques.

Les pages d'administration doivent privilégier une densité utile. Il faut éviter les grands espaces décoratifs qui réduisent la quantité d'information visible sans apporter de valeur.

## Couleurs

La palette doit être professionnelle, équilibrée et accessible.

Les couleurs doivent servir principalement à :

- distinguer les états ;
- signaler les risques ;
- guider l'attention ;
- renforcer la structure ;
- soutenir le thème light et dark.

Les couleurs de statut doivent être cohérentes :

- succès ;
- attention ;
- danger ;
- information ;
- neutre ;
- désactivé ;
- archivé ;
- révoqué ;
- verrouillé.

Le produit ne doit pas reposer sur une palette monotone ou sur des dégradés décoratifs. Les couleurs doivent rester au service de la lisibilité.

## Typographie

La typographie doit être sobre, lisible et adaptée à une application technique.

Les noms de secrets, identifiants, rôles, permissions, dates, états et chemins doivent être faciles à lire. Les tailles doivent être hiérarchisées sans excès. Les interfaces compactes doivent utiliser des titres plus mesurés que les pages d'accueil ou vues de synthèse.

La typographie doit éviter les effets visuels qui nuisent à la lisibilité. La cohérence entre listes, formulaires, modales, tableaux et pages de détail est essentielle.

## Composants

Le frontend doit s'appuyer sur un système de composants cohérent.

Composants attendus :

- navigation principale ;
- navigation contextuelle ;
- tableaux ;
- filtres ;
- recherche ;
- badges d'état ;
- formulaires ;
- modales de confirmation ;
- panneaux de détail ;
- menus d'actions ;
- alertes ;
- toasts ;
- champs sensibles ;
- vues vides ;
- loaders ;
- pagination ;
- tabs ;
- toggles ;
- boutons d'action ;
- cartes uniquement lorsque leur usage est justifié.

Les composants doivent être réutilisables, testables et cohérents. Une action comme révoquer, archiver ou révéler doit conserver le même style mental partout.

## Tables et listes

Les tables sont importantes pour un produit d'administration.

Elles doivent être lisibles, filtrables et capables d'afficher des statuts, dates, noms, acteurs et actions. Les colonnes doivent être choisies selon l'usage réel. Les actions de ligne doivent être accessibles sans créer de surcharge.

Les listes doivent prévoir :

- états de chargement ;
- états vides ;
- erreurs ;
- pagination ou chargement progressif ;
- recherche ;
- filtres ;
- tri lorsque pertinent ;
- actions rapides ;
- accès au détail.

## États sensibles

Les états sensibles doivent être immédiatement reconnaissables.

Exemples :

- clé révoquée ;
- vault verrouillé ;
- projet archivé ;
- secret supprimé logiquement ;
- permission insuffisante ;
- accès refusé ;
- valeur masquée ;
- lecture de valeur auditée ;
- erreur de configuration.

L'interface doit éviter les ambiguïtés. Un utilisateur ne doit pas confondre une ressource inactive, archivée, verrouillée ou supprimée.

## Modales et confirmations

Les modales doivent être utilisées pour les décisions qui exigent une attention particulière, pas pour toutes les interactions.

Une confirmation sensible doit inclure :

- action concernée ;
- ressource concernée ;
- conséquence principale ;
- possibilité d'annuler ;
- bouton d'action clair ;
- niveau de gravité visuel.

Les messages doivent être concis, mais jamais vagues.

## États vides

Les états vides doivent aider l'utilisateur à démarrer.

Un vault sans projet, un projet sans secret, une instance sans audit logs ou une liste sans résultat filtré ne doivent pas être des impasses. L'interface doit proposer une prochaine action claire lorsque l'utilisateur a les permissions nécessaires.

## Premium sans imitation

Les inspirations produit doivent rester philosophiques.

Linear inspire la clarté, la vitesse et la rigueur des workflows.

GitHub inspire la familiarité des interfaces développeur, la densité maîtrisée et la lisibilité des historiques.

Vercel inspire la qualité perçue, la précision des détails et la fluidité SaaS.

Infisical et Doppler inspirent la spécialisation secret management, la pédagogie des concepts et les workflows de credentials.

HashiCorp Vault inspire la rigueur sécurité, la profondeur Enterprise et la crédibilité infrastructure.

MCP Secret Manager doit construire sa propre identité : plus orientée IA, MCP, agents, OpenClaw et administration claire de secrets modernes.

# Objectifs techniques

Le frontend doit être construit avec une base technique robuste, maintenable et évolutive. Même si ce document ne définit aucun choix d'implémentation, il fixe les objectifs qui guideront les futurs documents techniques.

## Performance

L'application doit être rapide au chargement et réactive à l'usage.

Objectifs :

- temps de chargement initial maîtrisé ;
- navigation fluide entre vues ;
- listes performantes ;
- filtres et recherches réactifs ;
- états de chargement non bloquants ;
- limitation des appels inutiles ;
- gestion propre des erreurs réseau ;
- expérience acceptable même sur une machine de développement modeste.

La performance est un facteur de confiance. Une interface de sécurité lente peut pousser les utilisateurs à contourner le produit.

## Maintenabilité

Le code frontend devra être organisé de manière claire, cohérente avec le domaine et facile à faire évoluer.

Objectifs :

- séparation nette entre pages, composants, logique de données et modèles d'affichage ;
- conventions de nommage stables ;
- composants réutilisables ;
- limitation de la duplication ;
- documentation suffisante des décisions structurantes ;
- tests adaptés aux risques ;
- absence de logique métier sensible réinventée côté frontend.

Le frontend doit refléter le domaine sans dupliquer les règles d'autorisation critiques du backend.

## Évolutivité

L'application doit pouvoir évoluer du MVP vers une offre plus complète.

Objectifs :

- accueillir de nouvelles ressources ;
- ajouter des vues Enterprise ;
- supporter le multi-tenant ;
- intégrer de futurs providers ;
- faire évoluer RBAC ;
- ajouter monitoring, analytics et billing ;
- gérer davantage de volumes ;
- permettre des parcours avancés sans refonte de navigation.

L'architecture d'information doit donc être pensée avec une marge d'évolution.

## Accessibilité technique

L'accessibilité doit être intégrée aux composants et aux workflows.

Objectifs :

- navigation clavier ;
- focus visible ;
- contrastes suffisants ;
- labels explicites ;
- messages d'erreur reliés aux champs ;
- composants interactifs utilisables par lecteurs d'écran ;
- tableaux structurés ;
- modales accessibles ;
- absence de dépendance exclusive à la couleur.

La sécurité et l'accessibilité se renforcent mutuellement : une interface plus compréhensible réduit les erreurs.

## Composants réutilisables

Le frontend doit créer un socle de composants réutilisables pour les futures vues.

Objectifs :

- éviter que chaque page réinvente ses propres formulaires ;
- standardiser les confirmations sensibles ;
- standardiser les champs de secrets ;
- standardiser les badges d'état ;
- standardiser les tables de ressources ;
- standardiser les messages d'erreur ;
- standardiser les états vides ;
- faciliter les tests.

Les composants de sécurité doivent être particulièrement cohérents. Révéler une valeur secrète, confirmer une révocation ou afficher une permission doit suivre des conventions fortes.

## Fiabilité des données

Le frontend doit représenter fidèlement l'état retourné par le backend.

Objectifs :

- éviter les états optimistes dangereux pour les actions sensibles ;
- rafraîchir les données après mutations critiques ;
- gérer les conflits ;
- afficher les erreurs d'autorisation clairement ;
- ne pas masquer les échecs ;
- ne pas présenter comme réussie une action incertaine ;
- éviter les incohérences entre vues.

Pour les actions sensibles, la vérité doit rester le backend.

## Sécurité frontend

Le frontend doit limiter les risques propres à l'interface.

Objectifs :

- ne pas stocker inutilement de valeurs secrètes ;
- masquer les valeurs par défaut ;
- éviter les fuites dans logs navigateur ;
- éviter les valeurs sensibles dans URLs ;
- contrôler les durées d'affichage ;
- limiter les copies accidentelles ;
- gérer l'expiration de session ;
- afficher les permissions sans surexposer les détails inutiles ;
- respecter les décisions backend.

Le frontend ne doit jamais donner une illusion de sécurité indépendante du backend. Il doit renforcer les protections existantes.

## Testabilité

Les workflows critiques doivent pouvoir être testés.

Objectifs :

- tester la création de ressources ;
- tester les états vides ;
- tester les erreurs d'autorisation ;
- tester les confirmations ;
- tester les actions sensibles ;
- tester les vues responsive ;
- tester les composants de champs secrets ;
- tester les filtres d'audit ;
- tester les états de chargement et d'erreur.

Le niveau de test doit être proportionné au risque. Les workflows liés aux secrets, clés API, permissions et audit sont prioritaires.

# Hors périmètre

Le MVP doit rester concentré. Certaines fonctionnalités importantes seront volontairement exclues de la première version afin de protéger la qualité, la sécurité et la vitesse de livraison.

Les éléments suivants sont hors périmètre du MVP frontend :

- rotation automatique des secrets ;
- webhooks configurables ;
- notifications utilisateur avancées ;
- multi-tenant complet ;
- gestion d'organisations multiples ;
- intégrations cloud natives ;
- intégration KMS externe ;
- intégration HSM ;
- analytics avancés ;
- billing ;
- plans commerciaux ;
- SSO Enterprise ;
- annuaires utilisateurs ;
- SCIM ;
- politiques contextuelles avancées ;
- permissions conditionnelles ;
- approbations humaines ;
- identités d'agents IA de première classe ;
- quotas de lecture ;
- budgets d'utilisation par agent ;
- détection d'anomalies ;
- export SIEM avancé ;
- monitoring complet ;
- sauvegarde et restauration depuis l'interface ;
- marketplace d'intégrations ;
- gestion avancée de providers externes ;
- secrets dynamiques ;
- workflows de conformité avancés ;
- personnalisation poussée de marque ;
- application mobile native ;
- mode hors ligne ;
- édition collaborative temps réel ;
- import massif de secrets ;
- export massif de valeurs secrètes ;
- affichage bulk de valeurs secrètes ;
- automatisations visuelles complexes ;
- console de requêtes ou explorateur API intégré.

Certaines exclusions sont temporaires, d'autres sont des limites volontaires pour des raisons de sécurité. En particulier, l'absence d'affichage bulk de valeurs secrètes doit être considérée comme un choix de sécurité, pas comme un manque fonctionnel.

Le MVP doit privilégier :

- administration claire des ressources principales ;
- gestion sûre des secrets ;
- gestion des clés API ;
- audit exploitable ;
- RBAC compréhensible ;
- expérience premium ;
- base technique évolutive.

# Conclusion

Le frontend de MCP Secret Manager doit devenir la console d'administration de référence pour un Secret Manager moderne, IA-first, MCP-native et orienté DevOps.

Sa mission est de rendre visibles, compréhensibles et maîtrisables des opérations sensibles qui, sans interface dédiée, restent dispersées entre API, scripts, fichiers de configuration, dashboards tiers et connaissances implicites.

Le produit doit offrir une expérience simple sans être simpliste, rapide sans être précipitée, premium sans être décorative, sécurisée sans être paralysante. Il doit aider un développeur indépendant à sécuriser ses projets, une startup à structurer ses accès, une PME à gouverner ses secrets, une équipe DevOps à opérer efficacement, une équipe IA à contrôler ses agents et une entreprise à préparer des usages avancés.

Le MVP doit se concentrer sur les fondations essentielles : dashboard, vaults, projects, secrets, secret versions, API keys, audit logs, RBAC, profil utilisateur et paramètres. Ces fonctionnalités doivent être réalisées avec un haut niveau de clarté, de cohérence et de confiance.

Les ambitions futures ouvriront la voie à des capacités Enterprise : rotation automatique, webhooks, notifications, multi-tenant, intégrations cloud, monitoring, KMS, HSM, analytics, billing, SSO, approbations et identités d'agents IA.

La vision à long terme est claire : faire de MCP Secret Manager non seulement un outil de stockage chiffré, mais une couche de gouvernance et de confiance pour les systèmes modernes où humains, services, agents IA et serveurs MCP manipulent des secrets critiques.
