import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from flower_scraper import num_class
from database import myPassword, myDatabase_name, myTables_name, Database


def calc_accu(data, train_features, train_idx, num_of_neighbors):
    correct_num = total_num = 0
    for value in tqdm(data):
        total_num += 1
        query, label = np.array(value[0]), value[1]
        # dists = (features_array@query.T)/(np.linalg.norm(features_array, axis=1) * np.linalg.norm(features_array))
        dists = np.sum(np.abs(train_features - query), axis=1)  # calc Manhattan distance
        # dists = np.linalg.norm(features_array - query, axis=1)  # calc L2 distance
        # print(len(dists))

        ids = np.argsort(dists)[0: num_of_neighbors]  # sort dists return ids
        # print(ids)

        # 统计每种花卉出现的频率
        freq = np.zeros(num_class)
        for id in ids:
            freq[int(mydatabase.select_result(myTables_name[0], train_idx[id])) - 1] += 1  

        # 将频率最高的花卉名称作为识别结果
        result_id = np.argmax(freq)+1
        if result_id == label:
            correct_num += 1
    return correct_num/total_num
    
def validate(neighbor_range):
    start, end = neighbor_range[0], neighbor_range[1]

    # 根据不同的近邻个数求出验证集的分类准确率
    lens = end - start
    accus = np.zeros(lens)

    for iter in tqdm(range(lens)):
        val_xy_data = mydatabase.select_xy_from_a_table(myTables_name[1]) 
        accu = calc_accu(val_xy_data, train_features, train_idx, iter + start)

        print(f"近邻个数为{iter+start}时，验证集的精确率为{accu}%")
        accus[iter] = accu

    x = np.arange(start, end)
    plt.xlabel("num of neighbors selected/*5")
    plt.ylabel("accuracy")
    plt.plot(x, accus)
    # plt.show()
    plt.savefig("val_res/accu.png", dpi=500)

    return np.argmax(accus) + start

def test(num_of_neighbors):
    test_xy_data = mydatabase.select_xy_from_a_table(myTables_name[2]) 
    accu = calc_accu(test_xy_data, train_features, train_idx, num_of_neighbors)
    print(f"测试集的准确率为{accu}%")

if __name__ == "__main__":
    start = 15
    end = 30
    # 从数据库读取训练集中所有的特征向量
    mydatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
    train_features = mydatabase.select_all_train_features(myTables_name[0])  
    train_idx, train_features = list(zip(*train_features))
    train_features = np.array(train_features, dtype=object)
    num_of_neighbors = validate((start, end))
    test(num_of_neighbors)
    mydatabase.close()






