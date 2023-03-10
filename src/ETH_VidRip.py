from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


import urllib.request

from tqdm import tqdm

from multiprocessing.pool import ThreadPool

from time import time as timer
from time import sleep
import json, os



class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)




class ETHLecture():
    def __init__(self, obj, credentials, driver, base="downloads"):
        self.name = obj["name"]
        self.url = obj["url"]

        if "username" in obj and "password" in obj:
            self.credentials = {"username": obj["username"], "password": obj["password"]}
        else:
            self.credentials = credentials

        self.driver = driver

        self.path = os.path.join(base, self.name)

        self.createFolder()

    def createFolder(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def check_access(self):
        try:
            username_title = self.driver.find_element(By.XPATH, '//*[@id="j_username_title"]').text.lower()
            if "series" in username_title:
                return "series"
            elif "eth" in username_title:
                return "eth"
            else:
                return None
        except NoSuchElementException:
            return True


    def login(self):
        if self.check_access() != True:
            print("Have to relogin")
            username_el = self.driver.find_element(By.XPATH, '//input[@aria-labelledby="j_username_title"]')
            password_el = self.driver.find_element(By.XPATH, '//input[@aria-labelledby="j_password_title"]')
            
            username_el.click()
            username_el.send_keys(self.credentials['username'])
            password_el.click()
            password_el.send_keys(self.credentials['password'])

            # self.driver.find_element(By.XPATH, '//*[@id="login"]/fieldset/div/div[1]/button').click()
            self.driver.find_element(By.CSS_SELECTOR, "div.vertical:nth-child(1) > button:nth-child(5)").click()



    
    
    def getVideosLinks(self):
        """Get the links to the individual video pages of the course """
        self.driver.get(self.url)
        print("Getting videos for {}".format(self.name))

        self.login()

        elem = self.driver.find_elements(By.XPATH, '//*[@id="filter-container"]/*[@class="newsListBox"]/div/a')
        links = [i.get_attribute('href') for i in elem]
      
        vids = []
        for i, link in enumerate(reversed(links)):
            self.driver.get(link)
            delay = 2
            try:
                WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="contentMain"]/div[3]/div[2]/div/div/h3')))
            except TimeoutException:
                print(f"Failed to get link {i} from {self.name}")
                continue
            
            if self.check_access() != True:
                print(f"Can't Login at {self.name}")
                return vids


            title = self.driver.find_element(By.XPATH, '//*[@id="contentMain"]/div[3]/div[2]/div/div/h3').get_attribute("innerHTML")
            lecturer = self.driver.find_element(By.XPATH, '//*[@id="contentMain"]/div[3]/div[2]/div/div/p[1]/span/span').get_attribute("innerHTML")
            date = self.driver.find_element(By.XPATH, '//*[@id="contentMain"]/div[3]/div[2]/div/div/p[3]/time').get_attribute("innerHTML")
            

            self.driver.switch_to.frame(self.driver.find_element(By.TAG_NAME, "iframe"))

            try:
                WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="video_0"]/source')))
            except TimeoutException:
                print(f"Failed to get video {i} from {self.name}")
                continue

            src = self.driver.find_element(By.XPATH, '//*[@id="video_0"]/source')
            vidSource = src.get_attribute("src")
            self.driver.switch_to.default_content()
            
            vids.append((i, title,lecturer,date, vidSource, self.path))
            #driver.save_screenshot("screenshot{}.png".format(i))
        return vids




class ETHVideoScraper():

    def __init__(self, jobs, credentials, config={}):
        self.config = {
            'base': "downloads",
            'njobs': 1
        }

        self.config = {**self.config, **config}

        self.credentials = credentials

        self.driver = webdriver.Firefox()

        self.wait = WebDriverWait(self.driver, 10)
        self.driver.implicitly_wait(3)

        


        ## Login before initializing jobs
        self.login()
        sleep(2)
        
        self.jobs = [ETHLecture(j, credentials, self.driver, self.config["base"]) for j in jobs]

        if not os.path.exists(self.config["base"]):
            os.makedirs(self.config["base"])


    def login(self):
        ## Get a random course just to login
        self.driver.get("https://video.ethz.ch/lectures/d-infk/2021/autumn/263-2800-00L.html")

        username_el = self.driver.find_element(By.XPATH, '//input[@aria-labelledby="j_username_title"]')
        password_el = self.driver.find_element(By.XPATH, '//input[@aria-labelledby="j_password_title"]')
        
        username_el.click()
        username_el.send_keys(self.credentials['username'])
        password_el.click()
        password_el.send_keys(self.credentials['password'])

        # self.driver.find_element(By.XPATH, '//*[@id="login"]/fieldset/div/div[1]/button').click()
        self.driver.find_element(By.CSS_SELECTOR, "div.vertical:nth-child(1) > button:nth-child(5)").click()
    

    def run(self):

        start = timer()


        def fetch_url(entry):
            index, title, name, date, src, path = entry
            fileName = os.path.join(path, f"{index}_{date}_{title}_{name}.mp4")
            if os.path.exists(fileName) and not self.config["no_skip"]:
                print(f"Skipping {index}")
                return fileName
            
            with open(fileName, 'wb') as f:
                print("Getting {index}")
                r = requests.get(src, allow_redirects=True, stream=True)
                if r.status_code == 200:
                    for chunk in r:    
                        f.write(chunk)
                print("Done {index}")
            return fileName


        links = []
        for j in self.jobs:
            links += j.getVideosLinks()

        # We don't need the driver anymore
        self.driver.close()

        for entry in links:
            index, title, name, date, src, path = entry
            fileName = os.path.join(path, f"{index}_{date}_{title}_{name}.mp4")
            
            if os.path.exists(fileName):
                print("Skipping {index}")
                continue

            with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc="{}-{}".format(index,title)) as t:
                urllib.request.urlretrieve(src, filename=fileName, reporthook=t.update_to)

        # results1 = ThreadPool(self.config['njobs']).imap_unordered(fetch_url, links)

        # results2 = ThreadPool(self.config['njobs']).imap_unordered(upload, results1)


        # for result in results1:
            # print("Finished {}".format(result))

        print("Elapsed Time: {:.2f}s".format(timer() - start))
