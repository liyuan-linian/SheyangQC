import os

from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.secret_key = '11223344'

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = 'tb_user'
    id = db.Column(db.Integer, primary_key=True, comment='ID', autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False, comment='Username')
    nameZH = db.Column(db.String(20), nullable=False, comment="nameZH")
    password = db.Column(db.String(20), nullable=False, comment='Password')


class Data(db.Model):
    __tablename__ = 'tb_data'
    recDateTime = db.Column(db.DateTime, comment="受理日期")
    recUnit = db.Column(db.String(20), comment="受理单位")
    id = db.Column(db.String(20), primary_key=True, index=True, comment='工单编号')
    electionID = db.Column(db.String(20), comment="发电户号")
    projectName = db.Column(db.String(20), comment="发电项目名称")
    projectType = db.Column(db.String(20), comment="项目类型")
    projectArchivingResponsible = db.Column(db.String(20), comment="项目归档负责人")
    bussinessProcessName = db.Column(db.String(20), comment="业务环节名称")
    nowProcessName = db.Column(db.String(20), comment="当前环节名称")
    notArchivingProcessNotIncludeNow = db.Column(db.String(20), nullable=True, comment="未完成归档环节（除当前环节）")
    processBussinessStartDateTime = db.Column(db.DateTime, nullable=True, comment="业务环节开始时间")
    processBussinessEndDateTime = db.Column(db.DateTime, nullable=True, comment="业务环节结束时间")
    archiveProcess = db.Column(db.String(20), comment="归档进度")
    archiveDateTime = db.Column(db.DateTime, nullable=True, comment="归档时间")
    numberofNotArchivingNotIncludeNow = db.Column(db.Integer, comment="项目剩余未归档环节数（除当前环节）")
    projectGridConnectionDate = db.Column(db.Date, nullable=True, comment="项目并网日期")
    daysLeft = db.Column(db.Integer,comment="项目归档剩余天数")

    def __repr__(self):
        return f"Post('{self.id}')"

# LoginManager 储存用户登录配置相关
login_manager = LoginManager()
login_manager.init_app(app)

# 验证失败后转跳的页面
login_manager.login_view = 'login'
# 重定向到页面时显示的消息
login_manager.login_message = '欢迎回来'
# 会话保护等级
login_manager.session_protection = 'strong'


# 用户信息回调函数 加入装饰器后 调用该函数返回一个用户对象  !!注意该函数要在实例化对象后使用
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 用户功能实现
# 注册功能
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db.session.add(User(username=username, password=password))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('reg.html')


# 登录功能
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usr = User.query.filter(
            and_(User.username == request.form['username'], User.password == request.form['password'])).first()
        print(request.form['username'], request.form['password'])

        if usr:
            # 实现用户的登录
            login_user(usr)
            return redirect(url_for('index'))
        return '用户不存在，登陆失败'
    return render_template('login.html')


# 注销/退出登录 需要登录状态 加入login——required装饰器
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/api/data/get')
@login_required
def get_data():
    data = []
    return jsonify(data)


@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/')
def hello():
    return render_template('hello.html')

with app.app_context():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run()
