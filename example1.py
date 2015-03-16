from ida_proc import IDAProc

app = IDAProc()

@app.route('test/file_a')
def file_a():
    return 'Test String'

b_data = 99999

@app.route('test/file_b')
def file_b():
    global b_data
    return b_data

@app.route('test/file_b', method='SET')
def file_b(data):
    global b_data
    b_data = data
    return data

if __name__ == '__main__':
    app.run()
