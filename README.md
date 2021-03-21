# speedtest-to-influxdb

## Launching
1. Start influx
```
docker run -it --rm --name influx \
    -p 8086:8086 \
    -e INFLUXDB_HTTP_AUTH_ENABLED=true \
    -e INFLUXDB_DB=speedtest \
    -e INFLUXDB_ADMIN_USER=admin \
    -e INFLUXDB_ADMIN_PASSWORD=admin \
    -e INFLUXDB_USER=speedtest \
    -e INFLUXDB_USER_PASSWORD=speedtest \
    -v /mnt/c/CODE/influx:/var/lib/influxdb \
    influxdb:1.8
```
2. Build and run docker image
3. If you run into issues, ensure that both images are running on the same docker network
