# Introduction

Ce document définit la politique officielle de sécurité du frontend de MCP Secret Manager.

Il décrit exclusivement les responsabilités de sécurité de l'application web. Il ne remplace pas le document `SECURITY.md` du backend. Il le complète en définissant les règles que le frontend doit respecter lorsqu'il affiche des ressources sensibles, interagit avec l'API, gère la session utilisateur, manipule temporairement des valeurs secrètes et présente les décisions de sécurité du backend.

Le frontend n'est pas une frontière de confiance.

Un navigateur peut être inspecté, modifié, instrumenté ou compromis. Un utilisateur peut changer le JavaScript, appeler directement l'API, modifier des requêtes, contourner un bouton désactivé ou manipuler l'état local. Pour cette raison, aucune décision critique ne doit dépendre uniquement du frontend.

Le backend reste l'autorité pour :

- authentification ;
- autorisation ;
- RBAC ;
- validation métier ;
- chiffrement ;
- audit ;
- accès aux secrets ;
- révocation ;
- états des ressources ;
- refus d'accès.

Pour autant, le frontend a des responsabilités importantes.

Il est la surface d'interaction humaine avec le Secret Manager. Il peut réduire ou augmenter le risque d'erreur. Il peut exposer accidentellement une valeur dans l'interface, le cache, les logs, le presse-papiers, l'historique navigateur, un outil de monitoring ou une erreur. Il peut rendre une action dangereuse trop facile, un refus trop ambigu ou une permission trop difficile à comprendre.

La sécurité frontend est donc une sécurité d'usage, d'exposition et de discipline.

Elle ne remplace pas la sécurité réelle du backend, mais elle la complète :

- en évitant les fuites accidentelles ;
- en rendant les actions sensibles explicites ;
- en masquant les secrets par défaut ;
- en nettoyant les états temporaires ;
- en respectant strictement les refus backend ;
- en évitant les logs dangereux ;
- en protégeant la navigation ;
- en gardant les composants accessibles et compréhensibles.

Il faut distinguer UX de sécurité et sécurité réelle.

L'UX de sécurité consiste à guider l'utilisateur, confirmer les actions sensibles, afficher des badges, masquer des valeurs, désactiver des boutons, montrer des warnings et expliquer les conséquences. Elle réduit les erreurs humaines.

La sécurité réelle consiste à empêcher une action non autorisée même si le frontend est contourné. Elle appartient au backend.

Le frontend doit fournir une excellente UX de sécurité sans jamais prétendre être la source de sécurité réelle.

# Principes fondamentaux

## Zero Trust

Le frontend applique une philosophie Zero Trust envers lui-même, l'utilisateur, le navigateur, les données reçues et l'environnement d'exécution.

Conséquences :

- aucune donnée API n'est supposée sûre sans contrat ;
- aucun état client n'est une autorité ;
- aucun bouton masqué n'est une protection ;
- aucune permission n'est déduite localement comme vérité finale ;
- aucune valeur secrète n'est exposée par défaut ;
- aucun contenu utilisateur n'est considéré comme sûr à injecter.

Zero Trust côté frontend signifie que le navigateur est une surface d'exposition, pas un coffre-fort.

## Backend = autorité

Le backend est l'autorité unique pour les décisions de sécurité.

Le frontend doit toujours accepter que :

- une action visible puisse être refusée ;
- une permission puisse changer pendant la session ;
- une ressource puisse devenir inaccessible ;
- une session puisse expirer ;
- une mutation puisse échouer ;
- une valeur secrète puisse ne pas être révélée.

Le frontend doit représenter fidèlement les décisions backend. Il ne doit pas les interpréter de manière optimiste lorsqu'elles concernent la sécurité.

## Least Privilege

Le frontend doit demander et conserver le minimum d'information nécessaire.

Conséquences :

- ne pas demander une valeur secrète pour afficher une liste ;
- ne pas précharger des valeurs sensibles ;
- ne pas stocker de token ;
- ne pas conserver une réponse sensible après fermeture ;
- ne pas envoyer de champs inutiles dans les requêtes ;
- ne pas afficher des détails interdits ou inutiles.

Le principe de moindre privilège s'applique aussi à l'interface : l'utilisateur voit ce dont il a besoin pour agir, pas tout ce que l'application pourrait techniquement charger.

## Defense in Depth

La sécurité frontend ajoute des couches de protection.

Exemples :

- masquage par défaut ;
- confirmation de reveal ;
- nettoyage mémoire ;
- absence de cache durable ;
- messages d'erreur sûrs ;
- CSP future ;
- protection CSRF selon backend ;
- composants accessibles ;
- logs minimisés ;
- refus backend gérés.

