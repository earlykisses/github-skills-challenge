from src.event_topic import EventTopic

# added the path fix
class EventProducer:
    """Publishes anomaly events to an in-memory topic."""

    def __init__(self, topic: EventTopic):
        self.topic = topic

    def publish(self, event):
        if not event:
            return False

        self.topic.publish(event)
        return True