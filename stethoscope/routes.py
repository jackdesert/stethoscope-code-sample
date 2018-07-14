def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('landing', '/')
    config.add_route('docs__rssi_readings', '/api-docs/rssi_readings')
    config.add_route('rssi_readings', '/rssi_readings', request_method='GET')
    config.add_route('badge_show', '/badges/{id}', request_method='GET')
    config.add_route('badge_fetch', '/badges/{id}/fetch', request_method='GET')
    config.add_route('home', '/original_home')
    config.add_route('create_rssi_reading', '/rssi_readings', request_method='POST')
