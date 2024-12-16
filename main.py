import tkinter as tk
from tkinter import simpledialog, messagebox
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def connect_to_db(user_login, user_password):
    try:

        conn = psycopg2.connect(dbname="projectdb", user=user_login, password=user_password, host="localhost")
        cursor = conn.cursor()

        cursor.execute("SELECT current_user")
        current_user = cursor.fetchone()[0]
        messagebox.showinfo("Подключение", f"Подключение прошло успешно! Подключены как {current_user}.")

        cursor.close()
        conn.close()

        open_main_window(user_login, user_password)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")


def create_user(user_login, user_password):
    try:

        conn = psycopg2.connect(dbname="projectdb", user="alexkulbyakov")
        cursor = conn.cursor()

        cursor.execute(sql.SQL("CALL create_user_if_not_exists(%s, %s);"), [user_login, user_password])

        conn.commit()

        messagebox.showinfo("Регистрация", f"Пользователь {user_login} был создан или уже существует.")

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при создании пользователя: {str(e)}")


def check_and_connect_user(user_login, user_password):
    try:

        conn = psycopg2.connect(dbname="projectdb", user="alexkulbyakov", host="localhost")
        cursor = conn.cursor()

        cursor.execute("CALL check_and_connect_user(%s, %s);", (user_login, user_password))

        conn.commit()

        connect_to_db(user_login, user_password)

        cursor.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Ошибка подключения", f"Ошибка при подключении: {str(e)}")


# Функция для подключения
def on_connect():
    user_login = simpledialog.askstring("Подключение", "Введите логин пользователя:")
    user_password = simpledialog.askstring("Подключение", "Введите пароль пользователя:", show="*")

    if user_login and user_password:
        try:
            check_and_connect_user(user_login, user_password)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")
    else:
        messagebox.showwarning("Ошибка", "Введите логин и пароль.")


def on_register():
    user_login = simpledialog.askstring("Регистрация", "Введите логин пользователя:")
    user_password = simpledialog.askstring("Регистрация", "Введите пароль пользователя:", show="*")

    if user_login and user_password:
        create_user(user_login, user_password)
    else:
        messagebox.showwarning("Ошибка", "Введите логин и пароль.")


