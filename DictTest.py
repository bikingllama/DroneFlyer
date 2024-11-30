commands = {
    "start_charging": 1,
    "stop_charging": 2,
    "turn_on_controller": 3,
    "turn_off_controller": 4,
    "perform_special_task": 9,
}




if 1 in commands.values():
    print(":)")
else:
    print(":(")