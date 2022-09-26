compiler = meson.get_compiler('c')

libzint = compiler.find_library('libzint', dirs: '/app/lib')

shared_library('barcode-content-encoder',
	['barcode_content_encoder.c'],
	install: true,
	install_dir: plugindir,
	dependencies: [libzint])

conf = configuration_data()
conf.set('plugindir', plugindir)

configure_file(
	input: 'barcode_content_encoder.py.in',
	output: 'barcode_content_encoder.py',
	configuration: conf,
	install: true,
	install_dir: moduledir
)
