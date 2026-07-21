# Vision

Le Design System de MCP Secret Manager définit l'identité visuelle, les règles d'interface et les principes d'expérience qui guideront toute la construction du frontend.

MCP Secret Manager est une application SaaS d'administration pour un produit de sécurité. Son design doit donc inspirer immédiatement la confiance. L'utilisateur doit sentir qu'il manipule un outil sérieux, précis, fiable et conçu pour protéger des ressources critiques.

La philosophie du design repose sur cinq intentions principales :

- confiance ;
- précision ;
- sécurité ;
- sobriété ;
- modernité.

Le produit doit paraître premium, mais jamais ostentatoire. Le design ne doit pas chercher à impressionner par des effets décoratifs, des animations excessives, des couleurs agressives ou une identité visuelle trop bruyante. Il doit plutôt impressionner par son calme, sa lisibilité, sa cohérence et son niveau de finition.

L'interface doit soutenir des décisions de sécurité. Chaque écran doit aider l'utilisateur à comprendre où il se trouve, quelle ressource il manipule, quel état elle possède, quelles actions sont disponibles et quelles conséquences peuvent suivre une action sensible.

Le design doit être moderne sans être fragile. Il doit rester lisible dans le temps, compatible avec une utilisation quotidienne, adapté aux environnements techniques et crédible pour des usages professionnels. Il doit être capable de servir un développeur indépendant, une startup, une équipe DevOps, une équipe IA, une PME et une future organisation Enterprise.

La beauté recherchée est celle d'un outil bien construit : alignements précis, hiérarchie claire, espacements réguliers, typographie nette, états explicites, composants cohérents, retours utilisateur immédiats et absence de confusion.

Le design doit réduire la charge mentale. Les concepts comme vault, project, secret, version, API key, role, permission, audit log, locked, archived, revoked ou current version doivent être visuellement compréhensibles. L'utilisateur ne doit pas deviner si une action est dangereuse, si une donnée est masquée, si une permission manque ou si une ressource est active.

Le Design System doit aussi protéger le produit contre l'incohérence. Sans règles communes, chaque écran peut introduire une variation subtile : un bouton dangereux d'une autre couleur, un badge d'état ambigu, une modale trop bavarde, une table trop dense, un champ sensible mal traité. Dans un produit de sécurité, ces variations ne sont pas seulement esthétiques. Elles peuvent devenir des risques d'usage.

Le design de MCP Secret Manager doit donc être sobre, discipliné et vivant. Il doit donner envie d'utiliser le produit, mais ne jamais détourner l'attention des informations importantes.

# Inspirations

Les inspirations visuelles de MCP Secret Manager sont philosophiques. Aucun design, écran, composant, palette, animation, layout ou identité de marque ne doit être copié.

Les produits cités servent de repères de maturité, pas de modèles à reproduire. MCP Secret Manager doit construire sa propre identité, adaptée à son domaine : secret management IA-first, MCP-native, DevOps et SaaS.

## Linear

Linear inspire par sa clarté, sa vitesse perçue et sa discipline d'interface.

Ce qui est pertinent pour MCP Secret Manager :

- sensation de fluidité ;
- hiérarchie nette ;
- faible friction ;
- composants cohérents ;
- densité bien maîtrisée ;
- expérience qui respecte l'attention de l'utilisateur.

Linear montre qu'une application professionnelle peut être élégante sans surcharge visuelle. Pour MCP Secret Manager, cette philosophie doit se traduire par une console rapide, précise et concentrée sur les tâches.

## GitHub

GitHub inspire par sa familiarité pour les développeurs et sa capacité à présenter beaucoup d'informations sans perdre l'utilisateur.

Ce qui est pertinent pour MCP Secret Manager :

- tableaux lisibles ;
- navigation robuste ;
- états explicites ;
- historiques compréhensibles ;
- actions contextuelles ;
- densité adaptée aux utilisateurs techniques.

MCP Secret Manager doit apprendre de cette capacité à rendre des systèmes complexes administrables. Les audit logs, permissions, API keys et versions de secrets doivent bénéficier de cette clarté opérationnelle.

## Vercel

Vercel inspire par sa qualité perçue, sa finition visuelle et son expérience SaaS premium.

Ce qui est pertinent pour MCP Secret Manager :

- sobriété moderne ;
- attention aux détails ;
- transitions discrètes ;
- qualité typographique ;
- équilibre entre technique et accessibilité ;
- impression de produit mature.

MCP Secret Manager doit reprendre cette exigence de finition, mais dans un registre plus orienté sécurité et administration.

## Infisical

Infisical inspire par sa spécialisation dans la gestion de secrets et par sa pédagogie autour des concepts liés aux environnements, secrets et accès.

Ce qui est pertinent pour MCP Secret Manager :

- vocabulaire métier explicite ;
- workflows centrés sur les secrets ;
- distinction entre configuration et valeur sensible ;
- expérience adaptée aux équipes techniques ;
- effort de rendre le secret management accessible.

MCP Secret Manager doit s'inscrire dans cette famille de produits, tout en affirmant sa différence autour de MCP, des agents IA et d'une architecture orientée confiance.

## Doppler

Doppler inspire par sa simplicité d'utilisation dans la gestion des secrets pour développeurs et équipes.

Ce qui est pertinent pour MCP Secret Manager :

- onboarding clair ;
- organisation des secrets ;
- workflows rapides ;
- lisibilité des environnements ;
- approche pratique de la gestion quotidienne.

MCP Secret Manager doit viser cette facilité d'usage sans réduire son exigence de sécurité.

## HashiCorp Vault

HashiCorp Vault inspire par sa crédibilité infrastructure, sa rigueur sécurité et sa profondeur Enterprise.

Ce qui est pertinent pour MCP Secret Manager :

- sérieux du domaine ;
- respect des frontières de sécurité ;
- importance des policies ;
- audit ;
- gestion stricte des accès ;
- posture Enterprise.

MCP Secret Manager ne doit pas imiter la complexité visuelle ou fonctionnelle de Vault. Il doit plutôt reprendre l'exigence de rigueur et la traduire dans une interface plus moderne, plus lisible et plus adaptée aux usages IA et MCP.

# Identité visuelle

L'identité visuelle de MCP Secret Manager doit être celle d'un outil technique premium, calme et précis.

## Personnalité visuelle

La personnalité visuelle doit être :

- professionnelle ;
- fiable ;
- directe ;
- structurée ;
- moderne ;
- attentive aux détails ;
- discrètement sophistiquée.

Le produit ne doit pas paraître froid ou intimidant. Il doit rester accueillant, mais dans un registre sérieux. L'utilisateur doit ressentir que le produit est construit pour l'aider, pas pour le juger ou l'impressionner.

