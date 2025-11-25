from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for,flash
from sqlalchemy import extract, func
from flask import jsonify
from datetime import timedelta
from models import db,User,Product,CartItem,News,Order,OrderItem
from flask_login import (
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'Top ... secret!'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=10)
app.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = True


def get_month_name(month_number):
    """Возвращает название месяца по номеру"""
    months = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    return months.get(month_number, 'Неизвестно')


db.init_app(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
login_manager.login_message='Пожалуйста, войдите в систему'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

@app.route('/index')
@app.route('/')
def index():
    news=db.session.query(News).order_by(News.id.desc()).offset(1).limit(3).all()
    last=db.session.query(News).order_by(News.id.desc()).first()

    archives = db.session.query(
        extract('year', News.date).label('year'),
        extract('month', News.date).label('month'),
        func.count(News.id).label('count')
    ).group_by(
        extract('year', News.date),
        extract('month', News.date)
    ).order_by(
        extract('year', News.date).desc(),
        extract('month', News.date).desc()
    ).all()
    formatted_archives = []
    for archive in archives:
        formatted_archives.append({
            'year': int(archive.year),
            'month': int(archive.month),
            'month_name': get_month_name(int(archive.month)),
            'count': archive.count
        })
    # print(f"{formatted_archives}")
    return render_template('index.html',news=news,last=last,archives=formatted_archives)

@app.route('/catalog_news/<int:year>/<int:month>')
def news_by_month(year,month):
    page = request.args.get('page', 1, type=int)
    if month < 1 or month > 12:
        return "Неверный месяц", 400
        # Получаем новости
    news_list = News.query.filter(
        extract('year', News.date) == year,
        extract('month', News.date) == month
    ).order_by(News.date.desc())
    pagination = news_list.paginate(
        page=page,
        per_page=5,
        error_out=False
    )
    return render_template('catalog_news.html',news=pagination)

@app.route('/registration', methods=['GET','POST'])
def registration():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует','error')
            return redirect(url_for('registration'))
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует','error')
            return redirect(url_for('registration'))
        user=User(username=username,email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Теперь вы можетет войти.','success')
        return redirect(url_for('login'))
    return render_template('registration.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        email=request.form['username']
        user=User.query.filter_by(username=username).first()
        user_email=User.query.filter_by(username=email).first()
        remember_me = 'remember_me' in request.form
        if user and user.check_password(password):
            login_user(user,remember=remember_me)
            next_page=request.args.get('next')
            return redirect(next_page or url_for('index'))
        elif user_email and user_email.check_password(password):
            login_user(user_email,remember=remember_me)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль','error')
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart_items=CartItem.query.filter_by(user_id=current_user.id).all()
    total=sum(item.product.price*item.quantity for item in cart_items)
    return render_template('cart.html',cart_items=cart_items,total=total)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    if not current_user.is_authenticated:
        return jsonify({
            'success': False,
            'message': 'Необходимо авторизоваться'
        })
    else:
        product = Product.query.get_or_404(product_id)
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product_id)
            db.session.add(cart_item)

        db.session.commit()

        # Считаем общее количество товаров в корзине
        cart_count = db.session.query(db.func.sum(CartItem.quantity)) \
                     .filter(CartItem.user_id == current_user.id) \
                     .scalar() or 0

        return jsonify({
            'success': True,
            'message': 'Товар добавлен в корзину',
            'cart_count': cart_count
        })

@app.route('/remove_from_cart/<int:cart_item_id>')
@login_required
def remove_from_cart(cart_item_id):
    cart_item=CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id!=current_user.id:
        flash('Ошибка доступа','error')
        return redirect(url_for('cart'))
    db.session.delete(cart_item)
    db.session.commit()
    flash('Товар удален из корзины','info')
    return redirect(url_for('cart'))

@app.route('/update_cart/<int:cart_item_id>',methods=['POST'])
@login_required
def update_cart(cart_item_id):
    cart_item=CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id != current_user.id:
        return jsonify({'error':'Ошибка доступа'}),403
    quantity=int(request.form['quantity'])
    if quantity<=0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity=quantity
    db.session.commit()
    cart_items=CartItem.query.filter_by(user_id=current_user.id).all()
    total=sum(item.product.price*item.quantity for item in cart_items)
    return jsonify({'success': True,'total':total})

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Требуются права администратора','warning')
            return redirect(url_for('index'))
        return f(*args,**kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_users = User.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    last_register=db.session.query(User).order_by(User.created_at.desc()).first()
    last_product=db.session.query(Product).order_by(Product.created_at.desc()).first()
    last_news=db.session.query(News).order_by(News.date.desc()).first()
    return render_template('admin/dashboard.html',
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_users=total_users,
                           total_revenue=total_revenue,
                           recent_orders=recent_orders,
                           time_ago=time_ago,
                           last_register=last_register,
                           last_product=last_product,
                           last_news=last_news)

@app.route('/admin/users')
@admin_required
def admin_users():
    users=User.query.all()
    total_cart_items=CartItem.query.count()
    total_users=User.query.count()
    admin_users=User.query.filter_by(is_admin=True).count()
    return render_template('admin/users.html',
                           users=users,
                           total_cart_items=total_cart_items,
                           total_users=total_users,
                           admin_users=admin_users)

@app.route('/admin/delete_user/<int:id>',methods=['POST'])
@admin_required
def delete_user(id):
    data=User.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/')


@app.route('/admin/users/make_admin/<int:user_id>', methods=['POST'])
@admin_required
def make_user_admin(user_id):
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Нельзя изменить свои права'})

    user = User.query.get_or_404(user_id)

    try:
        user.is_admin = True
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Пользователь {user.username} назначен администратором'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        }), 500


@app.route('/admin/users/remove_admin/<int:user_id>', methods=['POST'])
@admin_required
def remove_user_admin(user_id):
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Нельзя снять с себя права администратора'})

    user = User.query.get_or_404(user_id)

    try:
        user.is_admin = False
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'С пользователя {user.username} сняты права администратора'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        }), 500


@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    try:
        # Получаем товары из корзины пользователя
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

        if not cart_items:
            return jsonify({'success': False, 'message': 'Корзина пуста'})

        # Создаем заказ
        order = Order(
            user_id=current_user.id,
            total_amount=sum(item.product.price * item.quantity for item in cart_items),
            email=current_user.email,
            shipping_address=request.form.get('shipping_address', ''),
            phone=request.form.get('phone', '')
        )
        db.session.add(order)
        db.session.flush()  # Получаем ID заказа

        # Добавляем товары в заказ
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price  # Сохраняем цену на момент заказа
            )
            db.session.add(order_item)

        # Очищаем корзину
        CartItem.query.filter_by(user_id=current_user.id).delete()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Заказ успешно создан!',
            'order_id': order.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500




