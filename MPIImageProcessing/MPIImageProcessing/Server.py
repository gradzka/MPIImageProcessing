from flask import Flask, jsonify, abort, request, make_response
from mpi4py import MPI
import numpy
import sys

import ImageProcessing as ImageProc
from PIL import Image

app = Flask(__name__, static_url_path="")
print('Iam')
sys.stdout.flush()
my_op = MPI.Op.Create(ImageProc.my_sum)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    
@app.route('/histogram', methods=['GET'])
def histogram():
    return jsonify({'Result': 'OK'})

@app.route('/rotation', methods=['GET'])
def rotate():
    return jsonify({'Result': 'OK'})

@app.route('/reflection', methods=['GET'])
def reflect():
    return jsonify({'Result': 'OK'})

@app.route('/filter/<string:operation_name>', methods=['GET'])
def get_with_param(operation_name):
    #convert image to Image object
    INPicture = Image.open("teddy.jpg")  
    comm = MPI.COMM_SELF.Spawn(sys.executable, args=['MPIImageProcessing.py'], maxprocs=4)
    comm.bcast(operation_name, root=MPI.ROOT)
    comm.bcast(INPicture, root=MPI.ROOT)
    #send in bcast option
    if (operation_name == "RGBSelection") or (operation_name == "brightness") or (operation_name == "contrast") or (operation_name == "gamma") or (operation_name == "rotation") or (operation_name == "mirrorReflection"):
        comm.bcast(0, root=MPI.ROOT)# change first parameter to option
    OUTPicture = None
    OUTPicture=comm.reduce(None, op=my_op, root=MPI.ROOT)
    comm.Disconnect()
    OUTPicture.save("out " + operation_name + ".jpg")
    return jsonify({'Receive': str(operation_name)})

if __name__ == '__main__':
    app.run(host='localhost', port=1247)
