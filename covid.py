import csv
import plotly.express as px
import pandas as pd
import poparea
# general overview of how the program works: Read in number of covid cases and covid deaths from CSV files downloaded onto local machine.
# then also read in ISO 3 country codes from a seperate CSV file. Also use requests to access CIA world factbook and get country population and land area data
# Then, add all the data into one big array and calculate various factors to display (ex. covid cases per capita). Then create plotly figures and show them
country_names = [] # array used to store all the country names present in the csv file
cases_for_country = [] # array used to store the cases for every country on every day. The first dimension of the array is country, second is date.
cases_on_date = [] # reverse of the above. Stores the cases for every country on a singular day: EG cases_on_date[0][0] is the cases for afganistan on day 0
row_count = 0 # used below
area = [] # stores the area of each country
pop = [] # stores the population of each country
with open('time_series_confirmed_crunch.csv', newline='') as csvfile: # read the covid daily cases csv file and input the data into the arrays
    covid_data = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in covid_data:
        country_names.append(row[1])
        cases_for_country.append([])
        for i in range(len(row[4:])):
            cases_for_country[row_count].append(row[i+4])
        row_count += 1
        area.append(0.0)
        pop.append(0.0)

dates = ['Country'] + cases_for_country[0] # array that stores all the dates that there is data recorded for

for i in range(len(cases_for_country[0])):
    cases_on_date.append([])
    for j in range(len(cases_for_country)):
        cases_on_date[i].append(cases_for_country[j][i]) # input data for cases_on_date

deaths_for_country = [] # covid deaths for every country
deaths_on_date = [] # covid deaths for every country on a certain date
row_count = 0
with open('time_series_covid_19_deaths.csv', newline='') as csvfile: # same as above, except records the covid deaths instead of cases
    covid_data = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in covid_data:
        deaths_for_country.append([])
        for i in range(len(row[4:])):
            deaths_for_country[row_count].append(row[i+4])
        row_count += 1
        
for i in range(len(deaths_for_country[0])):
    deaths_on_date.append([])
    for j in range(len(deaths_for_country)):
        deaths_on_date[i].append(deaths_for_country[j][i]) # add data into deaths_on_date array

name_to_iso_3 = {} # dictionary that has a country's name as its key and its ISO 3 code as its value. Read in this info from a seperate csv file
with open('iso_convert.csv', newline='', errors='ignore') as csvfile:
    covid_data = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in covid_data:
        name_to_iso_3[row[0]] = row[2]

iso_codes = [] # these next lines of code convert all the country names into their ISO codes, if it is in the dictionary
for i in range(1, len(country_names)):
    try:
        iso_codes.append(name_to_iso_3[country_names[i]])
    except:
        iso_codes.append(country_names[i])

area_data = poparea.get_area_pop_data() # runs a function in a different python file. Requests population and area data from the CIA world factbase and returns it as an array

area_data[244][1] = 'US' # fix error involving US name
offset = 0
for i in area_data:
    if i[1] in country_names:
        area[country_names.index(i[1]) - 1]= float(i[2]) # input CIA world factbase data into area and population arrays
        pop[country_names.index(i[1]) - 1] = float(i[3])

country_date_cases = [] # countains all the data from above in one convenient array. Lines below add in the data
for i in range(len(country_names) - 1):
    for j in range(len(dates)- 1):
                  country_date_cases.append( [iso_codes[i]]
                                             + [country_names[i+1]]
                                             + [dates[j + 1]]
                                             + [int(cases_on_date[j][i + 1])]
                                             + [(area[i])]
                                             + [(pop[i])]
                                             + [int(cases_on_date[j][i + 1]) / (pop[i] + 1)]
                                             + [int(cases_on_date[j][i + 1]) / (area[i] + 1)]
                                             + [int(deaths_on_date[j][i + 1])]
                                             + [int(deaths_on_date[j][i + 1]) / (pop[i] + 1)]
                                             + [int(deaths_on_date[j][i + 1]) / (area[i] + 1)]
                                             + [int(cases_on_date[j][i + 1]) / (int(deaths_on_date[j][i + 1]) + 1)])



