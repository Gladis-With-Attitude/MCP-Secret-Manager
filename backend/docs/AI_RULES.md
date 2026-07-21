# Règles de développement assisté par IA

Ce document définit les règles officielles applicables aux assistants IA, agents de développement et outils automatisés qui contribuent à MCP Secret Manager.

Il décrit ce qu'une IA peut faire, ce qu'elle ne doit jamais faire, le workflow attendu et les invariants qui doivent être respectés lors de toute contribution assistée.

Ce document ne contient pas de code. Il définit une gouvernance.

## 1. Objectifs

### Pourquoi le projet est AI-first

MCP Secret Manager est conçu pour une infrastructure où les agents IA, serveurs MCP et orchestrateurs jouent un rôle central.

Le projet est AI-first dans son produit, mais aussi dans sa manière de travailler. Les assistants IA peuvent aider à :

- produire de la documentation ;
- analyser l'architecture ;
- écrire du code ;
- écrire des tests ;
- détecter des incohérences ;
- améliorer la qualité ;
- accélérer les revues ;
- préparer des migrations ;
- expliquer des décisions.

Cette capacité est un avantage, mais elle introduit aussi des risques.

### Pourquoi les IA doivent suivre des règles strictes

Un assistant IA peut produire rapidement du contenu plausible, mais incorrect, incomplet ou dangereux.

Dans un Secret Manager, ces erreurs peuvent être critiques.

Risques spécifiques :

- invention de comportements non documentés ;
- contournement involontaire des permissions ;
- affaiblissement de la crypto ;
- suppression de tests ;
- ajout de dépendances risquées ;
- incohérence entre REST et MCP ;
- fuite de secrets ;
- refactorings trop larges ;
- modifications non alignées avec l'architecture ;
- documentation trompeuse.

Les règles de ce document existent pour canaliser la contribution IA vers un travail vérifiable, explicite et sûr.

### Pourquoi les humains gardent la décision finale

Les humains restent responsables des décisions finales.

Une IA peut proposer, analyser, implémenter ou relire, mais elle ne doit pas être considérée comme l'autorité finale sur :

- architecture ;
- sécurité ;
- cryptographie ;
- modèle de permissions ;
- migrations ;
- releases ;
- incidents ;
- acceptation d'une Pull Request.

La décision finale appartient aux mainteneurs humains du projet.

## 2. Principes

### Documentation Before Code

Une IA doit respecter la documentation comme source de vérité.

Avant de modifier un comportement public ou une règle de sécurité, elle doit vérifier les documents pertinents :

- `backend/docs/PROJECT.md` ;
- `backend/docs/CONSTITUTION.md` ;
- `backend/docs/ARCHITECTURE.md` ;
- `backend/docs/SECURITY.md` ;
- `backend/docs/DATABASE.md` ;
- `backend/docs/CRYPTOGRAPHY.md` ;
- `backend/docs/API_SPEC.md` ;
- `backend/docs/MCP_SPEC.md` ;
- `backend/docs/TESTING.md`.

Conséquences :

- pas de fonctionnalité non documentée ;
- pas de changement de comportement sans mise à jour documentaire ;
- pas de divergence silencieuse avec les spécifications ;
- les décisions structurantes doivent être expliquées avant implémentation.

### Security First

Une IA doit traiter MCP Secret Manager comme un produit de sécurité.

Conséquences :

- refus par défaut ;
- least privilege ;
- pas de secret dans logs ;
- pas de contournement de permissions ;
- pas de cryptographie maison ;
- tests obligatoires pour les changements sensibles ;
- prudence sur les dépendances.

Si un choix améliore la vitesse mais réduit la sécurité, il doit être refusé.

### Small Changes

Une IA doit privilégier les changements petits, ciblés et relisibles.

Conséquences :

- une PR doit résoudre un problème principal ;
- les refactorings massifs doivent être évités ;
- les changements mécaniques doivent être séparés des changements métier ;
- les modifications sécurité doivent être isolées autant que possible.

Un changement trop large est difficile à auditer, même s'il semble correct.

### Explain Before Modify

