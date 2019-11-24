from publishApp.models import Author, Subject, Article, Comment, Visitor, ArticleVote, CommentVote, VisitVote, SensitiveWord
from publishApp import db, app
from datetime import datetime
from flask import session
import os


class db_tool:

    @staticmethod
    def delete_article_relative(id):
        article = Article.query.filter_by(id=id).first()
        article_vote = ArticleVote.query.filter_by(article_id=id).first()

        if article:
            db.session.delete(article)
            db.session.commit()

        if article_vote:
            db.session.delete(article_vote)
            db.session.commit()

    @staticmethod
    def delete_comment_relative(id):
        comment = Comment.query.filter_by(id=id).first()
        comment_vote = CommentVote.query.filter_by(comment_id=id).first()

        if comment:
            db.session.delete(comment)
            db.session.commit()

        if comment_vote:
            db.session.delete(comment_vote)
            db.session.commit()

    @staticmethod
    def hide_article(id):
        article = Article.query.filter_by(id=id).first()
        if article:
            article.status = 0
            db.session.add(article)
            db.session.commit()


class Tool:

    @staticmethod
    def find(subject):
        if(subject.pid=='None'):
            print(subject.id)
        else:
            subject = Subject.query.filter_by(id=subject.pid).first()
            Tool.find(subject)

    # ==================================================================================================
    # @param subject object
    # @return subject's full url
    # ==================================================================================================
    @staticmethod
    def subject_url(subject):
        url = ''
        while subject.pid != 'None':
            url = subject.name + '/' + url
            subject = Subject.query.filter_by(id=subject.pid).first()
        url = subject.name + '/' + url
        return url[0:-1]

    # ==================================================================================================
    # @param request.path for example, /article/100
    # @return 100
    # ======================================================================================================
    @staticmethod
    def find_path_last_id(path):
        return path[path.rfind('/', 1) + 1:]

    # =====================================================================================================
    # @param some text
    # @return some text without sensitive words
    # ======================================================================================================
    @staticmethod
    def sensitive_words_filter(text): 
        f = open('static/sensitive words/1.txt', 'r')
        result = ''
        flag = True
        for line in f:
            if line.strip() in text.split():
                flag = False
                result = text.replace(line.strip(), '**')
                text = result
        f.close()

        if flag:
            return text
        else:
            return result

    @staticmethod
    def check_short_time():
        if session.get('last_time') is None:
            session['last_time'] = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        else:
            x = (datetime.now() - datetime.strptime(session.get('last_time'), "%Y-%m-%d %H:%M")).seconds
            if x < 120:
                return "pivot"
            else:
                session['last_time'] = str(datetime.now().strftime("%Y-%m-%d %H:%M"))


    # =======================================================================================================
    # @param article orm object
    # @return article's metric
    # =======================================================================================================
    @staticmethod
    def calculate_metric(article):
        likes = article.upvote
        dislikes = article.downvote
        visits = article.visit
        comments = Comment.query.filter_by(article_id=article.id).count()

        metric = likes * 50 - dislikes * 30 + visits * 10 + comments * 20
        return metric



    @staticmethod
    def email_display_filter(email):
        pre = email[:email.rfind('@')]
        display = pre[:len(pre) // 2]
        suf = email[email.rfind('@') + 1:]

        for i in range(len(pre[len(pre) // 2:])):
            display += '*'

        return display + suf
