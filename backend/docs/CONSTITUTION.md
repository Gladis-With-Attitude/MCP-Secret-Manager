# Constitution du projet MCP Secret Manager

Cette Constitution définit les principes fondamentaux de MCP Secret Manager.

Elle n'est pas une documentation technique, une roadmap ou un guide utilisateur. Elle est le cadre de décision du projet.

Toute Pull Request, décision d'architecture, fonctionnalité, dépendance ou modification de comportement doit respecter cette Constitution.

Lorsqu'un choix est difficile, cette Constitution prévaut sur les préférences individuelles, la commodité immédiate et la vitesse de développement.

## Article 1 - Security First

**Principe**

La sécurité est la priorité absolue du projet.

**Pourquoi**

MCP Secret Manager protège des secrets capables de donner accès à une infrastructure, des comptes tiers, des agents IA, des services MCP et des systèmes applicatifs. Une erreur de sécurité peut compromettre bien plus que l'application elle-même.

**Conséquences concrètes**

- Une fonctionnalité utile peut être refusée si elle affaiblit la sécurité.
- Les comportements dangereux ne doivent pas être activés par défaut.
- Les raccourcis de développement ne doivent jamais devenir des comportements de production.
- Toute modification liée à l'authentification, aux permissions, à la crypto ou à l'audit exige une revue stricte.

## Article 2 - Least Privilege

**Principe**

Chaque acteur doit recevoir uniquement les permissions nécessaires à son action.

**Pourquoi**

Les utilisateurs, services, agents IA et serveurs MCP ne doivent jamais disposer d'un accès plus large que leur besoin réel. Le rayon d'impact d'une compromission doit être aussi petit que possible.

**Conséquences concrètes**

- Lire les métadonnées d'un secret ne donne pas le droit de lire sa valeur.
- Administrer une ressource ne donne pas automatiquement le droit de révéler tous les secrets.
- OpenClaw, les agents et les comptes de service doivent utiliser des permissions minimales.
- Les accès larges doivent être explicitement justifiés, documentés et testés.

## Article 3 - Fail Closed

**Principe**

En cas d'erreur, d'ambiguïté ou d'état incomplet, le système doit refuser l'accès.

**Pourquoi**

Un Secret Manager ne doit jamais deviner une intention de sécurité. Une permission absente, une configuration invalide ou une erreur interne doit produire un refus sûr, pas un accès permissif.

**Conséquences concrètes**

- L'absence de permission équivaut à un refus.
- Une erreur d'évaluation des permissions équivaut à un refus.
- Une clé, un vault ou un secret dans un état invalide ne doit pas être utilisé.
- Les erreurs doivent être sûres, explicites et auditables.

## Article 4 - Audit Everything

**Principe**

Toute action sensible doit être auditée.

**Pourquoi**

La sécurité ne repose pas uniquement sur la prévention. Le projet doit permettre de comprendre ce qui s'est passé, qui a agi, quelle ressource était concernée et quelle décision a été prise.

**Conséquences concrètes**

- Les lectures de valeurs secrètes doivent être auditables.
- Les refus d'accès doivent être auditables.
- Les changements de permissions, tokens, vaults et secrets doivent être auditables.
- Les logs et événements d'audit ne doivent jamais contenir de valeur secrète.

## Article 5 - Documentation Before Code

**Principe**

Les décisions structurantes doivent être documentées avant ou avec leur implémentation.

**Pourquoi**

MCP Secret Manager est un composant de confiance. Son comportement doit être compréhensible, explicite et durable. Le code seul ne suffit pas à porter les invariants de sécurité et les choix d'architecture.

**Conséquences concrètes**

- Une PR qui change un comportement public doit mettre à jour la documentation.
- Une PR qui introduit un nouveau concept de sécurité doit l'expliquer.
- Une décision non documentée ne doit pas devenir une convention implicite.
- La documentation fait partie du produit.

## Article 6 - Simplicity Before Complexity

**Principe**

La solution la plus simple qui respecte les garanties de sécurité doit être préférée.

**Pourquoi**

