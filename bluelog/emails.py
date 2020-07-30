from threading import Thread
from flask import url_for, current_app
from flask_mail import Message

from bluelog.extensions import mail
from bluelog.models import Admin


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_new_comment_email(post):
    admin = Admin.query.first()
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    body = f'''
                <p>文章 <i>《{post.title}》</i> 有新的评论, 点击链接查看：</p>
                <p><a href="{post_url}">{post_url}</a></P>
                <p><small style="color: #868e96">不要回复此邮件</small></p>
            '''
    send_mail(subject='新评论', to=admin.email, html=body)


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    body = f'''
                <p>你对文章 <i>《{comment.post.title}》</i> 的评论有新回复, 点击链接查看：</p>
                <p><a href="{post_url}">{post_url}</a></p>
                <p><small style="color: #868e96">不要回复此邮件</small></p>
            '''
    send_mail(subject='新回复', to=comment.email, html=body)
