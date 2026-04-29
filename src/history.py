from Sand import STORE_PATH, TABLE_WIDTH, TABLE_LENGTH,\
    IMAGE_WIDTH, IMAGE_HEIGHT, CACHE_FILE,\
    HISTORY_COUNT, get_image_type
from os import listdir, remove
import os
import json
import re
from time import time
from datetime import datetime
from Chains import Chains
import pickle as pickle


_HISTORY_DIR = os.path.join(STORE_PATH, 'history')
_SAVED_DIR = os.path.join(STORE_PATH, 'saved')
_LEGACY_HISTORY_INDEX_FILE = os.path.join(STORE_PATH, '_history.json')
_HISTORY_INDEX_FILE = os.path.join(_HISTORY_DIR, '_history.json')


def _safe_history_token(value):
    token = re.sub(r'[^A-Za-z0-9_-]+', '_', str(value or '').strip())
    return token or 'drawing'


def _is_legacy_history_name(name):
    name = str(name or '').strip()
    return bool(re.fullmatch(r'_history\d+', name) or name.startswith('_history_'))


def _history_name(method, created, suffix=None):
    created = int(created or time())
    methodToken = _safe_history_token(method)
    stamp = datetime.fromtimestamp(created).strftime('%Y%m%d_%H%M%S')
    if suffix is None:
        return '%s_%s' % (methodToken, stamp)
    return '%s_%s_%02d' % (methodToken, stamp, int(suffix))


def _history_paths(name):
    return (
        os.path.join(_HISTORY_DIR, '%s.sand' % name),
        os.path.join(_HISTORY_DIR, '%s.png' % name),
    )


def _saved_paths(name):
    return (
        os.path.join(_SAVED_DIR, '%s.sand' % name),
        os.path.join(_SAVED_DIR, '%s.png' % name),
    )


def _public_store_path(*parts):
    clean = [str(part).strip('/\\') for part in parts if str(part)]
    return '/'.join([STORE_PATH.rstrip('/')] + clean)


def _ensure_store_dirs():
    os.makedirs(_HISTORY_DIR, exist_ok=True)
    os.makedirs(_SAVED_DIR, exist_ok=True)


def _move_if_exists(old_path, new_path):
    if not os.path.exists(old_path):
        return False
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    os.replace(old_path, new_path)
    return True


def _delete_history_files(name):
    sandPath, pngPath = _history_paths(name)
    for path in (sandPath, pngPath):
        try:
            remove(path)
        except OSError:
            pass


def _history_title(method, created):
    stamp = datetime.fromtimestamp(int(created)).strftime('%Y-%m-%d %H:%M:%S')
    return '%s %s' % (str(method or 'drawing'), stamp)


