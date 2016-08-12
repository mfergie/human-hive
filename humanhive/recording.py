import numpy as np

class Recording:
    """
    Takes the input data from the sound interface, segments them into samples
    and then directs these samples to a sample bank.
    """

    def __init__(self, source_bank, recording_queue, n_samples_buffer):
        self.source_bank = source_bank
        self.recording_queue = recording_queue

        # Stores a list of frames which make up the current sample. Initialised
        # to None to indicate that there is no current sample being recorded.
        self.current_sample = None

        # Stores the volume of the last sub-frame picked up by process_audio()
        # Used to threshold volume when segmenting audio. Initialise to None
        # to allow setting at initial levels. n_ambient_chunks stores the
        # number of ambient chunks used to compute the average
        self.ambient_volume = None
        self.n_ambient_chunks = 0

        self.n_samples_buffer = n_samples_buffer

        # Stores past samples for capturing recorded data when threshold
        # lies between calls to process_audio
        self.sample_buffer = []

        # Stores changing volumes over time for analysis
        self.volume_buffer = []

    def run(self):
        """
        Puts the recording module into a running mode. Consumes data from
        recording queue and processes it.
        """
        while True:

            self.process_audio()

    def process_audio(self):
        """
        Processes incoming audio data. Segments when a voice is detected and
        records sample. This is then saved to the sample_bank.
        """
        in_data = self.recording_queue.get()
        assert in_data.shape[0] == frame_count

        print("ch 0 max: {}, ch 1 max: {}".format(
            np.abs(in_data[:,0]).max(), np.abs(in_data[:,0]).max()))
        #
        # if self.current_sample is None:
        #     self.update_ambient_volume(in_data)
        #
        # print(self.ambient_volume)
        #
        # self.update_sample_buffers(in_data, frame_count)

        # Turn volumes into threshold crossings

        # If there's a threshold crossing with no opposing return within the
        # specified time limit, start recording.

        # If the recording has passed a minimum length, and there is a down
        # threshold which stays down for a specified time stop recording.

        # Save the recorded data somewhere

        # Send this off to the SourceBank for adding into the mix.



    def update_sample_buffers(self, in_data, frame_count):

        # Check whether to discard oldest audio and volume samples. This assumes
        # that the frame_count is always consistent
        if len(sample_buffer) > (self.n_samples_buffer / frame_count):
            self.sample_buffer.pop(0)
            self.volume_buffer.pop(0)

        self.sample_buffer.append(in_data)
        self.volume_buffer.append(
            utils.compute_audio_volume_per_frame(in_data))

    def update_ambient_volume(self, in_data):
        """
        Updates the ambient volume
        """
        if self.ambient_volume is None:
            self.ambient_volume = utils.compute_audio_volume(in_data)
        else:
            existing_ambient_volume = (
                self.ambient_volume *
                (self.n_ambient_chunks / (self.n_ambient_chunks + 1)))
            current_contribution = (
                utils.compute_audio_volume(in_data) / (self.n_ambient_chunks + 1))
            self.ambient_volume = existing_ambient_volume + current_contribution
