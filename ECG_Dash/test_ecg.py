import unittest
from models import ECGdata, Reading
import numpy as np
import pandas as pd
import time as tm
from services import sanitize
from django.test import Client
from django.urls.base import reverse
from constants import ECG_waveform_file
import json

unittest.TestLoader.sortTestMethodsUsing = None

class TestECGdata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ getting ECG object once as as to avoid calling it for each test
            and storing the result as class variable
        """
        cls.file_path = r'/Users/shanti/workspace/null_data2.json'
        cls.ecg_data = ECGdata(file_path=cls.file_path, nrows = 5000)
  
    def test_sanitizing_ecg_data_nullifies_readings_with_less_than_240_numbers(self):
        now = tm.time()
        reading = Reading(time = now, values = [1,2,3])
        self.ecg_data.inject(reading = reading)
        data = sanitize(self.ecg_data)
        last_values = data.iloc[-1]["values"]
        self.assertTrue(np.nan in last_values, "Oops! null not returned for invalid chunk")
    def test_sanitizing_ecg_data_nullifies_readings_with_240_alphabets(self):
        now = tm.time()
        reading = Reading(time = now, values = ['A'] * 240)
        self.ecg_data.inject(reading = reading)
        data = sanitize(self.ecg_data)
        last_values = data.iloc[-1]["values"]
        self.assertTrue(np.nan in last_values, "Oops! null not returned for invalid chunk")
    def test_2_second_interval_returns_chunks(self):
        hour_offset = 0
        ''' one second = 1/60 minute '''
        two_seconds = 2 / 60
        window = self.ecg_data.get_window(offset_hours = hour_offset, interval_minutes = two_seconds)
        self.assertTrue(window.shape[0] != 0, "Oops! 2 second interval returned")

    def test_2_second_interval_returns_2_chunks(self):
        hour_offset = 0
        ''' one second = 1/60 minute '''
        two_seconds_converted_in_minutes = 2 / 60
        window = self.ecg_data.get_window(offset_hours = hour_offset, interval_minutes = two_seconds_converted_in_minutes)
        self.assertTrue(window.shape[0] == 2, "Oops! 2 second interval not returned")
    def test_30_second_interval_with_gaps_returns_30_chunks_and_contains_gaps(self):
        hour_offset = 0
        ''' one second = 1/60 minute '''
        thirty_seconds_converted_to_minutes =  30 / 60
        window = self.ecg_data.get_window(offset_hours = hour_offset, interval_minutes = thirty_seconds_converted_to_minutes, gaps = 'yes')
        ''' check if window has chunks that have nan '''
        ''' the data contains invalid chunks in the first thirty seconds '''
        invalid_readings = window[window['values'].astype(str).str.contains("nan")]
        self.assertTrue((window.shape[0] == 30) & (invalid_readings.shape[0] != 0), "Oops! 2 second interval with gaps does not contain gaps")
    def test_30_second_interval_without_gaps_returns_30_chunks_and_does_not_contain_gaps(self):
        hour_offset = 0
        ''' one second = 1/60 minute '''
        thirty_seconds_converted_to_minutes =  30 / 60
        window = self.ecg_data.get_window(offset_hours = hour_offset, interval_minutes = thirty_seconds_converted_to_minutes, gaps = 'no')
        ''' check if window has chunks that have nan '''
        ''' the data contains invalid chunks in the first thirty seconds '''
        invalid_readings = window[window['values'].astype(str).str.contains("nan")]
        self.assertTrue((window.shape[0] == 30) & (invalid_readings.shape[0] == 0), "Oops! 2 second interval without gaps contains gaps")    
    def test_rest_api_returns_200_status_code(self):
        client = Client()
        response = client.get(reverse('rest', kwargs = {'offset_hours': 1, "interval_minutes": 1, "gaps":'yes'}))
        self.assertTrue(response.status_code == 200, "Oops! status_code is not 200 OK")
    def test_rest_api_returns_response(self):
        client = Client()
        response = client.get(reverse('rest', kwargs = {'offset_hours': 1, "interval_minutes": 1, "gaps":'yes'}))
        self.assertTrue('columns' in json.loads(response.content), "Oops! response does not contain columns")

