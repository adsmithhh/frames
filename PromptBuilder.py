class PromptBuilder:

    @classmethod
    def build(cls, payload, stimulus):
        """Build prompt entirely from payload schema."""
        # Extract sections from payload
        protocol = payload.get("protocol", {})
        instructions = payload.get("instructions", {})
        stimulus_schema = payload.get("stimulus_schema", {})
        
        # Build prompt components
        role_block = cls._build_role_block(protocol)
        goal_block = cls._build_goal_block(protocol)
        rules_block = cls._build_rules_block(protocol)
        task_block = cls._build_task_block(instructions)
        stimulus_block = cls._build_stimulus_block(stimulus_schema, stimulus)
        response_format_block = cls._build_response_format_block(instructions)
        example_block = cls._build_example_block(instructions)
        closing_block = cls._build_closing_block(instructions)

        # Assemble final prompt
        prompt_parts = [
            cls._build_header(),
            role_block,
            goal_block,
            rules_block,
            task_block,
            stimulus_block,
            response_format_block,
            example_block,
            closing_block,
            cls._build_answer_prompt()
        ]
        
        return "\n\n".join(filter(None, prompt_parts))

    @classmethod
    def _build_header(cls):
        return """You are participating in a cognitive psychology experiment."""

    @classmethod
    def _build_role_block(cls, protocol):
        role = protocol.get("role", "experimental subject")
        return f"""ROLE
You are the {role}."""

    @classmethod
    def _build_goal_block(cls, protocol):
        goal = protocol.get("goal", "Execute the task exactly as instructed.")
        return f"""GOAL
{goal}"""

    @classmethod
    def _build_rules_block(cls, protocol):
        rules = protocol.get("rules", [])
        if not rules:
            return None
        
        rules_text = "\n".join(f"- {rule}" for rule in rules)
        return f"""RULES
{rules_text}"""

    @classmethod
    def _build_task_block(cls, instructions):
        task = (
            instructions.get("task")
            or instructions.get("task_detail")
            or instructions.get("task_brief")
            or ""
        ).strip()
        if not task:
            return None
        return f"""TASK
{task}"""

    @classmethod
    def _build_stimulus_block(cls, stimulus_schema, stimulus):
        """Build stimulus display based on declared schema."""
        if not stimulus_schema or not isinstance(stimulus, dict):
            return None
        
        lines = []
        
        # Get field order from schema or use natural order
        field_order = cls._get_field_order(stimulus_schema, stimulus)
        
        for field_name in field_order:
            if field_name not in stimulus:
                continue
                
            label = cls._get_field_label(field_name, stimulus_schema)
            value = stimulus[field_name]
            lines.append(f"{label}: {value}")

        if not lines:
            return None
            
        return """STIMULUS

{}""".format("\n".join(lines))

    @classmethod
    def _get_field_order(cls, stimulus_schema, stimulus):
        """Get field display order from schema or fall back to stimulus keys."""
        fields = stimulus_schema.get("fields", [])
        
        # First, use schema order if specified
        schema_order = []
        for field in fields:
            field_name = field.get("name")
            if field_name in stimulus and field.get("display", True):
                schema_order.append(field_name)
        
        # Add any remaining fields from stimulus
        for field_name in stimulus.keys():
            if field_name not in schema_order:
                schema_order.append(field_name)
        
        return schema_order

    @classmethod
    def _get_field_label(cls, field_name, stimulus_schema):
        """Get display label for a field."""
        # Look up label in schema
        fields = stimulus_schema.get("fields", [])
        for field in fields:
            if field.get("name") == field_name:
                return field.get("label", cls._default_field_label(field_name))
        
        # Fall back to default
        return cls._default_field_label(field_name)

    @classmethod
    def _default_field_label(cls, field_name):
        """Generate default label for a field."""
        # Handle common acronyms
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

    @classmethod
    def _field_label(cls, field_name):
        """Backward compatibility method for ExperimentRunner."""
        return cls._default_field_label(field_name)

    @classmethod
    def _build_response_format_block(cls, instructions):
        response_format = instructions.get("response_format", "Provide your answer.")
        return f"""RESPONSE FORMAT

{response_format}"""

    @classmethod
    def _build_example_block(cls, instructions):
        """Build example section if provided."""
        example = instructions.get("example", {})
        if not example:
            return None
        
        example_stimulus = example.get("stimulus", {})
        example_response = example.get("correct_response", "Example answer")
        
        if not example_stimulus:
            return None
        
        # Build example stimulus display
        stimulus_lines = []
        for field_name, value in example_stimulus.items():
            label = cls._get_field_label(field_name, {})
            stimulus_lines.append(f"{label}: {value}")
        
        stimulus_text = "\n".join(stimulus_lines)
        
        return f"""Example:

{stimulus_text}

Correct response:
{example_response}"""

    @classmethod
    def _build_closing_block(cls, instructions):
        closing_prompt = instructions.get("closing_prompt", "Please provide your answer now.")
        return closing_prompt

    @classmethod
    def _build_answer_prompt(cls):
        return "Answer:"

    @classmethod
    def placeholder_stimulus(cls, payload):
        """Generate a placeholder stimulus for template purposes."""
        stimulus_schema = payload.get("stimulus_schema", {})
        fields = stimulus_schema.get("fields", [])
        
        placeholder = {}
        for field in fields:
            field_name = field.get("name")
            if field.get("display", True):
                placeholder[field_name] = "<trial stimulus>"
        
        # Add any fields from the first real stimulus if schema is empty
        if not fields and payload.get("stimuli"):
            first_stimulus = payload["stimuli"][0]
            if isinstance(first_stimulus, dict):
                for key, value in first_stimulus.items():
                    if key not in {"id", "stimulus_id"}:
                        placeholder[key] = "<trial stimulus>"
        
        return placeholder if placeholder else {"stimulus": "<trial stimulus>"}

    @classmethod
    def validate_stimulus(cls, payload, stimulus):
        """Validate stimulus against payload schema."""
        stimulus_schema = payload.get("stimulus_schema", {})
        fields = stimulus_schema.get("fields", [])
        
        if not isinstance(stimulus, dict):
            raise ValueError("Stimulus must be a dictionary")
        
        # Check required fields
        for field in fields:
            field_name = field.get("name")
            is_required = field.get("required", False)
            
            if is_required and field_name not in stimulus:
                raise ValueError(f"Missing required field '{field_name}' in stimulus")
        
        return True
