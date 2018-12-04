from pyramid.view import view_config
from ..models.rssi_reading import RssiReading
from ..models.location_predictor import LocationPredictor
from ..models.location_history_presenter import LocationHistoryPresenter
import json
import ipdb

@view_config(route_name='location_history',
             renderer='json')
def location_history_view(request):
    badge_id = request.matchdict.get('badge_id')

    whitelist = ['algorithm', 'grain', 'date', 'return_value']

    if request.body:
        priors = request.json_body.get('priors')
        params = request.json_body
    else:
        priors = None
        params = request.params

    kwargs = {key: value for key, value in params.items() if key in whitelist}

    if kwargs.get('grain'):
        kwargs['grain'] = int(kwargs['grain'])

    # rename "date" key to "date_string"
    if 'date' in kwargs:
        date_string = kwargs['date']
        kwargs['date_string'] = date_string
        del kwargs['date']


    reading = RssiReading()
    predictor = LocationPredictor(reading, priors=priors)
    presenter = LocationHistoryPresenter(request.dbsession,
                                         predictor,
                                         badge_id,
                                         **kwargs)


    return presenter.present()