## Ambiance

L'ambiance générale doit évoquer un centre de contrôle sécurisé.

Elle doit donner une impression de :

- calme ;
- maîtrise ;
- visibilité ;
- ordre ;
- protection ;
- efficacité.

Les écrans doivent respirer, mais rester denses lorsque l'information opérationnelle le demande. Le design ne doit pas multiplier les grands blocs décoratifs. Les surfaces doivent servir à organiser l'information.

## Ton graphique

Le ton graphique doit être sobre et net.

Il doit éviter :

- les effets trop brillants ;
- les dégradés décoratifs dominants ;
- les illustrations purement marketing ;
- les ombres lourdes ;
- les couleurs saturées en excès ;
- les compositions spectaculaires ;
- les formes trop ludiques.

Il doit privilégier :

- lignes fines ;
- contrastes maîtrisés ;
- badges lisibles ;
- surfaces claires ;
- états explicites ;
- typographie précise ;
- icônes cohérentes ;
- animations discrètes.

## Niveau de densité

Le niveau de densité doit être adapté à une application d'administration.

MCP Secret Manager n'est pas une landing page. Les écrans principaux doivent permettre de scanner des listes, comparer des états, filtrer des données et accéder rapidement aux actions.

La densité doit être :

- moyenne sur les vues générales ;
- plus élevée sur les tables et audit logs ;
- plus aérée sur les formulaires sensibles ;
- plus guidée sur les états vides ;
- plus stricte sur les dialogs de confirmation.

La densité ne doit jamais nuire à la lisibilité, à l'accessibilité ou à la sécurité.

## Hiérarchie des informations

Chaque écran doit avoir une hiérarchie claire.

Ordre de priorité :

- contexte de la page ;
- état de la ressource ;
- action principale ;
- informations critiques ;
- contenu principal ;
- actions secondaires ;
- détails complémentaires ;
- informations techniques avancées.

Les informations sensibles ou de sécurité doivent être visibles au bon moment. Elles ne doivent pas être noyées dans une décoration ou un texte secondaire.

# Palette de couleurs

La palette de couleurs doit être sobre, accessible et fonctionnelle.

Les couleurs servent d'abord à guider la compréhension. Elles ne doivent jamais devenir un décor autonome. Elles doivent soutenir les états, les actions, la hiérarchie et la perception de confiance.

Aucun code couleur précis n'est défini dans ce document. Les choix exacts seront traduits plus tard dans les fondations visuelles, mais devront respecter les rôles décrits ici.

## Primary

La couleur Primary représente l'action principale, l'identité active du produit et les éléments interactifs les plus importants.

Rôle :

- bouton principal ;
- lien d'action majeur ;
- élément actif de navigation ;
- focus d'une action centrale ;
- mise en avant maîtrisée.

La couleur Primary doit être moderne, professionnelle et suffisamment distinctive. Elle ne doit pas dominer toute l'interface. Elle doit guider l'oeil vers l'action attendue.

## Secondary

La couleur Secondary soutient les éléments complémentaires.

Rôle :

- actions secondaires ;
- surfaces discrètement différenciées ;
- états non critiques ;
- éléments de support ;
- accents modérés.

La couleur Secondary doit rester calme. Elle ne doit pas concurrencer la couleur Primary ni les couleurs de statut.

## Success

La couleur Success indique une action réussie ou un état sain.

Rôle :

- succès de soumission ;
- état actif sain ;
- validation terminée ;
- opération confirmée ;
- intégration fonctionnelle.

La couleur Success doit être rassurante sans être trop vive. Elle doit rester lisible en light mode et dark mode.

## Warning

La couleur Warning signale une attention nécessaire sans indiquer un danger immédiat.

Rôle :

- configuration incomplète ;
- action potentiellement sensible ;
- ressource proche d'un état critique ;
- expiration future ;
- avertissement avant confirmation.

La couleur Warning doit attirer l'attention sans créer une alarme excessive.

## Danger

La couleur Danger est réservée aux risques, erreurs critiques et actions destructives ou irréversibles.

Rôle :

- révocation ;
- suppression logique ;
- refus critique ;
- erreur importante ;
- action destructrice ;
- état compromis ou bloquant.

La couleur Danger doit être immédiatement reconnaissable. Elle doit être utilisée avec parcimonie pour conserver son impact.

## Info

La couleur Info accompagne les messages neutres ou explicatifs.

Rôle :

- information contextuelle ;
- aide ;
- état en cours ;
- détails complémentaires ;
- messages non bloquants.

La couleur Info doit clarifier sans distraire.

## Neutral

La palette Neutral constitue la base de l'interface.

Rôle :

- arrière-plans ;
- surfaces ;
- bordures ;
- textes ;
- séparateurs ;
- états inactifs ;
- tableaux ;
- cartes ;
- modales.

La palette Neutral est la plus importante pour la perception premium. Elle doit offrir suffisamment de nuances pour hiérarchiser l'information sans créer une interface monotone.

# Light Mode

Le light mode doit être clair, professionnel et confortable pour une utilisation prolongée.

Il ne doit pas paraître vide, clinique ou trop lumineux. Les contrastes doivent être équilibrés afin de préserver la lisibilité des textes, tableaux, états et actions.

## Fond

Le fond principal doit être neutre, légèrement différencié des surfaces, et suffisamment calme pour ne pas fatiguer.

Il doit soutenir :

- navigation longue ;
- consultation de tables ;
- pages de détail ;
- formulaires ;
- dashboard.

Le fond ne doit pas être décoratif. Il sert à donner de la profondeur et de la structure.

## Surfaces

Les surfaces doivent organiser les contenus.

Elles peuvent représenter :

- zones de navigation ;
- blocs de synthèse ;
- panneaux ;
- tables ;
- formulaires ;
- dialogs ;
- sections de détails.

En light mode, les surfaces doivent rester lumineuses mais distinguables du fond. La distinction doit venir d'un contraste léger, de bordures fines ou d'une différence subtile de ton.

## Cartes

Les cartes doivent être utilisées pour des éléments regroupés ou répétés, pas pour encadrer chaque section de page.

En light mode, une carte doit donner une impression de précision et de calme. Elle ne doit pas flotter excessivement. La bordure est souvent préférable à une ombre marquée.

## Bordures

Les bordures doivent structurer sans durcir l'interface.

Elles servent à :

- séparer les lignes de table ;
- encadrer les inputs ;
- distinguer les cartes ;
- délimiter les dialogs ;
- séparer navigation et contenu.

