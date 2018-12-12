import numpy as np
import utils
from itertools import zip_longest
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict

import os.path

# plt.xkcd()


def build_line(group):
    returns_mean = []
    returns_std = []
    for i, samples in enumerate(zip_longest(*group.returns)):
        samples = [s for s in samples if s is not None]
        
        mean = np.mean(samples)
        std = np.std(samples)
        
        returns_mean.append(mean)
        returns_std.append(std)

    returns_mean = np.array(returns_mean)
    returns_std = np.array(returns_std)
    return pd.DataFrame([{"returns_mean": returns_mean, "returns_std": returns_std}])


def build_plot(env_name, selection_conditions: Dict =None, w=0.5):
    
    # experiments = []
    # for d in [0, 100, 500]:
    #     experiments += [
    #         {
    #             "returns": [d + round(200 -i) + np.random.randint(-50, 50) for i in range(1, np.random.randint(50, 180))],
    #             "seed": np.random.randint(0, 2000),
    #             "demonstration_value": d,
    #             "chunks": np.random.choice([0, 1, 2, 3, 4]),
    #             "eps_iterations": np.random.choice([0, 1, 2, 3, 4, 8, 10, 17])
    #         }
    #         for j in range(50)
    #     ]
    #
    # experiments = pd.DataFrame(experiments)

    experiments = utils.load_experiments(env_name)
    
    if selection_conditions is not None:
        for column, values in selection_conditions.items():
            experiments = experiments[experiments[column].isin(values)]
    
    experiments.demonstration_value.fillna("From Scratch", inplace=True)

    # print(experiments.groupby(by="demonstration_value").size())
    print(experiments[["demonstration_value", "train_length"]])
    
    statistics = experiments.groupby(by="demonstration_value").apply(build_line).reset_index()

    plt.figure()
    
    best_demostration = -100000
    
    for i, row in statistics.iterrows():
        
        try:
            v = float(row.demonstration_value)
            best_demostration = max(v, best_demostration)
        except ValueError:
            pass
        
        smooth = 30
        
        returns_mean, returns_std = row.returns_mean, row.returns_std
        plt.plot(utils.smooth(returns_mean, smooth), label=row.demonstration_value)
        
        plt.fill_between(np.arange(0, returns_mean.shape[0]-smooth+1), utils.smooth(returns_mean - w*returns_std, smooth), utils.smooth(returns_mean + w*returns_std, smooth), alpha=0.1)
    plt.legend(title="Demonstration Value")
    plt.title("Episodes' Returns during Training")
    plt.xlabel("Episode during training")
    plt.ylabel("Total Return in episode")

    if RANGE_Y is not None:
        plt.ylim(RANGE_Y)

    plt.hlines(best_demostration, xmin=0, xmax=300, linewidth=0.5, color='black', linestyles='--', label='optimal trajectory')
    plt.yticks(list(plt.yticks()[0]) + [best_demostration])
    
    dir = utils.build_data_dir(env_name)
    outfile = os.path.join(dir, "{}.svg".format(env_name))
    
    plt.draw()
    plt.savefig(outfile, format='svg', dpi=1000)
    plt.show()


# RANGE_Y = (-1000, 0)
RANGE_Y = None

# build_plot("Maze_(15,15,42,1.0,1.0)", {"chunks": [5, None], "eps_iterations": [10, None]})
build_plot("MountainCar-v0")
