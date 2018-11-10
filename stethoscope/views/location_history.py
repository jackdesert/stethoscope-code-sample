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

    algorithm = request.matchdict.get('algorithm')
    date_string = request.matchdict.get('date')
    grain = request.matchdict.get('grain')
    priors = None
    return_value = request.matchdict.get('return_value')

    if request.body:
        params = json.loads(request.body)

        algorithm = params.get('algorithm')
        date_string = params.get('date')
        grain = params.get('grain')
        priors = params.get('priors')
        return_value = params.get('return_value')

    kwargs = {}
    if algorithm:
        kwargs['algorithm'] = algorithm
    if grain:
        kwargs['grain'] = grain
    if date_string:
        kwargs['date_string'] = date_string
    if return_value:
        kwargs['return_value'] = return_value

    reading = RssiReading()
    predictor = LocationPredictor(reading, priors=priors)
    presenter = LocationHistoryPresenter(request.dbsession,
                                         predictor,
                                         badge_id,
                                         **kwargs)


    return presenter.present()