@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()

    # Статистика для админ-панели
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0

    return render_template('admin/admin_orders.html',
                           orders=orders,
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_revenue=total_revenue)

@app.route('/admin/order/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/admin_order_detail.html', order=order)


@app.route('/admin/order/<int:order_id>/update_status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')

    if new_status in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash('Статус заказа обновлен', 'success')
    else:
        flash('Неверный статус', 'error')

    return redirect(url_for('admin_orders'))



@app.route('/admin/products')
@admin_required
def admin_products():
    products=Product.query.all()
    return render_template('admin/products.html',products=products)

@app.route('/admin/add_product',methods=["POST","GET"])
@admin_required
def add_product():

    if request.method=="POST":
        name=request.form.get("name")
        price=request.form.get("price")
        description=request.form.get("description")
        category=request.form.get("category")
        file=request.files['file']
        if file.filename=='':
            image="/static/Catalog_images/1.jpg"
        else:
            filename=db.session.query(Product).order_by(Product.id.desc()).first()
            file.save("/app/static/Catalog_images/"+str(filename.id+1)+".jpg")
            image="/static/Catalog_images/"+str(filename.id+1)+".jpg"
        new_product=Product(name=name,description=description,price=price,image=image,category=category)
        db.session.add(new_product)
        db.session.commit()
        title = "Изменения в каталоге товаров: " + name
        text = "Был добавлен товар " + name + " по цене " + price + " р."
        image = "/static/News_images/orig.jpg"
        new_news = News(title=title, text=text, image=image)
        db.session.add(new_news)
        db.session.commit()
        return redirect('/catalog')
    else:
        return render_template('admin/add_product.html')