class History():
    @staticmethod
    def _migrate_storage_layout():
        _ensure_store_dirs()

        if os.path.exists(_LEGACY_HISTORY_INDEX_FILE) and not os.path.exists(_HISTORY_INDEX_FILE):
            _move_if_exists(_LEGACY_HISTORY_INDEX_FILE, _HISTORY_INDEX_FILE)

        payload = None
        try:
            with open(_HISTORY_INDEX_FILE, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            payload = None

        history_names = set()
        if isinstance(payload, list):
            for item in payload:
                if not isinstance(item, dict):
                    continue
                name = str(item.get('name', '')).strip()
                if name:
                    history_names.add(name)

        for name in history_names:
            root_sand = os.path.join(STORE_PATH, '%s.sand' % name)
            root_png = os.path.join(STORE_PATH, '%s.png' % name)
            history_sand, history_png = _history_paths(name)
            _move_if_exists(root_sand, history_sand)
            _move_if_exists(root_png, history_png)

        for filename in listdir(STORE_PATH):
            full_path = os.path.join(STORE_PATH, filename)
            if not os.path.isfile(full_path):
                continue
            if not (filename.endswith('.sand') or filename.endswith('.png')):
                continue
            stem, ext = os.path.splitext(filename)
            if stem.startswith('_'):
                continue
            if stem in history_names:
                target = _history_paths(stem)[0 if ext == '.sand' else 1]
            else:
                target = _saved_paths(stem)[0 if ext == '.sand' else 1]
            _move_if_exists(full_path, target)

    @staticmethod
    def _unique_history_name(method, created, exclude_name=None):
        _ensure_store_dirs()
        name = _history_name(method, created)
        sandPath, _ = _history_paths(name)
        suffix = 1
        while os.path.exists(sandPath) and name != exclude_name:
            name = _history_name(method, created, suffix)
            sandPath, _ = _history_paths(name)
            suffix += 1
        return name

    @staticmethod
    def _metadata_for_history_name(name, fallback_created=0):
        _ensure_store_dirs()
        created = int(fallback_created or 0)
        method = 'drawing'
        sandPath, _ = _history_paths(name)
        try:
            with open(sandPath, 'rb') as f:
                params = pickle.load(f)
            method = str(getattr(params, 'sandable', '') or 'drawing')
        except Exception:
            method = 'drawing'
        if not created:
            try:
                created = int(os.path.getmtime(sandPath))
            except OSError:
                created = int(time())
        return {
            'method': method,
            'created': created,
            'title': _history_title(method, created),
        }

    @staticmethod
    def _load_index_raw():
        History._migrate_storage_layout()
        try:
            with open(_HISTORY_INDEX_FILE, 'r', encoding='utf-8') as f:
                payload = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            payload = None

        items = []
        if isinstance(payload, list):
            for item in payload:
                if not isinstance(item, dict):
                    continue
                name = str(item.get('name', '')).strip()
                if not name:
                    continue
                items.append({
                    'name': name,
                    'method': str(item.get('method', '') or ''),
                    'created': int(item.get('created', 0) or 0),
                    'title': str(item.get('title', '') or ''),
                })
            return items

        bootstrapped = []
        for filename in listdir(STORE_PATH):
            if not filename.endswith('.sand'):
                continue
            rawName = filename[:-5]
            if not _is_legacy_history_name(rawName):
                continue
            name = rawName
            sandPath, _ = _history_paths(name)
            created = 0
            try:
                created = int(os.path.getmtime(sandPath))
            except OSError:
                pass
            method = ''
            title = _history_title('drawing', created if created else int(time()))
            bootstrapped.append({
                'name': name,
                'method': method,
                'created': created,
                'title': title,
            })
        bootstrapped.sort(key=lambda item: int(item.get('created', 0) or 0), reverse=True)
        return bootstrapped

    @staticmethod
    def migrate_legacy():
        items = History._load_index_raw()
        changed = False
        usedNames = {item.get('name') for item in items if item.get('name') and not _is_legacy_history_name(item.get('name'))}
        migrated = []

        for item in items:
            name = str(item.get('name', '')).strip()
            if not name:
                continue

            metadata = History._metadata_for_history_name(name, item.get('created', 0))
            item['method'] = metadata['method']
            item['created'] = metadata['created']
            item['title'] = metadata['title']

            if _is_legacy_history_name(name):
                newName = _history_name(metadata['method'], metadata['created'])
                suffix = 1
                while newName in usedNames or (os.path.exists(_history_paths(newName)[0]) and newName != name):
                    newName = _history_name(metadata['method'], metadata['created'], suffix)
                    suffix += 1

                oldSand, oldPng = _history_paths(name)
                newSand, newPng = _history_paths(newName)
                if newName != name:
                    try:
                        if os.path.exists(oldSand):
                            os.replace(oldSand, newSand)
                        if os.path.exists(oldPng):
                            os.replace(oldPng, newPng)
                    except OSError:
                        newName = name
                    else:
                        changed = True
                item['name'] = newName
                usedNames.add(newName)
            else:
                usedNames.add(name)

            migrated.append(item)

        History._prune_index(migrated)
        if changed or migrated != items:
            History._save_index(migrated)
        return migrated

    @staticmethod
    def _load_index():
        return History.migrate_legacy()

    @staticmethod
    def _save_index(items):
        _ensure_store_dirs()
        with open(_HISTORY_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, sort_keys=False)

    @staticmethod
    def _prune_index(items):
        while len(items) > HISTORY_COUNT:
            oldest = items.pop()
            _delete_history_files(oldest.get('name', ''))

    @staticmethod
    def history(params, sandable, chains):
        # Don't store history if the image is too simple
        if sum(map(len, chains)) < 8:
            return

        created = int(time())
        name = History._unique_history_name(sandable, created)

        History._write_entry(_history_paths(name), params, sandable, chains)

        items = History._load_index()
        items = [item for item in items if item.get('name') != name]
        items.insert(0, {
            'name': name,
            'method': str(sandable),
            'created': created,
            'title': _history_title(sandable, created),
        })
        History._prune_index(items)
        History._save_index(items)

    @staticmethod
    def save(params, sandable, chains, name):
        History._write_entry(_saved_paths(name), params, sandable, chains)

    @staticmethod
    def _write_entry(paths, params, sandable, chains):
        _ensure_store_dirs()
        sandPath, pngPath = paths
        params.sandable = sandable
        with open(sandPath, 'wb') as f:
            pickle.dump(params, f)
        boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
        Chains.saveImage(chains, boundingBox, pngPath, int(IMAGE_WIDTH/2), int(IMAGE_HEIGHT/2), get_image_type(), clipToTable=True)

    @staticmethod
    def delete(name):
        _delete_history_files(name)
        saved_sand, saved_png = _saved_paths(name)
        for path in (saved_sand, saved_png):
            try:
                remove(path)
            except OSError:
                pass
        items = History._load_index()
        updated = [item for item in items if item.get('name') != name]
        if len(updated) != len(items):
            History._save_index(updated)

    @staticmethod
    def load(name):
        _ensure_store_dirs()
        for sandPath in (_saved_paths(name)[0], _history_paths(name)[0], os.path.join(STORE_PATH, '%s.sand' % name)):
            try:
                with open(sandPath, 'rb') as f:
                    return pickle.load(f)
            except OSError:
                continue
        raise OSError('Unable to load drawing "%s"' % name)

    @staticmethod
    def image_path(name, history=False):
        return (_history_paths(name)[1] if history else _saved_paths(name)[1])

    @staticmethod
    def image_url(name, history=False):
        return _public_store_path('history' if history else 'saved', '%s.png' % name)

    @staticmethod
    def list():
        History._migrate_storage_layout()
        save = []
        history = [item.get('name') for item in History._load_index() if item.get('name')]
        filenames = listdir(_SAVED_DIR)
        filenames.sort()
        for name in filenames:
            if name.endswith('sand'):
                save.append(name[:-5])
        return (save, history)


class Memoize():
    """Memoize is used to cache drawings"""

    def __init__(self):
        try:
            with open(CACHE_FILE, 'rb') as f:
                self.sandable = pickle.load(f)
                self.params = pickle.load(f)
                self.chainLoc = f.tell()
        except FileNotFoundError:
            self.sandable = None
            self.params = None

    def match(self, sandable, params):
        return self.sandable == sandable and all(a.startswith('__') or getattr(self.params, a, None) == getattr(params, a, None) for a in dir(params))

    def chains(self):
        with open(CACHE_FILE, 'rb') as f:
            f.seek(self.chainLoc)
            return pickle.load(f)

    def save(self, sandable, params, chains):
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(sandable, f)
            pickle.dump(params, f)
            pickle.dump(chains, f)