df = pd.DataFrame(country_date_cases, columns=['ISO', 'Country', 'Date', 'Cases', # create dataframe containing all the data
                                               'Area(SQMI)','Population', 'Cases per Capita', 'Cases per Area(SQMI)',
                                               'Deaths', 'Deaths per Capita', 'Deaths per Area(SQMI)',
                                               'Cases per Death'])

cases_time = px.choropleth(df, locations="ISO", color='Cases', animation_frame='Date', hover_name="Country",
                          color_continuous_scale=px.colors.sequential.Magma[::-1], range_color=(0,500000) ) # graphs covid cases over time
# This visualization is the most basic, as it just uses a choropleth map to display the raw numbers of covid cases over time.
# This visualization definitely conveys the dire situation the United States is in right now, as their covid case numbers are just incredibly high
# In addition, it shows that in a lot of Africa, covid is rather under control. China is also doing incredibly well at stopping the spread

cases_per_capita = px.choropleth(df, locations="ISO", color="Cases per Capita",
                                 animation_frame='Date', range_color=(0, .004)) # graphs covid cases per capita over time
# This visualization is like the above one, except that it divides the total covid case by the population of the country that they are in.
# This visualization is interesting for a few reasons. First, it makes the US look not as bad because even though we have lots of cases, we also have lots of people.
# It also shows how both Canada and South America is doing just as bad as the US in that respect. Africa and china again are doing quite well

cases_per_area = px.choropleth(df, locations="ISO", color="Cases per Area(SQMI)",
                               animation_frame='Date', range_color=(0, .04)) # graphs covid cases per SQMI over time
# This visualization divides the number of covid cases by the land area of the country in square miles.
# This is interesting for a few reasons. It shows Europe in quite a bad light in this visualization, but that is because the countries are constrained to such a small area
# It also shows Canada and China are doing quite well in this respect because of their large areas

deaths_per_capita = px.choropleth(df, locations="ISO", color="Deaths per Capita",
                                  animation_frame='Date', range_color=(0, .00005)) # graphs covid deaths per capita over time
# This visualization is like the cases per capita one except it is graphing number of deaths instead of cases.
# There is a few important points to take away here. The United States was doing incredibly poorly even quite early into covid with a high death rate
# In addition, it is scary to look at over time, and especially as you go close to the end of the data set, the death rates are increasing all over the globe
# One would imagine death rates would be going down, but this is not the case.

deaths_per_area = px.choropleth(df, locations="ISO", color="Deaths per Area(SQMI)",
                                animation_frame='Date', range_color=(0, .005)) # graphs covid deaths per SQMI over time
# This visualization displays covid deaths per land area over time.
# This visualization is like the covid cases per land area one, as it portrays Europe in quite a bad light, but this is only because Europe has such small land area

cases_per_death = px.choropleth(df, locations="ISO", color="Cases per Death",
                                animation_frame='Date', range_color=(0, 100)) # graphs covid cases per covid death over time
# This visualization divides the total covid cases by the total covid deaths, and should serve as an indicator of how many people in a country are able to recover from covid
# This is perhaps the most scary visualization. It shows the wealth and healthcare inequality in the world, as countries in Africa, despite having very few cases, have incredibly high death rates
# It also shows how Europe is doing perhaps the best job at making sure their citizens do not die if they have COVID. Perhaps a correlation with universal healthcare?

user_input = ""
while user_input != 'q':
    print("Which graph would you like to see? Cases/Time, Cases/Capita, Cases/Area, Deaths/Capita, Deaths/Area, Cases/Death")
    user_input = input("\n")
    if user_input == 'Cases/Time':
        cases_time.show()
    if user_input == 'Cases/Capita':
        cases_per_capita.show()
    if user_input == 'Cases/Area':
        cases_per_area.show()
    if user_input == 'Deaths/Capita':
        deaths_per_capita.show()
    if user_input == 'Deaths/Area':
        deaths_per_area.show()
    if user_input == 'Cases/Death':
        cases_per_death.show()
    
#cases_time.show()
#cases_scatter.show()
#cases_per_capita.show()
#cases_per_area.show()
#deaths_per_capita.show()
#deaths_per_area.show()
#cases_per_death.show()

