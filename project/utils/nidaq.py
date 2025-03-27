import nidaqmx
import time
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import threading
import numpy as np
from scipy.signal import find_peaks, medfilt
from utils.utils import low_filter, convert_voltage_to_force

GRAVITY_CONSTANT = 9.80665

# Define the AI channels to read
# ai4 to 7 are for z forces
# ai0 and 1 are for x
# ai2 and 3 are for y
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
num_samples = 10  # 0.03s at 1000Hz


def nidaq_base_config(task: nidaqmx.Task):
    # Configure the DAQmx task
    task.ai_channels.add_ai_voltage_chan(
        ",".join(channels), terminal_config=TerminalConfiguration.DIFF
    )
    task.timing.cfg_samp_clk_timing(sampling_rate, samps_per_chan=num_samples)

    data = task.read(number_of_samples_per_channel=num_samples)

    return data


class BaseDataAcquisition:
    def __init__(
        self,
        channels,
        sample_frequency=100,
        global_data_length=None,
        timeout_duration=100,
        fz_range=2.5,
    ):
        self.channels = channels
        self.sample_frequency = sample_frequency
        self.global_data_length = global_data_length
        self.timeout_duration = timeout_duration
        self.fz_range = fz_range
        self.global_data_x = np.empty((2, 1))
        self.global_data_y = np.empty((2, 1))
        self.global_data_z = np.empty((4, 1))
        self.acquisition_thread = None
        self.acquisition_running = False

    def start_acquisition(self):
        self.acquisition_running = True
        self.acquisition_thread = threading.Thread(target=self.data_acquisition)
        self.acquisition_thread.start()

    def stop_acquisition(self):
        self.acquisition_running = False
        if self.acquisition_thread is not None:
            self.acquisition_thread.join()
            self.acquisition_thread = None
            return True
        return False

    def data_acquisition(self):
        """function to handle the data acquisition.
        A callback is being registered to the task using register_every_n_samples_acquired_into_buffer_event,
        and the new data is processed using `process_data`, which adds new data after transforming it to the
        `global_data_<>` object.
        """
        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(
                    ",".join(self.channels),
                    terminal_config=TerminalConfiguration.DIFF,
                )
                task.timing.cfg_samp_clk_timing(
                    self.sample_frequency, sample_mode=AcquisitionType.CONTINUOUS
                )

                def sample_callback(
                    task_handle,
                    every_n_samples_event_type,
                    number_of_samples,
                    callback_data,
                ):
                    new_data = np.array(
                        task.read(number_of_samples_per_channel=self.sample_frequency)
                    )
                    new_data_x = new_data[:2]
                    new_data_y = new_data[2:4]
                    new_data_z = new_data[-4:]
                    new_data_z_filtered = low_filter(new_data_z, threshold=0.02)
                    # new_data_z_filtered = medfilt(   volume=new_data_z_filtered, kernel_size=5)
                    self.process_data(new_data_x, new_data_y, new_data_z_filtered)
                    return 0

                task.register_every_n_samples_acquired_into_buffer_event(
                    self.sample_frequency, sample_callback
                )
                task.start()

                timeout = time.time() + self.timeout_duration + 0.1

                while True:
                    if not self.acquisition_running or time.time() > timeout:
                        return
        except nidaqmx.DaqError as e:
            print(f"An error occurred: {e}")

    def process_data(self, new_data_x, new_data_y, new_data_z):
        if (
            self.global_data_length is not None
            and len(self.global_data_z[1]) > self.global_data_length
        ):
            self.global_data_z = self.global_data_z[:, -self.global_data_length :]
        self.global_data_x = np.append(self.global_data_x, new_data_x, axis=1)
        self.global_data_y = np.append(self.global_data_y, new_data_y, axis=1)
        self.global_data_z = np.append(self.global_data_z, new_data_z, axis=1)

    def get_data_x(self):
        return self.global_data_x

    def get_data_y(self):
        return self.global_data_y

    def get_data_z(self):
        return self.global_data_z

    def get_z_data_converted(self):
        sum_data_tension = np.sum(self.global_data_z, axis=0)
        sum_data_force = convert_voltage_to_force(sum_data_tension, self.fz_range)
        return sum_data_force


class FreeDataAcquisition(BaseDataAcquisition):
    def __init__(
        self,
        channels,
        sample_frequency=100,
        global_data_length=None,
        timeout_duration=100,
        fz_range=2.5,
    ):
        super().__init__(
            channels, sample_frequency, global_data_length, timeout_duration, fz_range
        )
        self.max_force = 0

    def process_data(self, new_data_x, new_data_y, new_data_z):
        sum_new_data_z = np.sum(new_data_z, axis=0)
        sum_data_force = convert_voltage_to_force(sum_new_data_z, self.fz_range)
        self.max_force = max(
            self.max_force,
            np.max(sum_data_force),
        )
        super().process_data(new_data_x, new_data_y, new_data_z)

    def get_max_force(self):
        return self.max_force


