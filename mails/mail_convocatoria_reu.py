import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
from jinja2 import Template
from pathlib import Path
from utils.acta_utils import get_last_minutes_id, create_new_minutes
from utils.utils import *
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent
MAIL_PATH = BASE_DIR / "../mails/convocatoria-reu.html"

# Dates
today = datetime.now()
yesterday = today - timedelta(days=1)
week_ago = today - timedelta(days=7)


today_str = today.strftime("%d/%m/%Y")
yesterday_str = yesterday.strftime("%d/%m")
week_ago_str = week_ago.strftime("%d/%m")

days_es = [
    "lunes", "martes", "miércoles", "jueves",
    "viernes", "sábado", "domingo"
]

# Spanish months
months_es = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

date = datetime.now()

day = date.day
month = months_es[date.month - 1]

def format_spanish_date(date_str):
    date = datetime.strptime(date_str, "%d/%m/%Y")

    day_name = days_es[date.weekday()].upper()
    day_num = date.day
    month_name = months_es[date.month - 1]

    return f"{day_name} {day_num} de {month_name}"


# Cargamos los puntos del día y de noche
if does_file_exist(DAY_POINTS_TEMP_PATH):
    day = load_from_json(DAY_POINTS_TEMP_PATH)
else:
    day = load_from_json(DAY_POINTS_PATH)

if does_file_exist(NIGHT_POINTS_TEMP_PATH):
    night = load_from_json(NIGHT_POINTS_TEMP_PATH)
else:
    night = load_fromm_json(NIGHT_POINTS_PATH)

# Generamos el HTML de los puntos
day_html = ""
for item in day:
    day_html += f'  <div class="item">{item}</div>\n'

night_html = ""
for item in night:
   night_html += f'  <div class="item">{item}</div>\n'



with open(MAIL_PATH, "r", encoding="utf-8") as f:
    template = Template(f.read())

last_minutes_id = get_last_minutes_id()
new_minutes_id = create_new_minutes()

last_minutes_link = f"https://docs.google.com/document/d/{last_minutes_id}/edit"
new_minutes_link = f"https://docs.google.com/document/d/{new_minutes_id}/edit"
last_meeting_str = get_last_meeting_date().strftime("%d/%m/%Y")
next_meeting_str = get_next_meeting_date().strftime("%d/%m/%Y")
next_meeting_formatted = format_spanish_date(next_meeting_str)
day_before = get_next_meeting_date() - timedelta(days=1)
day_before_str = day_before.strftime("%d/%m")

html = template.render(
    today_str = next_meeting_str,
    yesterday_str=day_before_str,
    week_ago_str=last_meeting_str,
    today_formatted=next_meeting_formatted,
    last_minutes_link=last_minutes_link,
    new_minutes_link=new_minutes_link,
    day_points=day_html,
    night_points=night_html
)

set_last_meeting_date(get_next_meeting_date())

# Email content
subject = f"[Secretaría] [Agenda] Reunión semanal {next_meeting_str}"

name_secre = os.environ.get("NOMBRE_SECRE")

msg = MIMEText(html, "html")
msg["Subject"] = subject
msg["From"] = f"Carlos Beltrán | Secretaría"
msg["To"] = "smashing-bros@bestvalencia.org"


# SMTP server (example: Gmail)
smtp_server = "smtp.gmail.com"
smtp_port = 465

username = "secretary@bestvalencia.org"
password = os.getenv("EMAIL_PASSWORD") # use app password, not your real password

# Send email
with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
    server.login(username, password)
    server.send_message(msg)

# Borramos los puntos temporales
if does_file_exist(DAY_POINTS_TEMP_PATH):
    delete(DAY_POINTS_TEMP_PATH)

if does_file_exist(NIGHT_POINTS_TEMP_PATH):
    delete(NIGHT_POINTS_TEMP_PATH)

print("Email sent!")
