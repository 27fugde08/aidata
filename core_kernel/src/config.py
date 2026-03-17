# Proxy to new shared config
import shared.config as shared_config
import sys

# Inject all uppercase attributes (constants) from shared config into this module
for attr in dir(shared_config):
    if attr.isupper():
        setattr(sys.modules[__name__], attr, getattr(shared_config, attr))

# Also support config object for config.WORKSPACE_ROOT style
class ConfigProxy:
    def __getattr__(self, name):
        return getattr(shared_config, name)

config = ConfigProxy()
