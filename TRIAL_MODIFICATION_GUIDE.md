# HOW TO MODIFY TRIAL NUMBERS

## Current Trial Counts
- **Oddball Experiment**: 100 trials
- **Stroop Experiment**: 200 trials
- **Theory of Mind Experiment**: 20 trials

## Option 1: Modify Configuration (Recommended)

Edit the main configuration file:
`yaml
execution:
  repetitions: 10  # Change from 20 to 10
  stop_after_trials: 10  # Add this to limit trials
