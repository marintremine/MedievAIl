from __future__ import annotations
from models.unit import *
from enum import Enum

from dataclasses import dataclass

@dataclass(frozen=True)
class GeneralId:
    cls_name: str   
    instance_id: int 

    def __str__(self):
        return f"{self.cls_name}#{self.instance_id}"

class General:
    def __init__(self, name: str, battle_model) -> None: # pyright: ignore[reportUndefinedVariable]
        self.name = name
        self.battle_model = battle_model

        cls = type(self)
        if not hasattr(cls, "_counter"):
            cls._counter = 0

        cls._counter += 1
        self.instance_id = cls._counter
        

    def get_closest_enemy(self, unit, enemy_list):
        """
        Trouve l'ennemi le plus proche dans une liste donnée en utilisant la distance de Manhattan
        """
        alive_enemies = (enemy for enemy in enemy_list if enemy.is_alive())
        manhattan = lambda enemy: abs(unit.x - enemy.x) + abs(unit.y - enemy.y)
        return min(
            alive_enemies,
            key=manhattan,
            default=None
        )

    def sort_army(self, army):
        """
        :param army:
        :return: dictionnaire contenant des listes d'unités de même type.
        """
        dict_army = {}
        for unit in army:
            if type(unit).__name__ not in dict_army:
                dict_army[type(unit).__name__] = []
            dict_army[type(unit).__name__].append(unit)
        return dict_army

    def manhattan(self, a, b):
        """
        Renvoie la manhattan
        """
        return abs(a.x - b.x) + abs(a.y - b.y)

    def decide(self) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.name}#{self.instance_id}"

class Daft(General):
    def __init__(self, battle_model):
        super().__init__("Daft", battle_model)

    def decide(self) -> None:
        my_units = self.battle_model.get_army(self)
        enemy_units = self.battle_model.get_enemy_army(self)

        if not enemy_units:
            return

        for unit in my_units:
            if not unit.is_alive() or not isinstance(unit.order, Wait):
                continue

            closest_enemy = self.get_closest_enemy(unit, enemy_units)
            if closest_enemy is None:
                continue

            unit.order = Attack(unit, closest_enemy)



class BrainDead(General):
    """
    Un général qui ne donne aucun ordre, toute l'armée est en mode Defense donc les unités attaquent les ennemis dans leur portée.
    """
    def __init__(self, battle_model):
        super().__init__("BrainDead", battle_model)

    def decide(self) -> None:
        for unit in self.battle_model.get_army(self):
           unit.order = Defense(unit)



