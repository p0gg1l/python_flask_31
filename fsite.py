import os
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for
import sqlite3
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required,logout_user,current_user
from UserLogin import UserLogin



# конфигурация
DATABASE = '/tmp/fsite.db'
DEBUG = True
SECRET_KEY = 'SDZFDHGFDNGFDHNCGBN6R5H54YTN45Y7457Y'
MAX_CONTENT_LENGHT = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__) #конфигурируем базу на основе наших данных
app.config.update(dict(DATABASE=os.path.join(app.root_path,'fsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизируйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)



def connect_db():
    conn = sqlite3.connect(app.config['DATABASE']) #путь к базе данных(из конфигурации)
    conn.row_factory = sqlite3.Row #для того чтобы записи были не ввиде кортежей а ввиде словаря
    return conn

def create_db():
    # Вспомогательная функция для создания таблиц БД
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    # Соединение с Бд если оно еще не установлено
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    """установление соединения с бд пе6ред выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.route("/")
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.route('/login', methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated:  # устранение процесса авторизации для авторизированных пользователей
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        # """получаем данные о пользователе"""
        if user and check_password_hash(user['psw'], request.form['psw']):
            #если данные получены и пароль был введен верно
            userlogin = UserLogin().create(user)
            #передаем только что созданному экземпляру инфу из БД
            rm = True if request.form.get('remainme') else False
            #когда пользователь нажимает галочку(запомнить меня) присваивается значение TRUE
            login_user(userlogin, remember=rm)
            #авторизуем пользователя и запоминаем его
            return redirect(request.args.get('next') or url_for('profile'))
        flash('Hеверный логин или пароль!!!!!!', category='error')

    return render_template('login.html', menu=dbase.getMenu(), title = 'Авторизация')


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Такая почта уже существует", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")



@app.route('/add_post', methods=['POST', 'GET'])
def addPost():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category = 'error')
            else:
                flash('Статья добавлена успешно', category = 'success')
        else:
            flash('Пишите больше букав', category = 'error')
    return render_template('add_post.html', menu=dbase.getMenu(), title = 'Добавление статьи')


@app.route('/post/<alias>')
@login_required  #строчка для ограничения неавторизованных пользователей
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post )


@app.teardown_appcontext
# Закрываем соединение с БД если оно было установлено
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', category='success')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', menu=dbase.getMenu(), title='Профиль')
    #Отображаем информацию о пользователе(Id)



@app.errorhandler(404)
def pageNotFound(error):                                                                #в случае если 404
    return render_template('page404.html', title="Страница не найдена")

if __name__ == '__main__':
    app.run(debug=True)
