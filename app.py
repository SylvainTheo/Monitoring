#! /usr/bin/python3.5
# -*- coding:utf-8 -*-

from flask import Flask, render_template, request, g, session, url_for, redirect, flash
import mysql.connector
from passlib.hash import argon2

#Construct app
app = Flask(__name__)
app.config.from_object('config')
app.config.from_object('secret_config')


#Database functions
def connect_db () :
    g.mysql_connection = mysql.connector.connect(
        host = app.config['DATABASE_HOST'],
        user = app.config['DATABASE_USER'],
        password = app.config['DATABASE_PASSWORD'],
        database = app.config['DATABASE_NAME']
    )

    g.mysql_cursor = g.mysql_connection.cursor()
    return g.mysql_cursor

def get_db () :
    if not hasattr(g, 'db') :
        g.db = connect_db()
    return g.db

@app.teardown_appcontext
def close_db (error) :
    if hasattr(g, 'db') :
        g.db.close()

@app.route('/show_websites/')
@app.route('/')
def show_websites():
    db = get_db()
    db.execute('SELECT id,url FROM websites')
    sites = db.fetchall()
    print(sites)
    requests_sites = []
    for site in sites:
        oneSite = []
        strSQL= "SELECT request_result from checks where websites = (SELECT id from websites where url = '"+site[1]+"') order by id DESC"
        db.execute(strSQL)
        result = db.fetchall()
        oneSite.append(site[1])
        if len(result) !=0:
            oneSite.append(result[0][0])
        else:
            oneSite.append("Aucune requête n'a encore été envoyé")
        oneSite.append(site[0])
        requests_sites.append(oneSite)

    return render_template('show_websites.html', requests_sites= requests_sites)

@app.route('/show_one_website/<id_site>/')
def show_one_website(id_site):

    db = get_db()
    db.execute("select checkTime, request_result from checks where websites ="+id_site+" order by id DESC")
    results_site = db.fetchall()

    db.execute("select id, url from websites where id = "+id_site)
    current_site=db.fetchall()

    result_is_empty=True
    if not results_site:
        result_is_empty=False
    return render_template('show_one_website.html',id_site= id_site, results_site= results_site, result_is_empty=result_is_empty, current_site= current_site)

@app.route('/login/', methods = ['GET', 'POST'])
def login () :

    if request.form :
        email = str(request.form.get('email'))
        password = str(request.form.get('password'))

        db = get_db()
        db.execute('SELECT email, password, is_admin FROM user WHERE email = %(email)s', {'email' : email})
        users = db.fetchall()
        valid_user = False
        for user in users :
            if argon2.verify(password, user[1]) :
                valid_user = user

        if valid_user :
            session['user'] = valid_user
            flash('Vous avez bien été connecté', 'success')
            return redirect(url_for('admin'))
        elif not valid_user :
            flash('Email ou mot de passe incorrect', 'error')
    return render_template('login.html')

@app.route('/admin/')
def admin () :
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))

    db =get_db()
    db.execute("SELECT * from websites")
    websites = db.fetchall()
    return render_template('admin.html', user = session['user'], websites= websites)

@app.route('/admin/logout/')
def admin_logout () :
    session.clear()
    flash('Vous avez bien été déconnecté', 'success')
    return redirect(url_for('login'))

@app.route('/add/', methods = ['GET', 'POST'])
def add_website():
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))

    if request.form:
        url = request.form.get('url')
        db =get_db()
        db.execute("INSERT INTO websites (url) VALUES ('"+url+"')")
        g.mysql_connection.commit()
        db.close()
        flash('Site ajouté avec succès !', 'success')
        return redirect(url_for('admin'))
    flash("Erreur de l'ajout du site", 'error')
    return redirect(url_for('admin'))

@app.route('/delete/<id_site>/')
def delete_website(id_site):
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))

    db = get_db()
    strSQL='delete from checks where websites = '+id_site
    db.execute(strSQL)
    strSQL='delete from websites where id = '+id_site
    db.execute(strSQL)
    g.mysql_connection.commit()
    flash("Site supprimé avec succès !", 'success')
    return redirect(url_for('admin'))

@app.route('/modify/<id_site>/')
def modify_website_form(id_site):
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))

    db=get_db()
    db.execute("SELECT * from websites where id ="+id_site)
    info_site=db.fetchall()

    return render_template('modify_website.html', info_site=info_site)

@app.route('/modify/', methods = ['GET', 'POST'])
def modify_website():
    if not session.get('user') or not session.get('user')[2] :
        return redirect(url_for('login'))

    if request.form:
        url = request.form.get('url')
        id_site = request.form.get('id_site')
        print(url, id_site)
        db=get_db()
        db.execute("DELETE from checks where websites="+id_site)
        db.execute("UPDATE websites SET url='"+url+"' WHERE id="+id_site)
        g.mysql_connection.commit()
        db.close()
        flash('Modification du site effectuée', 'success')
        return redirect(url_for('admin'))
    redirect(url_for('modify_website_form'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

