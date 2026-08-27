import os
from pathlib import Path
from gever.leads import DdgsSearchProvider, GeversLeadProfile, LeadEvaluator, LeadHunter, LeadStore

def build_hunter(db_path=None):
    profile=GeversLeadProfile()
    store=LeadStore(db_path or os.getenv("GEVER_LEADS_DB") or (Path.home()/".gever"/"leads.db"))
    hunter=LeadHunter(store, LeadEvaluator(profile), profile, [DdgsSearchProvider()])
    return hunter, store

def main():
    hunter,store=build_hunter(); summary=hunter.run()
    print("\nGEVER LEAD HUNTER")
    print(f"Encontrados: {summary.raw_findings} | Aceptados: {summary.accepted_leads} | Rechazados: {summary.rejected_findings}")
    print(f"HOT: {summary.hot_count} | WARM: {summary.warm_count} | PROSPECT: {summary.prospect_count}")
    if summary.errors:
        for provider,error in summary.errors.items(): print(f"ERROR {provider}: {error}")
    leads=store.list_leads()
    if not leads: print("No hay oportunidades almacenadas todavía.")
    for lead in leads[:20]:
        print(f"\n[{lead.classification.value}] Score {lead.score:.0f}\n{lead.evidence}\n{lead.source_url}")
    return 0

if __name__=="__main__": raise SystemExit(main())
