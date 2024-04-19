from django.shortcuts import render
from django.http import HttpResponse,FileResponse
import json
import mysql.connector
import pymysql
import hashlib
# Create your views here.

#使用配置方式连接数据库
config={
    "host" : "127.0.0.1",
    "port" : 3306,
    "user" : "root",
    "password" : "root",
    "database" : "HNcoal"
}

# 数据库连接
def connect():
    '''连接MySQL数据库'''
    try:
        db = pymysql.connect(**config)
        return db
    except Exception:
        raise Exception("数据库连接失败")
    


# 根据角色ID获取角色名称
def findRoleById(conn,id):
    try:
        role_name=None
        cursor = conn.cursor()
        sql = "select * from role where id= %s"
        cursor.execute(sql, (id,))
        result = cursor.fetchone()
        if result is not None:
            role_name = result[1]     
        return role_name
    except Exception :
        print("查询失败")  
    finally:
         cursor.close()  

# 根据角色ID获取角色类别
def findRoleTypeById(conn,id):
    """
    return 
        0: 总公司
        1：分公司
        2：煤矿

    """
    try:
        role_type=None
        cursor = conn.cursor()
        sql = "select * from role where id= %s"
        cursor.execute(sql, (id,))
        result = cursor.fetchone()
        if result is not None:
            role_type = result[2]     
        return role_type
    except Exception :
        print("查询失败")  
    finally:
         cursor.close()  

def login(request):
    if request.method=='POST':
        postbody=request.body
        param=json.loads(postbody.decode())
        username=param['username']
        password=param['password']

        # 获取

        #---测试---
        # username = request.POST.get('username')
        # password = request.POST.get('password')
        #---------
        print("用户名：%s,密码：%s",(username,password))
        # return HttpResponse('登陆成功')
        conn = connect()
        cursor = conn.cursor()
        
        salt_sql = "select password,salt from user_2 where name= %s"

        sql = "select * from user_2 where name= %s and password=%s"
        tooken={
                'status':0,
                'message':'数据库连接错误',
                'role':''
                    }
                
        try:
            cursor.execute(salt_sql, (username))
            result = cursor.fetchone()

            if result is None:
                tooken={
                'status':10001,
                'message':'用户名或密码错误',
                'role':''
                    }
                print("用户名或密码错误！")
            else:
                salt = result[1]
                md5 = hashlib.md5()
                # 更新md5对象中的字符串
                md5.update((password + salt).encode("utf-8"))
                # 获取十六进制表示的结果
                password = md5.hexdigest()

            cursor.execute(sql, (username, password)) 
            # 使用 fetchone() 方法获取单条数据.
            result = cursor.fetchone()
            if result is None:
                tooken={
                'status':10001,
                'message':'用户名或密码错误',
                'role':''
                    }
                print("用户名或密码错误！")
            else:
                user_right = result[4]   # 员工：0   管理员：1
                role_id = result[2]
                role_name = findRoleById(conn=conn,id=role_id)
                role_type = findRoleTypeById(conn=conn,id=role_id)
                print("========user==========")
                print(role_name)

                # 保存登录信息
                request.session['is_login'] = True
                request.session['user_name'] = username
                request.session['role_name'] = role_name
                request.session['role_type'] = role_type
                request.session['user_right'] = user_right
                tooken={
                    'status':10000,
                    'message':'登陆成功',
                    'role':role_name,
                    'right':user_right
                    }
        except Exception :
            print("查询失败")
        finally:
            cursor.close()
            conn.close()
        return HttpResponse(json.dumps(tooken,ensure_ascii=False))

# def login(request):
#     if request.method=='POST':
#         postbody=request.body
#         param=json.loads(postbody.decode())
#         username=param['username']
#         password=param['password']

#         #---测试---
#         # username = request.POST.get('username')
#         # password = request.POST.get('password')
#         #---------
#         print("用户名：%s,密码：%s",(username,password))
#         # return HttpResponse('登陆成功')
#         conn = connect()
#         cursor = conn.cursor()
#         sql = "select * from user where name= %s and password=%s"
#         tooken={
#                 'status':0,
#                 'message':'数据库连接错误',
#                 'role':''
#                     }
                
#         try:
#             cursor.execute(sql, (username, password)) 
#             # 使用 fetchone() 方法获取单条数据.
#             result = cursor.fetchone()
#             if result is None:
#                 tooken={
#                 'status':10001,
#                 'message':'用户名或密码错误',
#                 'role':''
#                     }
#                 print("用户名或密码错误！")
#             else:
#                 role_id = result[2]
#                 role_name = findRoleById(conn=conn,id=role_id)
#                 role_type = findRoleTypeById(conn=conn,id=role_id)
#                 print("========user==========")
#                 print(role_name)

#                 # 保存登录信息
#                 request.session['is_login'] = True
#                 request.session['user_name'] = username
#                 request.session['role_name'] = role_name
#                 request.session['role_type'] = role_type
#                 tooken={
#                     'status':10000,
#                     'message':'登陆成功',
#                     'role':role_name
#                     }
#         except Exception :
#             print("查询失败")
#         finally:
#             cursor.close()
#             conn.close()
#         return HttpResponse(json.dumps(tooken,ensure_ascii=False))
