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

# driver.get("https://dl.acm.org/conference/hri/proceedings")

# elements = driver.find_elements(By.CLASS_NAME, "conference__proceedings")

# conferenceLinksList = []

# for element in elements:
#     #print(element.text)
#     confLinks = element.find_element(By.CLASS_NAME, "conference__title")
#     #print(confLinks.text)
#     aLink = confLinks.find_elements(By.TAG_NAME, "a")
    
#     for a in aLink:
#         hrefLink = a.get_attribute("href")
#         conferenceLinksList.append(hrefLink)

# #print(conferenceLinksList)  #This prints all the link to the individual conferences
# containersList = []
# for link in conferenceLinksList:
#     headingsLinksList = []
#     driver.get(link)
#     findHeadings = driver.find_elements(By.CSS_SELECTOR, '[id*="heading"]')
#     headingCount = len(findHeadings)  #Counting how many headings are there per conference link
#     #print(headingCount)

#     for heading in findHeadings:
#         hrefLinkHead = heading.get_attribute("href")
#         headingsLinksList.append(hrefLinkHead)
#     #print(headingsLinksList)   #Prints the links for each heading for each conference website

#     for headLink in headingsLinksList:
#         driver.get(headLink)

#         containers = driver.find_elements(By.CLASS_NAME, "issue-item-container")
#         #print(len(containers))    #How many containers per heading
#         # containersList = []
#         for container in containers:
#             name = container.find_element(By.CLASS_NAME, "issue-heading").text
#             if (name == "RESEARCH-ARTICLE" or name == "SHORT-PAPER"):
#                 articleSection = container.find_element(By.XPATH, './/div[@class = "issue-item__content-right"]//h5[@class = "issue-item__title"]/a')
#                 articleLink = articleSection.get_attribute('href')
#                 #print(articleLink)
#                 containersList.append(articleLink)
#         print(containersList)  #Gives the list for link of containers that appease the conditions

    














#containersList = ['https://dl.acm.org/doi/10.1145/3610977.3634953', 'https://dl.acm.org/doi/10.1145/3610977.3634953','https://dl.acm.org/doi/10.1145/3610977.3634948', 'https://dl.acm.org/doi/10.1145/3610977.3634960', 'https://dl.acm.org/doi/10.1145/3610977.3634921']
containersList = ["https://dl.acm.org/doi/10.1145/3610977.3634957", 'https://dl.acm.org/doi/10.1145/3610977.3634953']
wait = WebDriverWait(driver, 5)




for article in containersList:

    if article == "https://dl.acm.org/doi/10.1145/3610977.3634957":
        continue

    try:
        driver.get(article)
        pubDate = driver.find_element(By.XPATH, '//span[@class="core-date-published"]').text
        #print(pubDate)
        year = pubDate.split()[-1]
        #print(year)

        if int(year) >= 2010:

            authors = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@property="author"]')))
            authorNum = 1

            for author in authors:
                #print(authorNum)
                time.sleep(1)
                #print(authorNum)

                author = wait.until(EC.presence_of_element_located((By.XPATH, f'(//span[@property="author"])[{authorNum}]')))
                givenName = author.find_element(By.XPATH, './/span[@property="givenName"]').text
                #print(givenName.text)
                familyName = author.find_element(By.XPATH, './/span[@property="familyName"]').text
                #print(familyName.text)
       
                openStartName = wait.until(EC.presence_of_element_located((By.XPATH, f'//a[@aria-expanded="false" and @data-db-target-for="axel_author_artseq-0000{authorNum}"]')))
                openStartName.click()           
                aff = wait.until(EC.presence_of_element_located((By.XPATH, f'//div[@id="artseq-0000{authorNum}"]//span[@property="name"]')))
                authorAff = aff.text
                print(authorAff)
                openStartName.click()



                uniqueAuthorName = f"{givenName} + {familyName} + {authorAff}"  #Unique Key for each author

                if uniqueAuthorName not in authorData:
                    authorData[uniqueAuthorName] = {year: 0 for year in yearRange}
            
                authorData[uniqueAuthorName][year] += 1

                

            


                authorNum += 1
    except Exception as e:
        articlesISSUE.append(article)
        print(f"ISSUE:{article}with{e}")


        
driver.quit()
print(f"Article with Issues: {articlesISSUE}")







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
