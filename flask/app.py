# setup
from flask import Flask
from flask import render_template, redirect, request
app = Flask(__name__)

# SQL
from database import db_session
from sqlalchemy.sql import text

@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response

@app.route('/')
def index():
    return render_template("index.html")

### START CHARACTER PAGES ###
@app.route('/char/<int:page>/')
def char_list(page):
    s = text("""
                SELECT C.CHARACTER_ID, CHARACTER_NAME, CHARACTER_GENDER, COUNT( * ) AS ISSUE_COUNT
                FROM DETAIL_CHARACTER C, ISSUE_CHARACTER I
                    WHERE I.CHARACTER_ID = C.CHARACTER_ID
                GROUP BY C.CHARACTER_ID
                ORDER BY CHARACTER_NAME ASC
                LIMIT 30
                OFFSET :p
            """)
    results = db_session.execute( s, {'p':page*30} )
    obj = results.fetchall()

    s = text("""
                SELECT DISTINCT C.CHARACTER_ID, CHARACTER_NAME, CHARACTER_GENDER
                FROM DETAIL_CHARACTER C, USER_ISSUE U, ISSUE_CHARACTER I
                    WHERE U.ISSUE_ID = I.ISSUE_ID
                    AND I.CHARACTER_ID = C.CHARACTER_ID
            """)
    results = db_session.execute( s )
    obj2 = results.fetchall()

    return render_template( "char_list.html", obj=obj, obj2=obj2, page=page )

@app.route('/char/detail/<int:id>/')
def char_detail(id):
    s = text("""
                SELECT *
                FROM `DETAIL_CHARACTER`
                WHERE CHARACTER_ID = :id
            """)
    results = db_session.execute( s, {'id':id} )
    obj = results.fetchone()

    s = text("""
                SELECT *
                FROM ISSUE_CHARACTER C, DETAIL_ISSUE I
                    WHERE C.CHARACTER_ID = :id
                    AND I.ISSUE_ID = C.ISSUE_ID
                ORDER BY I.ISSUE_YEAR DESC
                LIMIT 30
            """)
    results = db_session.execute( s, {'id':id} )
    obj2 = results.fetchall()

    s = text("""
                SELECT DP.POWER_ID, DP.POWER_NAME
                FROM DETAIL_CHARACTER C, CHARACTER_POWER CP, DETAIL_POWER DP
                    WHERE CP.POWER_ID = C.CHARACTER_ID
                    AND CP.CHARACTER_ID = DP.POWER_ID
                    AND C.CHARACTER_ID = :id
            """)
    results = db_session.execute( s, {'id':id} )
    obj3 = results.fetchall()

    return render_template( "char_detail.html", obj=obj, obj2=obj2, obj3=obj3)
### END CHARACTER PAGES ###

### START ISSUE PAGES ###
@app.route('/issue/search/', methods=['GET','POST'])
def issue_search():
    if request.method == 'POST':
        q = request.form['search']
        q = '%' + q + '%'

        s = text("""
                    SELECT ISSUE_ID, ISSUE_NAME, ISSUE_DAY, ISSUE_MONTH, ISSUE_YEAR
                    FROM DETAIL_ISSUE
                    WHERE ISSUE_NAME LIKE :q
                    ORDER BY `ISSUE_YEAR` DESC , `ISSUE_MONTH` DESC , `ISSUE_DAY` DESC
                """)
        results = db_session.execute( s, {'q':q} )
        obj = results.fetchall()
    else:
        obj = ''

    s = text("""
                SELECT I.ISSUE_ID, ISSUE_NAME, ISSUE_DAY, ISSUE_MONTH, ISSUE_YEAR
                FROM USER_ISSUE U, DETAIL_ISSUE I
                    WHERE U.ISSUE_ID = I.ISSUE_ID
                LIMIT 30
            """)
    results = db_session.execute( s )
    obj2 = results.fetchall()

    return render_template( "issue_search.html", obj=obj, obj2=obj2 )

@app.route('/issue/<int:page>/')
def issue_list(page):
    s = text("""
                SELECT ISSUE_ID, ISSUE_NAME, ISSUE_DAY, ISSUE_MONTH, ISSUE_YEAR
                FROM DETAIL_ISSUE
                ORDER BY `ISSUE_YEAR` DESC , `ISSUE_MONTH` DESC , `ISSUE_DAY` DESC
                LIMIT 30
                OFFSET :p
            """)
    results = db_session.execute( s, {'p':page*30} )
    obj = results.fetchall()

    s = text("""
                SELECT I.ISSUE_ID, ISSUE_NAME, ISSUE_DAY, ISSUE_MONTH, ISSUE_YEAR
                FROM USER_ISSUE U, DETAIL_ISSUE I
                    WHERE U.ISSUE_ID = I.ISSUE_ID
                LIMIT 30
            """)
    results = db_session.execute( s )
    obj2 = results.fetchall()

    return render_template( "issue_list.html", obj=obj, obj2=obj2, page=page )

