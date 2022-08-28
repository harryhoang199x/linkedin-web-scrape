#!/usr/bin/env python
# coding: utf-8

# In[ ]:


pip install selenium bs4


# In[ ]:


import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
from parsel import Selector
import re


# In[ ]:


# USING DRIVER TO GO TARGETED WEBSITE LINKEDIN - NEED TO INSTALL CHROME DRIVER BEFORE RUN SCRIPT
PATH = './chromedriver'
browser = webdriver.Chrome(PATH)
browser.get('https://www.linkedin.com/')
browser.maximize_window()
time.sleep(1)


# In[ ]:


#LOGIN PROCEDURE - NOTE THAT USING A CLONE ACCOUNT TO AVOID BANNING FROM LINKEDIN
username = browser.find_element('id', 'session_key')
username.send_keys('email_address') # Change your account to log in
password = browser.find_element('id', 'session_password')
password.send_keys('password') # your password to log in
browser.find_element(By.CLASS_NAME,'sign-in-form__submit-button').click()
time.sleep(2)


# In[ ]:


# GO TO JOB SEARCH
browser.get('https://www.linkedin.com/jobs/search/')
time.sleep(1)


# In[ ]:


# SEARCH ALL JOB RELATED TO DATA
job_search = browser.find_element(By.CLASS_NAME, "jobs-search-box__text-input")
job_search.send_keys('data')
job_loc_search = browser.find_element(By.XPATH, '//input[@aria-label="City, state, or zip code"]')
job_loc_search.clear()
job_loc_search.send_keys('Ontario')
browser.find_element(By.CLASS_NAME, "jobs-search-box__submit-button").click()
time.sleep(2)


# In[ ]:


#USING FOR GET JOB_ID
def get_job_id(url):
    a = re.search('\d{10,11}',url).group()
    return a


# In[ ]:


#DUMMY VARIABLE
raw_job =pd.DataFrame()
job_list = []
job_main_info_list = []
list_url = []
check = 0


# In[ ]:


# COLLECT THE DATA
for page in range(1,51): 
    job_cards = browser.find_elements(By.XPATH, '//ul[@class="scaffold-layout__list-container"]/li')
    card_ids = [result.get_attribute('id') for result in job_cards]
    url = browser.current_url
    response = requests.request('GET', url)
    content = response.content.decode('utf-8')
    soup = bs(content, 'html.parser')
    items = soup.find('ul', {'class': 'jobs-search__results-list'})
    ## GET URL
    job_links = [i["href"].strip('\n ') for i in items.find_all('a', {'class': 'base-card__full-link'})]
    job_id_list = [get_job_id(link) for link in job_links]
    ## GO TO EACH JOB CARD BY URL TO GET DATA FIELDS
    for job_id in job_id_list:
        try:
            # JOB TITLE - JOB DES - COMPANY - LOCATION
            job_title = browser.find_element(By.XPATH, "//h2[@class='t-24 t-bold jobs-unified-top-card__job-title']").text
            job_description = browser.find_element(By.XPATH, '//div[@id="job-details"]').text.replace('\n',' ')
            job_company = items.find('h4', {'class': 'base-search-card__subtitle'}).text.strip('\n ')
            job_location = items.find('span', {'class': 'job-search-card__location'}).text.strip('\n ')
        except:
            job_title =''
            job_description = ''
            job_company = ''
            job_location = ''
        try:
            # JOB POST DATE - NUMBER APPLICATION
            sub_card_2 = browser.find_element(By.XPATH, "//span[@class='jobs-unified-top-card__subtitle-secondary-grouping t-black--light']").find_elements(By.TAG_NAME, 'span')
            job_post_date = sub_card_2[0].text
            job_no_of_app = sub_card_2[1].text
        except:
            job_post_date = ''
            job_no_of_app = ''
        try:
            #SALARY - JOB TYPE - JOB LEVEL
            sub_card_3 = browser.find_elements(By.XPATH, '//div[@class="mt5 mb2"]/ul//li')
            if sub_card_3[0].text != '':
                job_info = sub_card_3[0].text.split(" · ")
                if (len(job_info) == 1):
                    job_salary = ''
                    job_work_dur = job_info[0]
                    job_pos_title = ''
                elif (len(job_info) == 2):
                    job_salary = ''
                    job_work_dur = job_info[0]
                    job_pos_title = job_info[1]
                else:
                    job_salary = job_info[0]
                    job_work_dur = job_info[1]
                    job_pos_title = job_info[2]
            else:
                job_salary = ''
                job_work_dur = ''
                job_pos_title = ''

            if sub_card_3[1].text != '':
                job_info = sub_card_3[1].text.split(" · ")
                if len(job_info) == 2:
                    company_size = job_info[0]
                    company_sector = job_info[1]
                elif len(job_info) == 1:
                    company_size = job_info[0]
                    company_sector = ''
                else:
                    company_size = ''
                    company_sector = ''
            else:
                company_size = ''
                company_sector = ''
        except:
            job_salary = ''
            job_work_dur = ''
            job_pos_title = ''
            company_size = ''
            company_sector = ''
            time.sleep(5)
        try:
            job_data = [job_title,job_company,job_location,job_salary,job_work_dur,job_pos_title,company_size,company_sector,job_post_date,job_no_of_app,job_description]
            job_list.append(job_data)
        except:
            continue
        try:
            #CHANGE URL FOR NEXT JOB
            get_url = browser.current_url
            new_url = get_url.replace(get_job_id(get_url),job_id)
            browser.get(new_url)
            time.sleep(5)
        except:
            continue
            check += 1
            if check >= len(job_id_list):
                break
            else:
                continue 
    # GO TO NEXT PAGE OF JOB SEARCH
    browser.find_element(By.XPATH, f'//button[@aria-label="Page {page}"]').click()
    time.sleep(10)


# In[ ]:


#CONVERT TO DATAFRAME
raw_data = pd.DataFrame(job_list, columns = ['job_title',
                                             'company_name',
                                             'location',
                                             'salary',
                                             'job_type',
                                             'job_level',
                                             'company_size',
                                             'industry',
                                             'date_post',
                                             'num_application',
                                             'job_description'])


# In[ ]:


# EXPORT TO CSV
raw_data.to_csv('linkedin_raw_data.csv')

