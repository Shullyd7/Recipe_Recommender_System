from icrawler.builtin import BingImageCrawler

from threading import Thread

number=100

def negative():
    classes2=['trees','Human faces','road signs']
    for c2 in classes2:
        bing_crawler=BingImageCrawler(storage={'root_dir':f'n/'}) 
        bing_crawler.crawl(keyword=c2,filters=None,max_num=number,offset=0)       

t = Thread(target=negative).start()

def positive():
    classes=[
        'SUV','rav4','ford explorer',
        'jeep grand cherokee','toyota highlander',
        'Hyundai Tucson',
        ]
    
    for c2 in classes:
        bing_crawler=BingImageCrawler(storage={'root_dir':f'suv/'}) 
        bing_crawler.crawl(keyword=c2,filters=None,max_num=number,offset=0)       

t = Thread(target=positive).start()

