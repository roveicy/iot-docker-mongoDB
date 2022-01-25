##  Build

```shell
docker-compose build
```

## Set the configuration of sensors
* Edit IoT/schedule.list: 
```text
5 10
10 10
```
- means simulating 5 sensors in 10 senconds and then 10 sensors in 10 seconds You can also simulate 0 sensors to simulate sleeping.
- as the second parameters means how long the sensors should be alive in the workload, it is recommended to keep it 10 seconds for all of the experiments.

* Edit IoT/sensors.list
```text
temp 1
device 5 1
gps 2
asd 24
camera 15 50000
```
- means: the first sensor will be a temperature sensor which reports the temperature every 1 seconds
- the second sensor will be a device sensor which reports ON or OFF in every 5 seconds (Gaussian distribution with the mean value 5 and the standard deviation value 1
- the third sensor will be a gps sensor which reports a position every 2 seconds
- the forth sensor will be a sound sensor which reports sound data and samples per second is set to 24
- the fifth sensor will be a camera sensor whill reports video data and FPS(frames per second) is set to 15 and bits per second is set to 50000.


## Run

1. Start simulation
    ```
    docker-compose create
    docker-compose up -d
    ```
    then the iot container will start the simulation after 10 seconds
    - Please note that you can scale the "web" container based on the load. You might use auto-scaling policies on the web container based on your applicaiton need. This will help the workload generator to avoid crashing.

2. Start auto scale
```sell
python3 auto-scale.py
```
- Run `python3 auto-scale --help` to see the help information
- Set mimimun containers with `-m`
- Set maximum containers with `-M`
- Set down-scale cpu threshold with `-d`
- Set up-scale cpu threshold with `-u`
- Set checking interval with `-i`

## View the database

Access `http://127.0.0.1:8081` and the database name is `iot`, the collection name is `sensors`.


## How
- It starts a `db` containter for database 
- one/many `web` containers for receiving iot data and storing in the database 
- a `haproxy` container for balancing requests to `web` containers
- and an `iot` container for generating iot data.
- Besides, it starts a `dbmanager` for providing `http://127.0.0.1:8081` for managing the database
- a `cadvisor` for monitoring all containers.
Access live monitoring by cadvisor: `https://127.0.0.1:8080`

You can cite the following papers for this project:

*Rasolroveicy, M., & Fokaefs, M. (2020, November). Dynamic reconfiguration of consensus protocol for IoT data registry on blockchain. In Proceedings of the 30th Annual International Conference on Computer Science and Software Engineering (pp. 227-236).*

References:
*Ramprasad, B., Fokaefs, M., Mukherjee, J., & Litoiu, M. (2019, June). EMU-IoT-A Virtual Internet of Things Lab. In 2019 IEEE International Conference on Autonomic Computing (ICAC) (pp. 73-83). IEEE.*
