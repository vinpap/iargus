"""
Un seul endpoint : /predict, pour faire une prédiction à partir des infos données par l'utilisateur
Bien sécuriser l'API avec quelque chose de mieux qu'un token unique

Fonctionnement :
Le modèle est entraîné avec des données stockées dans une base de données et stocké à l'aide de MLflow. 
On check les performances du modèles à intervalles réguliers. Le seuil de performances acceptable
est défini à l'avance en MAPE (e.g. pas plus de 15% d'erreur sur le prix en moyenne, fixé par les dirigeants 
de l'Argus dans le scénario). Ce monitoring est réalisé à l'aide d'un script exécuté à intervalles
réguliers. Le réentraînement est automatisé si le seuil n'est pas respecté. Si le seuil n'est toujours
pas respecté après le réentraînement, on en alerte les gestionnaires de l'Argus par email.

"""