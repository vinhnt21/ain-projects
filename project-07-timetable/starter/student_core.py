"""Graded AI core for Project 07 (University Timetable Scheduler)."""

from __future__ import annotations

from typing import Dict, Optional, Tuple, List
from starter.loaders import candidate_domain

Choice = Tuple[str, str, str]  # (lecturer_id, room_id, slot_id)


def solve_csp(instance: dict, strategy: str = "naive") -> Optional[Dict[str, Choice]]:
    """Search for a legal assignment of every course to (lecturer, room, slot)."""
    
    courses = instance["courses"]
    
    # 1. Khởi tạo Domain cho từng môn học
    domains: Dict[str, List[Choice]] = {
        c_id: candidate_domain(c_id, instance) 
        for c_id in courses
    }
    
    # Nếu có môn học nào domain rỗng ngay từ đầu -> UNSAT
    if any(len(dom) == 0 for dom in domains.values()):
        return None

    assignment: Dict[str, Choice] = {}

    def is_consistent(course_id: str, choice: Choice, current_assignment: Dict[str, Choice]) -> bool:
        lec_id, room_id, slot_id = choice
        c_info = courses[course_id]
        c_cohorts = set(c_info.get("cohorts", []))
        
        for assigned_c_id, (a_lec, a_room, a_slot) in current_assignment.items():
            if a_slot == slot_id:
                # Kiểm tra trùng phòng
                if a_room == room_id:
                    return False
                # Kiểm tra trùng giảng viên
                if a_lec == lec_id:
                    return False
                # Kiểm tra trùng lịch của Cohort
                assigned_c_info = courses[assigned_c_id]
                assigned_cohorts = set(assigned_c_info.get("cohorts", []))
                if c_cohorts.intersection(assigned_cohorts):
                    return False
        return True

    def select_unassigned_variable(current_assignment: Dict[str, Choice]) -> str:
        unassigned = [c for c in courses if c not in current_assignment]
        if strategy == "mrv":
            # MRV (Minimum Remaining Values): Ưu tiên chọn môn có ít lựa chọn hợp lệ nhất
            return min(unassigned, key=lambda c: len(domains[c]))
        else:
            # Naive: Chọn theo thứ tự xuất hiện ban đầu
            return unassigned[0]

    def backtrack() -> bool:
        if len(assignment) == len(courses):
            return True

        var = select_unassigned_variable(assignment)

        for value in domains[var]:
            if is_consistent(var, value, assignment):
                assignment[var] = value
                
                if backtrack():
                    return True
                
                # Undo nếu không tìm ra kết quả
                del assignment[var]

        return False

    if backtrack():
        return assignment
    
    return None


def soft_constraint_score(instance: dict, assignment: Dict[str, Choice]) -> float:
    """Optional soft-constraint scoring."""
    return 0.0
