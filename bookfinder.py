# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import xlwt
import xlsxwriter as ex
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import pandas as pd

def urun_ara(URL, price):
    class defs():
        def amazon_tarayici(self,driver, URL, dataset, data_counter, main_url):
            driver.get(URL)
            soup_object = BeautifulSoup(driver.page_source, 'html.parser')
            elemanlar = soup_object.find_all("div", {"data-component-type": "s-search-result"})
            for i in elemanlar:

                adres = i.find("a", "a-link-normal a-text-normal").get("href")
                adres = main_url + adres
                driver.get(adres)
                """ASIN BULMA"""
                try:
                    asin_parca = driver.find_element_by_xpath('//*[@id="detailBullets_feature_div"]/ul').text.split(
                        "\n")
                    for i in asin_parca:
                        if i[0:7] == 'ISBN-13':
                            A_SIN = i[10:13]
                            A_SIN1 = i[14:]
                            ASIN = A_SIN + A_SIN1
                except:
                    pass
                """ASIN BULMA BİTTİ"""
                eleman_soup = BeautifulSoup(driver.page_source, 'html.parser')
                try:
                    secili = eleman_soup.find("li", attrs={"class": "swatchElement selected"})
                    if secili == None:
                        secili = eleman_soup.find("li", attrs={"class": "swatchElement selected resizedSwatchElement"})
                except:
                    pass
                try:
                    """KİTAP TÜRÜNÜ BUL"""
                    fs = secili.find('span', attrs={"class": "a-button-inner"}).a.text
                    fs = fs.split("\n")[1]
                    new_linki = secili.find('span', 'olp-new olp-link').a.get("href")
                    new_linki = main_url + new_linki
                    driver.get(new_linki)
                    new_soup = BeautifulSoup(driver.page_source, "html.parser")
                    new_soup_prices = new_soup.find_all("div", attrs={"class": "a-row a-spacing-mini",
                                                                      "class": "a-row a-spacing-mini olpOffer"})
                    sonuclar = []
                    for t in new_soup_prices:
                        fiyat = float(
                            t.find('span', 'a-size-large a-color-price olpOfferPrice a-text-bold').text.strip()[1:])
                        try:
                            ship = float(t.find('span', attrs={"class": "olpShippingPrice"}).text[1:])
                            fiyat += ship
                        except:
                            pass
                        sonuclar.append(fiyat)
                    dataset.loc[data_counter] = {'ASIN': ASIN, 'Cover': fs, 'AmzMin': min(sonuclar),
                                                 'AmzMax': max(sonuclar), 'AmzOrt': sum(sonuclar) / len(sonuclar),
                                                 'EbayMin': None, 'EbayMax': None, 'EbayOrt': None, 'Kar':None}
                    data_counter += 1
                except:
                    pass
            """YENİ SAYFAYA GEÇMEK İÇİN BURASI"""
            try:
                go_next_page=soup_object.find('li',attrs={'class':'a-last'}).a.get('href')
                go_next_page=main_url+go_next_page
                self.amazon_tarayici(driver, go_next_page, dataset, data_counter, main_url)
            except:
                pass

            return driver, dataset

        def ebay_tarayici(self, driver, dataset):
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

        def sonuc_yaz(self, dataset, price):
            sıra_counter=1
            path = r'C:\Users\daimo\OneDrive\Masaüstü'
            wb = ex.Workbook('{}\sonucla1r.xlsx'.format(path))
            sf1 = wb.add_worksheet('Sayfa1')
            sf1.write(0, 0, "ASIN")
            sf1.write(0, 1, "Cover")
            sf1.write(0, 2, "AmzMin")
            sf1.write(0, 3, "AmzMax")
            sf1.write(0, 4, "AmzOrt")
            sf1.write(0, 5, "EbayMin")
            sf1.write(0, 6, "EbayMax")
            sf1.write(0, 7, "EbayOrt")
            sf1.write(0, 8, "NetKar")
            for i in dataset.values:
                if(i[8]>price):
                    sf1.write(sıra_counter, 0, i[0])
                    sf1.write(sıra_counter, 1, i[1])
                    sf1.write(sıra_counter, 2, i[2])
                    sf1.write(sıra_counter, 3, i[3])
                    sf1.write(sıra_counter, 4, i[4])
                    sf1.write(sıra_counter, 5, i[5])
                    sf1.write(sıra_counter, 6, i[6])
                    sf1.write(sıra_counter, 7, i[7])
                    sf1.write(sıra_counter, 8, i[8])
                    sıra_counter+=1
            wb.close()

        def kar_hesap(self, dataset):
            """kar=AmzFiyat-RefFee-Vcf-Shipping-Alış-DepoKira"""
            kar_list=[]
            for i in dataset.values:
                kar=i[4]-0.15*i[4]-float(1.8)-float(3)-i[5]-float(1)
                kar_list.append(kar)
            dataset['Kar']=kar_list
            return dataset

    islem = defs()
    main_url = 'https://www.amazon.com'
    sonuclar = {'ASIN': [],
                'Cover': [],
                'AmzMin': [],
                'AmzMax': [],
                'AmzOrt': [],
                'EbayMin': [],
                'EbayMax': [],
                'EbayOrt': [],
                'Kar':[]}
    dataset = pd.DataFrame(sonuclar, columns=['ASIN', 'Cover', 'AmzMin', 'AmzMax',
                                              'AmzOrt', 'EbayMin', 'EbayMax', 'EbayOrt', 'Kar'])
    data_counter = 0
    driver=webdriver.Chrome()
    driver.get(main_url)
    driver,dataset=islem.amazon_tarayici(driver, URL, dataset, data_counter, main_url)
    dataset=islem.ebay_tarayici(driver, dataset)
    dataset=islem.kar_hesap(dataset)
    islem.sonuc_yaz(dataset, price)
###########################################
"""URL = 'https://www.amazon.com/s?me=A3TDR7PXU58ECM&marketplaceID=ATVPDKIKX0DER'
price=float(1)
urun_ara(URL, price)"""

