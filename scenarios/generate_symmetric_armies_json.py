import json
import random

# Paramètres de la map
map_width = 200
map_height = 200

# Paramètres des unités
num_crossbow = 80
num_knight = 80
num_pikeman = 80
num_obstacle = 0

# Générer obstacles
obstacles = []
obstacles += [{'type':'Bush', 'x':random.randint(0,map_width-1,), 'y':random.randint(0,map_height-1)} for _ in range(num_obstacle)]
obstacles += [{'type':'Rock', 'x':random.randint(0,map_width-1,), 'y':random.randint(0,map_height-1)} for _ in range(num_obstacle)]
obstacles += [{'type':'Tree', 'x':random.randint(0,map_width-1,), 'y':random.randint(0,map_height-1)} for _ in range(num_obstacle)]
# Générer armée 1
army1 = []
army1 += [{'type':'crossbowman', 'x':i, 'y':0} for i in range(num_crossbow)]
army1 += [{'type':'knight', 'x':i, 'y':10} for i in range(num_knight)]
army1 += [{'type':'pikeman', 'x':i, 'y':16} for i in range(num_pikeman)]

# Générer armée 2 (symétrique)
army2 = []
army2 += [{'type':'crossbowman', 'x':map_width-1-i, 'y':map_height-1} for i in range(num_crossbow)]
army2 += [{'type':'knight', 'x':map_width-1-i, 'y':map_height-2} for i in range(num_knight)]
army2 += [{'type':'pikeman', 'x':map_width-1-i, 'y':map_height-3} for i in range(num_pikeman)]

# Créer le dictionnaire final
battlefield = {
    'map_width': map_width, 
    'map_height': map_height,
    'obstacles': obstacles,
    'army1': army1,
    'army2': army2
}

# Écrire dans un fichier JSON
with open('scenarios/symmetric_armies.json', 'w') as f:
    json.dump(battlefield, f, indent=2)

print('Fichier symmetric_armies.json généré avec succès !')