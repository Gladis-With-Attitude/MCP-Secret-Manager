# Stratégie de tests de MCP Secret Manager

Ce document définit la stratégie officielle de tests et de qualité de MCP Secret Manager.

Il explique comment le projet doit être testé pendant tout son cycle de vie, quels risques les tests doivent réduire, quels modules exigent une attention particulière et quelles garanties doivent être vérifiées avant chaque fusion ou release.

Ce document ne contient pas de code, pas de test pytest et pas d'implémentation. Il définit les attentes qualité du projet.

## 1. Objectifs

### Pourquoi les tests sont critiques

MCP Secret Manager est un composant de sécurité.

Il protège des secrets utilisés par OpenClaw, des serveurs MCP, des agents IA, des applications, des scripts et des services d'infrastructure.

Une régression peut provoquer :

- fuite de secret ;
- lecture non autorisée ;
- absence d'audit ;
- token révoqué encore valide ;
- erreur crypto silencieuse ;
- comportement divergent entre REST et MCP ;
- perte d'historique ;
- corruption de versions ;
- migration destructive ;
- contournement du principe de moindre privilège.

Les tests sont donc une barrière de sécurité, pas seulement une aide au développement.

### Risques réduits

La stratégie de tests vise à réduire :

- régressions fonctionnelles ;
- erreurs de permissions ;
- erreurs de chiffrement ou déchiffrement ;
- fuites dans les logs ;
- fuites dans les erreurs ;
- comportements non déterministes ;
- divergences REST/MCP ;
- migrations cassantes ;
- mauvaise gestion des états ;
- erreurs d'audit ;
- contournements de l'Application Layer ;
- oublis de documentation.

Les tests ne garantissent pas l'absence de bugs, mais ils rendent les comportements critiques observables et vérifiables.

## 2. Principes

### Test Pyramid

Le projet suit une pyramide de tests.

La majorité des tests doivent être rapides, ciblés et proches de la logique métier.

Répartition attendue :

- beaucoup de tests unitaires ;
- un nombre solide de tests d'intégration ;
- des tests de composants pour REST, MCP et CLI ;
- moins de tests end-to-end, mais couvrant les scénarios critiques ;
- des tests sécurité à chaque niveau.

Les tests end-to-end ne doivent pas compenser un manque de tests unitaires sur les règles critiques.

### Shift Left

Les problèmes doivent être détectés le plus tôt possible.

Conséquences :

- tests locaux simples à lancer ;
- CI rapide sur chaque Pull Request ;
- validation de sécurité avant merge ;
- documentation vérifiée tôt ;
- erreurs de migration détectées avant release.

Plus une faille est détectée tard, plus elle coûte cher et plus elle est dangereuse.

### Security First

Les tests de sécurité ont priorité sur les tests de confort.

Toute logique qui touche :

- permissions ;
- tokens ;
- crypto ;
- audit ;
- lifecycle des secrets ;
- MCP ;
- REST ;
- migrations ;

doit être couverte par des tests adaptés au risque.

### Reproducibility

Les tests doivent être reproductibles.

Un test qui passe une fois et échoue sans changement de code n'est pas fiable.

Conséquences :

- environnements contrôlés ;
- fixtures explicites ;
- données de test maîtrisées ;
- pas de dépendance implicite à l'état local ;
- pas d'ordre de test fragile.

### Determinism

Les tests doivent être déterministes.

Même lorsque le système utilise du hasard, le résultat observable du test doit être stable.

Conséquences :

- pas de tests dépendants de l'heure réelle sans contrôle ;
- pas de tests dépendants d'Internet ;
- pas de tests sensibles à l'ordre d'exécution ;
- pas de tests qui dépendent d'un service externe non maîtrisé.

### Small Tests

Les tests doivent être petits et ciblés.

Un test doit échouer pour une raison claire.

Conséquences :

- préférer plusieurs tests précis à un test géant ;
- isoler les scénarios ;
- nommer les comportements attendus ;
- limiter les assertions non liées ;
- éviter les setups massifs inutiles.

### No Untested Security Change

Aucune modification de sécurité ne doit être fusionnée sans test.

Sont considérés comme changements de sécurité :

- permissions ;
- authentification ;
- tokens ;
- crypto ;
- audit ;
- erreurs ;
- MCP tools ;
- endpoints REST sensibles ;
- migrations touchant secrets ou tokens ;
- configuration de production.

