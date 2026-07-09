from ConfigurationLoader import ConfigurationLoader
from Validator import Validator
from Task_Loader import TaskLoader
from ExperimentRunner import ExperimentRunner
from ModelAdapter import ModelAdapter
import os
import sys


def load_env_file(path=".env"):
    """Load KEY=VALUE pairs from a local .env file into os.environ.

    Real environment variables always win - this only fills in values
    that aren't already set, so a session-level $env:X still overrides
    whatever's in the file.
    """
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()

# Load configuration
loader = ConfigurationLoader("experiment_configuration.yaml")
configuration = loader.load()


def pick_engine(configuration):
    """Offer an interactive engine picker if the config declares one.

    Falls back silently to whatever's already in model: if no engines list
    is present, or if stdin isn't interactive (e.g. running non-interactively).
    """
    engines = configuration.get("engines")
    if not engines:
        return

    if not sys.stdin.isatty():
        return

    print("Available engines:")
    for i, engine in enumerate(engines, start=1):
        print(f"  {i}. {engine.get('label', engine.get('adapter'))}")

    choice_raw = input(f"Choose engine [1]: ").strip()
    if not choice_raw:
        index = 0
    else:
        try:
            index = int(choice_raw) - 1
            if index < 0 or index >= len(engines):
                print(f"Invalid choice, defaulting to 1.")
                index = 0
        except ValueError:
            print(f"Invalid choice, defaulting to 1.")
            index = 0

    chosen = engines[index]
    model_config = configuration.setdefault("model", {})
    model_config["adapter"] = chosen.get("adapter")
    model_config["model"] = chosen.get("model")
    model_config["api_key_env"] = chosen.get("api_key_env")
    model_config["base_url"] = chosen.get("base_url")

    key_env = chosen.get("api_key_env")
    if key_env and not os.environ.get(key_env):
        print(f"WARNING: {key_env} is not set in this environment. "
              f"Set it before running, e.g.: $env:{key_env} = \"...\"")


pick_engine(configuration)

# Validate configuration
validator = Validator()
validator.validate_configuration(configuration)

# Load task package
task_loader = TaskLoader()
package = task_loader.load(configuration)

# Extract model configuration correctly
model_config = configuration["model"]
execution_config = configuration["execution"]

selected_backend = (model_config.get("adapter") or "").strip().lower()
selected_model = model_config.get("model")
selected_api_key_env = model_config.get("api_key_env")

print("Model selection")
print(f"Backend    : {selected_backend}")
print(f"Model      : {selected_model}")
print(f"API Key Env: {selected_api_key_env}")

# Build model adapter with correct field references
model_generation = model_config.get("generation", {})
temperature = model_generation.get("temperature", model_config.get("temperature", 0.0))
max_tokens = model_generation.get("max_tokens", model_config.get("max_tokens", 100))

model = ModelAdapter(
    backend=model_config["adapter"],
    model=selected_model,  # Fixed: use "model" not "method"
    temperature=temperature,
    max_tokens=max_tokens,
    api_key_env=model_config.get("api_key_env"),
    base_url=model_config.get("base_url"),
    timeout=execution_config.get("timeout_seconds", 60),
)

# Run experiment
runner = ExperimentRunner(package, model, configuration)
runner.run()
