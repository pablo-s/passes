# import_dialog.py
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
import tempfile

import gi

gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('Adw', '1')

from gi.repository import GLib, Gdk, Gio, Gtk, Gst, GstVideo, Adw


class ImportDialog(Adw.AlertDialog):

    def __init__(self, callback):
        super().__init__()
        self._callback = callback

        self.set_heading(_('Import Pass'))
        self.set_body(_('Select import method'))

        self.add_response('cancel', _('Cancel'))
        self.add_response('file', _('From File'))
        self.add_response('screenshot', _('From Screenshot'))
        self.add_response('camera', _('From Camera'))

        self.set_response_enabled('cancel', True)

        self.connect('response', self._on_response)

    def _on_response(self, dialog, response):
        if response == 'file':
            self._callback(0)
        elif response == 'screenshot':
            self._callback(1)
        elif response == 'camera':
            self._callback(2)


class CameraDialog(Adw.Dialog):

    __gtype_name__ = 'CameraDialog'

    def __init__(self, on_captured):
        super().__init__()
        self._on_captured = on_captured
        self._pipeline = None
        self._appsink = None
        self._preview_sink = None

        self.set_title(_('Scan QR Code'))
        self.set_content_width(640)
        self.set_content_height(480)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        header = Adw.HeaderBar()
        main_box.append(header)

        self._preview_picture = Gtk.Picture()
        self._preview_picture.set_vexpand(True)
        self._preview_picture.set_hexpand(True)
        self._preview_picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        self._preview_picture.set_visible(True)
        main_box.append(self._preview_picture)

        self._status_label = Gtk.Label(label=_('Starting camera...'))
        self._status_label.set_halign(Gtk.Align.CENTER)
        self._status_label.set_visible(False)
        main_box.append(self._status_label)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(12)
        button_box.set_margin_bottom(12)

        self._cancel_button = Gtk.Button(label=_('Cancel'))
        self._cancel_button.connect('clicked', self._on_cancel_clicked)
        button_box.append(self._cancel_button)

        self._capture_button = Gtk.Button(label=_('Capture'))
        self._capture_button.add_css_class('suggested-action')
        self._capture_button.set_sensitive(False)
        self._capture_button.connect('clicked', self._on_capture_clicked)
        button_box.append(self._capture_button)

        main_box.append(button_box)

        self.set_child(main_box)
        self.connect('closed', self._on_closed)

        self._start_camera()

    def _start_camera(self):
        Gst.init(None)

        try:
            self._pipeline = Gst.Pipeline.new('camera-pipeline')
            bus = self._pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect('message::error', self._on_gst_error)
            bus.connect('message::eos', self._on_gst_eos)

            src = Gst.ElementFactory.make('autovideosrc', 'src')
            if not src:
                src = Gst.ElementFactory.make('pipewiresrc', 'src')

            if not src:
                self._show_error(_('No camera source available'))
                return

            convert = Gst.ElementFactory.make('videoconvert', 'convert')
            tee = Gst.ElementFactory.make('tee', 'tee')

            if not convert or not tee:
                self._show_error(_('Missing GStreamer elements'))
                return

            self._pipeline.add(src)
            self._pipeline.add(convert)
            self._pipeline.add(tee)

            src.link(convert)
            convert.link(tee)

            # Preview branch
            queue1 = Gst.ElementFactory.make('queue', 'queue1')
            scale = Gst.ElementFactory.make('videoscale', 'scale')
            self._preview_sink = Gst.ElementFactory.make('appsink', 'preview_sink')

            if not queue1 or not scale or not self._preview_sink:
                self._show_error(_('Missing GStreamer appsink element'))
                return

            self._preview_sink.set_property('emit-signals', True)
            self._preview_sink.set_property('sync', False)
            self._preview_sink.set_property('max-buffers', 1)
            self._preview_sink.set_property('caps',
                Gst.Caps.from_string('video/x-raw,format=RGB,width=640,height=480'))

            self._preview_sink.connect('new-sample', self._on_preview_sample)

            self._pipeline.add(queue1)
            self._pipeline.add(scale)
            self._pipeline.add(self._preview_sink)

            tee.link(queue1)
            queue1.link(scale)
            scale.link(self._preview_sink)

            # Capture branch
            queue2 = Gst.ElementFactory.make('queue', 'queue2')
            convert2 = Gst.ElementFactory.make('videoconvert', 'convert2')
            self._appsink = Gst.ElementFactory.make('appsink', 'appsink')

            if not queue2 or not convert2 or not self._appsink:
                self._show_error(_('Missing GStreamer appsink element'))
                return

            self._appsink.set_property('emit-signals', False)
            self._appsink.set_property('max-buffers', 1)
            self._appsink.set_property('drop', True)
            self._appsink.set_property('caps',
                Gst.Caps.from_string('video/x-raw,format=RGBA'))

            self._pipeline.add(queue2)
            self._pipeline.add(convert2)
            self._pipeline.add(self._appsink)

            tee.link(queue2)
            queue2.link(convert2)
            convert2.link(self._appsink)

            ret = self._pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                self._show_error(_('Failed to start camera'))
                return

            self._capture_button.set_sensitive(True)

        except Exception as e:
            self._show_error(str(e))

    def _on_preview_sample(self, sink):
        sample = sink.emit('pull-sample')
        if not sample:
            return Gst.FlowReturn.OK

        buf = sample.get_buffer()
        caps = sample.get_caps()
        if not caps:
            return Gst.FlowReturn.OK

        info = GstVideo.VideoInfo.new_from_caps(caps)

        success, map_info = buf.map(Gst.MapFlags.READ)
        if not success:
            return Gst.FlowReturn.OK

        try:
            stride = info.stride[0]
            end = info.size if info.size > 0 else len(map_info.data)
            data = bytes(map_info.data[:end])

            texture = Gdk.MemoryTexture.new(
                info.width, info.height,
                Gdk.MemoryFormat.R8G8B8,
                GLib.Bytes.new(data), stride)

            GLib.idle_add(self._set_preview_texture, texture)
        except Exception as e:
            GLib.idle_add(self._show_error, str(e))
        finally:
            buf.unmap(map_info)

        return Gst.FlowReturn.OK

    def _set_preview_texture(self, texture):
        self._preview_picture.set_paintable(texture)
        self._status_label.set_visible(False)
        return GLib.SOURCE_REMOVE

    def _show_error(self, message):
        self._status_label.set_text(message)
        self._status_label.set_visible(True)
        self._capture_button.set_sensitive(False)

    def _on_gst_error(self, bus, message):
        err, debug = message.parse_error()
        self._show_error(str(err))

    def _on_gst_eos(self, bus, message):
        pass

    def _on_capture_clicked(self, button):
        if not self._appsink:
            return

        sample = self._appsink.emit('try-pull-sample', Gst.SECOND)
        if not sample:
            self._show_error(_('Could not capture frame'))
            return

        temp_path = self._save_frame(sample)
        if temp_path:
            self._stop_pipeline()
            self.close()
            self._on_captured(temp_path)

    def _save_frame(self, sample):
        from PIL import Image

        buf = sample.get_buffer()
        caps = sample.get_caps()

        info = GstVideo.VideoInfo.new_from_caps(caps)
        stride = info.stride[0]

        success, map_info = buf.map(Gst.MapFlags.READ)
        if not success:
            return None

        try:
            end = info.size if info.size > 0 else len(map_info.data)
            img = Image.frombuffer('RGBA', (info.width, info.height),
                                   map_info.data[:end],
                                   'raw', 'RGBA', stride, 1)

            rgb_img = img.convert('RGB')

            fd, path = tempfile.mkstemp(suffix='.png')
            os.close(fd)
            rgb_img.save(path)

            return path

        except Exception as e:
            return None

        finally:
            buf.unmap(map_info)

    def _on_cancel_clicked(self, button):
        self._stop_pipeline()
        self.close()

    def _on_closed(self, dialog):
        self._stop_pipeline()

    def _stop_pipeline(self):
        if self._pipeline:
            self._pipeline.set_state(Gst.State.NULL)
            self._pipeline = None
            self._appsink = None
            self._preview_sink = None
