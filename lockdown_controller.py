"""Module for managing simulation lockdown states with hysteresis control"""

class LockdownController:
    def __init__(self, entry_threshold: float = 0.012, exit_threshold: float = 0.008):
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.current_state = False
        self.lockdown_periods = []
        self.current_period_start = None

    def update_lockdown_status(self, day: int, infection_rate: float) -> bool:
        """
        Updates lockdown status based on infection rate using hysteresis control
        
        Args:
            day: Current simulation day
            infection_rate: Current global infection rate
            
        Returns:
            bool: Current lockdown status
        """
        previous_state = self.current_state
        
        if not self.current_state and infection_rate >= self.entry_threshold:
            # Enter lockdown
            self.current_state = True
            self.current_period_start = day
        elif self.current_state and infection_rate < self.exit_threshold:
            # Exit lockdown
            self.current_state = False
            if self.current_period_start is not None:
                self.lockdown_periods.append({
                    'start': self.current_period_start,
                    'end': day,
                    'duration': day - self.current_period_start
                })
                self.current_period_start = None

        return self.current_state

    def get_lockdown_statistics(self) -> dict:
        """Returns summary statistics about lockdown periods"""
        if not self.lockdown_periods:
            return {
                'total_periods': 0,
                'total_days': 0,
                'average_duration': 0,
                'periods': []
            }
            
        return {
            'total_periods': len(self.lockdown_periods),
            'total_days': sum(period['duration'] for period in self.lockdown_periods),
            'average_duration': sum(period['duration'] for period in self.lockdown_periods) / len(self.lockdown_periods),
            'periods': self.lockdown_periods
        }
