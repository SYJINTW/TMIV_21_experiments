import os
import pandas as pd
import numpy as np

def copy_pose():
    camera = '6x6'
    for scene in range(5):
        os.system(f'cat ./{camera}_{scene}/nG1/rec_0/{camera}_{scene}_rec0_AdditiveSynthesizer_pose1_texture_1280x720_yuv420p10le.yuv > move.yuv')

if __name__ == '__main__':
    copy_pose()