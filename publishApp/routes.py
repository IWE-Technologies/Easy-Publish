from publishApp.models import Author, Subject, Article, Comment, Visitor, ArticleVote, CommentVote, VisitVote, SensitiveWord
from publishApp.tools import Tool, db_tool
from publishApp import db, app, threshold, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, basedir
from flask import render_template, url_for, session, redirect, jsonify, send_from_directory, flash, request
from datetime import datetime, timedelta
import os, uuid ,math, random
from sqlalchemy import or_
from werkzeug.utils import secure_filename

@app.route('/article_upvote/<articleID>')
def article_upvote(articleID):
    # get goal article
    article = Article.query.filter_by(id=articleID).first()

    ip = session.get('ip')
    visitor = Visitor.query.filter_by(ip=ip).first()

    articlevote = ArticleVote.query.filter_by(visitor_id=visitor.id, article_id=articleID).first()


    # didn't vote this article before
    if articlevote is None:
        articlevote = ArticleVote(visitor_id=visitor.id, article_id=articleID)
        article.upvote += 1
        article.metric = Tool.calculate_metric(article)

        # Tool.calculate_metric(article)

        db.session.add(articlevote)
        db.session.add(article)
    else:
        return jsonify({'ht': 'You have voted, please do not submit again', 'upvote': article.upvote})
    return jsonify({'upvote': article.upvote})


@app.route('/article_downvote/<articleID>')
def article_downvote(articleID):
    # get goal article
    article = Article.query.filter_by(id=articleID).first()

    ip = session.get('ip')
    visitor = Visitor.query.filter_by(ip=ip).first()

    articlevote = ArticleVote.query.filter_by(visitor_id=visitor.id, article_id=articleID).first()
    # didn't vote this article before
    if articlevote is None:
        articlevote = ArticleVote(visitor_id=visitor.id, article_id=articleID)
        article.downvote += 1
        article.metric = Tool.calculate_metric(article)

        db.session.add(articlevote)
        db.session.add(article)
    else:
        return jsonify({'ht': 'You have voted, please do not submit again', 'downvote': article.downvote})
    return jsonify({'downvote': article.downvote})


@app.route('/comment_upvote/<commentID>')
def comment_upvote(commentID):
    # get goal comment
    comment = Comment.query.filter_by(id=commentID).first()
    ip = session.get('ip')
    visitor = Visitor.query.filter_by(ip=ip).first()

    commentvote = CommentVote.query.filter_by(visitor_id=visitor.id, comment_id=commentID).first()
    # didn't vote this article before
    if commentvote is None:
        commentvote = CommentVote(visitor_id=visitor.id, comment_id=commentID)
        comment.upvote += 1
        db.session.add(commentvote)
        db.session.add(comment)
    else:
        return jsonify({'ht': 'You have voted, please do not submit again', 'upvote': comment.upvote})
    return jsonify({'upvote': comment.upvote})


@app.route('/comment_downvote/<commentID>')
def comment_downvote(commentID):
    # get goal comment
    comment = Comment.query.filter_by(id=commentID).first()
    ip = session.get('ip')
    visitor = Visitor.query.filter_by(ip=ip).first()

    commentvote = CommentVote.query.filter_by(visitor_id=visitor.id, comment_id=commentID).first()
    # didn't vote this article before
    if commentvote is None:
        commentvote = CommentVote(visitor_id=visitor.id, comment_id=commentID)
        comment.downvote += 1
        db.session.add(commentvote)
        db.session.add(comment)
    else:
        return jsonify({'ht': 'You have voted, please do not submit again', 'downvote': comment.downvote})
    return jsonify({'downvote': comment.downvote})


# =========================================================================================
# check if a email is banned
# ========================================================================================
@app.route('/check/<mail>')
def check_mail(mail):
    author = Author.query.filter_by(mail=mail).first()
    if not author:
        return jsonify('ok')
    #return jsonify({'isbanned': author.is_banned})
    return jsonify(author.is_banned)


# ==================================================================================================
# subject
# ==================================================================================================
@app.route('/subject/<subjectID>')
def get_subject(subjectID):
    subject = Subject.query.filter_by(id=subjectID).first()
    url = Tool.subject_url(subject)

    # articles = subject.articles
    articles = Article.query.filter_by(subject_id=subject.id, status=1).all()

    # ==================================================
    # hot article
    # ==================================================
    hot_article = []
    total = 0

    a = db.session.query(Article).filter(
        Article.subject_id == subject.id,
        Article.metric > threshold
    ).all()


    for x in a:
        hot_article.append(x)




    return render_template('subject.html', url=url, subject_id=subject.id, articles=articles, hot_article=hot_article, Tool=Tool)