Chaque couche réduit une catégorie de risque, même si aucune ne suffit seule.

## Fail Secure

En cas d'incertitude, le frontend doit adopter un comportement sûr.

Conséquences :

- session incertaine : demander reconnexion ;
- permission inconnue : ne pas présenter l'action comme autorisée ;
- erreur de reveal : ne pas afficher de valeur ;
- réponse inattendue : afficher une erreur sûre ;
- mutation incertaine : vérifier l'état backend ;
- données sensibles présentes lors d'une erreur : nettoyer.

Fail Secure ne signifie pas bloquer inutilement l'utilisateur. Cela signifie éviter de présenter une situation risquée comme sûre.

## Secure by Default

Le comportement par défaut doit être sécurisé.

Exemples :

- secrets masqués ;
- API keys affichées une seule fois ;
- valeurs non persistées ;
- actions dangereuses confirmées ;
- logs sans payload sensible ;
- cookies sécurisés privilégiés ;
- routes protégées ;
- dark et light mode lisibles pour éviter les erreurs ;
- composants sensibles isolés.

L'utilisateur ne doit pas avoir à configurer l'interface pour qu'elle soit sûre.

# Responsabilités du frontend

Le frontend doit faire plusieurs choses avec rigueur.

Il doit :

- afficher uniquement les données autorisées par le backend ;
- appeler l'API via une couche d'intégration contrôlée ;
- présenter les erreurs de manière sûre ;
- masquer les valeurs secrètes par défaut ;
- demander une action volontaire pour révéler un secret ;
- nettoyer les valeurs sensibles après usage ;
- empêcher les doubles soumissions ;
- confirmer les actions sensibles ;
- gérer les expirations de session ;
- nettoyer les caches au logout ;
- respecter les statuts backend ;
- invalider les caches après mutation ;
- distinguer metadata et value ;
- rendre les permissions compréhensibles ;
- gérer les refus comme des cas normaux ;
- maintenir l'accessibilité des actions sensibles ;
- éviter toute donnée sensible dans logs, monitoring et analytics.

Le frontend ne doit jamais :

- décider qu'une action est autorisée sans validation backend ;
- stocker un secret dans localStorage ;
- stocker un token sensible dans localStorage ;
- placer un token ou secret dans l'URL ;
- afficher une valeur secrète par défaut ;
- précharger des valeurs secrètes ;
- afficher une valeur secrète dans une table ;
- afficher une valeur secrète dans un toast ;
- logger un payload contenant un secret ;
- exposer un refresh token à JavaScript ;
- faire confiance à un rôle local pour accorder une action ;
- masquer silencieusement un refus backend ;
- convertir une erreur serveur en succès visuel ;
- contourner une protection backend ;
- injecter du HTML utilisateur non sûr.

La responsabilité principale du frontend est de rendre la sécurité visible et praticable sans s'approprier les décisions qui appartiennent au backend.

# Gestion des secrets

La gestion des secrets est la zone la plus sensible du frontend.

Un secret peut apparaître dans le navigateur uniquement dans des conditions strictes :

- l'utilisateur effectue une action explicite ;
- le backend autorise l'accès ;
- la réponse est reçue pour un usage immédiat ;
- l'affichage est temporaire ;
- la valeur n'est pas stockée durablement ;
- la valeur est nettoyée dès que possible.

## Affichage masqué

Les valeurs secrètes sont toujours masquées par défaut.

Règles :

- aucune valeur complète dans les listes ;
- aucune valeur complète dans les tables ;
- aucune valeur complète dans les cards de résumé ;
- aucune valeur complète dans les audit logs ;
- aucune valeur complète dans les tooltips ;
- aucune valeur complète dans les URLs ;
- aucune valeur complète dans les messages d'erreur ;
- aucune valeur complète dans les toasts.

Un secret peut être représenté par :

- son nom ;
- ses métadonnées ;
- son statut ;
- sa version courante ;
- des badges ;
- un indicateur masqué ;
- un fragment uniquement si le backend et la politique produit l'autorisent explicitement.

## Reveal volontaire

Révéler une valeur secrète doit toujours être volontaire.

Le reveal doit :

- être déclenché par une action utilisateur explicite ;
- être visible comme action sensible ;
- indiquer que l'action peut être auditée ;
- afficher un état loading distinct ;
- gérer le refus backend ;
- ne jamais se produire au chargement ;
- ne jamais être préchargé ;
- ne jamais être déclenché par hover ;
- ne jamais être appliqué en bulk.