class IA_Global(General):
    class Strategy(Enum):
        OFFENSIVE = 1
        DEFENSIVE = 2
        LURE = 3

    def __init__(self, battle_model):
        self.strategy = self.Strategy.OFFENSIVE
        self.tactics_methods = [
            self.tactic_hit_and_run,
            self.tactic_bonus_damage,
            self.tactic_safe_position,
            self.tactic_group_units,
            self.tactic_attack_weakest,
            self.tactic_one_shot_enemy,
            self.tactic_focus_nearest,
            self.tactic_group_units,
            self.tactic_avoid_hard_counters,
        ]
        self.army_size = None
        self.formation_broken = False
        super().__init__("IA_Global", battle_model)


    def tactic_hit_and_run(self, unit):
        weight = 0
        order = None
        return weight, order

    def tactic_safe_position(self, unit):
        """Si le puissance de l'unité est inférieuers a 30% il joint le point de rassemblement qui est la moyenne de tous ces alléis"""
        weight = 0
        order = None
        if unit.hp > (unit.max_hp * 25 / 100):
            return weight, order
        allies = self.battle_model.get_army(self)
        if not allies:
            return weight, order

        coordd = self.find_meeting_point(allies)
        #On regarde si on se trouve déjà dans le groupe de coordonnées
        if abs(unit.x - coordd[0]) + abs(unit.y - coordd[1]) <=2:
            return 0, None
        weight= 40
        order = Move(unit, coordd[0], coordd[1])
        return weight, order

    def tactic_avoid_hard_counters(self, unit):
        """
        fuis les bonus des ennemis
        """
        weight = 0
        order = None
        enemies = self.battle_model.get_enemy_army(self)
        for enemy in enemies:
            bonus= enemy.bonus_attacks.get(type(unit), 0)
            if bonus > 0:
                dist = self.manhattan(unit, enemy)
                threat_range = enemy.range + enemy.speed + 1
                if dist <= threat_range:
                    if self.calc_damages(unit, enemy) >= enemy.hp:
                        continue
                    weight = 80
                    coor= self.find_meeting_point(self.battle_model.get_army(self))
                    order = Move(unit, coor[0], coor[1])
                    return weight, order
        return weight, order

    def tactic_bonus_damage(self, unit):
        """Cherche la cible sur laquelle on a un bonus d'attaque."""
        weight = 0
        order = None
        if not unit.bonus_attacks:
            return weight, order
        enemy_army = self.battle_model.get_enemy_army(self)
        target = None
        best_dist = 999
        for enemy in enemy_army:
            if type(enemy) in unit.bonus_attacks:
                dist = self.manhattan(unit, enemy)
                if dist < best_dist:
                    best_dist = dist
                    target = enemy
        if target:
            if best_dist <= max(1, unit.range):
                weight = 95
                order = Attack(unit, target)
            else:
                weight = 90
                order = Move(unit, target.x, target.y)
        return weight, order

    def tactic_attack_weakest(self, unit):
        """Attaque l'ennemi le plus faible à portée."""
        weight = 0
        order = None
        targets = self.find_enemies_in_scope(unit, self.battle_model.get_enemy_army(self))
        if targets:
            weakest = min(targets, key=lambda e: e.hp)
            weight = 60
            order = Attack(unit, weakest)
        return weight, order


    def tactic_one_shot_enemy(self, unit):
        """ Est il possibke de oneshotter un enemi et si oui le plus fort (max hp)"""
        weight = 0
        order = None
        enemies = self.battle_model.get_enemy_army(self)
        enemy_to_shot = self.find_enemies_in_scope(unit, enemies)
        candidates = []
        if enemy_to_shot:
            for enemy in enemy_to_shot:
                potential_dmg= self.calc_damages(unit, enemy)
                if potential_dmg >= enemy.hp:
                    weight = 100
                    candidates.append(enemy)
            if candidates:
                target = self.find_highest_hp(candidates)
                order = Attack(unit, target)
        return weight, order

    def find_all_in_scope(self, target, list_candidate):
        candidate_scope = set()
        for candidate in list_candidate:
            dist= self.manhattan(target, candidate)
            if candidate.range >= dist:
                candidate_scope.add(candidate)
        return candidate_scope

    def find_enemies_in_scope(self, unit, enemies):
        return [enemy for enemy in enemies if unit.range >= self.manhattan(unit, enemy)]

    def calc_damages(self, unit, target):
        dmg = unit.attack
        bonus = unit.bonus_attacks.get(type(target), 0)
        return dmg + bonus

    def squad_attack(self, busy_list, army):
        """Attaque les enemis en groupe afin de faire le plus de dégâts possible"""

        enemy_army = self.battle_model.get_enemy_army(self)
        sorted_enemies = sorted([e for e in enemy_army], key=lambda x: x.hp)
        for enemy in sorted_enemies:
            squad = self.find_all_in_scope(enemy, army)
            if squad:
                target_hp = 0
                candidates = set()
                for soldier in squad:
                    if soldier in busy_list:
                        continue
                    target_hp+= self.calc_damages(soldier, enemy)
                    candidates.add(soldier)
                    if target_hp >= enemy.hp:
                        for unit in candidates:
                            unit.order = Attack(unit, enemy)
                            busy_list.add(unit)
                        break

    def tactic_focus_nearest(self, unit):
        """Le moteur principal : aller vers l'ennemi et taper"""
        weight = 10  # Poids de base pour que l'unité fasse au moins ça
        order = None
        enemies = unit.nearest_enemies()
        if enemies:
            target = enemies[0]
            dist = self.manhattan(unit, target)
            if dist <= max(1,unit.range):
                order = Attack(unit, target)
                weight = 50
            else:
                order = Move(unit, target.x, target.y)
                weight = 20

        return weight, order

    def tactic_group_units(self, unit):
        """Si aucun ennemi en vue, on se regroupe"""
        weight = 5
        order = Wait(unit)
        friends = self.battle_model.get_army(self)
        if len(friends) > 1:
            coor= self.find_meeting_point(friends)

            if abs(unit.x - coor[0]) + abs(unit.y - coor[1]) > 3:
                order = Move(unit, coor[0], coor[1])

        return weight, order

    def find_highest_hp(self, units):
        max_hp = units[0]
        for unit in units:
            if unit.hp > max_hp.hp:
                max_hp = unit
        return max_hp

    def find_meeting_point(self, army):
        x_avg = 0
        y_avg = 0
        min_x = self.battle_model.map_width
        max_x = 0
        for unit in army:
            x_avg += unit.x
            y_avg += unit.y
            if unit.x > max_x:
                max_x = unit.x
            if unit.x < min_x:
                min_x = unit.x

        x_avg //= len(army)
        y_avg //=len(army)
        return (x_avg, y_avg)

    def decide(self) -> None:
        if self.army_size is None:
            self.army_size = len(self.battle_model.get_army(self))
        if (self.army_size * 20 // 100) >= self.army_size and self.army_size is not None:
            self.strategy = self.Strategy.DEFENSIVE
        busy_list = set()
        army = self.battle_model.get_army(self)
        self.squad_attack(busy_list, army)
        match self.strategy:
            case self.Strategy.OFFENSIVE:
                for unit in self.battle_model.get_army(self):
                    best_tactic_name = "Grouped"
                    if unit in busy_list:
                        continue
                    best_weight = 0
                    enemies = unit.nearest_enemies()
                    best_order = Wait
                    for tactic in self.tactics_methods:
                        weight, order = tactic(unit)
                        if weight > best_weight:
                            best_weight = weight
                            best_order = order
                            best_tactic_name = tactic
                    unit.order = best_order
            case self.Strategy.DEFENSIVE:
                for unit in self.battle_model.get_army(self):
                    unit.order = Defense(unit)
            case self.Strategy.LURE:
                print("Lure strategy not yet implemented.")


class Aegis(General):
    """
    Un général qui privilégie la contre-attaque : ses Knight tiennent la position
    sous la couverture des Crossbowman et ne chargent que lorsque l'affrontement est favorable.
    """

    def __init__(self, battle_model):
        super().__init__("Aegis", battle_model)

    def has_crossbow_support(self, unit):
        """
        Vérifie si l'unité a un support archer
        """
        for ally in self.battle_model.get_army(self):
            if not ally.is_alive():
                continue
            if ally is unit:
                continue
            if ally.name == "Crossbowman" and self.manhattan(unit, ally) <= 5:
                return True
        return False

    def get_best_enemy(self, unit, enemies):
        """
        Choisie le meilleur enemies à cibler en attribuant un score en fonction du type
        """
        best_enemy = None
        best_score = None
        for enemy in enemies:
            score = -(self.manhattan(unit, enemy))
            if unit.name == "Knight" and enemy.name == "Crossbowman":
                score += 3
            if unit.name == "Knight" and enemy.name == "Pikeman" and self.manhattan(unit, enemy) > 2:
                score -= 5
            if best_score is None or score > best_score:
                best_score = score
                best_enemy = enemy
        return best_enemy

    def decide(self) -> None:
        enemies = self.battle_model.get_enemy_army(self)
        if not enemies:
            return

        for unit in self.battle_model.get_army(self):
            if not isinstance(unit.order, Wait):
                continue

            target = self.get_best_enemy(unit, enemies)
            if not target:
                unit.order = Wait(unit)
                continue

            if unit.name != "Knight":
                unit.order = Attack(unit, target)
                continue

            if self.manhattan(unit, target) <= 2:
               unit.order = Attack(unit, target)
            elif target.name == "Pikeman" and self.has_crossbow_support(unit):
               unit.order = Wait(unit)
            else:
               unit.order = Attack(unit, target)

class GeneralAugustin(General):
    def __init__(self, battle_model):
        super().__init__("General-Augustus", battle_model)

    def decide(self) -> None:
        army = self.battle_model.get_army(self)
        sorted_army = self.sort_army(army)
        enemies = self.battle_model.get_enemy_army(self)
        meeting_point = self.find_meeting_point(enemies)
        if not enemies:
            return
        if "Pikeman" in sorted_army:
            pikemen = sorted_army["Pikeman"]
        elif "Knight" in sorted_army:
            knights = sorted_army["Knight"]
        elif "Crossbowman" in sorted_army:
            crossbowmen = sorted_army["Crossbowman"]

        for unit in army:
            prox_targets = self.find_all_in_scope(unit, enemies)
            if not prox_targets:
                coor = self.measure_max_damage_without_target(unit, enemies, meeting_point)
                if coor:
                    match coor[0]:
                        case 1:
                           unit.order = Move(unit, coor[1][0], coor[1][1])
                        case 2:
                           unit.order = Move(unit, coor[1], coor[2])
                        case 3:
                           unit.order = Defense(unit)
                        case _:
                           unit.order = Wait(unit)

                else:
                   unit.order = Defense(unit)
            else:
                target = self.measure_max_damage_target(unit, prox_targets)
                if target:
                   unit.order = Attack(unit, target[1])
                else:
                   unit.order = Defense(unit)


    def measure_max_damage_target(self, unit, prox_targets):
            candidate = []
            candidate_bonus = []
            for next in prox_targets:
                if str(type(next).__name__) in unit.bonus_attacks:
                        candidate_bonus.append(next)
                if (next.hp - unit.attack)  <= 0:
                    candidate.append(next)
            if candidate_bonus:
                target = self.find_highest_hp(candidate_bonus)
                return [1,target]

            if not candidate:
                target = self.find_lowest_hp(prox_targets)
                return [1, target]


            sorted_target = self.sort_army(candidate)
            if "Knight" in sorted_target:
                knights = sorted_target["Knight"]
                target = self.find_highest_hp(knights)
                return [1,target]
            elif "Crossbowman" in sorted_target:
                crossbowmen = sorted_target["Crossbowman"]
                target = self.find_highest_hp(crossbowmen)
                return [1,target]
            elif "Pikeman" in sorted_target:
                pikemen = sorted_target["Pikeman"]
                target = self.find_highest_hp(pikemen)
                return [1,target]

    def is_same_unit(self, unit, enemy):
        return type(unit).__name__ == type(enemy).__name__

    def find_lowest_hp(self, units):
        lowest = units[0]
        for unit in units:
            if lowest.hp > unit.hp:
                lowest = unit
        return lowest



    def measure_max_damage_without_target(self, unit, enemies, meeting_point):
        exposure = self.map_enemy(unit, enemies)
        if not exposure:
            return [2, meeting_point[1][0], meeting_point[1][1]]

        else:
            matrix_pos = self.matrice_pos(unit)
            for pos in matrix_pos:
                decision = self.in_security(pos[0], pos[1], enemies)
                if decision:
                    return [2, pos[0], pos[1]]
        target = self.find_lowest_hp(enemies)
        if target is not None:
            return [2, target.x, target.y]
        return [3]

    def matrice_pos(self, unit):
        x_init = unit.x -1
        y_init = unit.y -1
        pos_matrix = []
        for i in range(x_init, x_init +3):
            for j in range(y_init, y_init + 3):
                pos_matrix.append((i, j))
        return pos_matrix



    def in_security(self, x, y, enemies):
        near_enemies = self.map_enemy_coor_unit(x, y, enemies)
        if near_enemies:
            for enemy in enemies:
                distance = self.calc_distance_coor_unit(x, y, enemy)
                if enemy.range >= distance:
                    return False
            return True
        else:
            return True

    def find_meeting_point(self, enemies):
        x_avg = 0
        y_avg = 0
        min_x = self.battle_model.map_width
        max_x = 0
        for unit in enemies:
            x_avg += unit.x
            y_avg += unit.y
            if unit.x > max_x:
                max_x = unit.x
            if unit.x < min_x:
                min_x = unit.x

        x_avg //= len(enemies)
        y_avg //=len(enemies)
        return [(min_x, y_avg), (x_avg, y_avg), (max_x, y_avg)]

    def can_escape_enemy_range(self, unit, enemy):
        distance = self.calc_distance(unit, enemy)
        if distance + unit.speed <= enemy.range :
            return []
        else:
            dx = unit.x - enemy.x
            dy = unit.y - enemy.y
            ratio= unit.speed / distance
            x = unit.x + (dx * ratio)
            y = unit.y + (dy * ratio)
            return [x, y]

    def map_enemy(self, unit, enemies):
        near_enemies =[]
        for enemy in enemies:
            distance = self.calc_distance(unit, enemy)
            if enemy.range >= distance:
                near_enemies.append(enemy)
        return near_enemies

    def map_enemy_coor_unit(self, x, y, enemies):
        near_enemies = []
        for enemy in enemies:
            distance = self.calc_distance_coor_unit(x, y, enemy)
            if enemy.range >= distance:
                near_enemies.append(enemy)
        return near_enemies

    def find_highest_hp(self, units):
        max_hp = units[0]
        for unit in units:
            if unit.hp > max_hp.hp:
                max_hp = unit
        return max_hp

    def find_all_in_scope(self,unit,  enemies):
        prox_enemies = []
        for enemy in enemies:
            distance = self.calc_distance(unit, enemy)
            if unit.range >= distance:
                prox_enemies.append(enemy)
        else:
            return prox_enemies

    def calc_max_loss(self, unit, enemies):
        risk = enemies[0]
        for enemy in enemies:
            if enemy.attack > risk.attack:
                risk = enemy
        return risk

    def calc_distance(self, unit, enemy):
        return abs((enemy.x - unit.x) + (enemy.y - unit.y))

    def calc_distance_coor_unit(self, x, y, unit):
        return abs(x - unit.x) + abs(y - unit.y)


class MoveTestGeneral(General):
    """
    Un général qui ordonne à chaque unité de se déplacer vers des coordonnées aléatoires sur la carte si elle est en attente.
    """
    def __init__(self, battle_model):
        super().__init__("MoveTestGeneral", battle_model)

    def decide(self) -> None:
        for unit in self.battle_model.get_army(self):
            if isinstance(unit, Unit) and unit.is_alive() and isinstance(unit.order, Wait):
                # pick random coords inside the map 
                new_x = random.randrange(0, self.battle_model.map_width)
                new_y = random.randrange(0, self.battle_model.map_height)

                unit.order = Move(unit, new_x, new_y)



class AttackTestGeneral(General):
    """
    Un général qui ordonne à chaque unité d'attaquer une unité ennemie aléatoire si elle est en attente.
    """
    def __init__(self, battle_model):
        super().__init__("AttackTestGeneral", battle_model)

    def decide(self) -> None:
        enemy_units = self.battle_model.get_enemy_army(self)

        for unit in self.battle_model.get_army(self):
            if unit.is_alive() and isinstance(unit.order, Wait):
                if enemy_units:
                    # choose a random enemy unit to attack
                    target = random.choice(tuple(enemy_units))
                    unit.order = Attack(unit, target)
                else:
                    unit.order = Wait(unit)

    

class MomoIA(General):
    def __init__(self, battle_model):
        super().__init__("MomoIA", battle_model)
        self.posx_last_pike = 0
        self.posy_last_pike = 0
        
    def is_anyone_there(self, px, py, ux, uy, R):
        dx = ux - px
        dy = uy - py
        distance = (dx*dx + dy*dy)**0.5
        return distance <= R
    
    def dist_ht_2(self, x1, y1, x2, y2):
        distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return distance >= 2


    def decide(self):
        enemy_units = self.battle_model.get_enemy_army(self)
        if not enemy_units:
            return
        n = len(enemy_units)
        avg_x = sum(u.x for u in enemy_units) / n
        avg_y = sum(u.y for u in enemy_units) / n
        for unit in self.battle_model.get_army(self):
            dx = avg_x - unit.x
            dy = avg_y- unit.y
            distance = (dx*dx + dy*dy) ** 0.5
            if distance == 0:
                distance = 1
            new_x = unit.x+dx / distance
            new_y = unit.y+dy / distance
            nearest = min(enemy_units, key=lambda e: (e.x - unit.x)**2 + (e.y - unit.y)**2)
            dist2 = (nearest.x - unit.x)**2 + (nearest.y - unit.y)**2

            #Pikeman
            if isinstance(unit, Pikeman):
                self.posx_last_pike = unit.x
                self.posy_last_pike = unit.y
                if abs(avg_x-unit.x) <=3 and abs(avg_y -unit.y) <= 3:
                    unit.order = Attack(unit, nearest)
                    # if dist2 <= 4: 
                    #    unit.order = Attack(unit, nearest)
                else :
                    for u in enemy_units :
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x , u.y, 2)
                    if not anyone :
                        unit.order = Attack(unit, nearest)
                    else :
                        unit.order = Move(unit, new_x, new_y)

            # Knights
            if isinstance(unit, Knight):
                if self.posx_last_pike != 0 and self.posy_last_pike != 0:
                    if self.dist_ht_2(unit.x, unit.y, self.posx_last_pike, self.posy_last_pike):
                        Wait(unit)
                        
                if abs(avg_x-unit.x) <= 3 and abs(avg_y-unit.y) <= 3:
                   unit.order = Attack(unit, nearest)
                else:
                    for u in enemy_units:
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x, u.y, 2)
                    if not anyone:
                        unit.order = Attack(unit, nearest)
                    else:
                        unit.order = Move(unit, new_x, new_y)

            #Crossbowman
            if isinstance(unit, Crossbowman):
                if abs(avg_x-unit.x) <=3 and abs(avg_y -unit.y) <= 3:
                    unit.order = Attack(unit, nearest)
                    # if dist2 <= 4: 
                    #    unit.order = Attack(unit, nearest)
                else :
                    for u in enemy_units :
                        anyone = self.is_anyone_there(avg_x, avg_y, u.x , u.y, 2)
                    if not anyone :
                        unit.order = Attack(unit, nearest)
                    else :
                        unit.order = Move(unit, new_x, new_y)
            anyone = False


