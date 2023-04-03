from sqlalchemy import create_engine
from datetime import date
from datetime import datetime
from datetime import timedelta
from pandas.tseries.holiday import *
from pandas.tseries.offsets import CustomBusinessDay
import pandas as pd
import sqlite3 as sql
from rocketchat.api import RocketChatAPI
from RocketChatBot import RocketChatBot
import schedule, time
from datetime import date
from datetime import datetime
from datetime import timedelta
import os
from dotenv import load_dotenv


# Variables de entorno
load_dotenv()
botname = os.getenv('user')
password = os.getenv('pw')
domain = os.getenv('url')
route = os.getenv('route')
grupo = os.getenv('group')


# Creacion de database omitiendo los festivos

# No colocar festivos que caen un domingo
class EsBusinessCalendar(AbstractHolidayCalendar):
       rules = [
         Holiday('Día de los Reyes Magos', month=1, day=9, observance=sunday_to_monday),
         Holiday('Día de San José', month=3, day=20, observance=sunday_to_monday),
         Holiday('Jueves Santo', month=4, day=6, observance=sunday_to_monday),
         Holiday('Viernes Santo', month=4, day=7, observance=sunday_to_monday),
         Holiday('Día de Trabajo', month=5, day=1, observance=sunday_to_monday),
         Holiday('Día de la Ascensión', month=5, day=22, observance=sunday_to_monday),
         Holiday('Corpus Christi', month=6, day=12, observance=sunday_to_monday),
         Holiday('Sagrado Corazón', month=6, day=19, observance=sunday_to_monday),
         Holiday('San Pedro y San Pablo', month=7, day=3, observance=sunday_to_monday),
         Holiday('Día de la Independencia', month=7, day=20, observance=sunday_to_monday),
         Holiday('Batalla de Boyacá', month=8, day=7, observance=sunday_to_monday),
         Holiday('La asunción de la Virgen', month=8, day=21, observance=sunday_to_monday),
         Holiday('Día de la Raza', month=10, day=16, observance=sunday_to_monday),
         Holiday('Todos los Santos', month=11, day=6, observance=sunday_to_monday),
         Holiday('Independencia de Cartagena', month=11, day=13, observance=sunday_to_monday),
         Holiday('Día de la Inmaculada Concepción', month=12, day=8, observance=sunday_to_monday),
         Holiday('Día de Navidad', month=12, day=25, observance=sunday_to_monday),
       ]

# Creacion de calendario de dias no laborales (inclyenedo festivos)
es_BD = CustomBusinessDay(calendar=EsBusinessCalendar())
# Se crea un arreglo con las fechas de todo un año omitiendo los festivos y dias laborales
s = pd.date_range('2023-01-1', end='2023-12-31', freq=es_BD)
# Se crea un dataframe con una columna que contiene las reglas de los fstivos y dias no laborales
df1 = pd.DataFrame(s, columns=['fechas'])

# Creacion de dataframe del personal
el_personal = ["persona_1", "persona_2", "persona_3","persona_4", "persona_5", "persona_6", "persona_7", 
               "persona_8", "persona_9", "persona_10" ] * 24
df2 = pd.DataFrame(el_personal, columns=['nombres'])

# Concatenar los dos dataframes
lista_p = pd.concat([df1, df2], axis=1)
# Converitr la columna fechas (que se encuentra en porpiedad de series) en una propiedad de fecha para poder consultar este campo en formato datetime
lista_p['fechas'] = pd.to_datetime(lista_p['fechas']).dt.date

# Conocer la cantidad de campos por cada usuario del dataframe
# print(lista_p["nombres"].value_counts())


# Uso de SQLite3

# cargue dataframe a SQLite3, creando base de datos
engine = create_engine(f'sqlite:///{route}', echo=False)
lista_p.to_sql('personal', con=engine, if_exists="replace")

def leer_datos():
    conn = sql.connect(route)
    cursor = conn.cursor()
    instruccion = f"SELECT * FROM personal"
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    print(datos)

def buscar_fecha(fecha):
    conn = sql.connect(route)
    cursor = conn.cursor()
    instruccion = f"SELECT * FROM personal WHERE fechas like '{fecha}'"
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    
    if datos == []:
        return None
    
    conn.commit()
    conn.close()
    return datos

def buscar_nombre(nombre):
    conn = sql.connect(route)
    cursor = conn.cursor()
    instruccion = f"SELECT * FROM personal WHERE nombres like '{nombre}'"
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    print(datos)

