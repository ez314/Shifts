import time
import random
from typing import Optional

NUM_UNITS = 672
SHIFT_LENGTH = 24
MIN_AVAILABILITY = 1
MAX_AVAILABILITY = 8

NUM_TESTS = 100


def generate_units():
    return [random.randint(MIN_AVAILABILITY, MAX_AVAILABILITY) for _ in range(NUM_UNITS)]


def find_first_possible_shift(units: list[int], search_start=0) -> Optional[int]:
    for i in range(search_start, NUM_UNITS - SHIFT_LENGTH + 1):
        if all(units[i + j] > 0 for j in range(SHIFT_LENGTH)):
            return i
    return None


def remove_shifts(units: list[int], shift_start: int, num_shifts: int) -> list[int]:
    """
    Return remaining availability after removing `num_shifts` shifts beginning at `shift_start`
    """
    return [(val - num_shifts) if (shift_start <= j < (shift_start + SHIFT_LENGTH)) else val
            for j, val in enumerate(units)]


def solve_dfs(units: list[int], search_start=0) -> int:
    """
    Correct algorithm, tries every possibility
    """
    # Find the earliest available shift's start index
    shift_start = find_first_possible_shift(units, search_start)

    # If no consecutive block found, there are no shifts - return 0
    if shift_start is None:
        return 0

    # Find the bottleneck (how many shifts can we pull out of this block?)
    max_num_shifts = min(units[shift_start:shift_start+SHIFT_LENGTH])

    # Loop through all possible numbers of shifts we can pull out of this block
    best = 0
    for num_shifts in range(max_num_shifts + 1):
        # Remove that number of shifts from the block
        new_units = remove_shifts(units, shift_start, num_shifts)
        # Add the shifts we removed to the solution of the sub-problem
        subproblem_solution = solve_dfs(new_units, shift_start + 1) + num_shifts
        best = max(best, subproblem_solution)

    # Return best solution out of all branches
    return best


def solve_greedy(units: list[int], search_start=0) -> int:
    """
    Correct and optimal algorithm, greedily takes first available shift
    """
    # Find the earliest available shift's start index
    shift_start = find_first_possible_shift(units, search_start)

    # If no consecutive block found, there are no shifts - return 0
    if shift_start is None:
        return 0

    # Remove as many shifts as possible from this block
    max_num_shifts = min(units[shift_start:shift_start+SHIFT_LENGTH])
    new_units = remove_shifts(units, shift_start, max_num_shifts)

    # Add the shifts we just removed to the solution of the subproblem
    return solve_greedy(new_units, shift_start + 1) + max_num_shifts


def main():
    for i in range(NUM_TESTS):
        units = generate_units()
        t1 = time.time()
        dfs_solution = solve_dfs(units)
        t2 = time.time()
        greedy_solution = solve_greedy(units)
        t3 = time.time()

        if dfs_solution != greedy_solution:
            print(f'Different solutions: DFS got {dfs_solution} while greedy got {greedy_solution}')
            print(f'Units: {units}')
            break
        else:
            time_dfs = t2 - t1
            time_greedy = t3 - t2
            speedup = round(time_dfs / time_greedy)
            print(f'Solutions same ({greedy_solution})\tdfs:{time_dfs:.2f}s greedy:{time_greedy:.2f}s speedup:{speedup}x')
    else:
        print(f'No differences found after running {NUM_TESTS} tests')


if __name__ == '__main__':
    main()