class RPSGeneral(General):
    """
    IA avec :
    - priorité de type (RPS : Pikeman attaque Knight attaque Crossbowman attaque Pikeman)
    - un score qui calcule = bonus RPS + bonus ennemi faible (HP bas)+ bonus ennemi dangereux (haut DPS / bonus_attacks)-pénalité distance (Manhattan)
    - prise en compte du range (unit.range) ensuite on attack ou on attend
    """
    TARGET_PREFS = {
        "Pikeman":      ["Knight", "Crossbowman", "Pikeman"],
        "Knight":       ["Crossbowman", "Pikeman", "Knight"],
        "Crossbowman":  ["Pikeman", "Knight", "Crossbowman"],
    }

    def __init__(self, battle_model):
        super().__init__("RPS", battle_model)

    # calcul du score

    def score_target(self, unit: Unit, enemy: Unit) -> float | None:
        if not enemy.is_alive():
            return None

        dist = self.manhattan(unit, enemy)
        score = 0.0
        #pénalité distance
        score -= dist * 2.0
        #bonus RPS (type préféré)
        prefs = self.TARGET_PREFS.get(unit.name, [])
        if enemy.name in prefs:
            rps_weight = len(prefs) - prefs.index(enemy.name)
            score += rps_weight * 10.0

        #bonus ennemi faible
        if enemy.max_hp > 0:
            hp_ratio = enemy.hp / enemy.max_hp
            score += (1.0 - hp_ratio) * 8.0  

        # bonus ennemi dangereux 
        score += enemy.attack * 0.5

        #bonus si notre type est dans ses bonus_attacks
        if unit.__class__ in enemy.bonus_attacks:
            score += enemy.bonus_attacks[unit.__class__] * 0.5

        return score
    
    #prendre le meilleur score pour l'attaquer
    def get_best_enemy(self, unit: Unit, enemies: list[Unit]) -> Unit | None:
        best = None
        best_score = None
        for e in enemies:
            s = self.score_target(unit, e)
            if s is None:
                continue
            if best_score is None or s > best_score:
                best_score = s
                best = e
        return best

    #déplacement

    def get_step_towards(self, unit: Unit, target: Unit) -> tuple[int, int] | None:
        """
        Utilise le mini-pathfinding de BattleModel pour obtenir la prochaine case.
        """
        start = (unit.x, unit.y)
        end = (target.x, target.y)
        nxt = self.battle_model.shortest_path(unit, start, end)
        return nxt  # soit (nx, ny), soit None si bloqué

    #décision
    def decide(self) -> None:
        enemies = self.battle_model.get_enemy_army(self)
        if not enemies:
            return

        for unit in self.battle_model.get_army(self):
            if not unit.is_alive() or not isinstance(unit.order, Wait):
                continue

            target = self.get_best_enemy(unit, enemies)
            if target is None:
                unit.order = Wait(unit)
                continue

            dist = self.manhattan(unit, target)
            # range = unit.range (0 pour Pikeman / Knight, 5 pour Crossbowman)
            attack_range = max(1, unit.range) 
            # Si possible d'attaquer ce tour, on Attack, sinon on Move vers la cible
            if dist <= attack_range:
                unit.order = Attack(unit, target)
            else:
                step = self.get_step_towards(unit, target)
                if step is None:
                    # bloqué : on peut attendre ou faire autre chose
                    unit.order = Wait(unit)
                else:
                    nx, ny = step
                    unit.order = Move(unit, nx, ny)


def generalFactory(general_type: str, battle_model) -> General:
    general_classes = {
        "daft": Daft,
        "braindead": BrainDead,
        "aegis": Aegis,
        "movetest": MoveTestGeneral,
        "attacktest": AttackTestGeneral,
        "augustus" : GeneralAugustin,
        "momoia": MomoIA,
        "rps": RPSGeneral,
        "iaglobal": IA_Global,
    }
    key = general_type.lower()
    if key in general_classes:
        return general_classes[key](battle_model)
    else:
        raise ValueError(f"Unknown general type: {key}")


