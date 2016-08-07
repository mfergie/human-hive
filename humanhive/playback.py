import numpy as np

class Playback:
    """
    Manages the playback of sounds. Keeps active samples and controls volumes
    etc.
    """
    def __init__(self,
                 source_bank,
                 n_channels,
                 sample_rate,
                 master_volume):

        self.source_bank = source_bank

        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.master_volume = master_volume


    def retrieve_samples(self, n_frames):
        samples = np.zeros(
            (n_frames, self.n_channels), dtype=np.float)
        for source in self.source_bank.sources:
            samples += source.get_frames(n_frames)

        samples *= self.master_volume
        return np.asarray(samples, np.int16)


class PlaybackQueueProducer:
    """
    Keeps a queue filled with audio samples.
    """
    def __init__(self,
                 source_bank,
                 chunks_queue,
                 n_channels,
                 sample_rate,
                 n_samples_per_chunk,
                 master_volume=1.0):

        self.source_bank = source_bank
        self.chunks_queue = chunks_queue

        self.n_channels = n_channels
        self.sample_rate = sample_rate
        self.n_samples_per_chunk = n_samples_per_chunk
        self.master_volume = master_volume


    def run(self):
        """
        Generates samples and inserts them into queue.
        """
        while True:
            print("Producing")
            samples = np.zeros(
                (self.n_samples_per_chunk, self.n_channels), dtype=np.float)
            for source in self.source_bank.sources:
                samples += source.get_frames(self.n_samples_per_chunk)

            samples *= self.master_volume

            samples_int16 = np.asarray(samples, np.int16)
            # Insert into queue, block if queue fills up.
            self.chunks_queue.put(samples_int16, block=True)


class PlaybackQueueConsumer:
    """
    This is a class that meets the playback interface. Instead of computing
    samples online it will retrieve them from a shared queue populated by a
    PlaybackQueueProducer.
    """
    def __init__(self,
                 chunks_queue):
        self.chunks_queue = chunks_queue

    def retrieve_samples(self, n_frames):
        print("Consuming")
        samples = self.chunks_queue.get(block=True)
        return samples
