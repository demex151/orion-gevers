class ClapDetector:
    """Detect a deliberate double clap from timestamped RMS audio levels."""

    def __init__(
        self,
        *,
        spike_ratio=7.0,
        min_rms=0.06,
        min_double_gap=0.08,
        max_double_gap=0.32,
        cooldown=0.75,
        retrigger_ratio=0.45,
        noise_floor_alpha=0.992,
        quiet_gate_mult=2.2,
    ):
        self.spike_ratio = spike_ratio
        self.min_rms = min_rms
        self.min_double_gap = min_double_gap
        self.max_double_gap = max_double_gap
        self.cooldown = cooldown
        self.retrigger_ratio = retrigger_ratio
        self.noise_floor_alpha = noise_floor_alpha
        self.quiet_gate_mult = quiet_gate_mult
        self.noise_floor = 1e-4
        self.first_clap_time = None
        self.last_double_time = -1e9
        self.armed = True

    def reset(self):
        """Forget an incomplete clap sequence when audio ownership changes."""
        self.first_clap_time = None
        self.armed = True

    def update(self, level: float, now: float) -> bool:
        level = max(0.0, float(level))
        now = float(now)

        quiet_gate = max(self.noise_floor * self.quiet_gate_mult, self.min_rms)
        if level < quiet_gate:
            self.noise_floor = max(
                1e-7,
                self.noise_floor_alpha * self.noise_floor
                + (1.0 - self.noise_floor_alpha) * level,
            )

        threshold = max(self.noise_floor * self.spike_ratio, self.min_rms)

        if level < threshold * self.retrigger_ratio:
            self.armed = True

        if self.first_clap_time is not None:
            if now - self.first_clap_time > self.max_double_gap:
                self.first_clap_time = None

        if (
            not self.armed
            or level < threshold
            or now - self.last_double_time < self.cooldown
        ):
            return False

        self.armed = False

        if self.first_clap_time is None:
            self.first_clap_time = now
            return False

        gap = now - self.first_clap_time

        if gap < self.min_double_gap:
            return False

        if gap <= self.max_double_gap:
            self.first_clap_time = None
            self.last_double_time = now
            return True

        self.first_clap_time = now
        return False
