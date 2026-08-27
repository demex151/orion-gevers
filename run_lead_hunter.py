import os
import sys
from pathlib import Path

from gever.leads.evaluator import LeadEvaluator
from gever.leads.hunter import LeadHunter
from gever.leads.search import GeversLeadProfile, JsonSearchProvider
from gever.leads.store import LeadStore


def build_hunter(endpoint: str, api_key: str | None, db_path: str | Path):
    profile = GeversLeadProfile()
    store = LeadStore(db_path)
    provider = JsonSearchProvider(endpoint, api_key=api_key)
    hunter = LeadHunter(store, LeadEvaluator(profile), profile, [provider])
    return hunter, store


def main() -> int:
    endpoint = os.getenv("GEVER_SEARCH_ENDPOINT", "").strip()
    if not endpoint:
        print("Falta GEVER_SEARCH_ENDPOINT. Lead Hunter no ejecutó ninguna búsqueda.", file=sys.stderr)
        return 2

    api_key = os.getenv("GEVER_SEARCH_API_KEY") or None
    db_path = os.getenv("GEVER_LEADS_DB", str(Path.home() / ".gever" / "leads.db"))

    hunter, store = build_hunter(endpoint, api_key, db_path)
    summary = hunter.run()

    print("\nGEVER LEAD HUNTER")
    print(f"Encontrados: {summary.raw_findings}")
    print(f"Aceptados: {summary.accepted_leads}")
    print(f"Rechazados: {summary.rejected_findings}")
    print(f"Duplicados fusionados: {summary.duplicate_merges}")
    print(f"HOT: {summary.hot_count} | WARM: {summary.warm_count} | PROSPECT: {summary.prospect_count}")

    if summary.errors:
        print("\nErrores de proveedores:")
        for provider, error in summary.errors.items():
            print(f"- {provider}: {error}")

    leads = store.list_leads(limit=20)
    if leads:
        print("\nOPORTUNIDADES PRIORIZADAS")
        for lead in leads:
            print(f"\n[{lead.classification.value}] Score {lead.score:.0f}")
            print(lead.evidence)
            print(lead.source_url)
    else:
        print("\nNo hay oportunidades almacenadas todavía.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
