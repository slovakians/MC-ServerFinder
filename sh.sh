version: "3.8"
services:
  casaos:
    image: casaos/casaos:latest
    container_name: casaos
    ports:
      - "8080:80"  # Change 80->8080 if needed
    privileged: true
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - casaos_data:/etc/casaos
volumes:
  casaos_data: