import time
from ida_proc import IDAProc

app = IDAProc()

@app.route('/time')
def ctime():
    return time.ctime()

def register_for_data():
    # nonlocal in python 2.7
    # https://technotroph.wordpress.com/2012/10/01/python-closures-and-the-python-2-7-nonlocal-solution/
    data = dict()
    data['data'] = 99999

    @app.route('/test/data')
    def getter():
        return data['data']

    @app.route('/test/data', method='SET')
    def setter(d):
        data['data'] = d
        return data['data']

if __name__ == '__main__':
    register_for_data()
    app.run()