Le reveal doit être disponible uniquement dans des contextes conçus pour cela, principalement Secret Details ou une vue de version.

## Nettoyage mémoire

Les valeurs secrètes doivent être nettoyées dès qu'elles ne sont plus nécessaires.

Situations de nettoyage :

- fermeture de RevealDialog ;
- fermeture d'un panneau contenant une valeur ;
- changement de route ;
- changement de vault, project ou secret ;
- logout ;
- expiration de session ;
- erreur inattendue ;
- annulation de formulaire ;
- soumission terminée ;
- fermeture de dialog API key.

Le nettoyage mémoire JavaScript n'est pas une garantie cryptographique, mais il limite les expositions accidentelles.

## Copie

Copier une valeur secrète est une action sensible.

Règles :

- copie volontaire ;
- bouton clairement nommé ;
- feedback bref ;
- ne jamais afficher la valeur dans le feedback ;
- gérer erreur de clipboard ;
- ne pas copier automatiquement ;
- ne pas copier en bulk ;
- distinguer copie d'identifiant non sensible et copie de secret.

La copie ne doit pas prolonger inutilement la durée de vie de la valeur dans l'état React.

## Durée de vie

Une valeur secrète révélée doit avoir une durée de vie minimale.

Options possibles selon UX finale :

- fermeture manuelle ;
- masquage automatique après délai ;
- nettoyage au changement de focus ;
- nettoyage au changement de route ;
- nettoyage au logout.

Le MVP doit au minimum nettoyer à la fermeture, au changement de route et au logout.

## Cache

Les valeurs secrètes ne doivent pas être stockées durablement dans le cache.

Règles :

- pas de secret value dans TanStack Query cache durable ;
- pas de prefetch ;
- pas de background refresh ;
- pas de persistance ;
- pas d'hydratation serveur contenant la valeur ;
- pas de stockage dans des modèles UI globaux.

Les métadonnées peuvent être cachées selon les règles d'intégration API, mais les valeurs doivent rester temporaires.

## Logs

Les secrets ne doivent jamais être loggés.

Interdictions :

- console ;
- monitoring ;
- analytics ;
- error reporting ;
- network debug volontaire ;
- traces de développement ;
- payloads bruts ;
- headers ;
- messages d'erreur.

Cette règle s'applique en développement, test, staging et production.

## Clipboard

Le clipboard est externe au contrôle du frontend.

Le frontend peut copier une valeur, mais ne peut pas garantir ce que l'utilisateur, le système d'exploitation, une extension ou une autre application en fera ensuite.

Règles :

- informer par feedback sans afficher la valeur ;
- ne pas tenter de lire le clipboard ;
- ne pas promettre un nettoyage impossible ;
- documenter les limites ;
- éviter la copie automatique.

# Authentification

L'authentification frontend gère l'expérience de session.

Elle ne décide pas des droits métier.

## Session

La session représente l'utilisateur connecté.

Le frontend peut afficher :

- nom ;
- email ;
- avatar futur ;
- rôle résumé si fourni ;
- organisation future ;
- état de connexion.

Le frontend ne doit pas stocker :

- refresh token lisible ;
- access token sensible si évitable ;
- API key ;
- secret ;
- mot de passe ;
- session complète dans localStorage.

## Cookies

Les cookies sécurisés sont privilégiés pour l'authentification web.

Responsabilités frontend :

- inclure credentials si nécessaire ;
- s'aligner avec SameSite ;
- gérer erreurs CSRF si stratégie activée ;
- ne pas tenter de lire les cookies HttpOnly ;
- ne pas dupliquer les tokens dans un stockage client.

Responsabilités backend :

- définir HttpOnly ;
- définir Secure ;
- définir SameSite ;
- gérer durée de vie ;
- valider session ;
- révoquer session.

## Expiration

Une session peut expirer à tout moment.

Comportement frontend attendu :

- arrêter les actions sensibles ;
- nettoyer valeurs révélées ;
- nettoyer caches appropriés ;
- afficher un message clair ;
- rediriger vers Login ;
- préserver destination si sûr ;
- ne pas afficher de données protégées après expiration.

## Logout

Le logout doit être robuste.

Il doit :

- appeler le backend si nécessaire ;
- invalider session ;
- nettoyer TanStack Query ;
- fermer dialogs ;
- supprimer valeurs sensibles ;
- réinitialiser états UI ;
- rediriger vers Login ;
- empêcher retour arrière vers données sensibles rendues depuis cache.

## Refresh

Le refresh de session doit être centralisé.

Règles :

