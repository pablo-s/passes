project('passes', 'c',
          version: '0.9',
    meson_version: '>= 0.59.0',
  default_options: [ 'warning_level=2',
                   ],
)

i18n = import('i18n')

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  update_desktop_database: true,
  gtk_update_icon_cache: true,
)
