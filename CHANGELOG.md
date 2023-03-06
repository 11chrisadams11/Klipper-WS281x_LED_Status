# Change Log

----

## 2023-03-04
Remove power off functions and add Moonraker API class

### Changed
- Removed settings and functions for powering off printer, as it was not related to controlling LED strips (moved to https://github.com/11chrisadams11/klipper-power-off-on-completion)
- Moved Moonraker API functions to a class
- General cleanup

----

## 2022-05-15
Threading and settings sample

### Changed
- Moved non-progress effects to their own thread to avoid pause between status checks
- Cleaned up effects class to work with threads
- Renamed settings.conf to settings_sample.conf to not overwrite previous settings
- Write sample settings if file not found
- Update service sample to clear LED strip on service stop

----

## 2022-04-04
More effects and a lot of cleanup.
The settings format has changed a bit, so you might need to redo your changes (Sorry)

### Added
- More effects (fill, fill_unfill, fill_chase, twinkle, twinkle_colors, noise, wave)
- Ability to specify a second color to blend with first
- Rainbow as a color choice

### Changed
- Moved effects to a class to enable effects to work with more color selections
- Cleaned up testing outputs
- Tried to make the install instruction more clear

### Fixed
- Fixed command in README.md (thanks [NatatorD](https://github.com/11chrisadams11/Klipper-WS281x_LED_Status/issues/9))