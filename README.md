#Compilateur de string et float en typage dynamique 

compilateur partie string : 
## Table des matières 
[String](#string)
[Float](#float)
[Typage dynamique](#typage-dynamique)
[Factorielle](#factorielle)


###String: 
> Une string s'écrit entre guillemets. La concaténation se fait par l'opérateur +, et n'accepte que les strings (pas sous forme de variable). Les string ne peuvent être affectées à deux valeurs différentes: typiquement a = "ab" et b="ab" mènera à une erreur admettent deux méthodes: 

> len("string"): prend un string en argument (pas sous forme de variable) et renvoie la taille de la chaine de charactère + 1 
	
> charAt("string",int): prend un string et un entier en argument (pas sous forme de variable) et renvoie le rang du charactère de la chaine de charactère 
	au rang indiqué. Le rang est déterminé comme en C ou Pyhton: le premier élément est d'indice 0, et ainsi de suite. 

###Float: 
> les float s’écrivent avec une virgule dans le code mais avec un point en entrée et en sortie.
> les variables sont non typées.
> on peut additionner deux entiers ensemble et deux floats ensemble mais pas un entier et un float.

###Typage dynamique: 
> Une variable peut passer d'un type à l'autre au cours du code. Le code reconnait en continu le type de la variable (valable pour les compilos string et float) 

###Factorielle: 
> pour calculer une factorielle, il faut un nombre suivi d'un "!" ou une variable suivie d'un "!" (dans les deux cas on passe à travers deux expressions différentes), tant que on écrit pas d'expression factorielle dans le return, et qu'on ne demande pas factorielle de 0, on obtient la bonne valeur. 

Andrea Dubruel, Logan Marcellin et Paul Chriqui 
