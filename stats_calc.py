from cv2 import (
    VideoCapture,
    dct,
    split,
    CAP_PROP_FRAME_COUNT,
    CAP_PROP_FRAME_HEIGHT,
    CAP_PROP_FRAME_WIDTH
)
from numpy import int32, float32

from itertools import product
from os.path import join
from os import listdir
from json import dump
from sys import argv


if __name__ == "__main__":

    videos_dir = argv[1]
    dct_coefficient_1 = int(argv[2]), int(argv[3])
    dct_coefficient_2 = int(argv[4]), int(argv[5])

    # open video capture objects
    videos = [VideoCapture(join(videos_dir, filename)) for filename in listdir(videos_dir) if filename != ".DS_Store"]

    # check if all videos have same frame count
    n = int(videos[0].get(CAP_PROP_FRAME_COUNT))
    for video in videos[1:]:
        if video.get(CAP_PROP_FRAME_COUNT) != n:
            print("ERROR: Unequal frame count!")
            exit()

    # get frame shape
    frame_shape = (int(videos[0].get(CAP_PROP_FRAME_HEIGHT)), int(videos[0].get(CAP_PROP_FRAME_WIDTH)))

    # check if all videos have the same frame size
    if [1 for video in videos[1:] if video.get(CAP_PROP_FRAME_HEIGHT) != frame_shape[0] or video.get(CAP_PROP_FRAME_WIDTH) != frame_shape[1]]:
        print("ERROR: Video frame dimensions not compatible!")
        exit()

    # variation logging variables
    lowest_variation = [0, 0, 0]
    highest_variation = [0, 0, 0]
    variation_totals = [0, 0, 0]
    variation_hists = [[0] * 2048, [0] * 2048, [0] * 2048]
    block_count = 0

    # coefficient value logging variables
    lowest = 1e9
    highest = -1e9

    # correlation logging variables
    correlation_heatmap = [[[0] * 2048 for _j in range(2048)] for _i in range(3)]

    # iterate over video frames
    for frame_i in range(n):

        try:
            # read next frames from video capture objects
            reads = [video.read() for video in videos]
            rets = [i[0] for i in reads] # ugly
            frames = [i[1] for i in reads] # ugly

            # if last frame, break read loop
            if rets.count(False): break

            # split frames into channel arrays
            channels = [split(frame) for frame in frames]

            # iterate over 8x8 blocks and channel indexes
            for x, y in product(
                range(0, frame_shape[1], 8),
                range(0, frame_shape[0], 8)
            ):
                # calculate dct coefficients for current block of each frame
                x_upper = x + 8 if x + 8 < frame_shape[1] else None
                y_upper = y + 8 if y + 8 < frame_shape[0] else None
                dct_coefficients = [
                    [
                        int32(dct(
                            float32(frame_channels[i][y: y_upper, x: x_upper])
                        )).tolist()
                        for i in range(3)
                    ]
                    for frame_channels in channels
                ]

                # calculate variation of DCT_COEFFICIENT_1 in current block
                variations = [
                    abs(max(
                        dct_coefficients,
                        key=lambda x: x[channel_index][dct_coefficient_1[0]][dct_coefficient_1[1]]
                    )[channel_index][dct_coefficient_1[0]][dct_coefficient_1[1]] - min(
                        dct_coefficients,
                        key=lambda x: x[channel_index][dct_coefficient_1[0]][dct_coefficient_1[1]]
                    )[dct_coefficient_1[0]][dct_coefficient_1[1]][0])
                    for channel_index in range(3)
                ]

                # update variation logging variables
                for i, variation in enumerate(variations):
                    if variation < lowest_variation[i]:
                        lowest_variation[i] = variation
                    if variation > highest_variation[i]:
                        highest_variation[i] = variation
                    variation_totals[i] += variation
                    variation_hists[i][variation] += 1
                block_count += 1

                # update correlation and coefficient logging variables
                for dct_blocks in dct_coefficients:
                    for channel_index, channel_block in enumerate(dct_blocks):

                        correlation_heatmap[channel_index][1024 + channel_block[dct_coefficient_1[0]][dct_coefficient_1[1]]][1024 + channel_block[dct_coefficient_2[0]][dct_coefficient_2[1]]] += 1

                        if channel_block[dct_coefficient_1[0]][dct_coefficient_1[1]] < lowest:
                            lowest = channel_block[dct_coefficient_1[0]][dct_coefficient_1[1]]
                        if channel_block[dct_coefficient_1[0]][dct_coefficient_1[1]] > highest:
                            highest = channel_block[dct_coefficient_1[0]][dct_coefficient_1[1]]

            print(f"Progress {frame_i / n * 100:.2f}%")

        except KeyboardInterrupt:
            break

    coefficients_signature = "_".join([str(i) for i in dct_coefficient_1 + dct_coefficient_2])
    with open(f"stats/stats_{coefficients_signature}_{videos_dir}.json", "w") as output_file:
        dump({
            "lowest_variation": lowest_variation,
            "highest_variation": highest_variation,
            "variation_totals": variation_totals,
            "variation_hists": variation_hists,
            "lowest_val": lowest,
            "highest_val": highest,
            "block_count": block_count,
            "function_of_dct_2_hists": correlation_heatmap
        }, output_file)
