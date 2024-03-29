**Plugin Archived. Not working**


VistaPool integration for home assistant
============================================================

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![hacs][hacsbadge]](hacs)

Description
------------
The `havistapool` component offers integration with the Vista Pool API and offers temperature, Ph, Rx and relay readings from your pool automation system.

NOTE. This is based on reverse engineering work of the IOS app since there is no official API. 

Credits go to the guys that made the [audi_connect_ha](https://github.com/arjenvrh/audi_connect_ha) plugin. I've based the implementation on their plugin code though highly modified to fit this and future purposes.

Installation
------------

There are two ways this integration can be installed into [Home Assistant](https://www.home-assistant.io).

The easiest way is to install the integration using [HACS](https://hacs.xyz).

Alternatively, installation can be done manually by copying the files in this repository into the custom_components directory in the HA configuration directory:
1. Open the configuration directory of your HA configuration.
2. If you do not have a custom_components directory, you need to create it.
3. In the custom_components directory create a new directory called vistapool.
4. Copy all the files from the custom_components/vistapool/ directory in this repository into the vistapool directory.
5. Restart Home Assistant
6. Add the integration to Home Assistant (see `Configuration`)

Configuration
-------------

Configuration is done through the Home Assistant UI.

To add the integration, go to `Configuration->Integrations`, click `+` and search for `Vista Pool`

![Configuration](ha_config.png)

Configuration Variables
-----------------------
**username**

- (string)(Required)The username associated with your Vista Pool account.

**password**

- (string)(Required)The password for your given Vista Pool account.

**scan_interval**

- specify in minutes how often to fetch status data from Vista Pool (optional, default 5 min, minimum 1 min)


[commits]: https://github.com/tellerbop/havistapool/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
