# Irish Property Sales Analysis

### Dependencies

This project was developed in an environment using the following software
- Python(3.7.7)
- PostgresSQL(12.2) - developed by running locally but can be configured in the [config](resources/config.yaml) file, i.e. `postgres.connection` 
- MongoDB(4.0.3) - developed by running locally but can be configured in the [config](resources/config.yaml) file, i.e. `mongo.connection`
- Nominatim(3.4) - developed by running locally [using this Docker image](https://github.com/mediagis/nominatim-docker) but can be configured in the [config](resources/config.yaml) file, i.e. `geocoders.nominatim`

*It is recommended that you run this app using the specific versions mentioned above.*

---
### Getting Started

To run the app you need to run [main.py](app/main.py) using a Python interpreter, i.e. python app/main.py.

*Please note that to use some geocoding services and Chart Studio you will need to provide API keys.
These keys should be added to a secrets.yaml file under the resources directory.
The Chart Studio username should be changed in the [config](resources/config.yaml) file*

A [config](resources/config.yaml) file is provided that enables you to modularise the project and enable/disable features.