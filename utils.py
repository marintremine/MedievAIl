from models.obstacle import *

def bfs_path(start, end, map_width, map_height ,list_objects):
    """
    Recherche le plus court chemin entre deux coordonnées sur une grille en utilisant l'algorithme BFS.
    Il effectue plusieurs vérifications
    - Si la nouvelle position est dans les limites de la carte
    - Si elle n'a pas déjà été visitée
    - S'il n'y a pas d'obstacle à cette position.

    Parameters
    ----------
    start_x : int
        Coordonnée X de départ.
    start_y : int
        Coordonnée Y de départ.
    goal_x : int
        Coordonnée X d'arrivée.
    goal_y : int
        Coordonnée Y d'arrivée.

    Returns
    -------
    list[tuple[int, int]]
        Liste ordonnée des coordonnées constituant le chemin trouvé.
        Retourne une liste vide si aucun chemin n'existe.
    """
    def is_in_map(x, y):
        """Vérification si les coordonnées sont dans les limites de la carte"""
        return 0 <= x < map_width and 0 <= y < map_height

    def is_obstacle_at(x, y):
        """Vérification de si un obstacle se trouve à la position (x, y)"""
        for obj in list_objects:
            if isinstance(obj, Obstacle) and obj.x == x and obj.y == y:
                return True
        return False

    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]

    start_x, start_y = start
    end_x, end_y = end

    visited = set()
    queue = [(start_x, start_y, [(start_x, start_y)])]
    visited.add((start_x, start_y))

    while queue:
        x, y, path = queue.pop(0)
        if (x, y) == (end_x, end_y):
            return path

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (is_in_map(nx, ny) and (nx, ny) not in visited and not is_obstacle_at(nx, ny)):
                visited.add((nx, ny))
                queue.append((nx, ny, path + [(nx, ny)]))
    return []