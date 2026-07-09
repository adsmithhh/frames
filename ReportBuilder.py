# ReportBuilder.py - FIXED VERSION with txt format support
# Consumes unified contract through analysis results

import json
import re
from datetime import datetime
from html import escape
from pathlib import Path


class ReportBuilder:

    def save(self, analysis, configuration):
        """Save analysis reports in multiple formats."""
        report_config = configuration.get("report", {})
        output_directory = Path(report_config.get("output_directory", "reports"))
        formats = report_config.get("formats", ["json"])
        output_directory.mkdir(parents=True, exist_ok=True)

        # Generate run metadata
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_id = analysis["experiment"]["id"]
        model_adapter = configuration.get("model", {}).get("adapter", "unknown")
        experiment_folder = self._experiment_folder_name(experiment_id)
        run_directory = output_directory / model_adapter / f"{experiment_folder}_{timestamp}"
        run_directory.mkdir(parents=True, exist_ok=True)
        
        report_paths = []

        # Always save text summary (for internal use)
        summary_path = run_directory / "summary.txt"
        summary_path.write_text(self._build_text_summary(analysis), encoding="utf-8")
        report_paths.append(str(summary_path))

        # Save requested formats
        for report_format in formats:
            if report_format == "json":
                path = run_directory / "analysis.json"
                path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
                report_paths.append(str(path))
            elif report_format == "html":
                path = run_directory / "report.html"
                path.write_text(self._build_html_report(analysis), encoding="utf-8")
                report_paths.append(str(path))
            elif report_format == "txt":
                path = run_directory / "report.txt"
                path.write_text(self._build_detailed_text_report(analysis), encoding="utf-8")
                report_paths.append(str(path))
            else:
                raise ValueError(f"Unsupported report format: {report_format}")

        return report_paths

    def _engine_name(self, configuration):
        """Get model adapter name for directory naming."""
        model_config = configuration.get("model", {})
        return (model_config.get("adapter") or "unknown").strip().lower()

    def _experiment_folder_name(self, experiment_id):
        """Clean experiment ID for directory naming."""
        cleaned = re.sub(r"_\d+$", "", str(experiment_id).strip())
        return cleaned or "experiment"

    def _build_text_summary(self, analysis):
        """Build text summary from analysis."""
        experiment = analysis["experiment"]
        summary = analysis["summary"]
        enabled_metrics = experiment.get("enabled_metrics", [])

        lines = [
            f"Experiment ID: {experiment['id']}",
            f"Experiment name: {experiment['name']}",
            f"Version: {experiment['version']}",
            f"Executed trials: {experiment['executed_trials']}",
            f"Available stimuli: {experiment['available_stimuli']}",
        ]

        # Add accuracy metrics if enabled
        if "accuracy" in enabled_metrics:
            lines.extend([
                f"Correct trials: {summary.get('correct_trials', 0)}",
                f"Incorrect trials: {summary.get('incorrect_trials', 0)}",
                f"Accuracy rate: {summary.get('accuracy_rate', 0):.2%}",
            ])

        # Add response time metrics
        lines.extend([
            f"Total response time (s): {summary.get('total_response_time_seconds', 0):.3f}",
            f"Average response time (s): {summary.get('average_response_time_seconds', 0):.3f}",
        ])

        # Add protocol adherence metrics if enabled
        if "protocol_adherence" in enabled_metrics:
            lines.extend([
                f"Protocol-adherent trials: {summary.get('protocol_adherent_trials', 0)}",
                f"Protocol adherence rate: {summary.get('protocol_adherence_rate', 0):.2%}",
                f"Non-adherent trials: {summary.get('non_adherent_trials', 0)}",
            ])

        return "\\n".join(lines) + "\\n"

    def _build_detailed_text_report(self, analysis):
        """Build detailed text report from analysis."""
        experiment = analysis["experiment"]
        summary = analysis["summary"]
        enabled_metrics = experiment.get("enabled_metrics", [])

        lines = [
            "=" * 60,
            f"EXPERIMENT REPORT: {experiment['id']}",
            "=" * 60,
            f"Name: {experiment['name']}",
            f"Version: {experiment['version']}",
            f"Executed Trials: {experiment['executed_trials']}",
            f"Available Stimuli: {experiment['available_stimuli']}",
            f"Enabled Metrics: {', '.join(enabled_metrics)}",
            "=" * 60,
            ""
        ]

        # Summary section
        lines.append("SUMMARY")
        lines.append("-" * 30)
        lines.append(f"Total Response Time: {summary.get('total_response_time_seconds', 0):.3f}s")
        lines.append(f"Average Response Time: {summary.get('average_response_time_seconds', 0):.3f}s")
        
        if "accuracy" in enabled_metrics:
            lines.append(f"Accuracy: {summary.get('accuracy_rate', 0):.2%} ({summary.get('correct_trials', 0)}/{experiment['executed_trials']})")
        
        if "protocol_adherence" in enabled_metrics:
            lines.append(f"Protocol Adherence: {summary.get('protocol_adherence_rate', 0):.2%} ({summary.get('protocol_adherent_trials', 0)}/{experiment['executed_trials']})")
        
        lines.append("")

        # Trial details
        lines.append("TRIAL DETAILS")
        lines.append("-" * 30)
        
        for trial in analysis["trials"]:
            lines.append(f"Trial {trial['trial']}:")
            lines.append(f"  Stimulus: {trial.get('stimulus_fields', {})}")
            lines.append(f"  Response: {trial.get('raw_response', '')}")
            lines.append(f"  Time: {trial.get('response_time_seconds', 0):.3f}s")
            lines.append(f"  Extracted Answer: {trial.get('extracted_answer', '')}")
            
            if "expected_response" in trial:
                lines.append(f"  Expected Answer: {trial['expected_response']}")
            
            if "accuracy" in enabled_metrics:
                lines.append(f"  Correct: {'Yes' if trial.get('is_correct', False) else 'No'}")
            
            if "protocol_adherence" in enabled_metrics:
                lines.append(f"  Protocol Adherent: {'Yes' if trial.get('is_protocol_adherent', False) else 'No'}")
            
            lines.append("")

        return "\\n".join(lines)

    def _build_html_report(self, analysis):
        """Build HTML report from analysis."""
        experiment = analysis["experiment"]
        summary = analysis["summary"]
        enabled_metrics = experiment.get("enabled_metrics", [])
        
        # Build trial table
        rows = []
        headers = self._build_table_headers(analysis)
        
        for trial in analysis["trials"]:
            row = self._build_trial_row(trial, analysis, enabled_metrics)
            rows.append(row)

        # Build summary list
        summary_items = self._build_summary_items(summary, enabled_metrics)

        # Generate HTML template
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(experiment['id'])} report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    .correct {{ color: green; }}
    .incorrect {{ color: red; }}
    .adherent {{ color: green; }}
    .non-adherent {{ color: orange; }}
  </style>
