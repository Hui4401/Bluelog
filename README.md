# Bluelog

> 《[Flask Web 开发实战](http://helloflask.com/book)》中的实战程序，做了一些修改。

[![atFUAg.png](https://s1.ax1x.com/2020/08/02/atFUAg.png)](https://imgchr.com/i/atFUAg)

## 如何使用

- clone项目到本地
- `pip install -r requirements.txt`安装依赖
- `flask init`输入用户名，密码进行博客初始化

到这里一个空的博客程序已经初始化完成了，可以用`flask run`运行，另外如果想查看充满内容的博客效果，可以用`flask forge`生成随机数据，生成的管理员账户密码均为 **admin** （会覆盖之前的初始化用户信息）。此外，博客的邮件系统需要私人smtp账户信息，想要使用完整的邮件功能，还需要如下操作：

- 在根目录下创建一个 **.env** 文件，写入如下信息：
```
# 程序秘钥，一个随机字符串
SECRET_KEY = assassin

# 自己的smtp账户信息
MAIL_SERVER = smtp服务器地址
MAIL_USERNAME = 自己的smtp账号
MAIL_PASSWORD = 密码
```
- 运行博客程序后打开主页，登录管理员账户后进入设置，补全自己用来接收通知的邮箱（不能和上面的smtp邮箱一样，那个是用来发送邮件的）
