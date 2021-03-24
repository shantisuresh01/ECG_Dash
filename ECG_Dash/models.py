from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List
import datetime as dt
from utils.decorators import Singleton
from constants import ECG_waveform_file
from geopandas.tests.test_pandas_methods import df

''' PEP 557: Dataclasses '''
@dataclass(frozen = True)
class Reading:
    time: float # ms since epoch
    values: List[int] = field(default_factory=list)
    
@Singleton
class ECGdata:
    def __init__(self, **kwargs):
        self.load(**kwargs)

    
            
    def load(self, file_path: str = ECG_waveform_file, nrows: int = None):
        target_file_path = Path(file_path)
        try:
            self.readings = pd.read_json(target_file_path, dtype={"values":"int"})
        except Exception as e:
            ''' for line-delimited JSON, "nrows" may be directly specified.  But the 'nrows' option is broken'''
            self.readings = pd.read_json(target_file_path, lines=True, dtype={"values":"int"}, nrows = nrows)
        ''' truncate the dataframe '''
        if nrows:
            self.readings = self.readings[:nrows]
        ''' Validating entire file takes too long '''
        self.readings = self.sanitize(self.readings)
        self.readings = self.add_wallclock_time(self.readings)
        return self.readings
         
#     def inject(self, reading: Reading):
#         ''' append the given reading '''
#         self.readings.loc[len(self.readings), 'time'] = reading.time
#         self.readings.loc[len(self.readings), 'values'] = reading.values
#         ''' add wallclock time '''
#         self.readings.loc[len(self.readings), 'wallclock'] = pd.to_datetime(reading.time)

    def inject(self, reading: Reading):
        #self.readings = self.readings.append({"time": time, "values":reading}, ignore_index=True)
        rows_list = self.readings.to_dict('records')
        wallclock = pd.to_datetime(reading.time, unit='ms')
        when = dt.datetime.fromtimestamp(reading.time).strftime('%D %T')
        dict1 = {"time": reading.time,
                 "values": reading.values,
                 "wallclock": wallclock,
                 "when": when,
                 }
        rows_list.append(dict1)
        self.readings = pd.DataFrame(rows_list)
    
    def sanitize(self, df):
        ''' validate the readings: check length of chunk and data type 
        return a sanitized dataframe
        '''
          
        try:
            df.loc[:,'values'] = df['values'].apply(self._validate_values)
        except Exception as e:
            print(e)
        return df
          
        ''' sort the data ascending by time '''
        ''' for another time '''
    def _validate_values(self, values):
        ''' check that there are 240 values in chunk '''
        ''' and if there is any element that is not a signed integer '''
        ''' return an array of invalid values '''
        if len(values) != 240 or any(not isinstance(x, int) for x in values):            
            return [np.nan] * 240
        else:
            return values 
         
    def add_wallclock_time(self, df):
        ''' convert to wallclock time '''
        df['wallclock'] = pd.to_datetime(df['time'], unit='ms')
        ''' convert to native Python datetime.datetime format so Plotly interprets it in the frontend '''
        df['wallclock'] = df['wallclock'].dt.to_pydatetime()
        df['when'] =  df['wallclock'].dt.strftime('%D %T')
        return df
    
    def get_window(self, offset_hours, interval_minutes, gaps = 'yes'):
        '''
            return the data from the given hour for the specified number of minutes
        '''
        if interval_minutes == 0:
            ''' no readings are requested; return empty dataframe '''
            return pd.DataFrame(columns = self.readings.columns)
        source_window = self.readings.copy()
        start_td = self.readings.iloc[0]['wallclock'] + pd.Timedelta(hours = offset_hours)
        source_window = source_window.loc[self.readings['wallclock'] >= start_td]

        ''' calculate the number of rows in the given 'interval_minutes'; 
        there is one chunk of 240 values for each second.  So #rows = #seconds '''
        nrows = round(interval_minutes * 60)
        if gaps.lower() == 'no':
            ''' we do not want invalid chunks '''
            ''' remove entries with invalid chunks '''
            source_window = source_window[~source_window['values'].astype(str).str.contains("nan")]
        source_window = source_window[:nrows]
        return source_window
    
    