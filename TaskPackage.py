class TaskPackage:
    def __init__(
        self,
        metadata,
        system_prompt,
        user_prompt,
        parser_config,
        metrics_config,
        payload,
        ground_truth,
        stimuli,
        resources,
    ):
        self.metadata = metadata
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.parser_config = parser_config
        self.metrics_config = metrics_config
        self.payload = payload
        self.ground_truth = ground_truth
        self.stimuli = stimuli
        self.resources = resources