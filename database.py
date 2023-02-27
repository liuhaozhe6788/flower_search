import mysql.connector
import numpy as np
from tabulate import tabulate


# 预先在mysql上设置好密码，并建立数据库"create database flower_data"
# 和表格"""
myPassword = '12345678'
myDatabase_name = 'flower_data'
myTables_name = ['train_imgs', 'val_imgs', 'test_imgs']  

flowers_demapper = {
    1: '向日葵',
    2: '梅花',
    3: '牡丹',
    4: '兰花',
    5: '桂花',
    6: '水仙花',
    7: '玫瑰',
    8: '菊花',
    9: '凤仙花',
    10: '郁金香',
    11: '马蹄莲',
    12: '蝴蝶兰',
    13: '扶桑花',
    14: '山茶花',
    15: '栀子花',
    16: '杜鹃花',
    17: '灯笼花',
    18: '玉兰花',
}

class Database:

    def __init__(self, mypassword, database_name=None, tables_name=[]):
        """
        私有变量初始化，建立MySQL的连接，并建立cursor
        :param mypassword: 访问MySQL的密码
        :param database_name: 数据库的名称
        :param tables_name: 该数据库中所有表格的名称
        """
        self._password = mypassword
        self._mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password=self._password
        )
        self._mycursor = self._mydb.cursor(buffered=True)
        self._database_name = database_name
        self._mycursor.execute(f"create database if not exists {database_name}")
        self._mycursor.execute(f"use {database_name}")
        self._mycursor.execute("show databases")
        self._databases_list = [x for x in self._mycursor]
        self._tables = tables_name
        self._tables_list_in_database = []
        # print("database class initialized")

    def close(self):
        """
        断开MySQL连接
        :return:
        """
        self._mycursor.close()
        self._mydb.close()

    def create_table(self, table_name: str):
        """
        创建表格
        :param table_name: 表格名称
        :return:
        """
        self._mycursor.execute(f"create table if not exists {table_name} (id int not null auto_increment, img_url varchar(255), \
                         result int unsigned, feature longtext not null, primary key (id))")
        self._mydb.commit()
        self._mycursor.execute("show tables")
        self._tables_list_in_database = [x for x in self._mycursor]

    def insert_img_info_single(self, table_name: str, val: tuple):
        """
        插入一行信息
        :param table_name: 表格名称
        :param val: 一行信息
        :return:
        """
        sql = f"insert into {table_name} (img_url, result, feature) values (%s, %s, %s)"
        self._mycursor.execute(sql, val)
        self._mydb.commit()
    
    def insert_img_info_multiple(self, table_name: str, vals: list):
        """
        插入多行信息
        :param table_name: 表格名称
        :param vals: 多行信息
        :return:
        """
        for val in vals:
            self.insert_img_info_single(table_name, val)

    def insert_feature(self, table_name: str, vector: np.ndarray, iter_id: int):
        """
        插入一张图片的特征向量
        :param table_name: 表格名称
        :param vector: 特征向量
        :param iter_id: 插入行的位置
        :return:
        """
        sql = f"update {table_name} set feature = %s where id = {iter_id}"
        val = str(vector.tolist())
        self._mycursor.execute(sql, (val, ))
        self._mydb.commit()

    def insert_features(self, table_name: str, vectors: np.ndarray, iter_ids: list):
        """
        插入多张图片的特征向量
        :param table_name: 表格名称
        :param vectors: 特征向量
        :param iter_ids: 插入行的位置
        :return:
        """
        for i in range(len(vectors)):
            self.insert_feature(table_name, vectors[i], iter_ids[i])

    def select_url(self, table_name: str, iter_id: int) -> str:
        """
        选择一张图片的URl信息
        :param table_name:表格名称
        :param iter_id: 选择行的位置
        :return:URL信息
        """
        self._mycursor.execute(f"select img_url from {table_name} where id = {iter_id}")
        return self._mycursor.fetchone()[0]

    def select_urls(self, table_name: str, ids: list) -> str:
        """
        选择多张图片的URl信息
        :param table_name:表格名称
        :param ids: 选择多行的位置
        :return:多行URL信息
        """
        self._mycursor.execute(f"select img_url from {table_name} where id in({','.join(ids)})")
        return [line[0] for line in self._mycursor.fetchall()]
    
    def select_result(self, table_name: str, iter_id: int) -> str:
        """
        选择一张图片的result信息
        :param table_name: 表格名称
        :param iter_id: 选择行的位置
        :return: 花卉种类结果
        """
        self._mycursor.execute(f"select result from {table_name} where id = {iter_id}")
        return self._mycursor.fetchone()[0]

    def select_all_train_features(self, table_name: str) -> list:
        """
        选择所有训练集图片的特征向量
        :param table_name: 表格名称
        :return: 所有特征向量
        """
        self._mycursor.execute(f"select feature from {table_name}")
        features = self._mycursor.fetchall()

        # 将所有特征向量转换为二维numpy序列
        features_array = []
        for fe in features:  
            features_array.append(eval(fe[0]))
        return np.array(features_array)

    def select_xy_from_a_table(self, table_name: str) -> list:
        """
        选择某个表格中的特征x与标签y
        :param table_name: 表格名称
        :return: 所有特征向量
        """
        self._mycursor.execute(f"select feature, result from {table_name}")
        data = self._mycursor.fetchall()

        return [[eval(val[0]), val[1]] for val in data]
    
    def select_all_imgs_of_a_class(self, table_name: str, flower_class: int) -> list:
        """
        选择某种花卉的所有图片
        :param table_name: 表格名称
        :param flower_class: 花卉的种类
        :return: 某种花卉的所有图片URL
        """
        self._mycursor.execute(f"select img_url from {table_name} where result = {flower_class}")
        return self._mycursor.fetchall()

    def data(self, table_name: str, table_headers: list) -> str:
        """
        打印某张表的所有数据
        :param table_name: 表格名称
        :param table_headers: 表头
        :return: 表格数据
        """
        import copy
        self._mycursor.execute(f"select * from {table_name}")
        results = self._mycursor.fetchall()
        return copy.deepcopy(str(tabulate(results, headers=table_headers, tablefmt='psql')))

    @property
    def databases(self) -> str:
        """
        获得所有数据库的名称
        :return: 所有数据库的名称
        """
        import copy
        return copy.deepcopy(str(self._databases_list))

    @property
    def tables(self) -> str:
        """
        获得本数据库flower_data的所有表格的名称
        :return: 本数据库flower_data的所有表格的名称
        """
        import copy
        return copy.deepcopy(str(self._tables_list_in_database))


