import uuid
import time
from pipeline import stage1_intent, stage2_design, stage3_schemas, stage4_validate, stage5_codegen


def run_pipeline(user_prompt: str) -> dict:
    job_id      = str(uuid.uuid4())[:8]
    stage_outputs = {}
    all_metrics   = []
    start_total   = time.time()

    # Stage 1
    intent, m1 = stage1_intent.run(user_prompt)
    stage_outputs["stage1_intent"] = intent
    all_metrics.append(m1)
    time.sleep(4)

    # Stage 2
    design, m2 = stage2_design.run(intent)
    stage_outputs["stage2_design"] = design
    all_metrics.append(m2)
    time.sleep(4)

    # Stage 3
    db, api, ui, m3_db, m3_api, m3_ui = stage3_schemas.run(design, intent)
    stage_outputs["stage3_db"]  = db
    stage_outputs["stage3_api"] = api
    stage_outputs["stage3_ui"]  = ui
    all_metrics.extend([m3_db, m3_api, m3_ui])

    auth_design = design.get("auth_design", {})
    auth = {
        "auth_type":        auth_design.get("type", "jwt"),
        "roles":            auth_design.get("roles", ["user", "admin"]),
        "role_permissions": auth_design.get("role_permissions", []),
        "protected_routes": [],
    }

    # Stage 4
    db, api, ui, auth, all_errors, repair_log = stage4_validate.run(db, api, ui, auth)
    stage_outputs["stage4_validated"] = {"db": db, "api": api, "ui": ui, "auth": auth}

    # Stage 5
    code_files = stage5_codegen.run(db, api, intent)
    stage_outputs["stage5_codegen"] = code_files

    total_latency = round(time.time() - start_total, 2)
    total_tokens  = sum(m.get("total_tokens", 0) for m in all_metrics)

    return {
        "job_id":  job_id,
        "status":  "success" if not all_errors else "partial",
        "app_schema": {"intent": intent, "database": db, "api": api, "ui": ui, "auth": auth},
        "generated_code":    code_files,
        "stage_outputs":     stage_outputs,
        "validation_errors": all_errors,
        "repair_log":        repair_log,
        "assumptions":       intent.get("assumptions", []),
        "metrics": {
            "total_latency_seconds": total_latency,
            "total_tokens":          total_tokens,
            "estimated_cost_usd":    0.0,
            "stages":                all_metrics,
            "repair_attempts":       len(repair_log),
        },
    }
