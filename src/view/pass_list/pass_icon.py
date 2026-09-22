# pass_icon.py
#
# Copyright 2022-2023 Pablo Sánchez Rodríguez
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

from gi.repository import Gdk, Graphene, Gsk, Gtk

from .digital_pass import Color


@Gtk.Template(resource_path='/me/sanchezrodriguez/passes/pass_icon.ui')
class PassIcon(Gtk.Box):

    __gtype_name__ = 'PassIcon'

    ICON_SIZE = 45
    BORDER_RADIUS = 6
    BORDER_WIDTH = 5

    def __init__(self):
        super().__init__()
        self.__background_color = None
        self.__image = None

        self.props.height_request = PassIcon.ICON_SIZE + PassIcon.BORDER_WIDTH
        self.props.width_request = PassIcon.ICON_SIZE + PassIcon.BORDER_WIDTH

        self.__badge_text = None

    def __draw_background(self, snapshot):
        if not self.__background_color:
            return

        rectangle = Graphene.Rect()
        rectangle.init(0, 0, PassIcon.ICON_SIZE + PassIcon.BORDER_WIDTH,
                             PassIcon.ICON_SIZE + PassIcon.BORDER_WIDTH)

        rounded_rectangle = Gsk.RoundedRect()
        rounded_rectangle.init_from_rect(rectangle, PassIcon.BORDER_RADIUS)

        snapshot.push_rounded_clip(rounded_rectangle)
        snapshot.append_color(self.__background_color.as_gdk_rgba(), rectangle)
        snapshot.pop()

    def __draw_icon(self, snapshot):
        if not self.__image:
            return

        rectangle = Graphene.Rect()
        rectangle.init(PassIcon.BORDER_WIDTH,
                       PassIcon.BORDER_WIDTH,
                       PassIcon.ICON_SIZE - PassIcon.BORDER_WIDTH,
                       PassIcon.ICON_SIZE - PassIcon.BORDER_WIDTH)

        rounded_rectangle = Gsk.RoundedRect()
        rounded_rectangle\
            .init_from_rect(rectangle,
                            PassIcon.BORDER_RADIUS - PassIcon.BORDER_WIDTH)

        image = self.__image
        if hasattr(image, 'as_texture'):
            texture = image.as_texture()
        else:
            texture = image
        texture_height = texture.get_height()
        texture_width = texture.get_width()
        scale = (PassIcon.ICON_SIZE) / max(texture_width, texture_height)

        padding_top = (PassIcon.ICON_SIZE - (texture_height * scale)) / 2
        padding_left = (PassIcon.ICON_SIZE - (texture_width * scale)) / 2

        rect_texture = Graphene.Rect()
        rect_texture.init(padding_left + PassIcon.BORDER_WIDTH,
                          padding_top + PassIcon.BORDER_WIDTH,
                          texture_width * scale - PassIcon.BORDER_WIDTH,
                          texture_height * scale - PassIcon.BORDER_WIDTH)

        snapshot.push_rounded_clip(rounded_rectangle)
        snapshot.append_texture(texture, rect_texture)
        snapshot.pop()

    def __guess_background_color(self):
        if not self.__image:
            return None

        try:
            pixel_buffer = self.__image.as_pixbuf()
        except Exception:
            return None

        if not pixel_buffer:
            return None

        data = pixel_buffer.read_pixel_bytes().get_data()
        if len(data) < 4:
            return None

        # This method assumes that the background color of an image is the color
        # of the first pixel of the image if it is not transparent.

        background_color = None
        if not pixel_buffer.get_has_alpha() or data[3] > 0:
            background_color = data[0:3]

        return Color(*background_color) if background_color else None

    def __draw_badge(self, snapshot):
        if self.__image or not self.__badge_text:
            return

        if PassIcon.ICON_SIZE <= 0:
            return

        rectangle = Graphene.Rect()
        rectangle.init(PassIcon.BORDER_WIDTH,
                       PassIcon.BORDER_WIDTH,
                       PassIcon.ICON_SIZE - PassIcon.BORDER_WIDTH,
                       PassIcon.ICON_SIZE - PassIcon.BORDER_WIDTH)

        cr = snapshot.append_cairo(rectangle)

        from gi.repository import Pango, PangoCairo

        layout = PangoCairo.create_layout(cr)
        layout.set_text(self.__badge_text, -1)
        layout.set_font_description(Pango.FontDescription
                                    .from_string('Sans 10'))

        ink, logical = layout.get_pixel_extents()
        text_w = logical.width
        text_h = logical.height

        # Zentrierte, abgerundete Plakette mit dem Text
        bw, bh = text_w + 16, text_h + 8
        bx = (PassIcon.ICON_SIZE - bw) / 2
        by = (PassIcon.ICON_SIZE - bh) / 2

        cr.new_path()
        radius = 6
        cr.move_to(bx + radius, by)
        cr.arc(bx + bw - radius, by + radius, radius, -1.5708, 0)
        cr.arc(bx + bw - radius, by + bh - radius, radius, 0, 1.5708)
        cr.arc(bx + radius, by + bh - radius, radius, 1.5708, 3.14159)
        cr.arc(bx + radius, by + radius, radius, 3.14159, 4.71239)
        cr.close_path()
        cr.set_source_rgba(0.08, 0.08, 0.08, 0.9)
        cr.fill()

        cr.move_to(bx + 8, by + 4)
        cr.set_source_rgba(1, 1, 1, 1)
        PangoCairo.show_layout(cr, layout)
        cr.stroke()

    def set_badge_text(self, text):
        self.__badge_text = text
        self.queue_draw()

    def set_image(self, image):
        self.__image = image
        self.queue_draw()

    def set_background_color(self, color):
        self.__background_color = color
        self.queue_draw()

    def do_snapshot(self, snapshot):
        self.__draw_background(snapshot)
        self.__draw_icon(snapshot)
        self.__draw_badge(snapshot)
