from copy import deepcopy
from threading import RLock
from time import time


def rejection_bucket(reason):
    text = str(reason or "").lower()
    if any(x in text for x in ("compet", "painting company", "existing painter")): return "competition"
    if any(x in text for x in ("director", "yellow pages", "directory")): return "directories"
    if any(x in text for x in ("advert", "marketing", "provider", "service page")): return "advertising"
    if any(x in text for x in ("job", "looking for work", "contractor seeking")): return "contractors"
    if any(x in text for x in ("stale", "old", "too old", "antigu")): return "stale"
    return "other"


class LeadHunterTelemetry:
    def __init__(self):
        self._lock=RLock(); self._snapshot=self._idle()

    @staticmethod
    def _idle():
        return {"state":"idle","run_id":None,"active_stage":None,"found":0,"analyzed":0,"rejected":0,"valid":0,"duplicates":0,"saved":0,"rejections":{"competition":0,"directories":0,"advertising":0,"contractors":0,"stale":0,"other":0},"classifications":{"HOT":0,"WARM":0,"PROSPECT":0},"query":None,"provider":None,"last_evidence":None,"updated_at":time(),"error":None}

    def publish(self,event):
        with self._lock:
            kind=event.get("type")
            if kind=="started":
                self._snapshot=self._idle(); self._snapshot.update(state="active",run_id=event.get("run_id"),active_stage="search")
            elif kind=="searching":
                self._snapshot.update(state="active",active_stage="search",query=event.get("query"),provider=event.get("provider"))
            elif kind=="finding":
                self._snapshot.update(active_stage="analyze",found=event.get("count",self._snapshot["found"]),last_evidence=event.get("evidence")); self._snapshot["analyzed"]+=1
            elif kind=="rejected":
                self._snapshot.update(active_stage="filter",rejected=event.get("rejected",self._snapshot["rejected"]+1)); bucket=rejection_bucket(event.get("reason")); self._snapshot["rejections"][bucket]+=1
            elif kind=="duplicate":
                self._snapshot.update(active_stage="dedupe",duplicates=event.get("duplicates",self._snapshot["duplicates"]+1))
            elif kind=="accepted":
                self._snapshot.update(active_stage="classify",valid=event.get("accepted",self._snapshot["valid"]+1)); c=event.get("classification");
                if c in self._snapshot["classifications"]: self._snapshot["classifications"][c]+=1
            elif kind=="saved": self._snapshot.update(active_stage="save",saved=event.get("saved",self._snapshot["saved"]+1))
            elif kind=="error": self._snapshot.update(error=event.get("error"))
            elif kind=="completed": self._snapshot.update(state="completed",active_stage="complete",found=event.get("found",self._snapshot["found"]),rejected=event.get("rejected",self._snapshot["rejected"]),valid=event.get("accepted",self._snapshot["valid"]),duplicates=event.get("duplicates",self._snapshot["duplicates"])); self._snapshot["classifications"]={"HOT":event.get("hot",0),"WARM":event.get("warm",0),"PROSPECT":event.get("prospect",0)}
            self._snapshot["updated_at"]=time()

    def snapshot(self):
        with self._lock: return deepcopy(self._snapshot)


lead_hunter_telemetry=LeadHunterTelemetry()
