# airline_logo.py
#
# Copyright 2026 Jan-Michael Brummer <jan.brummer@tabos.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import threading
import urllib.error
import urllib.request

from gi.repository import Gdk, GLib


class AirlineLogoFetcher:
    LOGO_URL = 'https://cdn.jsdelivr.net/gh/spydogenesis/airlines-logo@latest/' \
               'airlines-logo/200x200_v2/{}.png'

    __users_cache_directory = GLib.get_user_cache_dir()
    __logo_cache_directory = None
    __memory_cache = {}
    __pending_fetches = {}

    @classmethod
    def logo_cache_directory(cls):
        if not cls.__logo_cache_directory:
            cls.__logo_cache_directory = os.path.join(
                cls.__users_cache_directory, 'passes', 'airlines-logo')

        return cls.__logo_cache_directory

    @classmethod
    def preload(cls, iata_code, on_success, on_failure):
        code = cls.__normalized_code(iata_code)
        if not code:
            on_failure()
            return

        cached_texture = cls.__memory_cache.get(code)
        if cached_texture:
            on_success(cached_texture)
            return

        cache_path = cls.__logo_cache_path(code)
        try:
            with open(cache_path, 'rb') as f:
                bytes_data = f.read()

            texture = Gdk.Texture.new_from_bytes(GLib.Bytes(bytes_data))
            cls.__memory_cache[code] = texture
            on_success(texture)
        except OSError:
            on_failure()

    @classmethod
    def fetch(cls, iata_code, on_success, on_failure):
        code = cls.__normalized_code(iata_code)
        if not code:
            GLib.idle_add(on_failure)
            return

        cached_texture = cls.__memory_cache.get(code)
        if cached_texture:
            GLib.idle_add(on_success, cached_texture)
            return

        if code in cls.__pending_fetches:
            cls.__pending_fetches[code].append((on_success, on_failure))
            return

        cls.__pending_fetches[code] = [(on_success, on_failure)]

        thread = threading.Thread(target=cls.__fetch_worker,
                                  args=(code, ), daemon=True)
        thread.start()

    @classmethod
    def __fetch_worker(cls, code):
        texture, error = None, None

        try:
            bytes_data = cls.__load_from_disk_or_download(code)
            if not bytes_data:
                raise urllib.error.URLError('No airline logo for {code}')

            texture = Gdk.Texture.new_from_bytes(GLib.Bytes(bytes_data))
            cls.__memory_cache[code] = texture

        except Exception as exception:
            error = exception

        GLib.idle_add(cls.__deliver, code, texture, error)

    @classmethod
    def __deliver(cls, code, texture, error):
        callbacks = cls.__pending_fetches.pop(code, [])
        for on_success, on_failure in callbacks:
            if texture:
                on_success(texture)
            else:
                on_failure()

        return GLib.SOURCE_REMOVE

    @classmethod
    def __load_from_disk_or_download(cls, code):
        cache_path = cls.__logo_cache_path(code)

        try:
            with open(cache_path, 'rb') as f:
                return f.read()
        except OSError:
            pass

        url = cls.LOGO_URL.format(code)
        request = urllib.request.Request(url,
                                         headers={'User-Agent':
                                                  'passes/1.0'})
        with urllib.request.urlopen(request, timeout=10) as response:
            data = response.read()

        try:
            os.makedirs(cls.logo_cache_directory(), exist_ok=True)
            with open(cache_path, 'wb') as f:
                f.write(data)
        except OSError:
            pass

        return data

    @classmethod
    def __logo_cache_path(cls, code):
        return os.path.join(cls.logo_cache_directory(), code + '.png')

    @classmethod
    def __normalized_code(cls, iata_code):
        if not iata_code:
            return None

        code = iata_code.strip().upper()

        if not re.fullmatch(r'[A-Z0-9]{2,3}', code):
            return None

        return code
