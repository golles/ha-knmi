# KNMI

[![GitHub Release][releases-shield]][releases]
[![GitHub Repo stars][stars-shield]][stars]
[![License][license-shield]](LICENSE)
[![GitHub Activity][commits-shield]][commits]
[![Code coverage][codecov-shield]][codecov]
[![hacs][hacs-shield]][hacs]
[![installs][hacs-installs-shield]][ha-active-installation-badges]
[![Project Maintenance][maintenance-shield]][maintainer]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

KNMI custom component for Home Assistant. <br>
Weather data provided by KNMI, https://weerlive.nl.

## Installation

### HACS installation

The most convenient method for installing this custom component is via HACS. Simply search for the name, and you should be able to locate and install it seamlessly.

### Manual installation guide:

1. Utilize your preferred tool to access the directory in your Home Assistant (HA) configuration, where you can locate the `configuration.yaml` file.
2. Should there be no existing `custom_components` directory, you must create one.
3. Inside the newly created `custom_components` directory, generate a new directory named `knmi`.
4. Retrieve and download all files from the `custom_components/knmi/` directory in this repository.
5. Place the downloaded files into the newly created `knmi` directory.
6. Restart Home Assistant.

## Configuration is done in the UI

Within the HA user interface, navigate to "Configuration" -> "Integrations", click the "+" button, and search for "KNMI" to add the integration.

## Known limitations

This integration is translated into English and Dutch, including entity names and attributes, the data (from the API) is only available in Dutch.
Feel free to create a pull request with your language, see [translations](custom_components/knmi/translations/). Non-numerical values are only available in Dutch

## Entities

This integration comes with multiple pre-built entities, most of which are initially deactivated. To enable additional entities, follow these steps:

1. Navigate to "Configuration" -> "Integrations" -> "KNMI" in the Home Assistant interface.
2. Click on the specific integration with "1 service" that you desire.
3. Click on "X entities hidden", and a summary of all entities in this integration will be displayed.
4. Choose the desired entity, click on the cogwheel icon, and access its settings.
5. Toggle the "Enabled" switch to activate the entity.
6. Click "Update" to save the changes. Repeat these steps for each entity you wish to enable.

After completing this process, the newly enabled entities will receive values during the next update.

### Binary sensors

| Name (EN) | Name (NL)    | Attributes                                                         | Notes                                                                   |
| --------- | ------------ | ------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| Sun       | Zon          | Sunrise, Sunset, Sun chance today, tomorrow and day after tomorrow | Times of today, in UTC, frontend will convert this into your local time |
| Warning   | Waarschuwing | Title, Description, Code, Next code, Next warning                  | Code has its own entity, see Weather code below                         |

### Sensors

Normal sensors:

| Name (EN)                | Name (NL)                    | Attributes                          | Notes                 |
| ------------------------ | ---------------------------- | ----------------------------------- | --------------------- |
| Dew point                | Dauwpunt                     |                                     | Unit configurable     |
| Solar irradiance         | Globale stralingsintensiteit |                                     |                       |
| Wind chill               | Gevoelstemperatuur           |                                     | Unit configurable     |
| Air pressure             | Luchtdruk                    |                                     | Unit configurable     |
| Humidity                 | Luchtvochtigheid             |                                     |                       |
| Max temperature today    | Max temperatuur vandaag      |                                     | Unit configurable     |
| Max temperature tomorrow | Max temperatuur morgen       |                                     | Unit configurable     |
| Min temperature today    | Min temperatuur vandaag      |                                     | Unit configurable     |
| Min temperature tomorrow | Min temperatuur morgen       |                                     | Unit configurable     |
| Precipitation today      | Neerslag vandaag             |                                     |                       |
| Precipitation tomorrow   | Neerslag morgen              |                                     |                       |
| Description              | Omschrijving                 |                                     | State is in Dutch     |
| Temperature              | Temperatuur                  |                                     | Unit configurable     |
| Weather forecast         | Weersverwachting             |                                     | State is in Dutch     |
| Wind speed               | Windsnelheid                 | Bearing, Degree, Beaufort and Knots | Unit configurable     |
| Weather code             | Weercode                     |                                     | Raw state is in Dutch |
| Visibility               | Zicht                        |                                     | Unit configurable     |

