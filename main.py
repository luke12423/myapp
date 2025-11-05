# Импортируем Flask
from flask import Flask

# Создаём экземпляр приложения Flask
app = Flask(__name__)

# Определяем маршрут для главной страницы
@app.route("/index")
def home():
    return "Привет, мир! Flask работает!"  # Возвращаем текст в браузер

# Запускаем сервер
if __name__ == "__main__":
    app.run()
