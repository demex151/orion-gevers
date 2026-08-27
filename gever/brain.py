import os
import json
import unicodedata

from dotenv import load_dotenv
from openai import OpenAI

from gever.identity import SYSTEM_PROMPT
from gever.memory import GeversMemory


load_dotenv()

MODEL = os.getenv("NVIDIA_MODEL")
BASE_URL = os.getenv("NVIDIA_BASE_URL")
API_KEY = os.getenv("NVIDIA_API_KEY")


if not API_KEY:
    raise RuntimeError("No se encontró NVIDIA_API_KEY en .env")

if not MODEL:
    raise RuntimeError("No se encontró NVIDIA_MODEL en .env")

if not BASE_URL:
    raise RuntimeError("No se encontró NVIDIA_BASE_URL en .env")


client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


class GeversBrain:

    LEAD_HUNTER_SIGNALS = (
        "busca clientes",
        "buscar clientes",
        "busca oportunidades",
        "buscar oportunidades",
        "busca leads",
        "buscar leads",
        "clientes de pintura",
        "oportunidades de clientes",
        "find painting leads",
        "find clients",
        "find leads",
    )

    def __init__(self):
        self.memory = GeversMemory()
        self.lead_hunter = None

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    @staticmethod
    def _normalize_command(text):
        normalized = unicodedata.normalize("NFKD", str(text or ""))
        normalized = "".join(
            char for char in normalized
            if not unicodedata.combining(char)
        )
        return " ".join(normalized.lower().split())

    def _is_lead_hunter_command(self, user_message):
        normalized = self._normalize_command(user_message)
        return any(signal in normalized for signal in self.LEAD_HUNTER_SIGNALS)

    def _run_lead_hunter(self):
        if self.lead_hunter is None:
            from run_lead_hunter import build_hunter
            self.lead_hunter, _ = build_hunter()

        summary = self.lead_hunter.run(trigger="voice")

        if summary.accepted_leads == 0:
            return (
                f"Búsqueda completada. Revisé {summary.raw_findings} resultados "
                f"y no encontré ninguna oportunidad válida y reciente. "
                f"Rechacé {summary.rejected_findings} resultados que no cumplían los filtros."
            )

        return (
            f"Búsqueda completada. Encontré {summary.accepted_leads} oportunidades válidas "
            f"de {summary.raw_findings} resultados revisados. "
            f"HOT: {summary.hot_count}, WARM: {summary.warm_count}, "
            f"PROSPECT: {summary.prospect_count}."
        )

    def _clean_answer(self, answer):
        if not answer:
            return ""

        if "</think>" in answer:
            answer = answer.split("</think>", 1)[1].strip()

        return answer.strip()

    def _memory_context(self):
        memories = self.memory.get_context(limit=30)

        return f"""
MEMORIA PERMANENTE DE GEVER:

{memories}

REGLAS:
- Usa estas memorias solo cuando sean relevantes.
- No inventes recuerdos.
- Si el usuario corrige información anterior,
  utiliza la versión más reciente.
- Si una memoria fue eliminada, no la presentes
  como información conocida.
"""

    def _analyze_memory_action(self, user_message):
        existing_memories = self.memory.get_all()

        memory_list = [
            {
                "id": memory.get("id"),
                "content": memory.get("content", ""),
                "category": memory.get("category", "general")
            }
            for memory in existing_memories
        ]

        memory_prompt = f"""
Eres el administrador de memoria de GEVER.

Decide qué hacer con el mensaje del usuario.

MEMORIAS EXISTENTES:

{json.dumps(memory_list, ensure_ascii=False, indent=2)}

ACCIONES:

NONE
No modificar memoria.

CREATE
Crear una memoria nueva.

UPDATE
Actualizar una memoria existente.

DELETE
Eliminar una memoria existente cuando el usuario
pida claramente olvidar, borrar o dejar de recordar algo.

Información válida para memoria:
- preferencias estables
- objetivos
- negocios
- proyectos
- decisiones
- hechos personales o profesionales útiles

No guardar:
- conversación casual
- estados temporales
- deseos momentáneos
- saludos
- información trivial

Categorías:
preference
goal
business
decision
fact

Responde SOLO JSON válido.

NONE:

{{
    "action": "none"
}}

CREATE:

{{
    "action": "create",
    "category": "goal",
    "content": "memoria clara"
}}

UPDATE:

{{
    "action": "update",
    "memory_id": "mem_2",
    "category": "goal",
    "new_content": "memoria actualizada"
}}

DELETE:

{{
    "action": "delete",
    "memory_id": "mem_1"
}}

REGLAS:
- Usa únicamente IDs existentes.
- No inventes IDs.
- Si el usuario dice "olvida", "borra", "no recuerdes",
  "elimina de tu memoria" o equivalente, usa DELETE
  si existe una memoria correspondiente.
- Si el usuario corrige algo, usa UPDATE.
- Si no hay nada relevante, usa NONE.
- No escribas markdown.
- No des explicaciones.
"""

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": memory_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.1,
                max_tokens=350,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": False
                    }
                },
            )

            raw = response.choices[0].message.content or ""
            raw = self._clean_answer(raw)
            raw = raw.replace("```json", "").replace("```", "").strip()

            return json.loads(raw)

        except Exception:
            return {"action": "none"}

    def _process_memory(self, user_message):
        result = self._analyze_memory_action(user_message)

        action = str(
            result.get("action", "none")
        ).strip().lower()

        allowed_categories = {
            "preference",
            "goal",
            "business",
            "decision",
            "fact",
        }

        if action == "create":
            category = str(
                result.get("category", "")
            ).strip().lower()

            content = str(
                result.get("content", "")
            ).strip()

            if category not in allowed_categories:
                return False

            if not content:
                return False

            return self.memory.remember(
                content=content,
                category=category,
                source="automatic"
            )

        if action == "update":
            memory_id = str(
                result.get("memory_id", "")
            ).strip()

            new_content = str(
                result.get("new_content", "")
            ).strip()

            category = str(
                result.get("category", "")
            ).strip().lower()

            existing_ids = {
                memory.get("id")
                for memory in self.memory.get_all()
            }

            if memory_id not in existing_ids:
                return False

            if not new_content:
                return False

            if category not in allowed_categories:
                category = None

            return self.memory.update_by_id(
                memory_id=memory_id,
                new_content=new_content,
                category=category
            )

        if action == "delete":
            memory_id = str(
                result.get("memory_id", "")
            ).strip()

            existing_ids = {
                memory.get("id")
                for memory in self.memory.get_all()
            }

            if memory_id not in existing_ids:
                return False

            return self.memory.forget_by_id(
                memory_id
            )

        return False

    def think(self, user_message):
        if self._is_lead_hunter_command(user_message):
            try:
                return self._run_lead_hunter()
            except Exception as e:
                return f"No pude ejecutar Lead Hunter: {e}"

        memory_context = self._memory_context()

        messages_for_model = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "system",
                "content": memory_context
            }
        ]

        messages_for_model.extend(
            self.messages[1:]
        )

        messages_for_model.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages_for_model,
                temperature=1.0,
                top_p=0.95,
                max_tokens=1200,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": False
                    }
                },
            )

            answer = response.choices[0].message.content or ""
            answer = self._clean_answer(answer)

            self.messages.append(
                {
                    "role": "user",
                    "content": user_message
                }
            )

            self.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            self._process_memory(user_message)

            return answer

        except Exception as e:
            return (
                "Error al comunicarme con mi motor "
                f"de inteligencia: {e}"
            )

    def remember(self, content, category="manual"):
        return self.memory.remember(
            content=content,
            category=category,
            source="manual"
        )

    def memories(self):
        return self.memory.get_all()