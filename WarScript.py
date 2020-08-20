from app import app


@app.route('/testroute2', methods=['GET'])
def testfunc2():
    return 'it works!2'