@app.route('/admin/add_news',methods=["POST","GET"])
@admin_required
def add_news():
    if request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        file = request.files['file']
        if file.filename == '':
            image = "/static/News_images/orig.jpg"
        else:
            filename = db.session.query(News).order_by(News.id.desc()).first()
            file.save("/app/static/News_images/" + str(filename.id + 1) + ".jpg")
            image = "/static/News_images/" + str(filename.id + 1) + ".jpg"
        new_news = News(title=title, text=text, image=image)
        db.session.add(new_news)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('admin/add_news.html')

@app.route('/admin/edit_products')
@admin_required
def edit_products():
    products=Product.query.all()
    return render_template('admin/edit_products.html',products=products)

@app.route('/admin/edit_product/<int:id>', methods=['POST','GET'])
@admin_required
def edit_product(id):
    if request.method=='POST':
        product=Product.query.get(id)
        product.name=request.form.get('name')
        product.price=request.form.get('price')
        product.category=request.form.get('category')
        product.description=request.form.get('description')
        file = request.files['file']
        if not file.filename == '':
            file.save("/app/static/Catalog_images/" + str(product.id) + ".jpg")
            product.image = "/static/Catalog_images/" + str(product.id) + ".jpg"
        db.session.commit()
        flash('Изменения сохранены', 'info')
        return redirect('/admin/edit_products')
    else:
        product=Product.query.get(id)
        return render_template('admin/edit_product.html',product=product)



@app.route('/admin/delete_product/<int:id>',methods=['POST'])
@admin_required
def delete_product(id):
    product = Product.query.get(id)
    title = "Изменения в каталоге товаров: " + product.name
    text = "Был удален товар " + product.name
    image = "/static/News_images/orig.jpg"
    new_news = News(title=title, text=text, image=image)
    db.session.add(new_news)
    CartItem.query.filter_by(product_id=id).delete()
    product.is_deleted = True
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Товар удален',
    })

@app.route('/admin/recover_product/<int:id>', methods=['POST'])
@admin_required
def recover_product(id):
    product = Product.query.get(id)
    title = "Изменения в каталоге товаров: " + product.name
    text = "Был добавлен товар " + product.name
    image = "/static/News_images/orig.jpg"
    new_news = News(title=title, text=text, image=image)
    db.session.add(new_news)
    product.is_deleted = False
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Товар восстановлен'
    })



@app.route('/admin/delete_news/<int:id>')
@admin_required
def delete_new(id):
    data=News.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash('Новость удалена', 'info')
    return redirect('/admin/edit_news')


@app.route('/catalog')
@app.route('/catalog/<category>')
def catalog(category=None):
    search_query = request.args.get('search', '')
    category_filter=category
    if category_filter:
        products=db.session.query(Product).filter(db.and_(
            Product.category.contains(category_filter),
            Product.is_deleted==False
        )).all()
    else:
        products = Product.query.filter_by(is_deleted=False).all()
    if search_query:
        products = Product.query.filter(db.and_(
            Product.is_deleted==False,
        db.or_(
            Product.name.ilike(f'%{search_query}%'),
            Product.description.ilike(f'%{search_query}%')
        ))).all()
    if current_user.is_authenticated:
        total_quantity = db.session.query(db.func.sum(CartItem.quantity)) \
            .filter(CartItem.user_id == current_user.id) \
            .scalar()
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_product_ids = [item.product_id for item in cart_items]
        return render_template('catalog.html', products=products, cart_count=total_quantity,cart_product_ids=cart_product_ids)
    else:
        return render_template('catalog.html',products=products)



@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/api/orders_chart_data/<period>')
def orders_chart_data_period(period):
    end_date = datetime.now()

    if period == 'week':
        start_date = end_date - timedelta(days=6)
        date_format = '%d %b'
    elif period == 'month':
        start_date = end_date - timedelta(days=29)
        date_format = '%d %b'
    elif period == 'year':
        start_date = end_date - timedelta(days=364)
        date_format = '%b %Y'
    else:
        start_date = end_date - timedelta(days=9)
        date_format = '%d %b'

    orders_by_day = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('count')
    ).filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at)
    ).all()

    orders_dict = {str(order.date): order.count for order in orders_by_day}

    labels = []
    data = []
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime(date_format)
        labels.append(date_str)

        count = orders_dict.get(current_date.strftime('%Y-%m-%d'), 0)
        data.append(count)

        current_date += timedelta(days=1)

    return jsonify({
        'labels': labels,
        'data': data,
        'period': period
    })


