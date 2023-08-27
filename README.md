
## English users
Please note about the lang of this package. The "core" (rpiql.py) is in English. The Web UI and documentation is in French. I fix them shortly.

# RPI-QL v2
C'est la nouvelle version de RPI-QL, elle a été refaite pour plus de flexibilité. Ce script permet d'imprimer les étiquettes basé sur des Templates, et d'un module pour un service Web pour en créer via une interface, pour un usage local ou distant.

La version précédente avais des design prédéfini et peut personnalisable, vous étiez dont limité par les design établie par le script de cette époque.

Avec le support des templates, vous pouvez créer en ajoutant vos images, textes et code à barre avec plus de précision et de flexibilité. Il est possible de l'utiliser sous Linux et Windows.
 

## Nouveautés

* Refonte du code pour la création flexible d'étiquette,
* Ajout du support de "Templates" pour la création d'étiquettes personnalisés,
* Refont de l'interface Web pour supporter les "Templates" et simplification du design,
* Support de Linux, et Windows.

## To Do

* Impression depuis l'interface Web
* Intégration du "wrap" pour le texte
* Support de `;`, `"` et `'` dans les champs personnalisables

## Prérequis

* Python 3
* Pilotes Brother QL Officiel
* (Linux) Brother-QL Python librairie (https://pypi.org/project/brother-ql/)
* (Windows) Brother b-PAC3