Une exception doit être rare, explicitement justifiée et documentée.

## 3. Niveaux de tests

### Unit Tests

Objectif :

Tester une unité de logique isolée.

Périmètre :

- règles de domaine ;
- décisions de permissions ;
- validation d'états ;
- construction d'événements d'audit ;
- transitions de lifecycle ;
- erreurs métier.

Fréquence :

- à chaque changement ;
- en local ;
- dans chaque CI de Pull Request.

Les unit tests doivent être rapides et nombreux.

### Integration Tests

Objectif :

Tester l'interaction entre plusieurs modules et dépendances réelles contrôlées.

Périmètre :

- PostgreSQL ;
- repositories ;
- transactions ;
- migrations appliquées ;
- crypto avec stockage ;
- audit persistant ;
- permissions avec données réelles.

Fréquence :

- dans la CI ;
- avant merge ;
- avant release.

Les integration tests doivent prouver que les composants fonctionnent ensemble sans contourner l'architecture.

### Component Tests

Objectif :

Tester un composant complet à travers son interface publique interne ou externe.

Périmètre :

- REST API ;
- MCP server ;
- CLI ;
- Auth ;
- Audit ;
- Secret lifecycle.

Fréquence :

- sur chaque Pull Request qui touche le composant ;
- avant release.

Les component tests doivent vérifier le comportement observable sans forcément démarrer tout le système.

### End-to-End Tests

Objectif :

Tester des scénarios utilisateur ou service complets.

Périmètre :

- création de vault ;
- création de projet ;
- création de secret ;
- lecture via REST ;
- lecture via MCP ;
- audit visible ;
- token de service OpenClaw.

Fréquence :

- avant release ;
- sur les branches principales ;
- éventuellement sur Pull Request si le coût reste raisonnable.

Les E2E tests doivent rester peu nombreux mais critiques.

### Security Tests

Objectif :

Tester explicitement les garanties de sécurité.

Périmètre :

- refus par défaut ;
- RBAC ;
- séparation metadata/value ;
- absence de secret dans logs ;
- audit des refus ;
- erreurs sûres ;
- token révoqué ;
- vault verrouillé ;
- erreurs crypto ;
- MCP tool abuse ;
- énumération.

Fréquence :

- sur chaque changement sensible ;
- en CI ;
- avant release.

Les security tests sont obligatoires pour un Secret Manager.

### Regression Tests

Objectif :

Empêcher le retour d'un bug corrigé.

Périmètre :

- bugs fonctionnels ;
- bugs sécurité ;
- migrations ;
- erreurs de permissions ;
- erreurs MCP ;
- erreurs REST ;
- fuites dans logs ou erreurs.

Fréquence :

- ajoutés avec chaque correction ;
- exécutés à chaque CI.

Chaque bug de sécurité corrigé doit produire un test de non-régression.

### Performance Tests

Objectif :

Vérifier que le système reste raisonnablement performant pour les usages attendus.

Périmètre :

- lecture de secret ;
- vérification de permission ;
- écriture d'audit ;
- listing paginé ;
- migrations volumineuses futures.

Fréquence :

- ponctuelle au MVP ;
- régulière avant releases importantes ;
- renforcée lorsque le volume réel augmente.

Les performance tests ne doivent jamais justifier une réduction des garanties de sécurité.

## 4. Couverture

La couverture de tests est un indicateur, pas un objectif en soi.

Une couverture élevée ne garantit pas que les bons comportements sont testés. Le projet privilégie la couverture des risques et invariants.

### Objectifs généraux

Le projet doit viser :

- couverture élevée sur la logique critique ;
- couverture raisonnable sur les interfaces ;
- couverture explicite des refus ;
- couverture des erreurs ;
- couverture des invariants de domaine ;
- couverture des migrations sensibles.

### Modules critiques

Les modules suivants exigent une couverture très élevée :

#### Permissions

Doit couvrir :

- permission présente ;
- permission absente ;
- rôle absent ;
- acteur désactivé ;
- refus par défaut ;
- metadata distincte de value ;
- OpenClaw avec rôle minimal.

#### Crypto

Doit couvrir :

- chiffrement ;
- déchiffrement ;
- échec d'intégrité ;
- mauvaise clé ;
- mauvais contexte ;
- données associées ;
- absence de valeur partielle ;
- erreurs sûres.

