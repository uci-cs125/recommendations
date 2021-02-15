from flask import jsonify, Response, request
from .encoder import JSONEncoder
import json

def craftResp(data, req, code):
    prettyPrint = req.args.get("pretty")
    
    if prettyPrint == "true":
        return Response(json.dumps({'results': data}, cls=JSONEncoder, indent=4), code, mimetype='application/json')
    else:
        return Response(json.dumps({'results': data}, cls=JSONEncoder), code, mimetype='application/json')