</head>
<body>
  <h1>{escape(experiment['name'])} Report</h1>
  <h2>Experiment: {escape(experiment['id'])}</h2>
  
  <h3>Summary</h3>
  <ul>
    {summary_items}
  </ul>
  
  <h3>Trial Details</h3>
  <table>
    <thead>
      <tr>
        {headers}
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>"""

    def _build_table_headers(self, analysis):
        """Build table headers based on experiment schema."""
        headers = ["<th>Trial</th>"]
        
        # Add stimulus field headers
        for trial in analysis.get("trials", []):
            stimulus_fields = trial.get("stimulus_fields", {})
            if stimulus_fields:
                headers.extend([f"<th>{escape(field)}</th>" for field in stimulus_fields.keys()])
                break
        
        # Add response headers
        headers.extend([
            "<th>Raw Response</th>",
            "<th>Response Time (s)</th>",
            "<th>Extracted Answer</th>",
        ])
        
        # Add expected response header
        for trial in analysis.get("trials", []):
            if "expected_response" in trial:
                headers.append("<th>Expected Answer</th>")
                break
        
        # Add enabled metric headers
        enabled_metrics = analysis["experiment"].get("enabled_metrics", [])
        if "accuracy" in enabled_metrics:
            headers.append("<th>Correct</th>")
        if "protocol_adherence" in enabled_metrics:
            headers.append("<th>Protocol-adherent</th>")
        
        return "\\n".join(headers)

    def _build_trial_row(self, trial, analysis, enabled_metrics):
        """Build a single trial row for the table."""
        cells = [f"<td>{trial['trial']}</td>"]
        
        # Add stimulus fields
        stimulus_fields = trial.get("stimulus_fields", {})
        for field_name in stimulus_fields:
            value = stimulus_fields.get(field_name, "")
            cells.append(f"<td>{escape(str(value))}</td>")
        
        # Add response fields
        cells.extend([
            f"<td>{escape(str(trial.get('raw_response', '')))}</td>",
            f"<td>{trial.get('response_time_seconds', 0):.3f}</td>",
            f"<td>{escape(str(trial.get('extracted_answer', '')))}</td>",
        ])
        
        # Add expected answer
        if "expected_response" in trial:
            cells.append(f"<td>{escape(str(trial['expected_response']))}</td>")
        
        # Add enabled metric columns
        if "accuracy" in enabled_metrics:
            is_correct = trial.get("is_correct", False)
            cell_class = "correct" if is_correct else "incorrect"
            cell_text = "Yes" if is_correct else "No"
            cells.append(f'<td class="{cell_class}">{cell_text}</td>')
        
        if "protocol_adherence" in enabled_metrics:
            is_adherent = trial.get("is_protocol_adherent", False)
            cell_class = "adherent" if is_adherent else "non-adherent"
            cell_text = "Yes" if is_adherent else "No"
            cells.append(f'<td class="{cell_class}">{cell_text}</td>')
        
        return "<tr>" + "".join(cells) + "</tr>"

    def _build_summary_items(self, summary, enabled_metrics):
        """Build summary list items for HTML report."""
        items = []
        
        if "accuracy" in enabled_metrics:
            items.extend([
                f"<li>Correct trials: {summary.get('correct_trials', 0)}</li>",
                f"<li>Incorrect trials: {summary.get('incorrect_trials', 0)}</li>",
                f"<li>Accuracy rate: {summary.get('accuracy_rate', 0):.2%}</li>",
            ])
        
        items.extend([
            f"<li>Total response time (s): {summary.get('total_response_time_seconds', 0):.3f}</li>",
            f"<li>Average response time (s): {summary.get('average_response_time_seconds', 0):.3f}</li>",
        ])
        
        if "protocol_adherence" in enabled_metrics:
            items.extend([
                f"<li>Protocol-adherent trials: {summary.get('protocol_adherent_trials', 0)}</li>",
                f"<li>Protocol adherence rate: {summary.get('protocol_adherence_rate', 0):.2%}</li>",
                f"<li>Non-adherent trials: {summary.get('non_adherent_trials', 0)}</li>",
            ])
        
        return "\\n".join(items)

    def _stimulus_columns(self, analysis):
        """Get stimulus column names from analysis."""
        for trial in analysis.get("trials", []):
            stimulus_fields = trial.get("stimulus_fields", {})
            if stimulus_fields:
                return list(stimulus_fields.keys())
        return []

    def _expected_response_label(self, analysis):
        """Get expected response label from analysis."""
        for trial in analysis.get("trials", []):
            if "expected_response" in trial:
                return "Expected answer"
        return None

    def _field_label(self, field_name):
        """Generate display label for a field."""
        acronyms = {
            "id": "ID",
            "rgb": "RGB",
            "rgb_values": "RGB Values",
            "foreground": "Foreground",
            "background": "Background",
            "word": "Word",
            "text": "Text",
            "color": "Color",
            "ink": "Ink",
        }
        
        if field_name.lower() in acronyms:
            return acronyms[field_name.lower()]
        
        # Convert underscores to spaces and capitalize
        words = str(field_name).replace("_", " ").split()
        return " ".join(word.capitalize() for word in words)
