from .models import LeadClassification


class LeadHunter:
    def __init__(self, store, evaluator, profile, providers):
        self.store = store
        self.evaluator = evaluator
        self.profile = profile
        self.providers = list(providers)

    def _already_exists(self, dedupe_key):
        with self.store._connect() as conn:
            return conn.execute(
                "SELECT 1 FROM leads WHERE dedupe_key=? LIMIT 1",
                (dedupe_key,),
            ).fetchone() is not None

    def run(self, trigger="manual"):
        summary = self.store.start_run(trigger)
        try:
            for query in self.profile.queries():
                for provider in self.providers:
                    provider_name = getattr(provider, "name", provider.__class__.__name__)
                    try:
                        findings = provider.search(query)
                    except Exception as exc:
                        summary.errors[provider_name] = str(exc)
                        continue

                    for finding in findings:
                        summary.raw_findings += 1
                        result = self.evaluator.evaluate(finding)
                        if result.candidate is None:
                            summary.rejected_findings += 1
                            self.store.record_rejection(
                                summary.run_id,
                                result.rejection_reason or "rejected",
                                source_url=finding.url,
                                evidence=finding.snippet or finding.title,
                            )
                            continue

                        candidate = result.candidate
                        if self._already_exists(candidate.dedupe_key):
                            summary.duplicate_merges += 1

                        self.store.upsert_lead(candidate)
                        summary.accepted_leads += 1
                        if candidate.classification is LeadClassification.HOT:
                            summary.hot_count += 1
                        elif candidate.classification is LeadClassification.WARM:
                            summary.warm_count += 1
                        else:
                            summary.prospect_count += 1
        finally:
            self.store.finish_run(summary)

        return summary
