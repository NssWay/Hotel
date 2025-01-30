import tkinter as tk
import mysql.connector
from tkinter import messagebox
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'HOTEL'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None

def update_stats_labels(stats_frame):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM ROOMS r 
                WHERE r.room_id NOT IN (
                    SELECT room_id FROM BOOKINGS 
                    WHERE check_out_date >= CURDATE() AND check_in_date <= CURDATE()
                )
            """)
            available_rooms = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(DISTINCT room_id) FROM BOOKINGS 
                WHERE check_out_date >= CURDATE() AND check_in_date <= CURDATE()
            """)
            booked_rooms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM GUESTS")
            total_guests = cursor.fetchone()[0]

            for widget in stats_frame.winfo_children():
                widget.destroy()

            tk.Label(stats_frame, text=f"Количество доступных номеров: {available_rooms}").pack()
            tk.Label(stats_frame, text=f"Количество забронированных номеров: {booked_rooms}").pack()
            tk.Label(stats_frame, text=f"Количество зарегистрированных гостей: {total_guests}").pack()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching statistics: {err}")
        finally:
            cursor.close()
            conn.close()

def add_new_booking():
    pass

def delete_booking():
    pass

def edit_booking():
    pass

def add_new_room():
    pass

def delete_room():
    pass

def edit_room():
    pass

def add_new_guest():
    pass

def delete_guest():
    pass

def edit_guest():
    pass


