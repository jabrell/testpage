from app.database_access import DatabaseAccessLayer
from app.settings import db_url

if __name__ == "__main__":
    dal = DatabaseAccessLayer(db_url)
    session = dal.session
    print(session)
    print("done")
