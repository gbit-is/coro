#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import json


# Establish Vars
url = "https://www.worldometers.info/coronavirus/"
#url = "https://gbit.is/coro/static/"

home = "/var/www/gbit/coro/"  # location of home folder for html,json and population txt
report = home + "report.json"
popdoc = home + "population.txt"





# Get raw info from site

page = requests.get(url) # Get the sites content
soup = BeautifulSoup(page.content, 'html.parser') # Load it to BS4
#table = soup.find('table', id="main_table_countries") # Get the table itself
table = soup.find('table', id="main_table_countries_today") # Get the table itself
	





# Create the population dict

cs = { } # Dict to hold countries

f = open(popdoc,"r")
f = f.read()

for line in f.split("\n"):
        data = line.split("|")


        if len(data) == 2 : # dirty method but it works to get rid of empty lines, which were a problem
                country = data[0].strip()
                population = int(data[1].strip())
                cs[country] = population





# Parse the html table data 
headers = [header.text for header in table.find_all('th')]
results = [{headers[i]: cell for i, cell in enumerate(row.find_all('td'))}
	for row in table.find_all('tr')]


coll = [ ] # collects the parsed data to list



# Now for the good stuff ....

for x in results: # For each line in the html table

	if x == {}: # had some issues with empty entries, dirty fix I know
		pass
	else:

		l = x["Country,Other"] # Get the country field 
		l = l.contents # load the content


		if True: # It's quicker then removing a layer of indent after the site is changed and your code stop working ...


			l = l[0] # Get the only field 
			l = str(l)	 # make it a string
			if "href" in l:	 # if it contains a link
				l = l.split(">")[1].split("<")[0] # strip out the name from the field
			elif "span style=" in l: # If it contains some weird color info, like the diamond princess
				l = l.split(">")[1].split("<")[0] # strip out the name form the field

			l = l.strip() # Remove extra white space


			if l == "<strong>Total:</strong>": # No need to parse the header line
				pass
			else:
				# Total cases from table
				c = x["TotalCases"]
				c = c.contents[0].replace(",","") # let's strip those commas
				c = int(c) 
			
				# total deaths from table
				d = x["TotalDeaths"]
				d = d.contents[0].replace(",","").strip() # Those commas ain't our friends
				if d == "": # 0 is represented in the table as empty, which isn't great for math
					d = 0
				d = int(d)

				# oh yeah, our variable names suck, let's fix that
				name = l
				cases = c
				deaths = d

				
				try: # this fails when it doesn't find the country
					population = cs[name] # get the countries population from the population dict
					
					# let's do some math
					ppop = population / 1000
					freq = cases / ppop
					freq = freq * 100
					deathRate = deaths / cases
					deathRate = deathRate * 100
					
					# let's strip those decimals	
					freq = round(freq,2)
					deathRate = round(deathRate,2)
				
					# Foo ..... great name for your main variable containing assembled messages
					foo = {
						"country"	: name,
						"population" 	: population,
						"cases"		: cases,
						"deaths"	: deaths,
						"freq"		: freq,
						"deathRate"	: deathRate

						}
					coll.append(foo) # append it to the list of parsed messages
				except Exception as e:
					print("couldn't find country " + l) # couldn't find the country, complain about it

					

coll = sorted(coll, key = lambda i: i['freq'],reverse=True)  # sort it based on frequncy

# write the json
with open(report, 'w') as outfile:
	json.dump(coll, outfile)