- éviter boucles infinies ;
- éviter refresh concurrents incontrôlés ;
- ne pas relancer automatiquement des mutations sensibles ;
- nettoyer session si refresh échoue ;
- ne pas exposer refresh token.

## MFA futur

Le MFA futur renforcera l'authentification.

Responsabilités frontend futures :

- afficher étape MFA ;
- gérer erreurs ;
- ne pas stocker codes ;
- respecter expiration ;
- proposer fallback selon backend ;
- rester accessible.

Le frontend ne valide pas réellement le MFA. Il transmet au backend.

## SSO futur

Le SSO futur permettra une authentification via provider externe.

Responsabilités frontend futures :

- rediriger vers provider ;
- gérer retour ;
- afficher erreurs ;
- gérer sélection organisation future ;
- ne pas exposer tokens ;
- respecter session backend.

# Autorisations

L'autorisation détermine ce qu'un acteur peut faire.

Le frontend ne décide jamais de l'autorisation réelle.

## RBAC

Le RBAC est fourni et appliqué par le backend.

Le frontend peut :

- afficher des rôles ;
- afficher des permissions ;
- afficher des assignments ;
- afficher des permissions effectives si fournies ;
- masquer ou désactiver des actions ;
- expliquer un refus.

Le frontend ne doit pas :

- calculer les permissions réelles à partir d'un rôle local ;
- accorder une action parce qu'un badge est présent ;
- contourner un refus ;
- supposer qu'une permission de metadata donne accès à la value.

## Affichage conditionnel

L'affichage conditionnel est une aide UX.

Exemples :

- masquer "Créer API Key" si non autorisé ;
- désactiver "Reveal" si permission absente ;
- afficher un tooltip expliquant un refus ;
- rendre une section read-only.

Mais cet affichage ne protège rien seul. Le backend doit valider toute action.

## Refus

Les refus backend doivent être gérés comme des cas normaux.

Comportement :

- afficher ForbiddenState ou message local ;
- ne pas révéler détails interdits ;
- proposer retour ;
- nettoyer état sensible ;
- invalider données si permission changée.

Un refus ne doit pas être transformé en erreur générique incompréhensible.

## Permissions

Les permissions doivent être affichées avec précision.

Règles :

- distinguer metadata read et secret value read ;
- distinguer création, modification, archivage, révocation ;
- identifier permissions critiques ;
- ne pas utiliser seulement la couleur ;
- éviter les libellés ambigus.

## Ressources non autorisées

Une ressource non autorisée ne doit pas être exposée par l'interface.

Règles :

- ne pas afficher un nom interdit ;
- ne pas afficher un nombre qui révèle trop si backend ne l'autorise pas ;
- ne pas afficher liens vers ressources non accessibles ;
- ne pas afficher filtres contenant ressources interdites ;
- respecter les réponses backend.

# Stockage local

Le stockage local est une zone de risque.

Le frontend doit minimiser ce qu'il stocke.

## Mémoire

La mémoire React ou JavaScript peut contenir temporairement :

- état UI ;
- formulaires ;
- données API non sensibles ;
- valeur secrète révélée uniquement pendant un workflow contrôlé.

Règles :

- durée minimale ;
- nettoyage sur fermeture ;
- nettoyage logout ;
- pas de stockage global inutile ;
- pas de secret dans cache durable.

## localStorage

localStorage est interdit pour les données sensibles.

Interdit :

- secret ;
- API key ;
- token ;
- refresh token ;
- mot de passe ;
- payload de création ;
- données d'audit sensibles ;
- permissions utilisées comme sécurité.

Autorisé avec prudence :

- thème ;
- densité d'affichage ;
- préférence non sensible ;
- état de colonne non sensible.

## sessionStorage

sessionStorage est également interdit pour les données sensibles.

Il peut contenir uniquement des préférences temporaires non sensibles si nécessaire.

Il ne doit pas contenir :

- secret ;
- token ;
- API key ;
- valeur révélée ;
- payload sensible.

## IndexedDB

IndexedDB ne doit pas être utilisé pour des données sensibles au MVP.

Interdit :

- cache offline de secrets ;
- API keys ;
- tokens ;
- audit détaillé sensible ;
- payloads de formulaire secret.

Un usage futur nécessiterait une revue sécurité spécifique.

## Cache API

La Cache API du navigateur ne doit pas stocker des réponses sensibles.

Règles :

- pas de caching offline pour routes protégées contenant données sensibles ;
- pas de secret value ;
- prudence sur metadata ;
- stratégie explicite si PWA future.

# Protection XSS

Une faille XSS dans MCP Secret Manager serait critique.

