from .models import LeadClassification


class LeadHunter:
    def __init__(self, store, evaluator, profile, providers):
        self.store = store
        self.evaluator = evaluator
        self.profile = profile
        self.providers = list(providers)

    @staticmethod
    def _emit(callback, event_type, **data):
        if callback is None:
            return
        try:
            callback({"type": event_type, **data})
        except Exception:
            # Telemetry is observational only and must never break a hunt.
            pass

    def _already_exists(self, dedupe_key):
        with self.store._connect() as conn:
            return conn.execute(
                "SELECT 1 FROM leads WHERE dedupe_key=? LIMIT 1",
                (dedupe_key,),
            ).fetchone() is not None

    def run(self, trigger="manual", progress_callback=None):
        summary = self.store.start_run(trigger)
        self._emit(progress_callback, "started", run_id=summary.run_id, trigger=trigger)
        try:
            for query in self.profile.queries():
                for provider in self.providers:
                    provider_name = getattr(provider, "name", provider.__class__.__name__)
                    self._emit(progress_callback, "searching", run_id=summary.run_id, query=query, provider=provider_name)
                    try:
                        findings = provider.search(query)
                    except Exception as exc:
                        summary.errors[provider_name] = str(exc)
                        self._emit(progress_callback, "error", run_id=summary.run_id, provider=provider_name, error=str(exc))
                        continue

                    for finding in findings:
                        summary.raw_findings += 1
                        self._emit(progress_callback, "finding", run_id=summary.run_id, count=summary.raw_findings, source_url=finding.url, evidence=finding.snippet or finding.title)
                        result = self.evaluator.evaluate(finding)
                        if result.candidate is None:
                            summary.rejected_findings += 1
                            reason = result.rejection_reason or "rejected"
                            self.store.record_rejection(summary.run_id, reason, source_url=finding.url, evidence=finding.snippet or finding.title)
                            self._emit(progress_callback, "rejected", run_id=summary.run_id, reason=reason, rejected=summary.rejected_findings, source_url=finding.url)
                            continue

                        candidate = result.candidate
                        duplicate = self._already_exists(candidate.dedupe_key)
                        if duplicate:
                            summary.duplicate_merges += 1
                            self._emit(progress_callback, "duplicate", run_id=summary.run_id, duplicates=summary.duplicate_merges, source_url=finding.url)

                        summary.accepted_leads += 1
                        if candidate.classification is LeadClassification.HOT:
                            summary.hot_count += 1
                        elif candidate.classification is LeadClassification.WARM:
                            summary.warm_count += 1
                        else:
                            summary.prospect_count += 1
                        self._emit(progress_callback, "accepted", run_id=summary.run_id, classification=candidate.classification.value, accepted=summary.accepted_leads, hot=summary.hot_count, warm=summary.warm_count, prospect=summary.prospect_count, source_url=finding.url)

                        self.store.upsert_lead(candidate)
                        self._emit(progress_callback, "saved", run_id=summary.run_id, saved=summary.accepted_leads, source_url=finding.url)
        except Exception as exc:
            # A genuine failure (not a per-provider search error, which is
            # already caught above) must not be reported as "completed":
            # the old telemetry state drives the frontend's decision to
            # refresh results, and a failed run's partial counts are not a
            # trustworthy result.
            self.store.finish_run(summary, status="failed")
            self._emit(progress_callback, "failed", run_id=summary.run_id, error=f"{type(exc).__name__}: {exc}",
                       found=summary.raw_findings, rejected=summary.rejected_findings, accepted=summary.accepted_leads,
                       duplicates=summary.duplicate_merges, hot=summary.hot_count, warm=summary.warm_count,
                       prospect=summary.prospect_count)
            raise

        self.store.finish_run(summary, status="completed")
        self._emit(progress_callback, "completed", run_id=summary.run_id, found=summary.raw_findings, rejected=summary.rejected_findings, accepted=summary.accepted_leads, duplicates=summary.duplicate_merges, hot=summary.hot_count, warm=summary.warm_count, prospect=summary.prospect_count, errors=dict(summary.errors))
        return summary
