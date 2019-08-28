## v3.6.3
* Refonte totale du système de stocks
* Fix price profile
* Rajoute un nombre de citations sur la page de statistiques
* Fix les contributeurs sur la page about et gencontributors en commande
## v3.6.2
* Fix sur les prix des cotisations.
* Page À propose
* Fix typo
## v3.6.1
* Valeur par défaut des répartitions et calcul des répartitions
## v3.6.0
* AJout d'un débit direct comme champ du profil
* Suppression des codes bare
* Création plus simple (création automatiques des produits avec les bons prix)
* Calcul des prix des produits depuis le site
* Génération de factures depuis le site
* Ajouter un champ "raison" dans les accès gracieux
* Fix de la recherche dans l'admin
* Onglet de répartition des cotisations
* Ajout d'un champ alcool pour optimiser le classement
* Amélioration et fix de la redirection après connexion
* Amélioration de l'affichage du nombre de jour dans une cotisation
* Amélioration de l'affichage des pressions
* TM (trademarks) enlevés et remplacés
## v3.5.3
* Fix le profil (division par 0 lorsque toutes les transactions d'un produit avaient été annulées)
## v3.5.2
* Fix la vue editKeg
## v3.5.1
* Les catégories apapraissent que si elles sont pas vides
* Nombre de produits affiché sur la liste des catégories
* Fix catégories et bières pressions
## v3.5.0
* Ajout des stats
* Ajout des catégories dynamiques
## v3.4.2
* Fix de getConfig
## v3.4.1
* Rajout d'un bouton actif sur les KegForm
* Suppression épic épicier, maitre brasseur et vice-président.
* Rajout responsable Phoenix Technopôle Metz
* Rajout de la charte alcool
## v3.4.0
* Fix bugs et améliorations
* Réparation de la génération de documents en latex
* Ajout des bulletions d'adhésion et certificats d'adhésion générés en latex
* Ajout des documents sur le site (statuts, règlement intérieur et menu)
* Changement de validation, invalidation des cotisations en supression simple
* Amélioration de l'admin
* Amélioration du classement par produit
## v3.3.3
* fix commande (moyen de paiment n'affectant pas le solde)
## v3.3.2
* fix de la vérification du solde dans la commande
* fix de l'affichage de la liste des fûts
## v3.3.1
* contains devient icontains pour enlever la sensibilité à la casse
## v3.3.0
* Ajout d'icônes
* Le . est utilisé pour les décimaux
* Ajout de liens vers les profils de produits et utilisateurs
* Ajout de cotisations dans les transactions
* Ajout d'une page d'accueil. Les pressions du moment y sont affichées
* Belles couleurs sur le diagramme
* Verouillage automatique de la caisse
* Classement par produit
* Fix invalidation
* Recherche plus intuitive (le startswith devient contains)
* Easter egg sur 404
## v3.2.2
* Fix cotisation cancer
## v3.2.1
* Le module django_tex est directement inclu dans le projet (disparition du module sur pip)
## v3.2.0
* Ajout d'icônes (avec font awesome)
* Amélioration du diagramme sur le profil (couleurs, valeur pour les fromages et charcuts, seuil des 1%)
* Boutons flottants sur la page de transation (avec options pour activer ou désactiver)
* Ajout du module comptabilité (génération de relevé entre deux dates)
* Exportation en csv par groupe
* Liens pour ajouter/retirer des admins/superusers enlevés sur le profil
## v3.1.0
* Tronque la quantité d'alcool ingéré sur le profil (fix #8)
* La modification des produits retourne sur la pge de profil du produit (fix #9)
* Les rechargements affichés sur le profil s'arrête bien à 5 (fix #14)
* Seuls les bons moyens de paiement sont proposés dans les cotisations (fix #15)
* Seuls les bons produits sont proposés dans le formulaire de création de fût (fix #16)
* Ajout d'un formulaire pour exporter les utilisateurs au format csv (new feature #2)
* Ajout d'un système de suivi de pintes (new feature #25)
* Désactiver les utilisateurs depuis l'interface (new feature #10)
* Ajout d'une barre de recherche dans l'admin des profils (new feature #3)
* Corrections de mots dans les templates (fix #12)
* Fix de certaines permissions dans les templates de gestion de produits et d'utilisateurs (fix #21)
* Ajout d'un champ d'autocomplétion pour les produits dans les transactions (new feature #20)
* Annulation de rechargement (new feature #23)

## v3.0.2
* Fix des annulations de consommations

## v3.0.1
* Fix page inactive
* Fix prix dans les historiques de consommations
