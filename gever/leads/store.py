import json
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .models import LeadCandidate, LeadClassification, LeadRecord, LeadStatus, OpportunityType, SearchRunSummary


def _now():
    return datetime.now().isoformat(timespec="seconds")


class LeadStore:
    def __init__(self, db_path=None):
        root = Path(__file__).resolve().parent.parent.parent
        self.db_path = Path(db_path) if db_path else root / "data" / "leads.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def _initialize(self):
        with self._connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS leads (
                lead_id TEXT PRIMARY KEY, dedupe_key TEXT NOT NULL UNIQUE, classification TEXT NOT NULL,
                urgent INTEGER NOT NULL, score REAL NOT NULL, status TEXT NOT NULL, opportunity_type TEXT NOT NULL,
                name TEXT, organization TEXT, location TEXT, service_requested_or_inferred TEXT, source_url TEXT NOT NULL,
                source_domain TEXT NOT NULL, source_title TEXT, evidence TEXT NOT NULL, published_at TEXT, discovered_at TEXT NOT NULL,
                public_contact_method TEXT, missing_information TEXT NOT NULL, recommended_action TEXT, validation_notes TEXT,
                first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS lead_evidence (id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id TEXT NOT NULL REFERENCES leads(lead_id) ON DELETE CASCADE, source_url TEXT NOT NULL, evidence TEXT NOT NULL, seen_at TEXT NOT NULL, UNIQUE(lead_id, source_url, evidence));
            CREATE TABLE IF NOT EXISTS search_runs (run_id TEXT PRIMARY KEY, trigger TEXT NOT NULL, started_at TEXT NOT NULL, ended_at TEXT, status TEXT NOT NULL DEFAULT 'completed', raw_findings INTEGER NOT NULL DEFAULT 0, accepted_leads INTEGER NOT NULL DEFAULT 0, rejected_findings INTEGER NOT NULL DEFAULT 0, duplicate_merges INTEGER NOT NULL DEFAULT 0, hot_count INTEGER NOT NULL DEFAULT 0, warm_count INTEGER NOT NULL DEFAULT 0, prospect_count INTEGER NOT NULL DEFAULT 0, errors TEXT NOT NULL DEFAULT '{}');
            CREATE TABLE IF NOT EXISTS rejected_findings (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, source_url TEXT, evidence TEXT, reason TEXT NOT NULL, rejected_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS lead_status_history (id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id TEXT NOT NULL REFERENCES leads(lead_id) ON DELETE CASCADE, old_status TEXT, new_status TEXT NOT NULL, changed_at TEXT NOT NULL);
            """)
            # Migration for databases created before the status column existed.
            existing_columns = {row["name"] for row in conn.execute("PRAGMA table_info(search_runs)")}
            if "status" not in existing_columns:
                conn.execute("ALTER TABLE search_runs ADD COLUMN status TEXT NOT NULL DEFAULT 'completed'")

    def upsert_lead(self, candidate: LeadCandidate):
        now = _now()
        with self._connect() as conn:
            existing = conn.execute("SELECT lead_id FROM leads WHERE dedupe_key = ?", (candidate.dedupe_key,)).fetchone()
            if existing:
                lead_id = existing["lead_id"]
                conn.execute("""UPDATE leads SET classification=?, urgent=?, score=?, last_seen_at=?, evidence=?, public_contact_method=COALESCE(?, public_contact_method), recommended_action=COALESCE(?, recommended_action), validation_notes=COALESCE(?, validation_notes) WHERE lead_id=?""", (candidate.classification.value, int(candidate.urgent), candidate.score, now, candidate.evidence, candidate.public_contact_method, candidate.recommended_action, candidate.validation_notes, lead_id))
            else:
                lead_id = str(uuid4())
                conn.execute("INSERT INTO leads VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (lead_id, candidate.dedupe_key, candidate.classification.value, int(candidate.urgent), candidate.score, LeadStatus.NEW.value, candidate.opportunity_type.value, candidate.name, candidate.organization, candidate.location, candidate.service_requested_or_inferred, candidate.source_url, candidate.source_domain, candidate.source_title, candidate.evidence, candidate.published_at, now, candidate.public_contact_method, json.dumps(candidate.missing_information, ensure_ascii=False), candidate.recommended_action, candidate.validation_notes, now, now))
                conn.execute("INSERT INTO lead_status_history(lead_id, old_status, new_status, changed_at) VALUES(?,?,?,?)", (lead_id, None, LeadStatus.NEW.value, now))
            conn.execute("INSERT OR IGNORE INTO lead_evidence(lead_id, source_url, evidence, seen_at) VALUES(?,?,?,?)", (lead_id, candidate.source_url, candidate.evidence, now))
        return self.get_lead(lead_id)

    def _record_from_row(self, conn, row):
        evidence = conn.execute("SELECT source_url, evidence, seen_at FROM lead_evidence WHERE lead_id=? ORDER BY id", (row["lead_id"],)).fetchall()
        return LeadRecord(lead_id=row["lead_id"], classification=LeadClassification(row["classification"]), urgent=bool(row["urgent"]), score=row["score"], status=LeadStatus(row["status"]), opportunity_type=OpportunityType(row["opportunity_type"]), source_url=row["source_url"], source_domain=row["source_domain"], evidence=row["evidence"], dedupe_key=row["dedupe_key"], name=row["name"], organization=row["organization"], location=row["location"], service_requested_or_inferred=row["service_requested_or_inferred"], source_title=row["source_title"], published_at=row["published_at"], public_contact_method=row["public_contact_method"], missing_information=json.loads(row["missing_information"] or "[]"), recommended_action=row["recommended_action"], validation_notes=row["validation_notes"], discovered_at=row["discovered_at"], first_seen_at=row["first_seen_at"], last_seen_at=row["last_seen_at"], evidence_history=[dict(item) for item in evidence])

    def get_lead(self, lead_id):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
            return self._record_from_row(conn, row) if row else None

    def list_leads(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM leads ORDER BY CASE WHEN classification='HOT' AND urgent=1 THEN 0 WHEN classification='HOT' THEN 1 WHEN classification='WARM' THEN 2 ELSE 3 END, score DESC, last_seen_at DESC").fetchall()
            return [self._record_from_row(conn, row) for row in rows]

    def latest_run(self):
        # Only a run that finished successfully should be reported as "the
        # latest search" to the user; a failed run stays recorded for
        # auditing but must not be presented as if it completed normally.
        with self._connect() as conn:
            row=conn.execute("SELECT * FROM search_runs WHERE ended_at IS NOT NULL AND status='completed' ORDER BY ended_at DESC, started_at DESC LIMIT 1").fetchone()
            return dict(row) if row else None

    def latest_run_including_failed(self):
        with self._connect() as conn:
            row=conn.execute("SELECT * FROM search_runs WHERE ended_at IS NOT NULL ORDER BY ended_at DESC, started_at DESC LIMIT 1").fetchone()
            return dict(row) if row else None

    def update_status(self, lead_id, status):
        status = status if isinstance(status, LeadStatus) else LeadStatus(status); now = _now()
        with self._connect() as conn:
            row = conn.execute("SELECT status FROM leads WHERE lead_id=?", (lead_id,)).fetchone()
            if not row: return None
            old = row["status"]; conn.execute("UPDATE leads SET status=? WHERE lead_id=?", (status.value, lead_id)); conn.execute("INSERT INTO lead_status_history(lead_id, old_status, new_status, changed_at) VALUES(?,?,?,?)", (lead_id, old, status.value, now))
        return self.get_lead(lead_id)

    def start_run(self, trigger):
        summary = SearchRunSummary(run_id=str(uuid4()), trigger=trigger, started_at=_now())
        with self._connect() as conn: conn.execute("INSERT INTO search_runs(run_id, trigger, started_at) VALUES(?,?,?)", (summary.run_id, trigger, summary.started_at))
        return summary

    def finish_run(self, summary: SearchRunSummary, status: str = "completed"):
        summary.ended_at = summary.ended_at or _now()
        with self._connect() as conn: conn.execute("UPDATE search_runs SET ended_at=?, status=?, raw_findings=?, accepted_leads=?, rejected_findings=?, duplicate_merges=?, hot_count=?, warm_count=?, prospect_count=?, errors=? WHERE run_id=?", (summary.ended_at, status, summary.raw_findings, summary.accepted_leads, summary.rejected_findings, summary.duplicate_merges, summary.hot_count, summary.warm_count, summary.prospect_count, json.dumps(summary.errors, ensure_ascii=False), summary.run_id))
        return summary

    def record_rejection(self, run_id, reason, source_url=None, evidence=None):
        with self._connect() as conn: conn.execute("INSERT INTO rejected_findings(run_id, source_url, evidence, reason, rejected_at) VALUES(?,?,?,?,?)", (run_id, source_url, evidence, reason, _now()))
