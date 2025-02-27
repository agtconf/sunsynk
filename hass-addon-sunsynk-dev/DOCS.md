# Configuration

## Parameters

- `PORT` & `DRIVER`

  The port for RS485 communications, which can be either:

  - **umodbus** driver

    - A serial:// port. List of available ports under _Supervisor_ -> _System_ tab -> _Host_ card **&vellip;** -> _Hardware_

      Example:
      ```yaml
      PORT: serial:///dev/ttyUSB0
      DRIVER: umodbus
      ```

    - A tcp:// port of a Modbus TCP server. Example:
      ```yaml
      PORT: tcp://homeassistant.local:502
      DRIVER: umodbus
      ```

      This repository contains a mbusd TCP gateway add-on that can be used for this purpose.

    - A RFC2217 compatible port (e.g. `tcp://homeassistant.local:6610`)

  - **pymodbus** driver

    - Serial example
      ```yaml
      PORT: /dev/ttyUSB0
      DRIVER: pymodbus
      ```

    - TCP example
      ```yaml
      PORT: homeassistant.local:502
      DRIVER: pymodbus
      ```

- `SUNSYNK_ID`

  The serial number of your inverter. When you start the add-on the connected serial will be displayed in the log.

  The add-on will not run if the expected/configured serial number is not found.

  > This must be a string. So if your serial is a number only surround it with quotes `'1000'`

- `MODBUS_SERVER_ID`

  The Modbus Server ID, typically 1. Might be different in multi-inverter setups.

- `SENSOR_PREFIX`

  A prefix to add to all the MQTT Discovered Home Assistant Sensors (default: SS).

- `PROFILES`

  > BETA!!
  >
  > This writes settings, use at your own risk!

  Read & Write settings to your inverter.

  The profiles will be presented as a Home Assistant Select Entity, with options for the different profiles.

  Available profiles:

  | Profile              | Description                                                                              |
  | -------------------- | ---------------------------------------------------------------------------------------- |
  | system_mode          | The system mode, including time, grid charging, target SOC.                              |
  | system_mode_voltages | The system mode charging voltages (likely used when you dont have a Battery with a BMS). |

  The Inverter setting is only read when the Add-On starts, if you want to force re-reading the inverter settings and any configuration, choose the **UPDATE** option in the Select Entity. (You can schedule **UPDATE** through automations if this is important for you)

  When you **UPDATE** a profile, the Add-On performs the following actions:
  - Read all the settings related to the profile from the Inverter.
  - Read all the profile presets from `/share/hass-addon-sunsynk/*.yml`
  - The value of the Home Assistant Select entity will reflect the matching presets.
    - If the current settings is not part of existing presets, a new profile will be created.

      You can customize the name of the presets in the Yaml files (followed by an **UPDATE**).
      One option to access these files is though the Samba Add-On.

- `SENSORS`

  A list of sensors to poll. You can use any sensor defined in the sunsynk Python library - [here](https://github.com/kellerza/sunsynk/blob/main/sunsynk/definitions.py).

- `MQTT_*`

  You will need a working MQTT sevrer since all values will be sent via MQTT.
  The default configuration assumes the Mosquitto broker add-on and you simply have to
  fill in your password.

- `DEBUG`

  The values received will continuously be printed to the add-on's log. This will confirm
  that you receive values.

  | Value | Description                  |
  | ----- | ---------------------------- |
  | `0`   | No debug messages.           |
  | `1`   | Messages for filter changes. |
  | `2`   | Debug level logging.         |

## Sensor modifiers - Min/Max/Now/Average/Step

Sensors fields can be modified by adding a modifier to the end of the field name.
Without any modifier, a [default modifier](https://github.com/kellerza/sunsynk/blob/main/hass-addon-sunsynk/filter.py#L135) will be added based on the field name.



| Modifier       | Description                                                                                                                                                                                    |
| -------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `:avg`         | the average over the last 60 seconds.                                                                                                                                                          |
| `:max`         | the maximum value over the last 60 seconds. Ideal for _counters_ where you are typically interested only in the last value.                                                                    |
| `:min`         | the minimum value over the last 60 seconds.                                                                                                                                                    |
| `:now`         | the maximum value over the last 2 seconds. Useful to see current sensor value.                                                                                                                 |
| `:round_robin` | cycle over all configured settings. Ideal for config settings.                                                                                                                                 |
| `:step`        | the average over the last minute will be reported, except if there is a significant change (>50) then it will be reported immediately. This is useful for automations using the current power. |

## Home Assistant

### Energy Management

You can read more Energy Management in Home Assistant [here](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/) or [here](https://www.home-assistant.io/docs/energy/).

  >Add these sensors to the Home Assistant Energy Panel:
  >
  > [![Open your Home Assistant instance and show your Energy configuration panel.](https://my.home-assistant.io/badges/config_energy.svg)](https://my.home-assistant.io/redirect/config_energy/)
  > [![Open your Home Assistant instance and show your Energy panel.](https://my.home-assistant.io/badges/energy.svg)](https://my.home-assistant.io/redirect/energy/)

Sensors required to use Energy Management for a hybrid inverter with PV and a battery:

```yaml
SENSORS:
  - total_active_power
  - total_grid_export
  - total_grid_import
  - total_pv_power
  - total_load_power
  - total_battery_charge
  - total_battery_discharge
```



### Templates

You can view sensor values under Home Assistant using the "Developer Tools" -> Templates tab.

```jinja
Essentials:     {{ states("sensor.ss_essential_power") }} W
Non-Essentials: {{ states("sensor.ss_non_essential_power") }} W
Grid CT:        {{ states("sensor.ss_grid_ct_power") }} W


Battery:
  {{ states("sensor.ss_battery_power") }} W
  {{ states("sensor.ss_battery_voltage") }} V
  {{ states("sensor.ss_battery_current") }} Amps
  {{ states("sensor.ss_battery_temperature") }} °C

Grid Power:
  {{ states("sensor.ss_grid_power") }} W
  {{ states("sensor.ss_grid_frequency") }} Hz
  {{ states("sensor.ss_grid_voltage") }} V
  {{ states("sensor.ss_grid_current") }} Amp
  CT {{ states("sensor.ss_grid_ct_power") }} W

Inverter
  {{ states("sensor.ss_inverter_power") }} W
  {{ states("sensor.ss_inverter_frequency") }} Hz

Load
  {{ states("sensor.ss_essential_power") }} W
  {{ states("sensor.ss_grid_frequency") }} Hz
  {{ states("sensor.ss_grid_voltage") }} V
  {{ states("sensor.ss_grid_current") }} Amp

PV1
  {{ states("sensor.ss_pv1_power") }} W
  {{ states("sensor.ss_pv1_voltage") }} V
  {{ states("sensor.ss_pv1_current") }} A
```