Elle pourrait permettre à un attaquant de lire des valeurs affichées, déclencher des actions dans la session de l'utilisateur ou exfiltrer des métadonnées sensibles.

## HTML

Le frontend ne doit pas injecter du HTML non sûr.

Règles :

- privilégier le rendu texte ;
- échapper les contenus utilisateur ;
- éviter toute injection HTML ;
- interdire HTML riche dans metadata au MVP ;
- traiter descriptions, noms, tags et messages comme non fiables.

## Scripts

Les scripts dynamiques doivent être évités.

Règles :

- ne pas charger de scripts externes non nécessaires ;
- limiter les intégrations tierces ;
- éviter inline scripts selon CSP future ;
- contrôler les dépendances.

## Contenu utilisateur

Le contenu utilisateur inclut :

- noms de vault ;
- noms de project ;
- noms de secret ;
- descriptions ;
- tags ;
- commentaires ;
- noms d'acteurs ;
- metadata.

Ce contenu doit être considéré comme non fiable.

Il doit être affiché comme texte, jamais exécuté.

## Sanitation

Si un jour du contenu riche est supporté, une stratégie de sanitation devra être définie avant implémentation.

Au MVP, le plus sûr est de ne pas accepter ou rendre de HTML riche dans les champs utilisateur.

## CSP

Une Content Security Policy devra être prévue pour renforcer la défense contre XSS.

Objectifs :

- limiter les sources de scripts ;
- limiter les connexions ;
- limiter les images ;
- empêcher inline scripts lorsque possible ;
- encadrer les frames ;
- réduire l'impact d'une injection.

La CSP doit être coordonnée avec le mode de déploiement Next.js et les besoins backend.

## Bonnes pratiques

Règles :

- pas de dangerously set inner HTML sans revue sécurité ;
- pas d'évaluation dynamique de code ;
- pas de rendu Markdown non sanitizé ;
- dépendances limitées ;
- composants contrôlés ;
- tests sur champs contenant caractères spéciaux ;
- aucun secret affiché plus longtemps que nécessaire.

# Protection CSRF

La protection CSRF dépend de la stratégie d'authentification backend.

Si l'application utilise des cookies pour authentifier les requêtes, CSRF doit être traité explicitement.

Responsabilités frontend possibles :

- envoyer un token CSRF fourni par le backend ;
- inclure un header CSRF ;
- gérer les erreurs CSRF ;
- respecter SameSite ;
- ne pas contourner les mécanismes backend ;
- déclencher un refresh ou une reconnexion si nécessaire.

Responsabilités backend :

- générer et vérifier les tokens CSRF si requis ;
- configurer SameSite ;
- refuser les requêtes invalides ;
- documenter le comportement attendu.

Le frontend ne doit pas inventer une protection CSRF non alignée avec le backend.

En cas d'erreur CSRF, l'UI doit afficher un message sûr et proposer une récupération, souvent par rechargement ou reconnexion.

# Navigation

La navigation doit protéger l'accès aux routes et nettoyer les données sensibles.

## Routes protégées

Les routes protégées nécessitent une session valide.

Elles incluent :

- Dashboard ;
- Vaults ;
- Projects ;
- Secrets ;
- API Keys ;
- Audit Logs ;
- RBAC ;
- Profile ;
- Settings.

Le frontend doit vérifier la session via la stratégie définie, mais le backend reste responsable de chaque accès API.

## Redirections

Les redirections doivent être sûres.

Règles :

- rediriger vers Login si session absente ;
- rediriger après login vers destination initiale seulement si sûre ;
- éviter open redirects ;
- ne pas inclure tokens ou secrets dans les URLs ;
- gérer accès refusé avec ForbiddenState.

## Session expirée

En cas de session expirée :

- fermer dialogs sensibles ;
- nettoyer valeurs révélées ;
- nettoyer cache ;
- afficher message ;
- rediriger vers Login ;
- éviter que retour arrière affiche un écran sensible depuis cache.

## Retour arrière

Le bouton retour du navigateur ne doit pas réexposer des données sensibles.

Règles :

- nettoyer les valeurs au changement de route ;
- ne pas conserver secret value dans l'état historique ;
- éviter les URLs contenant des données sensibles ;
- revalider session sur routes protégées.

## Nettoyage des données

Le nettoyage doit se produire lors de :

- logout ;
- expiration ;
- changement de route ;
- changement de secret ;
- fermeture de dialog ;
- erreur inattendue ;
- changement de tenant futur.

# Erreurs

Les erreurs doivent informer sans exposer.

## Erreurs utilisateur

