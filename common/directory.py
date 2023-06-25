import os
def exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
