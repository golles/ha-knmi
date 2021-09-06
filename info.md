[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [knmi][knmi]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Weather alert `True` or `False`, the alert itself is an attribute.
`sensor` | a few weather related sensors.
`weather` | Weather data provided by KNMI, https://weerlive.nl/.

{% if not installed %}
## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "knmi".

{% endif %}


## Configuration is done in the UI

<!---->

***

[knmi]: https://github.com/golles/ha-knmi
[buymecoffee]: https://www.buymeacoffee.com/golles
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/golles/ha-knmi.svg?style=for-the-badge
[commits]: https://github.com/golles/ha-knmi/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com/golles/ha-knmi/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/golles/ha-knmi.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-golles-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/golles/ha-knmi.svg?style=for-the-badge
[releases]: https://github.com/golles/ha-knmi/releases
[user_profile]: https://github.com/golles