En light mode, les bordures doivent être visibles mais discrètes.

## Texte

Le texte principal doit être très lisible.

Hiérarchie attendue :

- texte principal contrasté ;
- texte secondaire plus discret ;
- texte désactivé clairement atténué ;
- texte danger ou warning réservé aux contextes concernés ;
- texte monospace pour valeurs techniques.

La lisibilité prime sur la sophistication visuelle.

## Boutons

Les boutons doivent être clairement identifiables.

En light mode :

- le bouton Primary doit ressortir nettement ;
- les boutons Secondary et Outline doivent rester calmes ;
- les boutons Ghost doivent être visibles au hover et focus ;
- les boutons Danger doivent être immédiatement reconnaissables ;
- les états disabled doivent être compréhensibles sans paraître cassés.

## Formulaires

Les formulaires doivent être clairs et rassurants.

En light mode :

- les champs doivent être bien délimités ;
- les labels doivent être lisibles ;
- les erreurs doivent être visibles ;
- les textes d'aide doivent rester secondaires ;
- les champs sensibles doivent avoir une représentation spécifique ;
- le focus doit être évident.

# Dark Mode

Le dark mode est un mode de première classe.

Il ne doit pas être une simple inversion du light mode. Il doit être pensé pour une utilisation prolongée par des développeurs, DevOps, équipes IA et administrateurs.

Le dark mode doit préserver :

- lisibilité ;
- contraste ;
- hiérarchie ;
- distinction des états ;
- perception premium ;
- accessibilité ;
- confiance.

## Fond

Le fond principal doit être sombre, mais pas noir absolu.

Il doit réduire la fatigue visuelle tout en laissant assez de profondeur pour distinguer les surfaces. Un fond trop noir rend les contrastes agressifs. Un fond trop clair affaiblit l'identité dark.

## Surfaces

Les surfaces doivent se détacher du fond par des différences subtiles.

Elles doivent permettre de distinguer :

- navigation ;
- contenu principal ;
- tableaux ;
- panneaux ;
- dialogs ;
- cartes ;
- formulaires.

La différence entre fond et surface doit être suffisamment visible pour guider l'oeil, mais assez subtile pour rester premium.

## Cartes

Les cartes en dark mode doivent éviter l'effet de blocs lourds.

Elles peuvent utiliser :

- bordures discrètes ;
- surfaces légèrement plus claires ;
- ombres très subtiles si nécessaire ;
- séparateurs internes.

La carte ne doit pas ressembler à un élément décoratif. Elle doit contenir une unité d'information utile.

## Bordures

Les bordures en dark mode doivent être visibles sans créer une grille agressive.

Elles servent à renforcer la structure lorsque les différences de surface sont faibles.

Les séparateurs de table, inputs, panels et dialogs doivent être particulièrement soignés.

## Texte

Le texte en dark mode doit éviter deux écueils :

- être trop faible et fatigant ;
- être trop blanc et agressif.

Le texte principal doit être confortable. Les textes secondaires doivent rester lisibles. Les labels, erreurs, avertissements et badges doivent conserver leur contraste.

## Boutons

Les boutons en dark mode doivent conserver leurs rôles.

Le bouton Primary doit être visible sans créer une zone lumineuse excessive. Les boutons Ghost doivent être perceptibles au hover. Les boutons Danger doivent rester clairement dangereux.

## Formulaires

Les formulaires en dark mode doivent être particulièrement lisibles.

Les champs doivent être différenciés de la surface. Les erreurs doivent ressortir. Les textes d'aide doivent rester accessibles. Les champs sensibles doivent conserver un traitement clair et non ambigu.

# Typography

La typographie doit soutenir la précision, la lisibilité et la crédibilité technique du produit.

Elle doit fonctionner dans des contextes variés :

- dashboard ;
- navigation ;
- tables ;
- formulaires ;
- audit logs ;
- secrets ;
- permissions ;
- messages d'erreur ;
- dialogs ;
- paramètres.

## Police principale

La police principale doit être une sans-serif moderne, sobre et très lisible.

Elle doit offrir :

- bonne lisibilité sur petits formats ;
- chiffres lisibles ;
- excellente distinction des caractères ;
- rendu professionnel ;
- confort en light mode et dark mode.

Elle ne doit pas avoir une personnalité trop décorative. Le produit doit paraître professionnel avant de paraître original.

## Police monospace

La police monospace doit être utilisée pour les éléments techniques.

Usages :

- identifiants ;
- fragments de clés masquées ;
- chemins ;
- noms techniques ;
- valeurs structurées ;
- permissions ;
- slugs ;
- événements d'audit techniques ;
- code affiché dans la documentation interne future.

Elle doit être lisible, compacte et stable. Elle ne doit pas être utilisée pour de longs paragraphes.

## Hiérarchie des titres

Les titres doivent créer une structure claire sans occuper trop d'espace.

Règles :

- les titres de page sont nets et visibles ;
- les titres de section sont plus modestes ;
- les titres dans les cartes et panels restent compacts ;
- les titres de dialogs sont explicites ;
- les titres ne doivent pas masquer l'information opérationnelle.

Le produit doit éviter les titres géants hors contexte. L'interface est une console, pas une page marketing.

## Paragraphes

Les paragraphes doivent être courts, lisibles et utiles.

Ils sont utilisés pour :

- explications d'état vide ;
- messages d'aide ;
- descriptions de conséquences ;
- textes de confirmation ;
- onboarding léger.

Les paragraphes ne doivent pas remplacer une bonne structure d'interface. Si une page a besoin de trop d'explications, le design doit être revu.

## Labels

Les labels doivent être précis et cohérents.

Ils doivent :

- nommer clairement les champs ;
- éviter les abréviations ambiguës ;
- rester visibles ;
- accompagner les champs sensibles ;
- distinguer métadonnée et valeur ;
- expliquer les actions dangereuses.

Un label est un élément de sécurité. Il réduit les erreurs.

## Tableaux

La typographie des tableaux doit privilégier la scannabilité.

Règles :

- en-têtes lisibles ;
- cellules compactes ;
- dates lisibles ;
- statuts visibles ;
- identifiants techniques en monospace si utile ;
- texte tronqué avec accès au détail ;
- aucune cellule critique illisible.

Les tableaux doivent permettre de comparer rapidement les ressources.

## Code

Le code ou les éléments assimilés au code doivent utiliser la police monospace.

Leur rendu doit être :

- compact ;
- lisible ;
- différencié ;
- non décoratif ;
- compatible avec le copier lorsque cette action est prévue.

Il ne doit jamais afficher de secret complet par défaut.

## Secrets

