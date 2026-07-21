# Cryptographie de MCP Secret Manager

Ce document définit la stratégie cryptographique officielle de MCP Secret Manager.

Il décrit les objectifs, principes, menaces couvertes, hiérarchie de clés, cycles de vie et invariants cryptographiques du projet.

Ce document ne contient pas de code, pas d'appel de bibliothèque et pas de format binaire d'implémentation. Il est une spécification de sécurité.

## 1. Objectifs de la stratégie cryptographique

La cryptographie de MCP Secret Manager a un objectif principal : protéger les valeurs secrètes lorsqu'elles sont stockées.

Elle doit garantir que l'exfiltration de PostgreSQL seule ne permet pas de récupérer les secrets en clair.

La stratégie cryptographique doit aussi permettre :

- chiffrement authentifié des valeurs ;
- séparation entre secrets, versions et clés ;
- rotation future des clés ;
- révocation et destruction cryptographique futures ;
- évolution vers TPM, HSM, YubiKey ou Cloud KMS ;
- auditabilité des choix cryptographiques ;
- simplicité suffisante pour éviter les erreurs d'implémentation.

La cryptographie ne remplace pas :

- l'authentification ;
- l'autorisation ;
- l'audit ;
- le durcissement Linux ;
- la protection de la configuration ;
- la sécurité des clients autorisés.

Elle est une couche de défense essentielle, mais elle n'est pas l'unique mécanisme de sécurité du projet.

## 2. Principes

### Confidentialité

Les valeurs secrètes doivent rester confidentielles au repos.

Un attaquant qui obtient uniquement la base PostgreSQL ne doit pas pouvoir lire les secrets.

Conséquences :

- les valeurs secrètes sont chiffrées avant stockage ;
- la base ne contient jamais de secret en clair ;
- la clé maître n'est jamais stockée dans PostgreSQL ;
- les backups sont considérés comme sensibles.

### Intégrité

Le système doit détecter toute modification non autorisée d'une valeur chiffrée ou de ses métadonnées cryptographiques critiques.

Conséquences :

- le chiffrement doit être authentifié ;
- les données associées doivent lier le ciphertext à son contexte ;
- une altération doit provoquer un échec sûr ;
- une erreur d'intégrité ne doit jamais retourner de valeur partielle.

### Authenticité

Le système doit pouvoir vérifier qu'une valeur déchiffrée correspond bien au secret, au vault, à la version et à l'algorithme attendus.

Conséquences :

- les données associées authentifiées doivent inclure le contexte logique ;
- un ciphertext ne doit pas pouvoir être déplacé silencieusement vers un autre secret ;
- une version ne doit pas pouvoir être substituée sans détection.

### Simplicité

La stratégie cryptographique doit rester simple.

La complexité cryptographique augmente le risque d'erreur.

Conséquences :

- pas de cryptographie maison ;
- primitives éprouvées ;
- hiérarchie de clés compréhensible ;
- peu d'algorithmes au MVP ;
- pas de modes exotiques ;
- pas de formats implicites.

### Rotation

Le modèle doit permettre la rotation progressive des secrets et des clés.

Conséquences :

- un DEK par SecretVersion ;
- KEK séparées des DEK ;
- Master Key séparée de PostgreSQL ;
- capacité future de rewrap ;
- versions immuables.

### Forward evolution

La cryptographie doit pouvoir évoluer sans casser les secrets existants.

Conséquences :

- métadonnées d'algorithme explicites ;
- versionnement des paramètres crypto ;
- possibilité future d'ajouter HSM, TPM, YubiKey ou Cloud KMS ;
- pas d'hypothèse irréversible sur un seul backend crypto ;
- compatibilité contrôlée entre anciennes et nouvelles versions.

## 3. Menaces couvertes

La stratégie cryptographique vise à réduire l'impact des menaces suivantes :

### Exfiltration de PostgreSQL

Un attaquant obtient un dump ou accès lecture à la base.

Mitigation :

- valeurs chiffrées ;
- DEK protégés ;
- clé maître absente de PostgreSQL ;
- données associées authentifiées.

Limite :

Si l'attaquant obtient aussi la clé maître et la configuration nécessaire, les secrets peuvent être compromis.

### Exfiltration de backup

Un backup contenant les ciphertexts et métadonnées est exposé.

Mitigation :

- mêmes garanties que PostgreSQL ;
- séparation opérationnelle de la clé maître ;
- chiffrement de backup prévu ;
- rotation post-incident.

