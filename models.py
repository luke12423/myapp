from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
import random

db=SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id=db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100),default='')
    email = db.Column(db.String(100), nullable=False, unique=True)
    username=db.Column(db.String(50), nullable=False, unique=True)
    password_hash=db.Column(db.String(200), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_seen = db.Column(db.DateTime, default=datetime.now)
    google_id = db.Column(db.String(100), unique=True)

    cart_items=db.relationship('CartItem',backref='user',lazy=True,cascade='all,delete-orphan')

    def update_last_seen(self):
        self.last_seen = datetime.now()
        db.session.commit()

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    name=db.Column(db.String(50), nullable=False,unique=True)
    description=db.Column(db.Text, nullable=False)
    category=db.Column(db.String(50))
    price=db.Column(db.Integer(),nullable=False)
    image=db.Column(db.String(50),nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_deleted=db.Column(db.Boolean,default=False)
    def __repr__(self):
        return f'Product : {self.name}'

class CartItem(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    product_id=db.Column(db.Integer,db.ForeignKey('product.id'), nullable=False)
    quantity=db.Column(db.Integer, default=1)

    product=db.relationship('Product',backref='cart_items')

class News(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    date=db.Column(db.DateTime,default=datetime.now)
    text=db.Column(db.Text,nullable=False)
    image=db.Column(db.String(50),nullable=False)

    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    author=db.relationship('User',backref=db.backref('news',lazy=True))

    def __repr__(self):
        return '<Article %r>' % self.id


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    shipping_address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))

    # Связи
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship('Product', backref='order_items')

def populate_database():
    """Функция для заполнения базы данных тестовыми данными"""

    # Создание пользователей
    users_data = [
        {
            'name': 'Администратор Системы',
            'email': 'admin@example.com',
            'username': 'admin',
            'password': 'admin',
            'is_admin': True,
            'created_at': datetime.now() - timedelta(days=365)
        },
        {
            'name': 'Иван Петров',
            'email': 'ivan@example.com',
            'username': 'ivan',
            'password': 'user123',
            'is_admin': False,
            'created_at': datetime.now() - timedelta(days=180)
        },
        {
            'name': 'Мария Сидорова',
            'email': 'maria@example.com',
            'username': 'maria',
            'password': 'user123',
            'is_admin': False,
            'created_at': datetime.now() - timedelta(days=120)
        },
        {
            'name': 'Алексей Козлов',
            'email': 'alex@example.com',
            'username': 'alex',
            'password': 'user123',
            'is_admin': False,
            'created_at': datetime.now() - timedelta(days=90)
        },
        {
            'name': 'Анна Новикова',
            'email': 'anna.novikova@inbox.ru',
            'username': 'anna_n',
            'password': 'AnnaSafe321!',
            'is_admin': False,
            'created_at': datetime.now() - timedelta(days=60)
        },
        {
            'name': 'Сергей Петров',
            'email': 's.petrov@company.org',
            'username': 'sergey_p',
            'password': 'Sergey2024!',
            'is_admin': False,
            'created_at': datetime.now() - timedelta(days=30)
        }
    ]

    users = []
    for user_data in users_data:
        user = User(
            name=user_data['name'],
            email=user_data['email'],
            username=user_data['username'],
            is_admin=user_data['is_admin'],
            created_at=user_data['created_at'],
            last_seen = datetime.now() - timedelta(days=random.randint(1, 30))
        )
        user.set_password(user_data['password'])
        users.append(user)
        db.session.add(user)

    db.session.commit()

    # Создание товаров
    products_data = [
        # Одежда
        {
            'name': 'Футболка хлопковая Premium Cotton',
            'description': '''Мужская футболка премиум-класса из 100% египетского хлопка. 
            Особенности: усиленные швы, двойная строчка по краям, специальная обработка против усадки. 
            Сохраняет цвет после множества стирок. Идеальна для повседневной носки и занятий спортом. 
            Мягкая ткань обеспечивает комфорт в течение всего дня.''',
            'category': 'Clothes',
            'price': 1299,
            'image': '/static/Catalog_images/tshirt.jpg'
        },
        {
            'name': 'Джинсы классические Slim Fit Premium',
            'description': '''Современные джинсы slim fit из премиального денима. 
            Эластичная ткань с добавлением лайкры обеспечивает идеальную посадку и свободу движений. 
            Экологичная обработка без использования агрессивных химикатов. 
            Усиленные карманы, металлическая фурнитура высшего качества.''',
            'category': 'Clothes',
            'price': 3499,
            'image': '/static/Catalog_images/jeans.jpg'
        },
        {
            'name': 'Куртка зимняя Extreme Warm',
            'description': '''Профессиональная зимняя куртка для экстремальных температур до -40°C. 
            Наполнитель: гусиный пух 90/10. Водонепроницаемая мембрана 20,000 мм. 
            Технологические особенности: ветрозащитные манжеты, регулируемый капюшон, 
            вентиляционные молнии, светоотражающие элементы.''',
            'category': 'Clothes',
            'price': 7999,
            'image': '/static/Catalog_images/jacket.jpg'
        },
        {
            'name': 'Платье вечернее',
            'description': 'Элегантное вечернее платье для особых случаев.',
            'category': 'Clothes',
            'price': 5999,
            'image': '/static/Catalog_images/dress.jpg'
        },

        # Спорт
        {
            'name': 'Футбольный мяч Pro Match',
            'description': '''Официальный матчевый мяч с сертификацией FIFA Quality Pro. 
            32 панели из термоскрепленного полиуретана. Бутиловая камера для оптимального отскока. 
            Идеальное сцепление с поверхностью в любых погодных условиях. 
            Используется в профессиональных лигах.''',
            'category': 'Sport',
            'price': 2499,
            'image': '/static/Catalog_images/football.jpg'
        },
        {
            'name': 'Беговая дорожка Elite Run',
            'description': '''Профессиональная беговая дорожка с двигателем 3.0 л.с. 
            Система амортизации Cushion Flex снижает нагрузку на суставы на 30%. 
            15 встроенных программ тренировок, Bluetooth-connectivity, 
            возможность синхронизации с фитнес-приложениями.''',
            'category': 'Sport',
            'price': 29999,
            'image': '/static/Catalog_images/treadmill.jpg'
        },
        {
            'name': 'Гантели наборные',
            'description': 'Набор гантелей с регулируемым весом до 20 кг.',
            'category': 'Sport',
            'price': 4599,
            'image': '/static/Catalog_images/dumbbells.jpg'
        },
        {
            'name': 'Спортивный костюм',
            'description': 'Тренировочный костюм из влагоотводящей ткани.',
            'category': 'Sport',
            'price': 3899,
            'image': '/static/Catalog_images/tracksuit.jpg'
        },

        # Товары для дома
        {
            'name': 'Кофемашина DeLonghi Magnifica',
            'description': '''Полностью автоматическая кофемашина с технологией Cappuccino System. 
            Двойные нагревательные элементы для одновременной подготовки кофе и пара. 
            13 степеней помола, память на 2 пользовательских рецепта. 
            Система автоматической очистки.''',
            'category': 'Household',
            'price': 15999,
            'image': '/static/Catalog_images/coffee_machine.jpg'
        },
        {
            'name': 'Робот-пылесос iRobot S9+',
            'description': '''Робот-пылесос премиум-класса с навигацией iAdapt 3.0 и камерой. 
            Система автоматической очистки контейнера. Работа по расписанию через приложение. 
            Технология PerfectEdge для очистки углов. Совместимость с голосовыми помощниками.''',
            'category': 'Household',
            'price': 22999,
            'image': '/static/Catalog_images/vacuum.jpg'
        },
        {
            'name': 'Набор посуды',
            'description': 'Кухонный набор из 12 предметов с антипригарным покрытием.',
            'category': 'Household',
            'price': 7899,
            'image': '/static/Catalog_images/cookware.jpg'
        },
        {
            'name': 'Электрический чайник',
            'description': 'Стеклянный электрочайник с подсветкой и терморегулятором.',
            'category': 'Household',
            'price': 2899,
            'image': '/static/Catalog_images/kettle.jpg'
        },

        # Электроника
        {
            'name': 'Смартфон Galaxy Ultra 5G',
            'description': '''Флагманский смартфон с процессором Snapdragon 8 Gen 3. 
            6.8" Dynamic AMOLED 2X дисплей с частотой 120 Гц. Основная камера 200 Мп 
            с системой стабилизации. Аккумулятор 5000 мАч с быстрой зарядкой 45 Вт. 
            Стекло Gorilla Glass Victus 2, защита IP68.''',
            'category': 'Electronics',
            'price': 89999,
            'image': '/static/Catalog_images/smartphone.jpg'
        },
        {
            'name': 'Ноутбук игровой Predator X',
            'description': '''Мощный игровой ноутбук с процессором Intel Core i9-14900HX
            и видеокартой NVIDIA GeForce RTX 4080. 16" IPS дисплей 240 Гц с покрытием 100% sRGB.
            Система охлаждения 5-го поколения с жидкометаллической термопастой.''',
            'category': 'Electronics',
            'price': 129999,
            'image': '/static/Catalog_images/laptop.jpg'
        },
        {
            'name': 'Наушники беспроводные Sony WH-1000XM5',
            'description': '''Беспроводные наушники с технологией шумоподавления премиум-класса. 
            Процессор HD Noise Canceling Processor QN1. Автономность до 30 часов. 
            Функция Quick Attention для быстрого общения. Качество звука Hi-Res Audio.''',
            'category': 'Electronics',
            'price': 12999,
            'image': '/static/Catalog_images/headphones.jpg'
        },
        {
            'name': 'Умные часы',
            'description': 'Смарт-часы с отслеживанием активности и уведомлениями.',
            'category': 'Electronics',
            'price': 15999,
            'image': '/static/Catalog_images/smartwatch.jpg'
        },
        {
            'name': 'Умный дом Xiaomi Ecosystem',
            'description': '''Комплексная система умного дома с хабом и датчиками. 
                Управление через приложение или голосовые команды. 
                В комплекте: умные лампы, датчики движения, открытия дверей, температуры. 
                Совместимость с Alexa и Google Assistant.''',
            'category': 'Household',
            'price': 15999,
            'image': '/static/Catalog_images/smarthome.jpg',
        },
        {
            'name': 'Программирование на Python',
            'description': '''Комплексный учебник по программированию на Python для начинающих и продвинутых. 
                Подробное объяснение основ и продвинутых концепций. Практические проекты и задачи. 
                Автор - опытный разработчик с 15-летним стажем.''',
            'category': 'Books',
            'price': 2499,
            'image': '/static/Catalog_images/python_book.jpg',
        },
        {
            'name': 'Курс по веб-разработке',
            'description': '''Полный курс по современной веб-разработке. 
                HTML5, CSS3, JavaScript, React, Node.js. Видеоуроки, практические задания, 
                поддержка ментора. Сертификат по окончании. Доступ на 12 месяцев.''',
            'category': 'Education',
            'price': 14999,
            'image': '/static/Catalog_images/web_course.jpg',
        }
    ]

    products = []
    for product_data in products_data:
        product = Product(
            name=product_data['name'],
            description=product_data['description'],
            category=product_data['category'],
            price=product_data['price'],
            image=product_data['image'],
            created_at=datetime.now() - timedelta(days=random.randint(1, 180))
        )
        products.append(product)
        db.session.add(product)

    db.session.commit()

    # Создание товаров в корзинах
    cart_items_data = [
        (users[1], products[0], 2),  # Иван: 2 футболки
        (users[1], products[4], 1),  # Иван: 1 футбольный мяч
        (users[2], products[12], 1),  # Мария: 1 смартфон
        (users[2], products[14], 1),  # Мария: 1 наушники
        (users[3], products[8], 1),  # Алексей: 1 кофемашина
    ]

    for user, product, quantity in cart_items_data:
        cart_item = CartItem(
            user_id=user.id,
            product_id=product.id,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()

    # Создание новостей
    news_data = [
        {
            'title': 'Открытие нового магазина',
            'text': 'Рады сообщить об открытии нашего нового магазина в центре города! Приходите на открытие и получите скидку 15% на первую покупку.',
            'image': '/static/News_images/store_opening.jpg',
            'author': users[0],
            'days_ago': 2
        },
        {
            'title': 'Скидки на электронику',
            'text': 'Специальная акция: скидки до 30% на всю электронику до конца месяца. Успейте приобрести новейшие гаджеты по выгодным ценам!',
            'image': '/static/News_images/electronics_sale.jpg',
            'author': users[0],
            'days_ago': 5
        },
        {
            'title': 'Новая коллекция одежды',
            'text': 'В продажу поступила новая весенняя коллекция одежды от ведущих брендов. Стильные и современные модели для всей семьи.',
            'image': '/static/News_images/new_collection.jpg',
            'author': users[0],
            'days_ago': 8
        },
        {
            'title': 'Бесплатная доставка',
            'text': 'Теперь при заказе от 5000 рублей доставка бесплатная! Заказывайте онлайн и получайте товары прямо к вашей двери.',
            'image': '/static/News_images/free_delivery.jpg',
            'author': users[0],
            'days_ago': 12
        }
    ]

    for news_item in news_data:
        news = News(
            title=news_item['title'],
            text=news_item['text'],
            image=news_item['image'],
            author_id=news_item['author'].id,
            date=datetime.now() - timedelta(days=news_item['days_ago'])
        )
        db.session.add(news)

    db.session.commit()

    # Создание заказов
    orders_data = [
        {
            'user': users[1],
            'total_amount': 6087,
            'status': 'delivered',
            'shipping_address': 'ул. Ленина, д. 15, кв. 42, Москва',
            'phone': '+79161234567',
            'email': 'ivan@example.com',
            'days_ago': 1,
            'items': [
                (products[0], 1, 1299),  # Футболка
                (products[4], 1, 2499),  # Футбольный мяч
                (products[5], 1, 2299)  # Беговая дорожка (частичная оплата)
            ]
        },
        {
            'user': users[2],
            'total_amount': 102998,
            'status': 'shipped',
            'shipping_address': 'пр. Мира, д. 88, Санкт-Петербург',
            'phone': '+79169876543',
            'email': 'maria@example.com',
            'days_ago': 3,
            'items': [
                (products[12], 1, 89999),  # Смартфон
                (products[14], 1, 12999)  # Наушники
            ]
        },
        {
            'user': users[3],
            'total_amount': 18898,
            'status': 'confirmed',
            'shipping_address': 'ул. Садовая, д. 25, Екатеринбург',
            'phone': '+79165554433',
            'email': 'alex@example.com',
            'days_ago': 5,
            'items': [
                (products[8], 1, 15999),  # Кофемашина
                (products[10], 1, 2899)  # Электрический чайник
            ]
        },
        {
            'user': users[1],
            'total_amount': 3499,
            'status': 'pending',
            'shipping_address': 'ул. Ленина, д. 15, кв. 42, Москва',
            'phone': '+79161234567',
            'email': 'ivan@example.com',
            'days_ago': 0.1,  # 2.4 часа назад
            'items': [
                (products[1], 1, 3499)  # Джинсы
            ]
        }
    ]

    for order_data in orders_data:
        order = Order(
            user_id=order_data['user'].id,
            total_amount=order_data['total_amount'],
            status=order_data['status'],
            shipping_address=order_data['shipping_address'],
            phone=order_data['phone'],
            email=order_data['email'],
            created_at=datetime.now() - timedelta(days=order_data['days_ago'])
        )
        db.session.add(order)
        db.session.commit()  # Коммитим, чтобы получить order.id

        # Добавляем товары в заказ
        for product, quantity, price in order_data['items']:
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=price
            )
            db.session.add(order_item)

    db.session.commit()

    print("База данных успешно заполнена тестовыми данными!")
    print(f"Создано:")
    print(f"- Пользователей: {len(users)}")
    print(f"- Товаров: {len(products)}")
    print(f"- Новостей: {len(news_data)}")
    print(f"- Заказов: {len(orders_data)}")