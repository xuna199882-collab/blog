from app.db import Base, engine
from app.models import user   # noqa，触发模型注册

Base.metadata.create_all(engine)
print("tables created")