### Modification de ciphertext

Un attaquant modifie une valeur chiffrée en base.

Mitigation :

- chiffrement authentifié ;
- détection d'altération ;
- échec de déchiffrement ;
- audit d'erreur crypto.

### Substitution de secret

Un attaquant tente de déplacer un ciphertext d'un secret vers un autre.

Mitigation :

- données associées authentifiées incluant le contexte ;
- liaison au vault, secret, version et algorithme.

### Réutilisation de clés ou nonces

Une erreur d'implémentation réutilise une combinaison dangereuse.

Mitigation :

- règles strictes de génération ;
- bibliothèques éprouvées ;
- tests ;
- revue crypto ;
- invariants explicites.

### Logs ou erreurs

Une valeur déchiffrée apparaît dans un log ou une erreur.

Mitigation :

- interdiction de logging des secrets ;
- séparation crypto/audit ;
- erreurs sûres ;
- tests de non-régression.

### Compromission partielle de configuration

Un attaquant obtient une partie de la configuration mais pas la clé maître.

Mitigation :

- clé maître protégée séparément ;
- pas de stockage de clé maître en base ;
- permissions Linux strictes.

### Compromission complète de l'hôte

Un attaquant contrôle l'hôte, le processus ou l'utilisateur root.

Mitigation partielle :

- réduction du temps de présence des secrets en mémoire ;
- audit ;
- rotation post-incident ;
- durcissement.

Limite :

La cryptographie applicative ne protège pas totalement contre un hôte entièrement compromis.

## 4. Envelope Encryption

MCP Secret Manager utilise le principe d'envelope encryption.

Envelope encryption sépare :

- la clé qui protège l'instance ;
- les clés qui protègent les vaults ;
- les clés qui chiffrent les valeurs secrètes.

Vue logique :

```text
Master Key
  -> Key Encryption Key for Vault
    -> Data Encryption Key for SecretVersion
      -> Encrypted Secret Value
```

### Master Key

La Master Key est la racine de confiance cryptographique de l'instance.

Responsabilités :

- protéger ou dériver la protection des KEK ;
- rester hors de PostgreSQL ;
- être protégée par l'environnement d'exécution ;
- permettre la restauration si elle est disponible ;
- rendre les secrets irrécupérables si elle est définitivement perdue.

La Master Key doit être traitée comme l'actif le plus sensible de l'instance.

### Key Encryption Key

Une Key Encryption Key protège les DEK.

Dans le modèle cible, une KEK est associée à un périmètre logique fort, notamment un vault.

Responsabilités :

- isoler cryptographiquement les vaults ;
- permettre la rotation par vault ;
- permettre le rewrap des DEK ;
- réduire le rayon d'impact d'une compromission future.

Au MVP, la représentation peut être simple, mais le modèle doit préserver la séparation conceptuelle entre Master Key, KEK et DEK.

### Data Encryption Key

Une Data Encryption Key chiffre une valeur secrète.

Dans MCP Secret Manager, un DEK est associé à une SecretVersion.

Responsabilités :

- chiffrer la valeur d'une version précise ;
- limiter le couplage entre versions ;
- faciliter la rotation ;
- faciliter la destruction cryptographique future.

### Pourquoi un DEK par SecretVersion

Un DEK par SecretVersion offre une isolation fine.

Avantages :

- chaque version est cryptographiquement indépendante ;
- une rotation de secret crée naturellement un nouveau DEK ;
- la révocation ou destruction future peut être plus ciblée ;
- le rewrap des clés est plus clair ;
- l'audit peut raisonner par version ;
- une erreur sur une version ne se propage pas à toutes les versions.

Coût accepté :

- plus de métadonnées cryptographiques ;
- plus de gestion de clés ;
- complexité légèrement supérieure au stockage d'une clé par vault.

Ce coût est acceptable pour un Secret Manager.

### Séparation des responsabilités

La crypto ne décide jamais si un acteur peut lire un secret.

Ordre obligatoire :

1. authentification ;
2. résolution de la ressource ;
3. vérification du vault ;
4. autorisation ;
5. chargement de la version ;
6. déchiffrement ;
7. audit sans valeur secrète ;
8. réponse minimale.

La couche crypto fournit une capacité technique. Elle ne porte pas la politique de sécurité métier.

## 5. Cycle de vie des clés

### Génération

Les clés doivent être générées avec une source aléatoire cryptographiquement sûre.

Exigences :

