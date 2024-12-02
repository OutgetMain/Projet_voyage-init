import psycopg2

conn=psycopg2.connect(
  database="voyagedb",
  user="postgres",
  host = "localhost",
  port = 5432,
  password ="1234"
)

