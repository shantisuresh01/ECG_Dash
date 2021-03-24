'''
    Author: Shanti Suresh
    Date: 02/25/2021
    Description: Interfaces for the main business needs
    Using loose coupling with lower "models" layer
'''
import numpy as np
import pandas as pd
import datetime as dt
from django.http import JsonResponse
import json
from models import ECGdata


def sanitize(waveform: ECGdata) -> pd.DataFrame :
    ''' validate the readings:
    call ECG sanitize() as presently we only have ECG data
    If we have more than one waveform types, call the 
    respective sanitize() method.
    Return the dataframe of the readings.
    '''
    
    
    waveform.readings = waveform.sanitize(waveform.readings)
    return waveform.readings
    
def _validate_values(values:list[int]):
        ''' check that there are 240 values in chunk '''
        ''' and if there is any element that is not a signed integer '''
        ''' return an array of invalid values '''
        if len(values) != 240 or any(not isinstance(x, int) for x in values):            
            return [np.nan] * 240
        else:
            return values    
        
def get_window(request, offset_hours, interval_minutes, gaps = 'yes'):
    ecg_data = ECGdata()
#     offset_hours = request.GET.get('offset_hours')
#     interval_minutes = request.GET.get('interval_minutes')
#     gaps = request.GET.get('gaps')
    
    '''
        return the data from the given hour for the specified number of minutes
    '''
    df = ecg_data.get_window(offset_hours, interval_minutes, gaps = gaps)
    if df.empty:
        ''' dataframe is empty, return no content in JsonResponse '''
        table = df.to_json(orient='split', index=False)
    else:
        table = df.explode('values').reset_index().to_json(orient='split', index=False)
   # table = df.to_json(orient='split', index=False)
    response = JsonResponse(json.loads(table), safe = False)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response
