## Import libraries
import csv 
import datetime 
import requests 
from bs4 import BeautifulSoup
import sys
import time 
from random import random

## Required functions
def split_string(string):
 
    # Split the string based on space delimiter
    list_string = string.split(' ')
     
    return list_string
 
def join_string(list_string):
 
    # Join the string based on '-' delimiter
    string = '%20'.join(list_string)
     
    return string

def save_record_to_csv(record, filepath, create_new_file=False):
    """Save an individual record to file; set `new_file` flag to `True` to generate new file"""
    header =   ['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'JobUrl']

    if create_new_file:
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    else:
        with open(filepath, mode='a+', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(record)



def get_url(position, location, publication_date):
  """Generate a url from position, location and publication date"""
  template = "https://fr.indeed.com/jobs?q={}&l={}&fromage={}"

  # pubblication_date (fromage) can take one of these values  {1, 3, 7, 14, last} 
  # (1) last 24 hours, (3) last three days, (7) last seven days, (last) since last visit
  position = join_string(split_string (position))
  url = template.format(position, location, publication_date)
  return url 



def find_post_date(text):

  il_ya = [int(s) for s in text.split() if s.isdigit()]
  if len(il_ya) == 0:
      published_day = datetime.datetime.today().strftime('%Y-%m-%d')
  else:

      days_passed = datetime.timedelta(il_ya[0])
      current_day = datetime.datetime.today()#.strftime('%Y-%m-%d') #daettime.date(2022,8,27)
      published_day = str( current_day - days_passed)[:10]
  return published_day

def get_job_data(card, soup):
   """Extract job data from single record"""
   atag = card.h2.a
   job_title = atag.span.get('title')
   job_url = "https://fr.indeed.com"+  atag.get('href')
   company_name = card.find('span', 'companyName').text
   job_location = card.find('div', 'companyLocation').text
   new_url = job_url
   headers = {"User-agent" :"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36" }
   new_response = requests.get(new_url, headers= headers)
   new_soup = BeautifulSoup(new_response.text, 'html.parser')
   poste_since  = new_soup.find('span', 'jobsearch-HiringInsights-entry--text').text
   post_date = find_post_date(poste_since)
   today = datetime.datetime.today().strftime("%Y-%m-%d")
   record = (job_title, company_name, job_location, post_date,today, job_url)

   return record 

def save_records(records, filepath):
    with open(filepath, 'w', newline ='', encoding = 'utf-8') as f:
          writer = csv.writer(f)
          writer.writerow(['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'JobUrl'])
          writer.writerows(records)
## Putting all together 
def main(position, location, publication_date, filepath ):
  """Run the main program"""
  records = []
  url = get_url(position, location, publication_date)
  headers = {"User-agent" :"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36" }

  #Extract the jobs data
  while True:
    response = requests.get(url, headers= headers)
    print(response)
    # Create an Beautifulsoup object to parse the html page
    soup= BeautifulSoup(response.text, 'html.parser')

    
    cards = soup.find_all('div', 'job_seen_beacon' )
    for card in cards:
      record = get_job_data(card, soup)
      records.append(record)
   
    
    try: 
      # next page url
      url =  'https://fr.indeed.com'  + soup.find('a', {'aria-label':'Suivant'}).get('href')  #url + '&start=' + str(start)#'https://fr.indeed.com/jobs?q=Data+scientist&l=France' +'&start=' + str(start)
      print("Next url", url)                          


    except AttributeError:
          ############################ Try again sending the request 
          response = requests.get(url, headers= headers)
          print(response)
          soup= BeautifulSoup(response.text, 'html.parser')
          cards = soup.find_all('div', 'job_seen_beacon' )
          for card in cards:
            record = get_job_data(card, soup)
            records.append(record)
      
        
          try: 
        # next page url
            url =  'https://fr.indeed.com'  + soup.find('a', {'aria-label':'Suivant'}).get('href')  #url + '&start=' + str(start)#'https://fr.indeed.com/jobs?q=Data+scientist&l=France' +'&start=' + str(start)
            print("Next url", url)   

          ########################## If the second try did not work stop sending requests  

          except AttributeError:
           
            cleaned_records = set(records)
            print('Finished collecting {:,d} job postings.'.format(len(cleaned_records)))
            save_records(cleaned_records, filepath)
            break
           
if __name__ == '__main__':
    # job search settings
    title = 'Data Scientist'
    loc = 'France'
    date = 3
    path = 'data_scientist_jobs.csv'

  
    main(title, loc, date, path)
