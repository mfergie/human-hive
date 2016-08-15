"""
Mixer: A simple process class for combining audio from different
sources and outputting them to a single destination.

Assumes that the content in queues behaves like numpy arrays.
"""
import time

class Mixer:

    def __init__(self,
                 input_queues,
                 output_queue):

        self.input_queues = input_queues
        self.output_queue = output_queue


    def process_audio(self):

        st = time.time()
        all_samples = []
        for ind, queue in enumerate(self.input_queues):
            print("Read queue: {}".format(ind), end="... ")
            try:
                 all_samples.append(queue.get(block=True))
            except Exception as e:
                 print("Queue {} empty: {}".format(ind, e))
            print("finished.")
        samples = sum(all_samples)
        print("Mixer get audio time: {}".format(time.time() - st))
        # print("mixer qsize: {}".format(self.output_queue.qsize()))

        self.output_queue.put(samples)


    def run(self):
        while True:
            self.process_audio()
