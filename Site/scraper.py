import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium import webdriver 
from selenium.webdriver.common.by import By

class ESPNManager:
    def __init__(self):
        self.driver = None

    def launch_ESPN(self, browser):
        if browser == 'chrome':
            self.driver = webdriver.Chrome()
        elif browser == 'firefox':
            self.driver = webdriver.Firefox()
        else:
            return 'Please select a valid browser'
        
        self.driver.get('https://www.espn.com/fantasy/football/')
        return 'ESPN launched successfully'

    def scrape_ESPN(self):
        dropdown_element = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/section/div/div[2]/main/div/div/div[3]/div[1]/div[1]/div[2]/div[1]/div/select')

        # Create a Select object
        dropdown = Select(dropdown_element)
        teams = dropdown.options
        table = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/section/div/div[2]/main/div/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div/div/div/div[2]/table")
        roster_size = len(table.find_elements(By.TAG_NAME, "tr")) - 1
        # roster is df where column names are team names and rows are roster requirements
        positions = []
        uniq_num = 0
        roster = pd.DataFrame()
        for i in range(len(teams)):
            dropdown.select_by_index(i)
            team_df = pd.DataFrame(columns=["Player", "Position"])
            for j in range(1, roster_size + 1):
                team_ele = self.driver.find_element(By.XPATH, f"/html/body/div[1]/div[1]/section/div/div[2]/main/div/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div/div/div/div[2]/table/tbody/tr[{j}]")
                # get the second time it says ("tag name","td")
                try:
                    element = self.driver.find_elements(By.CSS_SELECTOR, ".jsx-2810852873.table--cell.player-column")[j]
                    player = element.get_attribute("title")
                    if player is None or player == "":
                        player = " "
                except:
                    player = " "
                position_ele = team_ele.find_element(By.TAG_NAME, "td")
                team_df.loc[j] = [player, position_ele.text]
                if i == 0:
                    positions.append(position_ele.text + str(uniq_num))
                    uniq_num += 1
            roster[teams[i].text] = team_df["Player"]
        # make last column positions
        roster["Positions"] = positions
        print(roster)
        return roster.to_json()

    def scrape_ESPN2(self):
        title = self.driver.find_element(By.XPATH, '//*[@id="news-feed"]/section[1]/section[1]/a/div/div[3]/h2').text
        return title