Diagnostic sensors:

| Name (EN)              | Name (NL)                | Notes                   |
| ---------------------- | ------------------------ | ----------------------- |
| Location               | Plaats                   |                         |
| Remaining API requests | Resterende API verzoeken |                         |
| Latest update          | Laatste update           | Server side update time |

### Weather

The weather entity contains all the weather information, ideal for displaying a comprehensive overview in the Home Assistant frontend. It includes both a daily forecast spanning up to 5 days and an hourly forecast covering up to 24 hours.

Daily forecast attributes:

| Attribute                 | Notes                                                         |
| ------------------------- | ------------------------------------------------------------- |
| datetime                  | Times in UTC, frontend will convert this into your local time |
| condition                 |                                                               |
| templow                   |                                                               |
| temperature               |                                                               |
| precipitation_probability | in a percentage                                               |
| wind_bearing              |                                                               |
| wind_speed                |                                                               |
| wind_speed_bft            | Not officially supported, but nice addition                   |
| sun_chance                | Not officially supported, but nice addition                   |

Hourly forecast attributes:

| Attribute        | Notes                                                         |
| ---------------- | ------------------------------------------------------------- |
| datetime         | Times in UTC, frontend will convert this into your local time |
| condition        |                                                               |
| temperature      |                                                               |
| precipitation    | in millimeters                                                |
| wind_bearing     |                                                               |
| wind_speed       |                                                               |
| wind_speed_bft   | Not officially supported, but nice addition                   |
| solar_irradiance | Not officially supported, but nice addition                   |

## Examples

Integration with entities, notice the hidden ones: <br>
<img width="674" alt="Integration" src="https://github.com/golles/ha-knmi/assets/2211503/2924375b-5a07-43e4-96c5-fa0caa476053">

Weather cards (hourly and daily forecast): <br>
<img width="500" alt="Weather cards" src="https://github.com/golles/ha-knmi/assets/2211503/23417918-8b08-4005-9c36-5da9ff3e9122">

Weather entity (with daily and hourly forecast tabs): <br>
<img width="543" alt="Weather entity" src="https://github.com/golles/ha-knmi/assets/2211503/8d2b2ad5-c0f8-4890-b1d2-034fd1e7a1e9">

Sun entity: <br>
<img width="551" alt="Sun entity" src="https://github.com/golles/ha-knmi/assets/2211503/a7eb3045-dfb5-42e3-a1b6-ce2b396119a4">

Warning entity: <br>
<img width="552" alt="Warning entity" src="https://github.com/golles/ha-knmi/assets/2211503/66aecc7a-2e84-453e-8669-59db34cf6cb1">

## Collect logs

To activate the debug log necessary for issue reporting, follow these steps:

1. Go to "Configuration" -> "Integrations" -> "KNMI" within the Home Assistant interface.
2. On the left side, locate the "Enable debug logging" button and click on it.
3. Once you collected enough information, Stop debug logging, this will download the log file as well.
4. Share the log file in an issue.

Additionally, logging for this component can be enabled by configuring the logger in Home Assistant with the following steps:

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
[ha-active-installation-badges]: https://github.com/golles/ha-active-installation-badges
[hacs-installs-shield]: https://raw.githubusercontent.com/golles/ha-active-installation-badges/main/badges/knmi.svg
[license-shield]: https://img.shields.io/github/license/golles/ha-knmi.svg?style=for-the-badge
[maintainer]: https://github.com/golles
[maintenance-shield]: https://img.shields.io/badge/maintainer-golles-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/golles/ha-knmi.svg?style=for-the-badge
[releases]: https://github.com/golles/ha-knmi/releases
[stars-shield]: https://img.shields.io/github/stars/golles/ha-knmi?style=for-the-badge
[stars]: https://github.com/golles/ha-knmi/stargazers
