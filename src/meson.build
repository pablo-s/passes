pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
plugindir = join_paths(get_option('prefix'), get_option('libdir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'passes')
gnome = import('gnome')

compile_blueprint_files = custom_target('compile_blueprint_files',
  input: files(
    'view/auxiliary/colored_box.blp',
    'view/barcode_dialog.blp',
    'view/help_overlay.blp',
    'view/pass_list/pass_icon.blp',
    'view/pass_list/pass_list.blp',
    'view/pass_list/pass_row.blp',
    'view/pass_list/pass_row_header.blp',
    'view/pass_viewer/pkpass_back_view.blp',
    'view/pass_viewer/pkpass_field_row.blp',
    'view/window.blp'
  ),
  output: 'generated_ui_files',
  command: [find_program('blueprint-compiler'), 'batch-compile',
    '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

collect_ui_files = custom_target('collect_ui_files',
  depends: compile_blueprint_files,
  output: '.',
  command: ['find', '@OUTDIR@/generated_ui_files',
    '-type', 'f', '-name', '*.ui',
    '-exec', 'cp', '-t', '@OUTPUT@', '{}', '+'])

gnome.compile_resources('passes',
  'passes.gresource.xml',
  dependencies: collect_ui_files,
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
  'view/auxiliary/colored_box.py',
  'view/barcode_dialog.py',
  'view/barcode_widget.py',
  'view/pass_list/pass_icon.py',
  'view/pass_list/pass_list.py',
  'view/pass_list/pass_row_header.py',
  'view/pass_list/pass_row.py',
  'view/pass_viewer/pass_widget.py',
  'view/pass_viewer/pkpass_back_view.py',
  'view/pass_viewer/pkpass_field_row.py',
  'view/window.py',
  'main.py',
  'model/digital_pass_factory.py',
  'model/digital_pass_list_store.py',
  'model/digital_pass_updater.py',
  'model/digital_pass.py',
  'model/espass.py',
  'model/persistence.py',
  'model/pkpass.py',
]

install_data(passes_sources, install_dir: moduledir)
