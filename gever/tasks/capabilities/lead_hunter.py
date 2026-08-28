"""Adapter around the existing Lead Hunter; no model or voice changes."""

from ..models import Capability


class LeadHunterCapability(Capability):
    name = "lead_hunter"
    signals = ("busca clientes", "buscar clientes", "busca oportunidades", "buscar oportunidades",
               "busca leads", "buscar leads", "clientes de pintura", "oportunidades de clientes",
               "find painting leads", "find clients", "find leads")

    def __init__(self, get_tools, progress_callback=None):
        self.get_tools = get_tools
        self.progress_callback = progress_callback

    def execute(self, context):
        hunter, _store = self.get_tools()
        callback = self.progress_callback
        if callback is None:
            from gever.leads.telemetry import lead_hunter_telemetry
            callback = lead_hunter_telemetry.publish
        return hunter.run(trigger="voice", progress_callback=callback)

    def verify(self, summary):
        fields = ("raw_findings", "accepted_leads", "rejected_findings",
                  "hot_count", "warm_count", "prospect_count")
        if any(type(getattr(summary, field, None)) is not int or getattr(summary, field) < 0
               for field in fields):
            return False
        # Search-provider failures are not a verified zero-result search.
        if getattr(summary, "errors", None) != {}:
            return False
        return (summary.accepted_leads + summary.rejected_findings == summary.raw_findings
                and summary.hot_count + summary.warm_count + summary.prospect_count == summary.accepted_leads)

    def format_response(self, summary):
        if summary.accepted_leads == 0:
            return f"Búsqueda completada. Revisé {summary.raw_findings} resultados y no encontré ninguna oportunidad válida y reciente. Rechacé {summary.rejected_findings} resultados que no cumplían los filtros."
        return f"Búsqueda completada. Encontré {summary.accepted_leads} oportunidades válidas de {summary.raw_findings} resultados revisados. HOT: {summary.hot_count}, WARM: {summary.warm_count}, PROSPECT: {summary.prospect_count}."
