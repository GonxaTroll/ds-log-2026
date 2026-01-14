"""main.py
Script for running optimizer.
"""
import time
from src.models.milp_solver import FashionSolver

def main():
    t1 = time.time()
    solver = FashionSolver(
        slots=1,
        unavailable_times = [list(range(1, 13+1)) + list(range(15, 17))]
    )
    t2 = time.time()
    solver.solve()
    t3 = time.time()
    print(f"Time to initialize the solver: {t2-t1}")
    print(f"Time to solve: {t3-t2}")
    print(solver.get_best_product_choice())


if __name__ == "__main__":
    main()