Les secrets doivent avoir une représentation typographique spécifique.

Règles :

- valeur masquée par défaut ;
- fragments visibles uniquement si nécessaire ;
- monospace pour les fragments techniques ;
- distinction claire entre nom du secret et valeur ;
- action de révélation séparée ;
- action de copie explicite.

La typographie doit renforcer l'idée qu'une valeur secrète n'est pas un texte ordinaire.

## Badges

Les badges doivent utiliser une typographie compacte, lisible et stable.

Ils doivent être reconnaissables sans prendre trop d'espace. Les libellés doivent être courts, cohérents et non ambigus.

# Espacements

Les espacements doivent créer un rythme régulier et professionnel.

Ils servent à :

- clarifier les groupes ;
- rendre les tables lisibles ;
- séparer les actions ;
- réduire la fatigue visuelle ;
- guider la navigation ;
- maintenir une densité utile.

## Grille

Le design doit s'appuyer sur une grille régulière.

La grille doit permettre :

- alignements cohérents ;
- layouts responsive ;
- tables stables ;
- formulaires lisibles ;
- panels équilibrés ;
- navigation prévisible.

La grille doit rester flexible. Elle guide l'interface sans devenir rigide.

## Marges

Les marges de page doivent offrir de l'air sans gaspiller l'espace.

Les vues d'administration doivent éviter les marges excessives. Les écrans larges doivent utiliser l'espace intelligemment : tables plus lisibles, panneaux contextuels, colonnes de détail, mais pas de contenu étiré sans raison.

## Paddings

Les paddings doivent être cohérents par type de composant.

Les composants compacts comme badges, menus ou cellules de table utilisent des paddings réduits. Les dialogs, formulaires et panels de détail utilisent des paddings plus confortables.

Un padding incohérent est immédiatement visible dans un produit premium.

## Rythme vertical

Le rythme vertical doit rendre les pages faciles à scanner.

Chaque page doit distinguer :

- titre ;
- contexte ;
- actions ;
- filtres ;
- contenu ;
- détails secondaires.

Les espacements doivent indiquer la relation entre les éléments. Des éléments proches sont perçus comme liés. Des éléments séparés sont perçus comme distincts.

## Densité

La densité doit varier selon le contexte.

Règles :

- dashboard : densité moyenne ;
- tables : densité moyenne à élevée ;
- audit logs : densité élevée mais lisible ;
- formulaires : densité moyenne ;
- confirmations : densité plus aérée ;
- états vides : densité guidée ;
- mobile : densité adaptée, actions prioritaires.

La densité doit servir l'efficacité, jamais l'encombrement.

# Bordures

Les bordures donnent de la structure à l'interface.

Elles doivent être fines, sobres et cohérentes. MCP Secret Manager doit éviter les contours épais ou décoratifs.

## Radius

Le radius doit être modéré.

Les composants doivent paraître modernes sans devenir trop arrondis ou ludiques. Un radius contenu donne une impression de sérieux et de précision.

Les éléments concernés :

- boutons ;
- inputs ;
- cartes ;
- menus ;
- dialogs ;
- badges ;
- panneaux.

Le radius doit rester cohérent entre composants similaires.

## Épaisseur

Les bordures doivent généralement être fines.

Les bordures épaisses doivent être réservées à des cas exceptionnels comme :

- focus très visible ;
- état critique ;
- séparation structurelle forte.

Une bordure fine suffit dans la majorité des cas.

## Séparateurs

Les séparateurs doivent structurer les contenus denses.

Usages :

- lignes de table ;
- sections de détail ;
- navigation latérale ;
- panels ;
- groupes de paramètres ;
- zones de dialog.

Les séparateurs ne doivent pas créer une interface trop quadrillée. Ils doivent être visibles lorsque nécessaires, discrets sinon.

## Cartes

Les cartes doivent utiliser une bordure subtile ou une surface différenciée.

Le design doit éviter des cartes trop flottantes ou trop décoratives. Une carte sert à regrouper une unité d'information, pas à transformer chaque section en bloc isolé.

## Modales

Les modales doivent être clairement séparées du fond.

Elles peuvent utiliser :

- bordure visible ;
- surface distincte ;
- ombre maîtrisée ;
- arrière-plan atténué ;
- hiérarchie typographique claire.

La modale doit concentrer l'attention sans donner une impression dramatique sauf action réellement critique.

# Ombres

Les ombres doivent être utilisées avec retenue.

MCP Secret Manager doit privilégier les bordures, surfaces et séparateurs. Les ombres servent à établir une profondeur légère, pas à créer un effet visuel fort.

## Aucune ombre

Aucune ombre doit être le choix par défaut pour :

- tables ;
- sections standards ;
- inputs ;
- badges ;
- boutons ordinaires ;
- cartes simples ;
- navigation.

L'absence d'ombre renforce la sobriété et la précision.

## Ombre légère

Une ombre légère peut être utilisée pour :

- menus déroulants ;
- popovers ;
- tooltips ;
- petits panels flottants ;
- éléments superposés temporairement.

Elle doit aider à comprendre la superposition sans attirer excessivement l'attention.

## Ombre moyenne

Une ombre moyenne peut être utilisée pour :

- dialogs ;
- drawers ;
- overlays importants ;
- composants au-dessus d'une surface complexe.

Elle doit rester rare. Une ombre moyenne indique une élévation réelle dans l'interface.

# Icônes

Les icônes doivent soutenir la compréhension, pas remplacer les labels lorsque l'action n'est pas évidente.

## Style

Le style des icônes doit être :

- linéaire ;
- simple ;
- cohérent ;
- moderne ;
- non décoratif ;
- lisible en petite taille.

Les icônes doivent partager une même épaisseur visuelle. Mélanger plusieurs styles d'icônes nuit à la qualité perçue.

## Taille

Les icônes doivent rester proportionnées au composant.

Règles :

- petites icônes pour tables, menus et badges ;
- icônes moyennes pour boutons ;
- icônes plus visibles pour états vides ;
- jamais d'icône géante décorative dans les vues d'administration.

La taille doit favoriser la reconnaissance rapide.

## Utilisation

Les icônes sont utiles pour :

- actions fréquentes ;
- navigation ;
- statuts ;
- avertissements ;
- menus ;
- boutons icon-only avec tooltip ;
- états vides ;
- feedback.

Les actions sensibles doivent combiner icône, libellé et couleur lorsque nécessaire. Une icône seule ne suffit pas pour une action dangereuse.

## Cohérence

Une même action doit toujours utiliser la même icône.

Exemples :

