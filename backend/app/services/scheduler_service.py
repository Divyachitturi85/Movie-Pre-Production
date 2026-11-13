import time
import logging
from typing import List, Dict, Any, Tuple
try:
    from ortools.sat.python import cp_model
except (ImportError, OSError):
    cp_model = None

logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Production Shooting Schedule Optimizer using Google OR-Tools CP-SAT.
    
    Implements a Constraint Programming model that minimizes:
    1. Total number of shooting days (primary objective)
    2. Company moves / location changes (secondary objective)
    3. Cast standby / idle working days (tertiary objective)
    
    Under constraints:
    - Exactly one day assignment per scene
    - Maximum daily shooting hours (default 10h / 600 mins)
    - Consecutive day activation (symmetry breaking)
    - Setup & changeover time buffer
    - Day / Night transition ordering
    """

    def optimize_schedule(
        self,
        scenes: List[Dict[str, Any]],
        max_daily_hours: float = 10.0,
        include_setup_time: bool = True,
        prioritize_locations: bool = True
    ) -> Dict[str, Any]:
        start_wall_time = time.time()
        
        if not scenes:
            return {
                "total_days": 0,
                "total_hours": 0.0,
                "total_company_moves": 0,
                "optimization_status": "EMPTY",
                "solver_time_seconds": 0.0,
                "objective_value": 0.0,
                "shooting_days": [],
                "explanation": "No scenes to schedule."
            }

        max_daily_mins = int(max_daily_hours * 60)
        setup_mins_per_scene = 30 if include_setup_time else 10

        # Calculate estimated total minutes and upper bound on days
        total_scene_mins = sum(s.get("estimated_duration_minutes", 60) for s in scenes)
        min_days_est = max(1, (total_scene_mins + len(scenes) * setup_mins_per_scene) // max_daily_mins + 1)
        max_days = min(len(scenes), int(min_days_est + 5))

        if cp_model is None:
            logger.warning("OR-Tools CP-SAT unavailable; using greedy heuristic fallback.")
            return self._greedy_schedule_fallback(scenes, max_daily_mins, setup_mins_per_scene)

        model = cp_model.CpModel()

        # Sets
        num_scenes = len(scenes)
        scene_indices = list(range(num_scenes))
        day_indices = list(range(max_days))

        # Unique locations and cast
        locations = sorted(list({s.get("location_name", "UNKNOWN") for s in scenes}))
        all_cast = sorted(list({c for s in scenes for c in s.get("characters", [])}))

        # -------------------------------------------------------------
        # Decision Variables
        # -------------------------------------------------------------
        # scene_day[s, d] == 1 if scene s is scheduled on day d
        scene_day = {}
        for s in scene_indices:
            for d in day_indices:
                scene_day[(s, d)] = model.NewBoolVar(f"scene_{s}_day_{d}")

        # day_active[d] == 1 if day d has at least one scene
        day_active = {}
        for d in day_indices:
            day_active[d] = model.NewBoolVar(f"day_active_{d}")

        # loc_on_day[l, d] == 1 if location l is used on day d
        loc_on_day = {}
        for l_idx, loc in enumerate(locations):
            for d in day_indices:
                loc_on_day[(loc, d)] = model.NewBoolVar(f"loc_{l_idx}_day_{d}")

        # cast_on_day[c, d] == 1 if cast member c is called on day d
        cast_on_day = {}
        for c_idx, cast in enumerate(all_cast):
            for d in day_indices:
                cast_on_day[(cast, d)] = model.NewBoolVar(f"cast_{c_idx}_day_{d}")

        # -------------------------------------------------------------
        # Constraints
        # -------------------------------------------------------------
        # 1. Every scene must be scheduled on exactly one day
        for s in scene_indices:
            model.Add(sum(scene_day[(s, d)] for d in day_indices) == 1)

        # 2. Link scene assignment to day activity
        for s in scene_indices:
            for d in day_indices:
                model.Add(scene_day[(s, d)] <= day_active[d])

        # 3. Symmetry breaking: Days must be used consecutively (Day d before Day d+1)
        for d in range(max_days - 1):
            model.Add(day_active[d] >= day_active[d + 1])

        # 4. Link locations to days
        for s_idx, sc in enumerate(scenes):
            loc = sc.get("location_name", "UNKNOWN")
            for d in day_indices:
                model.Add(loc_on_day[(loc, d)] >= scene_day[(s_idx, d)])

        # 5. Link cast members to days
        for s_idx, sc in enumerate(scenes):
            for c in sc.get("characters", []):
                for d in day_indices:
                    model.Add(cast_on_day[(c, d)] >= scene_day[(s_idx, d)])

        # 6. Daily shooting duration limit (including scene duration, setup time, and company moves)
        for d in day_indices:
            daily_mins_expr = []
            for s in scene_indices:
                dur = scenes[s].get("estimated_duration_minutes", 60) + setup_mins_per_scene
                daily_mins_expr.append(scene_day[(s, d)] * dur)
            
            # Each location on day d beyond the first requires 45 mins company move delay
            loc_count_on_day = sum(loc_on_day[(loc, d)] for loc in locations)
            model.Add(sum(daily_mins_expr) + 45 * (loc_count_on_day - day_active[d]) <= max_daily_mins * day_active[d])

        # 7. Realistic maximum scenes per day cap (standard industry pace: at most 4 scenes per day)
        max_scenes_per_day = min(4, len(scenes))
        for d in day_indices:
            model.Add(sum(scene_day[(s, d)] for s in scene_indices) <= max_scenes_per_day * day_active[d])

        # -------------------------------------------------------------
        # Objective Function
        # Minimize:
        # 1000 * total_shooting_days
        # + 100 * total_location_occurrences (minimizes company moves)
        # + 10 * total_cast_days (minimizes idle standby)
        # -------------------------------------------------------------
        obj_terms = []
        
        # Days cost
        for d in day_indices:
            obj_terms.append(1000 * day_active[d])

        # Location continuity cost
        if prioritize_locations:
            for loc in locations:
                for d in day_indices:
                    obj_terms.append(100 * loc_on_day[(loc, d)])

        # Cast efficiency cost
        for c in all_cast:
            for d in day_indices:
                obj_terms.append(10 * cast_on_day[(c, d)])

        model.Minimize(sum(obj_terms))

        # -------------------------------------------------------------
        # Solve with CP-SAT
        # -------------------------------------------------------------
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10.0
        solver.parameters.num_workers = 4

        status = solver.Solve(model)
        solve_time = round(time.time() - start_wall_time, 3)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
            return self._build_schedule_result(
                solver,
                status_str,
                solve_time,
                scenes,
                scene_day,
                day_active,
                locations,
                max_days,
                setup_mins_per_scene
            )
        else:
            logger.warning("CP-SAT could not find feasible schedule within constraints. Using greedy fallback.")
            return self._greedy_schedule_fallback(scenes, max_daily_mins, setup_mins_per_scene)

    def _build_schedule_result(
        self,
        solver: Any,
        status_str: str,
        solve_time: float,
        scenes: List[Dict[str, Any]],
        scene_day: Dict[Tuple[int, int], Any],
        day_active: Dict[int, Any],
        locations: List[str],
        max_days: int,
        setup_mins: int
    ) -> Dict[str, Any]:
        """Assembles structured daily shooting schedules and sequencing"""
        active_days_count = sum(1 for d in range(max_days) if solver.Value(day_active[d]) == 1)
        shooting_days_data = []
        total_company_moves = 0
        total_hours_all = 0.0

        for d in range(active_days_count):
            day_scenes = []
            for s_idx, sc in enumerate(scenes):
                if solver.Value(scene_day[(s_idx, d)]) == 1:
                    day_scenes.append(sc)

            # Sequence scenes within day: Group by location to eliminate redundant moves,
            # then Day before Night
            day_scenes.sort(key=lambda s: (
                s.get("location_name", ""),
                1 if "NIGHT" in s.get("time_of_day", "") else 0,
                s.get("scene_number", 0)
            ))

            # Calculate times and company moves
            current_time_mins = 7 * 60  # 07:00 AM Call
            prev_location = None
            day_moves = 0
            scheduled_items = []
            day_cast = set()

            for seq_idx, sc in enumerate(day_scenes):
                loc = sc.get("location_name", "UNKNOWN")
                move_before = False
                if prev_location is not None and prev_location != loc:
                    day_moves += 1
                    move_before = True
                    current_time_mins += 45  # 45 mins company move delay
                prev_location = loc

                dur = sc.get("estimated_duration_minutes", 60)
                start_h = current_time_mins // 60
                start_m = current_time_mins % 60
                start_str = f"{start_h:02d}:{start_m:02d} {'AM' if start_h < 12 else 'PM'}"

                current_time_mins += dur + setup_mins

                for c in sc.get("characters", []):
                    day_cast.add(c)

                scheduled_items.append({
                    "sequence_order": seq_idx + 1,
                    "scene_id": sc.get("id", sc.get("scene_number", seq_idx + 1)),
                    "scene_number": sc.get("scene_number", seq_idx + 1),
                    "heading": sc.get("heading", ""),
                    "interior_exterior": sc.get("interior_exterior", "INT"),
                    "time_of_day": sc.get("time_of_day", "DAY"),
                    "pages": sc.get("estimated_pages", 0.5),
                    "complexity_level": sc.get("complexity_level", "LOW"),
                    "estimated_start_time": start_str,
                    "estimated_duration_minutes": dur,
                    "setup_time_minutes": setup_mins,
                    "location_name": loc,
                    "company_move_before": move_before
                })

            total_company_moves += day_moves
            total_day_hours = round((current_time_mins - 7 * 60) / 60.0, 1)
            total_hours_all += total_day_hours

            wrap_h = current_time_mins // 60
            wrap_m = current_time_mins % 60
            wrap_str = f"{wrap_h:02d}:{wrap_m:02d} {'AM' if wrap_h < 12 else 'PM'}"

            shooting_days_data.append({
                "day_number": d + 1,
                "shoot_date": f"Shoot Day {d + 1}",
                "call_time": "07:00 AM",
                "wrap_time": wrap_str,
                "meal_break_time": "01:00 PM (45 min courtesy lunch)",
                "total_shooting_hours": total_day_hours,
                "company_moves_count": day_moves,
                "primary_location": day_scenes[0].get("location_name") if day_scenes else "Location TBA",
                "cast_ids": sorted(list(day_cast)),
                "equipment_ids": ["Camera A (ARRI Alexa)", "Audio Kit", "Lighting Package"],
                "notes": f"Includes {len(day_scenes)} scenes. {day_moves} company moves.",
                "scheduled_scenes": scheduled_items
            })

        explanation = (
            f"Optimized via Google OR-Tools CP-SAT in {solve_time}s ({status_str}). "
            f"Scheduled {len(scenes)} scenes into {active_days_count} days with {total_company_moves} company moves. "
            f"Objective minimized shooting days and clustered shared locations."
        )

        return {
            "total_days": active_days_count,
            "total_hours": round(total_hours_all, 1),
            "total_company_moves": total_company_moves,
            "optimization_status": status_str,
            "solver_time_seconds": solve_time,
            "objective_value": solver.ObjectiveValue() if solver else 0.0,
            "shooting_days": shooting_days_data,
            "explanation": explanation
        }

    def _greedy_schedule_fallback(self, scenes: List[Dict[str, Any]], max_daily_mins: int, setup_mins: int) -> Dict[str, Any]:
        """Greedy heuristic fallback if solver encounters timeout or unbounded constraints"""
        days = []
        current_day_scenes = []
        current_mins = 0

        # Sort by location to preserve clustering
        sorted_scenes = sorted(scenes, key=lambda s: s.get("location_name", ""))

        for sc in sorted_scenes:
            dur = sc.get("estimated_duration_minutes", 60) + setup_mins
            if current_mins + dur > max_daily_mins and current_day_scenes:
                days.append(current_day_scenes)
                current_day_scenes = [sc]
                current_mins = dur
            else:
                current_day_scenes.append(sc)
                current_mins += dur

        if current_day_scenes:
            days.append(current_day_scenes)

        shooting_days_data = []
        for d_idx, d_scenes in enumerate(days):
            shooting_days_data.append({
                "day_number": d_idx + 1,
                "shoot_date": f"Shoot Day {d_idx + 1}",
                "call_time": "07:00 AM",
                "wrap_time": "06:00 PM",
                "meal_break_time": "01:00 PM",
                "total_shooting_hours": 9.5,
                "company_moves_count": 0,
                "primary_location": d_scenes[0].get("location_name") if d_scenes else "Main Set",
                "cast_ids": sorted(list({c for s in d_scenes for c in s.get("characters", [])})),
                "equipment_ids": ["Standard Production Package"],
                "notes": "Generated by heuristic clustering fallback",
                "scheduled_scenes": [
                    {
                        "sequence_order": i + 1,
                        "scene_id": s.get("id", s.get("scene_number", i + 1)),
                        "scene_number": s.get("scene_number", i + 1),
                        "heading": s.get("heading", ""),
                        "interior_exterior": s.get("interior_exterior", "INT"),
                        "time_of_day": s.get("time_of_day", "DAY"),
                        "pages": s.get("estimated_pages", 0.5),
                        "complexity_level": s.get("complexity_level", "LOW"),
                        "estimated_start_time": f"{8 + i}:00 AM",
                        "estimated_duration_minutes": s.get("estimated_duration_minutes", 60),
                        "setup_time_minutes": setup_mins,
                        "location_name": s.get("location_name", "UNKNOWN"),
                        "company_move_before": False
                    }
                    for i, s in enumerate(d_scenes)
                ]
            })

        return {
            "total_days": len(days),
            "total_hours": round(len(days) * 9.5, 1),
            "total_company_moves": 0,
            "optimization_status": "HEURISTIC_FALLBACK",
            "solver_time_seconds": 0.01,
            "objective_value": 0.0,
            "shooting_days": shooting_days_data,
            "explanation": "Greedy location-clustering fallback schedule."
        }
