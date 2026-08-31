from typing import Dict, List, Any, Optional

class ContextBuilder:
    @staticmethod
    def build_clinical_context(
        patient_profile: Optional[Dict[str, Any]] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        predictions: Optional[Dict[str, float]] = None,
        health_score: Optional[Dict[str, Any]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        lines = []

        # 1. Patient Demographics
        if patient_profile:
            lines.append("### Patient Demographics:")
            lines.append(f"- Name: {patient_profile.get('full_name', 'Patient')}")
            lines.append(f"- Age: {patient_profile.get('age', 'N/A')}, Gender: {patient_profile.get('gender', 'N/A')}")
            if patient_profile.get('blood_group'):
                lines.append(f"- Blood Group: {patient_profile.get('blood_group')}")
            if patient_profile.get('bmi'):
                lines.append(f"- BMI: {patient_profile.get('bmi'):.1f}")
            lines.append("")

        # 2. Key Biomarkers & Abnormalities
        if parameters:
            lines.append("### Extracted Lab Parameters & Biomarkers:")
            abnormal_count = 0
            for p in parameters:
                name = p.get('canonical_name') or p.get('parameter_name') or p.get('raw_name', 'Unknown')
                val = p.get('measured_value') if 'measured_value' in p else p.get('value', 'N/A')
                unit = p.get('unit', '')
                flag = p.get('flag', 'NORMAL')
                flag_str = f" [{flag}]" if flag != 'NORMAL' else ""
                lines.append(f"- {name}: {val} {unit}{flag_str}")
                if flag != 'NORMAL':
                    abnormal_count += 1
            if abnormal_count == 0:
                lines.append("  (All measured lab values within normal baseline ranges)")
            lines.append("")

        # 3. Disease Risk Assessment
        if predictions:
            lines.append("### AI Disease Risk Probabilities:")
            for disease, prob in predictions.items():
                pct = prob * 100 if prob <= 1.0 else prob
                risk_lvl = "Critical" if pct > 75 else "High" if pct > 55 else "Moderate" if pct > 30 else "Low"
                lines.append(f"- {disease}: {pct:.1f}% risk ({risk_lvl})")
            lines.append("")

        # 4. Overall Health Score
        if health_score:
            lines.append("### Composite Health Score:")
            score = health_score.get('overall_score', 'N/A')
            rating = health_score.get('rating', health_score.get('score_grade', 'N/A'))
            lines.append(f"- Overall Score: {score}/100 ({rating})")
            cat_scores = health_score.get('category_scores', {})
            if cat_scores:
                breakdown = ", ".join([f"{k}: {v:.0f}/100" for k, v in cat_scores.items()])
                lines.append(f"- Organ Systems Breakdown: {breakdown}")
            lines.append("")

        # 5. Key Recommendations
        if recommendations:
            lines.append("### Top AI Recommendations:")
            for rec in recommendations[:5]:
                title = rec.get('title') or rec.get('recommendation', '')
                lines.append(f"- {title}")
            lines.append("")

        return "\n".join(lines)
