import pandas as pd
import sys

sys.path.append("../")

class FileNames:
    #Unavailability
    employee_unavailability = "employee_unavailability"
    employee_status = "employee_status"

class ColumnVals:
    #Unavailability
    employee_name = "employee_name"
    start_block = "start_block"
    end_block = "end_block"

    #Status
    employee_status = "employee_status"
    gender = "gender"

    #Params
    start_date = "START_DATE"
    end_date = "END_DATE"
    shift_time = "SHIFT_TIME"

    #Shifts
    day_key = "day_key"
    start_shift = "start_shift"
    end_shift = "end_shift"
    shift_key = "shift_key"