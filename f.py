bandpass_zeros = [(1, 0), (-1, 0)]
highpass_zeros = [(1, 0)]
lowpass_poles = [(1, 0)]

self.ui.acitonHighPass.triggered.connect(
    lambda: self.import_filter(self.highpass_zeros, _, _, _)
)