if __name__ == "__main__":
    newDatabase = Database(mypassword=myPassword, database_name=myDatabase_name, tables_name=myTables_name)
    newDatabase.create_table(myTables_name[0])
    print(newDatabase.databases)
    print(newDatabase.tables)
    newVal = ('https://www.680news.com/wp-content/blogs.dir/sites/2/2014/01/rose.jpg.jpg', 0, '*')
    newDatabase.insert_img_info_single(myTables_name[0], newVal)
    newVal = ('https://m.media-amazon.com/images/I/61WBuAzMmZL._AC_SX425_.jpg', 1, '*')
    newDatabase.insert_img_info_single(myTables_name[0], newVal)
    newVal = ('https://hosstools.com/wp-content/uploads/2020/10/black-oil-sunflower.jpg', 2, '*')
    newDatabase.insert_img_info_single(myTables_name[0], newVal)
    newVal = ('https://gilmour.com/wp-content/uploads/2019/05/Jasmine-Care.jpg', 3, '*')
    newDatabase.insert_img_info_single(myTables_name[0], newVal)
    newVal = ('https://www.gardeningknowhow.com/wp-content/uploads/2020/11/chrysanthemum-flower.jpg', 4, '*')
    newDatabase.insert_img_info_single(myTables_name[0], newVal)
    newDatabase.insert_feature(myTables_name[0], np.array([1, 2, 3, 4]), 0)
    print(newDatabase.data(myTables_name[0], ['img_id', 'img_url', 'flower_class', 'img_vector']))
    print(newDatabase.select_url(myTables_name[0], 1))
    print(newDatabase.select_result(myTables_name[0], 4))
    newDatabase.close()

