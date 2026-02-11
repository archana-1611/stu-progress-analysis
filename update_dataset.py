import pandas as pd

# Load the dataset
df = pd.read_csv("training_dataset.csv")

# Define High Achiever: Attendance >= 95 AND (internal_marks >= 95 OR assignment_score >= 95)
# Or simply any student with very high scores across the board.
# Let's use: (attendance >= 90) & (internal_marks >= 95) & (assignment_score >= 95)
high_achiever_mask = (df["attendance"] >= 90) & (df["internal_marks"] >= 95) & (df["assignment_score"] >= 95)

# Update labels
df.loc[high_achiever_mask, "final_label"] = "High Achiever"

# Save to a new file to avoid locks
new_filename = "training_dataset_updated.csv"
df.to_csv(new_filename, index=False)
print(f"Updated {high_achiever_mask.sum()} rows to 'High Achiever'")

# Check unique labels again
print("Updated Unique Labels:", df["final_label"].unique())
