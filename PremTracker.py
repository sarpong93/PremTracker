#!/usr/bin/env python
# coding: utf-8

# In[21]:


import numpy as np


# In[22]:


import pandas as pd

def league_data(url, id):
    
    """
    scrape data from multiple tables on the fbref website and clean it.
    
    :param url, id: the website's url, and the table's id
    :return: selected table.
    """
    #scraping the data from the fbref website

    stats_df = pd.read_html(url, 
                  attrs=({"id":id}))[0]


    #dropping extra row if table is multi-index
    stats_df.columns = stats_df.columns.droplevel(0) if isinstance(stats_df.columns, pd.MultiIndex) else stats_df.columns


    #loads the selected table
    return stats_df

#calling the function
league_stats = league_data('https://fbref.com/en/comps/9/Premier-League-Stats#all_league_structure', "results2024-202591_overall")
team_stats = league_data('https://fbref.com/en/comps/9/Premier-League-Stats#all_league_structure', 'stats_squads_standard_for')
pass_stats = league_data('https://fbref.com/en/comps/9/Premier-League-Stats#all_league_structure', 'stats_squads_passing_for')
pass_type_stats = league_data('https://fbref.com/en/comps/9/Premier-League-Stats#all_league_structure', 'stats_squads_passing_types_for')
def_stats = league_data( 'https://fbref.com/en/comps/9/Premier-League-Stats#all_league_structure', 'stats_squads_defense_for')


# In[23]:


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def def_line(url):

    """
    Scrape data from tables from different websites and clean it.
    Adopted this second method when the first did not work for specific sites.
    
    :param 
    :return: selected table
    """    

    # Set up Selenium headless browser
    options = Options()
    options.add_argument("--headless")  # Run in background
    driver = webdriver.Chrome(options=options)

    # Load the webpage
    driver.get(url)
    time.sleep(5)  # Allow time for JS to load table

    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the table
    table = soup.find("table", {"id": "DataTables_Table_0"})

    # Convert to pandas DataFrame
    df = pd.read_html(str(table))[0]

    # Close the browser
    driver.quit()

    #Matching the names of teams in the table to fbref naming format(will try string matching for this later)
    df_short = df[['Team', 'DLINE']]
    df_short['Team'] = df_short['Team'].replace({
    'N. Forest': "Nott'ham Forest",
    'C. Palace': 'Crystal Palace',
    'Ipswich': 'Ipswich Town',
    'Man Utd' : 'Manchester Utd',
    'Man City' : 'Manchester City',
    'Newcastle' : 'Newcastle Utd',
    'Leicester' : 'Leicester City',
    'Spurs' : 'Tottenham'})

    return df_short

def_line_stats = def_line("https://markstats.club/teams-eng-24-25/")


# In[24]:


def clean_pass_stats(df):

    """
    Giving distint column names in the pass_stats table. 
    
    :param 
    :return: distinct column names.
    """     

    #renaming columns
    pass_stats.columns = ['Squad', '# Pl', '90s', 'Pass_Cmp', 'Pass_Att', 'Pass_Cmp%', 'TotDist', 'PrgDist',
       'Short_Cmp', 'Short_Att', 'Short_Cmp%', 'Medium_Cmp', 'Medium_Att', 'Medium_Cmp%', 'Long_Cmp', 'Long_Att', 'Long_Cmp%', 'Ast',
       'xAG', 'xA', 'A-xAG', 'KP', '1/3', 'PPA', 'CrsPA', 'PrgP']

clean_pass_stats(pass_stats)


# In[25]:


def possession_style(team_list):
    """
    Determines each team's possession style with data derived from the loaded tables.

    :param team_list: list of team names
    :return: dictionary with each team's possession style
    """ 
    result = {}
    
    for team in team_list:    
        team_data = team_stats[team_stats['Squad'] == team]
        pass_data = pass_stats[pass_stats['Squad'] == team]

        if team_data.empty or pass_data.empty:
            result[team] = {'error': 'Team not found'}
            continue  

        poss = team_data['Poss'].iloc[0]  # Get possession value
        pass_acc = pass_data['Pass_Cmp%'].iloc[0]  # Get pass completion %

        # Classify style
        if (poss > 55) and (pass_acc > 80):
            style = 'Possession based'
        elif (poss < 45) and (pass_acc < 80):
            style = 'Direct'
        else:
            style = 'A mix of possession and direct play'

        
        result[team] = {
            'Possession': poss,
            'Pass Accuracy': pass_acc,
            'Possession Style': style
        }

    return result


# In[26]:


def attacking_style(team_list):

    """
    Determines a team's possession style with data derived from the loaded tables.
    
    :param team_list: list of team names
    :return: the team's possession style
    """ 
    
    avg_lng = np.mean(pass_stats['Long_Att'].values)
    avg_crs = np.mean(pass_type_stats['Crs'].values)
    avg_sht_pass = np.mean(pass_stats['Short_Att'].values)
    result = {}

    for team in team_list:
        team_data = team_stats[team_stats['Squad'] == team]
        pass_data = pass_stats[pass_stats['Squad'] == team]
        pass_type_data = pass_type_stats[pass_type_stats['Squad'] == team]
        
        if team_data.empty and pass_data.empty and pass_type_data.empty:
            result[team] = {'error': 'Team not found'}
            continue   
    
        lng = pass_data['Long_Att'].iloc[0]
        crs = pass_type_data['Crs'].iloc[0]
        sht_pass = pass_data['Short_Att'].iloc[0]
        

        if crs > (1.2*avg_crs):
            style = "Reliant on wing play"
        elif lng > (1.2*avg_lng):
            style = "Direct Play"
        elif sht_pass >= (1.2*avg_sht_pass):
            style = "Slow build-up"
        else:
            style = "Mix of play styles"

        result[team] = {
            'Attacking Style': style
        }

    return result



# In[27]:


def defensive_style(team_list):
    """
    Determines each team's defensive style from a list of team names.

    :param team_list: list of team names
    :return: dictionary with each team's defensive line height and style
    """
    line_avg = np.mean(def_line_stats['DLINE'].values)
    result = {}

    for team in team_list:
        line_data = def_line_stats[def_line_stats['Team'] == team]

        if line_data.empty:
            result[team] = {'error': 'Team not found'}
            continue        

        line = line_data['DLINE'].iloc[0]

        if line >= 46:
            style = "Press High"
        elif line < 40:
            style = "Low Block"
        else:
            style = "Mid Block"

        result[team] = {
            'Defensive Line Height': line,
            'Defensive Style': style
        }

    return result


# In[28]:


names = league_stats['Squad'].tolist()
poss_style = possession_style(names)
att_style = attacking_style(names)
def_style = defensive_style(names)


# In[29]:


from collections import defaultdict

def merge_dicts(*dicts):
    """
    Merges the dictionaries created by the functions above.

    :param dicts: list of dictionaries to be merged.
    :return: a merged dictionary
    """

    merged = defaultdict(dict)
    for d in dicts:
        for team, stats in d.items():
            merged[team].update(stats)
    return dict(merged)

combined = merge_dicts(poss_style, att_style, def_style) 


# In[30]:


import json

def save_file(data):
    """
    Saves the combined dictionary into a json file

    :param data: data to be saved
    :return: a json file
    """    

    with open('team_styles.json', 'w') as f:
        json.dump(data, f, indent=4)

file = save_file(combined)
file

