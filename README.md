CoopeV3 by Nanoy

## Installation 
Pour installer le projet : 
```
git clone https://gitlab.rezometz.org/coope/coopeV3.git
```
Il faut ensuite créer un environnement virtuel associé à ce projet (si le dossier de l'env se trouve dans le dossier du projet, appelez le venv).
Installer ensuite toutes les dépendances du projet : 
```
pip3 install -r requirements.txt
```
Il faut ensuite copier le fichier `local_settings.example.py` en un fichier `local_settings.py` dans le dossier coopeV3 puis le remplir avec les informations. 
Executez ensuite les commandes suivantes :
```
./manage.py migrate
./manage.py collectstatic
```
Vous pouvez créer un super-user en executant la commande 
```
./manage.py createsuperuser
```
