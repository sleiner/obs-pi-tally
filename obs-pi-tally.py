import obswebsocket

from time import sleep


def on_scene_change(message):
    print(f"Scene changed to \"{message.getSceneName()}\"")


def main():
    client = obswebsocket.obsws()
    client.register(on_scene_change, obswebsocket.events.SwitchScenes)
    client.connect()

    try:
        while(True):
            sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
