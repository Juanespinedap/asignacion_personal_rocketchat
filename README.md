# Asignación de actividad a personal

Este Proyecto tiene como objetivo crear una base de datos donde se asigne a un trabajador una actividad especifica, unicamente con los dias laborales de todo un año.
Para luego notificar por medio del Rocketchat al empleado sobre su actividad a realizar para el dia de hoy, ademas de notificar en un Canal de la plataforma


## Entorno de trabajo

Se debe crear el entorno de trabajo teniendo en cuenta lo siguiente:

### Creacion de entorno virtual windows
    py -m venv venv

### Creacion de entonor virtual linux
    python3 -m venv venv

### Activacion de entonor virtual windows
    .\venv\Scripts\activate

### Activacion de entonor virtual linux
    source venv/bin/activate

### Create requirements
    pip3 freeze > requirements.txt

### Install requirements
    pip3 install -r /path/to/requirements.txt
    pip3 install -r requirements.txt


## Explicacion ejecucion en linux

Para que el proyecto pueda ejecutarse diariamente y quede automatizado, se debe crear un crontab. Ejemplo:
    29 08 * * 1-5 python3 your/paht/main.py

## Explicacion ejecucion en windows

Se debe ejecutar el proyecto desde el panel de tareas
