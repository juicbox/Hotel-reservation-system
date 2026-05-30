from dataclasses import dataclass, field
from datetime import datetime

from hotel.enums import ReportType


@dataclass
class Report:
    report_id: str
    report_type: ReportType
    generated_by: str
    period: str
    generated_at: datetime = field(default_factory=datetime.now)
    data: dict[str, object] = field(default_factory=dict)

    def generate(self) -> None:
        self.generated_at = datetime.now()

    def export(self, export_format: str) -> str:
        return f"Report {self.report_id} exported as {export_format.upper()}"

    def get_occupancy_rate(self) -> float:
        return float(self.data.get("occupancy_rate", 0.0))

    def get_revenue_summary(self) -> dict:
        return dict(self.data.get("revenue_summary", {}))
