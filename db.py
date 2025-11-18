import mysql.connector

def conectar():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="senha",
    database="locadora",
    auth_plugin="mysql_native_password"
    )