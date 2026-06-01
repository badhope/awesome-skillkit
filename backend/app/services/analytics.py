from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class UsageRecord:
    skill_id: str
    user_id: str
    agent_type: str
    task: str
    success: bool
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DashboardStats:
    total_skills: int = 0
    total_users: int = 0
    total_usage_events: int = 0
    average_success_rate: float = 0.0
    average_duration_ms: float = 0.0
    skills_added_last_7_days: int = 0
    usage_events_last_7_days: int = 0
    active_users_last_7_days: int = 0


@dataclass
class UsageReport:
    start_date: datetime
    end_date: datetime
    total_events: int
    unique_skills: int
    unique_users: int
    success_rate: float
    top_skills: List[Dict[str, Any]]
    daily_trends: List[Dict[str, Any]]
    category_distribution: Dict[str, int]
    agent_type_distribution: Dict[str, int]


class AnalyticsService:

    def __init__(self):
        self._records: List[UsageRecord] = []
        self._skills_db: Dict[str, Dict[str, Any]] = {}
        self._users_db: Dict[str, Dict[str, Any]] = {}

    def set_skills_db(self, skills: Dict[str, Dict[str, Any]]) -> None:
        self._skills_db = skills

    def set_users_db(self, users: Dict[str, Dict[str, Any]]) -> None:
        self._users_db = users

    def track_skill_usage(
        self,
        skill_id: str,
        user_id: str,
        agent_type: str,
        task: str,
        success: bool,
        duration: float,
    ) -> UsageRecord:
        record = UsageRecord(
            skill_id=skill_id,
            user_id=user_id,
            agent_type=agent_type,
            task=task,
            success=success,
            duration_ms=duration,
        )
        self._records.append(record)

        if skill_id in self._skills_db:
            skill = self._skills_db[skill_id]
            skill["usage_count"] = skill.get("usage_count", 0) + 1
            if success:
                skill["successful_uses"] = skill.get("successful_uses", 0) + 1

            total_duration = skill.get("total_duration_ms", 0) + duration
            total_uses = skill.get("usage_count", 1)
            skill["avg_duration_ms"] = total_duration / total_uses
            skill["total_duration_ms"] = total_duration

        return record

    def get_dashboard_stats(self) -> DashboardStats:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)

        total_skills = len(self._skills_db)
        total_users = len(self._users_db)
        total_usage = len(self._records)

        recent_records = [
            r for r in self._records if r.timestamp >= seven_days_ago
        ]

        successful = sum(1 for r in self._records if r.success)
        avg_success = (successful / total_usage * 100) if total_usage > 0 else 0.0

        avg_duration = (
            sum(r.duration_ms for r in self._records) / total_usage
            if total_usage > 0
            else 0.0
        )

        skills_added_recent = sum(
            1 for s in self._skills_db.values()
            if s.get("created_at") and self._parse_datetime(s["created_at"]) >= seven_days_ago
        )

        usage_recent = len(recent_records)

        active_users_recent = len(set(
            r.user_id for r in recent_records
        ))

        return DashboardStats(
            total_skills=total_skills,
            total_users=total_users,
            total_usage_events=total_usage,
            average_success_rate=round(avg_success, 2),
            average_duration_ms=round(avg_duration, 2),
            skills_added_last_7_days=skills_added_recent,
            usage_events_last_7_days=usage_recent,
            active_users_last_7_days=active_users_recent,
        )

    def get_skill_usage_trends(
        self, skill_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(days=days)

        daily_counts: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"total": 0, "success": 0, "failure": 0}
        )

        for record in self._records:
            if record.skill_id != skill_id or record.timestamp < cutoff:
                continue
            day_key = record.timestamp.strftime("%Y-%m-%d")
            daily_counts[day_key]["total"] += 1
            if record.success:
                daily_counts[day_key]["success"] += 1
            else:
                daily_counts[day_key]["failure"] += 1

        current = cutoff
        trends: List[Dict[str, Any]] = []
        while current <= datetime.utcnow():
            day_key = current.strftime("%Y-%m-%d")
            counts = daily_counts.get(day_key, {"total": 0, "success": 0, "failure": 0})
            total = counts["total"]
            success_rate = (counts["success"] / total * 100) if total > 0 else 0.0
            trends.append({
                "date": day_key,
                "total": total,
                "success": counts["success"],
                "failure": counts["failure"],
                "success_rate": round(success_rate, 2),
            })
            current += timedelta(days=1)

        return trends

    def get_popular_skills(self, limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(days=days)

        usage_counts: Dict[str, int] = defaultdict(int)
        success_counts: Dict[str, int] = defaultdict(int)

        for record in self._records:
            if record.timestamp >= cutoff:
                usage_counts[record.skill_id] += 1
                if record.success:
                    success_counts[record.skill_id] += 1

        ranked: List[Dict[str, Any]] = []
        for skill_id, count in sorted(usage_counts.items(), key=lambda x: x[1], reverse=True):
            skill_info = self._skills_db.get(skill_id, {})
            ranked.append({
                "skill_id": skill_id,
                "name": skill_info.get("name", skill_id),
                "usage_count": count,
                "success_rate": round(
                    (success_counts.get(skill_id, 0) / count * 100) if count > 0 else 0, 2
                ),
                "category": skill_info.get("category", ""),
            })
            if len(ranked) >= limit:
                break

        return ranked

    def get_trending_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        recent_window = now - timedelta(days=7)
        older_window = recent_window - timedelta(days=21)

        recent_counts: Dict[str, int] = defaultdict(int)
        older_counts: Dict[str, int] = defaultdict(int)

        for record in self._records:
            if record.timestamp >= recent_window:
                recent_counts[record.skill_id] += 1
            elif record.timestamp >= older_window:
                older_counts[record.skill_id] += 1

        trending_scores: Dict[str, float] = {}
        for skill_id in recent_counts:
            recent = recent_counts[skill_id]
            older = older_counts.get(skill_id, 0)
            if older > 0:
                score = (recent - older) / older
            elif recent > 0:
                score = float(recent)
            else:
                score = 0.0
            trending_scores[skill_id] = score

        ranked: List[Dict[str, Any]] = []
        for skill_id, score in sorted(trending_scores.items(), key=lambda x: x[1], reverse=True):
            if score <= 0 and len(ranked) >= max(3, limit // 2):
                break
            skill_info = self._skills_db.get(skill_id, {})
            ranked.append({
                "skill_id": skill_id,
                "name": skill_info.get("name", skill_id),
                "category": skill_info.get("category", ""),
                "trending_score": round(score, 4),
                "recent_usage": recent_counts[skill_id],
                "older_usage": older_counts.get(skill_id, 0),
            })
            if len(ranked) >= limit:
                break

        return ranked

    def get_category_distribution(self) -> Dict[str, int]:
        distribution: Dict[str, int] = defaultdict(int)

        for record in self._records:
            skill_info = self._skills_db.get(record.skill_id, {})
            category = skill_info.get("category", "uncategorized")
            distribution[category] += 1

        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

    def get_user_activity(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(days=days)

        daily_activity: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"skills_used": 0, "total_duration_ms": 0.0, "skills": set()}
        )

        for record in self._records:
            if record.user_id != user_id or record.timestamp < cutoff:
                continue
            day_key = record.timestamp.strftime("%Y-%m-%d")
            daily_activity[day_key]["skills_used"] += 1
            daily_activity[day_key]["total_duration_ms"] += record.duration_ms
            daily_activity[day_key]["skills"].add(record.skill_id)

        current = cutoff
        activity: List[Dict[str, Any]] = []
        while current <= datetime.utcnow():
            day_key = current.strftime("%Y-%m-%d")
            day_data = daily_activity.get(
                day_key,
                {"skills_used": 0, "total_duration_ms": 0.0, "skills": set()},
            )
            activity.append({
                "date": day_key,
                "skills_used": day_data["skills_used"],
                "unique_skills": len(day_data["skills"]),
                "total_duration_ms": round(day_data["total_duration_ms"], 2),
            })
            current += timedelta(days=1)

        return activity

    def generate_usage_report(
        self, start_date: datetime, end_date: datetime
    ) -> UsageReport:
        filtered = [
            r for r in self._records
            if start_date <= r.timestamp <= end_date
        ]

        total_events = len(filtered)
        unique_skills = len(set(r.skill_id for r in filtered))
        unique_users = len(set(r.user_id for r in filtered))

        successful = sum(1 for r in filtered if r.success)
        success_rate = (successful / total_events * 100) if total_events > 0 else 0.0

        skill_counts: Dict[str, int] = defaultdict(int)
        for r in filtered:
            skill_counts[r.skill_id] += 1

        top_skills: List[Dict[str, Any]] = []
        for skill_id, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            skill_info = self._skills_db.get(skill_id, {})
            top_skills.append({
                "skill_id": skill_id,
                "name": skill_info.get("name", skill_id),
                "usage_count": count,
                "category": skill_info.get("category", ""),
            })

        daily_trends: Dict[str, int] = defaultdict(int)
        for r in filtered:
            day_key = r.timestamp.strftime("%Y-%m-%d")
            daily_trends[day_key] += 1

        current = start_date
        trends_list: List[Dict[str, Any]] = []
        while current <= end_date:
            day_key = current.strftime("%Y-%m-%d")
            trends_list.append({
                "date": day_key,
                "events": daily_trends.get(day_key, 0),
            })
            current += timedelta(days=1)

        category_dist: Dict[str, int] = defaultdict(int)
        agent_type_dist: Dict[str, int] = defaultdict(int)
        for r in filtered:
            skill_info = self._skills_db.get(r.skill_id, {})
            category = skill_info.get("category", "uncategorized")
            category_dist[category] += 1
            agent_type_dist[r.agent_type] += 1

        return UsageReport(
            start_date=start_date,
            end_date=end_date,
            total_events=total_events,
            unique_skills=unique_skills,
            unique_users=unique_users,
            success_rate=round(success_rate, 2),
            top_skills=top_skills,
            daily_trends=trends_list,
            category_distribution=dict(category_dist),
            agent_type_distribution=dict(agent_type_dist),
        )

    def _parse_datetime(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
        return datetime.min