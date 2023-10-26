#import pydantic

from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from models import Session, AdModel
from schema import validate, UpdateAdModel, CreateAdModel


app = Flask('app')


class HTTPError(Exception):
    def __init__(self, status_code: int, error_message: str | list | dict ):
        self.status_code = status_code
        self.message = error_message


@app.errorhandler(HTTPError)
def error_handler(er: HTTPError):
    http_response = jsonify({"status": "error", "description": er.error_message})
    http_response.status_code = er.status_code
    return http_response


def get_adv(advertisement_id: int, session: Session) -> AdModel:
 
    adv = session.get(AdModel, advertisement_id)
    if adv is None:
        raise HTTPError(404, 'Advertisement is not found.')
    return adv


class AdView(MethodView):
    def get(self, advertisement_id: int):
        with Session() as session:
            adv = get_adv(advertisement_id=advertisement_id, session=session)
            return jsonify({
                'id': adv.id,
                'title': adv.title,
                #'creation_time': adv.creation_time,
                #'description': adv.description,
                #'owner': adv.owner,
            })
     
     
    def post(self):

        json_data = validate(json_data=request.json, model_class=CreateAdModel)  

        with Session() as session:
            new_adv = AdModel(**json_data)  
            session.add(new_adv)  
            try:
                session.commit()  
            except IntegrityError as error:
                raise HTTPError(409, 'file already exists.')  
            return jsonify({
                'id': new_adv.id,
                'title': new_adv.title,
                'creation_time': new_adv.creation_time,
                'description': new_adv.description,
                'owner': new_adv.owner,
            })
   

    def patch(self, advertisement_id: int):
     
        json_data = validate(json_data=request.json, model_class=UpdateAdModel)
        with Session() as session:
            adv = get_adv(advertisement_id=advertisement_id, session=session)
            for field, value in json_data.items():
                setattr(adv, field, value)
                session.commit()
            return jsonify({
                'title': adv.title,
                'creation_time': adv.creation_time,
                'description': adv.description,
            })
        

    def delete(self, advertisment_id: int):
            
            with Session() as session:
                adv = get_adv(advertisment_id=advertisment_id, session=session)
                session.delete(adv)
                session.commit()
                return jsonify({
                    'status': 'success'
                })
       


app.add_url_rule("/advertisements/<int:id_ad>/", view_func=AdView.as_view('advertisements_delete'),
                 methods=['DELETE', 'GET'])
app.add_url_rule("/advertisements", view_func=AdView.as_view('advertisements_create'), methods=['POST'])