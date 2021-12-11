
import os
import pandas as pd
import numpy as np
import subprocess
from subprocess import run

GT_path = '/mnt/data3/syjintw/TMIV_move_0/TMIV/dynamic_dataset/dynamic/random_trace_ground_truth/RealisticRendering/1_GT_texture_1280x720_yuv420p10le.yuv'

def psnr_ssim_vmaf(i, camera, QP, vmaf_trigger=0):
    """Get PSNR SSIM VMAF by vmaf

    Calculate PSNR, SSIM and VMAF by decoding source and ground truth.
    Run VMAF first and store the results to a csv file.
    Then, we read the csv file and get the PSNR, SSIM and VMAF value.
    Return three values.
    """
    
    if vmaf_trigger == 1:
        if not os.path.exists(f'./psnr'):
            os.system(f"mkdir ./psnr")

        os.system(f'vmaf \
                    --reference {GT_path} \
                    --distorted /mnt/data3/syjintw/TMIV_move_{i}/TMIV/decoder_output/move_{camera}_rec{QP}_90.yuv \
                    --width 1280 --height 720 --pixel_format 420 --bitdepth 10 \
                    --model version=vmaf_v0.6.1 \
                    --feature psnr \
                    --feature float_ssim \
                    --o ./psnr/move_{camera}_rec{QP}_psnr.csv --csv')
    
    df = pd.read_csv(f"./psnr/move_{camera}_rec{QP}_psnr.csv")
    return df['psnr_y'].mean(), df['float_ssim'].mean(), df['vmaf'].mean()

def parse_time_from_TMIV_log(log_path):
    # parse time in TMIV encode/decode log
    log = []
    with open(log_path, 'r') as f:
        log = f.readlines()
    for line in log:
        if("Total Time:" in line):
            return float(line.split()[2])

def parse_time_from_x265_log(log_path, isEncode):
    # parse time in x265 log
    log = []
    keyword = ""
    if(isEncode):
        keyword = "Encoding"
    else:
        keyword = "Decoding"

    with open(log_path, 'r') as f:
        log = f.readlines()
    for line in log:
        if(f"{keyword} Total Time:" in line):
            return float(line.split()[3])

def get_folder_size(camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num):
    # output unit: bits
    size = 0
    # geo
    for index in range(3):
        path = f'/mnt/data3/syjintw/TMIV_move_{index}/TMIV/x265_encoder_output'

    for i in range(2):
        folder_path = f'{path}/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/TMIV_nF{numFrame}_{camera_position}_{scene}_geo_c0{i}_640x3480_yuv420p10le.bit'
        process = run(['du', '-b', folder_path], capture_output=True, text=True)
        size = size + int(process.stdout.split()[0])
    # tex
    for i in range(2):
        folder_path = f'../x265_encoder_output/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/TMIV_nF{numFrame}_{camera_position}_{scene}_tex_c0{i}_1280x6960_yuv420p10le.bit'
        process = run(['du', '-b', folder_path], capture_output=True, text=True)
        size = size + int(process.stdout.split()[0])
    return int(size)*8

def codec_time(camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num):
    # TMIV encoding time
    TMIV_encoding_log = f"../log/TMIV_encoder/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/TMIV_nF{numFrame}_{camera_position}_{scene}.log"
    TMIV_encoding_time = parse_time_from_TMIV_log(TMIV_encoding_log)
    # TMIV decoding time
    TMIV_decoding_log = f"../log/TMIV_decoder/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/{camera_position}_{scene}_QP{QP}_{synthesizer}_pose{pose_trace_num}.log"
    TMIV_decoding_time = parse_time_from_TMIV_log(TMIV_decoding_log)
    # x265 encoding time    
    x265_encoding_log = f"../log/x265_encoder/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/TMIV_nF{numFrame}_{camera_position}_{scene}_time.log"
    x265_encoding_time = parse_time_from_x265_log(x265_encoding_log, 1)
    # x265 decoding time    
    x265_decoding_log = f"../log/x265_decoder/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/TMIV_nF{numFrame}_{camera_position}_{scene}_time.log"
    x265_decoding_time = parse_time_from_x265_log(x265_decoding_log, 0)
    return TMIV_encoding_time, TMIV_decoding_time, x265_encoding_time, x265_decoding_time
    
def main():
    # setup paras
    # camera_positions = np.array(["6x6", "9x4", "12x3", "18x2"])
    # scenes = np.array(['ArchVizInterior', 'LightroomInteriorDayLight', 'office', 'RealisticRendering', 'XoioBerlinFlat'])
    # QPs = np.array([20, 36, 44, 48, 50])
    # synthesizers = np.array(["AdditiveSynthesizer", "ViewWeightingSynthesizer"])
    # numGroups = np.array([1])
    # pose_traces = np.array([f'pose{i}' for i in range(10)])
    # numFrame = 1

    # test
    cameras = ['6x6', '9x4', '12x3']
    QPs = np.array([20, 36, 44, 48, 50])

    # create dir
    if not os.path.exists('./results'):
        os.system(f"mkdir ./results")

    for i in range(3):
        for QP in QPs:
            psnr_mean, ssim_mean, vmaf_mean = psnr_ssim_vmaf(i, cameras[i], QP, vmaf_trigger=1)
    
    # datas = []
    # datas.append(
    #     ['synthesizer', 'camera_position', 'scene', 'pose_traces', 'QP', 'numGroup', 'psnr_mean', 'ssim_mean', 'vmaf_mean', 'TMIV_encoding_time', 'TMIV_decoding_time', 'x265_encoding_time', 'x265_decoding_time', 'bitrate'])
    # for scene in scenes:
    #     for camera_position in camera_positions:
    #         if camera_position == 'sphere_6x6' and scene in ['ArchVizInterior', 'LightroomInteriorDayLight', 'office', 'XoioBerlinFlat']:
    #             continue
    #         for QP in QPs:
    #             for synthesizer in synthesizers:
    #                 for numGroup in numGroups:
    #                     for pose_trace_num in range(np.size(pose_traces)):
    #                         psnr_mean, ssim_mean, vmaf_mean = psnr_ssim_vmaf(
    #                             camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num, 1)
    #                         TMIV_encoding_time, TMIV_decoding_time, x265_encoding_time, x265_decoding_time = codec_time(
    #                             camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num)
    #                         bitrate = get_folder_size(
    #                             camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num)
    #                         data = [synthesizer, camera_position, scene, pose_traces[pose_trace_num], QP, numGroup, psnr_mean, ssim_mean, vmaf_mean, TMIV_encoding_time, TMIV_decoding_time, x265_encoding_time, x265_decoding_time, bitrate]
    #                         # print(data)
    #                         datas.append(data)
    # df = pd.DataFrame(data=datas)
    # df.to_csv(f"./results/all_nG1.csv", index=False, header=False)
    
if __name__ == '__main__':
    main()