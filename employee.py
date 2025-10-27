import pandas as pd
import sys

sys.path.append("../")

from constants.constants import ColumnVals as CV 

class Employee:
    def __init__(self, row:pd.Series):
        self.employee_name = row[CV.employee_name]
        self.employee_status = row[CV.employee_status]
        self.gender = row[CV.gender]