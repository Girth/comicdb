#!/usr/bin/python

# Flask
import config

# SQL
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# stdlib
import logging
import os, sys
import urllib
from xml.etree import ElementTree

### START PARSING ###
def parse_characters(url):
    e = make_request(url)

    for each in e.find("results"):
        # smash the data into fields
        id = each.find("id").text
        name = each.find("name").text
        origin = each.find("origin").text
        desc = each.find("description").text
        pub = each.find("publisher").text
        first_app = each.find("first_appeared_in_issue").text
        gender = each.find("gender").text

        # parameterized statement
        s = text("""
                REPLACE INTO DETAIL_CHARACTER
                VALUES ( :id, :name, :gender, :origin, :desc );
                """)

        # run the query
        try:
            results = conn.execute( s, id=id, name=name, gender=gender, origin=str(origin), desc=str(desc) )
        except:
            logging.error( "EXCEPTION at char#" + id + " : " + str(sys.exc_info()[0]) )
            continue

def parse_issues(url):
    try:
        e = make_request(url)
    except:
        logging.error( "REQUEST ERROR: " + str(sys.exc_info()[1]) )
        return

    for each in e.find("results"):
        # smash the data into fields
        id = each.find("id").text
        issue = each.find("issue_number").text
        name = each.find("name").text
        desc = each.find("description").text
        pub_mon = each.find("publish_month").text
        pub_day = each.find("publish_day").text
        pub_yr = each.find("publish_year").text

        # snap, not all issues have names!
        if name == None:
            logging.debug("issue#" + id + " has no name!")
            name = each.find("volume").find("name").text + " - " + str(issue)

        # parameterized statement
        s = text("""
                REPLACE INTO DETAIL_ISSUE
                VALUES (:id, :issue_number, :name, :pub_mon, :pub_day, :pub_yr, NULL);
                """)

        # run the query
        try:
            results = conn.execute( s, id=id, issue_number=issue, name=name, pub_mon=pub_mon, pub_day=pub_day, pub_yr=pub_yr )
        except:
            logging.error( "EXCEPTION at issue#" + id + " : " + str(sys.exc_info()[1]) )
            continue

def parse_locations(url):
    e = make_request(url)

    for each in e.find("results"):
        id = each.find("id").text
        name = each.find("name").text
        desc = each.find("description").text

        # parameterized statement
        s = text("""
                REPLACE INTO DETAIL_LOCATION
                VALUES ( :id, :name, :desc );
                """)

        # run the query
        try:
            results = conn.execute( s, id=id, name=name, desc=str(desc) )
        except:
            logging.error( "EXCEPTION at loc#" + id + " : " + str(sys.exc_info()[1]) )
            continue

def parse_objects(url):
    e = make_request(url)

    for each in e.find("results"):
        id = each.find("id").text
        name = each.find("name").text
        desc = each.find("description").text

        # parameterized statement
        s = text("""
                REPLACE INTO DETAIL_OBJECT
                VALUES ( :id, :name, :desc );
                """)

        # run the query
        try:
            results = conn.execute( s, id=id, name=name, desc=str(desc) )
        except:
            logging.error( "EXCEPTION at obj#" + id + " : " + str(sys.exc_info()[1]) )
            continue

def parse_persons(url):
    e = make_request(url)

    for each in e.find("results"):
        id = each.find("id").text
        name = each.find("name").text
        gender = each.find("gender").text
        birth = each.find("birth").text
        death = each.find("death").text

        # parameterized statement
        s = text("""
                REPLACE INTO DETAIL_PERSON
                VALUES ( :id, :name, :gender, :birth, :death);
                """)

        # run the query
        try:
            results = conn.execute( s, id=id, name=name, gender=gender, birth=birth, death=death )
        except:
            logging.error( "EXCEPTION at person#" + id + " : " + str(sys.exc_info()[1]) )
            continue

def parse_powers(url):
    e = make_request(url)

    for each in e.find("results"):
        id = each.find("id").text
        name = each.find("name").text
        desc = each.find("description").text

        # parameterized statement
        s = text("""
                REPLACE INTO DETAIL_POWER
                VALUES ( :id, :name, :desc );
                """)

        # run the query
        try:
            results = conn.execute( s, id=id, name=name, desc=str(desc) )
        except:
            logging.error( "EXCEPTION at power#" + id + " : " + str(sys.exc_info()[1]) )
            continue