def insertar_datos(lista):
    conn = sql.connect(route)
    cursor = conn.cursor()
    instruccion = f"INSERT INTO personal VALUES (?, ?, ?)"
    cursor.execute(instruccion, lista)
    conn.commit()
    conn.close()

def insertar_varios_datos(lista):
    conn = sql.connect(route)
    cursor = conn.cursor()
    instruccion = f"INSERT INTO personal VALUES (?, ?, ?)"
    cursor.executemany(instruccion, lista)
    conn.commit()
    conn.close()

def update_datos(nombre, fecha):
    conn = sql.connect(route)
    cursor = conn.cursor()
    instruccion = f"UPDATE personal SET nombres = '{nombre}' WHERE fechas like '{fecha}'"
    cursor.execute(instruccion)
    conn.commit()
    conn.close()

def eliminar_fecha(fecha):
    conn = sql.connect(route)
    cursor = conn.cursor()
    instruccion = f"DELETE FROM personal WHERE fechas like'{fecha}'"
    cursor.execute(instruccion)
    conn.commit()
    conn.close()


# Agregar datos faltantes en la base de datos
update_datos('persona_1' ,'2023-12-27')
update_datos('persona_2' ,'2023-12-28')
update_datos('persona_3' ,'2023-12-29')


# Programación de tareas Dia actual
def today_activity():

    # Fecha del dia de hoy
    today = date.today()

    # Variable fecha para hacer tests
    # fecha = '2023-04-01' 

    # Guardar fecha de dia de hoy en formato string con los valores de "año-mes-dia"
    fecha = today.strftime("%Y-%m-%d")

    # Guardar en variable la informacion de la tabla de la base de datos segun la fecha
    respuesta = buscar_fecha(fecha)

    if  respuesta is not None:
        # se extrae el usuario de la variable respuesta. Ej: de la base de datos se tiene la respuesta (19, '2023-01-27', 'persona_9'), en la cual se extrae el usuario 'persona_9'
        # index = respuesta[0][0]
        # fecha = respuesta[0][1]
        usuario = respuesta[0][2]
        return usuario
    else:
        return None


# Para conocer al usuario asignado para la siguiente fecha
def dia_siguiente():
    now = datetime.now()
    new_date = now + timedelta(days=1)
    fecha_2 = new_date.strftime("%Y-%m-%d")
    respuesta = buscar_fecha(fecha_2)
    
    if  respuesta == ['Botman']:
        return None
    else:
        usuario= respuesta[0][2]
        return usuario


# Enviar mensaje directo al usuario
def mensaje_usuario():
    print("Activando bot directo")
    api = RocketChatAPI(settings={'username': botname, 'password': password, 'domain': domain})

    # lista para guardar los canales
        #rooms = []
        #rooms = api.get_public_rooms()
    
    # Metodo para extraer los usuarios del servidor de RocketChat
    user = api.get_users()

    usuario = today_activity()

    if usuario is None:
        print("no se envia mensaje al ususario")
    else:
        mensaje = "Hola!! paso por aqui a recordarte que que la actividad del dia de hoy estan a cargo tuyo"
        
        # Diccionario que guarda nombre y ID del usuario
        rocketchat_user = {}
        for x in user:
            rocketchat_user[x['username']] = x['id']
        
        # Metodo para enviar mensaje a usuario asignado.
        api.send_message(mensaje , rocketchat_user[usuario])


# Enviar mensaje directo al grupo asignado
def mensaje_grupo():
    bot = RocketChatBot(botname, password, domain)

    # Canal al que se enviara el mensaje
    usuario = today_activity()
    if usuario is None:
        print("Hoy no es dia de Pausas")
    else:
        mensaje = f"Hola muchachos la actividad del dia de hoy estan a cargo de @{usuario}"
 
        # Metodo para enviar mensaje a sala publica asignado con variable bot
        bot.send_message(mensaje, channel_id=grupo)
        print("Activando bot mensaje grupo")


# Detener proceso
def stop():
    quit()


# Programación de horarios

# se envia mensaje directo al usuario asignado
schedule.every().day.at("08:05").do(mensaje_usuario)
# se envia mensaje directo al grupo asignado
schedule.every().day.at("08:10").do(mensaje_grupo)
# Ejecucion para detener todo el proceso
schedule.every().day.at("08:11").do(stop)

while True:
# Comprueba si una tarea programada está pendiente de ejecutarse o no
    schedule.run_pending()
    time.sleep(1)