from PIL import Image
import requests
from io import BytesIO
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import logging
requests.packages.urllib3.util.connection.HAS_IPV6 = False
from flower_scraper import train_size, val_size, test_size
from database import myPassword, myDatabase_name, myTables_name, Database
from log_setup import setup_logging

from feature_extractor import FeatureExtractor

def extract_features(logger):
    fe = FeatureExtractor()
    train_batch_size = 1
    val_batch_size = 1
    mydatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    # 以batch为单位从图片中提取出特征向量
    for table in myTables_name:
        batch_size = train_batch_size if table == 'train_imgs' else val_batch_size

        if table == 'train_imgs':
            data_size = train_size 
        elif table == 'val_imgs':
            data_size = val_size
        else:
            data_size = test_size

        total_steps = int(data_size/batch_size)
        logger.info(f"table name: {table}")
        for step in range(total_steps):
            logger.info(f"step: {step}")
            try: 
                iter_ids = [str(id) for id in list(range(step* batch_size + 1, (step + 1)* batch_size + 1))]
                # 从数据库取出图片的url
                img_urls = mydatabase.select_urls(table, iter_ids)

                imgs = []
                # 根据图片的url读取图片数据，提取图片的特征向量
                for url in img_urls:
                    # logger.info(f"URl: {url}")
                    response = requests.get(url, headers=headers, timeout=30, stream=True)
                    imgs.append(Image.open(BytesIO(response.content)))
                features = fe.extract(imgs)

                # 保存特征向量到数据库
                mydatabase.insert_features(table, features, iter_ids)
            except Exception:
                logger.info("Unable to show link")   

    mydatabase.close()


if __name__ == "__main__":
    setup_logging(log_name="offline_extract")
    logger = logging.getLogger(__name__)
    extract_features(logger)