def open_booking_page():
    root.withdraw()
    booking_window = tk.Toplevel()
    booking_window.title("Бронирования")
    booking_window.geometry("800x600")

    screen_width = booking_window.winfo_screenwidth()
    screen_height = booking_window.winfo_screenheight()
    position_top = int(screen_height / 2 - 600 / 2)
    position_right = int(screen_width / 2 - 800 / 2)
    booking_window.geometry(f'800x600+{position_right}+{position_top}')

    def check_room_availability(room_id, check_in, check_out, booking_id=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            if booking_id:
                cursor.execute("""
                    SELECT COUNT(*) FROM BOOKINGS 
                    WHERE room_id = %s 
                    AND booking_id != %s
                    AND (
                        (check_in_date <= %s AND check_out_date >= %s)
                        OR (check_in_date <= %s AND check_out_date >= %s)
                        OR (check_in_date >= %s AND check_out_date <= %s)
                    )
                """, (room_id, booking_id, check_in, check_in, check_out, check_out, check_in, check_out))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM BOOKINGS 
                    WHERE room_id = %s 
                    AND (
                        (check_in_date <= %s AND check_out_date >= %s)
                        OR (check_in_date <= %s AND check_out_date >= %s)
                        OR (check_in_date >= %s AND check_out_date <= %s)
                    )
                """, (room_id, check_in, check_in, check_out, check_out, check_in, check_out))

            count = cursor.fetchone()[0]
            return count == 0
        finally:
            if conn:
                conn.close()

    def add_new_booking():
        add_window = tk.Toplevel()
        add_window.title("Добавить бронирование")
        add_window.geometry("400x300")
        add_window.geometry(f'400x300+{position_right + 200}+{position_top + 150}')

        labels = ['ID гостя:', 'ID комнаты:', 'Дата заезда:', 'Дата выезда:']
        entries = {}

        for i, label_text in enumerate(labels):
            tk.Label(add_window, text=label_text).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(add_window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[label_text] = entry

        def save_new_booking():
            try:
                guest_id = entries['ID гостя:'].get()
                room_id = entries['ID комнаты:'].get()
                check_in = entries['Дата заезда:'].get()
                check_out = entries['Дата выезда:'].get()

                if not all([guest_id, room_id, check_in, check_out]):
                    messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
                    return

                if not check_room_availability(room_id, check_in, check_out):
                    messagebox.showerror("Ошибка", "Номер уже забронирован на указанные даты")
                    return

                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO BOOKINGS (guest_id, room_id, check_in_date, check_out_date)
                        VALUES (%s, %s, %s, %s)
                    """, (guest_id, room_id, check_in, check_out))
                    conn.commit()
                    messagebox.showinfo("Успех", "Бронирование успешно добавлено")
                    add_window.destroy()
                    refresh_bookings_table()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении бронирования: {str(e)}")
            finally:
                if conn:
                    conn.close()

        save_btn = tk.Button(add_window, text="Сохранить", command=save_new_booking)
        save_btn.grid(row=len(labels), column=0, columnspan=2, pady=20)

    def edit_booking():
        if selected_booking['row'] is None:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите бронирование для редактирования")
            return

        edit_window = tk.Toplevel()
        edit_window.title("Редактировать бронирование")
        edit_window.geometry("400x300")
        edit_window.geometry(f'400x300+{position_right + 200}+{position_top + 150}')

        booking_id = selected_booking['labels'][0].cget("text")
        current_values = [label.cget("text") for label in selected_booking['labels']]

        labels = ['ID бронирования:', 'ID гостя:', 'ID комнаты:', 'Дата заезда:', 'Дата выезда:']
        entries = {}

        for i, (label_text, value) in enumerate(zip(labels, current_values)):
            tk.Label(edit_window, text=label_text).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(edit_window)
            entry.insert(0, value)
            if label_text == 'ID бронирования:':
                entry.config(state='readonly')
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[label_text] = entry

        def save_changes():
            try:
                guest_id = entries['ID гостя:'].get()
                room_id = entries['ID комнаты:'].get()
                check_in = entries['Дата заезда:'].get()
                check_out = entries['Дата выезда:'].get()

                if not all([guest_id, room_id, check_in, check_out]):
                    messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
                    return

                if not check_room_availability(room_id, check_in, check_out, booking_id):
                    messagebox.showerror("Ошибка", "Номер уже забронирован на указанные даты")
                    return

                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE BOOKINGS 
                        SET guest_id = %s, room_id = %s, check_in_date = %s, check_out_date = %s
                        WHERE booking_id = %s
                    """, (guest_id, room_id, check_in, check_out, booking_id))
                    conn.commit()
                    messagebox.showinfo("Успех", "Бронирование успешно обновлено")
                    edit_window.destroy()
                    refresh_bookings_table()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении бронирования: {str(e)}")
            finally:
                if conn:
                    conn.close()

        save_btn = tk.Button(edit_window, text="Сохранить изменения", command=save_changes)
        save_btn.grid(row=len(labels), column=0, columnspan=2, pady=20)

    def refresh_bookings_table():
        for widget in table_frame.winfo_children():
            widget.destroy()

        for col, header in enumerate(headers):
            label = tk.Label(table_frame, text=header, font=('Arial', 10, 'bold'), relief=tk.RIDGE, width=15)
            label.grid(row=0, column=col, sticky='nsew')

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT booking_id, guest_id, room_id, check_in_date, check_out_date FROM BOOKINGS")
                bookings_data = cursor.fetchall()

                for row_idx, booking in enumerate(bookings_data, start=1):
                    row_labels = []
                    for col_idx, value in enumerate(booking):
                        if col_idx in [3, 4]:
                            value = value.strftime('%Y-%m-%d') if value else ''
                        label = tk.Label(table_frame, text=str(value), relief=tk.RIDGE, width=15)
                        label.grid(row=row_idx, column=col_idx, sticky='nsew')
                        row_labels.append(label)
                        label.bind('<Button-1>', lambda e, ri=row_idx, rl=row_labels: select_row(e, ri, rl))

                for i in range(len(headers)):
                    table_frame.grid_columnconfigure(i, weight=1)

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error fetching bookings data: {err}")
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    header = tk.Label(booking_window, text="Бронирования", font=("Arial", 24))
    header.pack(pady=20)

    add_booking_btn = tk.Button(booking_window, text="Добавить новое бронирование", width=25, command=add_new_booking)
    add_booking_btn.pack(anchor='w', padx=10, pady=10)

    status_frame = tk.Frame(booking_window)
    status_frame.pack(anchor='w', padx=10, pady=5)

    action_frame = tk.Frame(booking_window)
    action_frame.pack(anchor='w', padx=10, pady=5)

    selected_booking = {'row': None, 'labels': []}

    def delete_selected_booking():
        if selected_booking['row'] is not None:
            booking_id = selected_booking['labels'][0].cget("text")
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это бронирование?"):
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM BOOKINGS WHERE booking_id = %s", (booking_id,))
                        conn.commit()
                        messagebox.showinfo("Успех", "Бронирование успешно удалено")
                        refresh_bookings_table()
                    except mysql.connector.Error as err:
                        messagebox.showerror("Database Error", f"Error deleting booking: {err}")
                    finally:
                        if cursor:
                            cursor.close()
                        if conn:
                            conn.close()
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите бронирование для удаления")

    delete_booking_btn = tk.Button(action_frame, text="Удалить выбранное бронирование", width=30,
                                   command=delete_selected_booking)
    delete_booking_btn.pack(side=tk.LEFT, padx=5)

    edit_booking_btn = tk.Button(action_frame, text="Редактировать", width=15, command=edit_booking)
    edit_booking_btn.pack(side=tk.LEFT, padx=5)

    table_frame = tk.Frame(booking_window)
    table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    headers = ['ID бронирования', 'ID гостя', 'ID комнаты', 'Дата заезда', 'Дата выезда']
    for col, header in enumerate(headers):
        label = tk.Label(table_frame, text=header, font=('Arial', 10, 'bold'), relief=tk.RIDGE, width=15)
        label.grid(row=0, column=col, sticky='nsew')

    def select_row(event, row_idx, row_labels):
        if selected_booking['row'] is not None:
            for label in selected_booking['labels']:
                label.configure(bg='SystemButtonFace')

        for label in row_labels:
            label.configure(bg='lightblue')

        selected_booking['row'] = row_idx
        selected_booking['labels'] = row_labels

    refresh_bookings_table()

    back_to_main_btn = tk.Button(booking_window, text="Вернуться на главную", width=25,
                                 command=lambda: [booking_window.destroy(), root.deiconify()])
    back_to_main_btn.pack(side=tk.BOTTOM, pady=20)


def open_room_page():
    root.withdraw()
    room_window = tk.Toplevel()
    room_window.title("Номера")
    room_window.geometry("800x600")

    screen_width = room_window.winfo_screenwidth()
    screen_height = room_window.winfo_screenheight()
    position_top = int(screen_height / 2 - 600 / 2)
    position_right = int(screen_width / 2 - 800 / 2)
    room_window.geometry(f'800x600+{position_right}+{position_top}')

    selected_row = None

    def on_row_click(event):
        nonlocal selected_row
        widget = event.widget
        if widget.grid_info()['row'] > 0:
            for row in range(1, table_frame.grid_size()[1]):
                for col in range(len(headers)):
                    cell = table_frame.grid_slaves(row=row, column=col)[0]
                    cell.configure(bg='white')

            row_idx = widget.grid_info()['row']
            selected_row = row_idx
            for col in range(len(headers)):
                cell = table_frame.grid_slaves(row=row_idx, column=col)[0]
                cell.configure(bg='lightblue')

    def delete_selected_room():
        nonlocal selected_row
        if selected_row is None:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите номер для удаления")
            return

        room_id = table_frame.grid_slaves(row=selected_row, column=0)[0]['text']
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот номер?"):
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM ROOMS WHERE room_id = %s", (room_id,))
                    conn.commit()
                    refresh_table()
                    selected_row = None
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error deleting room: {err}")
                finally:
                    cursor.close()
                    conn.close()

    def edit_selected_room():
        if selected_row is None:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите номер для редактирования")
            return

        edit_window = tk.Toplevel(room_window)
        edit_window.title("Редактировать номер")
        edit_window.geometry("400x300")

        current_values = []
        for col in range(len(headers)):
            current_values.append(table_frame.grid_slaves(row=selected_row, column=col)[0]['text'])

        entries = []
        room_type_var = tk.StringVar()

        for i, header in enumerate(headers[1:], 1):
            tk.Label(edit_window, text=header).pack(pady=5)
            if header == "room_type":
                room_type_combo = ttk.Combobox(edit_window, textvariable=room_type_var,
                                               values=["single", "double", "suite"])
                room_type_combo.set(current_values[i])
                room_type_combo.pack(pady=5)
                entries.append(room_type_combo)
            else:
                entry = tk.Entry(edit_window)
                entry.insert(0, current_values[i])
                entry.pack(pady=5)
                entries.append(entry)

        def save_changes():
            new_values = [entry.get() for entry in entries]
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE ROOMS 
                        SET room_number = %s, room_type = %s, price = %s, capacity = %s 
                        WHERE room_id = %s
                    """, (*new_values, current_values[0]))
                    conn.commit()
                    refresh_table()
                    edit_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error updating room: {err}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(edit_window, text="Сохранить", command=save_changes).pack(pady=20)

    def add_new_room():
        add_window = tk.Toplevel(room_window)
        add_window.title("Добавить новый номер")
        add_window.geometry("400x300")

        entries = []
        room_type_var = tk.StringVar()

        for header in headers[1:]:
            tk.Label(add_window, text=header).pack(pady=5)
            if header == "room_type":
                room_type_combo = ttk.Combobox(add_window, textvariable=room_type_var,
                                               values=["single", "double", "suite"])
                room_type_combo.pack(pady=5)
                entries.append(room_type_combo)
            else:
                entry = tk.Entry(add_window)
                entry.pack(pady=5)
                entries.append(entry)

        def save_new_room():
            values = [entry.get() for entry in entries]
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO ROOMS (room_number, room_type, price, capacity)
                        VALUES (%s, %s, %s, %s)
                    """, values)
                    conn.commit()
                    refresh_table()
                    add_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error adding room: {err}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(add_window, text="Сохранить", command=save_new_room).pack(pady=20)

    def refresh_table():
        for widget in table_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM ROOMS")
                rooms_data = cursor.fetchall()

                for row_idx, room in enumerate(rooms_data, start=1):
                    for col_idx, value in enumerate(room):
                        label = tk.Label(table_frame, text=str(value), relief=tk.RIDGE, width=15)
                        label.grid(row=row_idx, column=col_idx, sticky='nsew')
                        label.bind('<Button-1>', on_row_click)

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error fetching rooms data: {err}")
            finally:
                cursor.close()
                conn.close()

    header = tk.Label(room_window, text="Номера", font=("Arial", 24))
    header.pack(pady=20)

    add_room_btn = tk.Button(room_window, text="Добавить новый номер", width=25, command=add_new_room)
    add_room_btn.pack(anchor='w', padx=10, pady=10)

    action_frame = tk.Frame(room_window)
    action_frame.pack(anchor='w', padx=10, pady=5)

    delete_room_btn = tk.Button(action_frame, text="Удалить выбранный номер", width=30, command=delete_selected_room)
    delete_room_btn.pack(side=tk.LEFT, padx=5)

    edit_room_btn = tk.Button(action_frame, text="Редактировать номер", width=15, command=edit_selected_room)
    edit_room_btn.pack(side=tk.LEFT, padx=5)

    table_frame = tk.Frame(room_window)
    table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    headers = ['ID', 'Номер комнаты', 'Тип комнаты', 'Цена', 'Вместимость']
    for col, header in enumerate(headers):
        label = tk.Label(table_frame, text=header, font=('Arial', 10, 'bold'), relief=tk.RIDGE, width=15)
        label.grid(row=0, column=col, sticky='nsew')

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ROOMS")
            rooms_data = cursor.fetchall()

            for row_idx, room in enumerate(rooms_data, start=1):
                for col_idx, value in enumerate(room):
                    label = tk.Label(table_frame, text=str(value), relief=tk.RIDGE, width=15)
                    label.grid(row=row_idx, column=col_idx, sticky='nsew')
                    label.bind('<Button-1>', on_row_click)

            for i in range(len(headers)):
                table_frame.grid_columnconfigure(i, weight=1)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching rooms data: {err}")
        finally:
            cursor.close()
            conn.close()

    back_to_main_btn = tk.Button(room_window, text="Вернуться на главную", width=25,
                                 command=lambda: [room_window.destroy(), root.deiconify()])
    back_to_main_btn.pack(side=tk.BOTTOM, pady=20)


def open_guest_page():
    root.withdraw()
    guest_window = tk.Toplevel()
    guest_window.title("Гости")
    guest_window.geometry("800x600")

    screen_width = guest_window.winfo_screenwidth()
    screen_height = guest_window.winfo_screenheight()
    position_top = int(screen_height / 2 - 600 / 2)
    position_right = int(screen_width / 2 - 800 / 2)
    guest_window.geometry(f'800x600+{position_right}+{position_top}')

    selected_row = tk.StringVar()

    def select_row(event):
        clicked_widget = event.widget
        if isinstance(clicked_widget, tk.Label) and clicked_widget.grid_info()['row'] > 0:
            row = clicked_widget.grid_info()['row']
            for widget in table_frame.grid_slaves():
                widget.configure(bg='white')
            for widget in table_frame.grid_slaves(row=row):
                widget.configure(bg='lightblue')
            selected_row.set(str(table_frame.grid_slaves(row=row, column=0)[0]['text']))

    def add_new_guest():
        add_window = tk.Toplevel(guest_window)
        add_window.title("Добавить гостя")
        add_window.geometry("400x300")

        fields = ['Имя:', 'Фамилия:', 'Email:', 'Телефон:', 'Адрес:']
        entries = []

        for i, field in enumerate(fields):
            tk.Label(add_window, text=field).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(add_window, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)

        def save_guest():
            values = [entry.get() for entry in entries]
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO GUESTS (first_name, last_name, email, phone, address)
                        VALUES (%s, %s, %s, %s, %s)
                    """, values)
                    conn.commit()
                    add_window.destroy()
                    refresh_table()
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"Failed to add guest: {err}")
                finally:
                    cursor.close()
                    conn.close()

        tk.Button(add_window, text="Сохранить", command=save_guest).grid(row=len(fields), column=0, columnspan=2,
                                                                         pady=20)

    def edit_guest():
        if not selected_row.get():
            messagebox.showwarning("Warning", "Пожалуйста, выберите гостя для редактирования")
            return

        edit_window = tk.Toplevel(guest_window)
        edit_window.title("Редактировать гостя")
        edit_window.geometry("400x300")

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT first_name, last_name, email, phone, address FROM GUESTS WHERE guest_id = %s",
                               (selected_row.get(),))
                guest_data = cursor.fetchone()

                fields = ['Имя:', 'Фамилия:', 'Email:', 'Телефон:', 'Адрес:']
                entries = []

                for i, (field, value) in enumerate(zip(fields, guest_data)):
                    tk.Label(edit_window, text=field).grid(row=i, column=0, padx=5, pady=5)
                    entry = tk.Entry(edit_window, width=30)
                    entry.insert(0, value)
                    entry.grid(row=i, column=1, padx=5, pady=5)
                    entries.append(entry)

                def update_guest():
                    values = [entry.get() for entry in entries]
                    values.append(selected_row.get())
                    try:
                        cursor.execute("""
                            UPDATE GUESTS 
                            SET first_name=%s, last_name=%s, email=%s, phone=%s, address=%s 
                            WHERE guest_id=%s
                        """, values)
                        conn.commit()
                        edit_window.destroy()
                        refresh_table()
                    except mysql.connector.Error as err:
                        messagebox.showerror("Error", f"Failed to update guest: {err}")

                tk.Button(edit_window, text="Сохранить", command=update_guest).grid(row=len(fields), column=0,
                                                                                    columnspan=2, pady=20)

            finally:
                cursor.close()
                conn.close()

    def delete_guest():
        if not selected_row.get():
            messagebox.showwarning("Warning", "Пожалуйста, выберите гостя для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого гостя?"):
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM GUESTS WHERE guest_id = %s", (selected_row.get(),))
                    conn.commit()
                    refresh_table()
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"Failed to delete guest: {err}")
                finally:
                    cursor.close()
                    conn.close()

    def refresh_table():
        for widget in table_frame.grid_slaves():
            if int(widget.grid_info()['row']) > 0:
                widget.destroy()

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT guest_id, first_name, last_name, email, phone, address FROM GUESTS")
                guests_data = cursor.fetchall()

                for row_idx, guest in enumerate(guests_data, start=1):
                    for col_idx, value in enumerate(guest):
                        label = tk.Label(table_frame, text=str(value), relief=tk.RIDGE, width=15)
                        label.grid(row=row_idx, column=col_idx, sticky='nsew')
                        label.bind('<Button-1>', select_row)

            finally:
                cursor.close()
                conn.close()

    header = tk.Label(guest_window, text="Гости", font=("Arial", 24))
    header.pack(pady=20)

    add_guest_btn = tk.Button(guest_window, text="Добавить нового гостя", width=25, command=add_new_guest)
    add_guest_btn.pack(anchor='w', padx=10, pady=10)

    action_frame = tk.Frame(guest_window)
    action_frame.pack(anchor='w', padx=10, pady=5)

    delete_guest_btn = tk.Button(action_frame, text="Удалить выбранного гостя", width=30, command=delete_guest)
    delete_guest_btn.pack(side=tk.LEFT, padx=5)

    edit_guest_btn = tk.Button(action_frame, text="Редактировать данные", width=30, command=edit_guest)
    edit_guest_btn.pack(side=tk.LEFT, padx=5)

    table_frame = tk.Frame(guest_window)
    table_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    headers = ['ID', 'Имя', 'Фамилия', 'Email', 'Телефон', 'Адрес']
    for col, header in enumerate(headers):
        label = tk.Label(table_frame, text=header, font=('Arial', 10, 'bold'), relief=tk.RIDGE, width=15)
        label.grid(row=0, column=col, sticky='nsew')

    refresh_table()

    for i in range(len(headers)):
        table_frame.grid_columnconfigure(i, weight=1)

    back_to_main_btn = tk.Button(guest_window, text="Вернуться на главную", width=25,
                                 command=lambda: [guest_window.destroy(), root.deiconify()])
    back_to_main_btn.pack(side=tk.BOTTOM, pady=20)


