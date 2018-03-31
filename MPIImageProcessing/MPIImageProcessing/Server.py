from flask import Flask, jsonify, abort, request, make_response
from mpi4py import MPI
import numpy
import sys

app = Flask(__name__, static_url_path="")
print('Iam')
sys.stdout.flush()

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    
@app.route('/hello', methods=['GET'])
def get_pi():
    comm = MPI.COMM_SELF.Spawn(sys.executable, args=['MPIImageProcessing.py'], maxprocs=4)
    N = numpy.array(100, 'i')
    comm.Bcast([N, MPI.INT], root=MPI.ROOT)
    PI = numpy.array(0.0, 'd')
    comm.Reduce(None, [PI, MPI.DOUBLE], op=MPI.SUM, root=MPI.ROOT)
    print(PI)
    sys.stdout.flush()
    comm.Disconnect()
    return jsonify({'Result': str(PI)})
    
@app.route('/hello/<string:account_name>/summary', methods=['GET'])
def get_with_param(account_name):
    return jsonify({'Receive': str(account_name)})

# import ImageProcessing as ImageProc
# from PIL import Image
if __name__ == '__main__':
    # wybor skladowej (RGB) (opcja: R(0)|G(1)|B(2))
    # INPicture = Image.open("haft.jpg")
    # OUTPicture = ImageProc.selectionOfRGB(INPicture, 0, INPicture.height, 1)
    # OUTPicture.save("outhaft.jpg")
    app.run(host='localhost', port=1247)
