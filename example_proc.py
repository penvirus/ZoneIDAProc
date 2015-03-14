from ida_proc import IDAProc

app = IDAProc()

@app.route('test/file_a')
def file_a():
    return 'Test String'

@app.route('test/file_b')
def file_b():
    return 99999

if __name__ == '__main__':
    app.run()
