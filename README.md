# Frames

  > A framework for consistent, evolving AI cognitive experiments

  ## 🎯 Vision & Philosophy

  Frames is designed to create a consistent, evolving framework for AI cognitive experiments where changing a single
  file (task_payload.yaml) allows you to perform different experiments. This is "vibe coding" at its best - a natural
  evolution of users gaining knowledge and experience with understanding AI complex systems.

  ## 🌱 Core Philosophy

  - Consistency through Simplicity: One file change = new experiment
  - Natural Evolution: Users learn and grow with the system
  - Complexity Made Accessible: Understanding AI systems through hands-on experimentation
  - Vibe Coding: Organic, intuitive development that feels natural

  ## 🚀 Quick Start

  ### Prerequisites

  - Python 3.8+
  - API keys for supported AI models (see .env template)

  ### Setup

  # Clone the repository
  git clone https://github.com/adsmithhh/frames.git
  cd frames

  # Install dependencies (if any)
  python -m pip install -r requirements.txt  # If requirements.txt exists

  # Copy and edit the environment file
  cp .env.example .env  # If .env.example exists
  # Edit .env with your API keys

  ### Running Your First Experiment

  python main.py
  # Choose your AI model when prompted
  # The system will run the experiment and generate reports

  ## 📁 Project Structure

  frames/
  ├── main.py                    # Main application entry point
  ├── .env                       # Environment variables with API keys
  ├── .gitignore                 # Git ignore file
  ├── task_payloads/             # **CORE EXPERIMENT DEFINITIONS**
  │   ├── oddbal_task_payload.yaml     # Oddball experiment
  │   ├── stroop_task_payload.yaml      # Stroop experiment
  │   └── theory_of_mind_task_payload.yaml  # Theory of Mind experiment
  ├── experiment configurations/  # Model-specific configurations
  │   ├── experiment_configuration.yaml     # Default configuration
  │   ├── deepseek_experiment_config.yaml     # DeepSeek specific
  │   ├── anthropic_experiment_config.yaml    # Anthropic specific
  │   ├── openai_experiment_config.yaml      # OpenAI specific
  │   ├── gemini_experiment_config.yaml       # Gemini specific
  │   ├── ollama_experiment_config.yaml       # Ollama specific
  │   └── experiments/                       # Individual experiment folders
  │       ├── oddbal/
  │       ├── stroop/
  │       └── theory_of_mind/
  ├── Core Application Files:
  │   ├── ConfigurationLoader.py    # Load experiment configurations
  │   ├── Task_Loader.py           # Load task definitions
  │   ├── ExperimentRunner.py      # Execute experiments
  │   ├── ModelAdapter.py          # AI model adapters
  │   ├── Validator.py             # Configuration validation
  │   ├── AnalysisEngine.py        # Analyze results
  │   ├── ReportBuilder.py         # Build experiment reports
  │   ├── PromptBuilder.py         # Build prompts for models
  │   └── ParserEngine.py          # Parse model responses
  └── Model Adapters:
      ├── DeepSeekModelAdapter.py
      ├── AnthropicModelAdapter.py
      ├── OpenAiModelAdapter.py
      ├── GeminiModelAdapter.py
      └── OllamaModelAdapter.py

  ## 🔧 The Single File Change Revolution

  The magic of Frames is in its simplicity:

  1. Change task_payloads/your_experiment.yaml
  2. Run python main.py
  3. Get results for your new experiment

  That's it! No complex configuration changes, no code modifications needed. Just update the task payload and you're
  running a completely different experiment.

  ### Example: From Oddball to Stroop

  Current: task_payloads/oddbal_task_payload.yaml → Visual shape classification

  Change to: task_payloads/stroop_task_payload.yaml → Color-word interference task

  Result: Completely different cognitive experiment, same framework, same analysis tools.

  ## 🧠 Current Experiments

  ### 1. Oddball Experiment (oddbal_task_payload.yaml)

  - ID: ascii_geometric_oddball_v1
  - Goal: Detect "oddball" visual stimuli among standard ones
  - Task: Classify geometric shapes as STANDARD or ODDBALL
  - Stimuli: Unicode shapes (⬢ ▲ ■ for standard, ⬟ ★ for oddball)
  - Trials: 100 trials with 80% standard, 20% oddball

  ### 2. Stroop Experiment (stroop_task_payload.yaml)

  - Goal: Demonstrate color-word interference
  - Task: Name the ink color of color words
  - Stimuli: Color words displayed in different ink colors
  - Interference: Word meaning conflicts with ink color

  ### 3. Theory of Mind (theory_of_mind_task_payload.yaml)

  - Goal: Test false belief understanding
  - Task: Understand characters' beliefs vs reality
  - Complexity: Advanced cognitive reasoning required

  ## 🤖 Supported AI Models

  Frames supports multiple AI backends:

   Model               Adapter                  Status
  ━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━
   OpenAI GPT          OpenAiModelAdapter       ✅ Active
  ──────────────────  ───────────────────────  ───────────
   Anthropic Claude    AnthropicModelAdapter    ✅ Active
  ──────────────────  ───────────────────────  ───────────
   Gemini              GeminiModelAdapter       ✅ Active
  ──────────────────  ───────────────────────  ───────────
   DeepSeek            DeepSeekModelAdapter     ✅ Active
  ──────────────────  ───────────────────────  ───────────
   Ollama              OllamaModelAdapter       ✅ Active

  ## 📊 Experiment Workflow

  1. Configuration: Model and experiment settings
  2. Task Loading: Load experiment definition from YAML
  3. Execution: Run trials with selected AI model
  4. Analysis: Analyze responses and accuracy
  5. Reporting: Generate detailed experiment reports

  ## 🔍 Metrics & Analysis

  Each experiment generates comprehensive metrics:

  - Accuracy: Correct response rate
  - Protocol Adherence: Following instructions
  - Response Time: How long responses take
  - Error Analysis: Pattern recognition in mistakes

  ## 🧪 Experiment Creation Guide

  ### Creating a New Experiment

  1. Copy an existing payload: task_payloads/your_experiment.yaml
  2. Edit the YAML: Change stimuli, instructions, and rules
  3. Update experiment metadata: ID, name, description
  4. Test: Run with python main.py
  5. Iterate: Refine based on results

  ### YAML Schema Reference

  See Configuration_Schema.yaml for the complete configuration schema.

  ## 🚧 Work in Progress

  This is a living project! We're actively:

  - ✅ Core Framework: Stable experiment execution
  - ✅ Multi-Model Support: 5 AI backends working
  - ✅ Experiment Types: 3 cognitive experiments ready
  - ⚠️ Web Interface: Planning user-friendly web UI
  - ⚠️ Real-time Analysis: Live experiment monitoring
  - ⚠️ Experiment Library: Curated experiments collection
  - ⚠️ Advanced Metrics: More sophisticated analysis
  - ⚠️ Export Capabilities: CSV, JSON, PDF reports

  ## 💡 Contribution Philosophy

  We welcome all suggestions and contributions! This is a community-driven project aimed at making AI cognitive
  research accessible to everyone.

  ### How to Contribute

  1. Suggest Experiments: What cognitive tasks should we add?
  2. Improve YAML Schema: Make experiment creation easier
  3. Add Metrics: What new measurements would be valuable?
  4. Documentation: Help us make this clearer
  5. Bug Reports: Find issues and help fix them

  ### Getting Started with Development

  # Fork the repository
  # Create your feature branch
  git checkout -b feature/your-experiment
  # Make your changes
  git commit -m "Add: Your new experiment"
  # Push to your fork
  # Submit a pull request

  ## 📝 License

  [License information goes here]

  ## 🤝 Acknowledgments

  - ExecutiveAudit: Original framework design
  - AI Community: For inspiration and support
  - Research Community: Cognitive science guidance

  ## 📞 Contact & Discussion

  - GitHub Issues: Bug reports and feature requests
  - Discussions: Share your experiments and ideas
  - Discord: Join our community chat

  ———

  Frames - Where AI cognitive research meets intuitive experimentation

  "Understanding AI systems, one experiment at a time"

  ———

  > Note: This is a work-in-progress project. All suggestions are welcome as we build the future of accessible AI
  > cognitive research.
