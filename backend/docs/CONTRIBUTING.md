# Guide de contribution

Merci de vouloir contribuer à MCP Secret Manager.

Ce document définit les règles officielles de contribution au projet. Il explique le workflow attendu, les exigences qualité, les règles de documentation, les attentes de tests, les contraintes de sécurité et la culture de revue.

MCP Secret Manager est un projet de sécurité. Contribuer à ce projet implique de respecter une discipline plus stricte que pour une application classique.

## 1. Objectifs

### Pourquoi un guide de contribution

Un guide de contribution existe pour rendre les contributions :

- cohérentes ;
- relisibles ;
- testables ;
- documentées ;
- alignées avec l'architecture ;
- sûres ;
- faciles à maintenir dans le temps.

Il permet aux contributeurs de comprendre comment proposer une modification sans casser les garanties fondamentales du projet.

### Objectifs qualité

Chaque contribution doit viser :

- sécurité ;
- simplicité ;
- lisibilité ;
- testabilité ;
- auditabilité ;
- cohérence avec les documents fondateurs ;
- compatibilité avec OpenClaw, REST et MCP ;
- absence de comportement caché.

Une contribution n'est pas jugée uniquement sur le fait qu'elle fonctionne. Elle est jugée sur sa capacité à rester correcte, compréhensible et maintenable.

### Valeurs du projet

MCP Secret Manager valorise :

- la sécurité avant la vitesse ;
- la clarté avant l'astuce ;
- les petites Pull Requests ;
- les décisions explicites ;
- la documentation ;
- les tests ;
- la revue attentive ;
- le respect des utilisateurs ;
- l'honnêteté sur les limites.

## 2. Philosophie

### Documentation Before Code

Les décisions importantes doivent être documentées avant ou avec le code.

Une contribution qui modifie un comportement public, une garantie de sécurité, une API, un tool MCP, une migration ou un invariant doit mettre à jour la documentation concernée.

### Security First

La sécurité est prioritaire.

Une contribution pratique mais dangereuse doit être refusée, redessinée ou reportée.

Les zones suivantes demandent une attention particulière :

- cryptographie ;
- permissions ;
- audit ;
- tokens ;
- secrets ;
- REST ;
- MCP ;
- migrations.

### Small Pull Requests

Les Pull Requests doivent rester petites.

Une PR devrait résoudre un problème principal.

Les refactorings, changements fonctionnels, migrations et modifications de documentation doivent être séparés lorsqu'ils ne servent pas le même objectif immédiat.

### Review Culture

La revue est un mécanisme de qualité, pas un obstacle administratif.

Une bonne revue cherche à protéger :

- les utilisateurs ;
- les secrets ;
- l'architecture ;
- les contributeurs futurs ;
- la maintenabilité du projet.

Les discussions doivent rester précises, respectueuses et ancrées dans les documents du projet.

### Test Everything

Tout comportement important doit être testé.

Les changements de sécurité exigent des tests adaptés.

Les tests doivent couvrir les succès, les refus et les erreurs.

### Explicit Decisions

Les décisions implicites sont dangereuses.

Une contribution doit rendre visibles :

- son objectif ;
- ses hypothèses ;
- ses compromis ;
- ses impacts ;
- ses limites ;
- ses tests.

### Respect the Architecture

Les contributions doivent respecter l'architecture validée.

En particulier :

- REST et MCP passent par l'Application Layer ;
- Domain ne dépend pas des frameworks ;
- Crypto ne décide pas des permissions ;
- Audit ne voit jamais les valeurs secrètes ;
- Infrastructure ne porte pas de logique métier cachée.

## 3. Workflow Git

Le workflow recommandé est :

```text
Issue
  -> Discussion
    -> Branch
      -> Implementation
        -> Tests
          -> Documentation
            -> Pull Request
              -> Review
                -> Merge
```

### Environnement local

Le workflow local par défaut passe par Docker Compose depuis la racine du dépôt.

Commandes principales :

```bash
cp .env.example .env
make up
make logs
make down
```

Le stack local démarre :

- `postgres` pour PostgreSQL ;
- `migrations` pour appliquer automatiquement le schéma Alembic ;
- `bootstrap` pour initialiser les données système minimales ;
- `backend` pour l'API FastAPI ;
- `frontend` pour l'application Next.js.

Le host ne doit pas avoir besoin d'installer les dépendances Python ou Node.js pour démarrer l'application complète.

Les commandes Python locales restent possibles depuis `backend/` lorsqu'un environnement Python est volontairement installé. Les commandes npm locales restent possibles depuis `frontend/` lorsqu'un environnement Node.js est volontairement installé. Elles ne remplacent pas le workflow Docker recommandé.

Les migrations PostgreSQL vivent sous `db/migrations/` et leur configuration Alembic sous `db/alembic.ini`.