def parse_publishers(url):
    e = make_request(url)

    for each in e.find("results"):
        id = each.find("id").text
        name = each.find("name").text
        desc = each.find("description").text

        # parameterized statement
        s = text("""
                REPLACE INTO DETAIL_PUBLISHER
                VALUES ( :id, :name, :desc );
                """)

        # run the query
        try:
            results = conn.execute( s, id=id, name=name, desc=str(desc) )
        except:
            logging.error( "EXCEPTION at publ#" + id + " : " + str(sys.exc_info()[1]) )
            continue

def parse_teams(url):
    e = make_request(url)

    for each in e.find("results"):
        id = each.find("id").text
        name = each.find("name").text
        desc = each.find("description").text

        # parameterized statement
        s = text("""
                REPLACE INTO DETAIL_TEAM
                VALUES ( :id, :name, :desc );
                """)

        # run the query
        try:
            results = conn.execute( s, id=id, name=name, desc=str(desc) )
        except:
            logging.error( "EXCEPTION at team#" + id + " : " + str(sys.exc_info()[1]) )
            continue
### END PARSING ###

### START N TO M MAPPING ###
def update_character_mappings():
    s = text("SELECT CHARACTER_ID FROM DETAIL_CHARACTER")
    id_list = conn.execute( s ).fetchall()

    requests = []
    for i in id_list:
        request_url = "http://api.comicvine.com/character/" + str( i['CHARACTER_ID']) + "/?api_key=" + config.APIKEY
        requests.append( request_url )

    for r in requests:
        char = make_request(r)

        # gnarly one-line selects
        char_id = char.find("results").find("id").text
        issues = char.find("results").find("issue_credits")
        powers = char.find("results").find("powers")
        teams = char.find("results").find("teams")

        # char/issue mapping
        for each in issues:
            issue_id = each.find("id").text

            s = text("REPLACE INTO ISSUE_CHARACTER VALUES(:issue_id, :char_id)")

            try:
                results = conn.execute( s, issue_id=issue_id, char_id=char_id )
            except:
                logging.error( "EXCEPTION at char,issue#" + char.find("id") + " : " + str(sys.exc_info()[1]) )
                continue

        # char/power mapping
        for each in powers:
            power_id = each.find("id").text

            s = text("REPLACE INTO CHARACTER_POWER VALUES(:char_id, :power_id)")

            try:
                results = conn.execute( s, char_id=char_id, power_id=power_id )
            except:
                logging.error( "EXCEPTION at char,power#" + char.find("id") + " : " + str(sys.exc_info()[1]) )
                continue

        # char/team mapping
        for each in teams:
            team_id = each.find("id").text

            s = text("REPLACE INTO CHARACTER_TEAM VALUES(:char_id, :team_id)")

            try:
                results = conn.execute( s, char_id=char_id, team_id=team_id)
            except:
                logging.error( "EXCEPTION at char,team#" + char.find("id") + " : " + str(sys.exc_info()[1]) )
                continue

def update_location_mappings():
    s = text("SELECT LOCATION_ID FROM DETAIL_LOCATION")
    id_list = conn.execute( s ).fetchall()

    requests = []
    for i in id_list:
        request_url = "http://api.comicvine.com/location/" + str( i['LOCATION_ID']) + "/?api_key=" + config.APIKEY
        requests.append( request_url )

    for r in requests:
        location = make_request(r)

        # gnarly one-line selects
        loc_id = location.find("results").find("id").text
        issues = location.find("results").find("issue_credits")

        # location/issue mapping
        for each in issues:
            issue_id = each.find("id").text

            s = text("REPLACE INTO ISSUE_LOCATION VALUES(:issue_id, :loc_id)")

            try:
                results = conn.execute( s, issue_id=issue_id, loc_id=loc_id )
            except:
                logging.error( "EXCEPTION at loc,issue#" + team_id + " : " + str(sys.exc_info()[1]) )
                continue

