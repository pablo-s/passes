compiler = meson.get_compiler('c')

libzint = compiler.find_library('libzint', dirs: '/app/lib')

shared_library('barcode-content-encoder',
	['barcode_content_encoder.c'],
	install: true,
	dependencies: [libzint])
