import json
from pathlib import Path
from datetime import datetime


ALLOWED_CATEGORIES = {
    "manual",
    "preference",
    "goal",
    "business",
    "decision",
    "fact",
    "general",
}


class GeversMemory:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.memory_file = self.data_dir / "memory.json"
        self.memories = self._load()

        self._ensure_ids()

    def _load(self):
        if not self.memory_file.exists():
            return []

        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except (json.JSONDecodeError, OSError):
            return []

    def _save(self):
        with open(self.memory_file, "w", encoding="utf-8") as file:
            json.dump(
                self.memories,
                file,
                ensure_ascii=False,
                indent=4
            )

    def _ensure_ids(self):
        changed = False
        used_ids = set()

        for memory in self.memories:
            memory_id = memory.get("id")

            if memory_id:
                used_ids.add(memory_id)

        next_number = 1

        for memory in self.memories:
            if not memory.get("id"):
                while f"mem_{next_number}" in used_ids:
                    next_number += 1

                memory["id"] = f"mem_{next_number}"
                used_ids.add(memory["id"])
                next_number += 1
                changed = True

        if changed:
            self._save()

    def _next_id(self):
        numbers = []

        for memory in self.memories:
            memory_id = memory.get("id", "")

            if memory_id.startswith("mem_"):
                try:
                    numbers.append(
                        int(memory_id.split("_", 1)[1])
                    )
                except ValueError:
                    pass

        if not numbers:
            return "mem_1"

        return f"mem_{max(numbers) + 1}"

    def remember(
        self,
        content,
        category="general",
        source="manual"
    ):
        content = content.strip()
        category = category.strip().lower()
        source = source.strip().lower()

        if not content:
            return False

        if category not in ALLOWED_CATEGORIES:
            category = "general"

        normalized = content.casefold()

        for memory in self.memories:
            existing = memory.get(
                "content",
                ""
            ).strip().casefold()

            if existing == normalized:
                return False

        memory = {
            "id": self._next_id(),
            "content": content,
            "category": category,
            "source": source,
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "updated_at": None
        }

        self.memories.append(memory)
        self._save()

        return True

    def update_by_id(
        self,
        memory_id,
        new_content,
        category=None
    ):
        memory_id = memory_id.strip()
        new_content = new_content.strip()

        if not memory_id or not new_content:
            return False

        for memory in self.memories:
            if memory.get("id") == memory_id:
                memory["content"] = new_content

                if category:
                    category = category.strip().lower()

                    if category in ALLOWED_CATEGORIES:
                        memory["category"] = category

                memory["updated_at"] = datetime.now().isoformat(
                    timespec="seconds"
                )

                self._save()
                return True

        return False

    def forget_by_id(self, memory_id):
        memory_id = memory_id.strip()

        if not memory_id:
            return False

        original_count = len(self.memories)

        self.memories = [
            memory
            for memory in self.memories
            if memory.get("id") != memory_id
        ]

        if len(self.memories) == original_count:
            return False

        self._save()
        return True

    def get_all(self):
        return self.memories.copy()

    def get_context(self, limit=30):
        if not self.memories:
            return "No hay memorias permanentes guardadas."

        selected = self.memories[-limit:]
        lines = []

        for memory in selected:
            memory_id = memory.get("id", "sin_id")
            category = memory.get("category", "general")
            content = memory.get("content", "")

            lines.append(
                f"- [{memory_id}] [{category}] {content}"
            )

        return "\n".join(lines)

    def forget_all(self):
        self.memories = []
        self._save()