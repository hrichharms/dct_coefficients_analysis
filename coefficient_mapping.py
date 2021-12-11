from json import load, dump
from sys import argv

# given the value of a secondary coefficient, what value should be the "one"
# value of the primary coefficient such that block distortion is minimized
# while keeping the error rate arbitrarily low

if __name__ == "__main__":

    # unpack command line arguments
    #   argv[1] -> filename of stats json to use : string
    #   argv[2] -> acceptable error rate : float in the range [0.0, 1.0]
    #   argv[3] -> coefficient correlation observed above this number is considered to be "natural" (vmax in sns.heatmap): integer
    #   argv[3] -> output filename : string
    try:
        stats_filename, acceptable_error, correlation_threshold, output_filename = argv[1:]
        acceptable_error = float(acceptable_error)
        correlation_threshold = int(correlation_threshold)
    except ValueError:
        print("ERROR: Too few or too many command line arguments!")
        exit()

    # load data from stats json file
    with open(stats_filename) as stats_file:
        coefficient_stats = load(stats_file)

    # calculate embeding differences for each channel
    embeding_differences = []
    for variation_hist in coefficient_stats["variation_hists"]:
        n = sum(coefficient_stats["variation_hists"][0])
        embeding_difference = 0
        while sum(variation_hist[:embeding_difference + 1]) / n < acceptable_error:
            embeding_difference += 1
        embeding_differences.append(embeding_difference)

    # calculate mapping for specified error rate using loaded coefficient statistics
    #   let coefficient_mappings[i][j] = some integer x such that, only in acceptable_error * 100 percent of cases does
    #                                    the following hold true: C[abs(x - v)][j] >= correlation_threshold where C is the
    #                                    correlation table observed in coefficient_stats["function_of_dct_2_hists"][i] and
    #                                    v is an integer representing the variation observed across video codecs
    #   Note: this description can probably be worded better with respect to the relationship between
    #         coefficient_mappings[i][j] and acceptable_error
    C = coefficient_stats["function_of_dct_2_hists"]
    natural_bounds = [[0] * 2048, [0] * 2048, [0] * 2048]
    coefficient_mappings = [[0] * 2048, [0] * 2048, [0] * 2048] # one mapping array per channel
    for i, mapping in enumerate(coefficient_mappings): # calculate channel mapping for each channel

        # iterate over independent coefficient
        for j in range(2040):

            # try to find lower and upper bounds of "natural" values for current coefficient value
            #   Note: this could be faster if needed by starting at the previous value's calculated
            #         bounds but I don't feel like implementing/testing that right now.
            natural_lower = 0
            natural_upper = 2047
            try:
                while C[i][natural_lower + 1][j] < correlation_threshold:
                    natural_lower += 1
                while C[i][natural_upper - 1][j] < correlation_threshold:
                    natural_upper -= 1
            except IndexError:
                natural_lower = -1
                natural_upper = -1

            # calculate and record mapping output
            #   Note: right now the mapping output is calculated "safely" by using the bound with the
            #         highest magnitude. There are non-zero perceptibility gains to be made by calculating
            #         mapping outputs for both the lower and upper bounds individually.
            natural_bound = max(abs(1024 - natural_lower), abs(1024 - natural_upper))
            mapping[j] = natural_bound + embeding_differences[i]
            if natural_lower == -1 and natural_upper == -1: # if natural bounds could not be found
                mapping[j] = -1
            natural_bounds[i][j] = natural_bound

    # write calculated mappings to output file
    with open(output_filename, "w") as output_file:
        dump({
            "natural_bounds": natural_bounds,
            "coefficient_mappings": coefficient_mappings
        }, output_file)
