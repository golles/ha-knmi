# KNMI

[![GitHub Release][releases-shield]][releases]
[![GitHub Repo stars][stars-shield]][stars]
[![License][license-shield]](LICENSE)
[![GitHub Activity][commits-shield]][commits]
[![Code coverage][codecov-shield]][codecov]
[![hacs][hacs-shield]][hacs]
[![hacs][hacs-installs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][maintainer]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

KNMI custom component for Home Assistant. <br>
Weather data provided by KNMI, https://weerlive.nl.

## Installation

### HACS

This component can be installed in your Home Assistant with HACS.


### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `knmi`.
4. Download _all_ the files from the `custom_components/knmi/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "knmi"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/knmi/translations/en.json
custom_components/knmi/translations/nl.json
custom_components/knmi/__init__.py
custom_components/knmi/api.py
custom_components/knmi/binary_sensor.py
custom_components/knmi/config_flow.py
custom_components/knmi/const.py
custom_components/knmi/coordinator.py
custom_components/knmi/diagnostics.py
custom_components/knmi/manifest.json
custom_components/knmi/sensor.py
custom_components/knmi/weather.py
```

## Configuration is done in the UI

You can configure and setup the KNMI integration in your integrations page, look for KNMI in the add integrations dialog.

## Known limitations

 - This integration is translated into English and Dutch, the entity names and the data (from the API) are only available in Dutch.
 - The free API only provides a forecast for 2 days ahead. To make the weather card aesthetically not look too bad, the forecast for today is also shown, resulting in showing only 3 days (see example below).

## Examples
Integration with all entities: <br>
<img width="662" alt="Integration" src="https://user-images.githubusercontent.com/2211503/179353840-009a710e-94b9-41a7-9efd-b9dd98ae5b66.png">

Weather card: <br>
<img width="472" alt="Weather card" src="https://user-images.githubusercontent.com/2211503/179353837-a535059b-b5b6-462a-8519-3bb15dd3fdab.png">

Weather entity: <br>
<img width="396" alt="Weather entity" src="https://user-images.githubusercontent.com/2211503/179353844-32d9c826-5701-4264-91e4-894c797b4e0d.png">

Sun entity: <br>
<img width="392" alt="Sun entity" src="https://user-images.githubusercontent.com/2211503/179353841-8376e62f-1bd8-4ee2-ae16-14e1dde41c9f.png">

Warning entity: <br>
<img width="370" alt="Warning entity" src="https://user-images.githubusercontent.com/2211503/179353843-fee87e24-eabd-4d44-a58c-b933cfe4625c.png">


## Collect logs

When you want to report an issue, please add logs from this component. You can enable logging for this component by configuring the logger in Home Assistant as follows:
```yaml
logger:
  default: warn
  logs:
    custom_components.knmi: debug
```
More info can be found on the [Home Assistant logger integration page](https://www.home-assistant.io/integrations/logger)


## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)


[buymecoffee]: https://www.buymeacoffee.com/golles
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[codecov]: https://app.codecov.io/gh/golles/ha-knmi
[codecov-shield]: https://img.shields.io/codecov/c/github/golles/ha-knmi?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/golles/ha-knmi.svg?style=for-the-badge
[commits]: https://github.com/golles/ha-knmi/commits/main
[hacs]: https://github.com/custom-components/hacs
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[hacs-installs-shield]: https://raw.githubusercontent.com/golles/ha-active-installation-badges/main/knmi.svg
[license-shield]: https://img.shields.io/github/license/golles/ha-knmi.svg?style=for-the-badge
[maintainer]: https://github.com/golles
[maintenance-shield]: https://img.shields.io/badge/maintainer-golles-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/golles/ha-knmi.svg?style=for-the-badge
[releases]: https://github.com/golles/ha-knmi/releases
[stars-shield]: https://img.shields.io/github/stars/golles/ha-knmi?style=for-the-badge
[stars]: https://github.com/golles/ha-knmi/stargazers