Exemples :

- champ requis ;
- format invalide ;
- confirmation incorrecte ;
- action impossible.

Comportement :

- message proche du champ ;
- correction claire ;
- aucun payload sensible ;
- ton neutre.

## Erreurs serveur

Exemples :

- erreur interne ;
- conflit ;
- ressource indisponible ;
- action refusée.

Comportement :

- message sûr ;
- retry si pertinent ;
- ne pas afficher stack trace ;
- ne pas afficher détails internes ;
- ne pas exposer secret, token ou headers.

## Erreurs réseau

Exemples :

- offline ;
- timeout ;
- backend indisponible ;
- proxy erreur.

Comportement :

- message réseau ;
- retry pour lectures ;
- prudence pour mutations ;
- pas de détails sensibles.

## Erreurs inattendues

Les erreurs inattendues doivent être capturées par des boundaries.

Comportement :

- afficher ErrorState ;
- nettoyer données sensibles ;
- proposer recovery ;
- envoyer un rapport minimal futur ;
- ne jamais afficher stack trace en production.

## Informations à ne jamais afficher

Interdit dans les erreurs :

- secret value ;
- API key complète ;
- token ;
- refresh token ;
- password ;
- cookie ;
- header authorization ;
- chaîne de connexion ;
- stack trace production ;
- payload brut de création secret ;
- détails crypto internes ;
- configuration sensible ;
- chemins internes serveur si dangereux.

# Logging

Le logging frontend doit être minimaliste et sûr.

## Console

En développement, les logs peuvent aider. Ils doivent rester sûrs.

Interdictions :

- secret ;
- token ;
- password ;
- API key ;
- payload sensible ;
- headers ;
- cookies ;
- valeurs de formulaire secret ;
- réponses de reveal.

En production, les logs console doivent être limités.

## Monitoring

Un outil de monitoring futur peut collecter des erreurs et métriques.

Données autorisées :

- code d'erreur normalisé ;
- route ;
- composant ;
- statut HTTP ;
- timestamp ;
- durée ;
- request id futur ;
- environnement.

Données interdites :

- secret ;
- token ;
- API key ;
- password ;
- payload complet ;
- headers sensibles ;
- cookies ;
- recherche contenant donnée sensible sans minimisation ;
- données d'audit détaillées non nécessaires.

## Analytics

Les analytics produit doivent respecter la minimisation.

Autorisés :

- vues visitées ;
- actions génériques ;
- performance ;
- erreurs agrégées ;
- usage de fonctionnalités.

Interdits :

- noms de secrets si considérés sensibles ;
- valeurs ;
- tokens ;
- API keys ;
- contenus de recherche ;
- metadata confidentielle ;
- détails d'audit non minimisés.

## Erreurs

Les erreurs envoyées au monitoring doivent être filtrées.

Règles :

- normaliser ;
- redacter ;
- limiter ;
- éviter stack traces contenant données ;
- tester la redaction.

# Clipboard

Le clipboard est une zone de passage sensible.

## Copie volontaire

Toute copie de secret doit être volontaire.

Règles :

- bouton explicite ;
- action utilisateur ;
- pas de copie automatique ;
- pas de copie bulk ;
- confirmation ou contexte clair ;
- permission backend préalable.

## Feedback

Le feedback doit confirmer la copie sans révéler la valeur.

Exemples acceptables :

- valeur copiée ;
- clé copiée ;
- impossible de copier.

Interdit :

- afficher la valeur copiée ;
- afficher un fragment non nécessaire ;
- logger le contenu.

## Nettoyage

Le navigateur ne permet pas de garantir un nettoyage fiable du clipboard.

Le frontend peut :

- nettoyer son propre état ;
- masquer la valeur ;
- fermer le dialog ;
- informer l'utilisateur sans fausse promesse.

Il ne doit pas promettre que le clipboard sera vidé.

## Limites

Le contenu du clipboard peut être lu par :

- système d'exploitation ;
- applications ;
- extensions ;
- outils de clipboard history ;
- politiques entreprise.

Le frontend doit reconnaître cette limite.

# Screenshots

Le navigateur ne peut pas empêcher de manière fiable les captures d'écran.

La philosophie frontend doit donc être :

- minimiser l'exposition visuelle ;
- masquer par défaut ;
- révéler volontairement ;
- réduire la durée d'affichage ;
- éviter les listes de valeurs ;
- éviter les toasts contenant des secrets ;
- éviter les overlays persistants avec valeurs.

MCP Secret Manager ne doit pas promettre une impossibilité de capture d'écran.

Il peut réduire le risque par design :