Une IA doit expliquer ce qu'elle compte changer avant de modifier des zones sensibles.

Conséquences :

- annoncer l'intention ;
- identifier les fichiers concernés ;
- expliquer les risques ;
- préciser les tests attendus ;
- demander validation humaine lorsqu'une décision structurante est nécessaire.

Ce principe ne signifie pas bloquer chaque petite modification, mais il s'applique strictement aux zones critiques.

### No Hidden Behaviour

Une IA ne doit pas introduire de comportement caché.

Conséquences :

- pas de fallback silencieux dangereux ;
- pas de permission implicite ;
- pas de configuration magique ;
- pas d'accès réseau inattendu ;
- pas de génération automatique de secrets en production sans action explicite ;
- pas de comportement différent entre REST et MCP sans documentation.

Tout comportement important doit être visible, documenté et testable.

### Explicit Assumptions

Une IA doit expliciter ses hypothèses.

Conséquences :

- distinguer faits observés et suppositions ;
- signaler les incertitudes ;
- ne pas inventer de contexte ;
- vérifier localement lorsque possible ;
- demander clarification si une hypothèse risquée est nécessaire.

Dans un projet de sécurité, une hypothèse implicite peut devenir une faille.

### Deterministic Outputs

Une IA doit produire des changements déterministes et reproductibles.

Conséquences :

- pas de génération aléatoire non contrôlée dans les artefacts ;
- pas de modifications dépendantes de l'heure ou de l'environnement sans justification ;
- pas de formatage instable ;
- pas de tests flaky ;
- pas de dépendance à Internet dans les tests ordinaires.

### Respect Existing Architecture

Une IA doit respecter les frontières définies par l'architecture.

Conséquences :

- REST et MCP passent par l'Application Layer ;
- Domain ne dépend pas de FastAPI, MCP ou PostgreSQL ;
- Crypto ne décide pas des permissions ;
- Audit ne voit jamais les valeurs secrètes ;
- Infrastructure ne porte pas de politique métier cachée.

L'architecture n'est pas une suggestion. Elle est une contrainte du projet.

## 3. Ce qu'une IA peut faire

Une IA peut contribuer aux tâches suivantes, sous réserve de respecter la documentation, les tests et les règles de sécurité.

### Écrire du code

Une IA peut écrire du code applicatif lorsque :

- le comportement est documenté ;
- l'architecture est respectée ;
- les tests sont ajoutés ou mis à jour ;
- les hypothèses sont explicites ;
- les changements restent ciblés.

### Écrire des tests

Une IA peut écrire :

- tests unitaires ;
- tests d'intégration ;
- tests REST ;
- tests MCP ;
- tests de sécurité ;
- tests de migration ;
- tests de régression.

Les tests générés doivent être déterministes et vérifier des comportements réels.

### Écrire de la documentation

Une IA peut rédiger ou améliorer :

- documentation d'architecture ;
- spécifications ;
- guides opérateur ;
- ADR ;
- documentation API ;
- documentation MCP ;
- documentation de sécurité ;
- notes de migration.

La documentation doit être exacte, claire et alignée avec le comportement réel.

### Proposer des refactorings

Une IA peut proposer des refactorings si :

- ils réduisent une complexité réelle ;
- ils ne changent pas le comportement sans le dire ;
- ils restent petits ;
- ils sont testés ;
- ils respectent les couches.

### Générer des migrations

Une IA peut proposer des migrations si :

- `backend/docs/DATABASE.md` est respecté ;
- les fichiers sont placés sous `db/migrations/` ;
- la configuration Alembic sous `db/alembic.ini` reste cohérente avec le monorepo ;
- les données historiques sont préservées ;
- les migrations sont testées ;
- les effets de rollback sont documentés ;
- aucune valeur secrète n'est exposée.

### Expliquer du code

Une IA peut expliquer :

- flux applicatifs ;
- décisions d'architecture ;
- comportements de sécurité ;
- erreurs ;
- tests ;
- migrations ;
- divergences possibles.

Elle doit distinguer ce qui est présent dans le code de ce qui est une inférence.

### Améliorer les performances

