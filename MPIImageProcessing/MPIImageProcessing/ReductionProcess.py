class ReductionProcess:
    def addToCompletedRanks(self, completed_rank):
        self.completedRanks.append(completed_rank)
    def __init__(self, rank,size, picture):
        #process rank
        self.rank = rank
        #size
        self.size = size
        #picture
        self.picture = picture
        #list of processes which end work
        self.completedRanks = []
        self.completedRanks.append(rank)




