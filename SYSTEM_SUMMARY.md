# COMPREHENSIVE EXPERIMENT SYSTEM

## System Overview
This system provides a comprehensive framework for running AI cognitive experiments with multiple models and experiment types.

## Key Features
- **Environment Management**: Automatic .env file loading with API keys
- **Multi-Model Support**: DeepSeek, Anthropic, OpenAI, Gemini, Ollama
- **Interactive Engine Selection**: Choose model at runtime
- **Multiple Experiment Types**: Oddball, Stroop, Theory of Mind

## Experiment Types

### 1. Oddball Experiment
- **ID**: ascii_geometric_oddball_v1
- **Description**: Visual oddball detection task with 100 trials using Unicode geometric shapes
- **Task Payload**: 	ask_payloads/oddbal_task_payload.yaml" >> 
C:\Users\mrcn2\new\SYSTEM_SUMMARY.md; echo " >> C:\Users\mrcn2\new\SYSTEM_SUMMARY.md; echo ###
2.
Stroop
Experiment >> C:\Users\mrcn2\new\SYSTEM_SUMMARY.md; echo -
**ID**:
standard_stroop_200_v2 >> C:\Users\mrcn2\new\SYSTEM_SUMMARY.md; echo -
**Description**:
Standard
Stroop
color-word
interference
task
with
200
trials >> C:\Users\mrcn2\new\SYSTEM_SUMMARY.md; echo -
**Task
Payload**:
	ask_payloads/stroop_task_payload.yaml"

- **ID**: theory_of_mind_v1
- **Description**: Advanced theory of mind experiment testing false belief understanding
- **Task Payload**: 	ask_payloads/theory_of_mind_task_payload.yaml" >> 
C:\Users\mrcn2\new\SYSTEM_SUMMARY.md; echo -
**README**:
Available
in
xperiment
configurations/experiments/theory_of_mind/"

## Directory Structure

``
new/
├── main.py                    # Main application with environment mechanism
├── .env                       # Environment variables with API keys
├── .gitignore                 # Git ignore file
├── task_payloads/             # Central location for all task payloads
│   ├── oddbal_task_payload.yaml
│   ├── stroop_task_payload.yaml
│   └── theory_of_mind_task_payload.yaml
├── experiment configurations/  # Model-specific configurations
│   ├── experiment_configuration.yaml
│   ├── deepseek_experiment_config.yaml
│   ├── anthropic_experiment_config.yaml
│   ├── openai_experiment_config.yaml
│   ├── gemini_experiment_config.yaml
│   ├── ollama_experiment_config.yaml
│   └── experiments/           # Individual experiment folders
│       ├── oddbal/
│       ├── stroop/
│       └── theory_of_mind/
├── Core Application Files:
│   ├── ConfigurationLoader.py
│   ├── Task_Loader.py
│   ├── ExperimentRunner.py
│   ├── ModelAdapter.py
│   ├── Validator.py
│   ├── AnalysisEngine.py
│   ├── ReportBuilder.py
│   ├── PromptBuilder.py
│   └── ParserEngine.py
└── Model Adapters:
    ├── DeepSeekModelAdapter.py
    ├── AnthropicModelAdapter.py
    ├── OpenAiModelAdapter.py
    ├── GeminiModelAdapter.py
    └── OllamaModelAdapter.py
``

## Usage
1. Run python main.py to start the system
2. Choose from available AI models when prompted
3. The system will load the appropriate configuration and run the experiment

## Environment Setup
The .env file contains API keys for all supported models:
- DEEPSEEK_API_KEY
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- GEMINI_API_KEY

## Key Features
1. **Environment Management**: Automatically loads API keys from .env file
2. **Interactive Model Selection**: Choose from 5 different AI models
3. **Multiple Experiment Types**: Cognitive experiments for different research purposes
4. **Centralized Task Payloads**: All experiment definitions in one location
5. **Modular Architecture**: Easy to add new models and experiments

Generated on: 07/09/2026 19:00:27