# ============================================================================================
# before request
# ============================================================================================
@app.before_request
def before_request():
    ip = str(request.remote_addr)
    #ip = '127.0.0.5'
    #ip = request.remote_addr
    session['ip'] = ip
    visitor = Visitor.query.filter_by(ip=ip).first()
    if visitor is None:
        visitor = Visitor(ip=ip)
        db.session.add(visitor)
    else:
        # banned ip, can not visitor
        if Visitor.query.filter_by(ip=ip).first().is_banned:
            print('you have beenn banned')
            return render_template('error.html', message='you have beenn banned')

        # ======================================================================================
        # from now on, ip is valid
        # ======================================================================================

        # about visit of a article
        if request.path.startswith('/article'):
            article_id = Tool.find_path_last_id(request.path)
            visitor = Visitor.query.filter_by(ip=ip).first()
            visitvote = VisitVote.query.filter_by(visitor_id=visitor.id, article_id=article_id).first()
            # first visit this article
            if visitvote is None:
                article = Article.query.filter_by(id=article_id).first()
                article.visit += 1
                article.metric = Tool.calculate_metric(article)
                visitvote = VisitVote(visitor_id=visitor.id, article_id=article_id)
                db.session.add(visitvote)
                db.session.add(article)


# ============================================================================================#
#                                         index                                               #
# ============================================================================================#
@app.route('/')
def index():
    return render_template('io.html')


@app.route('/test')
def test_one():
    return render_template('test.html')


# ============================================================================================#
# used to out new index after new a subcategory.
# ============================================================================================#
@app.route('/newindex')
def create_index():
    out = open('templates/io.html', 'w', encoding='UTF-8', newline='')

    def find_subjects(subject, count):
        if count == 0:
            out.write('<a href="subject/' + str(subject.id) + '">' + subject.name + '</a><br>\n')
        else:
            for i in range(count):
                out.write('&emsp;\n')
            out.write('<a href="subject/' + str(subject.id) + '">' + subject.name + '</a><br>\n')
        for subject in Subject.query.filter_by(pid=subject.id).all():
            find_subjects(subject, count + 1)

    subjects = Subject.query.filter_by(pid='None').all()
    out.write('{% extends "template.html" %}' + '\n')
    out.write('{% block content %}' + '\n')
    for subject in subjects:
        find_subjects(subject, 0)
        print('\n')

    out.write('{%  endblock  %}' + '\n')
    out.flush()
    out.close()

    return render_template('io.html')
    # return redirect('/')


# ================================================================================
# Edit and add subject
# ================================================================================
@app.route('/edit_subcategory', methods=['GET', 'POST'])
def add_sub_category():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        subject_name = request.form['subject_name']

        duplicate1 = Subject.query.filter_by(name=subject_name).first()
        duplicate2 = 'pivot'

        f = open('static/possible subject/subjects.txt', 'r')
        for line in f:
            if line.strip() == subject_name:
                duplicate2 = None
        f.close()

        if duplicate1 or duplicate2 is None:
            info = 'duplicate subject name!'
            return render_template('add_subcategory.html', info=info, subject_id=subject_id)
        else:
            subject = Subject(name=subject_name, pid=subject_id)
            if subject_id is None:
                subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.flush()
            # return render_template('add_subcategory.html',)
            create_index()
        # return render_template('io.html')
        return redirect('/')
    else:
        subject_id = request.args.get('subject_id')
        if request.args.get('add_father') == 'father':
            subject_id = str(None)

        return render_template('add_subcategory.html', subject_id=subject_id)
