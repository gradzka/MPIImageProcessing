from mpi4py import MPI
import numpy
import ImageProcessing as ImageProc
from PIL import Image

comm = MPI.Comm.Get_parent()
size = comm.Get_size()
rank = comm.Get_rank()

INPicture = None
operation_name = None

operation_name=comm.bcast(operation_name, root=0)
INPicture=comm.bcast(INPicture, root=0)

myFirst = int((rank * INPicture.height) / size)
myLast = int(((rank+1) * INPicture.height) / size)
print(rank, INPicture.width, INPicture.height, myFirst, myLast)
OUTPicture = ImageProc.negative(INPicture, myFirst, myLast)
my_op = MPI.Op.Create(ImageProc.my_sum)
OUTPicture=comm.reduce(OUTPicture, op=my_op, root=0)

comm.Disconnect()