- pas de génération déterministe non justifiée ;
- pas de seed fixe ;
- pas de réutilisation de clé entre usages différents ;
- pas de clé dérivée par concaténation ou méthode ad hoc ;
- paramètres documentés.

### Stockage

Les clés doivent être stockées selon leur niveau de sensibilité.

Principes :

- la Master Key n'est jamais stockée dans PostgreSQL ;
- les KEK ne doivent pas être exposées en clair dans la base ;
- les DEK ne doivent pas être stockées en clair ;
- les métadonnées de clés doivent être suffisantes pour déchiffrer légitimement ;
- les backups doivent préserver la séparation entre ciphertexts et racine de confiance.

### Chargement

Le chargement des clés doit être explicite et contrôlé.

Exigences :

- configuration validée au démarrage ;
- échec sûr si la clé nécessaire est absente ;
- pas de fallback silencieux vers une clé par défaut ;
- pas de génération automatique d'une nouvelle Master Key en production sans action explicite ;
- erreurs sûres.

### Rotation

La rotation doit être planifiée selon le type de clé.

Types :

- rotation de Master Key ;
- rotation de KEK ;
- rotation de DEK ;
- rotation de valeur secrète.

Chaque rotation doit être auditée et documentée.

### Révocation

La révocation marque une clé ou une version comme inutilisable selon la politique.

La révocation peut être logique avant d'être physique.

Exemples :

- une version révoquée ne doit plus être retournée ;
- une KEK compromise exige rewrap ou rotation ;
- une Master Key compromise exige incident response complet.

### Destruction

La destruction de clé peut rendre des secrets irrécupérables.

Elle doit être :

- explicite ;
- auditée ;
- difficile à déclencher accidentellement ;
- documentée ;
- compatible avec la stratégie de backup.

La destruction cryptographique est une capacité puissante et dangereuse. Elle ne doit pas être introduite sans garde-fous.

## 6. Structure logique d'un Secret chiffré

Une SecretVersion chiffrée doit contenir suffisamment d'informations pour permettre un déchiffrement autorisé et vérifier son intégrité.

Composants logiques :

- ciphertext ;
- nonce ou valeur équivalente requise par l'algorithme ;
- identifiant ou référence de clé ;
- algorithme ;
- version des paramètres cryptographiques ;
- métadonnées de wrapping du DEK ;
- données associées authentifiées ;
- état de la version ;
- horodatage de création ;
- acteur ayant créé la version.

### Ciphertext

Le ciphertext représente la valeur secrète chiffrée.

Il ne doit jamais être interprété comme une valeur en clair.

### Nonce

Le nonce est requis par le mode de chiffrement authentifié.

Exigences :

- unique pour une clé donnée ;
- généré selon les exigences de l'algorithme ;
- stocké avec les métadonnées nécessaires ;
- jamais réutilisé avec la même clé.

### Métadonnées cryptographiques

Les métadonnées cryptographiques permettent de savoir comment traiter une version.

Elles peuvent inclure :

- algorithme ;
- version de schéma crypto ;
- référence de KEK ;
- référence de DEK wrapped ;
- paramètres nécessaires au déchiffrement ;
- statut de clé.

Ces métadonnées ne doivent pas contenir de valeur secrète en clair.

### Données associées authentifiées

Les données associées authentifiées lient le ciphertext à son contexte.

Elles doivent inclure conceptuellement :

- identifiant du vault ;
- identifiant du secret ;
- numéro ou identifiant de version ;
- algorithme ;
- version de paramètres ;
- provider si pertinent.

L'objectif est d'empêcher la substitution silencieuse de ciphertext entre ressources.

## 7. Gestion de la Master Key

### Exigences de stockage

La Master Key :

- ne doit jamais être stockée dans PostgreSQL ;
- ne doit jamais être commitée dans Git ;
- ne doit jamais apparaître dans les logs ;
- ne doit jamais être transmise à un client ;
- doit être protégée par des permissions système strictes ;
- doit être sauvegardée séparément des backups PostgreSQL si la récupération est nécessaire.

### Exigences de protection

La Master Key doit être protégée contre :

- lecture par utilisateurs non autorisés ;
- fuite via logs ;
- inclusion dans image Docker ;
- exposition par variables mal gérées ;
- copie dans backups non protégés ;
- accès par processus non nécessaires.

En production, la configuration doit refuser les modes manifestement dangereux.

### Perte de Master Key

Si la Master Key est perdue définitivement, les secrets chiffrés avec la hiérarchie correspondante peuvent devenir irrécupérables.

