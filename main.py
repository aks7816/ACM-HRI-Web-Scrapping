#These are all of my imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from collections import defaultdict
from selenium.common.exceptions import TimeoutException

#These are used when data is being extracted and imported to excel
articlesISSUE = []
authorData = defaultdict(dict)
yearRange = [str(year) for year in range(2010, 2025)]

#This where the data scrapping process begins
driver = webdriver.Chrome()

driver.get("https://dl.acm.org/conference/hri/proceedings")

elements = driver.find_elements(By.CLASS_NAME, "conference__proceedings")

conferenceLinksList = [] #This has all the links to the individual conferences

#This loop helps us get the links to each individual conference such as 2024 Proceedings, 2024 Companion, 2023 Proceedings and so on...
for element in elements:
    #print(element.text)
    confLinks = element.find_element(By.CLASS_NAME, "conference__title")
    #print(confLinks.text)
    aLink = confLinks.find_elements(By.TAG_NAME, "a")
    for a in aLink:
        hrefLink = a.get_attribute("href")
        conferenceLinksList.append(hrefLink)

#print(conferenceLinksList)  #This prints all the links to the individual conferences
containersList = []
for link in conferenceLinksList:
    headingsLinksList = []
    driver.get(link)
    findHeadings = driver.find_elements(By.CSS_SELECTOR, '[id*="heading"]')
    headingCount = len(findHeadings)  #Counting how many headings are there per conference link
    #print(headingCount)

    for heading in findHeadings:
        hrefLinkHead = heading.get_attribute("href")
        headingsLinksList.append(hrefLinkHead)
    #print(headingsLinksList)   #Prints the links for each heading for each conference website

    for headLink in headingsLinksList:
        driver.get(headLink)

        containers = driver.find_elements(By.CLASS_NAME, "issue-item-container")
        #print(len(containers))    #How many containers per heading, by containers we mean each box that has information about an article
        # containersList = []
        for container in containers:
            name = container.find_element(By.CLASS_NAME, "issue-heading").text
            if (name == "RESEARCH-ARTICLE" or name == "SHORT-PAPER"):
                articleSection = container.find_element(By.XPATH, './/div[@class = "issue-item__content-right"]//h5[@class = "issue-item__title"]/a')
                articleLink = articleSection.get_attribute('href')
                #print(articleLink)
                containersList.append(articleLink)
        print(containersList)  #Gives the list for link of containers that appease the conditions of the if loop

    
#These commented containersList contains links to individual articles for extraction of author names and their affiliations. I use these to test the next section of the code with just a few articles at a time.
#containersList = ['https://dl.acm.org/doi/10.1145/3610977.3634953', 'https://dl.acm.org/doi/10.1145/3610977.3634953','https://dl.acm.org/doi/10.1145/3610977.3634948', 'https://dl.acm.org/doi/10.1145/3610977.3634960', 'https://dl.acm.org/doi/10.1145/3610977.3634921']
#containersList = ["https://dl.acm.org/doi/10.1145/3610977.3634957", 'https://dl.acm.org/doi/10.1145/3610977.3634953']
wait = WebDriverWait(driver, 5)

for article in containersList:

    #Use this loop when we want to avoid certain articles
    if article == "https://dl.acm.org/doi/10.1145/3610977.3634957":
        continue

    try:
        driver.get(article)
        pubDate = driver.find_element(By.XPATH, '//span[@class="core-date-published"]').text
        #print(pubDate)
        year = pubDate.split()[-1]
        #print(year)   #Here we are extracting just the year of the publication

        if int(year) >= 2010:

            authors = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@property="author"]')))
            authorNum = 1 #this is used to extract name and affiliation of each author in the html

            for author in authors:
                #print(authorNum)
                time.sleep(1)
                #print(authorNum)

                author = wait.until(EC.presence_of_element_located((By.XPATH, f'(//span[@property="author"])[{authorNum}]')))
                givenName = author.find_element(By.XPATH, './/span[@property="givenName"]').text
                #print(givenName.text) #Here we are extracting the first name
                familyName = author.find_element(By.XPATH, './/span[@property="familyName"]').text
                #print(familyName.text) #Here we are extracting the last name
       
                openStartName = wait.until(EC.presence_of_element_located((By.XPATH, f'//a[@aria-expanded="false" and @data-db-target-for="axel_author_artseq-0000{authorNum}"]')))
                openStartName.click()           
                aff = wait.until(EC.presence_of_element_located((By.XPATH, f'//div[@id="artseq-0000{authorNum}"]//span[@property="name"]')))
                authorAff = aff.text
                print(authorAff)
                openStartName.click()

                uniqueAuthorName = f"{givenName} + {familyName} + {authorAff}"  #Unique Key for each author

                #Here we are initalizing values for the columns of years. Each author will initally have 0 for each column. And there will be an increment of 1 each time an author publishes for a certain year.
                if uniqueAuthorName not in authorData:
                    authorData[uniqueAuthorName] = {year: 0 for year in yearRange}
            
                authorData[uniqueAuthorName][year] += 1

                authorNum += 1

    #Included this section b/c of timeout issues             
    except Exception as e:
        articlesISSUE.append(article)
        print(f"ISSUE:{article}with{e}")

        
driver.quit()
print(f"Article with Issues: {articlesISSUE}")


#This section is for the excel output
excelData = []

for uniqueAuthorName, yearNum in authorData.items():
    givenName, familyName, Affiliation = uniqueAuthorName.split('+')
    authorEntry = {
        'Author First Name': givenName,
        'Author Last Name': familyName,
        'Affiliation': Affiliation,
    }
    authorEntry.update(yearNum)
    excelData.append(authorEntry)



df = pd.DataFrame(excelData)

df.to_excel("ACM_HRI_Conference_Data.xlsx")
