"""milp_solver.py
Mixed integer linear programming (MILP) solver code.
"""
import numpy as np
import pandas as pd
from ortools.linear_solver import pywraplp
from src.data.read_data import read_data


class FashionSolver:
    """Solver for optimizing fashion product scheduling using MILP.
    
    This class models a scheduling problem where products with different durations
    and benefits need to be assigned to time slots to maximize total benefit.
    
    Attributes:
        slots: Number of parallel slots available for scheduling.
        data: DataFrame containing product information (id, duration, benefit, etc.).
    """
    
    # Class constants
    HOURS_PER_DAY = 24
    DEFAULT_SOLVER = "SCIP"
    MIN_SLOT_COUNT = 1
    MIN_DAYS = 1
    
    def __init__(
        self, 
        slots: int = 1, 
        n_days_to_schedule: int = 1, 
        unavailable_times: list = None,
        solver_name: str = DEFAULT_SOLVER,
        data: pd.DataFrame = None
    ):
        """Initialize the FashionSolver.
        
        Args:
            slots: Number of parallel time slots available (must be >= 1).
            n_days_to_schedule: Number of days in the scheduling horizon (must be >= 1).
            unavailable_times: List of hour indices that cannot be used for scheduling.
            solver_name: Name of the MILP solver backend (default: "SCIP").
            data: Optional DataFrame with product catalog. If None, loads from read_data().
        
        Raises:
            ValueError: If slots < 1, n_days_to_schedule < 1, or solver cannot be created.
        """
        self._validate_inputs(slots, n_days_to_schedule)
        
        self._slots = slots
        self._n_days = n_days_to_schedule
        self._time_mapping = list(range(self.HOURS_PER_DAY * n_days_to_schedule))
        self._unavailable_times = unavailable_times if unavailable_times is not None else []

        # Data
        self._data = data if data is not None else read_data()
        self._data_records = {
            product["id"]: product
            for product in self._data.to_dict(orient='records')
        }

        # Related to solver
        self._solver = self._create_solver(solver_name)
        self._variables = {}
        self._is_solved = False
        
        # Initialize problem
        self._initialize_variables()
        self._initialize_problem()

    @property
    def slots(self) -> int:
        """Get the number of available time slots."""
        return self._slots
    
    @property
    def data(self) -> pd.DataFrame:
        """Get the product catalog data."""
        return self._data
    
    @property
    def is_solved(self) -> bool:
        """Check if the optimization problem has been solved."""
        return self._is_solved
    
    def _validate_inputs(self, slots: int, n_days: int) -> None:
        """Validate constructor inputs.
        
        Args:
            slots: Number of parallel slots.
            n_days: Number of days to schedule.
            
        Raises:
            ValueError: If inputs are invalid.
        """
        if slots < self.MIN_SLOT_COUNT:
            raise ValueError(f"slots must be >= {self.MIN_SLOT_COUNT}, got {slots}")
        if n_days < self.MIN_DAYS:
            raise ValueError(f"n_days_to_schedule must be >= {self.MIN_DAYS}, got {n_days}")
    
    def _create_solver(self, solver_name: str) -> pywraplp.Solver:
        """Create and return a MILP solver instance.
        
        Args:
            solver_name: Name of the solver backend.
            
        Returns:
            Initialized solver instance.
            
        Raises:
            ValueError: If solver cannot be created.
        """
        solver = pywraplp.Solver.CreateSolver(solver_name)
        if solver is None:
            raise ValueError(f"Could not create solver '{solver_name}'")
        return solver

    def _initialize_variables(self) -> None:
        """Initialize decision variables for the optimization problem.
        
        Creates binary variables for each valid combination of product, start time,
        and slot. A variable is created only if scheduling the product at that time
        doesn't exceed the horizon or conflict with unavailable times.
        """
        last_hour = max(self._time_mapping)
        
        for product_id, product_info in self._data_records.items():
            duration_hours = int(np.ceil(product_info["duration"]))
            
            for hour in self._time_mapping:
                finish_hour = hour + duration_hours - 1
                
                # Skip if product would extend beyond horizon or use unavailable times
                if self._is_invalid_time_window(hour, finish_hour, last_hour):
                    continue
                
                # Create variable for each slot
                for slot in range(1, self._slots + 1):
                    variable_id = self._create_variable_id(product_id, hour, slot)
                    self._variables[variable_id] = self._solver.BoolVar(
                        f"Product {product_id} at hour {hour} in slot {slot}"
                    )
    
    def _is_invalid_time_window(self, start_hour: int, finish_hour: int, last_hour: int) -> bool:
        """Check if a time window is invalid for scheduling.
        
        Args:
            start_hour: Start hour of the window.
            finish_hour: Finish hour of the window.
            last_hour: Last available hour in the horizon.
            
        Returns:
            True if the window is invalid, False otherwise.
        """
        if finish_hour > last_hour:
            return True
        if start_hour in self._unavailable_times or finish_hour in self._unavailable_times:
            return True
        return False
    
    @staticmethod
    def _create_variable_id(product_id: int, hour: int, slot: int) -> str:
        """Create a unique identifier for a decision variable.
        
        Args:
            product_id: Product identifier.
            hour: Starting hour.
            slot: Slot number.
            
        Returns:
            String identifier in format "productId_hour_slot".
        """
        return f"{product_id}_{hour}_{slot}"
    
    @staticmethod
    def _parse_variable_id(variable_id: str) -> tuple[int, int, int]:
        """Parse a variable ID string into its components.
        
        Args:
            variable_id: Variable identifier string.
            
        Returns:
            Tuple of (product_id, hour, slot).
        """
        parts = variable_id.split("_")
        return int(parts[0]), int(parts[1]), int(parts[2])

    def _initialize_problem(self) -> None:
        """Initialize the complete optimization problem (objective + constraints)."""
        self._initialize_objective()
        self._initialize_constraints()

    def _initialize_objective(self) -> None:
        """Set up the objective function to maximize total benefit.
        
        The objective maximizes the sum of benefits from all scheduled products.
        """
        objective_terms = []
        for variable_id, variable in self._variables.items():
            product_id = self._parse_variable_id(variable_id)[0]
            product_benefit = self._data_records[product_id]["benefit"]
            objective_terms.append(product_benefit * variable)
        
        self._solver.Maximize(sum(objective_terms))

    def _initialize_constraints(self) -> None:
        """Set up all optimization constraints.
        
        Creates non-overlapping constraints: ensures that for each slot,
        at most one product occupies any given hour. Each constraint ensures
        that products with overlapping time windows cannot be scheduled simultaneously.
        """
        last_hour = max(self._time_mapping)
        
        for product_id, product_info in self._data_records.items():
            duration = int(np.ceil(product_info["duration"]))
            
            for start_hour in self._time_mapping:
                base_variable_id = self._create_variable_id(product_id, start_hour, 1)
                
                # Skip if this product can't start at this hour in any slot
                if base_variable_id not in self._variables:
                    continue
                
                # Get all variables that would conflict in the time window
                finish_hour = min(start_hour + duration - 1, last_hour)
                conflicting_variable_ids = []
                
                for other_product_id in self._data_records:
                    for hour in range(start_hour, finish_hour + 1):
                        variable_id = self._create_variable_id(other_product_id, hour, 1)
                        if variable_id in self._variables:
                            conflicting_variable_ids.append(
                                (other_product_id, hour)
                            )
                
                # Add constraint for each slot independently
                for slot in range(1, self._slots + 1):
                    slot_variables = [
                        self._variables[self._create_variable_id(pid, h, slot)]
                        for pid, h in conflicting_variable_ids
                    ]
                    if slot_variables:
                        self._solver.Add(sum(slot_variables) <= 1)


    def solve(self) -> int:
        """Solve the optimization problem.
        
        Returns:
            Status code from the solver:
                - 0 (OPTIMAL): An optimal solution was found
                - 1 (FEASIBLE): A feasible solution was found
                - 2 (INFEASIBLE): No feasible solution exists
                - 3 (UNBOUNDED): The problem is unbounded
                - Other codes indicate solver errors
                
        Raises:
            RuntimeError: If the solver encounters an error.
        """
        status = self._solver.Solve()
        self._is_solved = True
        
        if status not in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            self._is_solved = False
            print(f"Warning: Solver returned status {status}")
        
        return status

    def get_best_product_choice(self) -> pd.DataFrame:
        """Retrieve the optimal product scheduling solution.
        
        Returns:
            DataFrame with columns: id, hour, slot, and all product attributes
            from the catalog (duration, benefit, revenue, cost, xp, etc.).
            
        Raises:
            RuntimeError: If solve() has not been called yet.
        """
        if not self._is_solved:
            raise RuntimeError("Problem has not been solved yet. Call solve() first.")
        
        scheduled_products = []
        for variable_id, variable in self._variables.items():
            if variable.solution_value() > 0:
                product_id, hour, slot = self._parse_variable_id(variable_id)
                scheduled_products.append({
                    "id": product_id,
                    "hour": hour,
                    "slot": slot
                })
        
        if not scheduled_products:
            return pd.DataFrame(columns=["id", "hour", "slot"])
        
        result_df = pd.DataFrame(scheduled_products)
        result_df = result_df.merge(self._data, on="id", how="left")
        
        return result_df
    
    def get_objective_value(self) -> float:
        """Get the objective value of the optimal solution.
        
        Returns:
            The total benefit achieved by the optimal schedule.
            
        Raises:
            RuntimeError: If solve() has not been called yet.
        """
        if not self._is_solved:
            raise RuntimeError("Problem has not been solved yet. Call solve() first.")
        
        return self._solver.Objective().Value()
    
    def __repr__(self) -> str:
        """String representation of the solver."""
        return (f"FashionSolver(slots={self._slots}, "
                f"days={self._n_days}, "
                f"products={len(self._data_records)}, "
                f"solved={self._is_solved})")