class SessionDataAcquisition(BaseDataAcquisition):
    def __init__(
        self,
        channels,
        sample_frequency=100,
        global_data_length=None,
        timeout_duration=100,
        fz_range=2.5,
        weight=None,
        load=0,
        high_threshold_coeficient=1.2,
        low_threshold_coeficient=0.3,
    ):
        super().__init__(
            channels, sample_frequency, global_data_length, timeout_duration, fz_range
        )
        self.weight = weight
        self.load = load
        self.high_threshold_coeficient = high_threshold_coeficient
        self.low_threshold_coeficient = low_threshold_coeficient
        self.jumps_data = None

        self.low_peak_group_threshold = 20

        self.high_peak_width_threshold = 2

        self.weight_window_size = 100
        self.weight_std_threshold = 0.010

        if self.weight is not None:
            self.threshold = (
                (self.weight + self.load) * 0.0018 / (self.fz_range / 2.5) * 9.80665
            )
            self.high_threshold = self.threshold * self.high_threshold_coeficient
            self.low_threshold = self.threshold * self.low_threshold_coeficient

    def find_low_peaks(self, sum_data_z):
        group_threshold = self.low_peak_group_threshold
        low_peaks, low_peaks_properties = find_peaks(
            x=-sum_data_z, height=-self.low_threshold
        )
        if len(low_peaks) == 0:
            return

        # Group peaks that are close together (less than 100 points apart)
        grouped_peaks = [low_peaks[0]]

        for i in range(1, len(low_peaks)):
            if low_peaks[i] - low_peaks[i - 1] > group_threshold:
                grouped_peaks.append(low_peaks[i])

        return grouped_peaks

    def find_high_peaks(self, sum_data_z):
        # find low peaks
        low_peaks = self.find_low_peaks(sum_data_z=sum_data_z)

        peaks_data = []
        peaks_properties = []
        # Process each low peak
        if low_peaks is not None:
            for low_peak in low_peaks:
                n_after = 200
                # Look for high peaks in the next 100 points after low peak
                next_n_points = min(low_peak + n_after, len(sum_data_z))
                high_peaks_after, _ = find_peaks(
                    sum_data_z[low_peak:next_n_points],
                    height=self.high_threshold,
                    width=self.high_peak_width_threshold,
                )

                if len(high_peaks_after) > 0:
                    n_before = 100
                    # If high peak found, look for peaks in previous 100 points
                    start_point = max(0, low_peak - n_before)
                    peaks_before, properties_before = find_peaks(
                        sum_data_z[start_point:low_peak],
                        height=self.high_threshold,
                        width=self.high_peak_width_threshold,
                    )

                    if len(peaks_before) > 0:
                        # Find the peak with largest width
                        peak_heights = properties_before["widths"]
                        max_peak_idx = peaks_before[np.argmax(peak_heights)]
                        # Store the actual index by adding start_point
                        peaks_data.append(start_point + max_peak_idx)
                        peaks_properties.append(properties_before)
        return (peaks_data, peaks_properties)

    def find_weight(self, data_z):
        ## find a stable area in the data. Calculate the weight from this area
        # Find stable regions where the force variation is minimal

        tension_threshold = self.fz_range / 10

        # Calculate rolling standard deviation
        rolling_std = np.array(
            [
                np.std(data_z[i : i + self.weight_window_size])
                for i in range(len(data_z) - self.weight_window_size)
            ]
        )
        stable_regions = np.where(rolling_std < self.weight_std_threshold)[0]

        # Group consecutive stable indices
        stable_groups = group_indices(stable_regions)

        if stable_groups:
            # Filter stable groups by mean tension threshold
            valid_groups = []
            for group in stable_groups:
                mean_tension = np.mean(
                    data_z[group[0] : group[-1] + self.weight_window_size]
                )
                if mean_tension > tension_threshold:
                    valid_groups.append((group, mean_tension))

            if valid_groups:
                # Use the longest stable region above threshold to calculate weight
                longest_group, stable_tension = max(
                    valid_groups, key=lambda x: len(x[0])
                )
                print("Stable tension:", stable_tension)

                self.weight = (
                    convert_voltage_to_force(stable_tension, self.fz_range)
                    / GRAVITY_CONSTANT
                )

                print("Weight :", self.weight)

                # Update thresholds with new weight
                self.threshold = (
                    (self.weight + self.load)
                    * 0.0018
                    / (self.fz_range / 2.5)
                    * GRAVITY_CONSTANT
                )
                self.high_threshold = self.threshold * self.high_threshold_coeficient
                self.low_threshold = self.threshold * self.low_threshold_coeficient

    def process_data(self, new_data_x, new_data_y, new_data_z):
        if (
            self.global_data_length is not None
            and len(self.global_data_z[1]) > self.global_data_length
        ):
            self.global_data_z = self.global_data_z[:, -self.global_data_length :]

        # Append the new data to the global data
        self.global_data_x = np.append(self.global_data_x, new_data_x, axis=1)
        self.global_data_y = np.append(self.global_data_y, new_data_y, axis=1)
        self.global_data_z = np.append(self.global_data_z, new_data_z, axis=1)
        # Calculate the sum of the global data
        sum_data_z = np.sum(self.global_data_z, axis=0)

        ## Here, we want to find the weight of the athlete if the weight is not defined.
        if self.weight is None:
            self.find_weight(data_z=sum_data_z)

        if self.weight is not None:
            peaks_data, properties_before = self.find_high_peaks(sum_data_z=sum_data_z)
            if peaks_data:
                self.jumps_data = (peaks_data, properties_before)

    def get_jumps_data(self):
        return self.jumps_data


def group_indices(indices):
    if indices.size == 0:
        return []

    groups = []
    current_group = [indices[0]]

    for i in range(1, len(indices)):
        if indices[i] == indices[i - 1] + 1:
            current_group.append(indices[i])
        else:
            groups.append(current_group)
            current_group = [indices[i]]

    groups.append(current_group)
    return groups


def check_force_plate_connection():
    try:
        with nidaqmx.Task() as task:
            nidaq_base_config(task)
            return True
    except nidaqmx.DaqError:
        return False