En développement local, `docker compose up` exécute automatiquement
`alembic upgrade head` via le service one-shot `migrations` avant de démarrer le
backend. Les migrations sont sérialisées par un verrou advisory PostgreSQL.

Après les migrations, `docker compose up` exécute automatiquement le service
one-shot `bootstrap`. Ce service initialise les permissions système, les rôles
par défaut et l'administrateur configuré. Les seeds sont idempotents : une
deuxième exécution ne crée ni doublon de permissions, ni doublon de rôles, ni
second administrateur.

Commandes utiles :

```bash
make db-current
make db-history
make db-upgrade
make db-downgrade DB_DOWN_REVISION=-1
make db-revision DB_REVISION_MESSAGE="describe change"
make db-reset CONFIRM_RESET=dev
make seed-run
```

`make db-reset CONFIRM_RESET=dev` est destructif et réservé au développement :
il supprime le schéma `public`, le recrée, puis rejoue toutes les migrations.

`make seed-run` rejoue uniquement les seeds système sur une base déjà migrée.
Le bootstrap est configurable par variables d'environnement :

- `MCP_SECRET_MANAGER_BOOTSTRAP_ENABLED` active ou désactive les seeds ;
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL` définit l'email de l'administrateur initial ;
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME` définit son nom affiché ;
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY` permet de créer une clé API administrateur initiale ;
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD` est réservé au futur login mot de passe et n'est pas persisté aujourd'hui ;
- `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_*` configure le seed optionnel de service account.

Aucune valeur de clé API bootstrap ne doit être committée. Le backend stocke
uniquement le préfixe et le hash de la clé, et ne journalise jamais la valeur
brute.

### Issue

Une contribution significative doit commencer par une issue.

L'issue doit expliquer :

- le problème ;
- le contexte ;
- le comportement attendu ;
- les risques ;
- les documents concernés ;
- le périmètre proposé.

Pour une correction mineure, une issue séparée peut être facultative.

### Discussion

La discussion sert à clarifier la solution avant d'écrire trop de code.

Elle est particulièrement importante pour :

- architecture ;
- sécurité ;
- API ;
- MCP ;
- modèle de données ;
- migrations ;
- crypto ;
- permissions.

### Branch

Créer une branche dédiée par changement.

La branche doit avoir un objectif clair.

Éviter de mélanger plusieurs sujets dans une même branche.

### Implementation

L'implémentation doit être ciblée.

Elle doit respecter :

- la Constitution ;
- l'Architecture ;
- les spécifications ;
- les invariants ;
- les conventions du projet.

### Tests

Les tests doivent être ajoutés ou mis à jour avec le changement.

Une PR sans tests adaptés doit expliquer pourquoi.

Les changements de sécurité ne doivent pas être fusionnés sans tests, sauf exception exceptionnelle validée par mainteneur.

### Documentation

La documentation doit être mise à jour lorsque le comportement public, architectural ou sécurité change.

La documentation ne doit pas être traitée comme une tâche secondaire.

### Pull Request

La PR doit être claire, petite et relisible.

Elle doit expliquer ce qui change, pourquoi, comment c'est testé, et quels risques existent.

### Review

La revue vérifie :

- sécurité ;
- architecture ;
- tests ;
- documentation ;
- compatibilité ;
- lisibilité ;
- performance.

Une revue peut demander de réduire le périmètre d'une PR.

### Merge

Une PR ne doit être fusionnée que si :

- le périmètre est clair ;
- les tests requis passent ;
- la documentation nécessaire est à jour ;
- les questions importantes sont résolues ;
- les invariants sont respectés.

## 4. Pull Requests

### Taille attendue

Une Pull Request doit être aussi petite que raisonnablement possible.

Elle doit idéalement :

- résoudre un problème ;
- toucher un nombre limité de modules ;
- être testable indépendamment ;
- être relisible en une seule revue attentive.

Une PR massive peut être refusée même si son intention est bonne.

### Description

La description doit inclure :

- objectif ;
- contexte ;
- changements principaux ;
- documents consultés ou modifiés ;
- risques ;
- limites ;
- tests exécutés ;
- captures ou exemples si utile.

### Tests

La PR doit indiquer :

- tests ajoutés ;
- tests modifiés ;
- tests exécutés ;
- tests non exécutés et raison.

Pour les changements sensibles, les tests doivent inclure des scénarios de refus.

### Documentation

La PR doit indiquer si la documentation est :

- non concernée ;
- mise à jour ;
- à compléter dans une PR dédiée validée.

Une fonctionnalité publique sans documentation est incomplète.

### Justification

La PR doit justifier :

- nouvelle dépendance ;
- nouvelle abstraction ;
- changement d'architecture ;
- changement de permission ;
- migration ;
- changement de contrat public ;
- changement crypto.

