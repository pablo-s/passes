# barcode_content_encoder.py
#
# Copyright 2022 Pablo Sánchez Rodríguez
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

import ctypes
import math


class BarcodeContentEncoder():

    native_implementation = ctypes.CDLL('libbarcode-content-encoder.so')

    # encode_aztec_code
    native_implementation.encode_aztec_code.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
    native_implementation.encode_aztec_code.restype = ctypes.c_char_p

    # encode_qr_code
    native_implementation.encode_qr_code.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
    native_implementation.encode_qr_code.restype = ctypes.c_char_p

    @classmethod
    def encode_aztec_code(this_class, text, encoding):
        encoded_text = text.encode(encoding)
        data = (ctypes.c_ubyte * len(encoded_text))\
            .from_buffer_copy(encoded_text)

        module_list = this_class.native_implementation\
            .encode_aztec_code(data)\
            .decode()

        this_class.native_implementation.free_last_result()

        code_width = code_height = int(math.sqrt(len(module_list)))

        return module_list, code_width, code_height

    @classmethod
    def encode_qr_code(this_class, text, encoding):
        encoded_text = text.encode(encoding)
        data = (ctypes.c_ubyte * len(encoded_text))\
            .from_buffer_copy(encoded_text)

        module_list = this_class.native_implementation\
            .encode_qr_code(data)\
            .decode()

        this_class.native_implementation.free_last_result()

        code_width = code_height = int(math.sqrt(len(module_list)))

        return module_list, code_width, code_height
