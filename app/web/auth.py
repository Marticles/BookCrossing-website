from . import web
from app.forms.auth import RegisterForm,EmailForm,LoginForm,ResetPasswordForm
from app.models.user import User
from app.models.base import db
from flask import render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,current_user
from app.libs.email import send_email

@web.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
        #注册成功返回登录页面
        return redirect(url_for('web.login'))

    return render_template('auth/register.html',form=form)


@web.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user,remember=True)
            next = request.args.get('next')
            if not next or not next.startswith('/'):
                next = url_for('web.index')
            return redirect(next)
        else:
            flash('账号不存在或密码错误')
    return render_template('auth/login.html',form=form)


@web.route('/reset/password', methods=['GET', 'POST'])
def forget_password_request():
    form = EmailForm(request.form)
    if request.method == 'POST':
        if form.validate():
            account_email = form.email.data
            user = User.query.filter_by(email=account_email).first_or_404()
            send_email(form.email.data, '重置你的密码',
                       'email/reset_password.html', user=user,
                       token=user.generate_token())
            flash('密码重置邮件已发送到你的邮箱' + account_email + '，请及时查收')
            #return redirect(url_for('web.login'))
    return render_template('auth/forget_password_request.html',form=form)


@web.route('/reset/password/<token>', methods=['GET', 'POST'])
def forget_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('web.index'))
    form = ResetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        result = User.reset_password(token, form.password1.data)
        if result:
            flash('你的密码已更新,请使用新密码登录')
            return redirect(url_for('web.login'))
        else:
            flash('密码更新失败!')
            return redirect(url_for('web.index'))
    return render_template('auth/forget_password.html',form=form)


@web.route('/change/password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        current_user.password = form.new_password1.data
        db.session.commit()
        flash('密码修改成功')
        return redirect(url_for('web.personal'))
    return render_template('auth/change_password.html', form=form)


@web.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('web.index'))
