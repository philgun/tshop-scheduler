import foundation_data as fd
from parameters.parameters import params
from scheduler import TSModel
from get_roster import get_roster

files = {
    "employee_unavailability" : r"C:\Users\pgunawangan\OneDrive - Jetstar Airways Pty Ltd\Documents\git-project\tshop-scheduler\sample_data\employee_unavailability.csv",
    "employee_status" : r"C:\Users\pgunawangan\OneDrive - Jetstar Airways Pty Ltd\Documents\git-project\tshop-scheduler\sample_data\employee_status.csv"
}

ts_data = fd.TSData(files, params)
ts_model = TSModel(ts_data)

print(ts_model.x_vars)

