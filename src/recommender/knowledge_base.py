RECOMMENDATION_DATABASE = {
    "glucose_fasting": {
        "HIGH": {
            "title": "Elevated Fasting Blood Sugar Management",
            "diet": [
                "Adopt a low-glycemic index (GI) Mediterranean or DASH dietary pattern.",
                "Avoid sugar-sweetened beverages, refined carbohydrates, and ultra-processed foods.",
                "Increase dietary fiber intake (at least 25-30g daily) from legumes, whole grains, and leafy vegetables."
            ],
            "lifestyle": [
                "Engage in at least 150 minutes of moderate-intensity aerobic exercise per week.",
                "Incorporate post-meal 10-15 minute walks to attenuate glucose spikes.",
                "Maintain adequate sleep duration (7-9 hours) to optimize insulin sensitivity."
            ],
            "consult": "Consult an endocrinologist or primary care physician for HbA1c evaluation and oral glucose tolerance testing."
        },
        "LOW": {
            "title": "Hypoglycemia Precaution",
            "diet": ["Carry fast-acting carbohydrates (e.g., glucose tablets or fruit juice).", "Consume balanced meals with adequate complex carbs and protein."],
            "lifestyle": ["Avoid skipping meals, especially after strenuous physical exercise."],
            "consult": "Consult a physician if episodes of dizziness, tremors, or diaphoresis occur repeatedly."
        }
    },
    "cholesterol_total": {
        "HIGH": {
            "title": "Cardiovascular Lipid Management",
            "diet": [
                "Limit saturated fatty acid intake to < 7% of daily total caloric intake.",
                "Eliminate industrial trans-fats and reduce dietary cholesterol.",
                "Increase intake of soluble fiber, plant stanols/sterols, and omega-3 rich fatty fish (salmon, mackerel)."
            ],
            "lifestyle": [
                "Aim for 30-45 minutes of daily moderate cardiovascular exercise.",
                "Smoking cessation and moderate/restrict alcohol consumption."
            ],
            "consult": "Discuss a comprehensive fasting lipid panel (HDL, LDL, Triglycerides) and ASCVD risk scoring with a cardiologist."
        }
    },
    "creatinine": {
        "HIGH": {
            "title": "Renal Function & Hydration Support",
            "diet": [
                "Maintain optimal hydration unless under strict fluid restriction instructions.",
                "Avoid excessive intake of dietary protein and high-sodium processed foods."
            ],
            "lifestyle": [
                "Avoid self-medication with Non-Steroidal Anti-Inflammatory Drugs (NSAIDs like ibuprofen, naproxen).",
                "Monitor and maintain blood pressure within target clinical guidelines (< 130/80 mmHg)."
            ],
            "consult": "Consult a nephrologist for eGFR calculation and renal ultrasound evaluation."
        }
    },
    "alt_sgpt": {
        "HIGH": {
            "title": "Hepatic Health and Liver Protection",
            "diet": [
                "Eliminate alcohol consumption completely during liver enzyme elevation.",
                "Reduce intake of dietary fructose and saturated fats.",
                "Incorporate antioxidant-rich foods including green tea, berries, and cruciferous vegetables."
            ],
            "lifestyle": [
                "Engage in regular aerobic physical activity to reduce hepatic steatosis (fatty liver).",
                "Review all medications, supplements, and herbal products with a physician for potential hepatotoxicity."
            ],
            "consult": "Consult a gastroenterologist/hepatologist for viral hepatitis screening and liver ultrasound."
        }
    },
    "hemoglobin": {
        "LOW": {
            "title": "Anemia & Hematologic Evaluation",
            "diet": [
                "Increase intake of heme-iron (lean meats, poultry) and non-heme iron (spinach, lentils, fortified cereals).",
                "Pair iron-rich foods with vitamin C (citrus fruits, bell peppers) to enhance intestinal absorption.",
                "Avoid drinking tea or coffee simultaneously with iron-rich meals."
            ],
            "lifestyle": [
                "Rest adequately and avoid high-strain exhaustion if experiencing fatigue or dyspnea."
            ],
            "consult": "Consult a physician for complete iron studies (serum ferritin, TIBC, transferrin saturation) and vitamin B12/folate levels."
        }
    }
}
