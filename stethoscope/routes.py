def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('landing', '/')
    config.add_route('home', '/original_home')
    config.add_route('create_rssi_reading', '/rssi_readings', request_method='POST')