@app.route('/issue/detail/<int:id>/')
def issue_detail(id):
    s = text("SELECT * FROM `DETAIL_ISSUE` WHERE ISSUE_ID= :id")
    results = db_session.execute( s, {'id':id} )
    obj = results.fetchone()

    s = text("""
                SELECT DI.ISSUE_NUM, DI.ISSUE_NAME, DL.LOCATION_ID, DL.LOCATION_NAME
                FROM DETAIL_LOCATION DL , ISSUE_LOCATION IL , DETAIL_ISSUE DI
                    WHERE DL.LOCATION_ID = IL.LOCATION_ID
                    AND IL.ISSUE_ID = DI.ISSUE_ID
                    AND DI.ISSUE_NAME = :id
            """)
    results = db_session.execute( s, {'id':id} )
    obj2 = results.fetchall()

    return render_template( "issue_detail.html", obj=obj, obj2=obj2 )

@app.route('/issue/add/<int:id>/<path:next_page>')
def issue_add(id, next_page):
    s = text("REPLACE INTO USER_ISSUE VALUES(:id)")
    results = db_session.execute( s, {'id':id} )
    return redirect( next_page )

@app.route('/issue/del/<int:id>/<path:next_page>')
def issue_del(id, next_page):
    s = text("DELETE FROM USER_ISSUE WHERE ISSUE_ID=:id")
    results = db_session.execute( s, {'id':id} )
    return redirect( next_page )
### END ISSUE PAGES ###

### START LOCATION PAGES ###
@app.route('/loc/<int:page>/')
def loc_list(page):
    s = text("SELECT * FROM `DETAIL_LOCATION` ORDER BY `LOCATION_NAME` LIMIT 30 OFFSET :p")
    results = db_session.execute( s, {'p':page*30} )
    return render_template( "loc_list.html", obj=results.fetchall(), page=page )

@app.route('/loc/detail/<int:id>/')
def loc_detail(id):
    s = text("SELECT * FROM `DETAIL_LOCATION` WHERE LOCATION_ID= :id")
    results = db_session.execute( s, {'id':id} )
    obj = results.fetchone()

    s = text("""
                SELECT DI.ISSUE_ID, DI.ISSUE_NAME, DL.LOCATION_ID, DL.LOCATION_NAME
                FROM DETAIL_LOCATION DL , ISSUE_LOCATION IL , DETAIL_ISSUE DI
                    WHERE DL.LOCATION_ID = IL.LOCATION_ID
                    AND IL.ISSUE_ID = DI.ISSUE_ID
                    AND DL.LOCATION_ID = :id
            """)
    results = db_session.execute( s, {'id':id} )
    obj2 = results.fetchall()

    return render_template( "loc_detail.html", obj=obj, obj2=obj2 )
### END LOCATION PAGES ###

### START POWER PAGES ###
@app.route('/power/<int:page>/')
def power_list(page):
    s = text("SELECT * FROM `DETAIL_POWER` ORDER BY `POWER_NAME` LIMIT 30 OFFSET :p")
    results = db_session.execute( s, {'p':page*30} )
    return render_template( "power_list.html", obj=results.fetchall(), page=page )

@app.route('/power/detail/<int:id>/')
def power_detail(id):
    s = text("SELECT * FROM `DETAIL_POWER` WHERE POWER_ID= :id")
    results = db_session.execute( s, {'id':id} )
    return render_template( "power_detail.html", obj=results.fetchone() )
### END POWER PAGES ###

### START PUBLISHER PAGES ###
@app.route('/pub/<int:page>/')
def pub_list(page):
    s = text("SELECT * FROM `DETAIL_PUBLISHER` ORDER BY `PUB_NAME` LIMIT 30 OFFSET :p")
    results = db_session.execute( s, {'p':page*30} )
    return render_template( "pub_list.html", obj=results.fetchall(), page=page )

@app.route('/pub/detail/<int:id>/')
def pub_detail(id):
    s = text("SELECT * FROM `DETAIL_PUBLISHER` WHERE PUB_ID= :id")
    results = db_session.execute( s, {'id':id} )
    return render_template( "pub_detail.html", obj=results.fetchone() )
### END POWER PAGES ###

### START CREATOR PAGES ###
@app.route('/cre/<int:page>/')
def cre_list(page):
    s = text("SELECT * FROM `DETAIL_PERSON` ORDER BY `PERSON_NAME` LIMIT 30 OFFSET :p")
    results = db_session.execute( s, {'p':page*30} )
    return render_template( "cre_list.html", obj=results.fetchall(), page=page )

@app.route('/cre/detail/<int:id>/')
def cre_detail(id):
    s = text("SELECT * FROM `DETAIL_PERSON` WHERE PERSON_ID= :id")
    results = db_session.execute( s, {'id':id} )
    obj = results.fetchone()

    s = text("""
                SELECT DI.ISSUE_ID, DI.ISSUE_NAME, DP.PERSON_ID, DP.PERSON_NAME
                FROM  DETAIL_ISSUE DI , ISSUE_PERSON IP, DETAIL_PERSON DP
                    WHERE DI.ISSUE_ID = IP.ISSUE_ID
                    AND IP.CREATOR_ID = DP.PERSON_ID
                    AND DP.PERSON_ID = :id
            """)
    results = db_session.execute( s, {'id':id} )
    obj2 = results.fetchall()

    return render_template( "cre_detail.html", obj=obj, obj2=obj2 )
### END CREATOR PAGES ###

if __name__ == '__main__':
    app.run(host='192.168.10.10', port=5000, debug=True)
#    app.run()
