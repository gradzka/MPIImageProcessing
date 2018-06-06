from flask import Flask, jsonify, abort, request, make_response, send_file
import sys
from PIL import Image
from werkzeug.utils import secure_filename
from io import BytesIO
import psutil
import datetime
import subprocess
import os

app = Flask(__name__, static_url_path="")

@app.errorhandler(400)
def bad_request(error):
    if error == "":
        return make_response(jsonify({'Error': 'Bad request'}), 400)
    else:
        return make_response(jsonify({'Error': error}), 400)		

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Not found'}), 404)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'bmp'])

def deleteFile(file):
    if os.path.isfile(file):
        os.remove(file)

def getExtension(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'jpg':
        ext = 'jpeg'
    return ext

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def checkImage(request):
    if 'file' not in request.files:
        return 'No file part'
    elif request.files['file'].filename == '':
        return 'No selected file'
    elif not allowed_file(request.files['file'].filename):
        return 'Bad extension'
    else:
        return ''

def is_number(s, checkingInt):
    try:
        if checkingInt:
            int(s)
            return True
        else:
            float(s)
            return True
    except ValueError:
        return False

def checkParam(request, param, checkingInt):
    if param not in request.form:
        return 'No param part'
    elif request.form[param] == '':
        return 'Empty param'
    elif (not is_number(request.form[param], checkingInt)):
        return 'Param must be digit'
    else:
        return ''

def serve_pil_image(pil_img, filename):
    byte_io = BytesIO()
    ext = getExtension(filename)
    pil_img.save(byte_io, ext)
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/'+ext)

def getMaxProcsNumber(request):
    maxProcsNumber = 1
    error = checkParam(request, "proc", True)
    if error == '':
        maxProcsNumber = int(request.form['proc'])
        if maxProcsNumber<1 or maxProcsNumber>8:
            maxProcsNumber = 1
    return maxProcsNumber

def getExecutableWithoutPrefix():
    return sys.executable.replace(sys.exec_prefix,"")[1:]

def verification(maxProcsNumber):
    numberOfProcesses = 0;
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == getExecutableWithoutPrefix() and len(p.cmdline()) > 1 and "MPIImageProcessing.py" in p.cmdline()[1]:
            numberOfProcesses+=1
    if (maxProcsNumber+numberOfProcesses) > 64:
        return 'Server is busy'
    else:
        return ''

@app.route('/histogram', methods=['POST'])
def histogram():
    try:
        error = checkImage(request)
        if error != '':
            return bad_request(error)
    
        maxProcsNumber = getMaxProcsNumber(request)
        error = verification(maxProcsNumber)
        if error != '':
            return bad_request(error)

        file = request.files['file']
        INPicture = Image.open(file.stream)

        ext = getExtension(file.filename)
        path = (file.filename + str(request.environ['REMOTE_ADDR']) + str(datetime.datetime.now())).replace(":","").replace(".","") + "." + ext
        INPicture.save(path)
        subprocess.call(["mpiexec", "-n", "1", getExecutableWithoutPrefix(), "Worker.py", path, "histogram", str(maxProcsNumber)])

        deleteFile(path)
        file = open("OUT_" + path + ".json", "r") 
        histogram = file.read()
        file.close()

        deleteFile("OUT_" + path + ".json")

        return jsonify({'Result': histogram})
    except:
        return bad_request('Server error')

@app.route('/rotation', methods=['POST'])
def rotate():
    try:
        error = checkImage(request)
        if error != '':
            return bad_request(error)
    
        error = checkParam(request, "option", True)
        if error != '':
            return bad_request(error)

        option = int(request.form['option'])
        if option<0 or option>2:
            return bad_request('Invalid option value')

        maxProcsNumber = getMaxProcsNumber(request)
        error = verification(maxProcsNumber)
        if error != '':
            return bad_request(error)

        file = request.files['file']
        INPicture = Image.open(file.stream)
        
        ext = getExtension(file.filename)
        path = (file.filename + str(request.environ['REMOTE_ADDR']) + str(datetime.datetime.now())).replace(":","").replace(".","") + "." + ext
        INPicture.save(path)
        subprocess.call(["mpiexec", "-n", "1", getExecutableWithoutPrefix(), "Worker.py", path, "rotation", str(maxProcsNumber), str(option)])
        deleteFile(path)
        OUTPicture = Image.open("OUT_" + path)

        result = serve_pil_image(OUTPicture, "OUT_" + secure_filename(file.filename))
        OUTPicture.close()

        deleteFile("OUT_" + path)

        return result
    except Exception as e:
        return bad_request('Server error')

@app.route('/reflection', methods=['POST'])
def reflect():
    try:
        error = checkImage(request)
        if error != '':
            return bad_request(error)
    
        error = checkParam(request, "option", True)
        if error != '':
            return bad_request(error)

        option = int(request.form['option'])
        if option<0 or option>1:
            return bad_request('Invalid option value')

        maxProcsNumber = getMaxProcsNumber(request)
        error = verification(maxProcsNumber)
        if error != '':
            return bad_request(error)

        file = request.files['file']
        INPicture = Image.open(file.stream)

        ext = getExtension(file.filename)
        path = (file.filename + str(request.environ['REMOTE_ADDR']) + str(datetime.datetime.now())).replace(":","").replace(".","") + "." + ext
        INPicture.save(path)
        subprocess.call(["mpiexec", "-n", "1", getExecutableWithoutPrefix(), "Worker.py", path, "mirrorReflection", str(maxProcsNumber), str(option)])
        
        deleteFile(path)
        OUTPicture = Image.open("OUT_" + path)
        
        result = serve_pil_image(OUTPicture, "OUT_" + secure_filename(file.filename))
        OUTPicture.close()

        deleteFile("OUT_" + path)

        return result
    except:
        return bad_request('Server error')

@app.route('/filter/<string:operation_name>', methods=['POST'])
def filter(operation_name):
    try:
        if (operation_name != "RGBSelection") and (operation_name != "brightness") and (operation_name != "contrast") and (operation_name != "gamma") and (operation_name != "negative") and (operation_name != "shadesOfGrey"):
            return bad_request("")

        error = checkImage(request)
        if error != '':
            return bad_request(error)
    
        option = None

        if (operation_name == "RGBSelection") or (operation_name == "brightness"):
            error = checkParam(request, "option", True)
            if error != '':
                return bad_request(error)
            option = int(request.form['option'])
            if (operation_name == "RGBSelection") and (option<0 or option>2):
                return bad_request('Invalid option value')
            if (operation_name == "brightness") and (option<-255 or option>255):
                return bad_request('Invalid option value')

        if (operation_name == "contrast") or (operation_name == "gamma"):
            error = checkParam(request, "option", False)
            if error != '':
                return bad_request(error)
            option = float(request.form['option'])
            if option<0.1 or option>10:
                return bad_request('Invalid option value')

        maxProcsNumber = getMaxProcsNumber(request)
        error = verification(maxProcsNumber)
        if error != '':
            return bad_request(error)

        file = request.files['file']
        INPicture = Image.open(file.stream)

        ext = getExtension(file.filename)
        path = (file.filename + str(request.environ['REMOTE_ADDR']) + str(datetime.datetime.now())).replace(":","").replace(".","") + "." + ext
        INPicture.save(path)

        if (operation_name == "RGBSelection") or (operation_name == "brightness") or (operation_name == "contrast") or (operation_name == "gamma"):
            subprocess.call(["mpiexec", "-n", "1", getExecutableWithoutPrefix(), "Worker.py", path, operation_name, str(maxProcsNumber), str(option)])
        else:
            subprocess.call(["mpiexec", "-n", "1", getExecutableWithoutPrefix(), "Worker.py", path, operation_name, str(maxProcsNumber)])
        
        deleteFile(path)
        OUTPicture = Image.open("OUT_" + path)
        
        result = serve_pil_image(OUTPicture, "OUT_" + secure_filename(file.filename))
        OUTPicture.close()

        deleteFile("OUT_" + path)

        return result
    except:
        return bad_request('Server error')

from netifaces import interfaces, ifaddresses, AF_INET

def ip4_addresses():
    ip_list = []
    for interface in interfaces():
        if ifaddresses(interface).get(AF_INET) != None:
            for link in ifaddresses(interface).get(AF_INET):
                if link.get('addr') != None:
                    ip_list.append(link.get('addr'))
    return ip_list

if __name__ == '__main__':
    ip_list = ip4_addresses()
    if len(ip_list) > 0:
        chosenIPAddr = ""
        while chosenIPAddr == "": 
            i = 0;
            for ipAddr in ip_list:
                print(i, '-', ipAddr)
                i+=1
            data = input("Choose network interface: ")
            print('')
            if is_number(data, True):
                option = int(data)
                if option >= 0 and option < len(ip_list):
                    chosenIPAddr = ip_list[option]
        app.run(host=chosenIPAddr, port=1247, threaded=True)
    else:
        print('No network interface available!')