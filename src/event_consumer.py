from src.event_topic import EventTopic

# added the path fix
class EventConsumer:
    """Consumes events from an in-memory topic."""

    def __init__(self, topic: EventTopic):
        self.topic = topic

    def consume(self):
        return self.topic.get_messages()