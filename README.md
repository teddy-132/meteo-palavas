# Créneaux Mer Plate — version 100% autonome (sans Claude)

Cette page affiche les créneaux de mer plate à Palavas-les-Flots. Ce dossier
contient tout ce qu'il faut pour l'héberger et la rafraîchir automatiquement
**sans jamais repasser par Claude**, gratuitement, via GitHub.

## Ce qui change par rapport à la version faite avec Claude

- **Source des données** : au lieu de faire lire le site Météo Consult par un
  navigateur piloté par une IA, le rafraîchissement automatique utilise
  désormais l'API publique et gratuite **Open-Meteo Marine Weather**
  (aucune clé, aucune inscription).
- **Horizon réduit à 8 jours** (aujourd'hui + 7) au lieu de 13 : c'est la
  limite maximale de cette API gratuite. C'est le compromis nécessaire pour
  que tout tourne sans intervention humaine ni IA.
- **Le bloc "📺 Sport" (MXGP / F1 / MotoGP / VTT) ne se met plus à jour tout
  seul** : vérifier le bon week-end de course ou la bonne chaîne demande un
  jugement qu'un script ne peut pas faire fiablement. Il reste figé sur les
  dernières valeurs connues — modifiez-le à la main dans `index.html` (section
  `var BROADCASTS = [...]`) si besoin, ou redemandez ponctuellement à Claude
  de le corriger.
- Tout le reste (couleurs, mise en forme, tuiles cliquables, etc.) est
  identique.

## Mise en place (10 minutes, sans ligne de commande)

1. **Créer un compte GitHub** si vous n'en avez pas : https://github.com/signup
   (gratuit).

2. **Créer un nouveau dépôt ("repository")** :
   - En haut à droite de github.com, cliquez sur le **+** puis
     **New repository**.
   - Nom : par exemple `creneaux-mer-plate`.
   - Laissez-le en **Public** (nécessaire pour que GitHub Pages et les
     actions automatiques soient gratuits et simples).
   - Cliquez **Create repository**.

3. **Ajouter les 3 fichiers** de ce dossier dans le dépôt, un par un, via
   l'interface web (pas besoin d'installer quoi que ce soit) :
   - Dans votre nouveau dépôt, cliquez **Add file → Create new file**.
   - Dans le champ du nom de fichier, tapez exactement `index.html`, puis
     collez le contenu du fichier `index.html` fourni ici. Cliquez
     **Commit changes**.
   - Recommencez : **Add file → Create new file**, nom `update_tiles.py`,
     collez le contenu de `update_tiles.py`. **Commit changes**.
   - Recommencez une dernière fois : **Add file → Create new file**, et dans
     le champ du nom tapez tout le chemin
     `.github/workflows/refresh.yml` (GitHub crée les dossiers tout seul),
     collez le contenu de `refresh.yml`. **Commit changes**.

4. **Activer l'hébergement (GitHub Pages)** :
   - Dans le dépôt, allez dans **Settings** (onglet en haut) → **Pages**
     (menu de gauche).
   - Sous "Build and deployment" → **Source**, choisissez
     **Deploy from a branch**.
   - **Branch** : `main`, dossier `/ (root)`. Cliquez **Save**.
   - Après 1 à 2 minutes, la page sera visible à l'adresse indiquée en haut
     de cet écran, de la forme :
     `https://VOTRE-NOM-UTILISATEUR.github.io/creneaux-mer-plate/`
   - C'est cette adresse que vous pouvez partager ou mettre en favori —
     elle fonctionne sur n'importe quel appareil, sans compte Claude.

5. **Vérifier que le rafraîchissement automatique fonctionne** :
   - Onglet **Actions** du dépôt → vous devriez voir le workflow
     **"Rafraîchir Créneaux Mer Plate"**.
   - Pour le tester tout de suite sans attendre 2h : cliquez dessus, puis
     **Run workflow → Run workflow**. Après ~30 secondes, un nouveau
     commit "Rafraîchissement automatique des données de mer" doit
     apparaître, et la page (après ~1 minute de republication par GitHub
     Pages) affichera les nouvelles briques.
   - Ensuite, il tourne tout seul toutes les 2 heures, 24h/24, sans que
     vous ayez besoin d'ouvrir Claude.

## En cas de souci

- **Le workflow échoue (croix rouge dans l'onglet Actions)** : cliquez
  dessus pour voir le message d'erreur exact (affiché en clair par le
  script). Les causes les plus probables : Open-Meteo temporairement
  indisponible (le prochain passage 2h après se corrigera tout seul), ou
  quelqu'un a modifié la structure du fichier `index.html` (le script
  cherche précisément les lignes `var TILES = [...]`, `var LAST_UPDATE`
  et `var NEXT_CHECK` — ne renommez pas ces variables).
- **Changer la fréquence** : dans `.github/workflows/refresh.yml`, la ligne
  `cron: "15 */2 * * *"` définit "toutes les 2 heures". Le format est en
  heure UTC (pas heure de Paris) et GitHub peut retarder légèrement les
  exécutions programmées de quelques minutes en cas de forte charge — sans
  conséquence ici.
- **Remettre les 13 jours / la source Météo Consult** : ce n'est possible
  qu'en repassant par un navigateur piloté par une IA (ce que faisait
  Claude) — l'API gratuite utilisée ici plafonne à 8 jours. Vous pouvez
  toujours redemander ponctuellement à Claude un rafraîchissement complet à
  13 jours si besoin, en repartant du HTML de ce dépôt.
