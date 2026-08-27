import os
import sys
from pathlib import Path

from gever.leads import DdgsSearchProvider, GeversLeadProfile, LeadEvaluator, LeadHunter, LeadStore


def console_text(value, encoding=None):
    text = str(value)
    target_encoding = encoding or getattr(sys.stdout, "encoding", None) or "utf-8"
    return text.encode(target_encoding, errors="replace").decode(target_encoding, errors="replace")


def build_hunter(db_path=None):
    profile = GeversLeadProfile()
    store = LeadStore(db_path or os.getenv("GEVER_LEADS_DB") or (Path.home() / ".gever" / "leads.db"))
    hunter = LeadHunter(store, LeadEvaluator(profile), profile, [DdgsSearchProvider()])
    return hunter, store


def main():
    hunter, store = build_hunter()
    summary = hunter.run()

    print("\nGEVER LEAD HUNTER")
    print(f"Encontrados: {summary.raw_findings} | Aceptados: {summary.accepted_leads} | Rechazados: {summary.rejected_findings}")
    print(f"HOT: {summary.hot_count} | WARM: {summary.warm_count} | PROSPECT: {summary.prospect_count}")

    if summary.errors:
        for provider, error in summary.errors.items():
            print(console_text(f"ERROR {provider}: {error}"))

    leads = store.list_leads()
    if not leads:
        print("No hay oportunidades almacenadas todavía.")

    for lead in leads[:20]:
        block = f"\n[{lead.classification.value}] Score {lead.score:.0f}\n{lead.evidence}\n{lead.source_url}"
        print(console_text(block))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
