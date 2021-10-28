import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def scene_plot(camera_positions, scenes, QPs, synthesizers, numGroups, pose_traces, numFrame):
    for scene in scenes:
        AdditiveSynthesizer_datas = []
        ViewWeightingSynthesizer_datas = []
        df = pd.DataFrame()
        df_tmp = pd.read_csv(f'./results/{scene}.csv')
        df = df.append(df_tmp)
        
        print(df)
        
        ax_psnr = sns.barplot(x='camera_position', y='psnr_mean', hue='synthesizer', data = df)
        ax_psnr.set_title(f'{scene}_psnr')
        plt.show()

        ax_ssim = sns.barplot(x='camera_position', y='ssim_mean', hue='synthesizer', data = df)
        ax_ssim.set_title(f'{scene}_ssim')
        plt.show()

        ax_vmaf = sns.barplot(x='camera_position', y='vmaf_mean', hue='synthesizer', data = df)
        ax_vmaf.set_title(f'{scene}_vmaf')
        plt.show()

        ax_vmaf = sns.barplot(x='pose_traces', y='vmaf_mean', hue='camera_position', data = df)
        ax_vmaf.set_title(f'{scene}_vmaf')
        plt.show()


def main():
    # setup paras
    # camera_positions = np.array(["6x6", "9x4", "12x3", "18x2"])
    # scenes = np.array(['ArchVizInterior', 'LightroomInteriorDayLight', 'office', 'RealisticRendering', 'XoioBerlinFlat'])
    # QPs = np.array([44])
    # synthesizers = np.array(["AdditiveSynthesizer", "ViewWeightingSynthesizer"])
    # numGroups = np.array([1])
    # pose_traces = np.array([f'pose{i}' for i in range(10)])
    # numFrame = 1

    # 1
    camera_positions = np.array(["6x6", "sphere_6x6"])
    scenes = np.array(['RealisticRendering'])
    QPs = np.array([44])
    synthesizers = np.array(["AdditiveSynthesizer", "ViewWeightingSynthesizer"])
    numGroups = np.array([1])
    pose_traces = np.array([f'pose{i}' for i in range(10)])
    numFrame = 1

    scene_plot(camera_positions, scenes, QPs, synthesizers, numGroups, pose_traces, numFrame)


if __name__ == '__main__':
    main()