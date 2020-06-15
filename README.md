# The Drone Project

The Drone Project is my finishing project as a student in the Cyber class in Ohel-Shem high-school.
This project is the result of security research on IoT devices and smart cars and drones specifically.
I wanted to test for my self how secure automated and inter-connected vehicles can ever trully be and for that i built my own mini-car using a RaspberryPi.
I than setup a command server so that i could remote control it wirelessly through Wi-Fi. It was not secure one bit.
I researched attackes and performed them on my car, while coming up with a soultion for each attack i was able to pull of.
Some of the attacks are:
  - TCP Session Highjacking
  - Password sniffing through ARP Poisoning
  - Privacy breach thorugh Arp Poisoning MitM

The soultions I came up with and as a result this hopefully-secure commands server are strictly for educational perpouses and thus diffrent from the industry standard and best practices. My Protocol makes NO use of SSL, TLS, AES, RSA and other mainstream encryption standards.

# As a CLient:

  - you only need the GUI folder
  - Make sure you have Python3 and Flask installed
  - run the web_client.py file to start using!
# As a Server:

  - you only need the PI folder
  - Make sure you have Python3 and hashlib installed on your RaspberryPi.
  - run the new_server.py file to start using!
  - It is recommended to set server.py as a service to auto-start on boot.


I hope you enjoy reading or using this humble project, it took a while and was a VERY fun procces to research and develop!
