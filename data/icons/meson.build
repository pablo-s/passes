application_id = 'me.sanchezrodriguez.passes'

scalable_dir = join_paths('hicolor', 'scalable', 'apps')
install_data(
  join_paths(scalable_dir, ('@0@.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', scalable_dir)
)

symbolic_dir = join_paths('hicolor', 'symbolic', 'apps')
install_data(
  join_paths(symbolic_dir, ('@0@-symbolic.svg').format(application_id)),
  install_dir: join_paths(get_option('datadir'), 'icons', symbolic_dir)
)

action_dir = join_paths('hicolor', 'scalable', 'actions')
action_icons = [join_paths(action_dir, 'qr-code-symbolic.svg')]
install_data(
  action_icons,
  install_dir: join_paths(get_option('datadir'), 'icons', action_dir)
)
