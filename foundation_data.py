import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta

from constants.constants import(
    ColumnVals as CV,
    FileNames as FN
)

from employee import Employee

#Helper funcs
#TODO: move to another py?
def _generate_shifts(params:dict) -> pd.DataFrame:
    start_date = datetime.strptime(
        params[CV.start_date], "%d-%m-%Y %H:%M"
    )
    end_date = datetime.strptime(
        params[CV.end_date], "%d-%m-%Y %H:%M"
    )

    shifts = params[CV.shift_time]

    
    # Generate all days
    days = (end_date - start_date).days
    data = []
    
    day_key = 0
    for i in range(days):
        current_day = start_date + timedelta(days=i)
        for start_time, end_time, shift_key in shifts:
            start_shift = datetime.combine(current_day.date(), datetime.strptime(start_time, "%H:%M").time())
            end_shift = datetime.combine(current_day.date(), datetime.strptime(end_time, "%H:%M").time())
            data.append([day_key, start_shift.strftime("%d-%m-%Y %H:%M"), end_shift.strftime("%d-%m-%Y %H:%M"), shift_key])
        day_key += 1

    return pd.DataFrame(
        data,
        columns = [
            CV.day_key, CV.start_shift, CV.end_shift, CV.shift_key
        ]
    )

def load_data(fn:str) -> pd.DataFrame:
    return pd.read_csv(fn)



class TSData:
    def __init__(self, files:Dict[str,str], params:dict):
        self.files = files
        self.unavail_df, self.status_df, self.shifts_df = self.process_data(self.files, params)
        self.employee_unavailability = self._get_unavail_dict()
        self.employee_dict = self._construct_employee_dict(self.status_df)

    def process_data(self, files:Dict[str,str], params:dict):
        unavail_df = load_data(
            files[FN.employee_unavailability]
        )

        status_df = load_data(
            files[FN.employee_status]
        )

        shifts_df = _generate_shifts(params)

        return unavail_df, status_df, shifts_df

    def _get_unavail_dict(self) -> dict:
        """
        Return unavailability dictionary :
        {
            day_key: {
                shift_key_1: {
                    [name_1, name_2]
                },
                shift_key_2: {
                    [name_1, name_2]
                }       
            },
            ...
        }
        """
        employee_unavailability = {
            day_key : {
                shift_key : [
                    employee_name
                    for employee_name in self.unavail_df[CV.employee_name].unique() 
                    if self._is_employee_blocked(employee_name, day_key, shift_key)
                ]
                for shift_key in list(self.shifts_df[CV.shift_key].unique())               
            }
            for day_key in list(
                self.shifts_df[CV.day_key].unique()
            )
        }
        return employee_unavailability

    def _is_employee_blocked(self, employee_name:str, day_key, shift_key):
        row = self.shifts_df[
            (self.shifts_df[CV.day_key] == day_key) & 
            (self.shifts_df[CV.shift_key] == shift_key)
        ][
            [CV.start_shift, CV.end_shift]
        ].iloc[0]
        
        start_shift = datetime.strptime(row[CV.start_shift], "%d-%m-%Y %H:%M")
        end_shift = datetime.strptime(row[CV.end_shift], "%d-%m-%Y %H:%M")

        #Blocked time for employee
        rows_block = self.unavail_df[
            self.unavail_df[CV.employee_name] == employee_name
        ][
            [CV.start_block, CV.end_block]
        ]


        overlap = any(
            start_shift < datetime.strptime(b[CV.end_block], "%d-%m-%Y %H:%M") and
            end_shift > datetime.strptime(b[CV.start_block], "%d-%m-%Y %H:%M")
            for _, b in rows_block.iterrows()
        )

        return overlap
    
    def _construct_employee_dict(self, employee_df) -> dict:
        return {
            row[CV.employee_name] : Employee(row)
            for _, row in employee_df.iterrows()
        }



