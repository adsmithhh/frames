# Task_Loader.py - IMPROVED VERSION with proper response_contract conversion
# Outputs exact unified contract that AnalysisEngine expects

from copy import deepcopy
from pathlib import Path
import yaml

# Import TaskPackage at the top
from TaskPackage import TaskPackage


class TaskLoader:

    def load_yaml(self, filename):
        path = Path(filename)
        if not path.exists():
            raise FileNotFoundError(f"Cannot find: {filename}")
        
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    
    def validate_configuration(self, configuration):
        """Validate experiment_configuration.yaml."""
        if not isinstance(configuration, dict):
            raise ValueError("Configuration must be a dictionary")

        required_sections = ["framework", "model", "execution", "experiment_binding"]
        for section in required_sections:
            if section not in configuration:
                raise ValueError(f"Missing required section: {section}")

        payload_file = (
            configuration.get("experiment_binding", {}).get("payload_file")
            or configuration.get("task", {}).get("payload_file")
        )
        if not payload_file:
            raise ValueError("A payload file reference is required in experiment_binding.payload_file or task.payload_file")
        
        return True
    
    def validate_payload(self, payload):
        """Validate task_payload.yaml against the active runtime contract."""
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary.")

        required_sections = ["experiment", "instructions", "stimuli"]
        for section in required_sections:
            if section not in payload:
                raise ValueError(f"Payload missing required section: '{section}'")

        experiment = payload.get("experiment", {})
        for field in ["id", "name", "version"]:
            if field not in experiment:
                raise ValueError(f"Payload experiment section missing required field: '{field}'")

        if not isinstance(payload.get("stimuli"), list):
            raise ValueError("Payload stimuli must be a list.")

        return True

    def normalize_payload(self, payload):
        """Normalize payload to unified format that all components can use."""
        # If v2 format, convert to unified format
        if "payload" in payload and "schema" in payload["payload"]:
            normalized = self._convert_v2_to_unified(payload)
        else:
            # If legacy format, ensure it has unified structure
            normalized = self._ensure_unified_structure(payload)
        
        return normalized

    def _convert_v2_to_unified(self, payload):
        """Convert v2 format to PURE unified format (no runtime control)."""
        unified = {
            "experiment": payload.get("experiment", {}),
            "protocol": self._normalize_protocol(payload.get("protocol", {}), payload.get("instructions", {})),
            "instructions": self._normalize_instructions(payload.get("instructions", {}), payload.get("stimulus_schema", {})),
            "stimulus_schema": self._normalize_stimulus_schema(payload.get("stimulus_schema", {}), payload.get("stimuli", [])),
            "response_contract": self._normalize_response_contract(
                payload.get("response_contract"),
                payload.get("response", {}),
            ),
            "metrics": self._normalize_metrics(
                payload.get("metrics"),
                payload.get("evaluation", {}),
                payload.get("response_contract"),
                payload.get("response", {}),
            ),
            "stimuli": payload.get("stimuli", []),
            "response": payload.get("response", {}),
            "evaluation": payload.get("evaluation", {}),
            "parser": payload.get("parser", {}),
            "resources": payload.get("resources", {})
        }
        
        return unified

    def _normalize_protocol(self, protocol, instructions):
        normalized = dict(protocol or {})
        normalized.setdefault(
            "role",
            instructions.get("system_role", "experimental subject"),
        )
        normalized.setdefault("goal", "Follow instructions exactly.")
        normalized.setdefault("rules", [])
        return normalized

    def _normalize_instructions(self, instructions, stimulus_schema):
        normalized = dict(instructions or {})
        task_text = (
            normalized.get("task")
            or normalized.get("task_detail")
            or normalized.get("task_brief")
            or ""
        )
        normalized["task"] = str(task_text).strip()
        normalized.setdefault("response_format", "Provide your answer.")
        normalized.setdefault("closing_prompt", "Please provide your answer now.")

        if "example" not in normalized:
            examples = normalized.get("examples", [])
            if examples:
                first_example = dict(examples[0])
                normalized["example"] = {
                    "stimulus": first_example.get("stimulus", {}),
                    "correct_response": first_example.get("expected_response", ""),
                }

        if "stimulus_template" not in normalized:
            display_config = normalized.get("display", {})
            field_order = display_config.get("field_order", [])
            template = {}
            for field_name in field_order:
                template[field_name] = "<trial stimulus>"
            if not template:
                for field in stimulus_schema.get("fields", []) or []:
                    if field.get("display", True):
                        template[field.get("name")] = "<trial stimulus>"
            normalized["stimulus_template"] = template

        return normalized

    def _normalize_stimulus_schema(self, stimulus_schema, stimuli):
        if stimulus_schema:
            normalized = deepcopy(stimulus_schema)
            normalized.setdefault("id_field", "id")
            normalized.setdefault("fields", [])
            return normalized

        fields = []
        if stimuli:
            first_stimulus = stimuli[0]
            for key in first_stimulus.keys():
                if key != "id":
                    fields.append(
                        {
                            "name": key,
                            "type": "string",
                            "required": True,
                            "display": True,
                        }
                    )

        return {
            "id_field": "id",
            "fields": fields,
        }

    def _normalize_response_contract(self, response_contract, legacy_response):
        if response_contract and any(
            key in response_contract
            for key in ["extraction", "normalization", "validation", "expected_answer", "accepted_answer_space"]
        ):
            normalized = deepcopy(response_contract)
            extraction = dict(normalized.get("extraction", {}))
            extraction.setdefault("mode", normalized.get("extraction_mode", "last_token"))
            extraction.setdefault("regex", None)
            normalized["extraction"] = extraction

            normalization = normalized.get("normalization", {})
            if not isinstance(normalization, dict):
                normalization = {"case": normalization}
            normalization.setdefault("case", normalized.get("normalization_mode", "upper"))
            normalization.setdefault("trim_whitespace", True)
            normalization.setdefault("strip_punctuation", True)
            normalized["normalization"] = normalization

            validation = dict(normalized.get("validation", {}))
            validation.setdefault(
                "require_exactly_one_answer",
                normalized.get("require_exactly_one_answer", True),
            )
            validation.setdefault("allow_explanation", normalized.get("allow_explanation", False))
            validation.setdefault("allow_justification", normalized.get("allow_justification", False))
            validation.setdefault("allow_analysis", normalized.get("allow_analysis", False))
            validation.setdefault("allow_questions", normalized.get("allow_questions", False))
            validation.setdefault("allow_additional_text", normalized.get("allow_additional_text", False))
            validation.setdefault("allow_multiple_answers", normalized.get("allow_multiple_answers", False))
            normalized["validation"] = validation

            if "expected_answer" not in normalized and "expected_response" in normalized:
                expected = normalized.get("expected_response", {})
                normalized["expected_answer"] = self._normalize_expected_answer(expected)

            if "accepted_answer_space" not in normalized:
                accepted_values = normalized.get("allowed_values", [])
                normalized["accepted_answer_space"] = {
                    "source": "explicit_list",
                    "values": list(accepted_values),
                    "stimulus_fields": list(normalized.get("allowed_stimulus_fields", [])),
                }

            normalized.setdefault(
                "allowed_values",
                list(normalized.get("accepted_answer_space", {}).get("values", [])),
            )
            normalized.setdefault(
                "allowed_stimulus_fields",
                list(normalized.get("accepted_answer_space", {}).get("stimulus_fields", [])),
            )
            normalized.setdefault("aliases", {})
            return {}

        legacy_response = legacy_response or response_contract or {}
        unified_contract = {
            "extraction": {
                "mode": legacy_response.get("extraction_mode", "last_token"),
                "regex": legacy_response.get("regex", None)
            },
            "normalization": {
                "case": legacy_response.get("normalization", "upper"),
                "trim_whitespace": legacy_response.get("trim_whitespace", True),
                "strip_punctuation": legacy_response.get("strip_punctuation", True)
            },
            "validation": {
                "require_exactly_one_answer": legacy_response.get("require_exactly_one_answer", True),
                "allow_explanation": legacy_response.get("allow_explanation", False),
                "allow_justification": legacy_response.get("allow_justification", False),
                "allow_analysis": legacy_response.get("allow_analysis", False),
                "allow_questions": legacy_response.get("allow_questions", False),
                "allow_additional_text": legacy_response.get("allow_additional_text", False),
                "allow_multiple_answers": legacy_response.get("allow_multiple_answers", False)
            }
        }

        if "expected_response" in legacy_response:
            unified_contract["expected_answer"] = self._normalize_expected_answer(
                legacy_response["expected_response"]
            )

        accepted_answer_space = {
            "source": "explicit_list",
            "values": list(legacy_response.get("allowed_values", [])),
            "stimulus_fields": list(
                legacy_response.get("protocol_adherence", {}).get(
                    "allowed_stimulus_fields",
                    legacy_response.get("allowed_stimulus_fields", []),
                )
            ),
        }
        if accepted_answer_space["values"] or accepted_answer_space["stimulus_fields"]:
            unified_contract["accepted_answer_space"] = {
                "source": accepted_answer_space["source"],
                "values": accepted_answer_space["values"],
                "stimulus_fields": accepted_answer_space["stimulus_fields"],
            }
        unified_contract["allowed_values"] = accepted_answer_space["values"]
        unified_contract["allowed_stimulus_fields"] = accepted_answer_space["stimulus_fields"]
        unified_contract["aliases"] = {}
        return unified_contract

    def _normalize_expected_answer(self, expected):
        if expected.get("source") == "literal":
            return {
                "source": "literal",
                "value": expected.get("value"),
            }

        return {
            "source": "stimulus_field",
            "field": expected.get("field"),
        }

    def _normalize_metrics(self, metrics, legacy_evaluation, response_contract, legacy_response):
        if isinstance(metrics, dict) and "enabled" in metrics:
            normalized = deepcopy(metrics)
            normalized.setdefault("definitions", {})
            normalized.setdefault("aggregation", {})
            return normalized

        if not legacy_evaluation and not metrics:
            return {
                "enabled": ["accuracy", "response_time"],
                "definitions": {},
                "aggregation": {},
            }

        normalized_response_contract = self._normalize_response_contract(
            response_contract,
            legacy_response,
        )
        expected_answer = normalized_response_contract.get("expected_answer", {})
        expected_field = expected_answer.get("field", "id")
        accepted_answer_space = normalized_response_contract.get("accepted_answer_space", {})

        source_metrics = legacy_evaluation or metrics or {}
        unified_metrics = {
            "enabled": [],
            "definitions": {},
            "aggregation": {},
        }

        accuracy_config = source_metrics.get("accuracy", {})
        if accuracy_config is not False:
            unified_metrics["enabled"].append("accuracy")
            unified_metrics["definitions"]["accuracy"] = {
                "type": "exact_match",
                "expected_answer_source": {
                    "source": "stimulus_field",
                    "field": expected_field
                }
            }

        protocol_config = source_metrics.get("protocol_adherence", {})
        if protocol_config:
            unified_metrics["enabled"].append("protocol_adherence")
            unified_metrics["definitions"]["protocol_adherence"] = {
                "type": "allowed_response_check",
                "allowed_response_source": {
                    "source": "explicit_list",
                    "values": list(
                        protocol_config.get(
                            "allowed_values",
                            accepted_answer_space.get("values", []),
                        )
                    ),
                    "stimulus_fields": list(
                        protocol_config.get(
                            "stimulus_fields",
                            accepted_answer_space.get("stimulus_fields", []),
                        )
                    ),
                },
                "require_single_token": protocol_config.get(
                    "require_single_token",
                    True,
                ),
            }

        unified_metrics["enabled"].append("response_time")
        unified_metrics["definitions"]["response_time"] = {
            "type": "latency",
            "unit": "seconds",
        }
        unified_metrics["aggregation"] = {
            "accuracy_rate": {"from_metric": "accuracy", "reducer": "mean_boolean"},
            "protocol_adherence_rate": {
                "from_metric": "protocol_adherence",
                "reducer": "mean_boolean",
            },
            "average_response_time_seconds": {
                "from_metric": "response_time",
                "reducer": "mean",
            },
        }
        return unified_metrics

    def _ensure_unified_structure(self, payload):
        """Ensure legacy payload has PURE unified structure (no runtime control)."""
        unified = deepcopy(payload)
        
        # === Add missing unified fields with defaults ===
        
        # 1. Response Contract (FIXED)
        if "response_contract" not in unified:
            unified["response_contract"] = self._normalize_response_contract(
                None,
                unified.get("response", {}),
            )
        else:
            unified["response_contract"] = self._normalize_response_contract(
                unified.get("response_contract", {}),
                unified.get("response", {}),
            )
        
        # 2. Stimulus Schema (create from legacy stimuli)
        if "stimulus_schema" not in unified:
            if "stimuli" in unified and unified["stimuli"]:
                first_stimulus = unified["stimuli"][0]
                fields = []
                for key in first_stimulus.keys():
                    if key != "id":  # Skip ID field
                        fields.append({
                            "name": key,
                            "type": "string",
                            "required": True,
                            "display": True
                        })
                
                unified["stimulus_schema"] = {
                    "id_field": "id",
                    "fields": fields
                }
            else:
                unified["stimulus_schema"] = {
                    "id_field": "id",
                    "fields": []
                }
        
        # 3. Metrics (FIXED)
        if "metrics" not in unified:
            unified["metrics"] = self._normalize_metrics(
                None,
                unified.get("evaluation", {}),
                unified.get("response_contract", {}),
                unified.get("response", {}),
            )
        else:
            unified["metrics"] = self._normalize_metrics(
                unified.get("metrics", {}),
                unified.get("evaluation", {}),
                unified.get("response_contract", {}),
                unified.get("response", {}),
            )
        
        # 4. Protocol (add if missing)
        if "protocol" not in unified:
            unified["protocol"] = {
                "role": "experimental subject",
                "goal": "Follow instructions exactly.",
                "rules": ["Answer as instructed."]
            }
        
        # 5. Instructions (ensure complete structure)
        if "instructions" not in unified:
            unified["instructions"] = {
                "task": "",
                "response_format": "Provide your answer.",
                "example": {},
                "closing_prompt": "Please provide your answer now."
            }
        else:
            unified["instructions"] = self._normalize_instructions(
                unified["instructions"],
                unified.get("stimulus_schema", {}),
            )
        
        # === Remove runtime control fields from legacy payload ===
        runtime_fields = ["execution", "model"]
        for field in runtime_fields:
            if field in unified:
                del unified[field]
        
        return unified

    def _build_task_package(self, configuration, normalized_payload):
        """Build TaskPackage from PURE unified payload."""
        return TaskPackage(
            metadata=normalized_payload.get("experiment", {}),
            system_prompt=self._build_system_prompt(normalized_payload),
            user_prompt="",
            parser_config=normalized_payload.get("parser", {}),
            metrics_config=normalized_payload.get("metrics", {}),
            payload=normalized_payload,
            ground_truth=self._extract_ground_truth(normalized_payload),
            stimuli=self._extract_stimuli(normalized_payload),
            resources=normalized_payload.get("resources", {})
        )
    
    def _build_system_prompt(self, payload):
        """Build system prompt from unified payload."""
        protocol = payload.get("protocol", {})
        instructions = payload.get("instructions", {})
        
        system_prompt = f"You are a {protocol.get('role', 'research participant')}.\n\n"
        system_prompt += f"Goal: {protocol.get('goal', 'Follow instructions exactly.')}\n\n"
        system_prompt += "Rules:\n"
        
        for rule in protocol.get('rules', []):
            system_prompt += f"- {rule}\n"
        
        if instructions.get('task'):
            system_prompt += f"\nTask: {instructions['task']}\n"
        
        return system_prompt

    def _extract_ground_truth(self, payload):
        """Extract ground truth from unified payload."""
        ground_truth = {}
        
        response_contract = payload.get("response_contract", {})
        if "expected_answer" in response_contract:
            expected = response_contract["expected_answer"]
            if expected.get("source") == "stimulus_field":
                field_name = expected.get("field")
                ground_truth["expected_field"] = field_name
        
        return ground_truth

    def _extract_stimuli(self, payload):
        """Extract stimuli from unified payload."""
        stimuli = {}
        stimulus_schema = payload.get("stimulus_schema", {})
        id_field = stimulus_schema.get("id_field", "id")
        
        for stimulus in payload.get("stimuli", []):
            if id_field in stimulus:
                stim_id = stimulus[id_field]
                stimuli[stim_id] = stimulus
        
        return stimuli
    
    def _resolve_payload_path(self, configuration):
        """Resolve payload file path from configuration."""
        binding_config = configuration.get("experiment_binding", {})
        task_config = configuration.get("task", {})
        payload_file = (
            binding_config.get("payload_file")
            or task_config.get("payload_file")
            or "task_payload.yaml"
        )
        return Path(payload_file)

    def load(self, configuration):
        """Load task package from configuration and payload files."""
        # Validate configuration
        self.validate_configuration(configuration)
        
        # Resolve and load payload
        payload_path = self._resolve_payload_path(configuration)
        payload = self.load_yaml(payload_path)
        
        # Validate payload
        self.validate_payload(payload)
        
        # Normalize payload to PURE unified format
        normalized_payload = self.normalize_payload(payload)
        
        # Build and return TaskPackage
        return self._build_task_package(configuration, normalized_payload)
    
    def load_from_files(self, config_file, payload_file):
        """Convenience method to load from specific files."""
        configuration = self.load_yaml(config_file)
        configuration.setdefault("experiment_binding", {})
        configuration["experiment_binding"]["payload_file"] = str(payload_file)
        configuration.setdefault("task", {})
        configuration["task"]["payload_file"] = str(payload_file)
        return self.load(configuration)