### Critères d'acceptation

Une PR est acceptable si :

- elle résout le problème annoncé ;
- elle respecte les documents fondateurs ;
- elle est testée ;
- elle est documentée si nécessaire ;
- elle ne crée pas de comportement caché ;
- elle ne réduit pas les garanties de sécurité ;
- elle reste maintenable.

## 5. Documentation

La documentation est une partie du produit.

Elle doit être mise à jour lorsque :

- une API change ;
- un tool MCP change ;
- une permission change ;
- une entité de base change ;
- une migration importante est ajoutée ;
- un comportement de sécurité change ;
- un invariant change ;
- une nouvelle dépendance structurante est ajoutée ;
- une décision d'architecture est prise.

### Documents de référence

Les documents suivants sont normatifs :

- `backend/docs/PROJECT.md` ;
- `backend/docs/CONSTITUTION.md` ;
- `backend/docs/ARCHITECTURE.md` ;
- `backend/docs/SECURITY.md` ;
- `backend/docs/DATABASE.md` ;
- `backend/docs/CRYPTOGRAPHY.md` ;
- `backend/docs/API_SPEC.md` ;
- `backend/docs/MCP_SPEC.md` ;
- `backend/docs/TESTING.md` ;
- `backend/docs/AI_RULES.md` ;
- `frontend/docs/` pour les décisions frontend.

Une contribution qui contredit un document de référence doit soit être modifiée, soit proposer une mise à jour explicite du document concerné.

## 6. Architecture

Les contributions doivent respecter :

- Clean Architecture ;
- séparation des couches ;
- Dependency Inversion ;
- frontières de sécurité ;
- invariants documentés ;
- Application Layer comme point de passage métier ;
- séparation REST/MCP ;
- séparation metadata/value.

### ADR

Une Architecture Decision Record est requise ou fortement recommandée lorsqu'une contribution :

- change une frontière de couche ;
- ajoute une dépendance structurante ;
- modifie la crypto ;
- modifie le modèle de permissions ;
- modifie le modèle de données ;
- introduit un nouveau protocole ;
- ajoute un Secret Provider important ;
- crée une rupture de compatibilité.

L'ADR doit expliquer le contexte, la décision, les alternatives et les conséquences.

## 7. Tests

Avant une PR, le contributeur doit vérifier que les tests adaptés existent.

Attentes minimales :

- tests unitaires pour logique métier ;
- tests de refus pour permissions ;
- tests d'erreurs pour comportements sensibles ;
- tests REST pour endpoints touchés ;
- tests MCP pour tools touchés ;
- tests de migration si le schéma change ;
- tests d'audit si une action sensible change ;
- tests de non-régression pour bug corrigé.

Une couverture chiffrée ne suffit pas.

Les tests doivent vérifier les bons invariants.

## 8. Sécurité

### Crypto

Toute contribution crypto doit :

- respecter `backend/docs/CRYPTOGRAPHY.md` ;
- éviter toute cryptographie maison ;
- utiliser des primitives approuvées ;
- tester les échecs ;
- documenter le changement ;
- recevoir une revue attentive.

### RBAC

Toute contribution RBAC doit :

- tester allowed et denied ;
- préserver le refus par défaut ;
- garder metadata et value séparées ;
- documenter les nouvelles permissions ;
- vérifier REST et MCP.

### Audit

Toute contribution audit doit :

- ne jamais inclure de valeur secrète ;
- auditer les actions sensibles ;
- distinguer succès et refus ;
- préserver client_type ;
- être testée.

### REST

Toute contribution REST doit :

- respecter `backend/docs/API_SPEC.md` ;
- éviter les réponses trop larges ;
- paginer les listes ;
- produire des erreurs sûres ;
- ne pas contourner l'Application Layer.

### MCP

Toute contribution MCP doit :

- respecter `backend/docs/MCP_SPEC.md` ;
- exposer des tools explicites ;
- retourner des réponses minimales ;
- ne pas accorder de privilège supplémentaire ;
- auditer les actions sensibles ;
- tester les scénarios agentiques critiques.

### Secrets

Toute contribution liée aux secrets doit :

- ne jamais logger de valeur ;
- ne jamais stocker de valeur en clair ;
- préserver l'immuabilité des versions ;
- séparer metadata et value ;
- auditer les lectures de valeur.

### Migrations

Toute migration doit :

- préserver les données historiques ;
- respecter l'intégrité référentielle ;
- éviter les destructions implicites ;
- être testée ;
- documenter le rollback si possible ;
- ne jamais introduire de secret en clair.

## 9. Revue

La revue doit prioriser les points suivants.

### 1. Sécurité

Vérifier :

- absence de fuite de secrets ;
- permissions correctes ;
- audit ;
- erreurs sûres ;
- crypto ;
- tokens ;
- MCP ;
- migrations.

