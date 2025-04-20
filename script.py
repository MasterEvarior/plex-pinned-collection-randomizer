import os
import sys
import random
from plexapi.server import PlexServer
from plexapi.library import Library
from plexapi.collection import Collection
from typing import List


def get_env_var(name: str) -> str:
    result = os.environ.get(name)
    if result == None:
        sys.exit("Environment variable %s is not defined, exiting script!" % name)
    return result


def get_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value != None and value.isdigit():
        return int(value)
    else:
        return default


def get_list(name: str) -> List[str]:
    value = os.environ.get(name)
    if value == None:
        return []
    return value.split(";")


def get_libraries(server: PlexServer) -> List[Library]:
    return [
        section
        for section in server.library.sections()
        if section.type in ["movie", "show"]
    ]


def get_all_collections(libraries: List[Library]) -> List[Collection]:
    all_collections = []
    for library in libraries:
        all_collections.extend(library.collections())
    return all_collections


def unpin_from_everywhere(collection: Collection) -> None:
    hub = collection.visibility()
    hub.demoteRecommended()
    hub.demoteHome()
    hub.demoteShared()


def pin_collection(collection: Collection) -> None:
    hub = collection.visibility()
    hub.promoteRecommended()
    hub.promoteHome()
    hub.promoteShared()


def pin_random_collections(
    collections: List[Collection], amount: int, min: int
) -> None:
    pinned_collections = []

    for _ in range(amount):
        collection_to_pin = random.choice(collections)
        while (
            collection_to_pin in pinned_collections
            or collection_to_pin.childCount < min
        ):
            collection_to_pin = random.choice(collections)

        print(f"    - Pinning {collection_to_pin.title}")
        pin_collection(collection_to_pin)


def main():
    PLEX_BASE_URL = get_env_var("PPCR_BASE_URL")
    PLEX_TOKEN = get_env_var("PPCR_TOKEN")
    AMOUNT = get_int("PPCR_AMOUNT", 5)
    MIN = get_int("PPCR_MIN_AMOUNT_IN_COLLECTION", 0)
    ALWAYS_PIN = get_list("PPCR_ALWAYS_PIN")

    plex = PlexServer(PLEX_BASE_URL, PLEX_TOKEN)

    libraries = get_libraries(plex)

    print("Starting with the following configuration:")
    print(f"    - Plex URL: {PLEX_BASE_URL}")
    print(f"    - Plex Token: *****")
    print(f"    - Amount of collections to pin: {AMOUNT}")
    print(f"    - Minimum of movies in collection to allow for pinning: {MIN}")
    print(f"    - Found {len(ALWAYS_PIN)} collections to always pin:")
    for collection_to_pin in ALWAYS_PIN:
        print(f"        - {collection_to_pin}")

    print("Detected the following libraries:")
    for library in libraries:
        print(f"    - {library.title} ({library.type})")

    print("Detecting all available collections:")
    all_collections = get_all_collections(libraries)
    print(f"    - Detected {len(all_collections)} collections in total")

    collections_to_always_pin = []
    print("Upinning all collections:")
    for collection in all_collections:
        if any(keyword in collection.title for keyword in ALWAYS_PIN):
            print(
                f"    - NOT unpinning {collection.title} because it is marked as always pinned"
            )
            collections_to_always_pin.append(collection)
        else:
            print(f"    - Unpinning {collection.title}")
            unpin_from_everywhere(collection)

    print(f"Pinning {AMOUNT} random collections")
    pin_random_collections(all_collections, AMOUNT, MIN)

    print("Additionally pinning the following collections: ")
    for collection in collections_to_always_pin:
        print(f"    - {collection.title}")
        pin_collection(collection)


if __name__ == "__main__":
    main()
