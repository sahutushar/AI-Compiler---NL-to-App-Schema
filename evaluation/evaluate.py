"""
Evaluation Framework — runs 20 prompts and tracks metrics
Run: python evaluate.py
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from orchestrator import run_pipeline

PROMPTS = [
    # ── 10 Real Product Prompts ────────────────────────────────────────────────
    {
        "id": "real_01",
        "category": "real",
        "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
    },
    {
        "id": "real_02",
        "category": "real",
        "prompt": "Create an e-commerce store with product listings, shopping cart, checkout with Stripe, order tracking, and admin product management.",
    },
    {
        "id": "real_03",
        "category": "real",
        "prompt": "Build a project management tool like Trello with boards, cards, team members, deadlines, and notifications.",
    },
    {
        "id": "real_04",
        "category": "real",
        "prompt": "Create a blog platform where users can write posts, comment, like, and admins can moderate content. Include SEO metadata.",
    },
    {
        "id": "real_05",
        "category": "real",
        "prompt": "Build a hospital appointment booking system with doctors, patients, time slots, prescriptions, and billing.",
    },
    {
        "id": "real_06",
        "category": "real",
        "prompt": "Create a learning management system with courses, lessons, quizzes, student progress tracking, and certificate generation.",
    },
    {
        "id": "real_07",
        "category": "real",
        "prompt": "Build a food delivery app with restaurants, menus, orders, delivery tracking, ratings, and driver management.",
    },
    {
        "id": "real_08",
        "category": "real",
        "prompt": "Create a SaaS invoicing tool with clients, invoices, payment reminders, recurring billing, and financial reports.",
    },
    {
        "id": "real_09",
        "category": "real",
        "prompt": "Build a social media platform with profiles, posts, follow system, feed, direct messages, and content moderation.",
    },
    {
        "id": "real_10",
        "category": "real",
        "prompt": "Create a real estate platform with property listings, search filters, agent profiles, booking viewings, and mortgage calculator.",
    },

    # ── 10 Edge Cases ─────────────────────────────────────────────────────────
    {
        "id": "edge_01",
        "category": "vague",
        "prompt": "Build an app.",
    },
    {
        "id": "edge_02",
        "category": "vague",
        "prompt": "I need a website for my business.",
    },
    {
        "id": "edge_03",
        "category": "conflicting",
        "prompt": "Build a free app but also charge users monthly. Everyone is an admin but also no one has special access.",
    },
    {
        "id": "edge_04",
        "category": "conflicting",
        "prompt": "Create a private social network that is also fully public. Users should be anonymous but also have verified profiles.",
    },
    {
        "id": "edge_05",
        "category": "incomplete",
        "prompt": "Build something with users and products.",
    },
    {
        "id": "edge_06",
        "category": "incomplete",
        "prompt": "Add analytics to my app.",
    },
    {
        "id": "edge_07",
        "category": "vague",
        "prompt": "Make it like Uber but different.",
    },
    {
        "id": "edge_08",
        "category": "incomplete",
        "prompt": "I want login and a dashboard.",
    },
    {
        "id": "edge_09",
        "category": "conflicting",
        "prompt": "Build a todo app with no database that persists data forever and works offline and online simultaneously.",
    },
    {
        "id": "edge_10",
        "category": "vague",
        "prompt": "Build the next Facebook.",
    },
]


def evaluate():
    results = []
    print(f"\n{'='*60}")
    print("AI COMPILER — EVALUATION FRAMEWORK")
    print(f"Running {len(PROMPTS)} prompts...")
    print(f"{'='*60}\n")

    for i, test in enumerate(PROMPTS, 1):
        print(f"[{i:02d}/{len(PROMPTS)}] {test['id']} ({test['category']}) — {test['prompt'][:60]}...")
        try:
            start = time.time()
            result = run_pipeline(test["prompt"])
            latency = round(time.time() - start, 2)
            outcome = {
                "id": test["id"],
                "category": test["category"],
                "status": result["status"],
                "latency_seconds": latency,
                "total_tokens": result["metrics"]["total_tokens"],
                "estimated_cost_usd": result["metrics"]["estimated_cost_usd"],
                "repair_attempts": result["metrics"]["repair_attempts"],
                "validation_errors": len(result["validation_errors"]),
                "assumptions_made": len(result["assumptions"]),
                "tables_generated": len(result["app_schema"]["database"].get("tables", [])),
                "endpoints_generated": len(result["app_schema"]["api"].get("endpoints", [])),
                "pages_generated": len(result["app_schema"]["ui"].get("pages", [])),
                "error": None,
            }
            print(f"  ✅ {result['status']} | {latency}s | {outcome['endpoints_generated']} endpoints | {outcome['repair_attempts']} repairs\n")
        except Exception as e:
            outcome = {
                "id": test["id"],
                "category": test["category"],
                "status": "failed",
                "error": str(e),
                "latency_seconds": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0,
                "repair_attempts": 0,
                "validation_errors": 0,
            }
            print(f"  ❌ FAILED: {e}\n")
        results.append(outcome)

    # ── Summary ────────────────────────────────────────────────────────────────
    total = len(results)
    success = sum(1 for r in results if r["status"] in ("success", "partial"))
    failed = sum(1 for r in results if r["status"] == "failed")
    avg_latency = round(sum(r["latency_seconds"] for r in results) / total, 2)
    total_cost = round(sum(r["estimated_cost_usd"] for r in results), 4)
    total_repairs = sum(r["repair_attempts"] for r in results)

    by_category = {}
    for r in results:
        cat = r["category"]
        by_category.setdefault(cat, {"success": 0, "total": 0})
        by_category[cat]["total"] += 1
        if r["status"] in ("success", "partial"):
            by_category[cat]["success"] += 1

    summary = {
        "total_prompts": total,
        "success_count": success,
        "failed_count": failed,
        "success_rate_pct": round(success / total * 100, 1),
        "avg_latency_seconds": avg_latency,
        "total_cost_usd": total_cost,
        "total_repair_attempts": total_repairs,
        "by_category": by_category,
        "individual_results": results,
    }

    with open("evaluation_results.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Total:           {total}")
    print(f"  Success:         {success} ({summary['success_rate_pct']}%)")
    print(f"  Failed:          {failed}")
    print(f"  Avg Latency:     {avg_latency}s")
    print(f"  Total Cost:      ${total_cost}")
    print(f"  Total Repairs:   {total_repairs}")
    print(f"\n  By Category:")
    for cat, stats in by_category.items():
        rate = round(stats["success"] / stats["total"] * 100, 1)
        print(f"    {cat:12s}: {stats['success']}/{stats['total']} ({rate}%)")
    print(f"\n  Results saved to evaluation_results.json")
    print(f"{'='*60}\n")

    return summary


if __name__ == "__main__":
    evaluate()
