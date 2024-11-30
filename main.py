import tkinter as tk

def open_booking_page():
    root.withdraw()
    booking_window = tk.Toplevel()
    booking_window.title("Бронирования")

    header = tk.Label(booking_window, text="Бронирования", font=("Arial", 24))
    header.pack(pady=20)

    add_booking_btn = tk.Button(booking_window, text="Добавить новое бронирование", width=25)
    add_booking_btn.pack(anchor='w', padx=10, pady=10)

    date_filter_label = tk.Label(booking_window, text="Фильтр по дате:")
    date_filter_label.pack(anchor='w', padx=10, pady=5)

    date_entry = tk.Entry(booking_window, width=30)
    date_entry.pack(anchor='w', padx=10, pady=5)

    status_filter_label = tk.Label(booking_window, text="Фильтр по статусу:")
    status_filter_label.pack(anchor='w', padx=10, pady=5)

    status_frame = tk.Frame(booking_window)
    status_frame.pack(anchor='w', padx=10, pady=5)

    all_btn = tk.Button(status_frame, text="Все", width=10)
    all_btn.pack(side=tk.LEFT, padx=5)

    confirmed_btn = tk.Button(status_frame, text="Подтверждено", width=15)
    confirmed_btn.pack(side=tk.LEFT, padx=5)

    current_bookings_header = tk.Label(booking_window, text="Таблица с текущими бронированиями:", font=("Arial", 18))
    current_bookings_header.pack(pady=20)

    action_frame = tk.Frame(booking_window)
    action_frame.pack(anchor='w', padx=10, pady=5)

    delete_booking_btn = tk.Button(action_frame, text="Удалить выбранное бронирование", width=30)
    delete_booking_btn.pack(side=tk.LEFT, padx=5)

    edit_booking_btn = tk.Button(action_frame, text="Редактировать", width=15)
    edit_booking_btn.pack(side=tk.LEFT, padx=5)

    back_to_main_btn = tk.Button(booking_window, text="Вернуться на главную", width=25, command=lambda: [booking_window.destroy(), root.deiconify()])
    back_to_main_btn.pack(pady=10)

def open_room_page():
    root.withdraw()
    room_window = tk.Toplevel()
    room_window.title("Номера")

    header = tk.Label(room_window, text="Номера", font=("Arial", 24))
    header.pack(pady=20)

    add_room_btn = tk.Button(room_window, text="Добавить новый номер", width=25)
    add_room_btn.pack(anchor='w', padx=10, pady=10)

    current_rooms_header = tk.Label(room_window, text="Таблица номеров", font=("Arial", 18))
    current_rooms_header.pack(pady=20)

    action_frame = tk.Frame(room_window)
    action_frame.pack(anchor='w', padx=10, pady=5)

    delete_room_btn = tk.Button(action_frame, text="Удалить выбранный номер", width=30)
    delete_room_btn.pack(side=tk.LEFT, padx=5)

    edit_room_btn = tk.Button(action_frame, text="Редактировать номер", width=15)
    edit_room_btn.pack(side=tk.LEFT, padx=5)

    back_to_main_btn = tk.Button(room_window, text="Вернуться на главную", width=25, command=lambda: [room_window.destroy(), root.deiconify()])
    back_to_main_btn.pack(pady=10)

def open_guest_page():
    root.withdraw()
    guest_window = tk.Toplevel()
    guest_window.title("Гости")

    header = tk.Label(guest_window, text="Гости", font=("Arial", 24))
    header.pack(pady=20)

    add_guest_btn = tk.Button(guest_window, text="Добавить нового гостя", width=25)
    add_guest_btn.pack(anchor='w', padx=10, pady=10)

    current_guests_header = tk.Label(guest_window, text="Таблица гостей", font=("Arial", 18))
    current_guests_header.pack(pady=20)

    action_frame = tk.Frame(guest_window)
    action_frame.pack(anchor='w', padx=10, pady=5)

    delete_guest_btn = tk.Button(action_frame, text="Удалить выбранного гостя", width=30)
    delete_guest_btn.pack(side=tk.LEFT, padx=5)

    edit_guest_btn = tk.Button(action_frame, text="Редактировать данные", width=15)
    edit_guest_btn.pack(side=tk.LEFT, padx=5)

    back_to_main_btn = tk.Button(guest_window, text="Вернуться на главную", width=25, command=lambda: [guest_window.destroy(), root.deiconify()])
    back_to_main_btn.pack(pady=10)

def main_page():
    global root
    root = tk.Tk()
    root.title("Информационная система для гостиницы")

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

    available_rooms = tk.Label(stats_frame, text="Количество доступных номеров: 10")
    available_rooms.pack()

    booked_rooms = tk.Label(stats_frame, text="Количество забронированных номеров: 5")
    booked_rooms.pack()

    registered_guests = tk.Label(stats_frame, text="Количество зарегистрированных гостей: 20")
    registered_guests.pack()

    add_room_btn = tk.Button(root, text="Добавить новый номер", width=20)
    add_room_btn.pack(pady=10)

    exit_btn = tk.Button(root, text="Выход", width=20, command=root.quit)
    exit_btn.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_page()