def open_main_window(user_login, user_password):
    DATABASE_URL = f"postgresql+psycopg2://{user_login}:{user_password}@localhost:5432/projectdb"
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        engine.connect()
        print("Соединение с базой данных успешно.")
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        exit()

    def search_by_adress(adress):
        try:
            stmt = text(f"SELECT * FROM search_by_adress(:adress)")
            result = session.execute(stmt, {"adress": adress}).fetchall()

            if result:
                display_in_new_window_by_adress(result, adress)
            else:
                messagebox.showinfo(f"Содержимое поля {adress}", "Поле пусто.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def display_in_new_window_by_adress(data, adress):

        new_window = tk.Toplevel()
        new_window.title(f"Содержимое поля {adress}")
        new_window.geometry("600x400")

        text_box = tk.Text(new_window, wrap=tk.WORD, width=80, height=20)
        text_box.pack(pady=10)

        result_text = "\n".join([str(row) for row in data])
        text_box.insert(tk.END, result_text)
        text_box.config(state=tk.DISABLED)

        close_button = tk.Button(new_window, text="Закрыть", command=new_window.destroy)
        close_button.pack(pady=5)

    def call_display_table_function(table_name):
        try:
            stmt = text(f"SELECT * FROM display_table(:table_name)")
            result = session.execute(stmt, {"table_name": table_name}).fetchall()

            if result:
                display_in_new_window_table(result, table_name)
            else:
                messagebox.showinfo(f"Содержимое таблицы {table_name}", "Таблица пуста.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def display_in_new_window_table(data, table_name):

        new_window = tk.Toplevel()
        new_window.title(f"Содержимое таблицы {table_name}")
        new_window.geometry("600x400")

        text_box = tk.Text(new_window, wrap=tk.WORD, width=80, height=20)
        text_box.pack(pady=10)

        result_text = "\n".join([str(row) for row in data])
        text_box.insert(tk.END, result_text)
        text_box.config(state=tk.DISABLED)

        close_button = tk.Button(new_window, text="Закрыть", command=new_window.destroy)
        close_button.pack(pady=5)

    def add_visitor(Id, surname, first_name, last_name, adress):
        try:

            stmt = text("""
                CALL add_for_visitors(:id,:surname, :first_name, :last_name, :adress)
            """)
            session.execute(stmt, {
                "id": Id,
                "surname": surname,
                "first_name": first_name,
                "last_name": last_name,
                "adress": adress
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    # Окно для добавления нового посетителя
    def add_visitor_window():

        Id = simpledialog.askstring("Добавить посетителя", "Введите id:")
        if not Id: return

        surname = simpledialog.askstring("Добавить посетителя", "Введите фамилию:")
        if not surname: return

        first_name = simpledialog.askstring("Добавить посетителя", "Введите имя:")
        if not first_name: return

        last_name = simpledialog.askstring("Добавить посетителя", "Введите отчество:")
        if not last_name: return

        adress = simpledialog.askstring("Добавить посетителя", "Введите адрес:")
        if not adress: return

        add_visitor(Id, surname, first_name, last_name, adress)

    def add_employees(Id, surname, first_name, last_name, adress, experience_in_years):
        try:

            stmt = text("""
                CALL add_for_employees(:id,:surname, :first_name, :last_name, :adress,:experience_in_years)
            """)
            session.execute(stmt, {
                "id": Id,
                "surname": surname,
                "first_name": first_name,
                "last_name": last_name,
                "adress": adress,
                "experience_in_years": experience_in_years
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def add_employees_window():

        Id = simpledialog.askstring("Добавить работника", "Введите id:")
        if not Id: return

        surname = simpledialog.askstring("Добавить работника", "Введите фамилию:")
        if not surname: return

        first_name = simpledialog.askstring("Добавить работника", "Введите имя:")
        if not first_name: return

        last_name = simpledialog.askstring("Добавить работника", "Введите отчество:")
        if not last_name: return

        adress = simpledialog.askstring("Добавить работника", "Введите адрес:")
        if not adress: return

        experience_in_years = simpledialog.askstring("Добавить работника", "Введите опыт работы:")
        if not add_employees: return

        add_employees(Id, surname, first_name, last_name, adress, experience_in_years)

    def add_services(Id, name):
        try:

            stmt = text("""
                CALL add_for_services(:id,:name)
            """)
            session.execute(stmt, {
                "id": Id,
                "name": name
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def add_services_window():

        Id = simpledialog.askstring("Добавить сервис", "Введите id:")
        if not Id: return

        name = simpledialog.askstring("Добавить сервис", "Введите наименование сервиса:")
        if not name: return

        add_services(Id, name)

    def add_visit(Id, visitor, purpose, status, employee, date):
        try:

            stmt = text("""
                CALL add_for_visit(:id, :visitor, :purpose, :status, :employee, :date)
            """)
            session.execute(stmt, {
                "id": Id,
                "visitor": visitor,
                "purpose": purpose,
                "status": status,
                "employee": employee,
                "date": date
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def add_visit_window():

        Id = simpledialog.askstring("Добавить визит", "Введите id:")
        if not Id: return

        visitor = simpledialog.askstring("Добавить визит", "Введите id посетителя:")
        if not visitor: return

        purpose = simpledialog.askstring("Добавить визит", "Введите id сервиса:")
        if not purpose: return

        status = simpledialog.askstring("Добавить визит", "Введите статус:")
        if not status: return

        employee = simpledialog.askstring("Добавить визит", "Введите id работника:")
        if not employee: return

        date = simpledialog.askstring("Добавить визит", "Введите дату:")
        if not date: return

        add_visit(Id, visitor, purpose, status, employee, date)

    def update_visitors(Id, surname, first_name, last_name, adress):
        try:

            stmt = text("""
                CALL update_visitors(:id, :surname, :first_name, :last_name, :adress)
            """)
            session.execute(stmt, {
                "id": Id,
                "surname": surname,
                "first_name": first_name,
                "last_name": last_name,
                "adress": adress
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def update_visitors_window():
        # Ввод данных через простые диалоговые окна
        Id = simpledialog.askstring("Обновить данные посетителей", "Введите id посетителя:")
        if not Id: return

        surname = simpledialog.askstring("Обновить данные посетителей", "Введите новую фамилию посетителя:")
        if not surname: return

        first_name = simpledialog.askstring("Обновить данные посетителей", "Введите новое имя посетителя:")
        if not first_name: return

        last_name = simpledialog.askstring("Обновить данные посетителей", "Введите новое отчество посетителя:")
        if not last_name: return

        adress = simpledialog.askstring("Обновить данные посетителей", "Введите новый адрес посетителя:")
        if not adress: return

        update_visitors(Id, surname, first_name, last_name, adress)

    def update_services(Id, name):
        try:

            stmt = text("""
                CALL update_services(:id, :name)
            """)
            session.execute(stmt, {
                "id": Id,
                "name": name,
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def update_services_window():

        Id = simpledialog.askstring("Обновить данные cервиса", "Введите id сервиса:")
        if not Id: return

        name = simpledialog.askstring("Обновить данные сервиса", "Введите новое наименование сервиса:")
        if not name: return

        update_services(Id, name)

    def update_employees(Id, surname, first_name, last_name, adress, experience_in_years):
        try:

            stmt = text("""
                CALL update_employees(:id, :surname, :first_name, :last_name, :adress, :experience_in_years)
            """)
            session.execute(stmt, {
                "id": Id,
                "surname": surname,
                "first_name": first_name,
                "last_name": last_name,
                "adress": adress,
                "experience_in_years": experience_in_years
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def update_employees_window():

        Id = simpledialog.askstring("Обновить данные работника", "Введите id работника:")
        if not Id: return

        surname = simpledialog.askstring("Обновить данные работника", "Введите новую фамилию работника:")
        if not surname: return

        first_name = simpledialog.askstring("Обновить данные работника", "Введите новое имя работника:")
        if not first_name: return

        last_name = simpledialog.askstring("Обновить данные работника", "Введите новую фамилию работника:")
        if not last_name: return

        adress = simpledialog.askstring("Обновить данные работника", "Введите новый адрес работника:")
        if not adress: return

        experience_in_years = simpledialog.askstring("Обновить данные работника", "Введите новый стаж работы:")
        if not experience_in_years: return

        update_employees(Id, surname, first_name, last_name, adress, experience_in_years)

    def update_visit(Id, visitor, purpose, status, employee, date):
        try:

            stmt = text("""
                CALL update_visit(:id, :visitor, :purpose, :status, :employee, :date)
            """)
            session.execute(stmt, {
                "id": Id,
                "visitor": visitor,
                "purpose": purpose,
                "status": status,
                "employee": employee,
                "date": date
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def update_visit_window():

        Id = simpledialog.askstring("Обновить данные визита", "Введите id визита:")
        if not Id: return

        visitor = simpledialog.askstring("Обновить данные визита", "Введите новый id посетителя:")
        if not visitor: return

        purpose = simpledialog.askstring("Обновить данные визита", "Введите новое id цели:")
        if not purpose: return

        status = simpledialog.askstring("Обновить данные визита", "Введите новый статус визита:")
        if not status: return

        employee = simpledialog.askstring("Обновить данные визита", "Введите новый id работника:")
        if not employee: return

        date = simpledialog.askstring("Обновить данные визита", "Введите новую дату визита:")
        if not date: return

        update_visit(Id, visitor, purpose, status, employee, date)

    def delete_by_adress(adress):
        try:

            stmt = text("""
                CALL delete_adress(:adress)
            """)
            session.execute(stmt, {
                "adress": adress
            })
            session.commit()
            messagebox.showinfo("Успех", "Данные успешно удалены.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def delete_by_adress_window():

        adress = simpledialog.askstring("Удалить данные по адресу", "Введите адресс:")
        if not adress: return

        delete_by_adress(adress)

    def delete_visitors_cascade(Id):
        try:

            stmt = text("""
                CALL delete_visitors_cascade(:id)
            """)
            session.execute(stmt, {
                "id": Id,
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно удалена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def delete_visitors_cascade_window():

        Id = simpledialog.askstring("Удалить данные посетителя", "Введите id посетителя:")
        if not Id: return

        delete_visitors_cascade(Id)

    def delete_employees_cascade(Id):
        try:

            stmt = text("""
                CALL delete_employees_cascade(:id)
            """)
            session.execute(stmt, {
                "id": Id,
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно удалена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def delete_employees_cascade_window():

        Id = simpledialog.askstring("Удалить данные работника", "Введите id работника:")
        if not Id: return

        delete_employees_cascade(Id)

    def delete_services_cascade(Id):
        try:

            stmt = text("""
                CALL delete_services_cascade(:id)
            """)
            session.execute(stmt, {
                "id": Id,
            })
            session.commit()
            messagebox.showinfo("Успех", "Запись успешно удалена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def delete_services_cascade_window():

        Id = simpledialog.askstring("Удалить данные сервиса", "Введите id сервиса:")
        if not Id: return

        delete_services_cascade(Id)

    def delete_one_table(name):
        try:

            stmt = text("""
                CALL drop_table_by_name(:name)
            """)
            session.execute(stmt, {
                "name": name,
            })
            session.commit()
            messagebox.showinfo("Успех", "Таблица успешно удалена.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def delete_one_table_window():

        name = simpledialog.askstring("Удалить таблицу", "Введите имя таблицы:")
        if not name: return

        delete_one_table(name)

    def delete_all_tables():
        try:

            stmt = text("""
                CALL drop_all_tables()
            """)

            session.commit()
            messagebox.showinfo("Успех", "Таблицы успешно.")
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            messagebox.showerror("Ошибка запроса", f"Ошибка выполнения запроса:\n{e}")

    def search_field():
        adress = simpledialog.askstring("Поиск по адресу", "Введите адрес:")
        if adress:
            search_by_adress(adress)

    def display_table_field():
        table_name = simpledialog.askstring("Вывод содержимого таблицы", "Введите название таблицы:")
        if table_name:
            call_display_table_function(table_name)

    def open_add_field_window():
        # Создание второго окна с дополнительными кнопками
        add_field_window = tk.Toplevel()
        add_field_window.title("Добавить поле")
        add_field_window.geometry("400x500")

        btn_add_visitor = tk.Button(add_field_window, text="Добавить посетителя", command=add_visitor_window, width=30,
                                    height=2, bg="lightblue")
        btn_add_visitor.pack(pady=10)

        btn_add_employees = tk.Button(add_field_window, text="Добавить работника", command=add_employees_window,
                                      width=30, height=2, bg="lightblue")
        btn_add_employees.pack(pady=10)

        btn_add_services = tk.Button(add_field_window, text="Добавить сервис", command=add_services_window, width=30,
                                     height=2, bg="lightblue")
        btn_add_services.pack(pady=10)

        btn_add_visit = tk.Button(add_field_window, text="Добавить визит", command=add_visit_window, width=30, height=2,
                                  bg="lightblue")
        btn_add_visit.pack(pady=10)

        btn_close = tk.Button(add_field_window, text="Закрыть", command=add_field_window.destroy, width=30, height=2,
                              bg="lightgray")
        btn_close.pack(pady=10)

    def open_update_window():

        update_window = tk.Toplevel()
        update_window.title("Обновить кортеж")
        update_window.geometry("400x500")

        btn_update_visitors = tk.Button(update_window, text="Обновить посетителя", command=update_visitors_window,
                                        width=30, height=2, bg="lightblue")
        btn_update_visitors.pack(pady=10)

        btn_update_employees = tk.Button(update_window, text="Обновить работника", command=update_employees_window,
                                         width=30, height=2, bg="lightblue")
        btn_update_employees.pack(pady=10)

        btn_update_services = tk.Button(update_window, text="Обновить сервис", command=update_services_window, width=30,
                                        height=2, bg="lightblue")
        btn_update_services.pack(pady=10)

        btn_update_visit = tk.Button(update_window, text="Обновить визит", command=update_visit_window, width=30,
                                     height=2, bg="lightblue")
        btn_update_visit.pack(pady=10)

        btn_close = tk.Button(update_window, text="Закрыть", command=update_window.destroy, width=30, height=2,
                              bg="lightgray")
        btn_close.pack(pady=10)

    def open_delete_window():
        # Создание второго окна с дополнительными кнопками
        delete_window = tk.Toplevel()
        delete_window.title("Удалить данные по адресу")
        delete_window.geometry("400x500")

        btn_delete_by_adress = tk.Button(delete_window, text="Удалить данные по адресу",
                                         command=delete_by_adress_window, width=30, height=2, bg="lightblue")
        btn_delete_by_adress.pack(pady=10)

        btn_delete_visitors_cascade = tk.Button(delete_window, text="Удалить данные посетителя",
                                                command=delete_visitors_cascade_window, width=30, height=2,
                                                bg="lightblue")
        btn_delete_visitors_cascade.pack(pady=10)

        btn_delete_employees_cascade = tk.Button(delete_window, text="Удалить данные работника",
                                                 command=delete_employees_cascade_window, width=30, height=2,
                                                 bg="lightblue")
        btn_delete_employees_cascade.pack(pady=10)

        btn_delete_services_cascade = tk.Button(delete_window, text="Удалить данные сервиса",
                                                command=delete_services_cascade_window, width=30, height=2,
                                                bg="lightblue")
        btn_delete_services_cascade.pack(pady=10)

        btn_close = tk.Button(delete_window, text="Закрыть", command=delete_window.destroy, width=30, height=2,
                              bg="lightgray")
        btn_close.pack(pady=10)

    def open_delete_table_window():
        # Создание второго окна с дополнительными кнопками
        delete_table_window = tk.Toplevel()
        delete_table_window.title("Удалить таблицу/таблицы")
        delete_table_window.geometry("400x500")

        btn_delete_table = tk.Button(delete_table_window, text="Удалить выбранную таблицу",
                                     command=delete_one_table_window, width=30, height=2, bg="lightblue")
        btn_delete_table.pack(pady=10)

        bth_delete_all_tables = tk.Button(delete_table_window, text="Удалить все таблицы!!!", command=delete_all_tables,
                                          width=30, height=2, bg="lightblue")
        bth_delete_all_tables.pack(pady=10)

        # Кнопка для закрытия окна
        btn_close = tk.Button(delete_table_window, text="Закрыть", command=delete_table_window.destroy, width=30,
                              height=2, bg="lightgray")
        btn_close.pack(pady=10)

    def main_window():
        root = tk.Tk()
        root.title("Управление базой данных")
        root.geometry("400x600")

        btn_display_table = tk.Button(root, text="Вывод содержимого таблицы", command=display_table_field, width=30,
                                      height=2, bg="lightgreen")
        btn_display_table.pack(pady=5)

        btn_add_field = tk.Button(root, text="Добавить поле", command=open_add_field_window, width=30, height=2,
                                  bg="lightgreen")
        btn_add_field.pack(pady=20)

        btn_update = tk.Button(root, text="Обновить кортеж", command=open_update_window, width=30, height=2,
                               bg="lightgreen")
        btn_update.pack(pady=20)

        btn_search = tk.Button(root, text="Поиск по полю", command=search_field, width=30, height=2, bg="lightblue")
        btn_search.pack(pady=20)

        bth_delete = tk.Button(root, text="Удаление данных", command=open_delete_window, width=30, height=2,
                               bg="lightblue")
        bth_delete.pack(pady=20)

        bth_delete_table = tk.Button(root, text="Удаление таблиц", command=open_delete_table_window, width=30, height=2,
                                     bg="lightblue")
        bth_delete_table.pack(pady=20)

        btn_close = tk.Button(root, text="Закрыть", command=root.destroy, width=30, height=2, bg="lightgray")
        btn_close.pack(pady=30)

        def on_closing():
            session.close()
            root.quit()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()

    main_window()


def initial_window():
    root = tk.Tk()
    root.title("Регистрация и Подключение")
    root.geometry("400x300")

    register_button = tk.Button(root, text="Зарегистрироваться", command=on_register, width=30, height=2,
                                bg="lightgray")
    register_button.pack(pady=10)

    connect_button = tk.Button(root, text="Подключиться к БД", command=on_connect, width=30, height=2, bg="lightgray")
    connect_button.pack(pady=10)

    btn_close = tk.Button(root, text="Закрыть", command=root.destroy, width=30, height=2, bg="lightgray")
    btn_close.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    initial_window()
