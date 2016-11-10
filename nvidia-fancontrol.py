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
    if temperature < 80:
        return 100

def load_config(path="/etc/nvidia_fancontrol.py"):
    spec  = importlib.util.spec_from_file_location("module.name", path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def plot_fan_curves(config):
    try:
        from matplotlib import pyplot as plt
    except:
        return

    T = list(range(0, 100))

    plt.figure(figsize=(6, 6))

    plt.grid()

    plt.xlim(0, 100)
    plt.ylim(0, 105)
    plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    plt.xlabel("temperature / °C")
    plt.ylabel("percental fan speed")

    for fan, control in config.fan_controls.items():
        if not control[1]:
            speed = [fan_curve(T_) for T_ in T]
        else:
            try:
                f = getattr(config, control[1])
                speed = [f(T_) for T_ in T]
            except:
                speed = [fan_curve(T_) for T_ in T]
        plt.plot(T, speed, label=fan)
    title = plt.title("nvidia-fancontrol fan curves")
    legend = plt.legend(loc="upper center", fancybox=True, ncol=4, bbox_to_anchor=(0.5, -0.1))
    plt.savefig("/tmp/nvidia_fancontrol.pdf", bbox_extra_artists=(legend, title,), bbox_inches='tight')

if __name__ == "__main__":
    config = load_config()

    plot_fan_curves(config)

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