Cette propriété est normale et doit être documentée.

Une procédure de backup et récupération de la Master Key doit être définie avant usage production sérieux.

### Compromission de Master Key

Si la Master Key est compromise, l'incident est critique.

Actions attendues :

- contenir l'accès ;
- suspendre les clients ;
- analyser les audits ;
- générer une nouvelle racine de confiance ;
- rewrap ou rechiffrer selon capacités ;
- rotater les secrets exposés ;
- documenter l'incident.

### Évolutions futures

La gestion de Master Key doit pouvoir évoluer vers :

- TPM ;
- HSM ;
- YubiKey ;
- Cloud KMS ;
- passphrase administrateur avec KDF ;
- split recovery ;
- présence humaine obligatoire pour opérations sensibles.

Le MVP ne doit pas rendre ces évolutions impossibles.

## 8. Rotation des clés

### Rotation de Master Key

La rotation de Master Key change la racine de confiance.

Elle est rare, sensible et doit être fortement contrôlée.

Elle peut nécessiter :

- verrouillage temporaire ;
- backup préalable ;
- rewrap des KEK ;
- validation post-rotation ;
- audit complet ;
- plan de rollback ou recovery.

Une rotation de Master Key ne doit pas être une opération implicite.

### Rotation de KEK

La rotation d'une KEK affecte un périmètre comme un vault.

Objectif :

- remplacer la clé qui protège les DEK ;
- rewrap les DEK existants ;
- éviter de rechiffrer toutes les valeurs si ce n'est pas nécessaire.

La rotation de KEK doit préserver :

- intégrité des versions ;
- audit ;
- disponibilité contrôlée ;
- capacité de rollback selon état.

### Rotation de DEK

La rotation de DEK se produit naturellement lorsqu'une nouvelle SecretVersion est créée.

Objectif :

- associer une nouvelle clé de données à une nouvelle valeur ;
- éviter la réutilisation excessive d'une clé ;
- faciliter la révocation ciblée.

Une version existante ne doit pas recevoir silencieusement un nouveau DEK qui changerait son sens historique, sauf procédure explicite de re-encryption documentée.

### Rotation de valeur secrète

La rotation d'une valeur secrète est différente de la rotation de clé.

Elle consiste à remplacer le secret métier lui-même, par exemple une API key ou un mot de passe.

Elle doit créer une nouvelle SecretVersion.

Les anciennes versions peuvent ensuite être :

- dépréciées ;
- révoquées ;
- archivées ;
- détruites selon politique.

## 9. Bonnes pratiques cryptographiques

Le projet doit respecter les bonnes pratiques suivantes :

- utiliser uniquement des primitives reconnues ;
- utiliser uniquement des bibliothèques maintenues et réputées ;
- ne jamais implémenter une primitive cryptographique ;
- préférer le chiffrement authentifié ;
- lier les ciphertexts à leur contexte via données associées ;
- générer les clés avec une source cryptographiquement sûre ;
- générer les nonces selon les règles de l'algorithme ;
- ne jamais réutiliser une paire clé/nonce ;
- séparer Master Key, KEK et DEK ;
- stocker les clés sensibles hors PostgreSQL ou wrapped ;
- documenter les algorithmes et paramètres ;
- prévoir la migration d'algorithme ;
- tester les erreurs de déchiffrement ;
- refuser les downgrades silencieux ;
- ne jamais logger secret, clé, token ou payload sensible ;
- auditer les erreurs crypto significatives sans exposer de données sensibles.

## 10. Invariants cryptographiques

Les règles suivantes ne doivent jamais être violées :

