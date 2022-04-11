#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Dict, Tuple
import random
from math import sqrt
from copy import deepcopy
import numpy as np


class Shop:
    def __init__(self, nr, x: int, y: int, need_m: int, need_z: int, need_p: int, hours_punish: List[int]):
        self.nr = nr
        self.x: float = x
        self.y: float = y
        self.need_m: int = need_m
        self.need_z: int = need_z
        self.need_p: int = need_p
        self.hours = hours_punish
        self.hours_punish: float = hours_punish[0]*60 + hours_punish[1]

    def __eq__(self, other):
        return self.nr == other.nr

    def __hash__(self):
        return hash(self.nr)

    def get_name(self):
        return self.nr

    def get_position(self) -> Tuple[float, float]:
        return self.x, self.y

    def get_needs(self) -> Tuple[int, int, int]:
        return self.need_m, self.need_z, self.need_p

    def get_hour(self):
        if self.hours[1] == 0:
            zm = '{}:{}{}'.format(self.hours[0], self.hours[1], self.hours[1])
        else:
            zm = '{}:{}'.format(self.hours[0], self.hours[1])
        return zm

    def hour_penalty(self, act_hour: float) -> float:
        pen = 0
        if act_hour > self.hours_punish:
            diff = act_hour - self.hours_punish
            if 15 <= diff <= 60:
                pen = diff * 1 / 6
            elif diff > 60:
                pen = diff * 1 / 4
            return pen
        else:
            return pen


class Vehicle:
    petrol_cost: float = 6.5  # choose fixed value!

    def __init__(self, nr, velocity: float, cap: int, combustion: float):
        self.nr = nr
        self.velocity: float = velocity * 100 / 6
        self.cap: int = cap
        self.combustion: float = combustion / 100000
        self.act_cap: int = 0
        self.act_x: float = 0
        self.act_y: float = 0
        self.time: float = 180

    def __eq__(self, other):
        return self.nr == other.nr

    def __hash__(self):
        return hash(self.nr)

    def get_parameters(self) -> Tuple:
        return self.nr, self.velocity, self.cap, self.combustion

    def set_act_time(self, time: float) -> None:
        self.time = time

    def set_act_cap(self, pos: float) -> None:
        self.act_cap = pos

    def set_act_pos(self, x: float, y: float) -> None:
        self.act_x = x
        self.act_y = y

    def update_time(self, shop_stop: Shop) -> float:
        pos = shop_stop.get_position()
        distance = sqrt((self.act_x - pos[0]) ** 2 + (self.act_y - pos[1]) ** 2)
        new_time = distance/self.velocity
        self.set_act_time(self.time+new_time)
        return self.time

    def route_cost(self, shop_stop: Shop) -> float:
        pos = shop_stop.get_position()
        distance = sqrt((self.act_x - pos[0]) ** 2 + (self.act_y - pos[1]) ** 2)
        fuel = distance * self.combustion
        cost = fuel * self.petrol_cost
        self.set_act_pos(pos[0], pos[1])
        return cost

    def product_penalty(self) -> float:
        pen = 0
        if self.act_cap > self.cap:
            diff = self.act_cap - self.cap
            if diff <= 60:
                pen = diff * 1 / 6
            else:
                pen = diff * 1 / 4
            return pen
        else:
            return pen

    def sales_profit(self, shop_stop: Shop, wm: float, wz: float, wp: float) -> float:
        all_needs = shop_stop.get_needs()
        prof = wm * all_needs[0] + wz * all_needs[1] + wp * all_needs[2]
        self.set_act_cap(self.act_cap + all_needs[0] + all_needs[1] + all_needs[2])
        return prof


