import pandas as pd


from scheduler import TSModel 
from foundation_data import TSData
from constants.constants import ColumnVals as CV

def get_roster(ts_model:TSModel, ts_data:TSData) -> pd.DataFrame: 
    """
    Joining optimised roster with schedule
    """
    x_vars = ts_model.x_vars
    data = []
    for day_key in x_vars:
        for shift_key in x_vars[day_key]:
            for name in x_vars[day_key][shift_key]:
                x = x_vars[day_key][shift_key][name]
                if x.x > 0.5:
                    data.append(
                        [day_key, shift_key, name, x.x]
                    )

    roster_df = pd.DataFrame(
        data, columns = ['day_key', 'shift_key', 'name', 'assignment']
    )

    shifts = ts_data.shifts_df.copy(deep=True)

    roster_df = shifts.merge(
        roster_df,
        how = 'left',
        on = [
            CV.day_key, CV.shift_key
        ]
    )

    return roster_df.sort_values(
        by = [
            CV.day_key, CV.shift_key
        ], 
        ascending = [True, True]
    )
