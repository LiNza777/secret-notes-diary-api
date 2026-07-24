from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

DATABASE_URL = settings.DATABASE_URL

# Создаем движок (Engine) для работы с базой данных.
engine = create_engine(DATABASE_URL) 

# Фабрика сессий. Именно она создает "кладовщика" (db) для каждого запроса.
# Мы явно отключаем autocommit и autoflush, чтобы SQLAlchemy не делала хаотичных автоматических записей
# на диск до того, как мы сами напишем команду db.commit() в нашем коде.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Декларативная база. От неё будут наследоваться модели User и Note, 
# которые выбраны в Canvas, чтобы SQLAlchemy могла автоматически сгенерировать таблицы.
class Base(DeclarativeBase):
    pass

# Зависимость (Dependency) для получения сессии базы данных на время выполнения HTTP-запроса.
# FastAPI перехватывает управление, создает сессию, отдает ее в роутер (yield db), 
# а после отправки ответа клиенту ГАРАНТИРОВАННО заходит в блок finally и закрывает сессию (db.close()).
# Это защищает твой сервер от утечки соединений, которую мы разбирали в тесте.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()