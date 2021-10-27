import os
import pandas as pd
import numpy as np
import subprocess
from subprocess import run

def psnr_ssim_vmaf(camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num, vmaf_trigger, trigger):
    """Get PSNR SSIM VMAF by vmaf

    Calculate PSNR, SSIM and VMAF by decoding source and ground truth.
    Run VMAF first and store the results to a csv file.
    Then, we read the csv file and get the PSNR, SSIM and VMAF value.
    Return three values.
    """
    if trigger == 0:
        return 0, 0, 0
    
    if vmaf_trigger == 1:
        if os.path.exists(f'./psnr'):
            os.system(f"mkdir ./psnr")
        if os.path.exists(f'./psnr/{synthesizer}'):
            os.system(f"mkdir ./psnr/{synthesizer}")

        print(f"{camera_position}_{scene}_rec{QP}_{synthesizer}_pose{pose_trace_num}")
        os.system(f'vmaf \
                    --reference ../GT/{scene}/{pose_trace_num}_GT_texture_1280x720_yuv420p10le.yuv \
                    --distorted ../decoder_output/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/{camera_position}_{scene}_rec{QP}_{synthesizer}_pose{pose_trace_num}_texture_1280x720_yuv420p10le.yuv \
                    --width 1280 --height 720 --pixel_format 420 --bitdepth 10 \
                    --model version=vmaf_v0.6.1 \
                    --feature psnr \
                    --feature float_ssim \
                    --o ./psnr/{synthesizer}/{camera_position}_{scene}_rec{QP}_{synthesizer}_pose{pose_trace_num}_psnr.csv --csv')
    
    df = pd.read_csv(f"./psnr/{synthesizer}/{camera_position}_{scene}_rec{QP}_{synthesizer}_pose{pose_trace_num}_psnr.csv")
    return df['psnr_cr'].mean(), df['float_ssim'].mean(), df['vmaf'].mean()

def parse_time_from_TMIV_log(log_path, trigger=0):
    if trigger == 0:
        return 0
    # parse time in TMIV encode/decode log
    log = []
    with open(log_path, 'r') as f:
        log = f.readlines()
    for line in log:
        if("Total Time:" in line):
            return float(line.split()[2])

def parse_time_from_x265_log(log_path, isEncode, trigger):
    if trigger == 0:
        return 0
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

def get_folder_size(camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num, trigger):
    if trigger == 0:
        return 0
    # output unit: bits
    size = 0
    # geo
    for i in range(2):
        folder_path = f'../x265_encoder_output/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/TMIV_nF{numFrame}_{camera_position}_{scene}_geo_c0{i}_640x3480_yuv420p10le.bit'
        process = run(['du', '-b', folder_path], capture_output=True, text=True)
        size = size + int(process.stdout.split()[0])
    # tex
    for i in range(2):
        folder_path = f'../x265_encoder_output/{camera_position}_{scene}/nG{numGroup}/rec_{QP}/TMIV_nF{numFrame}_{camera_position}_{scene}_tex_c0{i}_1280x6960_yuv420p10le.bit'
        process = run(['du', '-b', folder_path], capture_output=True, text=True)
        size = size + int(process.stdout.split()[0])
    return int(size)*8


def codec_time(camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num, trigger):
    if trigger == 0:
        return 0, 0, 0, 0
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
    # QPs = np.array([44])
    # synthesizers = np.array(["AdditiveSynthesizer", "ViewWeightingSynthesizer"])
    # numGroups = np.array([1])
    # pose_traces = np.array([f'pose{i}' for i in range(10)])
    # numFrame = 1

    # test
    camera_positions = np.array(["6x6", "9x4", "12x3", "18x2"])
    scenes = np.array(['ArchVizInterior', 'LightroomInteriorDayLight', 'office', 'RealisticRendering', 'XoioBerlinFlat'])
    QPs = np.array([20, 36, 44, 48, 50])
    synthesizers = np.array(["AdditiveSynthesizer", "ViewWeightingSynthesizer"])
    numGroups = np.array([1])
    pose_traces = np.array([f'pose{i}' for i in range(10)])
    numFrame = 1

    # create dir
    if not os.path.exists('./results'):
        os.system(f"mkdir ./results")
    
    datas = []
    datas.append(
        ['synthesizer', 'camera_position', 'scene', 'pose_traces', 'QP', 'numGroup', 'psnr_mean', 'ssim_mean', 'vmaf_mean', 'TMIV_encoding_time', 'TMIV_decoding_time', 'x265_encoding_time', 'x265_decoding_time', 'bitrate'])
    for scene in scenes:
        for camera_position in camera_positions:
            for QP in QPs:
                for synthesizer in synthesizers:
                    for numGroup in numGroups:
                        for pose_trace_num in range(np.size(pose_traces)):
                            psnr_mean, ssim_mean, vmaf_mean = psnr_ssim_vmaf(
                                camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num, 0, 1)
                            TMIV_encoding_time, TMIV_decoding_time, x265_encoding_time, x265_decoding_time = codec_time(
                                camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num, 0)
                            bitrate = get_folder_size(
                                camera_position, scene, QP, synthesizer, numGroup, numFrame, pose_trace_num, 0)
                            data = [synthesizer, camera_position, scene, pose_traces[pose_trace_num], QP, numGroup, psnr_mean, ssim_mean, vmaf_mean, TMIV_encoding_time, TMIV_decoding_time, x265_encoding_time, x265_decoding_time, bitrate]
                            # print(data)
                            datas.append(data)
    df = pd.DataFrame(data=datas)
    df.to_csv(f"./results/all_results.csv", index=False, header=False)
    
if __name__ == '__main__':
    main()