Une IA peut proposer des améliorations de performance si :

- elles ne contournent pas la sécurité ;
- elles ne suppriment pas l'audit ;
- elles ne mettent pas de secrets en cache en clair ;
- elles sont mesurées ;
- elles restent compatibles avec les invariants.

### Détecter des incohérences

Une IA peut analyser le projet pour détecter :

- incohérences entre docs et code ;
- divergences REST/MCP ;
- tests manquants ;
- permissions incohérentes ;
- duplications dangereuses ;
- complexité excessive ;
- dépendances inutiles ;
- risques de sécurité.

## 4. Ce qu'une IA ne doit jamais faire

Une IA ne doit jamais :

- modifier l'architecture sans ADR ou validation humaine ;
- contourner RBAC ;
- contourner l'Application Layer ;
- ajouter une dépendance critique sans justification ;
- désactiver des tests critiques pour faire passer la CI ;
- supprimer de la documentation validée sans raison explicite ;
- inventer des comportements non spécifiés ;
- introduire des secrets dans le dépôt ;
- logger des secrets ;
- exposer des tokens complets ;
- contourner la crypto ;
- implémenter une primitive cryptographique maison ;
- modifier la stratégie crypto sans documentation ;
- ajouter un endpoint ou tool MCP qui lit des secrets en masse au MVP ;
- mélanger metadata et value ;
- ignorer un échec de test ;
- masquer une erreur de sécurité ;
- transformer un refus en succès silencieux ;
- introduire un fallback de clé par défaut en production ;
- rendre OpenClaw admin par facilité ;
- accorder des permissions implicites aux agents ;
- changer une migration historique sans justification stricte ;
- faire une réécriture massive non demandée ;
- modifier des fichiers sans rapport avec la tâche ;
- présenter une hypothèse comme un fait.

## 5. Workflow recommandé

Le workflow recommandé pour une contribution assistée par IA est :

```text
Analyse
  -> Plan
    -> Validation
      -> Implémentation
        -> Tests
          -> Documentation
```

Une IA ne doit pas sauter ces étapes pour une modification significative.

### Analyse

L'IA doit comprendre :

- la demande ;
- les documents applicables ;
- les fichiers concernés ;
- les invariants ;
- les risques.

Elle doit lire le contexte local avant de proposer un changement.

### Plan

L'IA doit proposer un plan proportionné au risque.

Le plan doit indiquer :

- les composants touchés ;
- les comportements attendus ;
- les tests nécessaires ;
- la documentation à mettre à jour ;
- les risques éventuels.

### Validation

Une validation humaine est requise lorsque le changement touche :

- architecture ;
- sécurité ;
- crypto ;
- permissions ;
- audit ;
- modèle de données ;
- API publique ;
- MCP ;
- migrations sensibles.

Pour les petites corrections non sensibles, la validation peut être implicite dans la demande.

### Implémentation

L'implémentation doit être :

- ciblée ;
- alignée avec l'architecture ;
- lisible ;
- testable ;
- sans comportement caché.

### Tests

L'IA doit exécuter ou proposer les tests adaptés.

Si les tests ne peuvent pas être exécutés, elle doit le dire clairement.

### Documentation

La documentation doit être mise à jour lorsque :

- un comportement public change ;
- un invariant change ;
- une API change ;
- un tool MCP change ;
- une migration importante est ajoutée ;
- une décision de sécurité est prise.

## 6. Modifications sensibles

Certaines zones exigent une prudence renforcée.

### Crypto

Exigences supplémentaires :

- respecter `backend/docs/CRYPTOGRAPHY.md` ;
- aucun algorithme maison ;
- tests d'échec ;
- revue humaine obligatoire ;
- documentation obligatoire ;
- pas de changement silencieux de format ou algorithme.

### Permissions

Exigences supplémentaires :

- tests allowed et denied ;
- refus par défaut ;
- pas de permission implicite ;
- documentation des nouvelles permissions ;
- cohérence REST/MCP.

### Audit

Exigences supplémentaires :

- aucun secret dans audit ;
- tests de succès et refus ;
- champ client_type correct ;
- actions sensibles couvertes ;
- conservation du sens des événements historiques.

