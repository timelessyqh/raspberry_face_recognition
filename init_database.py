from manage_face import connect_sqlite,disconnect_sqlite
print('began to create database and table')
conn,cursor=connect_sqlite()
cursor.execute('create table people_facetoken (id INTEGER PRIMARY key AUTOINCREMENT, name varchar(20), number varchar(20),class varchar(20),facetoken varchar(50),time datetime)')
cursor.execute('create table attend_log (id INTEGER PRIMARY key AUTOINCREMENT, name varchar(20), number varchar(20),class varchar(20),time datetime)')
disconnect_sqlite(conn,cursor)
print('success')