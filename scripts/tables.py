table_rec = '''CREATE TABLE records
              (id INTEGER PRIMARY KEY,
              user_id INTEGER NOT NULL,
              date_ts INTEGER NOT NULL,
              happiness INTEGER NOT NULL,
              comment varchar(100))'''

tables_arr = [ table_rec ]
