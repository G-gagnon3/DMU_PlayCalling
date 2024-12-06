import pandas as pd


def read_remote(year):
    data = pd.read_csv(f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.csv.gz',
                   compression= 'gzip', low_memory= False)
    return data
    
def read_local(path):
    data = pd.read_csv(path)
    return data

def read_span(year_start, year_end):
    YEARS = range(year_start, year_end)
    data = pd.DataFrame()

    for i in YEARS:  
        i_data = pd.read_csv(f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{i}.csv.gz',
                    compression= 'gzip', low_memory= False)

        data = data.append(i_data, sort=True)
    data.reset_index(drop=True, inplace=True)
    return data