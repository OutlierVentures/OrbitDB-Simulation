import sys
from itertools import combinations

sys.path.append("../../..")

from network_simulator.run import run
from network_simulator.batch_processor import simulation_paramters

def main():

    print("Carrying out model comparison")
    l = list(combinations(range(17), 2))

    redo = [81, 86]
    combo_idx = redo[int(sys.argv[1])]

    l = [l[combo_idx]]

    # l = [l[int(sys.argv[1])]]

    comp = Classification()
    comp.run_model_comparison_for_fs_list(l, "6MWT_Combinations_Of_Two", rf_mlp=True, cnn=False)

    print("Successfully carried out model comparison")


if __name__ == '__main__':
    main()
