# -*- coding: utf-8 -*-

from os import path
from flask import _request_ctx_stack, url_for
from flask.ext.assets import Environment, Bundle, get_static_folder
from flask.ext.themes import static_file_url


class ThemeAwareEnvironment(Environment):
    def _normalize_source_path(self, filename):
        if path.isabs(filename):
            return filename
        if self.config.get('directory') is not None:
            return super(Environment, self).abspath(filename)
        try:
            if hasattr(self._app, 'blueprints'):
                blueprint, name = filename.split('/', 1)
                if blueprint == '_themes':
                    theme, name = name.split('/', 1)
                    directory = self._app.theme_manager.themes[theme].static_path
                    filename = name
                else:
                    directory = get_static_folder(self._app.blueprints[blueprint])
                    filename = name
            else:
                # Module support for Flask < 0.7
                module, name = filename.split('/', 1)
                directory = get_static_folder(self._app.modules[module])
                filename = name
        except (ValueError, KeyError):
            directory = get_static_folder(self._app)
        return path.abspath(path.join(directory, filename))

    def absurl(self, fragment):
        if self.config.get('url') is not None:
            # If a manual base url is configured, skip any
            # blueprint-based auto-generation.
            return super(Environment, self).absurl(fragment)
        else:
            try:
                filename, query = fragment.split('?', 1)
                query = '?' + query
            except (ValueError):
                filename = fragment
                query = ''

            if hasattr(self._app, 'blueprints'):
                try:
                    blueprint, name = filename.split('/', 1)
                    self._app.blueprints[blueprint]  # generates keyerror if no module
                    endpoint = '%s.static' % blueprint
                    filename = name
                except (ValueError, KeyError):
                    endpoint = 'static'
            else:
                # Module support for Flask < 0.7
                try:
                    module, name = filename.split('/', 1)
                    self._app.modules[module]  # generates keyerror if no module
                    endpoint = '%s.static' % module
                    filename = name
                except (ValueError, KeyError):
                    endpoint = '.static'

            ctx = None
            if not _request_ctx_stack.top:
                ctx = self._app.test_request_context()
                ctx.push()
            try:
                if endpoint.startswith('_themes.'):
                    theme, filename = filename.split('/', 1)
                    return static_file_url(theme, filename) + query
                else:
                    return url_for(endpoint, filename=filename) + query
            finally:
                if ctx:
                    ctx.pop()


def load_theme_assets(env, theme):
    css_list = theme.options.get('assets_css', [])
    if isinstance(css_list, basestring):
        css_list = [css_list]
    css = Bundle(*[Bundle('_themes/%s/%s' % (theme.identifier, item),
            filters='cssmin', output='_themes/%s/%s.packed.css' % (theme.identifier, item)) for item in css_list],
        filters='cssrewrite', output='_themes/%s/eventframe.packed.css' % (theme.identifier))
    env.register('css_%s' % theme.identifier, css)

    js_list = theme.options.get('assets_js', [])
    if isinstance(js_list, basestring):
        js_list = [js_list]
    js = Bundle(*[Bundle('_themes/%s/%s' % (theme.identifier, item),
        filters='jsmin', output='_themes/%s/%s.packed.js' % (theme.identifier, item)) for item in js_list])
    env.register('js_%s' % theme.identifier, js)
