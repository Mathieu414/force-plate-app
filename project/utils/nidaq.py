import nidaqmx
import time
from nidaqmx.constants import TerminalConfiguration, AcquisitionType

# Define the AI channels to read
channels = [
    "Dev2/ai0",
    "Dev2/ai1",
    "Dev2/ai2",
    "Dev2/ai3",
    "Dev2/ai4",
    "Dev2/ai5",
    "Dev2/ai6",
    "Dev2/ai7",
]

# Set the sampling rate and number of samples to read
sampling_rate = 1000  # Hz
num_samples = 3000


def nidaq_base_config(task: nidaqmx.Task):
    # Configure the DAQmx task
    task.ai_channels.add_ai_voltage_chan(
        ",".join(channels), terminal_config=TerminalConfiguration.DIFF
    )
    task.timing.cfg_samp_clk_timing(sampling_rate, samps_per_chan=num_samples)

    data = task.read(number_of_samples_per_channel=num_samples)

    return data


def nidaq_trigger():
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0")

        task.timing.cfg_samp_clk_timing(1000, samps_per_chan=num_samples)

        samples = []

        def callback(
            task_handle, every_n_samples_event_type, number_of_samples, callback_data
        ):
            """Callback function for reading singals."""
            print("Every N Samples callback invoked.")

            samples.extend(task.read(number_of_samples_per_channel=1000))

            return 0

        task.register_every_n_samples_acquired_into_buffer_event(1000, callback)

        task.start()

        input(
            "Running task. Press Enter to stop and see number of "
            "accumulated samples.\n"
        )

        print(len(samples))