La complexité est un risque opérationnel et un risque de sécurité. Un système simple est plus facile à comprendre, tester, auditer, déployer et maintenir.

**Conséquences concrètes**

- Le MVP doit rester petit.
- Les abstractions doivent résoudre un problème réel.
- Les systèmes de permissions avancés ne doivent pas être introduits avant d'être nécessaires.
- Une fonctionnalité complexe doit démontrer sa valeur avant d'être acceptée.

## Article 7 - Explicit Over Implicit

**Principe**

Les comportements de sécurité doivent être explicites.

**Pourquoi**

Les décisions implicites créent des surprises. Dans un Secret Manager, une surprise peut devenir une faille.

**Conséquences concrètes**

- Les permissions doivent être nommées.
- Les rôles doivent être compréhensibles.
- Les endpoints, tools MCP et commandes CLI doivent exprimer clairement leur effet.
- Les conversions, héritages et valeurs par défaut liés à la sécurité doivent être limités et documentés.

## Article 8 - AI First

**Principe**

Le projet doit être conçu pour des systèmes agentiques, pas seulement pour des humains et applications classiques.

**Pourquoi**

Les agents IA peuvent appeler des outils, déléguer des tâches, être influencés par leur contexte et demander des secrets dans des situations imprévues. Cette réalité doit guider l'architecture.

**Conséquences concrètes**

- Les agents doivent être considérés comme des acteurs de sécurité à part entière.
- Les réponses destinées aux agents doivent être minimales.
- Les accès agents doivent pouvoir évoluer vers des TTL courts, quotas, budgets et justifications.
- Toute nouvelle surface d'accès doit être évaluée face aux risques de prompt injection et d'abus d'outil.

## Article 9 - MCP Native

**Principe**

MCP est une interface de première classe du projet.

**Pourquoi**

MCP Secret Manager existe pour servir des agents et orchestrateurs compatibles MCP. Le serveur MCP n'est pas un simple adaptateur autour de l'API REST ; c'est une surface produit et sécurité majeure.

**Conséquences concrètes**

- Les tools MCP doivent respecter les mêmes permissions que les autres interfaces.
- Aucun tool MCP ne doit exposer plus que nécessaire.
- Les réponses MCP doivent être limitées, prévisibles et auditables.
- Les changements MCP doivent être revus comme des changements de sécurité.

## Article 10 - OpenClaw First

**Principe**

OpenClaw est le premier consommateur officiel du projet.

**Pourquoi**

Le projet naît pour servir une infrastructure IA personnelle centrée sur OpenClaw. Le MVP doit résoudre ce cas d'usage avant de généraliser.

**Conséquences concrètes**

- Les décisions MVP doivent privilégier l'intégration OpenClaw.
- OpenClaw doit utiliser un rôle minimal et révocable.
- Les scénarios OpenClaw doivent rester documentés et testés.
- Une fonctionnalité générique ne doit pas retarder inutilement le besoin OpenClaw validé.

## Article 11 - Test Before Merge

**Principe**

Une modification ne doit pas être fusionnée sans tests adaptés à son risque.

**Pourquoi**

Les erreurs dans un Secret Manager sont coûteuses. Les tests sont une barrière de sécurité, de maintenance et de confiance.

**Conséquences concrètes**

- Toute logique de permission doit avoir des tests de refus et d'autorisation.
- Toute correction de bug doit ajouter un test de non-régression.
- Toute logique cryptographique doit être testée contre les erreurs attendues.
- Les tests manquants doivent être explicitement justifiés.

## Article 12 - Backward Compatibility

**Principe**

Les contrats publics doivent rester stables autant que possible.

**Pourquoi**

Un Secret Manager devient rapidement une dépendance d'infrastructure. Les clients, scripts, agents et serveurs MCP doivent pouvoir évoluer sans ruptures imprévisibles.

**Conséquences concrètes**

- Les changements d'API doivent être versionnés ou compatibles.
- Les migrations de données doivent être documentées.
- Les formats d'audit ne doivent pas changer sans justification.
- Une rupture peut être acceptée si elle corrige un risque de sécurité réel.