#### Audit

Doit couvrir :

- succès audité ;
- refus audité ;
- lecture de valeur auditée ;
- absence de secret dans AuditEvent ;
- client_type REST/MCP ;
- acteur et ressource renseignés.

#### Secret lifecycle

Doit couvrir :

- création ;
- version initiale ;
- nouvelle version ;
- version courante ;
- immutabilité ;
- archivage ;
- suppression logique ;
- vault verrouillé.

## 5. Cas critiques

Les scénarios suivants doivent toujours être testés.

### Permissions et accès

- permission accordée ;
- permission refusée ;
- absence de permission ;
- rôle absent ;
- acteur désactivé ;
- token invalide ;
- token révoqué ;
- token expiré lorsque l'expiration existe ;
- OpenClaw limité à son rôle ;
- lecture metadata autorisée sans lecture value.

### Vaults

- vault actif autorise les opérations prévues ;
- vault verrouillé refuse la lecture de valeur ;
- vault archivé refuse les écritures normales ;
- projet dans vault inexistant refusé ;
- secret dans vault verrouillé non déchiffré.

### Secrets

- création de secret ;
- création de version initiale ;
- création d'une nouvelle version ;
- version existante immuable ;
- version courante mise à jour ;
- lecture autorisée ;
- lecture refusée ;
- lecture d'un secret inexistant ;
- suppression logique ;
- archivage.

### Crypto

- chiffrement réussi ;
- déchiffrement réussi ;
- erreur crypto ;
- ciphertext altéré ;
- contexte altéré ;
- clé indisponible ;
- aucun secret partiel retourné.

### Audit

- création de secret auditée ;
- lecture de valeur auditée ;
- refus de permission audité ;
- révocation de token auditée ;
- aucun secret dans audit ;
- distinction REST/MCP ;
- audit consultable uniquement avec permission.

### MCP

- appel MCP valide ;
- appel MCP malformé ;
- tool inconnu ;
- permission refusée via MCP ;
- lecture MCP autorisée ;
- lecture MCP refusée ;
- prompt injection simulée ;
- list_secrets sans valeurs ;
- read_secret_value avec secret exact uniquement.

### REST

- requête REST valide ;
- payload invalide ;
- authentification absente ;
- autorisation refusée ;
- erreur prévisible ;
- pagination ;
- filtrage ;
- absence de secret dans erreur.

## 6. Tests sécurité

### RBAC

Les tests RBAC doivent prouver que :

- l'absence de permission refuse ;
- les permissions sont atomiques ;
- metadata et value sont séparées ;
- un rôle ne donne que ses permissions documentées ;
- modifier un rôle affecte correctement les décisions futures ;
- REST et MCP reçoivent la même décision métier.

### Fuite de secrets

Les tests doivent vérifier qu'aucun secret n'apparaît dans :

- logs ;
- erreurs ;
- audit ;
- réponses metadata ;
- listes ;
- traces de test ;
- sorties CLI non prévues.

### Erreurs

Les tests doivent vérifier :

- erreurs de validation sûres ;
- erreurs d'authentification sûres ;
- erreurs d'autorisation sûres ;
- erreurs crypto sûres ;
- erreurs internes sans détails sensibles ;
- absence de stacktrace en mode production.

### Logs

Les tests doivent vérifier :

- pas de valeur secrète ;
- pas de token complet ;
- pas de clé ;
- pas de payload brut sensible ;
- identifiants et request_id acceptables.

### Audit

Les tests doivent vérifier :

- audit des actions sensibles ;
- audit des refus importants ;
- absence de valeur secrète ;
- présence de l'acteur ;
- présence de l'action ;
- présence de la ressource ;
- présence de la décision ;
- distinction client_type.

### Brute force

Les tests futurs doivent couvrir :

- tentatives répétées de token invalide ;
- comportement des erreurs ;
- absence d'information utile à l'attaquant ;
- rate limiting si introduit.

### Replay

Les tests futurs doivent couvrir :

- réutilisation de tokens révoqués ;
- idempotence des mutations ;
- clés d'idempotence si introduites ;
- absence de double création accidentelle.

### Enumeration

Les tests doivent vérifier :

- listing limité aux permissions ;
- erreurs prudentes ;
- impossible de distinguer certaines ressources non autorisées si la politique le demande ;
- pagination obligatoire ;
- filtres qui ne contournent pas RBAC.

