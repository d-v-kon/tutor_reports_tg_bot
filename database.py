import psycopg
from datetime import datetime


def send_new_record(new_data: str, teacher_id: int):
    date_of_lesson, lesson_type, lesson_students = new_data.splitlines()
    date_of_record = datetime.now()

    if len(lesson_students.split(",")) >= 4:
        lesson_salary = 400
    elif lesson_type.split()[0] == "Індивідуальні" or len(lesson_students.split(",")) >= 2:
        lesson_salary = 300
    else:
        lesson_salary = 150

    with psycopg.connect("dbname=repeat-school user=postgres password=1234") as db_conn:
        with db_conn.cursor() as cur:
            cur.execute("""
            UPDATE 
                teacher_account
            SET
                total_lessons_counter = total_lessons_counter + 1
            WHERE
                teacher_telegram_id = %s
                """, (teacher_id,))

        with db_conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO 
                            lesson_record (teacher_telegram_id,
                                        lesson_type,
                                        lesson_students,
                                        lesson_salary,
                                        date_of_lesson,
                                        date_of_record)
                        VALUES (%s,
                                %s,
                                %s,
                                %s,
                                %s,
                                %s)
                            """, (teacher_id,
                                  lesson_type,
                                  lesson_students,
                                  lesson_salary,
                                  date_of_lesson,
                                  date_of_record))


def export_from_db(requested_data: str):
    pass


def get_last_lesson(teacher_id: int):
    with psycopg.connect("dbname=repeat-school user=postgres password=1234") as db_conn:
        with db_conn.cursor() as cur:
            last_lesson_raw_record = cur.execute("""
            SELECT 
                date_of_lesson,
                lesson_type,
                lesson_students
            FROM
                lesson_record
            WHERE
                %s IN (teacher_telegram_id)
            ORDER BY date_of_lesson DESC
            LIMIT 1
                """, (teacher_id,)).fetchone()

        last_lesson_date = last_lesson_raw_record[0].strftime("%d/%m/%Y")
        last_lesson_type = last_lesson_raw_record[1]
        last_lesson_student = last_lesson_raw_record[2]

        last_lesson_record = f'{last_lesson_date} \n {last_lesson_type} \n {last_lesson_student}'

    return last_lesson_record


def edit_table():
    action = input(f'What do you want to do? \n')
    if action == 'Add teacher':
        teacher_name = input("Teacher's name:")
        teacher_telegram_id = input("Teacher's telegram id")
        add_teacher(teacher_name, teacher_telegram_id)


def add_teacher(teacher_name, teacher_telegram_id):
    with psycopg.connect("dbname=repeat-school user=postgres password=1234") as db_conn:
        with db_conn.cursor() as cur:
            cur.execute("""
            INSERT INTO 
                teacher_account (teacher_name,
                                teacher_telegram_id,
                                total_lessons_counter)
            VALUES (%s,
                    %s,
                    %s)""", (teacher_name, teacher_telegram_id, 0))


def main():
    with psycopg.connect("dbname=repeat-school user=postgres password=1234") as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute("""
                                    CREATE TABLE IF NOT EXISTS teacher_account (
                                        id serial PRIMARY KEY,
                                        teacher_name VARCHAR(255) NOT NULL,
                                        teacher_telegram_id INT NOT NULL,
                                        total_lessons_number INT NOT NULL
                                        );

                                    CREATE TABLE IF NOT EXISTS lesson_record (
                                        id serial PRIMARY KEY,
                                        teacher_telegram_id INT NOT NULL,
                                        lesson_type VARCHAR(255) NOT NULL,
                                        lesson_students VARCHAR(255) NOT NULL,
                                        lesson_salary NUMERIC(12, 2) NOT NULL,
                                        date_of_lesson TIMESTAMP NOT NULL,
                                        date_of_record TIMESTAMP NOT NULL
                                        )
                                    """)

    running = True
    while running:
        edit_table()


if __name__ == "__main__":
    main()
