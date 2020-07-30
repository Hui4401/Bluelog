import random
from faker import Faker
from sqlalchemy.exc import IntegrityError

from bluelog.extensions import db
from bluelog.models import Admin, Category, Post, Comment, Link


fake = Faker('zh-CN')


def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='admin的博客',
        blog_sub_title="admin",
        name='admin',
        email = '',
        about='admin'
    )
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='默认分类')
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            read=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # 未读评论
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            read=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # 管理员评论
        comment = Comment(
            author='admin',
            email='',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            read=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    db.session.commit()


def fake_links():
    github = Link(name='GitHub', url='#')
    email = Link(name='邮箱', url='#')
    db.session.add_all([github, email])
    db.session.commit()
