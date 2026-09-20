import pytest
from app.services.scheduler_service import SchedulerService

def test_ortools_cp_sat_optimization():
    scheduler = SchedulerService()
    scenes = [
        {"scene_number": 1, "location_name": "LAB", "estimated_duration_minutes": 90, "characters": ["ELENA", "MARCUS"], "time_of_day": "DAY"},
        {"scene_number": 2, "location_name": "LAB", "estimated_duration_minutes": 120, "characters": ["ELENA"], "time_of_day": "DAY"},
        {"scene_number": 3, "location_name": "ROOFTOP", "estimated_duration_minutes": 150, "characters": ["MARCUS", "CHEN"], "time_of_day": "NIGHT"},
        {"scene_number": 4, "location_name": "ROOFTOP", "estimated_duration_minutes": 90, "characters": ["CHEN"], "time_of_day": "NIGHT"},
        {"scene_number": 5, "location_name": "HARBOR", "estimated_duration_minutes": 180, "characters": ["ELENA", "HAYES"], "time_of_day": "DAY"},
    ]

    result = scheduler.optimize_schedule(scenes, max_daily_hours=8.0)
    
    assert result["optimization_status"] in ["OPTIMAL", "FEASIBLE"]
    assert result["total_days"] >= 1
    assert result["total_hours"] > 0
    assert len(result["shooting_days"]) == result["total_days"]
    
    # Check that all scenes are scheduled
    scheduled_scene_numbers = []
    for day in result["shooting_days"]:
        for sc in day["scheduled_scenes"]:
            scheduled_scene_numbers.append(sc["scene_number"])
    
    assert set(scheduled_scene_numbers) == {1, 2, 3, 4, 5}
