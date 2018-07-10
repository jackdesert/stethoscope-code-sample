# Adapted from PServeCommand.run in site-packages/pyramid/scripts/pserve.py

from pyramid.scripts.common import get_config_loader

app_name    = None
app_name    = 'pickle' # Raises error LookupError: No section 'pickle' (prefixed by 'app' or 'application' or 'composite' or 'composit' or 'pipeline' or 'filter-app') found in config /home/ubuntu/stethoscope/production.ini
app_name    = 'main'
config_vars = {}
config_uri  = 'production.ini'

loader = get_config_loader(config_uri)               # config_uri == 'production.ini'
# config_vars = parse_vars(self.args.config_vars)      # config_vars == {}
app = loader.get_wsgi_app(app_name, config_vars)

## Apparently not needed
# #server_name = self.args.server_name                  # server_name == None
# #server = loader.get_wsgi_server(server_name, config_vars)
