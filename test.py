from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker


def get_database(host, db_name, user, password):
    """
    create existed postgre database engine and get its table with sqlalchemy

    :param host:host name, eg:'1892.168..8'
    :param db_name: postgre database's name,eg:'mydatabase'
    :param user: postgre database user's name, eg: 'myname'
    :param password: postgre databse user's password
    :return: db_engine, database engine,can used by sqlalchemy or pandas
             tables, database's tables
    """
    db_type = "mysql+pymysql"  # postgresql+psycopg2
    string = "%s://%s:%s@%s/%s" % (db_type, user, password, host, db_name)
    db_engine = create_engine(string) #, echo=False, client_encoding='utf8')
    # get sqlalchemy tables from database
    Base = automap_base()
    Base.prepare(db_engine, reflect=True)
    tables = Base.classes.dc_america_interview_days
    return db_engine, tables

host='60.205.119.77'
user="mobtop"
passwd='CSY5t6y7u8iC'
db="mobtop"

db_engine, tables = get_database(host, db, user, passwd)
print(db_engine)
print(tables)
session = sessionmaker(bind=db_engine)()
query_device = session.query(tables).first()
print(query_device.__table__)
print()