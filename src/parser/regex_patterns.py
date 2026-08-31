import re

# Comprehensive canonical parameter mapping
PARAMETER_MAP = {
    # Glycemic / Metabolic
    r"\b(fasting\s+(?:blood\s+)?glucose|glucose\s*fasting|fbs|blood\s*glucose|fasting\s*sugar)\b": "glucose_fasting",
    r"\b(post\s*prandial\s*(?:blood\s*)?glucose|ppbs|pp\s*glucose)\b": "glucose_pp",
    r"\b(random\s*blood\s*sugar|rbs|blood\s*glucose\s*random)\b": "glucose_random",
    r"\b(hba1c|glycosylated\s+hemoglobin|glycated\s+hemoglobin)\b": "hba1c",
    r"\b(insulin\s*(?:fasting)?)\b": "insulin",
    
    # Complete Blood Count (CBC) / Hematology
    r"\b(hemoglobin|haemoglobin|hgb|\bhb\b)\b": "hemoglobin",
    r"\b(total\s+(?:leukocyte|wbc|white\s*blood\s*cell)\s+count|wbc\s*count|tlc|\bwbc\b)\b": "wbc_count",
    r"\b(total\s+rbc\s+count|rbc\s*count|red\s*blood\s*cell\s*count|\brbc\b)\b": "rbc_count",
    r"\b(platelet\s+count|platelets|\bplt\b)\b": "platelet_count",
    r"\b(hematocrit(?:\s+value)?|packed\s*cell\s*volume|\bhct\b|\bpcv\b)\b": "hematocrit",
    r"\b(mean\s+corpuscular\s+volume|\bmcv\b)\b": "mcv",
    r"\b(mean\s+cell\s+ha?emoglobin\s+con(?:centration)?|\bmchc\b)\b": "mchc",
    r"\b(mean\s+cell\s+ha?emoglobin|\bmch\b)\b": "mch",
    r"\b(neutrophils?|polymorphs?)\b": "neutrophils",
    r"\b(lymphocytes?)\b": "lymphocytes",
    r"\b(eosinophils?)\b": "eosinophils",
    r"\b(monocytes?)\b": "monocytes",
    r"\b(basophils?)\b": "basophils",
    r"\b(esr|erythrocyte\s+sedimentation\s+rate)\b": "esr",
    r"\b(serum\s+iron|iron)\b": "iron",

    # Renal / Kidney Function (KFT/RFT)
    r"\b(serum\s+creatinine|creatinine|\bcr\b)\b": "creatinine",
    r"\b(blood\s+urea\s+nitrogen|\bbun\b)\b": "blood_urea_nitrogen",
    r"\b(blood\s+urea|serum\s+urea|urea)\b": "blood_urea",
    r"\b(serum\s+uric\s+acid|uric\s+acid)\b": "uric_acid",
    r"\b(serum\s+sodium|sodium|\bna\+?\b)\b": "sodium",
    r"\b(serum\s+potassium|potassium|\bk\+?\b)\b": "potassium",
    r"\b(serum\s+chloride|chloride|\bcl\-?\b)\b": "chloride",
    r"\b(serum\s+calcium|calcium|\bca\+?\+?\b)\b": "calcium",

    # Hepatic / Liver Function (LFT)
    r"\b(alanine\s+aminotransferase|sgpt|\balt\b)\b": "alt_sgpt",
    r"\b(aspartate\s+aminotransferase|sgot|\bast\b)\b": "ast_sgot",
    r"\b(alkaline\s+phosphatase|\balp\b)\b": "alkaline_phosphatase",
    r"\b(total\s+bilirubin|bilirubin\s+total)\b": "total_bilirubin",
    r"\b(direct\s+bilirubin|conjugated\s+bilirubin)\b": "direct_bilirubin",
    r"\b(total\s+proteins?|serum\s+protein)\b": "total_proteins",
    r"\b(serum\s+albumin|albumin)\b": "albumin",
    r"\b(serum\s+globulin|globulin)\b": "globulin",
    r"\b(a/g\s+ratio|albumin\s*[\/:]\s*globulin\s+ratio)\b": "ag_ratio",

    # Lipid Profile / Cardiovascular
    r"\b(total\s+cholesterol|serum\s+cholesterol|cholesterol\s+total|\bchol\b)\b": "cholesterol_total",
    r"\b(triglycerides?|\btg\b)\b": "triglycerides",
    r"\b(hdl\s+cholesterol|hdl|high\s+density\s+lipoprotein)\b": "hdl_cholesterol",
    r"\b(ldl\s+cholesterol|ldl|low\s+density\s+lipoprotein)\b": "ldl_cholesterol",
    r"\b(vldl\s+cholesterol|vldl)\b": "vldl_cholesterol",
    r"\b(systolic\s+blood\s+pressure|blood\s+pressure|resting\s+bp|\bbp\b)\b": "blood_pressure",

    # Thyroid Profile
    r"\b(tsh|thyroid\s+stimulating\s+hormone|thyrotropin)\b": "tsh",
    r"\b(ft3|free\s+triiodothyronine)\b": "ft3",
    r"\b(ft4|free\s+thyroxine)\b": "ft4",
    r"\b(total\s+t3|triiodothyronine|\bt3\b)\b": "t3",
    r"\b(total\s+t4|thyroxine|\bt4\b)\b": "t4"
}

# Regex to capture parameter name, value, and optional unit from text lines
# Supports format like:
# "HEMOGLOBIN 15 g/dl 13 - 17"
# "Glucose Fasting : 100 mg/dL"
# "Lymphocyte L 18 %"
PARAMETER_LINE_REGEX = re.compile(
    r"^(?P<param>[A-Za-z0-9\s,\(\)/_-]+?)\s*[:=-]?\s*(?:[HL]\s+)?(?P<value>\d+(?:,\d+)*(?:\.\d+)?)\s*(?P<unit>[a-zA-Z/%μuL/]+(?:\s*[a-zA-Z/%]+)?)?",
    re.IGNORECASE
)
