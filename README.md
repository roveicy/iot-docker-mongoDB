1. Build

docker-compose build
<br>
2. Set the configuration of sensors
<br>
* Edit IoT/schedule.list
-- For example<br>
5 10<br>
10 10<br>
<br>-- means simulating 5 sensors in 10 senconds and then 10 sensors in 10 seconds
<br>-- You can also simulate 0 sensors to simulate sleeping.

<br>* Edit IoT/sensors.list
<br>-- For example
<br>temp 1
<br>device 5 1
<br>gps 2
<br>asd 24
<br>camera 15 50000
<br>-- means: the first sensor will be a temperature sensor which reports the temperature every 1 seconds
<br>-- the second sensor will be a device sensor which reports ON or OFF in every 5 seconds (Gaussian distribution with the <br>mean value 5 and the standard deviation value 1
<br>-- the third sensor will be a gps sensor which reports a position every 2 seconds
<br>-- the forth sensor will be a sound sensor which reports sound data and samples per second is set to 24
<br>-- the fifth sensor will be a camera sensor whill reports video data and FPS(frames per second) is set to 15 and bits per second is set to 50000.
<br>-- the sixth sensor will be a temperature sensor
<br>-- and so on

<br>3. Run

<br>* Start simulation
<br>docker-compose up -d
<br>-- then the iot container will start the simulation after 10 seconds

<br>* Start auto scale
<br>python3 auto-scale.py
<br>-- Run "python3 auto-scale --help" to see the help information
<br>-- Set mimimun containers with -m
<br>-- Set maximum containers with -M
<br>-- Set down-scale cpu threshold with -d
<br>-- Set up-scale cpu threshold with -u
<br>-- Set checking interval with -i

<br>4. View the database
<br>Access http://127.0.0.1:8081 and the database name is 'iot', the collection name is 'sensors'.

<br>5. How
<br>It starts a 'db' containter for database, 
<br>one/many 'web' containers for receiving iot data and storing in the database, 
<br>a 'haproxy' container for balancing requests to 'web' containers,
<br>and an 'iot' container for generating iot data.
<br>Besides, it starts a 'dbmanager' for providing http://127.0.0.1:8081 for managing the database, 
<br>a 'cadvisor' for monitoring all containers.


<br> *You can cite the following papers for this project:*
<br>Rasolroveicy, M., & Fokaefs, M. (2020, November). Dynamic reconfiguration of consensus protocol for IoT data registry on blockchain. In Proceedings of the 30th Annual International Conference on Computer Science and Software Engineering (pp. 227-236).

<br>*References:*
<br>Ramprasad, B., Fokaefs, M., Mukherjee, J., & Litoiu, M. (2019, June). EMU-IoT-A Virtual Internet of Things Lab. In 2019 IEEE International Conference on Autonomic Computing (ICAC) (pp. 73-83). IEEE.
