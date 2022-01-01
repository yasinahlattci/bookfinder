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
        def searchAmazon(self,driver, URL, dataset, data_counter, main_url):
            driver.get(URL)
            soupObject = BeautifulSoup(driver.page_source, 'html.parser')
            elements = soupObject.find_all("div", {"data-component-type": "s-search-result"})
            for i in elements:
                address = i.find("a", "a-link-normal a-text-normal").get("href")
                address = main_url + address
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
                    new_linki = chosenItem.find('span', 'olp-new olp-link').a.get("href")
                    new_linki = main_url + new_linki
                    driver.get(new_linki)
                    newSoupItem = BeautifulSoup(driver.page_source, "html.parser")
                    newSoupItemPrices = newSoupItem.find_all("div", attrs={"class": "a-row a-spacing-mini",
                                                                      "class": "a-row a-spacing-mini olpOffer"})
                    results = []
                    for t in newSoupItemPrices:
                        fiyat = float(
                            t.find('span', 'a-size-large a-color-price olpOfferPrice a-text-bold').text.strip()[1:])
                        try:
                            ship = float(t.find('span', attrs={"class": "olpShippingPrice"}).text[1:])
                            fiyat += ship
                        except:
                            pass
                        results.append(fiyat)
                    dataset.loc[data_counter] = {'ASIN': ASIN, 'Cover': fs, 'AmzMin': min(results),
                                                 'AmzMax': max(results), 'AmzOrt': sum(results) / len(results),
                                                 'EbayMin': None, 'EbayMax': None, 'EbayOrt': None, 'Kar':None}
                    data_counter += 1
                except:
                    pass
            """YENİ SAYFAYA GEÇMEK İÇİN BURASI"""
            try:
                go_next_page=soupObject.find('li',attrs={'class':'a-last'}).a.get('href')
                go_next_page=main_url+go_next_page
                self.searchAmazon(driver, go_next_page, dataset, data_counter, main_url)
            except:
                pass

            return driver, dataset

        def searchEbay(self, driver, dataset):
            minlist = []
            maxlist = []
            ortlist = []
            for i in dataset['ASIN']:
                url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=' \
                      '{}&_sacat=0&rt=nc&LH_ItemCondition=3'.format(i)
                driver.get(url)
                ebay_soup = BeautifulSoup(driver.page_source, 'html.parser')
                new_books = ebay_soup.find_all('div', attrs={'class': 's-item__details clearfix'})
                fiyat_list = []
                for i in range(5):
                    try:
                        price = float(new_books[i].find('span', attrs={'class': 's-item__price'}).text[1:])
                        try:
                            ship = float(
                                new_books[i].find('span', attrs={'class': 's-item__shipping s-item__logisticsCost'})
                                    .text.split(" ")[0][2:])
                            price += ship
                        except:
                            pass
                        fiyat_list.append(price)
                    except:
                        pass
                try:
                    minlist.append(min(fiyat_list))
                    maxlist.append(max(fiyat_list))
                    ortlist.append(sum(fiyat_list) / len(fiyat_list))
                except:
                    minlist.append(float(0))
                    maxlist.append(float(0))
                    ortlist.append(float(0))

            dataset['EbayMin'] = minlist
            dataset['EbayMax'] = maxlist
            dataset['EbayOrt'] = ortlist
            driver.quit()
            return dataset

        def writeOutput(self, dataset, price):
            counter=1
            path = r'C:\Users\daimo\OneDrive\Masaüstü'
            wb = ex.Workbook('{}\sonucla1r.xlsx'.format(path))
            page1 = wb.add_worksheet('Page1')
            page1.write(0, 0, "ASIN")
            page1.write(0, 1, "Cover")
            page1.write(0, 2, "AmzMin")
            page1.write(0, 3, "AmzMax")
            page1.write(0, 4, "AmzOrt")
            page1.write(0, 5, "EbayMin")
            page1.write(0, 6, "EbayMax")
            page1.write(0, 7, "EbayOrt")
            page1.write(0, 8, "NetKar")
            for i in dataset.values:
                if(i[8]>price):
                    page1.write(counter, 0, i[0])
                    page1.write(counter, 1, i[1])
                    page1.write(counter, 2, i[2])
                    page1.write(counter, 3, i[3])
                    page1.write(counter, 4, i[4])
                    page1.write(counter, 5, i[5])
                    page1.write(counter, 6, i[6])
                    page1.write(counter, 7, i[7])
                    page1.write(counter, 8, i[8])
                    counter+=1
            wb.close()

        def kar_hesap(self, dataset):
            """kar=AmzFiyat-RefFee-Vcf-Shipping-Alış-DepoKira"""
            kar_list=[]
            for i in dataset.values:
                kar=i[4]-0.15*i[4]-float(1.8)-float(3)-i[5]-float(1)
                kar_list.append(kar)
            dataset['Kar']=kar_list
            return dataset

    islem = functions()
    main_url = 'https://www.amazon.com'
    results = {'ASIN': [],
                'Cover': [],
                'AmzMin': [],
                'AmzMax': [],
                'AmzOrt': [],
                'EbayMin': [],
                'EbayMax': [],
                'EbayOrt': [],
                'Kar':[]}
    dataset = pd.DataFrame(results, columns=['ASIN', 'Cover', 'AmzMin', 'AmzMax',
                                              'AmzOrt', 'EbayMin', 'EbayMax', 'EbayOrt', 'Kar'])
    data_counter = 0
    driver=webdriver.Chrome()
    driver.get(main_url)
    driver,dataset=islem.searchAmazon(driver, URL, dataset, data_counter, main_url)
    dataset=islem.searchEbay(driver, dataset)
    dataset=islem.kar_hesap(dataset)
    islem.writeOutput(dataset, price)
###########################################
"""URL = 'https://www.amazon.com/s?me=A3TDR7PXU58ECM&marketplaceID=ATVPDKIKX0DER'
price=float(1)
searchProduct(URL, price)"""

