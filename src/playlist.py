import json
import os
import uuid
from time import time
from datetime import datetime

from Sand import STORE_PATH


_PLAYLIST_FILE = os.path.join(STORE_PATH, '_playlist.json')


def _json_safe(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    return str(value)


class Playlist:
    @staticmethod
    def _title_for(method, created):
        stamp = datetime.fromtimestamp(int(created)).strftime('%Y-%m-%d %H:%M:%S')
        return '%s %s' % (str(method), stamp)

    @staticmethod
    def _delete_item_image(item):
        imageFile = str(item.get('imageFile', '') or '').strip()
        if not imageFile:
            return
        imageName = os.path.basename(imageFile)
        if not imageName:
            return
        imagePath = os.path.join(STORE_PATH, imageName)
        try:
            os.remove(imagePath)
        except OSError:
            pass

    @staticmethod
    def _load():
        try:
            with open(_PLAYLIST_FILE, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

        if not isinstance(payload, list):
            return []
        return payload

    @staticmethod
    def _save(items):
        with open(_PLAYLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, sort_keys=False)

    @staticmethod
    def list():
        return Playlist._load()

    @staticmethod
    def add(method, params, title=''):
        items = Playlist._load()
        created = int(time())
        item = {
            'id': uuid.uuid4().hex,
            'method': str(method),
            # Normalize display naming for playlist entries.
            'title': Playlist._title_for(method, created),
            'created': created,
            'params': _json_safe(params if isinstance(params, dict) else {}),
            'imageFile': '',
        }
        items.append(item)
        Playlist._save(items)
        return item

    @staticmethod
    def setImage(itemId, imageFile):
        itemId = str(itemId)
        imageFile = os.path.basename(str(imageFile or '').strip())
        if not imageFile:
            return False

        items = Playlist._load()
        for item in items:
            if str(item.get('id', '')) == itemId:
                item['imageFile'] = imageFile
                Playlist._save(items)
                return True
        return False

    @staticmethod
    def remove(itemId):
        itemId = str(itemId)
        items = Playlist._load()
        updated = []
        for item in items:
            if str(item.get('id', '')) == itemId:
                Playlist._delete_item_image(item)
                continue
            updated.append(item)
        Playlist._save(updated)

    @staticmethod
    def clear():
        for item in Playlist._load():
            Playlist._delete_item_image(item)
        Playlist._save([])

    @staticmethod
    def move(itemId, direction):
        """Move an item by one position. direction < 0 moves up, > 0 moves down."""
        itemId = str(itemId)
        items = Playlist._load()
        if not items:
            return False

        index = None
        for i, item in enumerate(items):
            if str(item.get('id', '')) == itemId:
                index = i
                break

        if index is None:
            return False

        newIndex = index - 1 if direction < 0 else index + 1
        if newIndex < 0 or newIndex >= len(items):
            return False

        items[index], items[newIndex] = items[newIndex], items[index]
        Playlist._save(items)
        return True
