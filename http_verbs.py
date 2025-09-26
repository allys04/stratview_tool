# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 21:48:13 2025

@author: Alpha Sylla
"""

import json
import requests 

def get_request(api_url):
    
    """
    This short function allows data retrieve by sending requests to an API
    """

    response = requests.get(api_url)
    rtext = (response.text)
    rtext = json.loads(rtext)
    
    return rtext