- aucun secret n'est stocké en clair dans PostgreSQL ;
- aucune Master Key n'est stockée dans PostgreSQL ;
- aucun token complet n'est stocké en clair ;
- aucune valeur secrète n'est écrite dans les logs ;
- aucune valeur secrète n'est écrite dans AuditEvent ;
- aucune primitive cryptographique maison n'est autorisée ;
- aucun chiffrement sans authentification n'est autorisé pour les valeurs secrètes ;
- AES-256-GCM ou un algorithme approuvé doit être utilisé selon la politique du projet ;
- chaque SecretVersion possède son propre DEK logique ;
- un DEK n'est jamais stocké en clair ;
- une KEK ne chiffre pas directement les valeurs secrètes ;
- la Master Key ne chiffre pas directement les valeurs secrètes ;
- une paire clé/nonce n'est jamais réutilisée ;
- les données associées authentifiées lient le ciphertext à son contexte ;
- un ciphertext ne peut pas être déplacé vers un autre secret sans détection ;
- une erreur de déchiffrement ne retourne jamais de valeur partielle ;
- une erreur d'intégrité entraîne un refus sûr ;
- les permissions sont vérifiées avant le déchiffrement ;
- Crypto ne décide jamais de l'autorisation ;
- Audit ne reçoit jamais de secret en clair ;
- une SecretVersion est immuable ;
- une nouvelle valeur de secret crée une nouvelle SecretVersion ;
- la rotation d'une valeur secrète n'écrase jamais une version existante ;
- la rotation de clé est auditée ;
- la destruction cryptographique est explicite et auditée ;
- aucun fallback vers une clé par défaut n'est autorisé en production ;
- aucun downgrade d'algorithme silencieux n'est autorisé ;
- les métadonnées crypto nécessaires sont versionnées ;
- les backups ne doivent pas contenir la Master Key en clair avec les ciphertexts ;
- toute modification de stratégie cryptographique doit mettre à jour ce document.

## 11. Évolutions futures

### HSM

Un HSM pourra protéger la racine de confiance ou certaines KEK.

Objectifs :

- empêcher l'export de clés sensibles ;
- déléguer unwrap ou opérations clés au matériel ;
- réduire l'exposition mémoire ;
- renforcer la production.

Le modèle crypto doit permettre qu'une clé soit représentée par une référence externe plutôt que par du matériel local.

### TPM

TPM pourra permettre de lier une clé à une machine ou un état de boot.

Objectifs :

- protection locale renforcée ;
- attestation future ;
- réduction du risque d'exfiltration de clé ;
- intégration Debian durcie.

TPM ne doit pas être obligatoire pour le MVP.

### YubiKey

YubiKey pourra servir à protéger des opérations sensibles.

Usages futurs possibles :

- déverrouillage de Master Key ;
- approbation humaine ;
- signature d'opérations ;
- protection d'une KEK ;
- break-glass contrôlé.

YubiKey doit rester une extension, pas une dépendance fondamentale.

### Cloud KMS

Cloud KMS pourra servir de backend de protection pour les clés.

Exemples :

- AWS KMS ;
- Google Cloud KMS ;
- Azure Key Vault ;
- autres fournisseurs.

Cette évolution doit rester compatible avec le modèle self-hosted.

MCP Secret Manager ne doit pas devenir dépendant d'un cloud pour fonctionner.

### Rewrap

Rewrap désigne le remplacement de la protection d'une clé sans rechiffrer nécessairement la valeur secrète.

Cas typique :

- une KEK est remplacée ;
- les DEK wrapped sont rewrapped ;
- les ciphertexts de secret restent inchangés.

Rewrap doit être :

- explicite ;
- transactionnel autant que possible ;
- audité ;
- vérifiable ;
- réversible seulement si la politique le permet.

### Multi-key

Le projet pourra gérer plusieurs clés actives ou historiques.

Objectifs :

- rotation progressive ;
- déchiffrement d'anciennes versions ;
- migration d'algorithme ;
- isolation par vault ;
- réduction du blast radius.

Le multi-key doit rester compréhensible et documenté.

### Crypto agility

Crypto agility signifie que le projet peut évoluer vers de nouveaux algorithmes ou paramètres sans casser les données existantes.

Exigences :

- algorithme stocké explicitement ;
- version de paramètres stockée explicitement ;
- refus des algorithmes inconnus ;
- migration documentée ;
- pas de downgrade silencieux ;
- tests de compatibilité.

Crypto agility ne signifie pas accepter n'importe quel algorithme configurable par l'utilisateur.

Les algorithmes autorisés doivent rester limités et approuvés par le projet.

## Conclusion

La stratégie cryptographique de MCP Secret Manager repose sur une idée simple : les secrets doivent être chiffrés avec des clés de données isolées, elles-mêmes protégées par une hiérarchie de clés contrôlée.

Le MVP doit rester sobre :

- AES-256-GCM ;
- envelope encryption ;
- Master Key hors PostgreSQL ;
- KEK par périmètre de vault ;
- DEK par SecretVersion ;
- versions immuables ;
- aucun secret en clair au repos ;
- aucune cryptographie maison.

Cette base doit être suffisamment solide pour protéger OpenClaw aujourd'hui et évoluer demain vers HSM, TPM, YubiKey, Cloud KMS, rewrap, multi-key et crypto agility.

