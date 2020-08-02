import os
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory, make_response
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail

from bluelog.extensions import db
from bluelog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from bluelog.models import Post, Category, Comment, Link
from bluelog.utils import redirect_back, allowed_file, random_filename


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/settings/', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        current_user.about = form.about.data
        db.session.commit()
        flash('设置已更新', 'success')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.email.data = current_user.email
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/post/manage/')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)


@admin_bp.route('/post/new/', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash('文章已创建', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('文章已更新', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete/', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除', 'success')
    return redirect_back()


@admin_bp.route('/post/<int:post_id>/set-comment/', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('已禁止评论', 'success')
    else:
        post.can_comment = True
        flash('已允许评论', 'success')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/manage/')
@login_required
def manage_comment():
    filter_rule = request.args.get('filter', 'unread')  # 'unread', 'all', 'admin'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(read=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@admin_bp.route('/comment/readall/', methods=['POST'])
@login_required
def read_all_comment():
    unread_comments = Comment.query.filter_by(read=False)
    for comment in unread_comments:
        comment.read = True
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/read/', methods=['POST'])
@login_required
def read_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.read = True
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/delete/', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect_back()


@admin_bp.route('/category/manage/')
@login_required
def manage_category():
    return render_template('admin/manage_category.html')


@admin_bp.route('/category/new/', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('新建分类成功', 'success')
        return redirect(url_for('.manage_category'))
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('默认分类不可编辑！', 'warning')
        return redirect(url_for('blog.index'))
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('分类已更新', 'success')
        return redirect(url_for('.manage_category'))

    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/delete/', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('默认分类不可删除！', 'warning')
        return redirect(url_for('blog.index'))
    category.delete()
    flash('分类已删除', 'success')
    return redirect(url_for('.manage_category'))


@admin_bp.route('/link/manage/')
@login_required
def manage_link():
    return render_template('admin/manage_link.html')


@admin_bp.route('/link/new/', methods=['GET', 'POST'])
@login_required
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        link = Link(name=name, url=url)
        db.session.add(link)
        db.session.commit()
        flash('新建链接成功', 'success')
        return redirect(url_for('.manage_link'))
    return render_template('admin/new_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    form = LinkForm()
    link = Link.query.get_or_404(link_id)
    if form.validate_on_submit():
        link.name = form.name.data
        link.url = form.url.data
        db.session.commit()
        flash('链接已更新', 'success')
        return redirect(url_for('.manage_link'))
    form.name.data = link.name
    form.url.data = link.url
    return render_template('admin/edit_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/delete/', methods=['POST'])
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('链接已删除', 'success')
    return redirect(url_for('.manage_link'))


@admin_bp.route('/uploads/<path:filename>/')
def get_image(filename):
    return send_from_directory(current_app.config['CKEDITOR_UPLOAD_PATH'], filename)


@admin_bp.route('/upload/', methods=['POST'])
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('仅允许上传图片！')
    new_filename = random_filename(f.filename)
    f.save(os.path.join(current_app.config['CKEDITOR_UPLOAD_PATH'], new_filename))
    url = url_for('.get_image', filename=new_filename)
    return upload_success(url=url)


@admin_bp.route('/change-theme/<theme_name>/')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLOG_THEMES'].keys():
        abort(404)

    current_app.config['BLOG_THEME'] = theme_name
    return redirect_back()