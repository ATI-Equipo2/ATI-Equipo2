# Política de control de versiones
Contaremos con 4 ramas
 - Develop: La usaremos para realizar la ejecución de nuestro proyecto . Todas las nuevas características y desarrollos se integran aquí
 - Release: La usaremos para realizar pruebas, ajustes finales y preparar el código para pasarlo a Release (paso anterior al Main).
 - Main: almacenara la versión actual funcional; todas las demás ramas parten de ésta y contiene el código en producción.
 - Hotfix: La utilizaremos para corregir errores que afectan la versión actual (Main) y sobretodo para tratar correcciones urgentes.

Contaremos con una persona encargada que se ocupará de revisar, aprobar e integrar todos los Pull Requests hacia Main. Quedan totalmente prohibidos los pushes directos a Main.

Usaremos prefijos claros para crear ramas secundarias como dev/ y hotfix/. Una vez que el PR sea aprobado y se haga el merge, la rama secundaria la vamos a eliminar para mantener el repositorio limpio.

se van a utilizar Conventional Commits para  que el historial sea claro, estructurado y fácil de leer:

 - fix: Lo usaremos para la corrección de errores .
 - feat: Lo usaremos para añadir una nueva funcionalidad .
 - docs: Lo usaremos para cambios únicamente en la documentación (como el README.md).
 - refactor:Lo usaremos para cambios en el código que no corrigen bugs ni añaden funcionalidades, sino que mejoran la estructura o calidad del código.
 - style: Lo usaremos para cambios que no afectan el significado del código (espacios, formato, comas, etc.).
 - test: Lo usaremos para añadir o corregir pruebas automatizadas.
 - chore: Lo usaremos para tareas secundarias, actualización de dependencias o configuración del proyecto

# Guía de estilo de código
Para mantener un código limpio y homogéneo nos basaremos en lo siguiente:
- variables: nombre_variable
- constantes: NOMBREVARIABLE
- clases: NombreClase
- funciones: nombre_funciones (los nombres deben ser verbos)

* Como vamos a trabajar con Django nos enfocaremos en establecer una programación orientada a objetos
* Usar MVC de Django

# GitActions. Automatización del Tablero en GitHub Projects

Nuestro objetivo es que las tarjetas del proyecto **mAsTIcotas** se muevan automáticamente a la columna de *Completado* (Done) cuando el código se integra definitivamente a la rama `main`.

## ¿Cómo funciona?

Hemos activado el flujo de trabajo nativo de GitHub Projects. 

Esta automatización escucha en segundo plano cada vez que un Pull Request (PR) es aceptado y fusionado. Si el PR está correctamente vinculado a un *Issue* (tarea), el sistema interviene: cierra el *Issue* automáticamente y mueve la tarjeta correspondiente al estado final en nuestro tablero, manteniendo todo sincronizado sin esfuerzo manual.

## Instrucciones para el Equipo

Para que esta automatización funcione, es **obligatorio** que todo el equipo siga este estándar al crear un Pull Request hacia la rama `main`:

**1. Abrir el Pull Request:** 
Sube tu rama de desarrollo a GitHub y abre el PR apuntando hacia `main`.

Al completarse el merge, la tarjeta vinculada viajará sola a la columna de finalizado del tablero

# Entorno de desarrollo y datos de prueba

La base de datos (SQLite) y las imágenes subidas (`media/`) **no se suben a git**. Para que todo el equipo tenga los mismos datos, hay un comando que puebla la base de datos.

## Con Docker

```
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_data --flush
```

(`docker-compose up` ya aplica las migraciones al arrancar; el `migrate` explícito es por si acaso.)

- `seed_data --flush` borra mascotas, solicitudes, notificaciones, mensajes y usuarios no administradores, y vuelve a crear los datos de ejemplo. Los superusuarios se conservan. Sin `--flush` solo crea o actualiza (se puede ejecutar varias veces).
- Usuarios de ejemplo: `rolando` y `jesus`, ambos con contraseña `test1234`. Incluye 7 mascotas y una solicitud de socialización pendiente de Brown (jesus) hacia Ronaldo (rolando), para probar las notificaciones.
- Panel de administración (`/admin/`): crea tu propio superusuario con `docker-compose exec web python manage.py createsuperuser`.

## Sin Docker

```
python -m venv venv
venv\Scripts\activate        # en Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data --flush
python manage.py runserver
```

La aplicación queda en `http://localhost:8000/` (también bajo `/matchPets/`).

## Si aparece `no such table: matchPets_user`

Tu base de datos se creó con un historial de migraciones anterior y no se puede migrar encima. Recréala (los datos locales se pierden, pero el seed los repone):

- Docker: `docker-compose down -v` y luego `docker-compose up --build` (borra el volumen `bd_data`).
- Sin Docker: borra `db.sqlite3` y ejecuta de nuevo `python manage.py migrate`.

## Traducciones

Después de añadir textos con `{% translate %}` o `gettext`, ejecuta:

```
python manage.py makemessages -l en --ignore=venv --no-obsolete
python manage.py compilemessages -l en
```

(`--ignore=venv` evita que se mezclen las cadenas de Django.)
