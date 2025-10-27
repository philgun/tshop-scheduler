import sys
from mip import Model, MAXIMIZE, CBC, BINARY, LinExpr, quicksum
from typing import List, Dict

from foundation_data import TSData
from constants.constants import ColumnVals as CV
from employee import Employee

def is_employee_available(unavail_dict:dict, e_obj:Employee, day_key: int, shift_key:int) -> bool:
    return e_obj.employee_name not in unavail_dict.get(day_key,{}).get(shift_key,[])


class TSModel:
    def __init__(self, ts_data:TSData):
        self.model = Model(
            sense = MAXIMIZE, 
            solver_name = CBC
        )

        self.x_vars = self._add_x_vars(ts_data)

        #Add constraints max 3 min 2
        self.shift_constraints = self._add_shift_constraints(ts_data)

        #Add constraints max 1 person 1 shift per day
        self.per_person_constraint = self._add_per_person_constraints(ts_data)

        #Adding objectives
        self._add_objectives(ts_data)

        #Optimise
        status = self.optimise()

        return status


    def _add_x_vars(self, ts_data:TSData) -> dict:
        x_vars = {
            day_key:{
                shift_key : {
                    e_obj.employee_name : self.model.add_var(
                        var_type = BINARY,
                        name = f"x_{e_obj.employee_name}_daykey_{day_key}_{shift_key}"
                    )
                    for _, e_obj in ts_data.employee_dict.items()
                    
                    if is_employee_available(
                        ts_data.employee_unavailability, 
                        e_obj, 
                        day_key, 
                        shift_key
                    )
                }
                for shift_key in ts_data.shifts_df[
                    ts_data.shifts_df[CV.day_key] == day_key
                ][CV.shift_key].unique()
            }
            for day_key in ts_data.shifts_df[CV.day_key].unique()
        }
        return x_vars
        
    def _add_shift_constraints(self, ts_data:TSData) -> dict:
        #At least 2 employee per shift
        shift_constraint = {
            day_key : {
                shift_key : {
                    "max": self.model.add_constr(
                        quicksum(
                            self.x_vars[day_key][shift_key][employee_name]
                            for employee_name in self.x_vars[day_key][shift_key]
                        ) <= 3,
                        name=f"shift_c_max_day_{day_key}_shift_{shift_key}"
                    ),

                    "min": self.model.add_constr(
                        quicksum(
                            self.x_vars[day_key][shift_key][employee_name]
                            for employee_name in self.x_vars[day_key][shift_key]
                        ) >= 2,
                        name=f"shift_c_min_day_{day_key}_shift_{shift_key}"
                    )
                }
                for shift_key in ts_data.shifts_df[
                    ts_data.shifts_df[CV.day_key] == day_key
                ][CV.shift_key].unique()
            }
            for day_key in ts_data.shifts_df[CV.day_key].unique()
        }
        return shift_constraint

    def _add_per_person_constraints(self, ts_data:TSData) -> dict:
        #1 person 1 shift per day
        return {
                day_key: self.model.add_constr(
                    quicksum(
                        self.x_vars[day_key][shift_key][employee_name]
                        for shift_key in self.x_vars[day_key]
                        if employee_name in self.x_vars[day_key][shift_key]
                    ) <= 1,
                    name=f"max_one_shift_{employee_name}_day_{day_key}"
                )
                for day_key in ts_data.shifts_df[CV.day_key].unique()
                for employee_name in [
                    e_obj.employee_name for _, e_obj in ts_data.employee_dict.items()
                ]
                if any(
                    employee_name in self.x_vars[day_key][shift_key]
                    for shift_key in self.x_vars[day_key]
                )
            }


    def _add_manpower_cost(self, ts_data:TSData) -> dict:
        #FIXME: TODO move this to params
        cost_per_head = 100

        manpower_cost_expr = {
            day_key: {
                shift_key: quicksum(
                    self.x_vars[day_key][shift_key][employee_name]
                    for employee_name in self.x_vars[day_key][shift_key]
                ) * cost_per_head
                for shift_key in self.x_vars[day_key]
                if self.x_vars[day_key][shift_key]  # skip empty shifts
            }
            for day_key in self.x_vars
        }


        return quicksum(
                expr
                for shift_dict in manpower_cost_expr.values()
                for expr in shift_dict.values()
            )

    def _add_revenue(self, ts_data:TSData) -> dict:
        #FIXME: TODO move this to params
        revenue_per_shift = 3000

        revenue_expr = {
            day_key: {
                shift_key: quicksum(
                    self.x_vars[day_key][shift_key][employee_name]
                    for employee_name in self.x_vars[day_key][shift_key]
                ) * revenue_per_shift
                for shift_key in ts_data.shifts_df[
                    ts_data.shifts_df[CV.day_key] == day_key
                ][CV.shift_key].unique()
            }
            for day_key in ts_data.shifts_df[CV.day_key].unique()
        }

        return quicksum(
                expr
                for shift_dict in revenue_expr.values()
                for expr in shift_dict.values()
            )
        
    def _add_objectives(self, ts_data:TSData):
        self.revenue = self._add_revenue(ts_data)
        self.manpower_cost = self._add_manpower_cost(ts_data)
        self.model.objective = self.revenue - self.manpower_cost

    def optimise(self):
        self.model.optimize(max_seconds = 300)