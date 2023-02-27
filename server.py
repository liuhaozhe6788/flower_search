from PIL import Image
import os
import send2trash
import numpy as np
from datetime import datetime
from flask import Flask, request, render_template

from flower_scraper import train_size, num_imgs_per_class, num_class
from database import myPassword, myDatabase_name, myTables_name, Database, flowers_demapper
from feature_extractor import FeatureExtractor

app = Flask(__name__)

# 从数据库读取所有的特征向量
mydatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
features_array = mydatabase.select_all_train_features(myTables_name[0])
mydatabase.close()

fe = FeatureExtractor()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 删除历史图片
        entries = os.listdir('./static/uploaded')
        if len(entries) > 10:
            send2trash.send2trash(f'./static/uploaded/{entries[0]}')
        file = request.files["query_img"]

        # 保存上传的图片
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = "./static/uploaded/" + \
                            datetime.now().isoformat().replace(":", ".") + "_" + file.filename  # create img path
        img.save(uploaded_img_path)

        # 运行搜索
        query = fe.extract(img=img)  # feature extract of uploaded img
        # dists = (features_array@query.T)/(np.linalg.norm(features_array, axis=1) * np.linalg.norm(features_array))
        dists = np.sum(np.abs(features_array - query), axis=1)  # calc Manhattan distance
        # dists = np.linalg.norm(features_array - query, axis=1)  # calc L2 distance
        # print(len(dists))
        ids = np.argsort(dists)[0: 20]  # sort dists return ids
        # print(ids)

        # 统计每种花卉出现的频率
        freq = np.zeros(num_class)
        mydatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
        for _id in ids:
            freq[int(mydatabase.select_result(myTables_name[0], _id + 1)) - 1] += 1
        print(freq)
        mydatabase.close()

        # 将频率最高的花卉名称作为识别结果
        result_id = np.argmax(freq)
        result = flowers_demapper[result_id + 1]
        # print(f"the flower is {result}")

        # 从数据库中读取URL，获得该种类花卉的图片
        mydatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
        # print(mydatabase.select_all_imgs_of_a_class(myTables_name[0], 1)[2][0])
        # scores = [mydatabase.select_url(myTables_name[0], id) for id in ids]
        scores = []
        for _i in range(min(num_imgs_per_class, 20)):
            scores.append(mydatabase.select_all_imgs_of_a_class(myTables_name[0], result_id + 1)[_i][0])
        mydatabase.close()
        # print(scores)

        return render_template("index.html", query_path=uploaded_img_path, variable=result, scores=scores)
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run()
