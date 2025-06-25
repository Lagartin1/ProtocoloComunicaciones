# Trabajo Práctico de comunicaciones

## Ejecucion y compilación

1. dirigirse a la carpeta `docker` y ejecutar el comando para compilar la imagen de docker
   ```bash
   docker build
   ```
2. abrir 3 terminales y ejecutar el comando para correr cada container:

    a. En la primera terminal, ejecutar el servidor de comunicaciones:
   ```bash
   docker compose up -d receptor && docker compose logs -f receptor
   ```
   b. En la segunda terminal, ejecutar el cliente de comunicaciones:
   ```bash
   docker compose up -d emisor && docker compose logs -f emisor
   ```
   c. En la tercera terminal, ejecutar el contenedor que simula errores en la comunicación, esto debe ser ejecutado
   después ver en la terminal del emisor el mensaje `Esperando 20 segundos antes de enviar los datos...`, en ese momento ejecuta el siguiente comando:
   ```bash
   docker compose up -d chaos_delay && docker compose up -d chaos_loss
    ```

3. Para detener los contenedores, ejecutar el siguiente comando en cada terminal:
4. ```bash
   docker compose down
   ```