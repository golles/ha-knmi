"""Tests for weather."""

from decimal import Decimal

import pytest
from _pytest.logging import LogCaptureFixture
from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_WEATHER_APPARENT_TEMPERATURE,
    ATTR_WEATHER_DEW_POINT,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_VISIBILITY,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_SPEED,
)
from homeassistant.core import HomeAssistant

from custom_components.knmi.coordinator import KnmiDataUpdateCoordinator
from custom_components.knmi.weather import KnmiWeather, KnmiWeatherDescription

from . import setup_integration, unload_integration


@pytest.mark.parametrize(
    ("input_value", "expected_output"),
    [
        ("zonnig", ATTR_CONDITION_SUNNY),
        ("bliksem", ATTR_CONDITION_LIGHTNING),
        ("buien", ATTR_CONDITION_POURING),
        ("regen", ATTR_CONDITION_RAINY),
        ("hagel", ATTR_CONDITION_HAIL),
        ("mist", ATTR_CONDITION_FOG),
        ("sneeuw", ATTR_CONDITION_SNOWY),
        ("bewolkt", ATTR_CONDITION_CLOUDY),
        ("lichtbewolkt", ATTR_CONDITION_PARTLYCLOUDY),
        ("halfbewolkt", ATTR_CONDITION_PARTLYCLOUDY),
        ("halfbewolkt_regen", ATTR_CONDITION_RAINY),
        ("zwaarbewolkt", ATTR_CONDITION_CLOUDY),
        ("nachtmist", ATTR_CONDITION_FOG),
        ("helderenacht", ATTR_CONDITION_CLEAR_NIGHT),
        ("nachtbewolkt", ATTR_CONDITION_CLOUDY),
        ("wolkennacht", ATTR_CONDITION_CLOUDY),  # Undocumented condition
        ("-", None),  # Unavailable condition
        ("_", None),  # Unavailable condition
    ],
)
async def test_map_conditions(hass: HomeAssistant, input_value: str, expected_output: str) -> None:
    """Test map condition."""
    config_entry = await setup_integration(hass)
    coordinator: KnmiDataUpdateCoordinator = config_entry.runtime_data
    description = KnmiWeatherDescription(key="weer")
    weather = KnmiWeather(config_entry, coordinator, description)

    assert weather.map_condition(input_value) == expected_output


async def test_map_conditions_error(hass: HomeAssistant, caplog: LogCaptureFixture) -> None:
    """Test map condition error cases."""
    config_entry = await setup_integration(hass)
    coordinator: KnmiDataUpdateCoordinator = config_entry.runtime_data
    description = KnmiWeatherDescription(key="weer")
    weather = KnmiWeather(config_entry, coordinator, description)

    assert weather.map_condition(None) is None
    assert 'Weather condition "None" can\'t be mapped, please raise a bug' in caplog.text
    assert weather.map_condition("") is None
    assert 'Weather condition "" can\'t be mapped, please raise a bug' in caplog.text
    assert weather.map_condition("hondenweer") is None
    assert 'Weather condition "hondenweer" can\'t be mapped, please raise a bug' in caplog.text


