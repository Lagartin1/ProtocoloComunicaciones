# Trabajo Práctico de comunicaciones

## Ejecucion y compilación

1. dirigirse a la carpeta `docker` y ejecutar el comando para compilar la imagen de docker
   >> Nota: Si utiliza Ubuntu, es necesario antes ejecutar el comando `sudo` ante cada comando de docker.

```sh
   docker compose build
```

1. abrir 3 terminales y ejecutar el comando para correr cada container:

    a. En la primera terminal, ejecutar el servidor de comunicaciones:

```sh
   docker compose up -d receptor && docker compose logs -f receptor
```

b. En la segunda terminal, ejecutar el cliente de comunicaciones:

```sh
   docker compose up -d emisor && docker compose logs -f emisor
```

c. En la tercera terminal, ejecutar el contenedor que simula errores en la comunicación, esto debe ser ejecutado
   después ver en la terminal del emisor el mensaje `Esperando 20 segundos antes de enviar los datos...`, en ese momento ejecuta el siguiente comando:

```sh
   docker compose up -d chaos_delay && docker compose up -d chaos_loss $$ docker compose up -d chaos_corruption
```
   >> Nota: Si se desea simular solo el delay, solo ejecutar el comando `docker compose up -d chaos_delay`, si se desea simular solo la pérdida de paquetes, ejecutar `docker compose up -d chaos_loss`, y si se desea simular solo la corrupción de datos, ejecutar `docker compose up -d chaos_corruption`.

1. Para detener los contenedores, ejecutar el siguiente comando en cada terminal:

```sh
   docker compose down
```