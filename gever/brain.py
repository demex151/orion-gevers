import os
import json
import unicodedata

from dotenv import load_dotenv
from openai import OpenAI

from gever.identity import SYSTEM_PROMPT
from gever.memory import GeversMemory

load_dotenv()
MODEL=os.getenv("NVIDIA_MODEL"); BASE_URL=os.getenv("NVIDIA_BASE_URL"); API_KEY=os.getenv("NVIDIA_API_KEY")
if not API_KEY: raise RuntimeError("No se encontró NVIDIA_API_KEY en .env")
if not MODEL: raise RuntimeError("No se encontró NVIDIA_MODEL en .env")
if not BASE_URL: raise RuntimeError("No se encontró NVIDIA_BASE_URL en .env")
client=OpenAI(base_url=BASE_URL,api_key=API_KEY)

class GeversBrain:
    LEAD_HUNTER_SIGNALS=("busca clientes","buscar clientes","busca oportunidades","buscar oportunidades","busca leads","buscar leads","clientes de pintura","oportunidades de clientes","find painting leads","find clients","find leads")
    def __init__(self):
        self.memory=GeversMemory(); self.lead_hunter=None; self.messages=[{"role":"system","content":SYSTEM_PROMPT}]
    @staticmethod
    def _normalize_command(text):
        normalized=unicodedata.normalize("NFKD",str(text or "")); normalized="".join(c for c in normalized if not unicodedata.combining(c)); return " ".join(normalized.lower().split())
    def _is_lead_hunter_command(self,user_message): return any(s in self._normalize_command(user_message) for s in self.LEAD_HUNTER_SIGNALS)
    def _run_lead_hunter(self):
        if self.lead_hunter is None:
            from run_lead_hunter import build_hunter
            self.lead_hunter,_=build_hunter()
        from gever.leads.telemetry import lead_hunter_telemetry
        summary=self.lead_hunter.run(trigger="voice",progress_callback=lead_hunter_telemetry.publish)
        if summary.accepted_leads==0: return f"Búsqueda completada. Revisé {summary.raw_findings} resultados y no encontré ninguna oportunidad válida y reciente. Rechacé {summary.rejected_findings} resultados que no cumplían los filtros."
        return f"Búsqueda completada. Encontré {summary.accepted_leads} oportunidades válidas de {summary.raw_findings} resultados revisados. HOT: {summary.hot_count}, WARM: {summary.warm_count}, PROSPECT: {summary.prospect_count}."
    def _clean_answer(self,answer):
        if not answer:return ""
        if "</think>" in answer: answer=answer.split("</think>",1)[1].strip()
        return answer.strip()
    def _memory_context(self):
        memories=self.memory.get_context(limit=30)
        return f"""MEMORIA PERMANENTE DE GEVER:\n\n{memories}\n\nREGLAS:\n- Usa estas memorias solo cuando sean relevantes.\n- No inventes recuerdos.\n- Si el usuario corrige información anterior, utiliza la versión más reciente.\n- Si una memoria fue eliminada, no la presentes como información conocida."""
    def _analyze_memory_action(self,user_message):
        existing_memories=self.memory.get_all(); memory_list=[{"id":m.get("id"),"content":m.get("content",""),"category":m.get("category","general")} for m in existing_memories]
        memory_prompt=f"""Eres el administrador de memoria de GEVER. Decide qué hacer con el mensaje del usuario.\nMEMORIAS EXISTENTES:\n{json.dumps(memory_list,ensure_ascii=False,indent=2)}\nACCIONES: NONE, CREATE, UPDATE, DELETE.\nInformación válida: preferencias estables, objetivos, decisiones, hechos útiles.\nResponde SOLO JSON con action, id, content, category."""
        try:
            r=client.chat.completions.create(model=MODEL,messages=[{"role":"system","content":memory_prompt},{"role":"user","content":user_message}],temperature=0.1,max_tokens=300)
            raw=self._clean_answer(r.choices[0].message.content); start=raw.find("{"); end=raw.rfind("}"); return json.loads(raw[start:end+1]) if start>=0 and end>=start else {"action":"NONE"}
        except Exception:return {"action":"NONE"}
    def _apply_memory_action(self,action):
        kind=str(action.get("action","NONE")).upper()
        try:
            if kind=="CREATE" and action.get("content"): self.memory.add(action["content"],action.get("category","general"))
            elif kind=="UPDATE" and action.get("id") and action.get("content"): self.memory.update(action["id"],action["content"],action.get("category","general"))
            elif kind=="DELETE" and action.get("id"): self.memory.delete(action["id"])
        except Exception: pass
    def think(self,user_message):
        if self._is_lead_hunter_command(user_message): return self._run_lead_hunter()
        memory_context=self._memory_context(); action=self._analyze_memory_action(user_message); self._apply_memory_action(action)
        messages=[self.messages[0],{"role":"system","content":memory_context},*self.messages[1:],{"role":"user","content":user_message}]
        response=client.chat.completions.create(model=MODEL,messages=messages,temperature=0.55,max_tokens=900)
        answer=self._clean_answer(response.choices[0].message.content); self.messages.append({"role":"user","content":user_message}); self.messages.append({"role":"assistant","content":answer}); return answer
