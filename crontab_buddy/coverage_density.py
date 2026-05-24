"""coverage_density: combined coverage + density scoring for a set of expressions."""
from typing import List, Dict, Any
from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.coverage_score import compute_coverage_score
from crontab_buddy.density_score import compute_density_score


def _grade(score: float) -> str:
    if score >= 0.85:
        return "rich"
    if score >= 0.65:
        return "balanced"
    if score >= 0.40:
        return "moderate"
    if score >= 0.20:
        return "thin"
    return "sparse"


class CoverageDensityResult:
    def __init__(
        self,
        expressions: List[str],
        coverage_score: float,
        density_score: float,
        combined_score: float,
        grade: str,
        error: str = "",
    ):
        self.expressions = expressions
        self.coverage_score = coverage_score
        self.density_score = density_score
        self.combined_score = combined_score
        self.grade = grade
        self.error = error

    def __str__(self) -> str:
        if self.error:
            return f"CoverageDensity(error={self.error})"
        return (
            f"CoverageDensity(coverage={self.coverage_score:.2f}, "
            f"density={self.density_score:.2f}, combined={self.combined_score:.2f}, "
            f"grade={self.grade})"
        )


def assess_coverage_density(expressions: List[str]) -> CoverageDensityResult:
    """Assess the combined coverage and density of a list of cron expressions."""
    if not expressions:
        return CoverageDensityResult(
            expressions=[], coverage_score=0.0, density_score=0.0,
            combined_score=0.0, grade="sparse", error="no expressions provided"
        )

    valid = []
    for expr in expressions:
        try:
            CronExpression(expr)
            valid.append(expr)
        except CronParseError:
            pass

    if not valid:
        return CoverageDensityResult(
            expressions=expressions, coverage_score=0.0, density_score=0.0,
            combined_score=0.0, grade="sparse", error="no valid expressions"
        )

    cov_r = compute_coverage_score(valid)
    cov_score = cov_r.score

    density_scores = [compute_density_score(e).score for e in valid]
    avg_density = sum(density_scores) / len(density_scores)

    combined = round((cov_score + avg_density) / 2.0, 4)
    return CoverageDensityResult(
        expressions=valid,
        coverage_score=round(cov_score, 4),
        density_score=round(avg_density, 4),
        combined_score=combined,
        grade=_grade(combined),
    )


def format_coverage_density(result: CoverageDensityResult) -> Dict[str, Any]:
    return {
        "expressions": result.expressions,
        "coverage_score": result.coverage_score,
        "density_score": result.density_score,
        "combined_score": result.combined_score,
        "grade": result.grade,
        "error": result.error,
    }