def time_ago(timestamp):
    now = datetime.now()
    diff = now - timestamp

    # Вычисляем разницу в разных единицах времени
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    weeks = days // 7
    months = days // 30
    years = days // 365

    if seconds < 60:
        return 'только что'
    elif minutes < 60:
        return f'{int(minutes)} минут назад'
    elif hours < 24:
        return f'{int(hours)} часов назад'
    elif days < 7:
        return f'{int(days)} дней назад'
    elif weeks < 4:
        return f'{int(weeks)} недель назад'
    elif months < 12:
        return f'{int(months)} месяцев назад'
    else:
        return f'{int(years)} лет назад'

@app.context_processor
def utility_processor():
    return dict(time_ago=time_ago)


@app.route('/catalog/<int:id>')
def card(id):
    prod = Product.query.get(id)
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_product_ids = [item.product_id for item in cart_items]
        total_quantity = db.session.query(db.func.sum(CartItem.quantity)) \
            .filter(CartItem.user_id == current_user.id) \
            .scalar()
        return render_template('product.html', prod=prod,cart_product_ids=cart_product_ids,cart_count=total_quantity)
    else:
        return render_template('product.html', prod=prod)

@app.route('/catalog_news')
def catalog_news():
    page = request.args.get('page', 1, type=int)

    news_pagination = News.query.order_by(News.date.desc()).paginate(
        page=page,
        per_page=5,
        error_out=False
    )
    return render_template('catalog_news.html', news=news_pagination)

@app.route('/catalog_news/<int:id>')
def new(id):
    new=News.query.get(id)
    news = db.session.query(News).order_by(News.id.desc()).limit(3).all()
    archives = db.session.query(
        extract('year', News.date).label('year'),
        extract('month', News.date).label('month'),
        func.count(News.id).label('count')
    ).group_by(
        extract('year', News.date),
        extract('month', News.date)
    ).order_by(
        extract('year', News.date).desc(),
        extract('month', News.date).desc()
    ).all()
    formatted_archives = []
    for archive in archives:
        formatted_archives.append({
            'year': int(archive.year),
            'month': int(archive.month),
            'month_name': get_month_name(int(archive.month)),
            'count': archive.count
        })
    return render_template('new.html',new=new,news=news,archives=formatted_archives)

@app.route('/admin/edit_news')
@admin_required
def edit_news():
    page = request.args.get('page', 1, type=int)
    news_pagination = News.query.order_by(News.date.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    return render_template('admin/edit_news.html', news=news_pagination)

@app.route('/admin/edit_news/<int:id>',methods=['POST','GET'])
@admin_required
def edit_new(id):
    if request.method=='POST':
        new=News.query.get(id)
        new.title=request.form.get('title')
        new.text=request.form.get('text')
        file = request.files['file']
        if not file.filename == '':
            file.save("/app/static/News_images/" + str(new.id) + ".jpg")
            new.image = "/static/News_images/" + str(new.id) + ".jpg"
        db.session.commit()
        flash('Новость изменена', 'info')
        return redirect('/admin/edit_news')
    else:
        new=News.query.get(id)
        return render_template('admin/edit_new.html',new=new)

@app.route('/profile')
@login_required
def profile():
    orders=Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    orders_count=len(orders)
    total_spent=sum(order.total_amount for order in orders)
    cart_items_count=db.session.query(db.func.sum(CartItem.quantity)).filter(CartItem.user_id==current_user.id).scalar() or 0
    return render_template('profile.html',orders=orders,orders_count=orders_count,total_spent=total_spent,cart_items_count=cart_items_count)

@app.route('/update_profile',methods=['POST'])
@login_required
def update_profile():
    name=request.form.get('name')
    email=request.form.get('email')
    username=request.form.get('username')
    current_password=request.form.get('current_password')
    new_password=request.form.get('new_password')

    if not current_user.check_password(current_password):
        flash('Неверный текущий пароль', 'error')
        return redirect(url_for('profile')+ '#edit')
    current_user.name=name
    current_user.email=email
    current_user.username=username
    if new_password:
        current_user.set_password(new_password)
    db.session.commit()
    flash('Профиль успешно обновлен','success')
    return redirect(url_for('profile'))


@app.route('/verify_password', methods=['POST'])
@login_required
def verify_password():
    data = request.get_json()
    password = data.get('password', '')

    if current_user.check_password(password):
        return jsonify({'valid': True})
    else:
        return jsonify({'valid': False})


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'),404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error500.html'),500

