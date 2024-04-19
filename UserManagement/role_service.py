from django.shortcuts import render
from django.http import HttpResponse,FileResponse
import json
import mysql.connector
import pymysql
# Create your views here.

#使用配置方式连接数据库
config={
    "host" : "127.0.0.1",
    "port" : 3306,
    "user" : "root",
    "password" : "root",
    "database" : "HNcoal"

}



# 根据角色名称获取角色类别
def findRoleTypeByName(role_name):
    """
    return 
        0: 总公司
        1：分公司
        2：煤矿

    """
    # 数据库连接
    def connect():
        '''连接MySQL数据库'''
        try:
            db = pymysql.connect(**config)
            return db
        except Exception:
            raise Exception("数据库连接失败")
    conn = connect()
    try:
        role_type=None
        cursor = conn.cursor()
        sql = "select * from role where name= %s"
        cursor.execute(sql, (role_name,))
        result = cursor.fetchone()
        if result is not None:
            role_type = result[2]     
        return role_type
    except Exception :
        print("查询失败")  
    finally:
         cursor.close()  

# 根据角色名称获取角色权限
def findPermissionByName(role_name):

    # 数据库连接
    def connect():
        '''连接MySQL数据库'''
        try:
            db = pymysql.connect(**config)
            return db
        except Exception:
            raise Exception("数据库连接失败")
        
    permission=None
    conn = connect()
    try:
        cursor = conn.cursor()
        sql = "select * from role where name= %s"
        cursor.execute(sql, (role_name,))
        result = cursor.fetchone()
        if result is not None:
            permission = result[3]
            permission = permission.split('、')
        print(permission)

        return permission
    except Exception :
        print("查询失败")
    finally:
         cursor.close()
         conn.close()
    