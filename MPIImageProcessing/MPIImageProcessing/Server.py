from flask import Flask, jsonify, abort, request, make_response, send_file
from mpi4py import MPI
import numpy
import sys

import ImageProcessing as ImageProc
from PIL import Image

from werkzeug.utils import secure_filename
from io import BytesIO
import psutil

app = Flask(__name__, static_url_path="")

my_op = MPI.Op.Create(ImageProc.my_sum)
my_opH = MPI.Op.Create(ImageProc.my_histogram_sum)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'Error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Not found'}), 404)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

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
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'jpg':
        ext = 'jpeg'
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

def verification(maxProcsNumber):
    numberOfProcesses = 0;
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == "python.exe" and len(p.cmdline()) > 1 and "MPIImageProcessing.py" in p.cmdline()[1]:
            numberOfProcesses+=1
    print('ProcNo: '+str(numberOfProcesses))
    sys.stdout.flush()
    if (maxProcsNumber+numberOfProcesses) > 64:
        return 'Server is busy'
    else:
        return ''

@app.route('/histogram', methods=['POST'])
def histogram():
    error = checkImage(request)
    if error != '':
        return jsonify({'Error': error})
    
    maxProcsNumber = getMaxProcsNumber(request)
    error = verification(maxProcsNumber)
    if error != '':
        return jsonify({'Error': error})

    file = request.files['file']
    INPicture = Image.open(file.stream)

    comm = MPI.COMM_SELF.Spawn(sys.executable, args=['MPIImageProcessing.py'], maxprocs=maxProcsNumber)
    comm.bcast("histogram", root=MPI.ROOT)
    comm.bcast(INPicture, root=MPI.ROOT)
    histogram = None
    histogram=comm.reduce(None, op=my_opH, root=MPI.ROOT)
    return jsonify({'Result': histogram})

@app.route('/rotation', methods=['POST'])
def rotate():
    error = checkImage(request)
    if error != '':
        return jsonify({'Error': error})
    
    error = checkParam(request, "option", True)
    if error != '':
        return jsonify({'Error': error})

    option = int(request.form['option'])
    if option<0 or option>2:
        return jsonify({'Error': 'Invalid option value'})

    maxProcsNumber = getMaxProcsNumber(request)
    error = verification(maxProcsNumber)
    if error != '':
        return jsonify({'Error': error})

    file = request.files['file']
    INPicture = Image.open(file.stream)

    comm = MPI.COMM_SELF.Spawn(sys.executable, args=['MPIImageProcessing.py'], maxprocs=maxProcsNumber)
    comm.bcast("rotation", root=MPI.ROOT)
    comm.bcast(INPicture, root=MPI.ROOT)
    comm.bcast(option, root=MPI.ROOT)

    OUTPicture = None
    OUTPicture=comm.reduce(None, op=my_op, root=MPI.ROOT)
    comm.Disconnect()

    return serve_pil_image(OUTPicture, "out_" + secure_filename(file.filename))

@app.route('/reflection', methods=['POST'])
def reflect():
    error = checkImage(request)
    if error != '':
        return jsonify({'Error': error})
    
    error = checkParam(request, "option", True)
    if error != '':
        return jsonify({'Error': error})

    option = int(request.form['option'])
    if option<0 or option>1:
        return jsonify({'Error': 'Invalid option value'})

    maxProcsNumber = getMaxProcsNumber(request)
    error = verification(maxProcsNumber)
    if error != '':
        return jsonify({'Error': error})

    file = request.files['file']
    INPicture = Image.open(file.stream)

    comm = MPI.COMM_SELF.Spawn(sys.executable, args=['MPIImageProcessing.py'], maxprocs=maxProcsNumber)
    comm.bcast("mirrorReflection", root=MPI.ROOT)
    comm.bcast(INPicture, root=MPI.ROOT)
    comm.bcast(option, root=MPI.ROOT)

    OUTPicture = None
    OUTPicture=comm.reduce(None, op=my_op, root=MPI.ROOT)
    comm.Disconnect()

    return serve_pil_image(OUTPicture, "out_" + secure_filename(file.filename))

@app.route('/filter/<string:operation_name>', methods=['POST'])
def filter(operation_name):
    if (operation_name != "RGBSelection") and (operation_name != "brightness") and (operation_name != "contrast") and (operation_name != "gamma") and (operation_name != "negative") and (operation_name != "shadesOfGrey"):
       return not_found(404)

    error = checkImage(request)
    if error != '':
        return jsonify({'Error': error})
    
    option = None

    if (operation_name == "RGBSelection") or (operation_name == "brightness"):
        error = checkParam(request, "option", True)
        if error != '':
            return jsonify({'Error': error})
        option = int(request.form['option'])
        if (operation_name == "RGBSelection") and (option<0 or option>2):
            return jsonify({'Error': 'Invalid option value'})
        if (operation_name == "brightness") and (option<-255 or option>255):
            return jsonify({'Error': 'Invalid option value'})

    if (operation_name == "contrast") or (operation_name == "gamma"):
        error = checkParam(request, "option", False)
        if error != '':
            return jsonify({'Error': error})
        option = float(request.form['option'])
        if option<0.1 or option>10:
            return jsonify({'Error': 'Invalid option value'})

    maxProcsNumber = getMaxProcsNumber(request)
    error = verification(maxProcsNumber)
    if error != '':
        return jsonify({'Error': error})

    file = request.files['file']
    INPicture = Image.open(file.stream)

    comm = MPI.COMM_SELF.Spawn(sys.executable, args=['MPIImageProcessing.py'], maxprocs=maxProcsNumber)
    comm.bcast(operation_name, root=MPI.ROOT)
    comm.bcast(INPicture, root=MPI.ROOT)

    #send in bcast option
    if (operation_name == "RGBSelection") or (operation_name == "brightness") or (operation_name == "contrast") or (operation_name == "gamma"):
        comm.bcast(option, root=MPI.ROOT)

    OUTPicture = None
    OUTPicture=comm.reduce(None, op=my_op, root=MPI.ROOT)
    comm.Disconnect()

    return serve_pil_image(OUTPicture, "out_" + secure_filename(file.filename))

if __name__ == '__main__':
    app.run(host='localhost', port=1247)