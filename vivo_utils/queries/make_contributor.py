from jinja2 import Environment

from vivo_utils.vdos.author import Author
from vivo_utils.vdos.contributor import Contributor
from vivo_utils.queries.get_vcard import run as get_vcard
from vivo_utils.queries.get_name_id import run as get_name_id
from vivo_utils.queries import make_person


def get_params(connection):
    author = Author(connection)
    contributor = Contributor(connection)
    params = {'Contributor': contributor, 'Author': author}
    return params


def fill_params(connection, **params):

    # Check if author exists
    query = "SELECT ?n_number " \
            "WHERE {?n_number <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> . "\
            + "?n_number <http://www.w3.org/2000/01/rdf-schema#label> \"" + params['Contributor'].name + "\"}"
    response = (connection.run_query(query)).json()

    # Author does not exist, create one
    if not response['results']['bindings']:
        params['Author'].name = params['Contributor'].name
        params['Author'].first = params['Contributor'].first
        params['Author'].middle = params['Contributor'].middle
        params['Author'].last = params['Contributor'].last

        make_person.run(connection, **params)

    if not params['Author'].vcard:
        params['Author'].vcard = get_vcard(connection, **params).split("/")[-1]
        if not params['Author'].name_id:
            params['Author'].name_id = get_name_id(connection, **params)

    print(params['Author'].vcard)
    print(params['Author'].name_id)

    params['namespace'] = connection.namespace

    params['Contributor'].n_number = connection.gen_n()
    # TODO Add URI for Investigator Role and Researcher Role
    contributor_role_uri = {'Co-Principal Investigator Role': 'http://vivoweb.org/ontology/core#CoPrincipalInvestigatorRole',
                            'Investigator Role': 'TBD',
                            'Researcher Role': 'TBD',
                            'Principal Investigator Role': 'http://vivoweb.org/ontology/core#PrincipalInvestigatorRole'}
    contributor_role_type = contributor_role_uri[params['Contributor'].type]
    params['Contributor'].type = contributor_role_type
    params['Contributor'].person_id = params['Author'].n_number

    return params


def get_triples():
    triples = """\
        {%- if Contributor.name %}
            <{{namespace}}{{Author.n_number}}> <http://www.w3.org/2000/01/rdf-schema#label> "{{Contributor.name}}"^^<http://www.w3.org/2001/XMLSchema#string> .
            <{{namespace}}{{Contributor.n_number}}> <http://purl.obolibrary.org/obo/ARG_2000028> <{{namespace}}{{Author.vcard}}> .
            <{{namespace}}{{Contributor.n_number}}> <http://purl.obolibrary.org/obo/RO_0000053> <{{namespace}}{{Author.name_id}}> .
        {%- endif -%}
    """

    api_trip = """\
    INSERT DATA {{
        GRAPH <http://vitro.mannlib.cornell.edu/default/vitro-kb-2>
        {{
            {TRIPS}
        }}
    }}
        """.format(TRIPS=triples)
    trips = Environment().from_string(api_trip)
    return trips


def run(connection, **params):
    params = fill_params(connection, **params)
    q = get_triples()
    # send data to vivo
    print('=' * 20 + "\nAdding contributor\n" + '=' * 20)
    response = connection.run_update(q.render(**params))
    print(response)
    return response