### API

Exigences supplémentaires :

- respecter `backend/docs/API_SPEC.md` ;
- stable contracts ;
- erreurs sûres ;
- pagination pour les listes ;
- documentation des changements ;
- tests REST.

### MCP

Exigences supplémentaires :

- respecter `backend/docs/MCP_SPEC.md` ;
- tool explicite ;
- réponses minimales ;
- pas de privilège supplémentaire ;
- tests MCP ;
- audit client_type MCP.

### Database

Exigences supplémentaires :

- respecter `backend/docs/DATABASE.md` ;
- préserver l'intégrité référentielle ;
- préserver les invariants ;
- ne pas stocker de secret en clair ;
- documenter toute nouvelle entité.

### Migrations

Exigences supplémentaires :

- test sur base vide ;
- test sur base existante ;
- données historiques préservées ;
- rollback documenté si possible ;
- pas de migration destructive implicite ;
- revue humaine obligatoire pour migrations sensibles.

## 7. Interaction avec Codex / OpenClaw

### Prompts attendus

Les demandes faites à Codex, OpenClaw ou un autre assistant IA doivent être précises.

Un bon prompt indique :

- objectif ;
- périmètre ;
- fichiers concernés si connus ;
- contraintes ;
- documents à respecter ;
- interdictions ;
- niveau de risque ;
- tests attendus.

### Réponses attendues

Une réponse IA de qualité doit :

- reformuler brièvement l'objectif si utile ;
- expliquer les hypothèses ;
- identifier les risques ;
- proposer un plan lorsque le changement est significatif ;
- effectuer des modifications ciblées ;
- exécuter ou indiquer les tests ;
- résumer les résultats ;
- signaler clairement ce qui n'a pas été vérifié.

### Limites

Une IA peut se tromper.

Elle peut :

- halluciner une API ;
- oublier une contrainte ;
- proposer une abstraction inutile ;
- sous-estimer un risque sécurité ;
- ignorer une documentation ;
- produire une réponse plausible mais fausse.

Les contributions IA doivent donc être relues avec attention.

### Vérifications humaines

Un humain doit vérifier :

- alignement avec la Constitution ;
- respect de l'architecture ;
- absence de fuite de secrets ;
- tests critiques ;
- documentation ;
- dépendances ;
- migrations ;
- impact sécurité.

Les zones Crypto, Permissions, Audit, API, MCP et Database exigent une attention particulière.

## 8. Revue de code

Avant de proposer une Pull Request, une IA doit vérifier :

- la demande est réellement satisfaite ;
- le changement est petit et ciblé ;
- les documents applicables ont été respectés ;
- les tests pertinents existent ;
- les tests pertinents passent ou l'impossibilité est signalée ;
- aucune donnée secrète n'est introduite ;
- aucune permission n'est élargie sans justification ;
- aucun endpoint ou tool ne contourne l'Application Layer ;
- aucune erreur ne révèle de secret ;
- aucun log ne contient de secret ;
- la documentation est mise à jour si nécessaire ;
- les migrations sont cohérentes si présentes ;
- les dépendances ajoutées sont justifiées ;
- les comportements REST et MCP restent cohérents ;
- les invariants de sécurité restent vrais.

Une IA qui réalise une revue doit prioriser :

1. failles de sécurité ;
2. contournements d'architecture ;
3. régressions fonctionnelles ;
4. tests manquants ;
5. documentation manquante ;
6. lisibilité ;
7. performance.

## 9. Invariants

Les règles suivantes doivent toujours rester vraies :

