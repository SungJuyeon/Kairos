



def control_led(action):
    from mqtt_client import home_control
    if action == "켜줘":
        home_control("led", "true")
    elif action == "꺼줘":
        home_control("led", "false")
def control_induction(action):
    from mqtt_client import home_control
    if action == "꺼줘":
        home_control("induction", "false")
def control_relay(action):
    from mqtt_client import home_control
    if action == "켜줘":
        home_control("relay", "true")
    elif action == "꺼줘":
        home_control("relay", "false")
