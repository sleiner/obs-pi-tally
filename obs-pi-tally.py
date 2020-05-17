import logging
from dataclasses import dataclass
from threading import Condition
from time import sleep
from typing import List

import obswebsocket
from obswebsocket import events, requests


@dataclass(unsafe_hash=True)
class Source:
    name: str
    kind: str


@dataclass
class Tally:
    name: str
    pin: int
    low_active: bool


@dataclass
class Config:
    tallies: List[Tally]


cv = Condition()
scenes = dict()
config = Config([Tally("iPhone 7: USB", pin=1, low_active=True),
                 Tally("iPhone XS: USB", pin=2, low_active=False)])


def __list_sources(scene, scenelist, including_invisible: bool):
    sources = set()
    for sceneItem in scene:
        isVisible = sceneItem['render']
        if isVisible or including_invisible:
            sources.add(Source(name=sceneItem['name'], kind=sceneItem['type']))
            if sceneItem['type'] == 'group':
                sources.update(__list_sources(sceneItem['groupChildren'], scenelist,
                                              including_invisible))
            elif sceneItem['type'] == 'scene':
                sources.update(__list_sources(
                    scenelist[sceneItem['name']], scenelist, including_invisible))
    return sources


def list_sources(scene, including_invisible: bool = False):
    global scenes, cv
    with cv:
        result = __list_sources(scene, scenes, including_invisible)
    return result


def update_leds(scene):
    sources_in_scene = list_sources(scene)
    source_names_in_scene = [source.name for source in sources_in_scene]
    tally_state = [(tally, tally.name in source_names_in_scene)
                   for tally in config.tallies]
    print(tally_state)


def on_scene_change(event):
    logging.info(f"Scene changed to: {event.getSceneName()}")
    update_leds(event.getSources())


def on_event(event):
    logging.debug(f" => Received {event}")


def trigger_scenelist_update(*args):
    with cv:
        cv.notify()


def __update_scenes(ws_client: obswebsocket.obsws) -> List:
    # returns the list of sources in the current scene
    global scenes

    scenelist = ws_client.call(requests.GetSceneList())
    scenes = {s['name']: s['sources'] for s in scenelist.getScenes()}
    current = scenelist.getCurrentScene()
    return scenes[current]


def __update_scenes_and_leds(ws_client: obswebsocket.obsws):
    current_scene = __update_scenes(ws_client)
    update_leds(current_scene)


def main():
    global scenes, cv

    client = obswebsocket.obsws()
    client.register(on_scene_change, events.SwitchScenes)
    client.register(on_event)
    for event in [events.ScenesChanged,
                  events.SourceCreated,
                  events.SourceDestroyed,
                  events.SourceRenamed,
                  events.SceneItemAdded,
                  events.SceneItemRemoved,
                  events.SceneItemVisibilityChanged,
                  ]:
        client.register(trigger_scenelist_update, event)
    client.connect()

    __update_scenes_and_leds(client)

    try:
        while True:
            with cv:
                cv.wait()  # ... until a scenelist update was triggered
                __update_scenes_and_leds(client)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
