import json
import sqlite3
import flask

app = flask.Flask(__name__)


def get_value_from_db(sql):
    with sqlite3.connect('netflix.db') as connection:
        connection.row_factory = sqlite3.Row

        result = connection.execute(sql).fetchall()
        return result


def get_value_by_title(title):
    sql = f"""select title, country, release_year, listed_in as genre, description from netflix
    where title = '{title}'
    order by release_year desc
    limit 1
    """

    result = get_value_from_db(sql)

    for item in result:
        return dict(item)


@app.get('/movie/<title>')
def view_title(title):
    result = get_value_by_title(title)

    return app.response_class(
        response=json.dumps(result,
                            ensure_ascii=False,
                            indent=4),
        status=200,
        mimetype='application/json'
    )


@app.get('/movie/<int:year1>/to/<int:year2>')
def get_by_year(year1, year2):
    sql = f"""select title, release_year from netflix
    where release_year between {year1} and {year2}
    limit 100
    """
    result = get_value_from_db(sql)
    search = []
    for item in result:
        search.append(dict(item))

    return app.response_class(
        response=json.dumps(search,
                            ensure_ascii=False,
                            indent=4),
        status=200,
        mimetype='application/json'
    )


@app.get('/rating/<rating>')
def get_by_rating(rating):
    rating_dict = {
        'children': ('G'),
        'family': ('G, PG, PG-13'),
        'adult': ('R, NC-17')
    }

    sql = f"""select title, rating, description from netflix
    where rating == '{rating_dict.get(rating)}'
    """

    result = get_value_from_db(sql)
    rating_dict = []
    for item in result:
        rating_dict.append(dict(item))

    return app.response_class(
        response=json.dumps(rating_dict,
                            ensure_ascii=False,
                            indent=4),
        status=200,
        mimetype='application/json'
    )

@app.get('/genre/<genre>')
def get_by_genre(genre):
    sql = f"""
    select title, description from netflix
    where listed_in like '%{genre}%'"""

    result = get_value_from_db(sql)
    genre_dict = []
    for item in result:
        genre_dict.append(dict(item))

    return app.response_class(
        response=json.dumps(genre_dict,
                            ensure_ascii=False,
                            indent=4),
        status=200,
        mimetype='application/json'
    )


def get_partner(name1 = 'Rose McIver', name2 = 'Ben Lamb'):
    sql = f"""
    select * from netflix
    where "cast" like '%{name1}%' and "cast" like '%{name2}%'
    """

    result = get_value_from_db(sql)

    tmp = []

    partner_dict = {}

    for item in result:
        partner = set(dict(item).get("cast").split(', ')) - set([name1, name2])

        for name in partner:
            partner_dict[name.strip()] = partner_dict.get(name.strip(), 0) + 1

    for key, value in partner_dict.items():
        if value > 2:
            tmp.append(key)

    return tmp

def get_movie(typ, year, genre):
    sql = f"""
    select * from netflix
    where type = '{typ}' and
    release_year = '{year}' and
    listed_in like '%{genre}%'
    """

    result = get_value_from_db(sql)
    rating_dict = []
    for item in result:
        rating_dict.append(dict(item))

    return json.dumps(rating_dict,
                            ensure_ascii=False,
                            indent=4),

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)