- aucune IA ne contourne l'Application Layer ;
- aucune IA ne modifie la crypto sans documentation et validation humaine ;
- aucune IA n'implémente de cryptographie maison ;
- aucune IA ne désactive un test critique pour faire passer une PR ;
- aucune IA ne supprime une documentation validée sans justification ;
- aucune IA n'introduit de secret dans le dépôt ;
- aucune IA ne logge de secret ;
- aucune IA ne stocke de token complet en clair ;
- aucune IA ne mélange metadata et value ;
- aucune IA n'ajoute un bulk read de secrets au MVP ;
- aucune IA ne transforme OpenClaw en admin par facilité ;
- aucune IA n'accorde de permission implicite à un agent ;
- aucune IA ne modifie RBAC sans tests allowed et denied ;
- aucune IA ne modifie Audit sans vérifier l'absence de secrets ;
- aucune IA ne modifie MCP sans respecter `backend/docs/MCP_SPEC.md` ;
- aucune IA ne modifie REST sans respecter `backend/docs/API_SPEC.md` ;
- aucune IA ne modifie le modèle de données sans respecter `backend/docs/DATABASE.md` ;
- aucune IA ne modifie la crypto sans respecter `backend/docs/CRYPTOGRAPHY.md` ;
- aucune IA ne modifie la sécurité sans respecter `backend/docs/SECURITY.md` ;
- aucune IA ne modifie l'architecture sans respecter `backend/docs/ARCHITECTURE.md` ;
- toute modification sécurité ajoute ou met à jour des tests ;
- toute nouvelle fonctionnalité publique met à jour la documentation ;
- tout nouveau tool MCP sensible ajoute des tests de permission ;
- tout nouvel endpoint REST sensible ajoute des tests de permission ;
- toute migration sensible est testée ;
- toute dépendance critique est justifiée ;
- tout comportement nouveau est explicite ;
- toute hypothèse risquée est signalée ;
- tout refus de test exécuté est expliqué ;
- tout échec de test est rapporté ;
- tout changement non demandé est évité ;
- tout refactoring large est séparé ;
- toute optimisation respecte les garanties de sécurité ;
- toute contribution IA reste relisible par un humain ;
- la décision finale appartient aux mainteneurs humains.

## 10. Évolutions futures

### Plusieurs agents spécialisés

Le projet pourra utiliser plusieurs agents IA spécialisés.

Exemples :

- agent architecture ;
- agent sécurité ;
- agent tests ;
- agent documentation ;
- agent performance ;
- agent migration ;
- agent QA.

Chaque agent devra respecter cette gouvernance.

### Relecteurs IA

Des relecteurs IA pourront aider à analyser les Pull Requests.

Ils devront prioriser :

- sécurité ;
- architecture ;
- tests ;
- documentation ;
- cohérence REST/MCP ;
- invariants.

Une revue IA ne remplace pas une revue humaine.

### Agents sécurité

Des agents sécurité pourront rechercher :

- fuites de secrets ;
- permissions trop larges ;
- erreurs crypto ;
- logs dangereux ;
- endpoints risqués ;
- tools MCP abusables ;
- dépendances vulnérables.

### Agents documentation

Des agents documentation pourront maintenir :

- spécifications ;
- guides ;
- ADR ;
- changelogs ;
- docs API ;
- docs MCP ;
- docs sécurité.

Ils devront vérifier que la documentation décrit le comportement réel.

### Agents performance

Des agents performance pourront analyser :

- requêtes lentes ;
- index manquants ;
- coûts crypto ;
- coûts audit ;
- latence REST/MCP ;
- scalabilité.

Ils ne devront jamais proposer une optimisation qui affaiblit la sécurité.

### Agents migration

Des agents migration pourront aider à concevoir et vérifier les migrations.

Ils devront respecter :

- intégrité référentielle ;
- données historiques ;
- rollback documenté ;
- absence de secret en clair ;
- tests de migration.

### Agents QA

Des agents QA pourront générer des scénarios de test, tester des régressions et vérifier la cohérence des interfaces.

Ils devront notamment comparer :

- REST vs MCP ;
- allowed vs denied ;
- metadata vs value ;
- audit attendu vs audit réel.

## Conclusion

Les assistants IA sont les bienvenus dans MCP Secret Manager, mais ils doivent contribuer avec discipline.

Le projet est AI-first, mais il protège des actifs critiques. La vitesse de génération ne doit jamais remplacer la rigueur, les tests, l'audit, la documentation et la revue humaine.

Une IA peut accélérer le développement. Elle ne doit jamais affaiblir les garanties du projet.
