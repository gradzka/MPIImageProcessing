from mpi4py import MPI
import ImageProcessing as ImageProc
from PIL import Image
import sys
import json


def Work():
    try:
        if len(sys.argv)>3:
            maxProcNo = sys.argv[3]
            if not maxProcNo.isdigit():
                return
            maxProcNo = int(maxProcNo)
            #pathToFile SHA
            path = sys.argv[1]
            action = sys.argv[2]
            if action in ["histogram", "rotation", "mirrorReflection", "RGBSelection", "negative", "shadesOfGrey", "brightness", "contrast", "gamma"]:
                if action in ["rotation", "mirrorReflection", "RGBSelection", "brightness", "contrast", "gamma"]:
                    if len(sys.argv)>4:
                        if action in ["contrast", "gamma"]:
                            option = float(sys.argv[4])
                            if option<0.1 or option>10:
                                return
                        elif action in ["RGBSelection","rotation"]:
                            option = int(sys.argv[4])
                            if option not in [0,1,2]:
                                return
                        elif action == "brightness":
                            option = int(sys.argv[4])
                            if option <-255 or option>255:
                                return
                        elif action == "mirrorReflection":
                            option = int(sys.argv[4])
                            if option not in [0,1]:
                                return
                    else:
                        return
                comm = MPI.COMM_SELF.Spawn(sys.executable, args=['MPIImageProcessing.py'], maxprocs=maxProcNo)
                #read InPicture
                INPicture = Image.open(path)
                comm.bcast(action, root=MPI.ROOT)
                comm.bcast(INPicture, root=MPI.ROOT)
                if len(sys.argv)>4:
                    comm.bcast(option, root=MPI.ROOT)
                #histogram or another
                if action == "histogram":
                    my_op = MPI.Op.Create(ImageProc.my_histogram_sum)
                    histogram = comm.reduce(None, op=my_op, root=MPI.ROOT)
                    serializedHistogram = json.dumps(histogram)
                    with open("OUT_"+sys.argv[1]+".json", "w") as file:
                        file.write(serializedHistogram)
                else: 
                    OUTPicture = None
                    my_op = MPI.Op.Create(ImageProc.my_sum)
                    OUTPicture=comm.reduce(None, op=my_op, root=MPI.ROOT)
                    OUTPicture.save("OUT_"+sys.argv[1])
                comm.Disconnect()
    except Exception as e:
        print("error: {0}".format(e))

if __name__ == '__main__':
    Work()