### Cryptographie

Les tests crypto doivent vérifier :

- mauvais contexte refusé ;
- mauvaise clé refusée ;
- ciphertext altéré refusé ;
- nonce ou metadata incohérents refusés ;
- aucun fallback vers algorithme non autorisé ;
- aucune valeur partielle.

## 7. Tests REST

Les tests REST vérifient le contrat public HTTP.

Ils doivent couvrir :

- authentification ;
- autorisation ;
- validation payload ;
- codes d'erreur conceptuels ;
- pagination ;
- filtrage ;
- création de ressources ;
- lecture metadata ;
- lecture value ;
- audit ;
- absence de secrets dans erreurs ;
- absence de valeurs dans endpoints metadata.

Les tests REST ne doivent pas dupliquer toute la logique métier si elle est déjà testée dans l'Application Layer. Ils doivent vérifier que REST appelle correctement les cas d'usage et transforme correctement les réponses et erreurs.

## 8. Tests MCP

Les tests MCP vérifient le comportement des tools MCP.

Ils doivent couvrir :

- tools disponibles ;
- arguments valides ;
- arguments invalides ;
- tool inconnu ;
- permissions accordées ;
- permissions refusées ;
- réponses minimales ;
- séparation metadata/value ;
- audit client_type MCP ;
- absence de secret dans erreurs ;
- comportements face à appels abusifs.

### Cohérence REST/MCP

REST et MCP doivent produire les mêmes décisions métier.

Pour un même acteur, une même ressource et une même action :

- REST autorisé implique MCP autorisé si le tool équivalent existe ;
- REST refusé implique MCP refusé ;
- MCP ne doit pas accorder de privilège supplémentaire ;
- MCP ne doit pas contourner l'audit ;
- les différences de format ne doivent pas changer la décision métier.

Des tests partagés ou scénarios communs doivent vérifier cette cohérence.

## 9. Tests de migration

### Migrations PostgreSQL

Les migrations doivent être testées.

Objectifs :

- appliquer une base vide ;
- appliquer une base existante ;
- préserver les données ;
- respecter les contraintes ;
- ne jamais stocker de secret en clair ;
- maintenir les relations critiques.

### Compatibilité

Les tests doivent vérifier que les migrations préservent :

- secrets existants ;
- versions ;
- acteurs ;
- rôles ;
- permissions ;
- tokens ;
- audit events.

### Rollback

Le rollback doit être documenté et testé lorsque le projet le supporte.

Si une migration ne peut pas être rollbackée automatiquement, cela doit être explicite.

### Données historiques

Les tests doivent vérifier que les données historiques restent compréhensibles.

En particulier :

- AuditEvent reste lisible ;
- SecretVersion reste liée à son Secret ;
- versions immuables non modifiées ;
- tokens révoqués restent révoqués ;
- ressources archivées restent archivées.

## 10. CI

La CI doit devenir une barrière de qualité obligatoire.

### Étapes obligatoires

La CI doit inclure progressivement :

- lint ;
- type checking ;
- tests unitaires ;
- tests d'intégration ;
- tests REST ;
- tests MCP ;
- tests de migration ;
- security scan ;
- dependency scan ;
- secret scan ;
- documentation check.

### Lint

Objectif :

Maintenir la cohérence, réduire les erreurs simples et faciliter les revues.

### Type checking

Objectif :

Détecter les incohérences avant runtime, surtout dans les flux critiques.

### Tests

Objectif :

Valider les comportements fonctionnels, sécurité et régression.

### Security scan

Objectif :

Détecter patterns dangereux, mauvaises pratiques ou vulnérabilités connues.

### Dependency scan

Objectif :

Identifier les dépendances vulnérables ou non maintenues.

### Secret scan

Objectif :

Empêcher l'introduction de secrets dans le dépôt.

### Documentation check

Objectif :

Vérifier que la documentation reste présente, cohérente et mise à jour pour les changements publics.

## 11. Invariants

Les invariants suivants doivent toujours rester vrais :