@pytest.mark.usefixtures("mocked_data")
async def test_state(hass: HomeAssistant) -> None:
    """Test state."""
    config_entry = await setup_integration(hass)

    state = hass.states.get("weather.knmi_home")
    assert state

    assert state.state == "cloudy"

    assert state.attributes.get(ATTR_WEATHER_HUMIDITY) == 97
    assert Decimal(str(state.attributes.get(ATTR_WEATHER_PRESSURE))) == Decimal("1015.03")
    assert Decimal(str(state.attributes.get(ATTR_WEATHER_TEMPERATURE))) == Decimal("10.5")
    assert Decimal(str(state.attributes.get(ATTR_WEATHER_VISIBILITY))) == Decimal("6.99")
    assert Decimal(str(state.attributes.get(ATTR_WEATHER_WIND_BEARING))) == 226
    assert Decimal(str(state.attributes.get(ATTR_WEATHER_WIND_SPEED))) == Decimal("29.1")
    assert Decimal(str(state.attributes.get(ATTR_WEATHER_DEW_POINT))) == Decimal("10.1")
    assert Decimal(str(state.attributes.get(ATTR_WEATHER_APPARENT_TEMPERATURE))) == Decimal("6.8")

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mocked_data")
async def test_async_forecast_daily(hass: HomeAssistant) -> None:  # pylint: disable=too-many-statements  # noqa: PLR0915
    """Test daily forecast."""
    config_entry = await setup_integration(hass)
    coordinator: KnmiDataUpdateCoordinator = config_entry.runtime_data
    description = KnmiWeatherDescription(key="weer")
    weather = KnmiWeather(config_entry, coordinator, description)

    forecast = await weather.async_forecast_daily()
    assert forecast
    assert len(forecast) == 5

    assert forecast[0][ATTR_FORECAST_TIME] == "2024-02-14T00:00:00+01:00"
    assert forecast[0][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[0][ATTR_FORECAST_NATIVE_TEMP_LOW] == 10
    assert forecast[0][ATTR_FORECAST_NATIVE_TEMP] == 10
    assert forecast[0][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 0
    assert forecast[0][ATTR_FORECAST_WIND_BEARING] == 221
    assert forecast[0][ATTR_FORECAST_NATIVE_WIND_SPEED] == 25
    assert forecast[0]["wind_speed_bft"] == 4  # type: ignore  # noqa: PGH003
    assert forecast[0]["sun_chance"] == 0  # type: ignore  # noqa: PGH003

    assert forecast[1][ATTR_FORECAST_TIME] == "2024-02-15T00:00:00+01:00"
    assert forecast[1][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[1][ATTR_FORECAST_NATIVE_TEMP_LOW] == 10
    assert forecast[1][ATTR_FORECAST_NATIVE_TEMP] == 12
    assert forecast[1][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 10
    assert forecast[1][ATTR_FORECAST_WIND_BEARING] == 184
    assert forecast[1][ATTR_FORECAST_NATIVE_WIND_SPEED] == 18
    assert forecast[1]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[1]["sun_chance"] == 8  # type: ignore  # noqa: PGH003

    assert forecast[2][ATTR_FORECAST_TIME] == "2024-02-16T00:00:00+01:00"
    assert forecast[2][ATTR_FORECAST_CONDITION] == "rainy"
    assert forecast[2][ATTR_FORECAST_NATIVE_TEMP_LOW] == 9
    assert forecast[2][ATTR_FORECAST_NATIVE_TEMP] == 10
    assert forecast[2][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 40
    assert forecast[2][ATTR_FORECAST_WIND_BEARING] == 199
    assert forecast[2][ATTR_FORECAST_NATIVE_WIND_SPEED] == 18
    assert forecast[2]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[2]["sun_chance"] == 14  # type: ignore  # noqa: PGH003

    assert forecast[3][ATTR_FORECAST_TIME] == "2024-02-17T00:00:00+01:00"
    assert forecast[3][ATTR_FORECAST_CONDITION] == "partlycloudy"
    assert forecast[3][ATTR_FORECAST_NATIVE_TEMP_LOW] == 6
    assert forecast[3][ATTR_FORECAST_NATIVE_TEMP] == 8
    assert forecast[3][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 20
    assert forecast[3][ATTR_FORECAST_WIND_BEARING] == 228
    assert forecast[3][ATTR_FORECAST_NATIVE_WIND_SPEED] == 18
    assert forecast[3]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[3]["sun_chance"] == 46  # type: ignore  # noqa: PGH003

    assert forecast[4][ATTR_FORECAST_TIME] == "2024-02-18T00:00:00+01:00"
    assert forecast[4][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[4][ATTR_FORECAST_NATIVE_TEMP_LOW] == 7
    assert forecast[4][ATTR_FORECAST_NATIVE_TEMP] == 8
    assert forecast[4][ATTR_FORECAST_PRECIPITATION_PROBABILITY] == 10
    assert forecast[4][ATTR_FORECAST_WIND_BEARING] == 210
    assert forecast[4][ATTR_FORECAST_NATIVE_WIND_SPEED] == 18
    assert forecast[4]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[4]["sun_chance"] == 0  # type: ignore  # noqa: PGH003

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mocked_data")
async def test_async_forecast_hourly(hass: HomeAssistant) -> None:  # pylint: disable=too-many-statements  # noqa: PLR0915
    """Test hourly forecast."""
    config_entry = await setup_integration(hass)
    coordinator: KnmiDataUpdateCoordinator = config_entry.runtime_data
    description = KnmiWeatherDescription(key="weer")
    weather = KnmiWeather(config_entry, coordinator, description)

    forecast = await weather.async_forecast_hourly()
    assert forecast
    assert len(forecast) == 24

    assert forecast[0][ATTR_FORECAST_TIME] == "2024-02-14T23:00:00+01:00"
    assert forecast[0][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[0][ATTR_FORECAST_NATIVE_TEMP] == 10
    assert forecast[0][ATTR_FORECAST_NATIVE_PRECIPITATION] == 0
    assert forecast[0][ATTR_FORECAST_WIND_BEARING] == 231
    assert forecast[0][ATTR_FORECAST_NATIVE_WIND_SPEED] == 21
    assert forecast[0]["wind_speed_bft"] == 4  # type: ignore  # noqa: PGH003
    assert forecast[0]["solar_irradiance"] == 0  # type: ignore  # noqa: PGH003

    assert forecast[3][ATTR_FORECAST_TIME] == "2024-02-15T02:00:00+01:00"
    assert forecast[3][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[3][ATTR_FORECAST_NATIVE_TEMP] == 10
    assert forecast[3][ATTR_FORECAST_NATIVE_PRECIPITATION] == 0
    assert forecast[3][ATTR_FORECAST_WIND_BEARING] == 226
    assert forecast[3][ATTR_FORECAST_NATIVE_WIND_SPEED] == 18
    assert forecast[3]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[3]["solar_irradiance"] == 0  # type: ignore  # noqa: PGH003

    assert forecast[5][ATTR_FORECAST_TIME] == "2024-02-15T04:00:00+01:00"
    assert forecast[5][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[5][ATTR_FORECAST_NATIVE_TEMP] == 10
    assert forecast[5][ATTR_FORECAST_NATIVE_PRECIPITATION] == 0
    assert forecast[5][ATTR_FORECAST_WIND_BEARING] == 219
    assert forecast[5][ATTR_FORECAST_NATIVE_WIND_SPEED] == 18
    assert forecast[5]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[5]["solar_irradiance"] == 0  # type: ignore  # noqa: PGH003

    assert forecast[8][ATTR_FORECAST_TIME] == "2024-02-15T07:00:00+01:00"
    assert forecast[8][ATTR_FORECAST_CONDITION] == "pouring"
    assert forecast[8][ATTR_FORECAST_NATIVE_TEMP] == 10
    assert Decimal(str(forecast[8][ATTR_FORECAST_NATIVE_PRECIPITATION])) == Decimal("0.9")
    assert forecast[8][ATTR_FORECAST_WIND_BEARING] == 196
    assert forecast[8][ATTR_FORECAST_NATIVE_WIND_SPEED] == 14
    assert forecast[8]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[8]["solar_irradiance"] == 0  # type: ignore  # noqa: PGH003

    assert forecast[13][ATTR_FORECAST_TIME] == "2024-02-15T12:00:00+01:00"
    assert forecast[13][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[13][ATTR_FORECAST_NATIVE_TEMP] == 12
    assert forecast[13][ATTR_FORECAST_NATIVE_PRECIPITATION] == 0
    assert forecast[13][ATTR_FORECAST_WIND_BEARING] == 206
    assert forecast[13][ATTR_FORECAST_NATIVE_WIND_SPEED] == 14
    assert forecast[13]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[13]["solar_irradiance"] == 30  # type: ignore  # noqa: PGH003

    assert forecast[18][ATTR_FORECAST_TIME] == "2024-02-15T17:00:00+01:00"
    assert forecast[18][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[18][ATTR_FORECAST_NATIVE_TEMP] == 14
    assert forecast[18][ATTR_FORECAST_NATIVE_PRECIPITATION] == 0
    assert forecast[18][ATTR_FORECAST_WIND_BEARING] == 168
    assert forecast[18][ATTR_FORECAST_NATIVE_WIND_SPEED] == 14
    assert forecast[18]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[18]["solar_irradiance"] == 72  # type: ignore  # noqa: PGH003

    assert forecast[23][ATTR_FORECAST_TIME] == "2024-02-15T22:00:00+01:00"
    assert forecast[23][ATTR_FORECAST_CONDITION] == "cloudy"
    assert forecast[23][ATTR_FORECAST_NATIVE_TEMP] == 12
    assert forecast[23][ATTR_FORECAST_NATIVE_PRECIPITATION] == 0
    assert forecast[23][ATTR_FORECAST_WIND_BEARING] == 162
    assert forecast[23][ATTR_FORECAST_NATIVE_WIND_SPEED] == 18
    assert forecast[23]["wind_speed_bft"] == 3  # type: ignore  # noqa: PGH003
    assert forecast[23]["solar_irradiance"] == 0  # type: ignore  # noqa: PGH003

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mocked_data")
async def test_async_forecast_twice_daily(hass: HomeAssistant) -> None:
    """Test twice daily forecast."""
    config_entry = await setup_integration(hass)
    coordinator: KnmiDataUpdateCoordinator = config_entry.runtime_data
    description = KnmiWeatherDescription(key="weer")
    weather = KnmiWeather(config_entry, coordinator, description)

    with pytest.raises(NotImplementedError):
        await weather.async_forecast_twice_daily()

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mocked_data")
@pytest.mark.parametrize("mocked_data", ["warm_snow.json"], indirect=True)
async def test_warm_snow_fix(hass: HomeAssistant) -> None:
    """Test if we return rainy if the API returns snowy and a temp higher than 6."""
    config_entry = await setup_integration(hass)

    state = hass.states.get("weather.knmi_home")
    assert state
    assert state.state == ATTR_CONDITION_RAINY

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mocked_data")
@pytest.mark.parametrize("mocked_data", ["cold_snow.json"], indirect=True)
async def test_real_snow(hass: HomeAssistant) -> None:
    """Test if we return snowy if the API returns snowy and a temp lower than 6."""
    config_entry = await setup_integration(hass)

    state = hass.states.get("weather.knmi_home")
    assert state
    assert state.state == ATTR_CONDITION_SNOWY

    await unload_integration(hass, config_entry)


@pytest.mark.freeze_time("2023-02-05T15:30:00+00:00")
@pytest.mark.usefixtures("mocked_data")
@pytest.mark.parametrize("mocked_data", ["clear_night_fix.json"], indirect=True)
async def test_sunny_during_day(hass: HomeAssistant) -> None:
    """When the API returns sunny when the sun isn't set, the weather state should be sunny."""
    config_entry = await setup_integration(hass)

    state = hass.states.get("weather.knmi_home")
    assert state
    assert state.state == ATTR_CONDITION_SUNNY

    await unload_integration(hass, config_entry)


@pytest.mark.freeze_time("2023-02-05T03:30:00+01:00")
@pytest.mark.usefixtures("mocked_data")
@pytest.mark.parametrize("mocked_data", ["clear_night_fix.json"], indirect=True)
async def test_clear_night_during_night(hass: HomeAssistant) -> None:
    """When the API returns sunny when the sun is set, the weather state should be clear night."""
    config_entry = await setup_integration(hass)

    state = hass.states.get("weather.knmi_home")
    assert state
    assert state.state == ATTR_CONDITION_CLEAR_NIGHT

    await unload_integration(hass, config_entry)
