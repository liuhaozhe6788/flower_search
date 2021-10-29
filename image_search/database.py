import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='lfd6788',
    database='flower_data'
)

mycursor = mydb.cursor()
mycursor.execute("create table if not exists flower_imgs (id int auto_increment primary key, img_url varchar(255), \
                 result tinyint unsigned, vector text) ")
mycursor.execute("alter table flower_imgs modify result tinyint unsigned")
mycursor.execute("show tables")
for x in mycursor:
    print(x)

mycursor.execute("describe flower_imgs")
flower_data = mycursor.fetchall()

print(flower_data)

mydb.close()