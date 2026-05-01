from playlist import Playlist
import mach


class PlaylistRunner:
    def _fallback_status(self, message):
        return {
            'state': 'error',
            'message': message,
            'current': None,
            'currentIndex': 0,
            'total': 0,
            'mode': 'all',
            'count': len(Playlist.list()),
        }

    def status(self):
        try:
            with mach.mach() as engine:
                status = engine.getPlaylistStatus() or {}
        except Exception as error:
            payload = self._fallback_status(str(error))
        else:
            payload = status.get('playlist') if isinstance(status, dict) else None
            if not isinstance(payload, dict):
                payload = self._fallback_status('Playlist status unavailable')

        payload = dict(payload)
        payload['name'] = Playlist.active_name()
        payload['count'] = len(Playlist.list())
        return payload

    def start_all(self):
        items = Playlist.list()
        if not items:
            return False, 'Playlist is empty'
        return self._start(items, 'all')

    def start_one(self, itemId):
        items = Playlist.list()
        item = next((entry for entry in items if str(entry.get('id', '')) == str(itemId)), None)
        if not item:
            return False, 'Playlist item was not found'
        return self._start([item], 'one')

    def _start(self, items, mode):
        try:
            with mach.mach() as engine:
                engine.run_playlist(items, mode)
                status = engine.status or {}
        except Exception as error:
            return False, str(error)

        result = status.get('result', {}) if isinstance(status, dict) else {}
        if not result.get('ok', False):
            return False, result.get('message', 'Playlist failed to start')
        return True, result.get('message', 'Playlist started')

    def stop(self):
        try:
            with mach.mach() as engine:
                engine.stop_playlist()
                status = engine.status or {}
        except Exception as error:
            return False, str(error)

        result = status.get('result', {}) if isinstance(status, dict) else {}
        return result.get('ok', False), result.get('message', 'Stopping playlist')

    def abort(self):
        try:
            with mach.mach() as engine:
                engine.abort_playlist()
                status = engine.status or {}
        except Exception as error:
            return False, str(error)

        result = status.get('result', {}) if isinstance(status, dict) else {}
        return result.get('ok', False), result.get('message', 'Aborting playlist')


runner = PlaylistRunner()
