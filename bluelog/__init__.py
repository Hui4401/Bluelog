import os
import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.extensions import bootstrap, db, login_manager, csrf, ckeditor, mail, moment, toolbar
from bluelog.models import Admin, Post, Category, Comment, Link
from bluelog.configs import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_template_context(app)
    register_shell_context(app)
    
    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'Admin': Admin,
            'Post': Post,
            'Category': Category,
            'Comment': Comment
        }


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments_count = Comment.query.filter_by(read=False).count()
        else:
            unread_comments_count = None
 
        return {
            'admin': admin,
            'categories': categories,
            'links': links,
            'unread_comments_count': unread_comments_count
        }


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):

    @app.cli.command()
    @click.option('--username', prompt=True, help='管理员用户名')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='管理员密码')
    def init(username, password):
        '''初始化博客'''

        click.echo('初始化数据库...')
        db.drop_all()
        db.create_all()

        click.echo('创建管理员账户...')
        admin = Admin(
            username=username,
            blog_title=f'{username.capitalize()}的博客',
            blog_sub_title='天涯路远 | 见字如面',
            name=username.capitalize(),
            about=username.capitalize() + '...'
        )
        admin.set_password(password)
        db.session.add(admin)

        click.echo('创建默认分类...')
        category = Category(name='默认分类')
        db.session.add(category)

        db.session.commit()

        if not os.path.exists(config['base'].CKEDITOR_UPLOAD_PATH):
            click.echo('图像上传路径不存在，创建中...')
            os.mkdir(config['base'].CKEDITOR_UPLOAD_PATH)

        click.echo('完成')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        '''生成虚拟数据'''
        from bluelog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links

        db.drop_all()
        db.create_all()

        click.echo('生成管理员...')
        fake_admin()

        click.echo(f'生成 {category} 个分类...')
        fake_categories(category)

        click.echo(f'生成 {post} 篇文章...')
        fake_posts(post)

        click.echo(f'生成 {comment} 条评论...')
        fake_comments(comment)

        click.echo('生成链接...')
        fake_links()

        if not os.path.exists(config['base'].CKEDITOR_UPLOAD_PATH):
            click.echo('图像上传路径不存在，创建中...')
            os.mkdir(config['base'].CKEDITOR_UPLOAD_PATH)

        click.echo('完成')