def main_page():
    global root
    root = tk.Tk()
    root.title("Информационная система для гостиницы")

    conn = get_db_connection()
    if not conn:
        root.quit()
        return
    conn.close()

    window_width = 800
    window_height = 600

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)

    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    header = tk.Label(root, text="Главная страница", font=("Arial", 24))
    header.pack(pady=20)

    navigation_frame = tk.Frame(root)
    navigation_frame.pack(pady=10)

    btn1 = tk.Button(navigation_frame, text="Бронирование", width=15, command=open_booking_page)
    btn1.pack(side=tk.LEFT, padx=5)

    btn2 = tk.Button(navigation_frame, text="Номера", width=15, command=open_room_page)
    btn2.pack(side=tk.LEFT, padx=5)

    btn3 = tk.Button(navigation_frame, text="Гости", width=15, command=open_guest_page)
    btn3.pack(side=tk.LEFT, padx=5)

    stats_header = tk.Label(root, text="Статистика гостиницы", font=("Arial", 18))
    stats_header.pack(pady=20)

    stats_frame = tk.Frame(root)
    stats_frame.pack(pady=10)

    update_stats_labels(stats_frame)

    add_room_btn = tk.Button(root, text="Добавить новый номер", width=20,
                            command=lambda: direct_add_room())
    add_room_btn.pack(pady=10)

    exit_btn = tk.Button(root, text="Выход", width=20, command=root.quit)
    exit_btn.pack(side=tk.BOTTOM, pady=20)

    root.mainloop()

