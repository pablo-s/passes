pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'passes')
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'auxiliary/colored_box.blp',
    'barcode_dialog.blp',
    'gtk/help-overlay.blp',
    'pkpass_back_view.blp',
    'pkpass_field_row.blp',
    'pkpass_front_view_fallback.blp',
    'pkpass_row.blp',
    'pkpass_row_header.blp',
    'pkpass_view.blp',
    'window.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile',
    '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('passes',
  'passes.gresource.xml',
  dependencies: blueprints,
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

subdir('model')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'passes.in',
  output: 'passes',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

passes_sources = [
  '__init__.py',
  'auxiliary/colored_box.py',
  'model/barcode_content_encoder.py',
  'model/digital_pass.py',
  'model/digital_pass_factory.py',
  'model/digital_pass_list_store.py',
  'model/persistence.py',
  'model/pkpass.py',
  'barcode_dialog.py',
  'barcode_widget.py',
  'main.py',
  'pkpass_back_view.py',
  'pkpass_field_row.py',
  'pkpass_front_view.py',
  'pkpass_row.py',
  'pkpass_row_header.py',
  'pkpass_view.py',
  'window.py',
]

install_data(passes_sources, install_dir: moduledir)
