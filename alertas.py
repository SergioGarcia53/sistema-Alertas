import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import schedule
import time
from threading import Thread
from datetime import datetime

# Crear base de datos para las alertas
def init_db():
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            alert_message TEXT,
            alert_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Enviar correo
def send_email(user_email, alert_message):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = "sgarcia.5318@gmail.com"
        smtp_password = "czdi tmxa flta dfra"

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = user_email
        msg['Subject'] = "Alerta Programada"
        body = alert_message
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, user_email, text)
        server.quit()

        messagebox.showinfo("Éxito", "Correo enviado exitosamente")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar el correo: {str(e)}")

# Función para programar alertas
def schedule_alert(email, alert_message, alert_time):
    schedule.every().day.at(alert_time).do(send_email, email, alert_message)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Iniciar sesión
def login():
    email = email_entry.get()
    password = password_entry.get()

    if email and password:
        app_frame.pack_forget()
        show_main_menu(email)
    else:
        messagebox.showerror("Error", "Credenciales inválidas")

# Programar una nueva alerta
def add_alert():
    alert_date = calendar.selection_get()
    alert_hour = hour_combobox.get()
    alert_minute = minute_combobox.get()
    alert_message = message_entry.get("1.0", tk.END)

    if not alert_hour or not alert_minute:
        messagebox.showerror("Error", "Debe seleccionar una hora válida")
        return

    alert_time = f"{alert_hour}:{alert_minute}"
    alert_datetime = f"{alert_date} {alert_time}"
    
    try:
        datetime.strptime(alert_datetime, '%Y-%m-%d %H:%M')
    except ValueError:
        messagebox.showerror("Error", "Formato de fecha/hora inválido")
        return
    
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alerts (user_email, alert_message, alert_time) VALUES (?, ?, ?)",
                   (user_email, alert_message, alert_datetime))
    conn.commit()
    conn.close()

    schedule_alert(user_email, alert_message, alert_time)
    messagebox.showinfo("Éxito", "Alerta programada exitosamente")
    alert_form_window.destroy()  # Cierra la ventana después de agregar la alerta

# Mostrar historial de alertas
def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("Historial de Alertas")
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT alert_message, alert_time FROM alerts WHERE user_email=?", (user_email,))
    alerts = cursor.fetchall()
    conn.close()

    for alert in alerts:
        tk.Label(history_window, text=f"Alerta: {alert[0]} - Programada para: {alert[1]}").pack()

# Menú principal después de iniciar sesión
def show_main_menu(email):
    global user_email
    user_email = email

    main_menu_frame.pack()
    tk.Label(main_menu_frame, text=f"Bienvenido {email}").pack()

    tk.Button(main_menu_frame, text="Programar Alerta", command=show_alert_form).pack()
    tk.Button(main_menu_frame, text="Mostrar Historial de Alertas", command=show_history).pack()

def show_alert_form():
    global calendar, hour_combobox, minute_combobox, message_entry, alert_form_window

    alert_form_window = tk.Toplevel(root)
    alert_form_window.title("Programar Alerta")

    tk.Label(alert_form_window, text="Fecha de la alerta:").pack()
    
    # Calendario
    calendar = Calendar(alert_form_window, selectmode='day', date_pattern='yyyy-mm-dd')
    calendar.pack(pady=10)

    tk.Label(alert_form_window, text="Hora de la alerta (HH:MM):").pack()

    # Combobox para seleccionar la hora
    hour_combobox = ttk.Combobox(alert_form_window, values=[f"{h:02d}" for h in range(24)])
    hour_combobox.pack(pady=5)
    
    # Combobox para seleccionar los minutos
    minute_combobox = ttk.Combobox(alert_form_window, values=[f"{m:02d}" for m in range(60)])
    minute_combobox.pack(pady=5)

    tk.Label(alert_form_window, text="Mensaje de la alerta:").pack()
    message_entry = tk.Text(alert_form_window, height=5)
    message_entry.pack()

    tk.Button(alert_form_window, text="Agregar Alerta", command=add_alert).pack()

# Iniciar interfaz gráfica
root = tk.Tk()
root.title("Sistema de Alertas")

# Fijar el tamaño de la ventana
root.geometry("400x400")  # Establecer el tamaño de la ventana (ancho x alto)
root.resizable(False, False)  # Deshabilitar redimensionamiento

# Login
app_frame = tk.Frame(root)
app_frame.pack()

tk.Label(app_frame, text="Correo:").pack()
email_entry = tk.Entry(app_frame)
email_entry.pack()

tk.Label(app_frame, text="Contraseña:").pack()
password_entry = tk.Entry(app_frame, show="*")
password_entry.pack()

tk.Button(app_frame, text="Iniciar Sesión", command=login).pack()

# Menú principal
main_menu_frame = tk.Frame(root)

# Iniciar el scheduler en un thread separado
scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Inicializar la base de datos
init_db()

root.mainloop()
