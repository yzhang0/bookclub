import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

host = 'postgres://liztyvnfvknrza:2aacdd828389a3218899db7794f58f19860d30fabbfac6e36fe16b2d9e87206f@ec2-107-22-169-45.compute-1.amazonaws.com:5432/d2b89pa095fjbd'
engine = create_engine(host)
db = scoped_session(sessionmaker(bind=engine))

books_col = {"isbn": "VARCHAR","title": "VARCHAR","author": "VARCHAR","year": "INTEGER"}
reviews_col = {"user_name": "VARCHAR","book_id": "INTEGER","rating": "INTEGER","comment": "VARCHAR"}
users_col = {"name": "VARCHAR UNIQUE","password": "VARCHAR","email": "VARCHAR","sex": "VARCHAR"}


def create_table(tablename, values):
  text = "DROP TABLE IF EXISTS " + tablename + ";"
  text += " CREATE TABLE " + tablename+ " ("
  text += "id SERIAL PRIMARY KEY,"
  for k, v in values.iteritems():
    if not k in ["rating", "comment"]:
      text += k + " " + v + " NOT NULL, "
    else:
      text += k + " " + v + ", "
  text = text[:-2]
  text += ");"
  print text
  db.execute(text)
  db.commit()

def insert(tablename, file):
  f = open(file)
  reader = csv.reader(f)
  for isbn,title,author,year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
              {"isbn": isbn, "title": title, "author": author, "year": year})
  db.commit()

def main():
    # create_table("books", books_col)
    # insert("books", "books.csv")
    # create_table("users", users_col)
    create_table("reviews", reviews_col)

if __name__ == "__main__":
    main()
