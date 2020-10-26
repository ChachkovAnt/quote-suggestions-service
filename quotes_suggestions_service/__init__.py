from flask import Flask, jsonify, request, make_response

from quotes_suggestions_service.clients import EN_QUOTES_API_CLIENTS
from quotes_suggestions_service.clients.dtos import Quote
from quotes_suggestions_service.quotes_generator import QuotesGenerator


app = Flask(__name__, static_url_path="")
quotes_generator = QuotesGenerator()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(ValueError)
def not_found(error):
    return make_response(jsonify({'error': error.args}), 400)


@app.route('/suggestions', methods=['GET'])
def get_suggestions():
    keywords = request.args.get('keywords')
    authors = request.args.get('authors')
    limit = int(request.args.get('limit', 5))
    offset = int(request.args.get('offset', 0))

    keywords = tuple(keyword.strip() for keyword in keywords.split(',')) \
        if keywords is not None else ()
    authors = tuple(keyword.strip() for keyword in authors.split(',')) \
        if authors is not None else ()

    if len(authors) == 0 and len(keywords) == 0:
        raise ValueError('"authors" or "keywords" URI-parameters should be passed')

    response = quotes_generator.get_quotes(authors, keywords, limit, offset)

    return jsonify(response)