- verrouiller ;
- archiver ;
- révoquer ;
- copier ;
- révéler ;
- masquer ;
- filtrer ;
- rechercher ;
- modifier ;
- supprimer ;
- confirmer.

Cette cohérence réduit l'effort d'apprentissage.

# Animations

Les animations doivent être discrètes, rapides et fonctionnelles.

Elles doivent aider l'utilisateur à comprendre un changement d'état, pas ralentir son travail. Elles ne doivent jamais masquer une erreur, retarder une action sensible ou créer une impression de produit instable.

## Durée

Les animations doivent être courtes.

Les micro-interactions comme hover, focus, menu ou tooltip doivent être presque immédiates. Les dialogs et transitions de panels peuvent être légèrement plus visibles, mais doivent rester rapides.

Une animation trop lente nuit à la perception de performance.

## Easing

L'easing doit être naturel et sobre.

Il doit éviter les rebonds, effets élastiques ou mouvements ludiques. MCP Secret Manager doit paraître sérieux et maîtrisé.

## Hover

Le hover doit indiquer l'interactivité.

Il peut changer :

- surface ;
- bordure ;
- couleur de texte ;
- fond ;
- visibilité d'une action secondaire.

Le hover doit rester subtil. Il ne doit pas modifier la mise en page.

## Focus

Le focus doit être visible, accessible et stable.

L'animation du focus, si présente, doit être très rapide. Le focus ne doit jamais être uniquement esthétique. Il sert à la navigation clavier et à la sécurité d'interaction.

## Ouverture de dialog

L'ouverture d'un dialog doit être fluide et immédiate.

L'animation peut aider à comprendre que l'utilisateur entre dans une décision isolée. Elle doit rester courte et ne pas retarder l'accès au contenu.

Les dialogs sensibles doivent apparaître clairement, sans effet dramatique inutile.

## Navigation

Les transitions de navigation doivent être sobres.

La priorité est la rapidité et la stabilité. Les changements de route doivent préserver le contexte et éviter les sauts visuels.

## Loading

Les animations de loading doivent rassurer.

Elles doivent indiquer que le système travaille, sans donner une impression de lenteur artificielle. Les skeletons sont préférables aux spinners lorsque la structure du contenu est connue.

# États

Les états visuels doivent être cohérents dans toute l'application.

Chaque état doit être reconnaissable par une combinaison de couleur, forme, texte, icône ou position. La couleur seule ne suffit jamais.

## Hover

Le hover indique qu'un élément est interactif.

Il doit :

- être visible ;
- rester subtil ;
- ne pas déplacer le layout ;
- ne pas masquer le texte ;
- ne pas créer de confusion avec l'état actif.

## Active

L'état active indique l'élément actuellement sélectionné ou engagé.

Usages :

- navigation courante ;
- tab actif ;
- filtre sélectionné ;
- bouton maintenu ;
- élément choisi.

L'état active doit être plus fort que hover, mais moins alarmant qu'un état danger.

## Disabled

L'état disabled indique qu'une action n'est pas disponible.

Il doit :

- être visuellement atténué ;
- rester lisible ;
- ne pas ressembler à une erreur ;
- être accompagné d'une explication lorsque la raison n'est pas évidente.

Pour des actions liées aux permissions, un tooltip ou message contextuel peut expliquer que l'action dépend d'un droit backend.

## Loading

L'état loading indique une action ou donnée en cours.

Il doit :

- empêcher les doubles soumissions ;
- préserver la structure ;
- afficher une progression si disponible ;
- ne pas faire croire que l'action est terminée ;
- être clair dans les actions sensibles.

## Success

L'état success confirme une action réussie ou une ressource saine.

Il doit :

- être bref lorsque lié à une action ;
- être visible lorsque lié à un statut ;
- ne pas masquer d'information importante ;
- ne pas être utilisé pour des situations ambiguës.

## Warning

L'état warning indique une attention nécessaire.

Il doit :

- attirer l'oeil ;
- expliquer le risque ;
- rester moins fort que danger ;
- proposer une action lorsque possible.

## Danger

L'état danger indique un risque fort, une erreur critique ou une action destructive.

Il doit :

- être immédiatement reconnaissable ;
- être utilisé avec parcimonie ;
- être accompagné d'un libellé clair ;
- apparaître dans les confirmations sensibles.

## Archived

L'état archived indique qu'une ressource n'est plus active mais reste consultable selon les règles backend.

Il doit :

- être distinct d'une suppression ;
- apparaître dans les listes et pages de détail ;
- atténuer les actions non disponibles ;
- expliquer les restrictions si nécessaire.

## Locked

L'état locked indique qu'un vault ou une ressource est verrouillé.

Il doit :

- être très visible ;
- indiquer que certaines actions sont bloquées ;
- ne pas être confondu avec archived ;
- être présent dans la navigation contextuelle lorsque le contexte est verrouillé.

## Revoked

L'état revoked indique qu'une clé ou un token n'est plus valide.

Il doit :

- être clairement différencié d'expiré ou désactivé ;
- être visible dans les listes ;
- empêcher les actions incompatibles ;
- rester consultable pour audit.

# Tables

Les tables sont un composant central de MCP Secret Manager.

Elles servent à présenter des ressources administrables : vaults, projects, secrets, versions, API keys, audit logs, rôles, permissions et futures données Enterprise.

## Présentation générale

Une table doit être :

- lisible ;
- dense sans être étouffante ;
- alignée ;
- filtrable lorsque pertinent ;
- compatible avec clavier ;
- responsive selon le contexte ;
- claire sur les actions disponibles.

Les tables ne doivent pas devenir des grilles décoratives. Elles sont des outils de travail.

## Colonnes

Les colonnes doivent être choisies selon la décision utilisateur attendue.

Principes :

- afficher les informations nécessaires au scan ;
- éviter les colonnes inutiles ;
- mettre le nom ou identifiant principal en premier ;
- afficher les statuts de manière visible ;
- placer les dates importantes dans un format lisible ;
- utiliser monospace pour identifiants techniques ;
- tronquer proprement les longues valeurs avec accès au détail.

Les valeurs secrètes complètes ne doivent jamais apparaître dans une table.

## Actions

Les actions de table doivent être cohérentes.

Règles :

- action principale clairement accessible ;
- actions secondaires dans un menu lorsque nombreuses ;
- actions dangereuses séparées ou visuellement distinctes ;
- tooltips pour boutons icon-only ;
- confirmation pour actions sensibles ;
- pas d'action ambiguë.

Les actions doivent toujours s'appliquer à la ligne visible et identifiable.

## Tri

Le tri doit être utilisé lorsque la comparaison est utile.

Champs pertinents :

