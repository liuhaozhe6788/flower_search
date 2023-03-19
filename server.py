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
train_features = mydatabase.select_all_train_features(myTables_name[0])
train_idx, train_features = list(zip(*train_features))
train_features = np.array(list(train_features), dtype=float)
mydatabase.close()

NUM_OF_NEIGHBORS = 19

fe = FeatureExtractor()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 删除历史图片
        if not os.path.exists('./static/uploaded'):
            os.mkdir('./static/uploaded')
        entries = os.listdir('./static/uploaded')
        if len(entries) > 10:
            send2trash.send2trash(f'./static/uploaded/{entries[0]}')
        file = request.files["query_img"]

        # 保存上传的图片
        try:
            img = Image.open(file.stream)  # PIL image
            uploaded_img_path = "./static/uploaded/" + \
                                datetime.now().isoformat().replace(":", ".") + "_" + file.filename  # create img path
            img.save(uploaded_img_path)

            # 运行搜索
            query = fe.extract(imgs=[img])[0]  # feature extract of uploaded img
            # dists = (train_features@query.T)/(np.linalg.norm(train_features, axis=1) * np.linalg.norm(train_features))
            dists = np.sum(np.abs(train_features - query), axis=1)  # calc Manhattan distance
            # dists = np.linalg.norm(train_features - query, axis=1)  # calc L2 distance
            print(len(dists))
            ids = np.argsort(dists)[0: NUM_OF_NEIGHBORS]  # sort dists return ids
            # print(ids)

            # 统计每种花卉出现的频率
            freq = np.zeros(num_class)
            mydatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
            for id in ids:
                freq[int(mydatabase.select_result(myTables_name[0], train_idx[id])) - 1] += 1
            print(freq)
            mydatabase.close()

            # 将频率最高的花卉名称作为识别结果
            result_id = np.argmax(freq)
            result = flowers_demapper[result_id + 1]
            print(f"the flower is {result}")

            # 从数据库中读取URL，获得该种类花卉的图片
            mydatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
            # print(mydatabase.select_all_imgs_of_a_class(myTables_name[0], 1)[2][0])
            # scores = [mydatabase.select_url(myTables_name[0], id) for id in ids]
            scores = []
            imgs_of_a_class = mydatabase.select_all_imgs_of_a_class(myTables_name[0], result_id + 1)
            for i in range(min(num_imgs_per_class, NUM_OF_NEIGHBORS)):
                url, feature = imgs_of_a_class[i]
                dist = np.linalg.norm(np.array(eval(feature), dtype=float) - query, axis=0)  # calc L2 distance
                scores.append((url, dist))
            mydatabase.close()
            # print(scores)

            return render_template("index.html", query_path=uploaded_img_path, variable=result, scores=scores)
        except Exception as e:
            print("Caught exception: %s" % repr(e))
            print("Restarting\n")
            return render_template("index.html")
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run()
