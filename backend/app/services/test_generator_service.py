from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import (
    Test, Question, TransformedPrompt, PromptTestSection,
    RetrievalData, RetrievalInstructions, RetrivedChunk,
    Chunk, ChunkMetadata, GeneratedTestSection
)
from backend.app.services.embeddings_service import EmbeddingsService
import json
import ast


class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.search_service = SearchService()
        self.prompts = SystemPrompts()
        self.embeddings_service = EmbeddingsService()

    def __transform_request_to_prompt(self, topic: str):
        return self.ai_service.ask(self.prompts.get_transform_request_to_prompt(topic))

    def __fix_generated_section_with_AI(self, broken_response: str) -> str:
        fix_prompt = f"""Poniższy tekst powinien być poprawnym JSONem w formacie:
        {{"Question": {{"content": {{"instruction": "", "body": ""}}}}}}

        Zwróć WYŁĄCZNIE poprawny JSON, nic więcej. Bez markdown, bez tekstu przed ani po.

        Bardzo częstymi błędami są:
        - używanie '' zamiast ""
        - niedomykanie klamer i nawiasów

        Tekst do naprawy:
        {broken_response}"""
        return self.ai_service.ask(fix_prompt)

    def __parse_raw_to_section(self, raw: str) -> GeneratedTestSection:

        cleaned = raw.strip()
        for prefix in ["```json", "```"]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        cleaned = cleaned.removesuffix("```").strip()


        try:
            obj = ast.literal_eval(cleaned)
        except Exception:

            obj = json.loads(cleaned)

        content = obj["Question"]["content"]
        return GeneratedTestSection(
            instruction=str(content["instruction"]),
            body=str(content["body"])
        )

    def __generate_used_content_summary(self, section: GeneratedTestSection) -> str:
        """
        Generuje zwięzłe podsumowanie konkretnych zdań i słów użytych w sekcji,
        żeby model nie powtarzał tych samych treści.
        """
        prompt = f"""Wypisz TYLKO konkretne zdania, sytuacje i słowa kluczowe użyte w poniższym ćwiczeniu językowym.
            Celem jest poinformowanie innego modelu, czego absolutnie NIE MOŻE użyć w kolejnym ćwiczeniu.
            Bądź bardzo konkretny. Wypisz w punktach.
            Przykład dobrego formatu:
            - użyto czytania ze zrozumieniem
            - użyto zadania z wpisywaniem w luki
            - uzyto zadania abc

            Ćwiczenie do przeanalizowania:
            Instrukcja: {section.instruction}
            Treść: {section.body}"""
        return self.ai_service.ask(prompt)

    def generate_test(self, topic: str):
        transformed_prompt = self.__transform_request_to_prompt(topic)

        try:
            transformed_prompt = TransformedPrompt.model_validate(json.loads(transformed_prompt))
        except Exception as e:
            raise ValueError(f"Invalid TransformedPrompt: {e}")

        test_sections = []

        used_content_summaries: list[str] = []

        for test_section in transformed_prompt.sections:
            for i in range(test_section.amount):
                grammar_inst = []
                exercise_inst = []

                self.embeddings_service.embed_text(
                    f"{test_section.section_type}, {test_section.subject}"
                )

                grammar_records = self.search_service.get_points_with_subject(test_section.subject)
                instruction_records = self.search_service.get_points_with_subject(test_section.section_type)

                for grammar_record in grammar_records:
                    grammar_inst.append(RetrivedChunk(
                        payload=Chunk(
                            id=str(grammar_record.get("id", "")),
                            section="grammar",
                            language=grammar_record.get("language", "en"),
                            level=transformed_prompt.level,
                            metadata=ChunkMetadata(
                                subject=grammar_record.get("subject", ""),
                                content=grammar_record.get("content", "")
                            )
                        ),
                        score=None
                    ))

                for instruction_record in instruction_records:
                    exercise_inst.append(RetrivedChunk(
                        payload=instruction_record.payload,
                        score=None
                    ))

                retrieval_data = RetrievalData(
                    instructions=RetrievalInstructions(
                        grammar_instructions=grammar_inst,
                        exercise_instructions=exercise_inst
                    )
                )

                generate_exercise_prompt = self.prompts.get_section_generation_prompt(
                    retrieval_data,
                    topic,
                    used_content_summaries if used_content_summaries else None
                )

                generated_section = self.ai_service.ask(generate_exercise_prompt)

                # --- Retry loop ---
                raw = generated_section
                validated_obj = None

                for attempt in range(5):
                    try:
                        validated_obj = self.__parse_raw_to_section(raw)
                        break
                    except Exception as e:
                        print(f"[attempt {attempt + 1}/5] Parse failed: {e}")
                        raw = self.__fix_generated_section_with_AI(raw)
                else:
                    print(f"FAILED after 5 attempts, skipping section")
                    continue

                summary = self.__generate_used_content_summary(validated_obj)
                used_content_summaries.append(summary)
                print(f"[section {len(test_sections) + 1}] OK. Summary: {summary[:80]}...")

                test_sections.append(validated_obj)

        return test_sections