- nom ;
- date de création ;
- dernière utilisation ;
- statut ;
- type ;
- acteur ;
- ressource ;
- résultat d'audit.

Le tri actif doit être visible et accessible.

## Pagination

La pagination doit préserver la performance et la lisibilité.

Règles :

- afficher l'état de pagination ;
- proposer navigation claire ;
- conserver les filtres ;
- éviter la perte de contexte ;
- adapter le modèle aux audit logs lorsque nécessaire.

La pagination ne doit pas masquer des erreurs de chargement.

## Filtres

Les filtres doivent être visibles lorsque leur usage est fréquent.

Filtres typiques :

- statut ;
- date ;
- acteur ;
- type d'action ;
- vault ;
- project ;
- permission ;
- résultat.

Les filtres actifs doivent être identifiables et faciles à retirer.

## Sélection

La sélection de lignes doit être utilisée avec prudence.

Les actions bulk sont sensibles dans un Secret Manager. Le MVP doit éviter les actions bulk dangereuses. Si une sélection existe, elle doit clairement indiquer :

- nombre d'éléments sélectionnés ;
- actions disponibles ;
- conséquences ;
- restrictions.

Aucune action bulk ne doit révéler des valeurs secrètes.

# Formulaires

Les formulaires doivent être clairs, accessibles et sûrs.

Ils sont utilisés pour créer ou modifier des ressources sensibles. Leur design doit réduire les erreurs avant soumission et rendre les conséquences explicites.

## Labels

Chaque champ doit avoir un label clair.

Le label doit :

- être visible ;
- utiliser le vocabulaire produit ;
- éviter les termes vagues ;
- distinguer metadata et value ;
- rester cohérent entre écrans.

Un placeholder ne remplace jamais un label.

## Erreurs

Les erreurs doivent être proches du champ concerné.

Elles doivent :

- expliquer le problème ;
- indiquer comment le corriger lorsque possible ;
- rester courtes ;
- être accessibles ;
- ne pas exposer de détail sensible.

Les erreurs globales de formulaire doivent apparaître dans une zone claire.

## Aide

Les textes d'aide doivent accompagner les champs ambigus ou sensibles.

Ils peuvent expliquer :

- format attendu ;
- conséquence d'une action ;
- visibilité d'une donnée ;
- règle de sécurité ;
- différence entre deux concepts.

L'aide doit être concise. Une interface qui nécessite trop d'aide doit être simplifiée.

## Validation

La validation doit être progressive.

Elle doit :

- éviter les erreurs évidentes avant soumission ;
- ne pas agresser l'utilisateur à la première frappe ;
- afficher les erreurs au bon moment ;
- rester cohérente avec les règles backend ;
- gérer les erreurs backend après soumission.

La validation frontend est une aide. Elle n'est pas une garantie de sécurité.

## Confirmations

Les formulaires déclenchant des actions sensibles doivent utiliser une confirmation adaptée.

La confirmation doit rappeler :

- ressource concernée ;
- action ;
- conséquence ;
- caractère réversible ou non ;
- éventuel impact sur les accès.

## Champs sensibles

Les champs sensibles doivent être traités différemment des champs ordinaires.

Règles :

- masquage par défaut ;
- révélation volontaire ;
- copie explicite ;
- pas d'autocomplétion non maîtrisée ;
- pas de persistance locale ;
- nettoyage après action ;
- message clair sur l'usage de la valeur.

Un champ de secret n'est jamais un simple input texte.

# Boutons

Les boutons doivent exprimer clairement l'importance et le risque de l'action.

La hiérarchie des boutons doit rester cohérente dans toute l'application.

## Primary

Le bouton Primary sert à l'action principale d'une vue ou d'un formulaire.

Usages :

- créer une ressource ;
- sauvegarder ;
- confirmer une action positive ;
- continuer un workflow principal ;
- lancer une action attendue.

Il ne doit pas y avoir plusieurs boutons Primary concurrents dans une même zone de décision.

## Secondary

Le bouton Secondary sert aux actions importantes mais non principales.

Usages :

- annuler sans danger ;
- ouvrir un détail ;
- accéder à une action complémentaire ;
- lancer un workflow secondaire.

Il soutient l'interface sans attirer plus que l'action principale.

## Outline

Le bouton Outline sert aux actions secondaires qui doivent rester visibles.

Usages :

- filtrer ;
- ouvrir un menu ;
- exporter des métadonnées non sensibles si prévu ;
- action contextuelle ;
- action alternative.

Il doit être lisible sur light mode et dark mode.

## Ghost

Le bouton Ghost sert aux actions discrètes.

Usages :

- actions de ligne ;
- icônes secondaires ;
- fermeture ;
- actions dans panels ;
- menus.

Il doit devenir visible au hover et au focus. Il ne doit pas être utilisé pour une action dangereuse sans signal visuel supplémentaire.

## Danger

Le bouton Danger sert aux actions destructives, sensibles ou à risque.

Usages :

- révoquer ;
- supprimer ;
- archiver lorsque l'impact est fort ;
- verrouiller ;
- retirer un rôle ;
- confirmer une action critique.

Il doit être accompagné d'un libellé explicite. Dans les dialogs critiques, il doit apparaître comme l'action de confirmation dangereuse.

## Success

Le bouton Success doit être rare.

Usages possibles :

- confirmer une opération positive explicitement sécurisée ;
- valider une étape terminée ;
- activer une configuration lorsque le contexte est clair.

Il ne doit pas remplacer le bouton Primary par goût esthétique.

# Badges

Les badges rendent les statuts, rôles, permissions et informations compactes immédiatement scannables.

Ils doivent être courts, cohérents et accessibles. La couleur seule ne suffit pas. Le libellé doit porter le sens.

## Status

Les badges Status indiquent l'état général d'une ressource.

Exemples :

- active ;
- inactive ;
- pending ;
- failed ;
- expired ;
- disabled.

Ils doivent être utilisés dans les tables, pages de détail et résumés.

## Permission

Les badges Permission représentent une capacité autorisée.

Exemples :

- read ;
- write ;
- create ;
- update ;
- delete ;
- audit read ;
- secret value read.

Ils doivent rester lisibles et éviter les libellés trop longs lorsque possible. Les permissions critiques doivent être reconnaissables.

## Role

Les badges Role représentent un rôle attribué.

Exemples :

- admin ;
- maintainer ;
- viewer ;
- service account ;
- future agent identity.

Ils doivent aider à distinguer rapidement la nature de l'acteur ou du niveau d'accès.

## Archived

Le badge Archived indique qu'une ressource est archivée.

