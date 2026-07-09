import re
from typing import Dict, List, Any


class AnalysisEngine:

    def analyze(self, package, results):
        """Analyze results based on unified payload structure."""
        payload = package.payload
        trial_reports = []
        
        # Get enabled metrics from unified payload
        metrics_config = payload.get("metrics", {})
        enabled_metrics = metrics_config.get("enabled", [])
        
        # Initialize counters based on enabled metrics
        summary_stats = self._initialize_summary_stats(enabled_metrics)
        
        # Analyze each trial
        for result in results:
            trial_report = self._analyze_trial(payload, result)
            trial_reports.append(trial_report)
            
            # Update summary statistics
            summary_stats = self._update_summary_stats(summary_stats, trial_report, enabled_metrics)
        
        # Calculate final rates and averages
        total_trials = len(trial_reports)
        summary = self._calculate_final_summary(summary_stats, total_trials, enabled_metrics)
        
        return {
            "experiment": {
                "id": payload.get("experiment", {}).get("id", ""),
                "name": payload.get("experiment", {}).get("name", ""),
                "version": payload.get("experiment", {}).get("version", ""),
                "executed_trials": total_trials,
                "available_stimuli": len(payload.get("stimuli", [])),
                "enabled_metrics": enabled_metrics,
            },
            "summary": summary,
            "trials": trial_reports,
        }

    def _initialize_summary_stats(self, enabled_metrics):
        """Initialize summary statistics based on enabled metrics."""
        stats = {
            "correct_trials": 0,
            "protocol_adherent_trials": 0,
            "total_response_time": 0.0,
            "adherent_trials": 0,
            "accurate_trials": 0,
        }
        return stats

    def _update_summary_stats(self, stats, trial_report, enabled_metrics):
        """Update summary statistics for a trial report."""
        # Update response time (always tracked)
        stats["total_response_time"] += trial_report.get("response_time_seconds", 0.0)
        
        # Update accuracy if enabled
        if "accuracy" in enabled_metrics:
            if trial_report.get("is_correct", False):
                stats["accurate_trials"] += 1
                stats["correct_trials"] += 1
        
        # Update protocol adherence if enabled  
        if "protocol_adherence" in enabled_metrics:
            if trial_report.get("is_protocol_adherent", False):
                stats["adherent_trials"] += 1
                stats["protocol_adherent_trials"] += 1
        
        return stats

    def _calculate_final_summary(self, stats, total_trials, enabled_metrics):
        """Calculate final summary statistics."""
        summary = {}
        
        # Accuracy metrics
        if "accuracy" in enabled_metrics:
            summary["correct_trials"] = stats["correct_trials"]
            summary["incorrect_trials"] = total_trials - stats["correct_trials"]
            summary["accuracy_rate"] = self._rate(stats["correct_trials"], total_trials)
        
        # Protocol adherence metrics
        if "protocol_adherence" in enabled_metrics:
            summary["protocol_adherent_trials"] = stats["protocol_adherent_trials"]
            summary["non_adherent_trials"] = total_trials - stats["protocol_adherent_trials"]
            summary["protocol_adherence_rate"] = self._rate(stats["protocol_adherent_trials"], total_trials)
        
        # Response time metrics
        summary["total_response_time_seconds"] = round(stats["total_response_time"], 6)
        summary["average_response_time_seconds"] = self._average(stats["total_response_time"], total_trials)
        
        return summary

    def _analyze_trial(self, payload, result):
        """Analyze a single trial based on unified payload structure."""
        stimulus = result["stimulus"]
        raw_response = result["response"]
        
        # Use unified response contract
        response_contract = payload.get("response_contract", {})
        
        # Extract answer based on contract
        extracted_answer = self._extract_answer(raw_response, response_contract)
        
        # Normalize response
        normalized_response = self._normalize_response(raw_response, response_contract)
        
        # Get expected answer
        expected_answer = self._get_expected_answer(stimulus, response_contract)
        
        # Validate response
        is_protocol_adherent = self._validate_response(extracted_answer, normalized_response, stimulus, response_contract)
        
        # Check correctness
        is_correct = extracted_answer == expected_answer
        
        # Build trial report
        trial_report = {
            "trial": result.get("trial", 1),
            "stimulus_id": stimulus.get("stimulus_id", 1),
            "stimulus": stimulus,
            "response": raw_response,
            "response_time_seconds": result.get("response_time_seconds", 0.0),
            "normalized_response": normalized_response,
            "extracted_answer": extracted_answer,
            "expected_response": expected_answer,
            "is_protocol_adherent": is_protocol_adherent,
            "is_correct": is_correct,
        }
        
        # Add additional fields based on response contract
        self._add_trial_report_fields(trial_report, response_contract, stimulus)
        
        return trial_report

    def _extract_answer(self, raw_response, response_contract):
        """Extract answer based on contract extraction rules."""
        extraction = response_contract.get("extraction", {})
        mode = extraction.get("mode", "last_token")
        
        tokens = self._extract_tokens(raw_response)
        
        if mode == "last_token":
            return tokens[-1] if tokens else ""
        elif mode == "first_token":
            return tokens[0] if tokens else ""
        elif mode == "full_text":
            return raw_response if raw_response is not None else ""
        else:
            raise ValueError(f"Unsupported extraction mode: {mode}")

    def _normalize_response(self, raw_response, response_contract):
        """Normalize response based on contract rules."""
        normalization = response_contract.get("normalization", {})
        case = normalization.get("case", "upper")
        
        text = raw_response if raw_response is not None else ""
        text = str(text).strip()
        
        if case == "upper":
            return text.upper()
        elif case == "lower":
            return text.lower()
        else:
            return text

    def _get_expected_answer(self, stimulus, response_contract):
        """Get expected answer from contract."""
        expected_config = response_contract.get("expected_answer", {})
        source = expected_config.get("source", "stimulus_field")
        
        if source == "stimulus_field":
            field_name = expected_config.get("field")
            if not field_name:
                # Try legacy field name
                field_name = expected_config.get("field")
                if not field_name:
                    # Try common field names in the stimulus
                    possible_fields = ["correct_label", "correct_answer", "expected_answer", "answer"]
                    for field in possible_fields:
                        if field in stimulus:
                            field_name = field
                            break
                    if not field_name:
                        raise ValueError(f"No expected answer field found in stimulus. Available fields: {list(stimulus.keys())}")
            if field_name not in stimulus:
                raise KeyError(f"Stimulus missing expected field: {field_name}")
            return stimulus[field_name]
        elif source == "literal":
            return expected_config.get("value", "")
        else:
            raise ValueError(f"Unsupported expected answer source: {source}")

    def _validate_response(self, extracted_answer, normalized_response, stimulus, response_contract):
        """Validate response against contract rules."""
        validation = response_contract.get("validation", {})
        
        # Check if exactly one answer is required
        if validation.get("require_exactly_one_answer", False):
            tokens = self._extract_tokens(normalized_response)
            if len(tokens) != 1:
                return False
        
        # Check against allowed values
        allowed_values = response_contract.get("allowed_values", [])
        if allowed_values:
            return normalized_response in allowed_values
        
        return True

    def _add_trial_report_fields(self, trial_report, response_contract, stimulus):
        """Add additional fields to trial report based on contract."""
        # Add allowed responses if specified
        allowed_values = response_contract.get("allowed_values", [])
        if allowed_values:
            trial_report["allowed_responses"] = sorted(allowed_values)
            trial_report["is_allowed_response"] = trial_report["extracted_answer"] in allowed_values

    def _get_stimulus_fields(self, stimulus, payload):
        """Get stimulus field display based on unified schema."""
        stimulus_schema = payload.get("stimulus_schema", {})
        fields = stimulus_schema.get("fields", [])
        
        field_display = {}
        for field in fields:
            field_name = field.get("name")
            if field_name in stimulus:
                label = field.get("label", field_name)
                field_display[label] = stimulus[field_name]
        
        return field_display

    def _extract_tokens(self, response):
        """Extract tokens from response."""
        if response is None:
            return []
        
        tokens = []
        for raw_token in re.split(r"\s+", str(response).strip()):
            token = raw_token.strip(".,!?;:\"'()[]{}")
            if token:
                tokens.append(token)
        
        return tokens

    def _rate(self, value, total):
        """Calculate rate as decimal."""
        if total == 0:
            return 0.0
        return round(value / total, 4)

    def _average(self, value, total):
        """Calculate average."""
        if total == 0:
            return 0.0
        return round(value / total, 6)
