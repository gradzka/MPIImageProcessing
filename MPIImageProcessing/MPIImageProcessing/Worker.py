from mpi4py import MPI
import ImageProcessing as ImageProc
from PIL import Image
import sys

if len(sys.argv)>3:
    comm = MPI.COMM_SELF.Spawn(sys.executable, args=['MPIImageProcessing.py'], maxprocs=sys.argv[3])
    #pathToFile SHA
    path = sys.argv[1]
    action = sys.argv[2]
    if len(sys.argv)>4:
        option = sys.argv[4]
    #read InPicture
    INPicture = INPicture = Image.open(sys.argv[1])
    comm.bcast(action, root=MPI.ROOT)
    comm.bcast(INPicture, root=MPI.ROOT)
    comm.bcast(option, root=MPI.ROOT)
    OUTPicture = None
    OUTPicture=comm.reduce(None, op=my_op, root=MPI.ROOT)
    OUTPicture.save("OUT_"+sys.argv[1])
    comm.Disconnect()