# ============================================================================================
# edit page
# ============================================================================================
@app.route('/edit', methods=['GET', 'POST'])
def post_article():
    if request.method == 'POST':
        email = request.form['email']
        # means that author didn't in database now
        if not Author.query.filter_by(mail=email).first():
            author = Author(mail=email, is_banned=False)
            db.session.add(author)

        # pdf only
        # ----------------------------------------------------------------
        message = 'only pdf file is allowed'
        file = request.files['file']
        filename = str(file.filename)[str(file.filename).rfind('.', 0):]
        if filename != '.pdf':
            return render_template('error.html', message=message)
        # ----------------------------------------------------------------

        # ----------------------------------------------------------------
        # can not submit in short time
        # ----------------------------------------------------------------
        if Tool.check_short_time() == 'pivot':
            email = request.form['email']
            subject_id = request.form['subject_id']
            title = request.form['title']
            abstract = request.form['abstract']
            highlight = request.form['highlight']
            message = 'You post too many time in short time!'
            return render_template('error.html', message=message)
        else:
            author_id = Author.query.filter_by(mail=email).first().id
            subject_id = request.form['subject_id']
            title = request.form['title']
            abstract = request.form['abstract']
            highlight = request.form['highlight']
            time = datetime.now()
            article = Article(author_id=author_id, subject_id=subject_id, title=title, abstract=abstract, highlight=highlight, time=time, upvote=0, downvote=0, visit=0)
            db.session.add(article)
            db.session.flush()
            upload_file(article)

            return redirect(url_for('get_article', articleID=article.id))

        #return render_template('io.html')
    else:
        email = request.args.get('email')
        subject_id = request.args.get('subject_id')
        return render_template('post_article.html', email=email, subject_id=subject_id)


# ==============================================================================================================================
# add sub category
# ==============================================================================================================================


# ============================================================================================
# submit after edit
# ============================================================================================
@app.route('/postpaper', methods=['POST'])
def post_paper():
    #email = request.args.get('email')
    #subject_id = request.args.get('subject_id')
    pass


# =============================================================================================
# article
# =============================================================================================

@app.route('/article/<articleID>')
def get_article(articleID):
    article = Article.query.filter_by(id=articleID).first()
    ip = session.get('ip')

    if not Visitor.query.filter_by(ip=ip).first():
        article.visit += 1
        db.session.add(article)

    comments = article.comments
    #comments = Comment.query.order_by(Comment.time.desc())


    return render_template('article.html', article=article, comments=comments, Tool=Tool)


# ========================================================================
# upload pdf file
# ========================================================================
@app.route('/postPdf', methods=['GET', 'POST'])
def upload_file(article):
    if request.method == 'POST':

        file = request.files['file']

        # session['filename'] = file.filename
        if file and allowed_file(file.filename):
            print('filename:--------------' + file.filename)
            u = str(uuid.uuid1())
            file.filename = u + file.filename
            filename = secure_filename(file.filename)
            #
            # print(article.title)
            article.fpath = filename
            db.session.add(article)
            db.session.flush()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    else:
        return render_template('io.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===========================================================================
# download pdf file
# ===========================================================================
@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename, as_attachment=True)


# ======================================================================
# post comment
# ======================================================================
@app.route('/post_comment/<articleID>', methods=['POST'])
def post_comment(articleID):
    if Tool.check_short_time() == 'pivot':
        email = request.form['email']
        body = request.form['body']
        message = 'You post too many time in short time!'
        return render_template('error.html', message=message)

    email = request.form['email']
    body = request.form['body']
    time = datetime.now()
    # means that author didn't in database now
    if not Author.query.filter_by(mail=email).first():
        author = Author(mail=email, is_banned=False)
        db.session.add(author)

    author_id = Author.query.filter_by(mail=email).first().id
    comment = Comment(author_id=author_id, article_id=articleID, body=body, upvote=0, downvote=0, time=time)
    db.session.add(comment)
    article = Article.query.filter_by(id=articleID).first()
    article.metric = Tool.calculate_metric(article)
    return redirect(url_for('get_article', articleID=articleID))


# ===============================================================================
# donation
# ===============================================================================
@app.route('/donation')
def donaton():
    return render_template('donation.html')

# ===========================================================================
# search function
# ===========================================================================
@app.route('/search')
def search():
    articles = None
    comments = None
    message = None

    select = request.args.get('select')
    content = request.args.get('content')

    a = db.session.query(Article).filter(or_(Article.title.contains(content), Article.highlight.contains(content), Article.abstract.contains(content))).all()
    c = db.session.query(Comment).filter(Comment.body.contains(content))



    if select == 'article':
        articles = a
    if select == 'comment':
        comments = c




    return render_template('search.html', articles=articles, comments=comments, Tool=Tool, message=message, content=content)


@app.route('/error/<message>')
def error(message):
    return render_template('error.html', message=message)


@app.route('/author/<author_id>')
def author(author_id):
    articles = Article.query.order_by(Article.time.desc()).filter_by(author_id=author_id).all()
    comments = Comment.query.order_by(Comment.time.desc()).filter_by(author_id=author_id).all()
    return render_template('author.html', articles=articles, comments=comments, Tool=Tool)



@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html'), 500


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404