### 2. Architecture

Vérifier :

- couches respectées ;
- dépendances autorisées ;
- pas de contournement Application Layer ;
- pas de logique métier cachée dans l'infrastructure ;
- pas de couplage REST/MCP.

### 3. Tests

Vérifier :

- tests pertinents ;
- tests de refus ;
- tests de régression ;
- tests REST/MCP ;
- tests de migration si nécessaire ;
- absence de tests flaky.

### 4. Documentation

Vérifier :

- documents mis à jour ;
- comportement public décrit ;
- décisions justifiées ;
- limites explicites.

### 5. Performance

Vérifier :

- absence de régression évidente ;
- requêtes raisonnables ;
- pas de cache dangereux ;
- pas d'optimisation qui affaiblit la sécurité.

## 10. Invariants

Les règles suivantes doivent toujours être respectées :

- aucune PR sans tests adaptés ;
- aucune PR sécurité sans revue attentive ;
- aucune fonctionnalité publique sans documentation ;
- aucune modification d'architecture sans ADR ou validation explicite ;
- aucune fuite de secrets ;
- aucun secret dans Git ;
- aucun secret dans les logs ;
- aucun secret dans les erreurs ;
- aucun secret dans AuditEvent ;
- aucun token complet stocké en clair ;
- aucune cryptographie maison ;
- aucun changement crypto non documenté ;
- aucune permission implicite ;
- aucun contournement RBAC ;
- aucun contournement de l'Application Layer ;
- aucun endpoint REST ne lit directement PostgreSQL ;
- aucun tool MCP ne lit directement PostgreSQL ;
- REST et MCP ne dépendent pas l'un de l'autre ;
- REST et MCP partagent les mêmes décisions métier ;
- metadata et value restent séparées ;
- une lecture metadata ne révèle jamais une value ;
- une liste ne retourne jamais de valeurs secrètes ;
- une lecture de value vérifie toujours les permissions ;
- un refus de permission ne déclenche jamais de déchiffrement ;
- un vault verrouillé interdit la lecture de value ;
- une SecretVersion est immuable ;
- une nouvelle valeur crée une nouvelle SecretVersion ;
- une migration ne détruit pas implicitement des données sensibles ;
- une migration ne casse pas l'audit historique sans décision explicite ;
- les erreurs client restent sûres ;
- les logs restent prudents ;
- les dépendances nouvelles sont justifiées ;
- les refactorings larges sont séparés ;
- les changements non liés sont évités ;
- les tests ne dépendent pas d'Internet ;
- les tests sont déterministes ;
- la documentation reste alignée avec le comportement réel ;
- la sécurité prime sur la compatibilité ;
- la sécurité prime sur la vitesse.

## 11. Évolutions futures

### Plusieurs mainteneurs

Le projet pourra évoluer vers une équipe de mainteneurs.

Il faudra alors définir :

- responsabilités ;
- droits de merge ;
- processus de décision ;
- escalade sécurité ;
- domaines d'expertise.

### Release process

Un processus de release formel devra être défini.

Il pourra inclure :

- versionnement ;
- changelog ;
- checklist sécurité ;
- tests complets ;
- signature d'artefacts ;
- migration notes ;
- procédure rollback.

### Security disclosure

Une politique de divulgation de vulnérabilités devra être créée.

Elle devra expliquer :

- comment signaler une faille ;
- délais de réponse ;
- confidentialité ;
- coordination de correctif ;
- publication d'avis.

### Governance

La gouvernance devra définir :

- mainteneurs ;
- règles de décision ;
- acceptation d'ADR ;
- évolution de la Constitution ;
- gestion des conflits ;
- roadmap.

### Code owners

Des propriétaires de code pourront être définis pour les zones critiques.

Exemples :

- crypto ;
- permissions ;
- audit ;
- MCP ;
- API ;
- database ;
- migrations.

### Bots

Des bots pourront aider à :

- vérifier les tests ;
- scanner les secrets ;
- analyser les dépendances ;
- appliquer les labels ;
- vérifier la documentation ;
- détecter les PR trop larges.

Les bots ne remplacent pas la revue humaine.

### CI avancée

La CI pourra évoluer vers :

- fuzzing ;
- mutation testing ;
- benchmarks ;
- analyse statique avancée ;
- tests de charge ;
- tests de migration historiques ;
- validation sécurité continue.

## Conclusion

Contribuer à MCP Secret Manager signifie contribuer à une infrastructure de confiance.

Le projet accepte les contributions qui améliorent la sécurité, la clarté, la documentation, les tests, l'architecture et l'expérience d'utilisation.

Les contributions doivent rester petites, explicites, testées et alignées avec les documents fondateurs.

La vitesse compte, mais la confiance compte davantage.
