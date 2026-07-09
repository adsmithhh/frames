import yaml
from pathlib import Path
from typing import Dict, Any, List


class Validator:

    def validate_configuration(self, configuration: Dict[str, Any], config_file: str = None) -> bool:
        """Validate experiment configuration."""
        if not isinstance(configuration, dict):
            raise TypeError("Configuration must be a dictionary.")

        # Check required sections
        required_sections = ["framework", "run", "experiment_binding", "model", "execution", "report", "logging", "validation"]
        for section in required_sections:
            if section not in configuration:
                raise ValueError(f"Missing required configuration section: '{section}'")

        # Validate model configuration
        self._validate_model_configuration(configuration.get("model", {}))

        # Validate execution settings
        self._validate_execution_settings(configuration.get("execution", {}))

        # Validate report settings
        self._validate_report_settings(configuration.get("report", {}))

        # Validate experiment binding
        self._validate_experiment_binding(configuration.get("experiment_binding", {}))

        # Validate payload file reference
        self._validate_payload_reference(configuration)

        return True

    def validate_payload(self, payload: Dict[str, Any], payload_file: str = None) -> bool:
        """Validate task payload."""
        if not isinstance(payload, dict):
            raise TypeError("Task payload must be a dictionary.")

        # Validate payload structure
        self._validate_payload_structure(payload)

        # Validate experiment section
        self._validate_experiment_section(payload.get("experiment", {}))

        # Validate stimulus schema
        self._validate_stimulus_schema(payload.get("stimulus_schema", {}))

        # Validate response contract
        self._validate_response_contract(payload.get("response_contract", {}))

        # Validate metrics configuration
        self._validate_metrics(payload.get("metrics", {}))

        # Validate stimuli data
        self._validate_stimuli_data(payload.get("stimuli", []), payload.get("stimulus_schema", {}))

        # Validate instructions
        self._validate_instructions(payload.get("instructions", {}))

        return True

    def _validate_model_configuration(self, model_config: Dict[str, Any]):
        """Validate model configuration."""
        if not isinstance(model_config, dict):
            raise TypeError("Model configuration must be a dictionary.")

        required_fields = ["adapter", "model"]
        for field in required_fields:
            if field not in model_config:
                raise ValueError(f"Missing required model configuration field: '{field}'")

        # Validate adapter-specific requirements
        adapter = model_config.get("adapter")
        if adapter == "deepseek" and "api_key_env" not in model_config:
            raise ValueError("DeepSeek model configuration requires 'api_key_env'")

        # Validate generation settings
        generation = model_config.get("generation", {})
        if isinstance(generation, dict):
            if "temperature" in generation and not isinstance(generation["temperature"], (int, float)):
                raise ValueError("Model generation temperature must be a number")
            if "max_tokens" in generation and not isinstance(generation["max_tokens"], int):
                raise ValueError("Model generation max_tokens must be an integer")

    def _validate_execution_settings(self, execution_config: Dict[str, Any]):
        """Validate execution settings."""
        if not isinstance(execution_config, dict):
            raise TypeError("Execution configuration must be a dictionary.")

        # Validate numeric settings
        if "repetitions" in execution_config and not isinstance(execution_config["repetitions"], int):
            raise ValueError("Execution repetitions must be an integer")
        
        if "parallel_runs" in execution_config and not isinstance(execution_config["parallel_runs"], int):
            raise ValueError("Execution parallel_runs must be an integer")

        # Validate boolean settings
        boolean_settings = ["shuffle_trials", "fail_fast", "save_raw_output"]
        for setting in boolean_settings:
            if setting in execution_config and not isinstance(execution_config[setting], bool):
                raise ValueError(f"Execution {setting} must be a boolean")

    def _validate_report_settings(self, report_config: Dict[str, Any]):
        """Validate report settings."""
        if not isinstance(report_config, dict):
            raise TypeError("Report configuration must be a dictionary.")

        # Validate output directory
        if "output_directory" in report_config and not isinstance(report_config["output_directory"], str):
            raise ValueError("Report output_directory must be a string")

        # Validate formats
        if "formats" in report_config:
            if not isinstance(report_config["formats"], list):
                raise ValueError("Report formats must be a list")
            
            valid_formats = ["json", "html", "txt"]
            for fmt in report_config["formats"]:
                if fmt not in valid_formats:
                    raise ValueError(f"Invalid report format: {fmt}. Must be one of {valid_formats}")

    def _validate_experiment_binding(self, binding_config: Dict[str, Any]):
        """Validate experiment binding configuration."""
        if not isinstance(binding_config, dict):
            raise TypeError("Experiment binding configuration must be a dictionary.")

        if "payload_file" not in binding_config:
            raise ValueError("Missing required experiment_binding field: 'payload_file'")

        if binding_config.get("fail_on_payload_mismatch", False):
            for field in ["expected_experiment_id", "expected_experiment_version"]:
                if field not in binding_config:
                    raise ValueError(
                        f"Missing required experiment_binding field when mismatch checking is enabled: '{field}'"
                    )

    def _validate_payload_reference(self, configuration: Dict[str, Any]):
        """Validate payload file reference in configuration."""
        binding = configuration.get("experiment_binding", {})
        payload_file = binding.get("payload_file")
        
        if not payload_file:
            raise ValueError("experiment_binding.payload_file is required")

        # Check if payload file exists
        payload_path = Path(payload_file)
        if not payload_path.exists():
            raise ValueError(f"Payload file not found: {payload_file}")

    def _validate_payload_structure(self, payload: Dict[str, Any]):
        """Validate overall payload structure."""
        # Check for required sections - be more flexible for the Stroop payload format
        required_sections = ["experiment"]
        for section in required_sections:
            if section not in payload:
                raise ValueError(f"Missing required payload section: '{section}'")

    def _validate_experiment_section(self, experiment: Dict[str, Any]):
        """Validate experiment section."""
        if not isinstance(experiment, dict):
            raise TypeError("Experiment section must be a dictionary.")

        required_fields = ["id", "name", "version"]
        for field in required_fields:
            if field not in experiment:
                raise ValueError(f"Missing required experiment field: '{field}'")

        # Validate experiment ID format
        experiment_id = experiment.get("id")
        if not isinstance(experiment_id, str) or not experiment_id.strip():
            raise ValueError("Experiment ID must be a non-empty string")

    def _validate_stimulus_schema(self, stimulus_schema: Dict[str, Any]):
        """Validate stimulus schema."""
        # Allow missing stimulus_schema for backward compatibility with Stroop format
        if not stimulus_schema:
            return

        if not isinstance(stimulus_schema, dict):
            raise TypeError("Stimulus schema must be a dictionary.")

        required_fields = ["id_field", "fields"]
        for field in required_fields:
            if field not in stimulus_schema:
                raise ValueError(f"Missing required stimulus_schema field: '{field}'")

        # Validate fields array
        fields = stimulus_schema.get("fields", [])
        if not isinstance(fields, list):
            raise ValueError("Stimulus schema fields must be an array")

        # Validate each field
        for i, field in enumerate(fields):
            if not isinstance(field, dict):
                raise ValueError(f"Stimulus field {i} must be a dictionary")

            field_name = field.get("name")
            if not field_name or not isinstance(field_name, str):
                raise ValueError(f"Stimulus field {i} must have a name")

            field_type = field.get("type")
            if not field_type or not isinstance(field_type, str):
                raise ValueError(f"Stimulus field {i} must have a type")

    def _validate_response_contract(self, response_contract: Dict[str, Any]):
        """Validate response contract."""
        # Allow missing response_contract for backward compatibility
        if not response_contract:
            return

        if not isinstance(response_contract, dict):
            raise TypeError("Response contract must be a dictionary.")

    def _validate_metrics(self, metrics: Dict[str, Any]):
        """Validate metrics configuration."""
        if not isinstance(metrics, dict):
            raise TypeError("Metrics configuration must be a dictionary.")

        # Validate enabled metrics list
        enabled = metrics.get("enabled", [])
        if not isinstance(enabled, list):
            raise ValueError("Metrics enabled must be a list")

    def _validate_stimuli_data(self, stimuli: List[Dict[str, Any]], stimulus_schema: Dict[str, Any]):
        """Validate stimuli data against schema."""
        if not isinstance(stimuli, list):
            raise TypeError("Stimuli must be a list")

        # Allow empty stimuli list
        if not stimuli:
            return

        # If schema exists, validate against it
        if stimulus_schema:
            id_field = stimulus_schema.get("id_field", "stimulus_id")

            for i, stimulus in enumerate(stimuli):
                if not isinstance(stimulus, dict):
                    raise TypeError(f"Stimulus {i} must be a dictionary")

    def _validate_instructions(self, instructions: Dict[str, Any]):
        """Validate instructions section."""
        if not isinstance(instructions, dict):
            raise TypeError("Instructions must be a dictionary")

        # Validate task field
        if "task" in instructions and not isinstance(instructions["task"], str):
            raise TypeError("Instructions.task must be a string")

        # Validate response format field
        if "response_format" in instructions and not isinstance(instructions["response_format"], str):
            raise TypeError("Instructions.response_format must be a string")

        # Validate closing prompt field
        if "closing_prompt" in instructions and not isinstance(instructions["closing_prompt"], str):
            raise TypeError("Instructions.closing_prompt must be a string")
