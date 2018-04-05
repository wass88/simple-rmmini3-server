from flask import Flask, render_template, Response
import broadlink
import os.path
import pickle
import json
from time import sleep

class SignalDB:
    def __init__(self, filename = "./db.picke"):
        self.load(filename)

    def load(self, filename):
        self.filename = filename
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                self.db = pickle.load(f)
        else:
            self.db = {"signals": {}}
        assert isinstance(self.db["signals"], dict)

    def save(self, filename = None):
        if filename is None:
            filename = self.filename
        with open(filename, 'wb') as f:
            pickle.dump(self.db, f)

    def get_signal(self, name):
        return self.db["signals"].get(name)

    def set_signal(self, name, packet):
        self.db["signals"][name] = packet
        self.save()

    def del_signal(self, name):
        del self.db["signals"][name]
        self.save()

    def info_signal(self, name):
        return self.db["signals"].get(name)

    def signal_list(self):
        return list(self.db["signals"].keys())

class RemoteController:
    def __init__(self):
        self.init_rm()
        self.db = SignalDB()

    def init_rm(self):
        self.device = broadlink.discover(timeout=3)[0]
        self.device.auth()

    def learn(self, name):
        for i in range(4):
            self.device.enter_learning()
            sleep(5)
            signal = self.device.check_data()
            if signal is not None:
                break
        if signal is None:
            return {"status": "ng"}
        else:
            self.db.set_signal(name, signal)
            return {"status": "ok"}

    def emit(self, name):
        signal = self.db.get_signal(name)
        if signal is None:
            return {"status": "ng"}
        self.device.send_data(signal)
        return {"status": "ok"}

    def forget(self, name):
        self.db.del_signal(name)
        return {"status": "ok"}

    def signal_list(self):
        print(self.db.db)
        print(self.db.db["signals"])
        print(self.db.signal_list())
        print(json.dumps(self.db.signal_list()))
        return self.db.signal_list()

app = Flask(__name__)
rc = RemoteController()

def res_json(obj):
    return Response(json.dumps(obj), mimetype='application/json')

@app.route('/api/signals')
def signals_index():
    return res_json(rc.signal_list())

@app.route('/api/signal/<name>')
def signal_info(name):
    return res_json(rc.info(name))

@app.route('/api/signal/<name>/learn')
def signal_learn(name):
    return res_json(rc.learn(name))

@app.route('/api/signal/<name>/emit')
def signal_emit(name):
    return res_json(rc.emit(name))

@app.route('/api/signal/<name>/forget')
def signal_forget(name):
    return res_json(rc.forget(name))

@app.route('/')
def index():
    return render_template("main.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20280)
