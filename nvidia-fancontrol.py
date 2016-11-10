#!/usr/bin/env python3

# Licensed under the MIT license (see LICENSE file)
# (C) Fabian Köhler 2016

from subprocess import check_output
from time import sleep
import importlib.util

def enable_fan_control(id):
    check_output([
        "nvidia-settings",
        "-a",
        id + "/GPUFanControlState=1"
    ])

def get_core_temperature(id):
    return int(check_output([
        "nvidia-settings",
        "-t",
        "-q",
        id + "/GPUCoreTemp"
    ]).decode())

def get_fan_speed(id):
    return int(check_output([
        "nvidia-settings",
        "-t",
        "-q",
        id + "/GPUCurrentFanSpeed"
    ]).decode())

def set_fan_speed(speed, id):
    check_output([
        "nvidia-settings",
        "-a",
        id + "/GPUTargetFanSpeed=" + str(speed)
    ])

def fan_curve(temperature):
    if temperature < 50:
        return 0
    if temperature < 60:
        return 20
    if temperature < 70:
        return 50
    if temperautre < 80:
        return 100

def load_config(path="/etc/nvidia_fancontrol.py"):
    spec  = importlib.util.spec_from_file_location("module.name", path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

if __name__ == "__main__":
    config = load_config()

    for _, control in config.fan_controls.items():
        enable_fan_control(control[0])

    while True:
        for fan, control in config.fan_controls.items():
            core_temp = get_core_temperature(control[0])
            current_speed = get_fan_speed(fan)
            if not control[1]:
                target_speed = fan_curve(core_temp)
            else:
                try:
                    target_speed = getattr(config, control[1])(core_temp)
                except:
                    target_speed = fan_curve(core_temp)

            if target_speed != current_speed:
                set_fan_speed(target_speed, fan)
        sleep(config.interval)
