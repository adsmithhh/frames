from PromptBuilder import PromptBuilder
from AnalysisEngine import AnalysisEngine
from ReportBuilder import ReportBuilder


class ExperimentRunner:

    def __init__(self, package, model, configuration):
        self.package = package
        self.model = model
        self.configuration = configuration

    def run(self):

        self.start()

        results = self.execute_trials()
        analysis = AnalysisEngine().analyze(self.package, results)
        report_paths = ReportBuilder().save(analysis, self.configuration)

        self.finish(analysis, report_paths)

        return {
            "results": results,
            "analysis": analysis,
            "report_paths": report_paths,
        }

    def start(self):
        """Start experiment using runtime configuration from experiment_configuration.yaml"""
        payload = self.package.payload
        execution_config = self.configuration.get("execution", {})
        model_config = self.configuration.get("model", {})
        
        total_stimuli = len(payload["stimuli"])
        
        # Apply field name mapping for execution config
        randomize = execution_config.get("shuffle_trials", execution_config.get("randomize", False))
        
        # FIX: Handle None values in stop_after_trials
        stop_after_trials = execution_config.get("stop_after_trials", None)
        stop_after = execution_config.get("stop_after", total_stimuli)
        
        # Use stop_after_trials if specified, otherwise use stop_after, otherwise use total_stimuli
        if stop_after_trials is not None:
            stop_after = stop_after_trials
        elif stop_after is None:
            stop_after = total_stimuli
            
        trial_count = min(stop_after, total_stimuli)

        print("Starting experiment")
        print(f"Experiment : {payload['experiment']['id']}")
        print(f"Version    : {payload['experiment']['version']}")
        print(f"Trials     : {trial_count}")
        
        # Handle nested model.generation structure
        generation_config = model_config.get("generation", {})
        temperature = generation_config.get("temperature", 0.0)
        max_tokens = generation_config.get("max_tokens", 100)
        
        print(f"Model Temp : {temperature}")
        print(f"Max Tokens : {max_tokens}")

    def execute_trials(self):
        """Execute trials using runtime configuration from experiment_configuration.yaml"""
        import random
        import time

        payload = self.package.payload
        execution_config = self.configuration.get("execution", {})
        model_config = self.configuration.get("model", {})

        stimuli = payload["stimuli"]
        
        # Apply field name mapping for execution config
        randomize = execution_config.get("shuffle_trials", execution_config.get("randomize", False))
        
        # FIX: Handle None values in stop_after_trials
        stop_after_trials = execution_config.get("stop_after_trials", None)
        stop_after = execution_config.get("stop_after", len(stimuli))
        
        # Use stop_after_trials if specified, otherwise use stop_after, otherwise use total_stimuli
        if stop_after_trials is not None:
            stop_after = stop_after_trials
        elif stop_after is None:
            stop_after = len(stimuli)

        # Create a working copy of the stimuli
        stimuli = list(stimuli)

        if randomize:
            random.shuffle(stimuli)

        # Respect the stop_after limit
        stimuli = stimuli[:stop_after]

        print("\\n==============================")
        print("Experiment Protocol")
        print("==============================")

        protocol_prompt = PromptBuilder.build(
            payload,
            PromptBuilder.placeholder_stimulus(payload),
        )

        print(protocol_prompt)

        print("\\n==============================")
        print("Beginning Trials")
        print("==============================")

        results = []

        for trial_number, stimulus in enumerate(stimuli, start=1):

            print(f"\\n--- Trial {trial_number} ---")
            self._print_trial_stimulus(payload, stimulus)

            prompt = PromptBuilder.build(
                payload,
                stimulus
            )

            # Get model config for this trial (with nested generation structure)
            generation_config = model_config.get("generation", {})
            
            started_at = time.perf_counter()
            response = self.model.generate(prompt)
            response_time_seconds = time.perf_counter() - started_at
            print(f"Response  : {response}")
            print(f"Latency   : {response_time_seconds:.3f}s")

            results.append(
                {
                    "trial": trial_number,
                    "stimulus": stimulus,
                    "response": response,
                    "response_time_seconds": round(response_time_seconds, 6),
                }
            )

        return results

    def _print_trial_stimulus(self, payload, stimulus):
        """Print trial stimulus using unified payload schema"""
        field_names = list(PromptBuilder.placeholder_stimulus(payload).keys())
        labels = [PromptBuilder._field_label(field_name) for field_name in field_names]
        label_width = max(len(label) for label in labels)

        for field_name, label in zip(field_names, labels):
            if field_name not in stimulus:
                raise KeyError(
                    f"Stimulus is missing required display field: {field_name}"
                )

            value = self._display_value(field_name, stimulus[field_name], stimulus)
            print(f"{label:<{label_width}} : {value}")

    def _display_value(self, field_name, value, stimulus):
        """Display stimulus value (override for custom formatting)"""
        return value

    def finish(self, analysis, report_paths):
        """Finish experiment and display results"""
        print("\\nExperiment finished")
        print(f"Accuracy   : {analysis['summary']['accuracy_rate']:.2%}")
        print(
            "Avg Time   : "
            f"{analysis['summary']['average_response_time_seconds']:.3f}s"
        )
        print(
            "Adherence  : "
            f"{analysis['summary']['protocol_adherence_rate']:.2%}"
        )

        for path in report_paths:
            print(f"Report     : {path}")
