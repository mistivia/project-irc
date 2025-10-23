sudo podman kill webircgw-c
sudo podman rm webircgw-c
sudo podman run -d \
    --name webircgw-c \
    -p 8180:8180 \
    -v ./conf:/conf \
    --restart=always \
    webircgw