- affichage ponctuel ;
- composants dédiés ;
- masquage rapide ;
- contexte clair ;
- aucune valeur dans les pages denses ;
- attention au mobile et au partage d'écran.

# Extensions navigateur

Les extensions navigateur représentent un risque externe.

Une extension malveillante ou trop permissive peut observer le DOM, les requêtes, le clipboard ou les interactions.

Hypothèses de confiance :

- le navigateur et ses extensions font partie de l'environnement utilisateur ;
- MCP Secret Manager ne peut pas garantir la sécurité contre une extension malveillante avec accès à la page ;
- l'application doit minimiser l'exposition pour réduire l'impact.

Mesures frontend :

- ne pas stocker de secrets localement ;
- révéler temporairement ;
- ne pas précharger ;
- ne pas afficher en masse ;
- ne pas placer en URL ;
- limiter les intégrations tierces ;
- CSP future.

La documentation utilisateur future pourra recommander d'utiliser le produit dans un navigateur et profil de confiance.

# Dépendances

Les dépendances frontend font partie de la surface de sécurité.

## Bibliothèques

Les bibliothèques doivent être choisies avec prudence.

Critères :

- maintenance active ;
- adoption raisonnable ;
- surface limitée ;
- compatibilité avec React et Next.js ;
- accessibilité ;
- absence de comportement réseau caché ;
- taille maîtrisée ;
- historique de sécurité.

Les bibliothèques manipulant formulaires, composants UI, dates ou données doivent être évaluées avant adoption.

## Audit

Les dépendances doivent être auditées.

Pratiques attendues :

- lockfile ;
- revue des nouvelles dépendances ;
- suivi des vulnérabilités ;
- suppression des dépendances inutilisées ;
- contrôle des dépendances transitoires critiques ;
- attention aux packages peu connus.

## Mises à jour

Les mises à jour doivent être régulières mais contrôlées.

Règles :

- tester avant upgrade ;
- lire changelogs pour dépendances majeures ;
- surveiller breaking changes ;
- prioriser patches sécurité ;
- éviter les upgrades massifs non maîtrisés.

## Supply Chain

La supply chain frontend peut introduire des risques.

Mesures :

- limiter le nombre de dépendances ;
- éviter packages inutiles ;
- ne pas ajouter de package pour une fonction triviale ;
- vérifier provenance ;
- utiliser lockfile ;
- intégrer scans CI futurs ;
- contrôler scripts postinstall si nécessaire.

# Incident Security

Le frontend doit prévoir un comportement clair en cas d'incident de sécurité ou de dégradation.

## Comportement attendu

En cas d'incident :

- afficher un message utilisateur sûr ;
- éviter détails internes ;
- désactiver les actions risquées si demandé par backend ;
- forcer logout si session compromise ;
- nettoyer caches ;
- empêcher reveal si backend le désactive ;
- orienter vers statut ou support si disponible.

Le frontend ne doit pas improviser une politique d'incident. Il doit suivre les signaux backend.

## Désactivation de fonctionnalités

Le backend peut indiquer qu'une fonctionnalité est désactivée.

Exemples :

- reveal suspendu ;
- création API key suspendue ;
- RBAC read-only ;
- maintenance audit ;
- settings verrouillés.

Le frontend doit :

- afficher l'état ;
- désactiver actions ;
- expliquer sobrement ;
- éviter contournement ;
- revalider périodiquement si nécessaire.

## Maintenance

En mode maintenance :

- l'UI doit afficher un message clair ;
- les actions non disponibles doivent être désactivées ;
- les lectures peuvent être limitées ;
- les erreurs doivent rester sûres.

## Messages utilisateur

Les messages d'incident doivent :

- être calmes ;
- être précis sans détails exploitables ;
- expliquer l'impact utilisateur ;
- proposer une action si possible ;
- éviter toute mention de secret compromis sauf communication officielle validée.

# Future Security

Le frontend doit pouvoir accueillir des fonctionnalités de sécurité avancées.

## WebAuthn

WebAuthn pourra permettre une authentification forte.

Responsabilités frontend futures :

- lancer le challenge ;
- gérer interaction navigateur ;
- afficher erreurs ;
- respecter accessibilité ;
- transmettre réponses au backend.

Le backend restera l'autorité de validation.

## Passkeys

Les passkeys pourront améliorer l'expérience d'authentification.

Responsabilités frontend futures :

- proposer connexion ;
- gérer création ;
- gérer récupération ;
- afficher états ;
- ne pas stocker secrets cryptographiques.

## Device Trust