Il doit être neutre ou légèrement atténué, mais suffisamment visible. Il ne doit pas être confondu avec Danger.

## Locked

Le badge Locked indique une restriction forte.

Il doit être plus visible qu'Archived. Il signale que certaines actions sont bloquées.

## Revoked

Le badge Revoked indique qu'une clé ou un token n'est plus utilisable.

Il doit être clairement reconnaissable et compatible avec les vues d'audit.

## Current Version

Le badge Current Version identifie la version actuellement utilisée d'un secret.

Il doit être visible dans l'historique des versions et ne pas être confondu avec un simple succès. Il indique une position fonctionnelle, pas seulement un état sain.

# Cards

Les cards servent à regrouper une unité d'information.

Elles ne doivent pas devenir le layout par défaut de toute page. MCP Secret Manager est une application d'administration ; les tables, listes, panels et sections structurées sont souvent plus efficaces.

## Quand utiliser une carte

Une carte est appropriée pour :

- indicateur de dashboard ;
- résumé de ressource ;
- état vide ;
- bloc de paramètre ;
- information contextuelle ;
- petit groupe d'actions ;
- ressource répétée dans un contexte non tabulaire ;
- contenu qui mérite une unité visuelle autonome.

Une carte doit avoir un objectif clair.

## Quand préférer une table

Une table est préférable lorsque l'utilisateur doit :

- comparer plusieurs ressources ;
- scanner des statuts ;
- trier ;
- filtrer ;
- agir sur des lignes ;
- lire des dates ou acteurs ;
- consulter un volume important.

Les listes de vaults, projects, secrets, API keys et audit logs doivent généralement privilégier les tables ou listes structurées.

## Règles de carte

Une carte doit :

- rester sobre ;
- avoir une bordure ou surface claire ;
- éviter les ombres fortes ;
- ne pas contenir une autre carte ;
- présenter une hiérarchie interne nette ;
- ne pas cacher des actions importantes.

# Dialogs

Les dialogs isolent une décision ou un formulaire important.

Ils doivent être utilisés avec discernement. Un dialog interrompt l'utilisateur ; cette interruption doit être justifiée.

## Confirmation

Un dialog de confirmation est utilisé lorsqu'une action a une conséquence sensible.

Il doit inclure :

- titre explicite ;
- ressource concernée ;
- conséquence ;
- action de confirmation ;
- action d'annulation ;
- niveau de risque.

Le texte doit être court, précis et non ambigu.

## Édition

Un dialog d'édition est approprié pour une modification courte.

Il doit :

- garder le contexte visible ;
- afficher les champs nécessaires seulement ;
- valider clairement ;
- indiquer les erreurs ;
- éviter de masquer des informations critiques.

Pour une édition complexe, une page dédiée est préférable.

## Suppression

Un dialog de suppression ou suppression logique doit être plus strict.

Il doit :

- nommer la ressource ;
- expliquer si l'action est réversible ;
- différencier suppression, archivage et révocation ;
- utiliser un bouton Danger ;
- demander une confirmation explicite si l'impact est fort.

## Révélation d'un secret

Un dialog ou composant de révélation de secret doit être traité comme une interaction de sécurité.

Règles :

- valeur masquée par défaut ;
- action volontaire ;
- indication que l'action peut être auditée ;
- affichage temporaire si possible ;
- copie explicite ;
- fermeture qui nettoie la valeur ;
- pas de persistance.

L'utilisateur doit comprendre qu'il franchit une frontière sensible.

## Création d'une API key

La création d'une API key nécessite une expérience spécifique.

Règles :

- expliquer le rôle de la clé ;
- présenter les permissions associées ;
- confirmer la création ;
- afficher la valeur complète uniquement lorsque le backend la fournit ;
- prévenir que la valeur ne sera plus récupérable si applicable ;
- proposer une action de copie claire ;
- nettoyer la valeur après fermeture.

Le moment de création d'une clé est critique. L'interface doit être calme, explicite et sûre.

# Empty States

Les empty states sont des moments importants de pédagogie.

Un écran vide ne doit pas ressembler à une erreur ou à une impasse. Il doit aider l'utilisateur à comprendre ce qu'il voit et quelle action peut suivre.

Chaque empty state doit :

- expliquer ;
- rassurer ;
- guider ;
- proposer une action.

## Expliquer

L'empty state doit dire pourquoi il n'y a pas de contenu.

Exemples :

- aucun vault n'a encore été créé ;
- aucun secret ne correspond aux filtres ;
- aucun audit log n'est disponible ;
- aucune API key active n'existe.

## Rassurer

L'empty state doit éviter l'inquiétude inutile.

Une absence d'audit log sur une instance fraîche peut être normale. Aucun secret dans un nouveau projet peut être attendu. Aucun résultat après filtre ne signifie pas que les données ont disparu.

## Guider

L'empty state doit orienter vers la prochaine étape.

Il peut indiquer :

- créer un vault ;
- créer un projet ;
- ajouter un secret ;
- ajuster les filtres ;
- créer une API key ;
- consulter la documentation future.

## Proposer une action

Si l'utilisateur a les permissions nécessaires, l'empty state doit proposer une action principale.

Si l'utilisateur n'a pas les permissions, il doit expliquer sobrement que l'action n'est pas disponible.

# Loading States

Les loading states doivent préserver la confiance.

L'utilisateur doit comprendre que le système charge ou traite une action. Il ne doit pas voir une interface cassée, vide sans explication ou ambiguë.

## Skeleton

Les skeletons sont privilégiés lorsque la structure du contenu est connue.

Usages :

- tables ;
- cards de dashboard ;
- pages de détail ;
- listes ;
- panels.

Ils doivent préserver les dimensions du contenu attendu pour éviter les sauts visuels.

## Spinner

Les spinners doivent être utilisés avec parcimonie.

Usages :

- action courte ;
- bouton en soumission ;
- chargement ponctuel ;
- zone dont la structure est inconnue.

Un spinner seul sur une page complète doit être évité si un skeleton ou état structuré est possible.

## Progress

Une indication de progression est utile lorsque l'action peut durer.

Usages futurs :

- import ;
- synchronisation ;
- rotation ;
- traitement ;
- export de métadonnées.

La progression doit être honnête. Elle ne doit pas simuler une précision inexistante.

## Optimistic feedback

Le feedback optimiste doit être prudent.

Il peut être utilisé pour des actions non sensibles et réversibles.

Il doit être évité pour :

- secrets ;
- révocations ;
- permissions ;
- actions destructives ;
- actions de sécurité ;
- création de clés API.

Pour ces actions, le feedback doit attendre la confirmation backend.

# Responsive Design

