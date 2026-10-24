"""One-off generator for messages_labeled.csv (development data only)."""

import csv
from pathlib import Path

LEGIT = [
    ("Your match starts in 10 minutes. Good luck!", "gaming_legit"),
    ("Team dinner at 7pm Friday — reply if you are coming.", "personal"),
    ("Library book due tomorrow. Renew online if needed.", "service"),
    ("Mom: call me when you get home safe.", "personal"),
    ("Weather alert: light rain expected this evening.", "news"),
    ("Your package was delivered to the front porch.", "shipping"),
    ("Meeting moved to conference room B at 2pm.", "work"),
    ("Grocery list: milk, eggs, bread.", "personal"),
    ("Game patch notes: bug fixes and balance changes.", "gaming_legit"),
    ("Reminder: dental appointment Tuesday 9am.", "appointment"),
    ("Class cancelled today due to instructor illness.", "education"),
    ("Your friend sent you a game invite — open the app to join.", "gaming_legit"),
    ("Bus route 12 delayed 5 minutes.", "transit"),
    ("Thanks for your purchase. Receipt attached.", "retail"),
    ("Office WiFi password updated — check intranet.", "work"),
    ("Happy birthday! Hope you have a great day.", "personal"),
    ("Study group at library room 204 tonight.", "education"),
    ("Your subscription renews next month unless you cancel in settings.", "service"),
    ("New episode of your podcast is available.", "media"),
    ("Car service complete. Vehicle ready for pickup.", "service"),
    ("Ranked season ends Sunday. Final push!", "gaming_legit"),
    ("Coach: practice moved to 5pm.", "sports"),
    ("Bank statement ready in mobile app — no action needed.", "bank_legit"),
    ("Amazon: your order has shipped with tracking in app.", "retail"),
    ("Steam summer sale live — browse store in client.", "gaming_legit"),
]

PHISH = [
    (
        "CONGRATULATIONS! You won 9999 FREE DIAMONDS! Click http://free-diamonds-giveaway.xyz/claim NOW!",
        "gaming_phish",
    ),
    (
        "Your account will be SUSPENDED in 1 hour. Verify password at http://login-secure-game.tk/update",
        "credential",
    ),
    ("Free COD skins — limited time! Enter OTP at http://skin-drop-2024.click/verify", "gaming_phish"),
    ("PayPal: unusual activity detected. Confirm at http://paypal-secure-login.xyz/", "brand_spoof"),
    ("URGENT Amazon refund pending. Login: http://amazon-security-check.ml/refund", "brand_spoof"),
    ("You received 5000 bonus coins! Tap http://bit.ly/game-coins-free to redeem", "gaming_phish"),
    ("WhatsApp: your number will be blocked. Verify at http://wa-verify-online.ga/", "smishing"),
    ("Netflix payment failed. Update billing http://netflix-billing-update.pw/", "brand_spoof"),
    ("Free UC for PUBG — send your login and OTP to unlock reward link", "gaming_phish"),
    ("Apple ID locked. Unlock now http://apple-id-unlock.support-team.ru/", "brand_spoof"),
    ("Winner! iPhone 15 prize. Claim fee required at http://prize-winner-claim.top/", "prize_scam"),
    ("Bank alert: transfer blocked. Call this number and share verification code immediately", "credential"),
    ("Free gems glitch working 2024!!! http://gem-hack-free.online/download apk", "gaming_phish"),
    ("Instagram copyright strike — appeal within 30 minutes http://ig-copyright-review.xyz/", "social"),
    ("Your game ID won legendary skin. Confirm account http://legend-skin-event.click/", "gaming_phish"),
    ("Microsoft: sign-in from new device. Approve at http://microsoft-login-verify.tk/", "brand_spoof"),
    ("Earn money fast — share bank details to receive transfer", "financial"),
    ("FREE ROBUX generator verify age with credit card at http://robux-gen-free.ml/", "gaming_phish"),
    ("DHL: package customs fee pay now http://dhl-payment-portal.xyz/pay", "shipping_spoof"),
    ("Telegram support: your account flagged. Enter 2FA code here to restore access", "credential"),
    ("Flash sale 90% off V-Bucks http://vbucks-deal-now.shop/login-steam-account", "gaming_phish"),
    ("Security notice: password expired. Reset at http://account-verify-now.gq/password", "credential"),
    ("You have (1) pending reward. Expires tonight http://reward-center-secure.online/", "urgency"),
    ("Coinbase wallet migration required — seed phrase needed at http://coinbase-migrate.io/", "crypto_phish"),
    (
        "Clash Royale free pass hack — install http://cr-mod-apk.cf/ and grant all permissions",
        "gaming_phish",
    ),
]


def main() -> None:
    rows = [{"message": m, "label": 0, "source": s} for m, s in LEGIT]
    rows += [{"message": m, "label": 1, "source": s} for m, s in PHISH]
    for m, s in PHISH[:12]:
        rows.append({"message": m.upper(), "label": 1, "source": f"{s}_var"})
    for m, s in LEGIT[:12]:
        rows.append({"message": f"{m} See you there.", "label": 0, "source": f"{s}_var"})

    path = Path(__file__).with_name("messages_labeled.csv")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["message", "label", "source"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    main()
