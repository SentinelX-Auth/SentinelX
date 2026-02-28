"""
Fraud and AI Bot Detection Module
Assesses requests for fraudulent patterns, rate abuse, and AI bot behavior.
"""

from datetime import datetime, timedelta
import collections
import re
from typing import Dict, Tuple, Any, Optional

class FraudDetectionSystem:
    def __init__(self, max_requests_per_minute: int = 20):

        self.ip_history = collections.defaultdict(lambda: collections.deque(maxlen=max_requests_per_minute * 5))
        self.max_requests_per_minute = max_requests_per_minute

        self.bad_ua_patterns = [
            re.compile(r'bot|crawler|spider|scraper|python|curl|wget|httpclient|postman', re.IGNORECASE),
            re.compile(r'headless|phantomjs|puppeteer|selenium', re.IGNORECASE)
        ]

    def _check_rate_limit(self, ip: str) -> bool:
        """Returns True if the IP is exceeding the rate limit."""
        now = datetime.now()
        history = self.ip_history[ip]
        

        while history and now - history[0] > timedelta(minutes=1):
            history.popleft()
            
        history.append(now)
        

        return len(history) > self.max_requests_per_minute

    def _check_user_agent(self, ua: str) -> Tuple[bool, str]:
        """Returns (is_suspicious_ua, reason)."""
        if not ua or ua.strip() == "":
            return True, "Missing User-Agent header"
            
        for pattern in self.bad_ua_patterns:
            if pattern.search(ua):
                return True, f"Suspicious User-Agent detected: {ua:.30s}..."
                
        return False, ""

    def _check_bot_behavior(self, behavioral_data: Dict[str, Any]) -> Tuple[bool, str, float]:
        """
        Analyzes client-side behavioral data for impossible or highly robotic patterns.
        Returns: (is_bot: bool, reason: str, bot_score: float)
        Bot score: 0.0 (Human) -> 1.0 (Definite AI/Bot)
        """
        if not behavioral_data:
            return False, "Missing behavioral data completely.", 0.2
            
        score = 0.0
        reasons = []

        iki_std = behavioral_data.get('iki_std', -1)
        if iki_std == 0:
            score += 0.6
            reasons.append("Zero variance in typing speed (perfect rhythm).")
        

        keystroke_rate = behavioral_data.get('keystroke_rate', 0)
        if keystroke_rate > 20: 
            score += 0.5
            reasons.append(f"Superhuman typing speed ({keystroke_rate:.1f} keys/sec).")
            

        mouse_velocity = behavioral_data.get('mouse_velocity', 0)
        if mouse_velocity > 5000:
            score += 0.4
            reasons.append(f"Unnatural mouse velocity ({mouse_velocity:.1f} px/sec).")
            

        total_time = behavioral_data.get('total_time', -1)
        if 0 <= total_time < 50:
            score += 0.6
            reasons.append("Form completed near-instantaneously.")

        is_bot = score >= 0.7
        return is_bot, " | ".join(reasons) if is_bot else "Behavior looks human", min(1.0, score)

    def evaluate_request(self, ip: str, user_agent: str, behavioral_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Master evaluation method.
        Returns a dictionary with the fraud assessment and a combined risk level.
        Risk Level: "Low", "Medium", "High"
        """
        is_rate_limited = self._check_rate_limit(ip)
        is_bad_ua, ua_reason = self._check_user_agent(user_agent)
        
        is_bot, bot_reason, bot_score = False, "", 0.0
        if behavioral_data:
             is_bot, bot_reason, bot_score = self._check_bot_behavior(behavioral_data)
        else:
             bot_score = 0.2

        total_risk_score = bot_score
        if is_rate_limited: total_risk_score += 0.8
        if is_bad_ua: total_risk_score += 0.4

        if total_risk_score >= 0.8:
            risk_level = "High"
        elif total_risk_score >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        should_block = is_rate_limited or is_bot or (risk_level == "High")

        return {
            "fraud_score": min(total_risk_score, 1.0),
            "bot_score": bot_score,
            "risk_level": risk_level,
            "should_block": should_block,
            "signals": {
                "rate_limited": is_rate_limited,
                "bad_user_agent": is_bad_ua,
                "ai_bot_detected": is_bot,
                "ua_reason": ua_reason,
                "bot_reason": bot_reason
            }
        }

fraud_detector = FraudDetectionSystem()