class Bakery:
    def __init__(self, cars: List[Vehicle], shops: List[Shop], wm: float, wz: float, wp: float, goal: float, size: int,
                 max_it: int):
        self.cars: List[Vehicle] = deepcopy(cars)
        self.shops: List[Shop] = deepcopy(shops)
        self.wm: float = wm  # choose fixed value!
        self.wz: float = wz
        self.wp: float = wp
        self.x: float = 0
        self.y: float = 0
        self.goal: float = goal
        self.size: int = size
        self.max_it: int = max_it

    def set_cars(self, c):
        self.cars = c

    def set_shops(self, s):
        self.shops = s

    def get_parameters(self) -> Tuple:
        return self.wm, self.wz, self.wp, self.goal, self.size, self.max_it

    def set_parameters(self, wm: float, wz: float, wp: float, goal: float, size: int, max_it: int):
        self.wm: float = wm
        self.wz: float = wz
        self.wp: float = wp
        self.goal: float = goal
        self.size: int = size
        self.max_it: int = max_it

    def goal_function(self, candidate: Dict[Vehicle, List[Shop]]) -> float:
        result = 0
        for vehicle in self.cars:
            for shop in candidate[vehicle]:
                result += (vehicle.sales_profit(shop, self.wm, self.wz, self.wp) - vehicle.route_cost(shop)
                           - vehicle.product_penalty() - shop.hour_penalty(vehicle.update_time(shop)))
            vehicle.set_act_time(180)
            vehicle.set_act_cap(0)
            vehicle.set_act_pos(0, 0)
        return result

    def first_solution(self) -> Dict[Vehicle, List[Shop]]:
        shuffle = random.sample(self.shops, len(self.shops))
        rand = random.sample(range(1, len(shuffle)), len(self.cars) - 1)
        sor = sorted(rand)
        sol = {}
        indx = 0
        for i in range(len(self.cars) - 1):  # use dict comprehension?
            sol[self.cars[i]] = shuffle[indx:sor[i]]
            indx = sor[i]
        sol[self.cars[len(self.cars) - 1]] = shuffle[indx:]
        return sol

    def swap_only_one_shop(self, candidate, first_veh, first_shop):
        sec_veh = random.choice([i for i in range(0, len(self.cars)) if i not in [first_veh]])
        sec_shop = random.randint(0, len(candidate[self.cars[sec_veh]]) - 1)
        first = candidate[self.cars[first_veh]][first_shop]
        second = candidate[self.cars[sec_veh]][sec_shop]
        return sec_veh, sec_shop, first, second

    def swap_only_one_car(self, candidate, first_veh, first_shop):
        sec_veh = first_veh
        sec_shop = random.choice([i for i in range(0, len(self.shops)) if i not in [first_shop]])
        first = candidate[self.cars[first_veh]][first_shop]
        second = candidate[self.cars[first_veh]][sec_shop]
        return sec_veh, sec_shop, first, second

    def normal_swap(self, candidate, first_veh, first_shop):
        sec_veh = random.randint(0, len(self.cars) - 1)
        sec_shop = random.randint(0, len(candidate[self.cars[sec_veh]]) - 1)
        first = candidate[self.cars[first_veh]][first_shop]
        second = candidate[self.cars[sec_veh]][sec_shop]
        if first_shop == sec_shop and first_veh == sec_veh:
            sec_shop -= 1
        return sec_veh, sec_shop, first, second

    def normal_insert(self, candidate, first_veh, first_shop):
        sec_veh = random.choice([i for i in range(0, len(self.cars)) if i not in [first_veh]])
        sec_shop = random.randint(0, len(candidate[self.cars[sec_veh]]))
        first = candidate[self.cars[first_veh]][first_shop]
        second = first
        return sec_veh, sec_shop, first, second

    def best_neighbor(self, candid: Dict[Vehicle, List[Shop]], t_list: List, s_best: Dict[Vehicle, List[Shop]]) \
            -> Tuple[Dict[Vehicle, List[Shop]], List]:
        it = 20
        tabu_list = deepcopy(t_list)
        best, best_candidate = deepcopy(s_best), deepcopy(candid)
        tab = None
        for j in range(it):
            candidate = deepcopy(candid)
            first_veh = random.randint(0, len(self.cars) - 1)  # index of first vehicle
            first_shop = random.randint(0, len(candidate[self.cars[first_veh]]) - 1)  # index of first shop
            if len(candidate[self.cars[first_veh]]) == 1:  # swapping shops
                sec_veh, sec_shop, first, second = self.swap_only_one_shop(candidate, first_veh, first_shop)
                candidate[self.cars[first_veh]][first_shop], candidate[self.cars[sec_veh]][sec_shop] = \
                    candidate[self.cars[sec_veh]][sec_shop], candidate[self.cars[first_veh]][first_shop]
            elif len(self.cars) == 1:  # swapping shops
                sec_veh, sec_shop, first, second = self.swap_only_one_car(candidate, first_veh, first_shop)
                candidate[self.cars[first_veh]][first_shop], candidate[self.cars[first_veh]][sec_shop] = \
                    candidate[self.cars[first_veh]][sec_shop], candidate[self.cars[first_veh]][first_shop]
            else:
                run = random.randint(0, 1)
                if run == 0:  # swapping shops
                    sec_veh, sec_shop, first, second = self.normal_swap(candidate, first_veh, first_shop)
                    candidate[self.cars[first_veh]][first_shop], candidate[self.cars[sec_veh]][sec_shop] = \
                        candidate[self.cars[sec_veh]][sec_shop], candidate[self.cars[first_veh]][first_shop]
                else:  # inserting shop
                    sec_veh, sec_shop, first, second = self.normal_insert(candidate, first_veh, first_shop)
                    candidate[self.cars[sec_veh]].insert(sec_shop, candidate[self.cars[first_veh]].pop(first_shop))
            tab = [{first_veh, sec_veh}, {first, second}]
            if j == 0:
                best_candidate = candidate
            if tab not in tabu_list:
                if self.goal_function(candidate) > self.goal_function(best_candidate):
                    best_candidate = candidate
            else:
                if self.goal_function(candidate) > self.goal_function(best):
                    best_candidate = candidate
        tabu_list.append(tab)
        return best_candidate, tabu_list

    def tabu_search_2(self):
        it, ex_it = 1, 1
        s0 = self.first_solution()
        s_best, best_candidate = s0, s0
        tabu_list = []
        values = []
        while True:
            best_candidate, new_tabu = self.best_neighbor(best_candidate, tabu_list, s_best)
            tabu_list = new_tabu
            values.append(self.goal_function(best_candidate))
            if self.goal_function(best_candidate) > self.goal_function(s_best):
                s_best = best_candidate
                ex_it = it
            if it >= self.max_it or self.goal_function(s_best) > self.goal:
                break
            it += 1
            if len(tabu_list) >= self.size:
                tabu_list.pop(0)
        s_best_off = {}
        for car in self.cars:
            s_best_off[car.nr] = [vehicle.nr for vehicle in s_best[car]]  # dict comprehension?
        return s_best, s_best_off, self.goal_function(s_best), ex_it, it, values
