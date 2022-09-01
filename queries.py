create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER AUTO_INCREMENT,
    id_tg INTEGER PRIMARY KEY NOT NULL
);
"""

create_dictionary_table = """
CREATE TABLE IF NOT EXISTS dictionary (
    id_user INTEGER NOT NULL,
    word TEXT NOT NULL,
    translation TEXT NOT NULL,
    status INTEGER NOT NULL,
    CONSTRAINT new_pk PRIMARY KEY (id_user, word)
    FOREIGN KEY (id_user) REFERENCES users (id_tg)
    )
"""

print_all_records = """
SELECT word, translation
FROM dictionary
WHERE id_user = {}
"""

get_reords_by_status = """
SELECT word, translation
FROM dictionary
WHERE id_user = {0} and status = {1}
"""

delete_record = """
DELETE FROM dictionary WHERE id_user = {0} and word = '{1}'
"""

insert_record = """
INSERT INTO
    dictionary (id_user, word, translation, status)
VALUES
    ({0}, '{1}', '{2}', {3})
"""

check_user_existence = """
SELECT id_tg
FROM users
WHERE id_tg = {0}
"""

insert_user = """
INSERT INTO
    users (id_tg)
VALUES
    ({0})
"""

delete_user = """
DELETE FROM users WHERE id_tg = {}
"""

check_unique_record = """
SELECT word
FROM dictionary
WHERE id_user = {0} and word = '{1}'
"""

change_status_all_records = """
UPDATE dictionary
SET status = 1
WHERE id_user = {} and status = 0
"""

change_status_one_record = """
UPDATE dictionary
SET status = 1
WHERE id_user = {} and word = {}
"""

check_record_existence = """
SELECT word
FROM dictionary
WHERE id_user = {} and word = '{}'
"""

print_all_users = """
SELECT *
FROM users
"""

delete_all = """
DELETE FROM dictionary WHERE id_user = {}
"""
