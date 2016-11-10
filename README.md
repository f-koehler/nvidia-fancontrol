nvidia-fancontrol
=================
Control the fan speed of your Nvidia GPU through the proprietary driver using your own fan curve.

Preqrequisites
--------------
- `python 3.4`
- `nvidia-settings` (through Nvidia's proprietary driver)
- allow fan control by setting the correct cool-bits (e.g. `nvidia-xconfig --cool-bits=4`)

Configuration
-------------
`nvidia-fancontrol` is control via a python file `/etc/nvidia_fancontrol.py`:
```python
fan_controls = {
    "[fan:0]": ("[gpu:0]", None)
}
interval = 5
```
The variable `interval = 5` means that the fan speeds are adjusted every 5 seconds.
The fans you want to control have to be specidied in the `fan_controls` dictionary.
The key of the dict is the fan identifier.
The first element of the value is the GPU whose core temperature will be used to adjust the fan speed.
Both IDs can be readout using `nvidia-settings` (both console and the gui) but I plan to provide an easy command-line interface to do this.
The second element of the value tuple is the name of a function (in the same python file!) as a string.
It can also be `None` in which case the `fan_curve` function from `nvidia-fancontrol.py` will be used.
So you could for example write
```python
fan_controls = {
    "[fan:0]": ("[gpu:0]", "fixed_speed")
}
interval = 5

def fixed_speed(temperature):
    return 50
```
to set the fan speed to a constant 50%.

Future plans
------------
- command line interface
- create plots of the fan curve at startup
- some logging of temperature and speed (changes)
