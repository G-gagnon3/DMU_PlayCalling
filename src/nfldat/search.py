import pandas as pd
import random

play_types = ['pass_long', 'pass_short', 'extra_point', 'field_goal', 'run', 'punt']
fourth_down_actions = ['pass_long', 'pass_short', 'field_goal', 'run', 'punt']
other_down_actions = ['pass_long', 'pass_short', 'run']

def find_all_plays(data, yardline, yard_range, play_type):
    filt = data.loc[(data.play_type==play_type) & (data.yardline_100<yardline+yard_range) & (data.yardline_100>yardline-yard_range)]
    return filt

def filter_pass_len(data, pass_length):
    filt = data.loc[(data.pass_length==pass_length)]
    return filt

class playData:
    def __init__(self, data):
        self.data = data
        self.fourth_actions = fourth_down_actions
        self.other_actions = other_down_actions

        return
    
    def find_all_plays(self, yardline, yard_range, play_type):
        data = self.data
        filt = data.loc[(data.play_type==play_type) & (data.yardline_100<yardline+yard_range) & (data.yardline_100>yardline-yard_range)]
        return filt
    
    def filter_pass_len(self, data, pass_length):
        filt = data.loc[(data.pass_length==pass_length)]
        return filt
    
    def get_runs(self, yardline, yard_range):
        f_data = self.find_all_plays(yardline, yard_range, "run")
        return f_data
    
    def get_pass_long(self, yardline, yard_range):
        f_data = self.find_all_plays(yardline, yard_range, "pass")
        f_data = filter_pass_len(f_data, 'deep')
        return f_data
    
    def get_pass_short(self, yardline, yard_range):
        f_data = self.find_all_plays(yardline, yard_range, "pass")
        f_data = filter_pass_len(f_data, 'short')
        return f_data
    
    def get_punt_rows(self, yardline, yard_range):
        f_data = self.find_all_plays(yardline, yard_range, "punt")
        return f_data
    
    def get_field_goal(self, yardline, yard_range):
        f_data = self.find_all_plays(yardline, yard_range, "field_goal")
        return f_data
    
    