def direct_add_room():
    headers = ["ID", "Номер комнаты", "Тип комнаты", "Цена", "Вместимость"]
    add_window = tk.Toplevel(root)
    add_window.title("Добавить новый номер")
    add_window.geometry("400x300")

    entries = []
    for header in headers[1:]:
        tk.Label(add_window, text=header).pack(pady=5)
        entry = tk.Entry(add_window)
        entry.pack(pady=5)
        entries.append(entry)

    def save_new_room():
        values = [entry.get() for entry in entries]
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ROOMS (room_number, room_type, price, capacity)
                    VALUES (%s, %s, %s, %s)
                """, values)
                conn.commit()
                messagebox.showinfo("Успех", "Номер успешно добавлен")
                add_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error adding room: {err}")
            finally:
                cursor.close()
                conn.close()

    tk.Button(add_window, text="Сохранить", command=save_new_room).pack(pady=20)

def combined_room_actions():
    global room_window
    open_room_page()
    add_new_room()

def add_new_room():
    headers = ["ID", "Номер комнаты", "Тип комнаты", "Цена", "Вместимость"]
    add_window = tk.Toplevel(room_window)
    add_window.title("Добавить новый номер")
    add_window.geometry("400x300")

    entries = []
    for header in headers[1:]:
        tk.Label(add_window, text=header).pack(pady=5)
        entry = tk.Entry(add_window)
        entry.pack(pady=5)
        entries.append(entry)

    def save_new_room():
        values = [entry.get() for entry in entries]
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ROOMS (room_number, room_type, price, capacity)
                    VALUES (%s, %s, %s, %s)
                """, values)
                conn.commit()
                refresh_table()
                add_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error adding room: {err}")
            finally:
                cursor.close()
                conn.close()

    tk.Button(add_window, text="Сохранить", command=save_new_room).pack(pady=20)

if __name__ == "__main__":
    main_page()