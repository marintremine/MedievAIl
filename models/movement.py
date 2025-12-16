# models/movement.py
import math
from collections import defaultdict

CELL_SIZE = 1.0

class SpatialGrid:
    def __init__(self):
        self.cells = defaultdict(list)

    def clear(self):
        self.cells.clear()

    def insert(self, unit):
        cx = int(unit.x // CELL_SIZE)
        cy = int(unit.y // CELL_SIZE)
        self.cells[(cx, cy)].append(unit)

    def neighbors(self, unit):
        cx = int(unit.x // CELL_SIZE)
        cy = int(unit.y // CELL_SIZE)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                yield from self.cells.get((cx + dx, cy + dy), [])


def desired_velocity(unit, tx, ty):
    dx = tx - unit.x
    dy = ty - unit.y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0.0, 0.0
    return (
        dx / dist * unit.speed,
        dy / dist * unit.speed
    )


def slide_velocity(vx, vy, nx, ny):
    dot = vx * nx + vy * ny
    return vx - dot * nx, vy - dot * ny


def resolve_collision(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    dist = math.hypot(dx, dy) or 0.0001

    penetration = (a.radius + b.radius) - dist
    if penetration <= 0:
        return

    nx = dx / dist
    ny = dy / dist

    total = a.density + b.density
    a_push = penetration * (b.density / total)
    b_push = penetration * (a.density / total)

    a.x += nx * a_push
    a.y += ny * a_push
    b.x -= nx * b_push
    b.y -= ny * b_push
