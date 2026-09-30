# backup-guard

Herramienta de línea de comandos en Python para automatizar copias de seguridad: comprime carpetas, guarda un historial, elimina automáticamente las copias más antiguas cuando se supera el límite configurado, y avisa por correo si algún trabajo falla.

Pensada para el tipo de tarea que se automatiza en cualquier puesto de soporte técnico: en vez de acordarte de hacer copias a mano, defines qué carpetas respaldar una vez y dejas que se ejecute solo, ya sea con el planificador de tareas del sistema o con el modo continuo integrado.

## Funcionalidades

- **Copias comprimidas**: cada ejecución genera un `.zip` con fecha y hora en el nombre.
- **Varios trabajos**: puedes definir tantas carpetas de origen como quieras en un único archivo de configuración.
- **Rotación automática**: cada trabajo tiene un número de copias a conservar (`keep`); las más antiguas se eliminan solas.
- **Aviso por correo ante fallos**: si un trabajo falla (por ejemplo, la carpeta de origen no existe o no hay permisos), se registra en el log y, si has configurado un correo, se envía un aviso.
- **Modo simulación (`--dry-run`)**: muestra qué haría el programa sin copiar ni borrar nada.
- **Restauración**: extrae cualquier copia anterior a la carpeta que quieras.

## Tecnologías

Solo librería estándar de Python (`zipfile`, `smtplib`, `argparse`, `logging`, `json`). No hace falta instalar nada para usarlo. Las pruebas usan `pytest`.

## Estructura del proyecto

```
backup-guard/
├── backupguard/
│   ├── archiver.py    # Crear y restaurar copias comprimidas
│   ├── rotation.py    # Política de retención (qué copias eliminar)
│   ├── notifier.py    # Aviso por correo ante fallos
│   └── cli.py          # Interfaz de línea de comandos
├── tests/
├── main.py              # Punto de entrada
├── config.example.json  # Configuración de ejemplo
└── requirements.txt
```

## Configuración

Copia `config.example.json` a `config.json` y edítalo con tus carpetas:

```json
{
  "jobs": [
    {
      "name": "documentos",
      "source": "/home/usuario/Documentos",
      "destination": "/mnt/backups/documentos",
      "keep": 5
    }
  ],
  "notify_email": null
}
```

- `keep`: cuántas copias conservar por trabajo antes de empezar a borrar las más antiguas (por defecto 5).
- `notify_email`: opcional. Si quieres recibir un aviso por correo cuando algo falle, rellénalo así:

```json
"notify_email": {
  "host": "smtp.gmail.com",
  "port": 587,
  "user": "tu_correo@gmail.com",
  "password": "tu_contraseña_de_aplicación",
  "to": "donde_quieres_el_aviso@gmail.com"
}
```

## Uso

```bash
git clone https://github.com/<tu-usuario>/backup-guard.git
cd backup-guard
cp config.example.json config.json   # y edítalo con tus carpetas

# Ejecutar una vez
python main.py run

# Ver qué haría, sin tocar nada
python main.py run --dry-run

# Ver las copias existentes
python main.py list

# Restaurar una copia concreta
python main.py restore /mnt/backups/documentos/documentos_20260930-120000-000000.zip /ruta/destino
```

### Programar la ejecución automática

Lo habitual es dejar que el propio sistema operativo lo lance periódicamente:

**Linux / macOS (cron)** — edita el crontab con `crontab -e` y añade, por ejemplo, para ejecutarlo cada noche a las 2:00:
```
0 2 * * * cd /ruta/a/backup-guard && python3 main.py run
```

**Windows (Programador de tareas)** — crea una tarea que ejecute `python main.py run` desde la carpeta del proyecto, con la periodicidad que quieras.

**Alternativa integrada**, si prefieres no tocar el planificador del sistema:
```bash
python main.py run --interval 3600   # se repite cada hora hasta que pares con Ctrl+C
```

## Ejecutar las pruebas

```bash
pip install pytest
pytest
```

