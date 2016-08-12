"""
Mixer: A simple process class for combining audio from different
sources and outputting them to a single destination.

Assumes that the content in queues behaves like numpy arrays.
"""

class Mixer:

    def __init__(self,
                 input_queues,
                 output_queue):

        self.input_queues = input_queues
        self.output_queue = output_queue


    def process_audio(self):

        all_samples = [queue.get() for queue in self.input_queues]
        samples = sum(all_samples)

        self.output_queue.put(samples)


    def run(self):
        while True:
            self.process_audio()
