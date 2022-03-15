import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class MixinPlugins:
    """
    Add support for plugins to a class.

    This lets you split and compose class behaviour in a way that is more
    flexible than multiple inheritance.

    The class should call `add_plugin` for all required plugins, and then call
    `verify_plugins` to ensure plugins are all configured correctly. See
    `puzzle1004.py` for an example of usage.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins = {}

    def add_plugin(self, plugin):
        assert plugin.plugin_name not in self.plugins, f'Already has "{plugin.plugin_name}"'
        self.plugins[plugin.plugin_name] = plugin
        plugin.set_parent(self)

    # TODO(sahil): Consider using Django signals?
    def dispatch_to_plugins(self, method, *args, **kwargs):
        for _ in self.iterate_plugins(method, *args, **kwargs):
            pass

    def get_plugin(self, plugin_name):
        self.assert_has_plugin(plugin_name)
        return self.plugins[plugin_name]

    def verify_plugins(self):
        self.dispatch_to_plugins('verify_plugin')

    def assert_has_plugin(self, plugin_name):
        assert plugin_name in self.plugins, f'Expected "{plugin_name}"'

    def iterate_plugins(self, method, *args, **kwargs):
        errors = []
        for plugin in self.plugins.values():
            if hasattr(plugin, method):
                assert callable(getattr(plugin, method))
                try:
                    yield getattr(plugin, method)(*args, **kwargs)
                except Exception as e:
                    logger.exception(f'Error while iterating plugins {method}')
                    errors.append(e)

        if len(errors) > 1:
            raise Exception(errors)
        elif len(errors):
            raise errors[0]

class Plugin(ABC):
    _parent = None

    @property
    @abstractmethod
    def plugin_name(self):
        """
        Accesses the name of the plugin. Should be unique per plugin instance,
        and not change.
        """
        pass

    def set_parent(self, parent):
        assert not self._parent
        self._parent = parent

    @property
    def parent(self):
        assert self._parent
        return self._parent

    def get_sibling_plugin(self, plugin_name):
        return self.parent.get_plugin(plugin_name)