- aucune PR sécurité sans test adapté ;
- aucune correction de bug sécurité sans test de régression ;
- aucun test ne dépend d'Internet ;
- tous les tests automatisés sont déterministes ;
- les tests ne dépendent pas de l'ordre d'exécution ;
- les tests ne dépendent pas de secrets réels ;
- les tests n'utilisent jamais de credentials de production ;
- aucun secret de test réaliste n'est commit ;
- aucune valeur secrète ne doit apparaître dans les logs de test ;
- aucune valeur secrète ne doit apparaître dans les erreurs de test ;
- AuditEvent de test ne contient jamais de valeur secrète ;
- les tests REST et MCP partagent les mêmes attentes métier ;
- REST et MCP doivent produire les mêmes décisions d'autorisation ;
- un refus de permission est testé pour chaque action sensible ;
- une autorisation réussie est testée pour chaque action sensible ;
- les endpoints metadata sont testés pour absence de value ;
- les tools metadata sont testés pour absence de value ;
- les lectures de value sont testées pour audit ;
- les erreurs crypto sont testées pour absence de valeur partielle ;
- les tokens révoqués sont testés ;
- les acteurs désactivés sont testés ;
- les vaults verrouillés sont testés ;
- les versions immuables sont testées ;
- les migrations sont testées avant release ;
- les tests de migration préservent les données historiques ;
- les tests de logs vérifient l'absence de secrets ;
- les tests d'erreurs vérifient l'absence de détails sensibles ;
- les dépendances nouvelles doivent passer le scan ;
- le secret scan doit être exécuté avant merge ;
- la CI doit échouer sur un test critique rouge ;
- un test flaky doit être corrigé ou isolé rapidement ;
- une baisse de couverture critique doit être justifiée ;
- la performance ne doit jamais être testée en affaiblissant la sécurité ;
- les tests de production simulée ne doivent jamais utiliser de secrets réels ;
- toute nouvelle interface publique doit avoir des tests ;
- tout nouveau tool MCP sensible doit avoir des tests de permission ;
- tout nouveau endpoint REST sensible doit avoir des tests de permission ;
- toute modification d'audit doit tester absence de secret ;
- toute modification de crypto doit tester les échecs ;
- toute modification de permission doit tester allowed et denied.

## 12. Évolutions futures

### Fuzzing

Le fuzzing pourra être utilisé pour tester :

- parsing d'entrées ;
- endpoints REST ;
- tools MCP ;
- chemins de secrets ;
- payloads malformés ;
- erreurs de validation.

Objectif :

Découvrir des cas inattendus et renforcer la robustesse.

### Property-based testing

Le property-based testing pourra vérifier des invariants sur de nombreuses entrées générées.

Exemples :

- une version créée reste immuable ;
- une permission absente refuse toujours ;
- metadata ne contient jamais value ;
- une erreur crypto ne retourne jamais de valeur.

### Chaos testing

Le chaos testing pourra être utile lorsque le projet aura plus de composants opérationnels.

Exemples :

- PostgreSQL indisponible ;
- migration interrompue ;
- clé absente ;
- erreur réseau ;
- audit store indisponible.

Objectif :

Vérifier que le système échoue de manière sûre.

### Mutation testing

Le mutation testing pourra mesurer la qualité réelle des tests.

Objectif :

Détecter des tests qui passent sans réellement vérifier les garanties critiques.

### Load testing

Le load testing pourra mesurer :

- lectures de secrets ;
- écritures d'audit ;
- vérifications de permissions ;
- listing paginé ;
- appels MCP répétés.

Objectif :

Préparer les usages plus intensifs sans compromettre la sécurité.

### Benchmarking

Le benchmarking pourra suivre :

- latence de lecture ;
- coût de crypto ;
- coût de permission ;
- coût d'audit ;
- performance PostgreSQL.

Objectif :

Détecter les régressions et orienter les optimisations.

### Continuous security validation

A terme, le projet pourra intégrer une validation de sécurité continue.

Exemples :

- scans réguliers ;
- tests de sécurité programmés ;
- vérification de configuration ;
- simulation d'abus MCP ;
- détection de secrets ;
- rapports de dépendances.

## Conclusion

La stratégie de tests de MCP Secret Manager doit refléter la nature du projet : un composant de sécurité, AI-first, MCP-native et OpenClaw-first.

Les tests doivent prouver que le système refuse correctement, chiffre correctement, audite correctement, sépare metadata et value, et applique les mêmes décisions métier à travers REST et MCP.

Un Secret Manager ne gagne pas la confiance par ses intentions. Il la gagne par des garanties vérifiées, répétables et maintenues dans le temps.