MCP Secret Manager est d'abord une application desktop et laptop, mais elle doit rester utilisable sur tablette et mobile.

Le responsive design doit préserver les priorités opérationnelles. Il ne suffit pas de réduire l'interface. Il faut réorganiser les informations selon le contexte d'usage.

## Desktop

Desktop est le contexte principal.

Priorités :

- tables complètes ;
- navigation latérale ou structurée ;
- actions contextuelles ;
- panels de détail ;
- filtres visibles ;
- comparaison rapide ;
- audit logs exploitables.

Les grands écrans doivent utiliser l'espace pour améliorer la lecture, pas pour agrandir artificiellement les éléments.

## Laptop

Laptop est le contexte quotidien le plus probable.

Priorités :

- densité équilibrée ;
- navigation efficace ;
- tables lisibles ;
- actions accessibles ;
- formulaires confortables ;
- aucune perte de fonctionnalité principale.

Le design doit être optimisé pour des hauteurs d'écran limitées.

## Tablet

Tablet doit permettre l'administration légère.

Priorités :

- consultation ;
- actions simples ;
- filtres essentiels ;
- dialogs lisibles ;
- tables adaptées ;
- navigation claire.

Les tables peuvent devenir des listes structurées lorsque l'espace horizontal est insuffisant.

## Mobile

Mobile doit permettre des actions rapides et sûres.

Priorités :

- consulter un état ;
- vérifier un audit log ;
- révoquer une clé si nécessaire ;
- confirmer une information ;
- naviguer vers une ressource ;
- gérer une urgence limitée.

Le mobile ne doit pas forcément offrir le même confort que desktop pour les opérations complexes, mais il ne doit jamais rendre une action sensible confuse.

# Accessibilité visuelle

L'accessibilité visuelle est une exigence de qualité et de sécurité.

Elle doit être intégrée dès le design initial.

## Contrastes

Les contrastes doivent permettre une lecture confortable.

Attention particulière :

- texte secondaire ;
- badges ;
- erreurs ;
- warnings ;
- disabled ;
- placeholders ;
- bordures d'input ;
- dark mode ;
- focus.

Un contraste insuffisant peut provoquer une erreur d'interprétation.

## Focus

Le focus doit être visible dans tous les thèmes.

Il doit permettre de savoir exactement quel élément est actif. Les composants interactifs doivent tous avoir un état focus clair.

Le focus ne doit pas être masqué pour des raisons esthétiques.

## Taille des cibles

Les cibles interactives doivent être suffisamment grandes.

Cela concerne :

- boutons ;
- menus ;
- actions de table ;
- checkboxes ;
- switches ;
- tabs ;
- icônes cliquables ;
- zones de fermeture de dialog.

Les actions dangereuses doivent être particulièrement faciles à identifier et difficiles à déclencher par erreur.

## Couleurs

La couleur ne doit jamais être la seule information.

Un statut doit combiner :

- couleur ;
- texte ;
- forme ;
- icône si utile ;
- position cohérente.

Cette règle est obligatoire pour les états success, warning, danger, archived, locked et revoked.

## Lisibilité

La lisibilité doit primer sur l'originalité.

Les textes doivent être suffisamment grands, les lignes suffisamment espacées et les éléments techniques suffisamment distincts. Les tables doivent rester lisibles même lorsque les données sont longues.

# Design Principles

Les règles suivantes doivent être respectées pendant tout le projet.

- Le produit doit paraître professionnel avant de paraître original.
- La couleur n'est jamais la seule information.
- Les actions dangereuses sont toujours identifiables.
- Une valeur secrète n'est jamais affichée par défaut.
- Une valeur secrète n'est jamais affichée en masse.
- Les valeurs sensibles ne sont jamais décoratives.
- Les confirmations sensibles doivent nommer la ressource concernée.
- Les animations ne doivent jamais ralentir l'utilisateur.
- Les animations doivent clarifier un changement, pas attirer l'attention sur elles-mêmes.
- Chaque écran doit avoir une hiérarchie claire.
- Chaque page doit indiquer le contexte actif.
- Un vault verrouillé doit être visuellement distinct d'un vault archivé.
- Une API key révoquée doit être immédiatement identifiable.
- Une version courante doit être distinguée des versions historiques.
- Les erreurs doivent être actionnables sans révéler d'information sensible.
- Les états vides doivent expliquer, rassurer, guider et proposer une action.
- Les tables doivent privilégier la scannabilité.
- Les formulaires doivent réduire les erreurs avant soumission.
- Les champs sensibles doivent être conçus comme des composants de sécurité.
- Les boutons Primary doivent être rares et évidents.
- Les boutons Danger doivent être réservés aux actions à risque.
- Les dialogs doivent être utilisés lorsque l'interruption est justifiée.
- Les cartes ne doivent pas remplacer systématiquement les tables.
- Les composants partagés doivent rester cohérents en light mode et dark mode.
- Le dark mode est un mode de première classe.
- Les icônes doivent soutenir le sens, pas le remplacer.
- Les textes doivent rester courts, précis et utiles.
- L'interface doit rester sobre même lorsqu'elle présente une information critique.
- La densité doit servir l'efficacité, jamais l'encombrement.
- La sécurité doit être visible sans devenir anxiogène.
- Le design doit réduire la charge mentale de l'utilisateur.
- Les décisions visuelles doivent rester cohérentes avec l'architecture frontend.
- Aucun écran ne doit encourager un contournement du Secret Manager.

# Conclusion

Le Design System de MCP Secret Manager doit construire une interface de confiance pour un produit de sécurité moderne.

Sa philosophie est claire : sobriété, précision, lisibilité, modernité et rigueur. Le produit doit être premium sans être ostentatoire, technique sans être froid, dense sans être confus, sécurisé sans être paralysant.

Chaque composant doit aider l'utilisateur à comprendre ce qu'il voit et ce qu'il peut faire. Les tables doivent être scannables. Les formulaires doivent être sûrs. Les dialogs doivent clarifier les conséquences. Les badges doivent rendre les statuts immédiatement lisibles. Les valeurs secrètes doivent rester masquées par défaut. Les actions dangereuses doivent être identifiables et confirmées.

Le light mode et le dark mode doivent recevoir le même niveau d'attention. Les couleurs, typographies, espacements, bordures, ombres, icônes et animations doivent former une identité cohérente, professionnelle et durable.

Ce Design System doit permettre à l'équipe produit et frontend de construire MCP Secret Manager avec une qualité constante, écran après écran, sans perdre la vision centrale : offrir une console SaaS moderne, fiable et sécurisée pour administrer les secrets des infrastructures IA, DevOps et MCP.
