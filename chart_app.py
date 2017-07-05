# -*- coding:utf-8 -*-
import tornado.web
import tornado.ioloop
import tornado.websocket
import os
import base64,uuid
import pymongo

from tornado.options import define, options,parse_command_line

# 路由处理基类，用于获取当前用户名
class Basehandler(tornado.web.RequestHandler):
    def get_current_user(self):
        self.get_secure_cookie("username")

#个人主页路由，显示个人信息，如果未登录需要跳转到登录页
class homepage(Basehandler):
    # @tornado.web.authenticated
    def get(self):
        # self.render('homepage.html',self.current_user)
        self.render('homepage.html')
#登录输入路由
class signin(Basehandler):
    #get请求则直接反馈登录页面
    def get(self):
        self.render('signin.html')
    #若post请求则判断表单数据有效性，有效则存入cookie，无效则重定向道login页面
    def post(self):
        username=self.get_argument('username')
        password=self.get_argument('password')
        if  username and password:          #username,password 不为空
            if not self.application.db.user.find_one({'username':username}):        #username在数据库中不存在
                self.application.db.user.insert({'username':username,'password':password})
                self.set_secure_cookie("username",username)
                self.redirect('/homepage')
            else:
                self.redirect('/signin')  #  是否可以通过jquery来post，决定是否需要重新载入页面
        else:
            self.redirect( '/signin' )
#登出路由
class logout(Basehandler):
    def get(self, *args, **kwargs):
        self.clear_cookie("username")
        self.redirect('/login')
#注册路由，用于用户注册
class login(Basehandler):
    def get(self, *args, **kwargs):
        self.render('login.html')
    def post(self):
        username=self.get_argument("username")
        password=self.get_argument("password")
        if username and password:
            user=passself.application.db.user.find_one['username']
            if user:
                if user['password']==password:
                    self.set_secure_cookie("username",username)
                    self.redirect('/homepage')
                else:
                    self.write("用户名或者密码错误")
            else:
                self.write( "用户名或者密码错误" )
        else:
            self.write( "用户名或者密码错误" )
#用户更改个人信息的路由
class edit_info(Basehandler):
    pass
#用于用户聊天，建立websocket进行实时通信
class chart_websocket(Basehandler,tornado.websocket.WebSocketHandler):
    pass



# application类继承tornado.web.Application,用来设置handlers和settings，然后以此为参数，调用父类的Application类的init来生成app
class application(tornado.web.Application):
    def __init__(self):
        handlers=[('/',homepage),
                  ('/login',login),
                  ('/logout',logout),
                  ('/signin',signin),
                  ('/chart',chart_websocket),
                  ('/edit_info',edit_info),
                  ]
        settings={'template_path':os.path.join(os.path.dirname(__file__),'template'),
                  'static_path':os.path.join(os.path.dirname(__file__),'static'),
                  'debug':True,
                  'cookie_secret':base64.b64encode(uuid.uuid4().bytes+uuid.uuid4().bytes),
                  'xsrf_cookies':True,
                  'login_url':'/login'
                  }
        self.db=pymongo.MongoClient('mongodb://localhost:27017/').chart_app
        tornado.web.Application.__init__(self,handlers,**settings)

if __name__=="__main__":
    # 设置命令行参数
    define( "port", default=8000, help="the app will run at the given port", type=int )
    # 解析命令行
    parse_command_line()
    app=application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()