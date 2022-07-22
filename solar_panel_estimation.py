#============================ SOLAR PANEL ESTIMATION ============================#
#                                                                                #
#                  Simple estimation of the photovoltaic panels                  #
#                          needed for self-consumption.                          #
#                                                                                #
#================================================================================#


import requests
import json
import matplotlib.pyplot as mpl
import statistics as st
import math
from tabulate import tabulate


vers='v5_2'
tool_name='MRcalc'
data_base = 'PVGIS-SARAH2'
start_year = '2005'
end_year = '2020'
isang = '1'


city = input('Enter a City: ')


# Get Latitude and Longitude
url_ll = f'https://nominatim.openstreetmap.org/search/{city}?format=json'
r = requests.get(url_ll)

datos_r = r.json()

lat = datos_r[0]['lat']
lon = datos_r[0]['lon']

# For the whole year
angle = 3.7 + 0.69 * float(lat)


url = f"https://re.jrc.ec.europa.eu/api/{vers}/{tool_name}?lat={lat}&lon={lon}&raddatabase={data_base}&startyear={start_year}&endyear={end_year}&selectrad={isang}&angle={angle}&outputformat=json"


# Request

response = requests.get(url)
data = json.loads(response.text)


year_irrad = [[], [], [], [], [], [], [], [], [], [], [], [], []] # [kWh/m2/year/month]

mean_month_irrad = [] # [kWh/m2/month]
psh = [] # Peak Solar Hour [h/month]


for i in range(len(data['outputs']['monthly'])):

    month_num = data['outputs']['monthly'][i]['month']

    year_irrad[month_num - 1].append(data['outputs']['monthly'][i]['H(i)_m'])


for i in range(len(year_irrad)-1):

    mean_month_irrad.append(round(st.mean(year_irrad[i]),2))


psh = mean_month_irrad


performance = 0.6


# Mean monthly consumption [kWh/month]
monthly_consumption = [252.67, 156.67, 177.33, 221.33, 187.67, 197.89, 266.50, 387.00, 332.67, 216.33, 201.00, 189.33]


# Worst month could be the month with the highest ratio -> Consumption / Radiation
ratio = []

for i in range(len(monthly_consumption)):
    ratio.append(monthly_consumption[i]/psh[i])

l_index = ratio.index(max(ratio))

l = monthly_consumption[l_index] # Consumtion in the worst month [kWh/month]


module_power = 0.4 # [kW]


# Photovoltaic Power required
p_pho = l/(psh[l_index] * performance) # [kW]


number_of_modules = math.ceil(p_pho / module_power)



# Plot
mpl.bar(range(0, 12), mean_month_irrad, linewidth=2.0)
mpl.title('Average monthly irradiation')
mpl.xlabel('Month')
mpl.ylabel('kWh/m2')
mpl.show()

mpl.bar(range(0, 12), monthly_consumption, linewidth=2.0)
mpl.title('Average monthly consumption')
mpl.xlabel('Month')
mpl.ylabel('kWh')
mpl.show()



# Print
mean_month_irrad.insert(0, 'Average monthly irradiation [kWh/m2]')
monthly_consumption.insert(0, 'Average monthly consumption [kWh]')

data_2=[mean_month_irrad, monthly_consumption]

print(tabulate(data_2, headers = [' ', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],tablefmt="github"))

print(f'\nNumber of {module_power*1000} W modules required: {number_of_modules}')




