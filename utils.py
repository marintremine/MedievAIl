from models.obstacle import *

def bfs_path(self, start_x, start_y, goal_x, goal_y):
    """
    Recherche le plus court chemin entre deux coordonnées sur une grille en utilisant l'algorithme BFS.
    Il effectue plusieurs vérifications
    – Si la nouvelle position est dans les limites de la carte
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

    def is_obstacle_at(x, y):
        """Vérification de si un obstacle se trouve à la position (x, y)"""
        for obj in self.list_objects:
            if isinstance(obj, Obstacle) and obj.x == x and obj.y == y:
                return True
        return False

    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    visited = set()
    queue = [(start_x, start_y, [(start_x, start_y)])]
    visited.add((start_x, start_y))

    while queue:
        x, y, path = queue.pop(0)
        if (x, y) == (goal_x, goal_y):
            return path

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= nx <= self.map_width and
                    0 <= ny <= self.map_height and
                    (nx, ny) not in visited and
                    not is_obstacle_at(nx, ny)):
                visited.add((nx, ny))
                queue.append((nx, ny, path + [(nx, ny)]))

    return []
