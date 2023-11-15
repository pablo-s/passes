pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
plugindir = join_paths(get_option('prefix'), get_option('libdir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'passes')
gnome = import('gnome')

blueprint_files = files(
    'view/barcode_dialog.blp',
    'view/help_overlay.blp',
    'view/pass_list/pass_icon.blp',
    'view/pass_list/pass_list.blp',
    'view/pass_list/pass_row.blp',
    'view/pass_list/pass_row_header.blp',
    'view/pass_viewer/additional_information_pane.blp',
    'view/pass_viewer/pass_field_row.blp',
    'view/window.blp')

blueprint_compiler = find_program('blueprint-compiler')
ui_files = []

foreach blueprint_file : blueprint_files
  path_as_string = '@0@'.format(blueprint_file)
  filename = path_as_string.split('/')[-1]

  ui_file = custom_target(path_as_string.underscorify(),
    input: blueprint_file,
    output: filename.replace('.blp', '.ui'),
    command: [blueprint_compiler, 'compile', '--output', '@OUTPUT@', '@INPUT@'])

  ui_files += ui_file
endforeach

gnome.compile_resources('passes',
  'passes.gresource.xml',
  dependencies: ui_files,
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

subdir('model')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('APPID', 'me.sanchezrodriguez.passes')
if get_option('profile') == 'development'
  vcs_tag = run_command('git', 'rev-parse', '--short', 'HEAD').stdout().strip()
  conf.set('DEVEL', 'Development')
  conf.set('VERSION', meson.project_version() + '.dev-' + vcs_tag)
else
  conf.set('DEVEL', 'Default')
  conf.set('VERSION', meson.project_version())
endif

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
  'view/barcode_dialog.py',
  'view/barcode_widget.py',
  'view/pass_list/pass_icon.py',
  'view/pass_list/pass_list.py',
  'view/pass_list/pass_row_header.py',
  'view/pass_list/pass_row.py',
  'view/pass_viewer/pass_widget.py',
  'view/pass_viewer/additional_information_pane.py',
  'view/pass_viewer/pass_field_row.py',
  'view/window.py',
  'main.py',
  'model/digital_pass_factory.py',
  'model/digital_pass_list_store.py',
  'model/digital_pass_updater.py',
  'model/digital_pass.py',
  'model/espass.py',
  'model/persistence.py',
  'model/pkpass.py',
  'model/settings.py',
]

passes_sources += configure_file(
  input: 'view/const.py.in',
  output: 'const.py',
  configuration: conf,
)

install_data(passes_sources, install_dir: moduledir)
