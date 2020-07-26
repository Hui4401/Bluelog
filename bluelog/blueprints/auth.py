from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from bluelog.forms import LoginForm
from bluelog.models import Admin
from bluelog.utils import redirect_back


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('登录成功', 'info')
                return redirect_back()
            flash('用户名或密码错误！', 'warning')
        else:
            flash('管理员账户未初始化！', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('已退出', 'info')
    return redirect_back()
