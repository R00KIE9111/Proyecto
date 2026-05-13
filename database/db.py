import pymysql

conexion = pymysql.connect(
    host='flask-db.c7saowikmas3.us-east-1.rds.amazonaws.com',
    user='admin',
    password='Inacap.2026',
    database='gestorecommerce',
    cursorclass=pymysql.cursors.DictCursor
)