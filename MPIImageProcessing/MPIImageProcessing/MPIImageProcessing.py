from mpi4py import MPI
import numpy
import ImageProcessing as ImageProc
from PIL import Image
import ReductionProcess


comm = MPI.Comm.Get_parent()
size = comm.Get_size()
rank = comm.Get_rank()

INPicture = None
operation_name = None

operation_name=comm.bcast(operation_name, root=0)
INPicture=comm.bcast(INPicture, root=0)

myFirst = int((rank * INPicture.height) / size)
myLast = int(((rank+1) * INPicture.height) / size)
#print(rank, INPicture.width, INPicture.height, myFirst, myLast)
#OUTPicture = ImageProc.negative(INPicture, myFirst, myLast)

if operation_name == "histogram":   
    myFirst = int((rank * INPicture.width*INPicture.height) / size)
    myLast = int(((rank+1) * INPicture.width*INPicture.height) / size)
    histogram = ImageProc.imageProcessing[operation_name](list(INPicture.getdata()),myFirst,myLast)
elif (operation_name == "RGBSelection") or (operation_name == "brightness") or (operation_name == "contrast") or (operation_name == "gamma") or (operation_name == "rotation") or (operation_name == "mirrorReflection"):
    option = None
    option=comm.bcast(option, root=0)
    OUTPicture = ImageProc.imageProcessing[operation_name](INPicture,myFirst,myLast,option)
elif  (operation_name == "negative") or (operation_name == "shadesOfGrey"):
    OUTPicture = ImageProc.imageProcessing[operation_name](INPicture,myFirst,myLast)

if operation_name == "histogram":
    my_op = MPI.Op.Create(ImageProc.my_histogram_sum)
    histogram = comm.reduce(histogram, op=my_op, root=0)
else: 
    my_op = MPI.Op.Create(ImageProc.my_sum)
    reductProc = ReductionProcess.ReductionProcess(rank, size,OUTPicture)
    reductProc=comm.reduce(reductProc, op=my_op, root=0)

comm.Disconnect()