## Article 13 - No Home-Made Cryptography

**Principe**

Le projet ne doit jamais inventer ses propres primitives cryptographiques.

**Pourquoi**

La cryptographie est difficile à concevoir, implémenter et auditer. La sécurité du projet doit reposer sur des primitives reconnues, des bibliothèques éprouvées et des usages documentés.

**Conséquences concrètes**

- Pas d'algorithme de chiffrement maison.
- Pas de protocole cryptographique improvisé.
- Pas de génération aléatoire non sécurisée.
- Les choix crypto doivent être documentés, testés et revus avec prudence.

## Article 14 - Small Pull Requests

**Principe**

Les Pull Requests doivent être petites, ciblées et fusionnables indépendamment.

**Pourquoi**

Les changements massifs cachent les erreurs, ralentissent les revues et augmentent le risque de régression. Un projet de sécurité doit favoriser les incréments clairs.

**Conséquences concrètes**

- Une PR doit résoudre un problème principal.
- Les refactorings non liés doivent être séparés.
- Les changements de sécurité doivent être isolés autant que possible.
- Une PR trop large peut être refusée même si son intention est correcte.

## Article 15 - Extensibility Without Premature Complexity

**Principe**

Le projet doit être extensible sans introduire de complexité avant qu'elle soit nécessaire.

**Pourquoi**

MCP Secret Manager doit pouvoir évoluer vers des Secret Providers, identités d'agents, politiques avancées et intégrations futures. Mais une extensibilité trop abstraite dès le départ rend le système fragile et difficile à auditer.

**Conséquences concrètes**

- Les points d'extension doivent être identifiés clairement.
- Les abstractions doivent rester minimales au MVP.
- Les providers futurs ne doivent pas complexifier le provider local initial.
- Une architecture ouverte ne doit pas devenir un système de plugins prématuré.

## Résoudre un conflit entre deux principes

Les principes de cette Constitution sont complémentaires, mais des tensions peuvent apparaître.

Lorsqu'un conflit survient, l'ordre de priorité est le suivant :

1. Sécurité des secrets et des utilisateurs.
2. Refus sûr en cas d'ambiguïté.
3. Principe du moindre privilège.
4. Auditabilité.
5. Correction cryptographique.
6. Clarté et documentation.
7. Simplicité.
8. Compatibilité.
9. Extensibilité.
10. Vitesse de développement.

### Sécurité contre rétrocompatibilité

Si la rétrocompatibilité entre en conflit avec la sécurité, la sécurité gagne.

Une rupture est acceptable lorsqu'elle corrige un comportement dangereux, mais elle doit être documentée, versionnée si possible et accompagnée d'un chemin de migration raisonnable.

### Simplicité contre extensibilité

Si la simplicité entre en conflit avec l'extensibilité, la simplicité gagne pour le MVP.

L'extensibilité doit être prévue par des frontières claires, pas par des abstractions spéculatives. Une abstraction devient acceptable lorsqu'elle simplifie un besoin réel ou prépare une évolution déjà validée.

### OpenClaw First contre généralisation

Si une fonctionnalité générique retarde fortement le cas d'usage OpenClaw validé, OpenClaw gagne pour le MVP.

La généralisation doit arriver après une intégration réelle, testée et documentée.

### MCP Native contre API REST

MCP et REST doivent partager les mêmes garanties de sécurité.

Aucune interface ne doit obtenir de privilège spécial. Si une divergence est nécessaire pour des raisons de protocole, elle doit être documentée et revue comme une décision de sécurité.

### Vitesse contre qualité

Si la vitesse de développement entre en conflit avec les tests, la documentation, l'audit ou la sécurité, la vitesse perd.

MCP Secret Manager est une infrastructure de confiance. Il vaut mieux livrer moins vite qu'installer une faiblesse durable.

## Clause finale

Cette Constitution doit rester stable, courte et exigeante.

Elle peut évoluer, mais seulement lorsque l'expérience du projet démontre qu'un principe doit être clarifié, renforcé ou corrigé.

Une modification de cette Constitution doit être traitée comme une décision majeure du projet.

