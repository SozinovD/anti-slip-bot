table_rec = '''CREATE TABLE records
                (id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                date_ts INTEGER NOT NULL,
                happiness INTEGER NOT NULL,
                comment varchar(100))
                '''

table_settings = '''CREATE TABLE settings
                    (id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    send_messages BOOL NOT NULL,
                    tz INTEGER NOT NULL,
                    worktime varchar(100),
                    period_sec INTEGER NOT NULL,
                    messages varchar(1000),
                    next_window_start_ts INTEGER NOT NULL
                    )'''

tables_arr = [ table_rec, table_settings ]