Device Trust futur pourrait permettre d'évaluer la confiance d'un appareil.

Responsabilités frontend futures :

- afficher état de l'appareil si fourni ;
- guider enrôlement ;
- gérer refus ;
- ne pas simuler une confiance locale.

## Hardware Keys

Les hardware keys pourront renforcer les actions sensibles.

Responsabilités frontend futures :

- déclencher challenge ;
- gérer erreurs de clé ;
- expliquer l'action ;
- rester compatible clavier et lecteurs d'écran ;
- ne pas remplacer validation backend.

## Audit renforcé

Le frontend devra pouvoir afficher un audit plus riche.

Évolutions possibles :

- corrélation d'événements ;
- détails agentiques ;
- contexte de reveal ;
- approbations ;
- alertes ;
- exports contrôlés ;
- visualisation d'incident.

Règles :

- aucun secret dans l'audit ;
- minimisation ;
- permissions strictes ;
- messages sûrs.

# Security Checklist

Chaque nouvelle fonctionnalité frontend doit respecter cette checklist avant validation.

## Données

- La fonctionnalité distingue metadata et value.
- Aucune valeur secrète n'est affichée par défaut.
- Aucune valeur secrète n'est affichée dans une table.
- Aucune valeur secrète n'est stockée dans localStorage.
- Aucune valeur secrète n'est stockée dans sessionStorage.
- Aucune valeur secrète n'est stockée dans IndexedDB.
- Aucune valeur secrète n'est placée dans une URL.
- Les données sensibles sont nettoyées après usage.

## API

- Toutes les actions passent par l'API backend.
- Le backend valide les entrées.
- Le backend autorise les actions.
- Le frontend gère les refus.
- Les mutations sensibles n'utilisent pas d'optimistic update.
- Le cache est invalidé après mutation.
- Les erreurs API sont normalisées.

## Authentification

- La route est protégée si nécessaire.
- L'expiration de session est gérée.
- Le logout nettoie les données sensibles.
- Aucun token sensible n'est exposé au JavaScript si évitable.
- Aucun token n'est placé dans l'URL.

## Autorisation

- Aucune permission métier n'est décidée localement.
- Les actions non autorisées sont masquées, désactivées ou expliquées.
- Les refus backend sont affichés correctement.
- Les ressources non autorisées ne sont pas révélées.
- Les permissions critiques sont identifiables.

## UI sensible

- Les actions dangereuses sont confirmées.
- Les dialogs nomment la ressource concernée.
- Reveal est volontaire.
- Copy est volontaire.
- Les feedbacks ne contiennent pas de secret.
- Les états archived, locked et revoked sont distincts.

## Erreurs et logs

- Aucun secret dans les erreurs.
- Aucun token dans les erreurs.
- Aucune stack trace production visible.
- Aucun payload sensible dans console.
- Aucun payload sensible dans monitoring.
- Les erreurs inattendues nettoient les données sensibles.

## XSS et contenu

- Le contenu utilisateur est traité comme non fiable.
- Aucun HTML non sûr n'est injecté.
- Aucun script dynamique non nécessaire.
- Les champs texte spéciaux sont testés.
- La CSP future reste compatible.

## Accessibilité

- Les actions sont accessibles au clavier.
- Le focus est visible.
- Les dialogs piègent et restaurent le focus.
- Les IconButtons ont un nom accessible.
- La couleur n'est jamais la seule information.
- Les contrastes sont suffisants.

## Tests

- Les états succès sont testés.
- Les erreurs sont testées.
- Les refus sont testés.
- L'expiration de session est testée.
- Le reveal est testé.
- Le nettoyage des valeurs sensibles est testé.
- Les logs ne contiennent pas de données interdites.

# Conclusion

La sécurité frontend de MCP Secret Manager repose sur une idée simple : le frontend n'est pas une frontière de confiance, mais il est une surface d'exposition critique.

Il ne décide pas des permissions, ne valide pas la sécurité réelle et ne remplace jamais le backend. En revanche, il doit rendre l'expérience sûre, claire et disciplinée.

Son rôle est de masquer les secrets par défaut, révéler uniquement sur action volontaire, nettoyer les données sensibles, protéger la session, éviter le stockage dangereux, prévenir les fuites dans les logs, gérer les erreurs avec prudence, respecter les refus backend et rendre les actions sensibles compréhensibles.

Cette politique doit guider toute l'implémentation React. Chaque composant, écran, formulaire, dialog, mutation et intégration API doit être conçu avec cette posture : confiance minimale dans le client, autorité maximale du backend, exposition minimale des secrets et UX de sécurité irréprochable.
