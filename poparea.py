import requests
from bs4 import BeautifulSoup
import pandas as pd
def get_area_pop_data():
    country_area_raw = requests.get("https://www.cia.gov/library/publications/the-world-factbook/fields/279rank.html") # get cia data on land area of countries
    country_area_html = BeautifulSoup(country_area_raw.text, 'html.parser')
    area_table = country_area_html.find_all('tr')
    area_data = [] # array to store data
    for i, data_values in enumerate(area_table[1:]):
      try:
        useful_data = data_values.text.split('\n')[1:5:2] + [float( "".join(data_values.text.split('\n')[5].split(','))) * 0.386102] # skip weird newline characters in the table. First array is country name and area ranking, next is land area which is converted to a float. Numerical constant converts SQKM to SQMI
        area_data.append(useful_data) # store it in data array
      except: # in case some countries do not have an ISO code : just ignore them they're usually pretty small anyway
        True

    country_pop_raw = requests.get("https://www.cia.gov/library/publications/the-world-factbook/fields/335rank.html")
    country_pop_html = BeautifulSoup(country_pop_raw.text, 'html.parser')
    pop_table = country_pop_html.find_all('tr')
    pop_data = []
    for i, data_values in enumerate(pop_table[1:]):
      try:
        data_values.text.split('\n')[3] # make sure this list is congruent with the above
        pop_data.append( [data_values.text.split('\n')[3]] + [float( "".join(data_values.text.split('\n')[5].split(',')) ) ] ) # add on the country name and population
      except: # in case some countries do not have an ISO code : just ignore them they're usually pretty small anyway
        True
    area_data.sort(key=lambda x:x[1]) # sort first list by the second element: country name
    pop_data.sort() # sort second list by country name as well
    offset = 0
    for i in range(len(area_data)):
      if area_data[i][1] == pop_data[i + offset][0]: # if both lists line up with the country name
        area_data[i].append(pop_data[i + offset][1]) # add on the population data and calculate the population density data and add it
        area_data[i].append( float(pop_data[i + offset][1]) / area_data[i][2])
      else:
        area_data[i].append(-1) # otherwise make the data point -1 for no data
        area_data[i].append(-1)
        offset -= 1 # this makes sure both lists are alligned in terms of country name
    #  print(area_data[i][2], " : ", area_data[i][1], " : ", area_data[i][3], " : ", area_data[i][4])
    return area_data
