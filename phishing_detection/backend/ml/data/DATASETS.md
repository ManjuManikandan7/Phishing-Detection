# Datasets

## Label mapping

| Label | Meaning     |
| ----- | ----------- |
| 0     | Legitimate  |
| 1     | Phishing    |

## `messages_labeled.csv` (included)

- **Source:** Synthetic, project-generated samples for development and smoke testing only.
- **License:** Project-owned demonstration data.
- **Limitation:** Not representative of real-world phishing volume or diversity. **Do not** cite metrics from this file as production performance without replacing it with licensed real data.
- **Categories:** Gaming rewards, OTP/credential theft, fake URLs, legitimate support-style messages.

## Recommended public datasets (optional upgrade)

When expanding the project, consider documenting and merging:

1. **SMS Spam Collection (UCI)** — ham/spam SMS; map spam → phishing with care (not all spam is phishing).
2. **Nazario Phishing Corpus** — email phishing; useful for text patterns (different channel).
3. **Kaggle SMS / phishing collections** — verify license terms before use in academic submission.

Always record source URL, license, preprocessing steps, and train/val/test split strategy in this file.
