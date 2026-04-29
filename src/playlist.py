import json
import os
import uuid
from time import time
from datetime import datetime

from Sand import STORE_PATH


_PLAYLIST_DIR = os.path.join(STORE_PATH, 'playlists')
_PLAYLIST_FILE = os.path.join(_PLAYLIST_DIR, 'Untitled.json')
_LEGACY_PLAYLIST_FILE_IN_DIR = os.path.join(_PLAYLIST_DIR, '_playlist.json')
_LEGACY_PLAYLIST_FILE = os.path.join(STORE_PATH, '_playlist.json')
_DEFAULT_PLAYLIST_NAME = 'Untitled'
_ACTIVE_PLAYLIST_FILE = os.path.join(_PLAYLIST_DIR, '_active_playlist.txt')


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
    def _ensure_storage_dir():
        os.makedirs(_PLAYLIST_DIR, exist_ok=True)

    @staticmethod
    def _safe_relative_store_path(path):
        value = str(path or '').replace('\\', '/').strip()
        if not value:
            return ''
        if value.startswith('/'):
            value = value.lstrip('/')
        norm = os.path.normpath(value)
        if norm in ('.', '') or norm.startswith('..'):
            return ''
        return norm

    @staticmethod
    def _safe_playlist_name(name):
        value = str(name or '').strip()
        if not value:
            return ''
        if any(k in value for k in '/\\~'):
            return ''
        base = os.path.basename(value)
        if base.endswith('.json'):
            base = base[:-5]
        base = base.strip().strip('.')
        if not base or base.startswith('_'):
            return ''
        return base

    @staticmethod
    def _named_playlist_path(name):
        safe = Playlist._safe_playlist_name(name)
        if not safe:
            return None, None
        Playlist._ensure_storage_dir()
        return safe, os.path.join(_PLAYLIST_DIR, '%s.json' % safe)

    @staticmethod
    def _active_name():
        Playlist._ensure_storage_dir()
        try:
            with open(_ACTIVE_PLAYLIST_FILE, 'r', encoding='utf-8') as f:
                safe = Playlist._safe_playlist_name(f.read())
                if safe:
                    return safe
        except OSError:
            pass
        return _DEFAULT_PLAYLIST_NAME

    @staticmethod
    def _set_active_name(name):
        safe = Playlist._safe_playlist_name(name)
        if not safe:
            return False
        Playlist._ensure_storage_dir()
        try:
            with open(_ACTIVE_PLAYLIST_FILE, 'w', encoding='utf-8') as f:
                f.write(safe)
        except OSError:
            return False
        return True

    @staticmethod
    def _active_playlist_path():
        safe = Playlist._active_name()
        _, path = Playlist._named_playlist_path(safe)
        return safe, path

    @staticmethod
    def active_name():
        return Playlist._active_name()

    @staticmethod
    def image_paths(itemId):
        Playlist._ensure_storage_dir()
        imageName = '_playlist_%s.png' % str(itemId)
        relPath = 'playlists/%s' % imageName
        absPath = os.path.join(_PLAYLIST_DIR, imageName)
        return relPath, absPath

    @staticmethod
    def _title_for(method, created):
        stamp = datetime.fromtimestamp(int(created)).strftime('%Y-%m-%d %H:%M:%S')
        return '%s %s' % (str(method), stamp)

    @staticmethod
    def _delete_item_image(item):
        imageFile = Playlist._safe_relative_store_path(item.get('imageFile', ''))
        if not imageFile:
            return
        imagePath = os.path.normpath(os.path.join(STORE_PATH, imageFile))
        storeRoot = os.path.abspath(STORE_PATH)
        absPath = os.path.abspath(imagePath)
        if not (absPath == storeRoot or absPath.startswith(storeRoot + os.sep)):
            return
        try:
            os.remove(imagePath)
        except OSError:
            pass

    @staticmethod
    def _load():
        Playlist._ensure_storage_dir()

        activeName, activePath = Playlist._active_playlist_path()

        paths = [activePath]
        if activeName == _DEFAULT_PLAYLIST_NAME:
            paths.append(_LEGACY_PLAYLIST_FILE_IN_DIR)
            if os.path.exists(_LEGACY_PLAYLIST_FILE):
                paths.append(_LEGACY_PLAYLIST_FILE)

        payload = None
        for path in paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    payload = json.load(f)
                break
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                continue

        if payload is None:
            Playlist._save([])
            return []

        if not isinstance(payload, list):
            return []
        return payload

    @staticmethod
    def _save(items):
        Playlist._ensure_storage_dir()
        activeName, activePath = Playlist._active_playlist_path()
        Playlist._set_active_name(activeName)
        with open(activePath, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, sort_keys=False)

    @staticmethod
    def _save_items_to_name(name, items):
        safe, path = Playlist._named_playlist_path(name)
        if not path:
            return False
        Playlist._ensure_storage_dir()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(items if isinstance(items, list) else [], f, indent=2, sort_keys=False)
        return True

    @staticmethod
    def list_saved():
        Playlist._ensure_storage_dir()
        names = []
        for entry in sorted(os.listdir(_PLAYLIST_DIR)):
            if not entry.endswith('.json'):
                continue
            if entry.startswith('_'):
                continue
            names.append(entry[:-5])
        if _DEFAULT_PLAYLIST_NAME not in names:
            names.insert(0, _DEFAULT_PLAYLIST_NAME)
        return names

    @staticmethod
    def save_named(name):
        safe, path = Playlist._named_playlist_path(name)
        if not path:
            return False, 'Invalid playlist name', ''
        oldActive = Playlist._active_name()
        items = Playlist._load()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, sort_keys=False)
        except OSError as error:
            return False, str(error), ''
        Playlist._set_active_name(safe)

        # If Untitled was the source playlist, reset it without touching image files.
        # This avoids deleting assets that may still be referenced by other playlists.
        if oldActive == _DEFAULT_PLAYLIST_NAME and safe != _DEFAULT_PLAYLIST_NAME:
            try:
                Playlist._save_items_to_name(_DEFAULT_PLAYLIST_NAME, [])
            except OSError:
                pass

        return True, 'Saved playlist "%s"' % safe, safe

    @staticmethod
    def load_named(name):
        safe, path = Playlist._named_playlist_path(name)
        if not path:
            return False, 'Invalid playlist name', ''
        try:
            with open(path, 'r', encoding='utf-8') as f:
                items = json.load(f)
        except FileNotFoundError:
            if safe == _DEFAULT_PLAYLIST_NAME:
                Playlist._set_active_name(safe)
                Playlist._save([])
                return True, 'Loaded playlist "%s"' % safe, safe
            return False, 'Playlist "%s" was not found' % safe, ''
        except (json.JSONDecodeError, OSError) as error:
            return False, str(error), ''
        if not isinstance(items, list):
            return False, 'Playlist file is not valid', ''
        Playlist._set_active_name(safe)
        return True, 'Loaded playlist "%s"' % safe, safe

    @staticmethod
    def rename_named(oldName, newName):
        oldSafe, oldPath = Playlist._named_playlist_path(oldName)
        newSafe, newPath = Playlist._named_playlist_path(newName)
        if not oldPath or not newPath:
            return False, 'Invalid playlist name', ''
        if not os.path.exists(oldPath):
            return False, 'Playlist "%s" was not found' % oldSafe, ''
        if oldPath == newPath:
            return True, 'Playlist name unchanged', newSafe
        if os.path.exists(newPath):
            return False, 'Playlist "%s" already exists' % newSafe, ''
        try:
            os.rename(oldPath, newPath)
        except OSError as error:
            return False, str(error), ''
        if Playlist._active_name() == oldSafe:
            Playlist._set_active_name(newSafe)
        return True, 'Renamed playlist "%s" to "%s"' % (oldSafe, newSafe), newSafe

    @staticmethod
    def delete_named(name):
        safe, path = Playlist._named_playlist_path(name)
        if not path:
            return False, 'Invalid playlist name'
        if not os.path.exists(path):
            return False, 'Playlist "%s" was not found' % safe
        try:
            os.remove(path)
        except OSError as error:
            return False, str(error)
        if Playlist._active_name() == safe:
            Playlist._set_active_name(_DEFAULT_PLAYLIST_NAME)
        return True, 'Deleted playlist "%s"' % safe

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
        imageFile = Playlist._safe_relative_store_path(imageFile)
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
