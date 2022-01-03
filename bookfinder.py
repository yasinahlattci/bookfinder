# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import xlwt
import xlsxwriter as ex
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import pandas as pd

def searchProduct(URL, price):

    class functions():

        def searchAmazon(self,driver, URL, dataset, dataCounter, mainUrl):
            driver.get(URL)
            soupObject = BeautifulSoup(driver.page_source, 'html.parser')
            elements = soupObject.find_all("div", {"data-component-type": "s-search-result"})
            for i in elements:
                address = i.find("a", "a-link-normal a-text-normal").get("href")
                address = mainUrl + address
                driver.get(address)
                "FIND ASINs"
                try:
                    dividedAsin = driver.find_element_by_xpath('//*[@id="detailBullets_feature_div"]/ul').text.split(
                        "\n")
                    for i in dividedAsin:
                        if i[0:7] == 'ISBN-13':
                            asin1 = i[10:13]
                            asin2 = i[14:]
                            ASIN = asin1 + asin2
                except:
                    pass
                "FIND ASIN's finished"
                soupElement = BeautifulSoup(driver.page_source, 'html.parser')
                try:
                    chosenItem = soupElement.find("li", attrs={"class": "swatchElement selected"})
                    if chosenItem == None:
                        chosenItem = soupElement.find("li", attrs={"class": "swatchElement selected resizedSwatchElement"})
                except:
                    pass
                try:
                    "FIND BOOK TYPE"
                    fs = chosenItem.find('span', attrs={"class": "a-button-inner"}).a.text
                    fs = fs.split("\n")[1]
                    newLink = chosenItem.find('span', 'olp-new olp-link').a.get("href")
                    newLink = mainUrl + newLink
                    driver.get(newLink)
                    newSoupItem = BeautifulSoup(driver.page_source, "html.parser")
                    newSoupItemPrices = newSoupItem.find_all("div", attrs={"class": "a-row a-spacing-mini",
                                                                      "class": "a-row a-spacing-mini olpOffer"})
                    results = []
                    for t in newSoupItemPrices:
                        price = float(
                            t.find('span', 'a-size-large a-color-price olpOfferPrice a-text-bold').text.strip()[1:])
                        try:
                            shippingPrice = float(t.find('span', attrs={"class": "olpShippingPrice"}).text[1:])
                            price += shippingPrice
                        except:
                            pass
                        results.append(price)
                    dataset.loc[dataCounter] = {'ASIN': ASIN, 'Cover': fs, 'AmzMin': min(results),
                                                 'AmzMax': max(results), 'AmzOrt': sum(results) / len(results),
                                                 'EbayMin': None, 'EbayMax': None, 'EbayOrt': None, 'profit':None}
                    dataCounter += 1
                except:
                    pass
            "Go to seller's new page"
            try:
                goNextPage = soupObject.find('li',attrs={'class':'a-last'}).a.get('href')
                goNextPage = mainUrl+goNextPage
                self.searchAmazon(driver, goNextPage, dataset, dataCounter, mainUrl)
            except:
                pass

            return driver, dataset

        def searchEbay(self, driver, dataset):
            minlist = []
            maxlist = []
            averageList = []
            for i in dataset['ASIN']:
                url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=' \
                      '{}&_sacat=0&rt=nc&LH_ItemCondition=3'.format(i)
                driver.get(url)
                soupObject = BeautifulSoup(driver.page_source, 'html.parser')
                newBooks = soupObject.find_all('div', attrs={'class': 's-item__details clearfix'})
                priceList = []
                for i in range(5):
                    try:
                        price = float(newBooks[i].find('span', attrs={'class': 's-item__price'}).text[1:])
                        try:
                            shippingPrice = float(
                                newBooks[i].find('span', attrs={'class': 's-item__shipping s-item__logisticsCost'})
                                    .text.split(" ")[0][2:])
                            price += shippingPrice
                        except:
                            pass
                        priceList.append(price)
                    except:
                        pass
                try:
                    minlist.append(min(priceList))
                    maxlist.append(max(priceList))
                    averageList.append(sum(priceList) / len(priceList))
                except:
                    minlist.append(float(0))
                    maxlist.append(float(0))
                    averageList.append(float(0))

            dataset['EbayMin'] = minlist
            dataset['EbayMax'] = maxlist
            dataset['EbayOrt'] = averageList
            driver.quit()
            return dataset

        def writeOutput(self, dataset, price):
            columnList = ["ASIN", "Cover", "AmzMin", "AmzMax", "AmzOrt", "EbayMin", "EbayMax", "EbayOrt", "Netprofit"]
            counter = 1
            path = r'C:\Users\daimo\OneDrive\Masaüstü'
            wb = ex.Workbook('{}\sonucla1r.xlsx'.format(path))
            page1 = wb.add_worksheet('Page1')
            for i in range(len(columnList)):
                page1.write(0, i, columnList[i])
            for i in dataset.values:
                if(i[8]>price):
                    for j in range(8):
                        page1.write(counter, j, i[j])
                    counter += 1
            wb.close()

        def calculateProfit(self, dataset):
            """profit=Amzprice-RefFee-Vcf-Shipping-Alış-DepoKira"""
            profitList = []
            for i in dataset.values:
                profit = i[4]-0.15*i[4]-float(1.8)-float(3)-i[5]-float(1)
                profitList.append(profit)
            dataset['profit'] = profitList
            return dataset

    process = functions()
    mainUrl = 'https://www.amazon.com'
    results = {'ASIN': [],
                'Cover': [],
                'AmzMin': [],
                'AmzMax': [],
                'AmzOrt': [],
                'EbayMin': [],
                'EbayMax': [],
                'EbayOrt': [],
                'profit':[]}
    dataset = pd.DataFrame(results, columns=['ASIN', 'Cover', 'AmzMin', 'AmzMax',
                                              'AmzOrt', 'EbayMin', 'EbayMax', 'EbayOrt', 'profit'])
    dataCounter = 0
    driver = webdriver.Chrome("./driver/chromedriver.exe")
    driver.get(mainUrl)
    driver, dataset = process.searchAmazon(driver, URL, dataset, dataCounter, mainUrl)
    dataset = process.searchEbay(driver, dataset)
    dataset = process.calculateProfit(dataset)
    process.writeOutput(dataset, price)
###########################################
"""URL = 'https://www.amazon.com/s?me=A3TDR7PXU58ECM&marketplaceID=ATVPDKIKX0DER'
price=float(1)
searchProduct(URL, price)"""

