import requests
from bs4 import BeautifulSoup
import xlwt
import logging
from sklearn.model_selection import train_test_split

import database
from image_scraper.GoogleImageScraper import GoogleImageScraper
from log_setup import setup_logging

num_class = 16
num_imgs_per_class = 400

test_ratio = 0.1
val_ratio = 1/9
data_size = num_class * num_imgs_per_class
train_size = data_size * (1-test_ratio) * (1-val_ratio)
val_size = data_size * (1-test_ratio) * val_ratio
test_size = data_size * test_ratio

def web_scraping(class_num, imgs_num):
    """
    网络爬虫
    :params
    class_num:花卉种类个数
    imgs_num:每种花卉的图片个数
    :return
    """
    # 网络花卉图片爬虫初始化
    webdriver_path = "webdriver/chromedriver"
    headless = True
    min_resolution=(0,0)
    max_resolution=(9999,9999)
    languages = [1, 2]  #1按中文搜索，2按英文搜索

    flowers_list = []
    with open('./static/txt/flowers_list.txt', 'r', encoding='utf-8') as file:
        for text in file.readlines():
            flowers_list.append(text[:-1].split(','))
    # work_book = xlwt.Workbook()
    # work_sheet = work_book.add_sheet('flowers_url')

    # 将图片信息存入一个excel表格和mySQL数据库中
    newDatabase = database.Database(mypassword=database.myPassword, database_name=database.myDatabase_name, tables_name=database.myTables_name)
    
    # 数据库创建新表格
    for table in database.myTables_name:
        newDatabase.create_table(table)

    # 爬取花卉图片
    for i in range(11, class_num):
        search_id = i+1
        search_key = flowers_list[i][languages[0]]
        logger.info(f"scraping flower name: {search_key}")

        image_scrapper = GoogleImageScraper(webdriver_path, int(imgs_num/2), search_key, headless, min_resolution, max_resolution, logger)
        X = []
        X = image_scrapper.find_image_urls(X) 

        search_key = flowers_list[i][languages[1]]
        logger.info(f"scraping flower name: {search_key}")
        image_scrapper = GoogleImageScraper(webdriver_path, int(imgs_num/2), search_key, headless, min_resolution, max_resolution, logger)   
        X = image_scrapper.find_image_urls(X)    
    
        # for j in range(imgs_num):
        #     # 将图片的URL（str）和种类结果（非负整数）存入excel表格中
        #     work_sheet.write(i * imgs_num + j, 0, image_urls[j][0])
        #     work_sheet.write(i * imgs_num + j, 1, flowers_list[i][2])
        y = [search_id] * imgs_num

        # 训练集，验证集和测试集划分
        X_train, X_test, y_train, _ = train_test_split(X, y, test_size=test_ratio, random_state=1)

        X_train, X_val, _, _ = train_test_split(X_train, y_train, test_size=val_ratio, random_state=1) # 1/9 x 0.9 = 0.1

        # 将训练集，验证集和测试集存储到数据库中的三个表格中
        trainVals = [(data, search_id, '*') for data in X_train]
        newDatabase.insert_img_info_multiple(database.myTables_name[0], trainVals)

        valVals = [(data, search_id, '*') for data in X_val]
        newDatabase.insert_img_info_multiple(database.myTables_name[1], valVals)

        testVals = [(data, search_id, '*') for data in X_test]
        newDatabase.insert_img_info_multiple(database.myTables_name[2], testVals)
    # work_book.save('./data/flowers_url.xls')
    newDatabase.close()

if __name__ == "__main__":
    setup_logging(log_name="image_scraper")
    logger = logging.getLogger(__name__)
    web_scraping(num_class, num_imgs_per_class)
