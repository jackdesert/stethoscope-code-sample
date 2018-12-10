from pyramid.view import view_config
from ..models.rssi_reading import RssiReading
from ..models.location_predictor import LocationPredictor
from ..models.location_history_presenter import LocationHistoryPresenter
from ..models.location_history_presenter import LocationHistoryFutureOffsetError

import json
import ipdb

@view_config(route_name='location_history',
             renderer='json')
def location_history_view(request):
    badge_id = request.matchdict.get('badge_id')

    if request.body:
        priors = request.json_body.get('priors')
        params = request.json_body
    else:
        priors = None
        params = request.params

    whitelist = ['algorithm', 'grain', 'offset', 'date', 'return_value']
    kwargs = {key: value for key, value in params.items() if key in whitelist}

    if kwargs.get('grain'):
        kwargs['grain'] = int(kwargs['grain'])

    if kwargs.get('offset'):
        kwargs['offset'] = int(kwargs['offset'])

    # rename "date" key to "date_string"
    if 'date' in kwargs:
        date_string = kwargs['date']
        kwargs['date_string'] = date_string
        del kwargs['date']


    reading = RssiReading()
    predictor = LocationPredictor(reading, priors=priors)

    try:
        presenter = LocationHistoryPresenter(request.dbsession,
                                             predictor,
                                             badge_id,
                                             **kwargs)
    except LocationHistoryFutureOffsetError as ee:
        request.response.status_code = 400
        return dict(error=ee.__repr__())



    return presenter.present()