def update_person_mappings():
    s = text("SELECT PERSON_ID FROM DETAIL_PERSON")
    id_list = conn.execute( s ).fetchall()

    requests = []
    for i in id_list:
        request_url = "http://api.comicvine.com/person/" + str( i['PERSON_ID']) + "/?api_key=" + config.APIKEY
        requests.append( request_url )

    for r in requests:
        person = make_request(r)

        # gnarly one-line selects
        person_id = person.find("results").find("id").text
        issues = person.find("results").find("issue_credits")

        # person/issue mapping
        for each in issues:
            issue_id = each.find("id").text

            s = text("REPLACE INTO ISSUE_PERSON VALUES(:issue_id, :person_id)")

            try:
                results = conn.execute( s, issue_id=issue_id, person_id=person_id )
            except:
                logging.error( "EXCEPTION at person,issue#" + team_id + " : " + str(sys.exc_info()[1]) )
                continue

def update_team_mappings():
    s = text("SELECT TEAM_ID FROM DETAIL_TEAM")
    id_list = conn.execute( s ).fetchall()

    requests = []
    for i in id_list:
        request_url = "http://api.comicvine.com/team/" + str( i['TEAM_ID']) + "/?api_key=" + config.APIKEY
        requests.append( request_url )

    for r in requests:
        team = make_request(r)

        # gnarly one-line selects
        team_id = team.find("results").find("id").text
        issues = team.find("results").find("issue_credits")

        # team/issue mapping
        for each in issues:
            issue_id = each.find("id").text

            s = text("REPLACE INTO ISSUE_TEAM VALUES(:issue_id, :team_id)")

            try:
                results = conn.execute( s, issue_id=issue_id, team_id=team_id )
            except:
                logging.error( "EXCEPTION at team,issue#" + team_id + " : " + str(sys.exc_info()[1]) )
                continue
### END N TO M MAPPING ###

### START REQUEST HANDLING ###
def make_request(url):
    logging.info("making request " + url)

    # do request
    output = urllib.urlopen(url).read()

    # clean the data up
    u = unicode(output, errors='replace')
    cleaned = u.encode('ascii', 'replace')

    # tree it up
    e = ElementTree.fromstring(cleaned)

    return e

def request_builder(req_type):
    # make one request of $type in order to paginate
    logging.debug("making initial request for " + req_type)
    initial = "http://api.comicvine.com/" + req_type + "/?api_key=" + config.APIKEY

    # set up the pagination
    e = make_request(initial)
    pages = int( e.find("number_of_total_results").text ) / 100

    # build a ton of paginated requests and append them to the global requests
    # XXX: fix range
    for offset in range(0, pages+1):
        request_url = "http://api.comicvine.com/" + req_type + "/?api_key=" + config.APIKEY + "&offset=" + str(offset*100)
        requests.append( (request_url, req_type) )
### END REQUEST HANDLING ###

if __name__ == "__main__":
    # logging
    LOG_FILENAME = '/tmp/comic_log'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.debug("*** starting parser.py ***")

    # sql connection
    engine = create_engine('mysql://' + config.USERNAME + ':' + config.PASSWORD + '@localhost/' + config.DATABASE)
    conn = engine.connect()

    # parser function mappings
    funcmap = { 'characters': parse_characters,
                'issues': parse_issues,
                'locations': parse_locations,
                'objects': parse_objects,
                'powers': parse_powers,
                'persons': parse_persons,
                'publishers': parse_publishers,
                'teams': parse_teams,
               }

    # build alot of requests (http://hyperboleandahalf.blogspot.com/2010/04/alot-is-better-than-you-at-everything.html)
    requests = []
    request_builder("characters")
    request_builder("locations")
    request_builder("objects")
    request_builder("persons")
    request_builder("powers")
    request_builder("publishers")
    request_builder("teams")
    request_builder("issues")

    # magic happens here: requests are in the form (url, type) so we use
    # funcmap[type] to grab the function and then pass in url
    for each in requests:
        funcmap[ each[1] ](each[0])

    # now that the database is populated, build the N:M relations
    update_character_mappings()
    update_location_mappings()
    update_person_mappings()
    update_team_mappings()
