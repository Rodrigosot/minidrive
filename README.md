# MiniDrive (Backend API)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Boto3](https://img.shields.io/badge/Boto3-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
[![Backblaze](https://img.shields.io/badge/Backblaze_B2-E22A26?style=for-the-badge)](https://www.backblaze.com/)

MiniDrive es una API RESTful construida con **FastAPI** y **Python** que simula el backend de una plataforma de almacenamiento en la nube (como Google Drive). Se encarga de gestionar usuarios, autenticación, creación de carpetas y manejo remoto de archivos con Backblaze B2.

## 🚀 Tecnologías

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **Base de Datos:** [PostgreSQL](https://www.postgresql.org/)
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
* **Almacenamiento Cloud:** [Backblaze B2](https://www.backblaze.com/) (API compatible con AWS S3) integrado mediante la librería `boto3`.
* **Autenticación:** JWT (JSON Web Tokens) usando `python-jose` y `passlib`
* **Rate Limiting:** `slowapi`
* **Contenedores:** Docker y Docker Compose

## ⚙️ Características y Funcionalidades

* **Autenticación de Usuarios:** Registro e inicio de sesión seguros mediante JWT.
* **Gestión de Carpetas:** Operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para organizar información en directorios.
* **Almacenamiento Seguro S3 (Backblaze B2):** Subida, descarga y eliminación de archivos alojados directamente en la nube mediante el estándar S3.
* **Gestión de Archivos:** Guardado de metadatos, control de acceso y seguridad de acceso de los archivos dentro de la base de datos.
* **Rate Limiting:** Protección de endpoints para limitar el número de peticiones, evitando abusos y asegurando estabilidad en la API.
* **Dockerizado:** Fácil de desplegar y configurar localmente gracias a `docker-compose.yml`.

## 🛠️ Instalación y Uso Local

### Requisitos previos
* [Docker](https://docs.docker.com/get-docker/) y Docker Compose instalados en tu sistema.
* [Git](https://git-scm.com/)

### Pasos para ejecutar

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/TuUsuario/minidrive.git
   cd minidrive
   ```

2. **Configurar las variables de entorno:**
   * Asegúrate de configurar un archivo `.env` en la raíz del proyecto basándote en un archivo de ejemplo (`.env.example` si lo hubiera) que incluya las credenciales de PostgreSQL y claves secretas para JWT.

3. **Levantar los contenedores con Docker:**
   ```bash
   docker-compose up -d --build
   ```

4. **Acceder a la documentación:**
   * Una vez levantado el servidor, FastAPI genera documentación interactiva automáticamente.
   * Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   * ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📁 Estructura del Proyecto

* `app/api/`: Contiene los routers y endpoints de la API organizados por versión (ej. V1) para `users`, `auth`, `folder`, `file`.
* `app/core/`: Configuraciones principales y seguridad.
* `app/models/`: Modelos de la base de datos de SQLAlchemy.
* `app/schemas/`: Esquemas de Pydantic para la validación de datos (Requests/Responses).
* `app/services/`: Lógica de negocio (CRUD y servicios).
* `docker-compose.yml`: Configuración para levantar el backend y la base de datos.
