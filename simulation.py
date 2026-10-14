import matplotlib.pyplot as plt
import random
from generator import gen_random_ref, gen_locality_ref, gen_custom_ref
from algorithms import FIFO, Optimal, ARB, CustomAlgorithm


def run_simulation(algorithm_class, ref_string, frames):
    algo = algorithm_class(frames) if algorithm_class != Optimal else algorithm_class(frames, ref_string) 
    for i, page in enumerate(ref_string):
        is_write = random.random() < 0.1 # 10%機率寫入
        algo.access_page(page, is_write=is_write)  

        if isinstance(algo, (ARB, CustomAlgorithm)) and i % 100 == 0 : #每100次存取後更新參考位元
            algo.periodic_shift()

    return algo.get_stats()


def main():
    frame_sizes = [30, 60, 90, 120, 150] #不同frame數
    reference_strings = {
        "Random": gen_random_ref(),
        "Locality": gen_locality_ref(),
        "Custom": gen_custom_ref()
    }

    algorithms = {
        "FIFO": FIFO,
        "Optimal": Optimal,
        "ARB": ARB,
        "Custom": CustomAlgorithm
    }

    results = {}

    for ref_name, ref_string in reference_strings.items(): #跑所有組合
        results[ref_name] = {}
        for algo_name, algo_class in algorithms.items():
            results[ref_name][algo_name] = []
            for frames in frame_sizes:
                print(f"跑 {algo_name} 在 {ref_name}, frames={frames}") #即時觀看進度
                pf, intr, writes = run_simulation(algo_class, ref_string, frames)
                results[ref_name][algo_name].append((pf, intr, writes))

    for ref_name in results:  #畫圖存檔
        for metric_idx, metric_name in enumerate(["Page Faults", "Interrupts", "Disk Writes"]):
            plt.figure()
            for algo_name in algorithms.keys():
                y = [results[ref_name][algo_name][i][metric_idx] for i in range(len(frame_sizes))] 
                plt.plot(frame_sizes, y, label=algo_name)
            plt.xlabel("Frames")
            plt.ylabel(metric_name)
            plt.title(f"{metric_name} vs Frames ({ref_name})")
            plt.legend()
            plt.savefig(f"{metric_name}_{ref_name}.png")
            plt.close()

    print("Done!")


if __name__ == "__main__":
    main()
