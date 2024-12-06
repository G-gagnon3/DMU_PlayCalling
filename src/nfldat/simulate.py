import pandas as pd
import random
from . import search
import math

def series_rewards(yardline, event):
    rewards = {"first_down": 10,
               "Turnover": -1,
               "Play": -0.5}
    if event == "Turnover":
        return rewards["Turnover"] - get_epa(1, 100 - yardline)
    
    else:
        return rewards[event]

def drive_rewards(yardline, event):
    rewards = {"Touchdown": 7,
               "Field_Goal": 3,
               "Turnover": 0}
    if event == "Turnover":
        return rewards["Turnover"] - get_epa(1, 100 - yardline)
    
    else:
        return rewards[event]
    
def get_epa(down, yardline):
        slope = -((6.2+0.5)/100)
        offset = [0, 6.2, 5.9, 5.1, 3.5]
        epa = offset[down] + yardline*slope
        return epa

class sim:
    def __init__(self, data, tmodel):
        self.data:search.playData = search.playData(data)
        self.tmodel:search.transitionModelStandard = tmodel(self.data)

    
    
    def choose_4th(self, yardline, distance, yard_range, nsims, do_print=False):
        plays_on_4th = search.fourth_down_actions
        n_att_per = math.ceil(nsims/len(plays_on_4th))

        rewards = [0 for i in range(len(plays_on_4th))]
        for i, play in enumerate(plays_on_4th):
            for j in range(n_att_per):
                reward, sequence = self.simulate_drive(play, 4, distance, yardline, yard_range, "naive")
                rewards[i] += reward
                if do_print:
                    print("Play sim", j, end=" ")
                    print("Reward", reward, end=' ')
                    print("Sequence:", sequence)
        
        best_play = plays_on_4th[rewards.index(max(rewards))]
        return best_play
    
    def choose_other(self, yardline, down, distance, yard_range, nsims, do_print=False):
        plays_on_other = search.other_down_actions
        n_att_per = math.ceil(nsims/len(plays_on_other))

        rewards = [0 for i in range(len(plays_on_other))]
        for i, play in enumerate(plays_on_other):
            #print("Simulating", play)
            for j in range(n_att_per):
                reward, sequence = self.simulate_series(play, down, distance, yardline, yard_range)
                if do_print:
                    print("Play sim", j, end=" ")
                    print("Reward", reward, end=' ')
                    print("Sequence:", sequence)
                rewards[i] += reward
        
        best_play = plays_on_other[rewards.index(max(rewards))]
        return best_play
    
    def simulate_drive(self, cur_action, down, distance, yardline, yard_range=3, drive_type="naive", n_4th_sims = 20, n_other_sims = 10, do_print=False):
        ###
        # THIS SIMULATES A SERIES --> NOT A FULL DRIVE
        ###
        #### Recursive, goes until terminal state
        init_yardline = yardline
        init_down = down
        first_down_yardline = yardline - distance
        # Simulate play
        is_terminal, turnover, reward, yardline = self.simulate_action(cur_action, yardline, yard_range, down, distance)
        # Check if terminal
        ## If terminal, return reward
        if is_terminal:
            if turnover:
                return reward, [(init_yardline, down, cur_action), (yardline, init_down, f"Turnover, Reward {reward}", yardline)]
            else:
                return reward, [(init_yardline, down, cur_action), (yardline, init_down, f"Score, Reward {reward}", yardline)]
        # Handle first down
        if first_down_yardline >= yardline:
            # First down
            distance = 10
            down = 1
            first_down_yardline = yardline-distance
        else:
            down += 1
            distance = yardline - first_down_yardline
        # Handle touchdown
        if yardline <= 0:
            reward += drive_rewards(yardline, "Touchdown")
            return reward, [(init_yardline, init_down, cur_action, yardline), (yardline, down, "Touchdown", yardline)]
        # Pick next action
        if down > 4:
            return drive_rewards(yardline, "Turnover"), [(init_yardline, init_down, cur_action, yardline), (yardline, down, "Turnover on Downs", yardline)]
        if down == 4:
            # Pick 4th down not random 
            next_action = self.choose_4th(yardline, distance, yard_range, nsims=n_4th_sims)
        else:
            # Pick 1-3 randomly
            if drive_type=="naive":
                next_action = random.choice(search.other_down_actions)
            else:
                next_action = self.choose_other(yardline, down, distance, yard_range, nsims=n_other_sims, do_print=do_print)

        # Return simulate_drive
        final_reward, action_sequence = self.simulate_drive(next_action, down, distance, yardline, yard_range, drive_type, n_4th_sims, n_other_sims)
        if down == 1:
            action_sequence = [(init_yardline, init_down, cur_action, yardline), (yardline, down, "First_down", yardline)] + action_sequence
        else:
            action_sequence = [(init_yardline, init_down, cur_action, yardline)] + action_sequence

        return final_reward, action_sequence

    def simulate_series(self, cur_action, down, distance, yardline, yard_range=3):
        ###
        # THIS SIMULATES A SERIES --> NOT A FULL DRIVE
        ###
        init_down = down
        init_yardline = yardline
        first_down_yardline = yardline - distance
        # Simulate play
        is_terminal, turnover, reward, yardline = self.simulate_action(cur_action, yardline, yard_range, down, distance)
        reward += series_rewards(yardline, "Play")
        # Check if terminal
        ## If terminal, return reward
        if is_terminal:
            if not turnover:
                #print("\nScored!")
                # Good guys scored
                return 10, [(yardline, cur_action)]
            else:
                # Bad guys got ball
                return series_rewards(yardline, "Turnover"), [(init_yardline, init_down, cur_action), (yardline, down, "Turnover", yardline)]

        # Handle first down
        if first_down_yardline >= yardline:
            # First down
            #print("\nGot First down!")
            distance = 10
            down = 1
            first_down_yardline = yardline-distance
            is_terminal = True
            return series_rewards(yardline, "first_down"), [(init_yardline, init_down, cur_action, yardline), (yardline, down, "First_down", yardline)]
        else:
            down += 1
            distance = yardline - first_down_yardline
        # Pick next action
        if down > 4:
            return series_rewards(yardline, "Turnover"), [(init_yardline, init_down, cur_action, yardline), (yardline, 4, "Turnover on Downs", yardline)]
        if down == 4:
            # Pick 4th down not random 
            next_action = self.choose_4th(yardline, distance, yard_range, nsims=20)
            
        else:
            # Pick 1-3 randomly
            next_action = random.choice(search.other_down_actions)
        # Return simulate_drive
        final_reward, action_sequence = self.simulate_series(next_action, down, distance, yardline, yard_range)
        action_sequence = [(init_yardline, init_down, cur_action, yardline)] + action_sequence
        return reward + final_reward, action_sequence

    def simulate_action(self, action, yardline, yard_range, down, distance):
        if action == "punt":
            return self.sim_punt(yardline, yard_range)
        elif action == "field_goal":
            return self.sim_kick(yardline, yard_range)
        elif action == "run":
            return self.sim_run(yardline, yard_range)
        elif action == "pass_long":
            return self.sim_pass_long(yardline, yard_range)
        elif action == "pass_short":
            return self.sim_pass_short(yardline, yard_range)
        # Sample a single instance

        return True, True, 0, yardline

    def sim_punt(self, yardline, yard_range):
        yardline_us, punt_distance = self.tmodel.get_punt(yardline, yard_range)
        rew = drive_rewards(yardline_us, "Turnover")
        return True, True, rew, yardline_us
    
    def sim_kick(self, yardline, yard_range):
        yardline_us, is_good = self.tmodel.get_fg(yardline, yard_range)
        if is_good:
            rew = drive_rewards(yardline_us, "Field_Goal")
        else:
            rew = drive_rewards(yardline_us, "Turnover")
        return True, not is_good, rew, yardline_us
    
    def sim_run(self, yardline, yard_range):
        yards_gained, turnover = self.tmodel.get_run(yardline, yard_range)
        yardline_us = yardline-yards_gained
        if turnover:
            rew = drive_rewards(yardline_us, "Turnover")
        else:
            rew = 0
        return turnover, turnover, rew, yardline_us
    
    def sim_pass_long(self, yardline, yard_range):
        yards_gained, turnover = self.tmodel.get_pass_long(yardline, yard_range)
        yardline_us = yardline-yards_gained
        if turnover:
            rew = drive_rewards(yardline_us, "Turnover")
        else:
            rew = 0
        return turnover, turnover, rew, yardline_us
    
    def sim_pass_short(self, yardline, yard_range):
        yards_gained, turnover = self.tmodel.get_pass_short(yardline, yard_range)
        yardline_us = yardline-yards_gained
        if turnover:
            rew = drive_rewards(yardline_us, "Turnover")
        else:
            rew = 0
        return turnover, turnover, rew, yardline_us



