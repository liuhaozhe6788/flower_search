import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='lfd6788',
    database='flower_data'
)

mycursor = mydb.cursor(buffered=True)
mycursor.execute("create table if not exists flower_imgs (img_url varchar(255) primary key, \
                 result int unsigned, vector text) ")
mycursor.execute("alter table flower_imgs modify result int unsigned")
mycursor.execute("show tables")
mysql = "insert into flower_imgs (img_url, result) values (%s, %s)"
val = [
    ('https://www.680news.com/wp-content/blogs.dir/sites/2/2014/01/rose.jpg.jpg', 0),
    ('https://t3.ftcdn.net/jpg/01/05/57/38/360_F_105573812_cvD4P5jo6tMPhZULX324qUYFbNpXlisD.jpg', 0)]
mycursor.executemany(mysql, val)

mycursor.execute("select * from flower_imgs")
flower_data = mycursor.fetchall()

print(flower_data)

mydb.close()
