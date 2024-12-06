from .search import *

class transitionModelStandard:
    def __init__(self, data):
        self.data:playData = data

    def get_punt(self, yardline, yard_range=3):
        rows = self.data.get_punt_rows(yardline, yard_range)
        n_found = rows.shape[0]
        if n_found == 0:
            punt_distance = 0
            return yardline, punt_distance
        random_row = rows.sample(n=1)
        punt_distance = random_row['kick_distance'][random_row['kick_distance'].keys()[0]]
        return yardline-punt_distance, punt_distance
    
    def get_fg(self, yardline, yard_range=3):
        rows = self.data.get_field_goal(yardline, yard_range)
        n_found = rows.shape[0]
        if n_found == 0:
            # Assume missed
            return yardline, False
        random_row = rows.sample(n=1)
        field_goal_good = random_row['field_goal_result'][random_row['field_goal_result'].keys()[0]] == "made"
        return yardline, field_goal_good

    def get_run(self, yardline, yard_range=3):
        # Returns yards gained, turnover 
        rows = self.data.get_runs(yardline, yard_range)
        n_found = rows.shape[0]
        if n_found == 0:
            # Assume turnover
            return 0, True
        random_row = rows.sample(n=1)
        row_index = random_row['yards_gained'].keys()[0]
        yards_gained = random_row['yards_gained'][row_index]
        fumble = random_row['fumble_lost'][row_index] == 1
        interception = random_row['interception'][row_index] == 1
        is_turnover = fumble or interception

        return yards_gained, is_turnover

    def get_pass_short(self, yardline, yard_range=3):
        # Returns yards gained, turnover 
        rows = self.data.get_pass_short(yardline, yard_range)
        n_found = rows.shape[0]
        if n_found == 0:
            # Assume incomplete
            return 0, False
        random_row = rows.sample(n=1)
        row_index = random_row['yards_gained'].keys()[0]
        yards_gained = random_row['yards_gained'][row_index]
        fumble = random_row['fumble_lost'][row_index] == 1
        interception = random_row['interception'][row_index] == 1
        is_turnover = fumble or interception

        return yards_gained, is_turnover

    def get_pass_long(self, yardline, yard_range=3):
        # Returns yards gained, turnover 
        rows = self.data.get_pass_long(yardline, yard_range)
        n_found = rows.shape[0]
        if n_found == 0:
            # Assume incomplete
            return 0, False
        random_row = rows.sample(n=1)
        row_index = random_row['yards_gained'].keys()[0]
        yards_gained = random_row['yards_gained'][row_index]
        fumble = random_row['fumble_lost'][row_index] == 1
        interception = random_row['interception'][row_index] == 1
        is_turnover = fumble or interception

        return yards_gained, is_turnover
    
class transitionModelExceptionalKicker(transitionModelStandard):
    def __init__(self, data):
        super().__init__(data)
    
    def get_fg(self, yardline, yard_range=3):
        if yardline <= 55:
            return yardline, True
        return yardline, False
    
class transitionModelExceptionalPunter(transitionModelStandard):
    def __init__(self, data):
        super().__init__(data)
    
    def get_punt(self, yardline, yard_range=3):
        if yardline <= 60:
            return 0, yardline
        return yardline-60, 60
    
class transitionModelExceptional4th(transitionModelStandard):
    def __init__(self, data):
        super().__init__(data)
    
    def get_punt(self, yardline, yard_range=3):
        if yardline <= 60:
            return 0, yardline
        return yardline-60, 60

