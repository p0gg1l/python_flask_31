from flask import Flask, render_template, url_for, request, flash, session, redirect, abort
app = Flask(__name__)
app.config['SECRET_KEY'] = '96a7fgw467o8se47go6se587dg5s6dxvb568so'

menu = [{'name':"Установка", 'url': "install-flask"},
        {'name':"Первое приложение", 'url': "install-flask"},
        {'name':"Обратная связь", 'url': "contact"}]


@app.route("/")
def index():
    print(url_for("index"))
    return render_template("index.html", menu=menu)   # обращение к какому либо шаблону


@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        if len(request.form["username"]) > 2:
            flash("Форма отправлена", category='success')                           #вспылвающие сообщения
        else:
            flash("Ошибка отправки", category='error')

    return render_template("contact.html", title="Обратная связь", menu=menu)


@app.route('/login', methods=['POST','GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))                     # переадресация
    elif request.method == 'POST' and request.form['username'] == 'selfedu' and request.form["psw"] == '123':   # форма для входа
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title="Авторизация", menu=menu)


@app.route("/about")
def about():
    print(url_for("about"))
    return render_template("about.html", title="О сайте", menu=menu)


@app.route("/profile/<username>")
def profile(username):   # адрес под каждый профиль
    if 'userLogged' not in session or session['userLogged'] != username:                    #если пользователь незалогинился или строка запроса не соответсвтует профилу(несуществующий профиль)
        abort(401)
    return f'Пользователь: {username}'


@app.errorhandler(401)
def userNotFound(error):                                                                     #в случае если 401 (пользователь не авторизирован)
    return render_template('abort401.html', title="Неавторизованный", menu=menu)


@app.errorhandler(404)
def pageNotFound(error):                                                                #в случае если 404
    return render_template('page404.html', title="Страница не найдена", menu=menu)


# if __name__ == "__main__":
#     app.run(debug=True)

