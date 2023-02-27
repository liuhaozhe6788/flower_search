from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np

from flower_scraper import train_size, num_imgs_per_class, num_class
from database import myPassword, myDatabase_name, myTables_name, Database, flowers_demapper
from feature_extractor import FeatureExtractor

# 运行搜索
fe = FeatureExtractor()

# 从数据库读取所有的特征向量
mydatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
train_features = mydatabase.select_all_train_features(myTables_name[0])

# TODO:根据不同的近邻个数求出验证集的分类准确率
correct_num = 0
total_num = 0
start = 10
end = 20
lens = end - start
accu = np.zeros(lens)

for _iter in range(lens):
    val_xy_data = mydatabase.select_xy_from_a_table(myTables_name[1])
    for value in val_xy_data:
        total_num += 1
        query, label = value[0], value[1]
        # dists = (features_array@query.T)/(np.linalg.norm(features_array, axis=1) * np.linalg.norm(features_array))
        dists = np.sum(np.abs(train_features - query), axis=1)  # calc Manhattan distance
        # dists = np.linalg.norm(features_array - query, axis=1)  # calc L2 distance
        # print(len(dists))

        ids = np.argsort(dists)[0: _iter + start]  # sort dists return ids
        # print(ids)

        # 统计每种花卉出现的频率
        freq = np.zeros(num_class)
        for _id in ids:
            freq[int(mydatabase.select_result(myTables_name[0], _id + 1)) - 1] += 1
        # print(freq)

        # 将频率最高的花卉名称作为识别结果
        result_id = np.argmax(freq)+1
        if result_id == label:
            correct_num += 1
    print(correct_num)
    print(total_num)
    print(f"精确率为{correct_num/total_num}%")
    accu[_iter] = correct_num/total_num
    correct_num = total_num = 0

x = np.arange(start, end)
plt.xlabel("num of neighbors selected/*5")
plt.ylabel("accuracy")
plt.plot(x, accu)
plt.show()
plt.savefig("val_res/accu.png", dpi=500)

mydatabase.close()






