from publishApp import db
from datetime import datetime


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(50), unique=True)
    is_banned = db.Column(db.Boolean, default=False)

    # OneToMany
    articles = db.relationship('Article', backref='author')
    comments = db.relationship('Comment', backref='author')


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    pid = db.Column(db.Integer)

    # OneToMany
    articles = db.relationship('Article', backref='subject')


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    title = db.Column(db.Text)
    abstract = db.Column(db.Text)
    highlight = db.Column(db.Text)
    time = db.Column(db.DateTime)
    visit = db.Column(db.Integer)
    upvote = db.Column(db.Integer)
    downvote = db.Column(db.Integer)
    metric = db.Column(db.Float, default=0)
    fpath = db.Column(db.String)
    status = db.Column(db.Integer, default=1)

    # OneToMany
    comments = db.relationship('Comment', backref='article')

    # def get_mail(self):
    #     # db.session.query(Author).filter(Author.id == articles[0].author_id).first().mail
    #     return db.session.query(Author).filter(Author.id == self.author_id).first().mail


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    body = db.Column(db.Text)
    upvote = db.Column(db.Integer)
    downvote = db.Column(db.Integer)

    time = db.Column(db.DateTime)

    # comment1.article.title


# ------------------------------------------------------#
#              record every visitor's ip               #
# ------------------------------------------------------#
class Visitor(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), unique=True)
    is_banned = db.Column(db.Boolean, default=False)

    # OneToMangy
    article_votes = db.relationship('ArticleVote', backref='visitor')
    comment_votes = db.relationship('CommentVote', backref='visitor')
    visit_votes = db.relationship('VisitVote', backref='visitor')

class ArticleVote(db.Model):
    __tablename__ = 'article_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))

    article_id = db.Column(db.Integer)
    #upvote_state = db.Column(db.Integer)


class CommentVote(db.Model):
    __tablename__ = 'comment_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    comment_id = db.Column(db.Integer)
    #vote_state = db.Column(db.Integer)


class VisitVote(db.Model):
    _tablename__ = 'visit_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    article_id = db.Column(db.Integer)


class SensitiveWord(db.Model):
    __tablename__ = 'sensitive_words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50))


