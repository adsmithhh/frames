# Theory of Mind False Belief Task (theory_of_mind_v1)

## Overview
This experiment tests **Theory of Mind (ToM)** abilities, specifically the understanding of **false beliefs**. Participants must predict where characters will search for objects based on their false beliefs, not reality.

## Scientific Background
Theory of Mind is the ability to attribute mental states—beliefs, intents, desires, emotions—to oneself and others. False belief tasks are a classic measure of ToM development and social cognition.

## Experimental Design
- **Task Type**: False belief prediction
- **Paradigm**: Social cognition
- **Stimuli**: 20 different character scenarios
- **Response Format**: Location-based answers

## Key Components

### 1. False Belief Structure
Each trial presents:
- **Character**: Person with a false belief
- **Object**: Item being searched for
- **True Location**: Where object actually is
- **Character Belief**: Where character thinks object is
- **Question**: Where will character search?

### 2. Example Trial
`
Character: Anna
Object: marble
True Location: Box
Character Belief: Drawer
Question: "Where will Anna look for her marble?"
Correct Answer: DRAWER (based on belief, not reality)
`

## Cognitive Requirements

### 1. **Belief-Desire Reasoning**
- Understand characters have mental states
- Recognize beliefs can be false

### 2. **Perspective Taking**
- Take character's perspective, not own
- Suppress own knowledge of reality

### 3. **Inhibitory Control**
- Inhibit response based on actual location
- Respond based on character's belief

## Stimuli Distribution

### Location Types
- **Indoor**: Box, Drawer, Cupboard, Kitchen, Bedroom, Living Room, Attic
- **Outdoor**: Garden, Garage

### Object Categories
- Personal items: marble, teddy bear, doll, necklace
- Daily objects: chocolate, football, bicycle, book
- Valuables: camera, laptop, ring, bracelet, wallet
- Accessories: keys, watch, earring, scarf, jacket

### Difficulty Levels
- **Easy**: Common locations (Box, Drawer)
- **Medium**: Familiar locations (Kitchen, Bedroom)
- **Hard**: Less common locations (Attic, Garage)

## Expected Performance

### Typical Results
- **Adult Humans**: 90-95% accuracy
- **Children (4-5 years)**: 50-70% accuracy  
- **Children (3-4 years)**: 20-40% accuracy
- **AI Systems**: Variable, tests social reasoning

### Response Patterns
- Fast responses: 2-5 seconds
- Slow responses: 5-10 seconds (indicating processing)
- Errors: Typically reality-based (true location responses)

## Analysis Metrics

### 1. **Accuracy**
- Percentage of correct belief-based responses
- Measures ToM understanding

### 2. **Response Time**
- Time to generate belief-based vs reality-based responses
- Indicates cognitive processing load

### 3. **Error Types**
- Reality errors (responding with true location)
- Response format errors
- Missing responses

## Files Created

### 1. task_payload.yaml
- Complete stimulus set (20 trials)
- Schema definitions
- Response contracts
- Analysis configurations

### 2. experiment_configuration.yaml
- DeepSeek model configuration
- Execution parameters
- Report settings
- Metadata

### 3. Expected Output
- JSON analysis with trial-by-trial results
- HTML report with performance summary
- Summary statistics and accuracy metrics

## Running the Experiment

### Prerequisites
- DeepSeek API key configured
- Cognitive experiment framework installed
- Required Python dependencies

### Execution Command
`ash
 = "your-api-key"
python main.py
`

### Configuration
- **Model**: DeepSeek Chat
- **Max Tokens**: 15 (for location responses)
- **Temperature**: 0.0 (deterministic responses)
- **Trials**: 5 (test run), 20 (full run)

## Scientific Applications

### 1. **Cognitive Development**
- Study ToM development across ages
- Identify developmental milestones

### 2. **Clinical Assessment**
- Autism spectrum disorder screening
- Social cognition impairment detection

### 3. **AI Research**
- Evaluate social reasoning in AI
- Compare human vs machine ToM

### 4. **Neuroscience**
- fMRI studies of ToM networks
- Neural correlates of false belief understanding

## Variations for Future Experiments

### 1. **Age-Appropriate Versions**
- **Children**: Simple scenarios, familiar objects
- **Adults**: Complex scenarios, abstract reasoning

### 2. **Cultural Variations**
- Different cultural contexts
- Cultural-specific scenarios and objects

### 3. **Difficulty Scaling**
- **Easy**: Single belief attribution
- **Hard**: Multiple nested beliefs
- **Expert**: Deception and irony understanding

### 4. **Modalities**
- **Visual**: Picture-based scenarios
- **Verbal**: Text-based scenarios
- **Video**: Animated scenarios

## References

### Classic ToM Studies
- Wimmer, P., & Perner, J. (1983). Beliefs about beliefs: Representation and constraining function of wrong beliefs in young children's understanding of deception.
- Baron-Cohen, S., Leslie, A. M., & Frith, U. (1985). Does the autistic child have a "theory of mind"?

### Modern Applications
- Apperly, I. A. (2011). Mindreaders: The cognitive basis of "theory of mind".
- Frith, U., & Frith, C. D. (2003). Development and neurophysiology of mentalizing.

## Notes
- This experiment tests **first-order false beliefs** (character's belief about reality)
- **Second-order false beliefs** (what character thinks another character believes) can be added
- **Deception scenarios** can be included for advanced testing
