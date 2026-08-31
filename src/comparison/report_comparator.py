from typing import List, Dict, Any, Tuple

class ReportComparator:
    """
    Compares two analytical reports to determine medical trends (Improvement, Deterioration).
    """

    @staticmethod
    def _map_parameters(params: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        param_map = {}
        for p in params:
            name = p.get('canonical_name') or p.get('parameter_name') or p.get('raw_name', '').lower()
            if not name:
                continue
            param_map[name.lower()] = {
                'value': float(p.get('measured_value', p.get('value', 0))),
                'unit': p.get('unit', ''),
                'flag': p.get('flag', 'NORMAL').upper()
            }
        return param_map

    @classmethod
    def compare_parameters(cls, old_params: List[Dict[str, Any]], new_params: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        old_map = cls._map_parameters(old_params)
        new_map = cls._map_parameters(new_params)

        comparison_results = []
        all_keys = set(old_map.keys()).union(new_map.keys())

        # Logic for determining "worsened" vs "improved" depends on typical medical bounds,
        # but for generics: if both are normal -> Stable.
        # if Old Normal -> New Abnormal -> Worsened.
        # if Old Abnormal -> New Normal -> Improved.
        # if Old Abnormal -> New Abnormal ->
        #     Check absolute deviation from mean or simple magnitude change if bounds aren't given.

        for key in all_keys:
            old_p = old_map.get(key)
            new_p = new_map.get(key)

            if not old_p:
                comparison_results.append({
                    "parameter": key.title(),
                    "old_value": "N/A",
                    "new_value": new_p['value'],
                    "unit": new_p['unit'],
                    "trend": "New Observation",
                    "color": "gray"
                })
                continue
            if not new_p:
                continue # ignore removed parameters for now

            old_val = old_p['value']
            new_val = new_p['value']
            old_flag = old_p['flag']
            new_flag = new_p['flag']

            trend = "Stable"
            color = "green" if new_flag == "NORMAL" else "orange"

            if old_flag == "NORMAL" and new_flag != "NORMAL":
                trend = "Worsened"
                color = "red"
            elif old_flag != "NORMAL" and new_flag == "NORMAL":
                trend = "Improved"
                color = "green"
            elif old_flag != "NORMAL" and new_flag != "NORMAL":
                # Both abnormal. Did value increase or decrease?
                # Without knowing if high/low is bad, we just denote direction.
                diff = new_val - old_val
                pct_change = (diff / max(old_val, 0.001)) * 100
                if abs(pct_change) < 5:
                    trend = "Stable (Abnormal)"
                else:
                    trend = f"{'Increased' if diff > 0 else 'Decreased'} by {abs(pct_change):.1f}%"
                color = "red"
            else:
                diff = new_val - old_val
                pct_change = (diff / max(old_val, 0.001)) * 100
                if abs(pct_change) > 10:
                    trend = f"{'Increased' if diff > 0 else 'Decreased'} (Stable)"

            comparison_results.append({
                "parameter": key.title(),
                "old_value": old_val,
                "new_value": new_val,
                "unit": new_p['unit'],
                "trend": trend,
                "color": color
            })

        return sorted(comparison_results, key=lambda x: (x['color'] == 'red', x['color'] == 'orange'), reverse=True)

    @classmethod
    def compare_predictions(cls, old_preds: Dict[str, float], new_preds: Dict[str, float]) -> List[Dict[str, Any]]:
        results = []
        all_diseases = set(old_preds.keys()).union(new_preds.keys())

        for disease in all_diseases:
            old_r = old_preds.get(disease)
            new_r = new_preds.get(disease)

            if old_r is None or new_r is None:
                continue

            diff = new_r - old_r
            if diff > 0.05:
                trend = f"Risk increased by {diff*100:.1f}%"
                color = "red"
            elif diff < -0.05:
                trend = f"Risk decreased by {abs(diff)*100:.1f}%"
                color = "green"
            else:
                trend = "Risk stable"
                color = "gray"

            results.append({
                "disease": disease,
                "old_risk": old_r,
                "new_risk": new_r,
                "trend": trend,
                "color": color
            })
        return results

    @classmethod
    def compare_scores(cls, old_score: float, new_score: float) -> Tuple[float, str]:
        diff = new_score - old_score
        if diff >= 5:
            return diff, "Improved"
        elif diff <= -5:
            return diff, "Declined"
        else:
            return diff, "Stable"
